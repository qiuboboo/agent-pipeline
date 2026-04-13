from __future__ import annotations

import base64
import http.client
import io
import json
import ssl
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from PIL import Image

from .config import ModelEndpointConfig
from .utils import extract_json_object, to_plain_text


class OpenAICompatibleClient:
    def __init__(self, config: ModelEndpointConfig):
        self.config = config
        self._usage_lock = threading.Lock()
        self.usage_totals: Dict[str, Any] = {
            "request_count": 0,
            "successful_request_count": 0,
            "failed_request_count": 0,
            "retry_count": 0,
            "text_request_count": 0,
            "multimodal_request_count": 0,
            "requests_with_usage": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cached_tokens": 0,
            "reasoning_tokens": 0,
            "total_request_seconds": 0.0,
            "last_error": None,
        }

    def snapshot_usage(self) -> Dict[str, Any]:
        with self._usage_lock:
            return {
                **self.usage_totals,
                "total_request_seconds": round(float(self.usage_totals.get("total_request_seconds", 0.0)), 3),
            }

    def _extract_usage(self, body: Dict[str, Any]) -> Dict[str, int]:
        usage = body.get("usage") or {}
        prompt_details = usage.get("prompt_tokens_details") or usage.get("input_tokens_details") or {}
        completion_details = usage.get("completion_tokens_details") or usage.get("output_tokens_details") or {}
        prompt_tokens = usage.get("prompt_tokens", usage.get("input_tokens", 0)) or 0
        completion_tokens = usage.get("completion_tokens", usage.get("output_tokens", 0)) or 0
        total_tokens = usage.get("total_tokens", 0) or (prompt_tokens + completion_tokens)
        cached_tokens = prompt_details.get("cached_tokens", 0) or 0
        reasoning_tokens = completion_details.get("reasoning_tokens", 0) or 0
        return {
            "prompt_tokens": int(prompt_tokens),
            "completion_tokens": int(completion_tokens),
            "total_tokens": int(total_tokens),
            "cached_tokens": int(cached_tokens),
            "reasoning_tokens": int(reasoning_tokens),
        }

    def _build_payload(self, system_prompt: str, user_content: Any) -> Dict[str, Any]:
        return {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "temperature": self.config.temperature,
            "response_format": {"type": "json_object"},
            "reasoning_effort": self.config.reasoning_effort,
        }

    def _post_json(self, payload: Dict[str, Any], has_images: bool = False) -> Optional[Dict[str, Any]]:
        if not self.config.enabled or not self.config.api_key:
            return None
        with self._usage_lock:
            self.usage_totals["request_count"] += 1
            if has_images:
                self.usage_totals["multimodal_request_count"] += 1
            else:
                self.usage_totals["text_request_count"] += 1
        url = self.config.base_url.rstrip("/") + "/chat/completions"
        last_error_text = None
        for attempt in range(1, 4):
            started = time.perf_counter()
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Connection": "close",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "Authorization": f"Bearer {self.config.api_key}",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                    body = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                elapsed = time.perf_counter() - started
                with self._usage_lock:
                    self.usage_totals["failed_request_count"] += 1
                    self.usage_totals["total_request_seconds"] += elapsed
                try:
                    error_body = exc.read().decode("utf-8", errors="ignore")
                except Exception:
                    error_body = ""
                last_error_text = f"HTTP {exc.code}: {error_body[:240] or exc.reason}"
                retryable = exc.code in {408, 409, 429} or exc.code >= 500
                if retryable and attempt < 3:
                    with self._usage_lock:
                        self.usage_totals["retry_count"] += 1
                    time.sleep(min(2.0, 0.5 * attempt))
                    continue
                with self._usage_lock:
                    self.usage_totals["last_error"] = last_error_text
                return None
            except (urllib.error.URLError, http.client.RemoteDisconnected, ConnectionResetError, BrokenPipeError, ssl.SSLError, TimeoutError, json.JSONDecodeError) as exc:
                elapsed = time.perf_counter() - started
                with self._usage_lock:
                    self.usage_totals["failed_request_count"] += 1
                    self.usage_totals["total_request_seconds"] += elapsed
                last_error_text = f"{type(exc).__name__}: {exc}"
                if attempt < 3:
                    with self._usage_lock:
                        self.usage_totals["retry_count"] += 1
                    time.sleep(min(2.0, 0.5 * attempt))
                    continue
                with self._usage_lock:
                    self.usage_totals["last_error"] = last_error_text
                return None
            elapsed = time.perf_counter() - started
            usage = self._extract_usage(body)
            with self._usage_lock:
                self.usage_totals["total_request_seconds"] += elapsed
                if usage["total_tokens"] > 0:
                    self.usage_totals["requests_with_usage"] += 1
                for key, value in usage.items():
                    self.usage_totals[key] += value
            choices = body.get("choices") or []
            if not choices:
                last_error_text = "Response missing choices."
                with self._usage_lock:
                    self.usage_totals["failed_request_count"] += 1
                if attempt < 3:
                    with self._usage_lock:
                        self.usage_totals["retry_count"] += 1
                        self.usage_totals["last_error"] = last_error_text
                    time.sleep(min(2.0, 0.5 * attempt))
                    continue
                with self._usage_lock:
                    self.usage_totals["last_error"] = last_error_text
                return None
            message = choices[0].get("message") or {}
            content = message.get("content", "")
            if isinstance(content, list):
                content = "\n".join(item.get("text", "") for item in content if isinstance(item, dict))
            parsed = extract_json_object(to_plain_text(content))
            if not parsed:
                raw_preview = json.dumps(body, ensure_ascii=False)[:400]
                last_error_text = f"Response missing JSON object. body_preview={raw_preview}"
                with self._usage_lock:
                    self.usage_totals["failed_request_count"] += 1
                if attempt < 3:
                    with self._usage_lock:
                        self.usage_totals["retry_count"] += 1
                        self.usage_totals["last_error"] = last_error_text
                    time.sleep(min(2.0, 0.5 * attempt))
                    continue
                with self._usage_lock:
                    self.usage_totals["last_error"] = last_error_text
                return None
            with self._usage_lock:
                self.usage_totals["successful_request_count"] += 1
                self.usage_totals["last_error"] = None
            parsed["_llm_usage"] = usage
            parsed["_llm_elapsed_seconds"] = round(elapsed, 3)
            parsed["_llm_request_mode"] = "multimodal" if has_images else "text"
            parsed["_llm_endpoint_name"] = self.config.name
            return parsed
        with self._usage_lock:
            self.usage_totals["last_error"] = last_error_text
        return None

    def image_to_data_url(self, image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.convert("RGB").save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"

    def chat_json_parts(self, system_prompt: str, user_parts: Sequence[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        content_parts: List[Dict[str, Any]] = []
        for item in user_parts:
            if not isinstance(item, dict):
                continue
            part_type = item.get("type")
            if part_type == "text":
                text_value = to_plain_text(item.get("text"))
                if text_value:
                    content_parts.append({"type": "text", "text": text_value})
            elif part_type == "image":
                image = item.get("image")
                if isinstance(image, Image.Image):
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {"url": self.image_to_data_url(image)},
                    })
            elif part_type == "image_url":
                url_value = to_plain_text(item.get("url"))
                if url_value:
                    content_parts.append({"type": "image_url", "image_url": {"url": url_value}})
        if not content_parts:
            content_parts = [{"type": "text", "text": "{}"}]
        has_images = any(part.get("type") == "image_url" for part in content_parts)
        return self._post_json(self._build_payload(system_prompt, content_parts), has_images=has_images)

    def chat_json(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        return self.chat_json_parts(system_prompt, [{"type": "text", "text": user_prompt}])

    def chat_json_with_images(self, system_prompt: str, user_prompt: str, images: Sequence[Image.Image]) -> Optional[Dict[str, Any]]:
        user_parts: List[Dict[str, Any]] = [{"type": "text", "text": user_prompt}]
        for image in list(images)[:3]:
            if isinstance(image, Image.Image):
                user_parts.append({"type": "image", "image": image})
        return self.chat_json_parts(system_prompt, user_parts)


class ModelRouter:
    def __init__(self, primary: OpenAICompatibleClient, fallback: Optional[OpenAICompatibleClient] = None):
        self.primary = primary
        self.fallback = fallback

    @classmethod
    def from_configs(cls, primary: ModelEndpointConfig, fallback: Optional[ModelEndpointConfig] = None) -> "ModelRouter":
        return cls(
            primary=OpenAICompatibleClient(primary),
            fallback=OpenAICompatibleClient(fallback) if fallback else None,
        )

    def chat_json(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        result = self.primary.chat_json(system_prompt, user_prompt)
        if result is not None:
            return result
        if self.fallback is not None:
            return self.fallback.chat_json(system_prompt, user_prompt)
        return None

    def chat_json_with_images(self, system_prompt: str, user_prompt: str, images: Sequence[Image.Image]) -> Optional[Dict[str, Any]]:
        result = self.primary.chat_json_with_images(system_prompt, user_prompt, images)
        if result is not None:
            return result
        if self.fallback is not None:
            return self.fallback.chat_json_with_images(system_prompt, user_prompt, images)
        return None

    def has_available_endpoint(self) -> bool:
        primary_ready = bool(self.primary.config.enabled and self.primary.config.api_key)
        fallback_ready = bool(self.fallback and self.fallback.config.enabled and self.fallback.config.api_key)
        return primary_ready or fallback_ready

    def ensure_available(self, operation_name: str) -> None:
        if self.has_available_endpoint():
            return
        raise RuntimeError(
            f"[{operation_name}] No enabled model endpoint has an API key. "
            "Set `PIPELINE2_API_KEY_PRIMARY` and/or `PIPELINE2_API_KEY_FALLBACK` before running the live pipeline."
        )

    def last_error_summary(self) -> Dict[str, Any]:
        return {
            "primary_last_error": self.primary.snapshot_usage().get("last_error"),
            "fallback_last_error": self.fallback.snapshot_usage().get("last_error") if self.fallback else None,
        }

    def usage_summary(self) -> Dict[str, Any]:
        return {
            "primary": self.primary.snapshot_usage(),
            "fallback": self.fallback.snapshot_usage() if self.fallback else None,
        }
