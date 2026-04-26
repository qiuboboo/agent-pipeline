from __future__ import annotations

import base64
import http.client
import io
import json
import logging
import ssl
import threading
import time
import urllib.error
import urllib.request
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List, Mapping, Optional, Sequence

import requests
from PIL import Image

from .config import ModelEndpointConfig
from .utils import extract_json_object, to_plain_text


LOGGER = logging.getLogger("benchmarkallinone.pipeline2.clients")


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
            "stream": True,
        }

    def _max_attempts(self) -> int:
        return max(1, int(self.config.max_attempts))

    def _retry_delay_seconds(self, attempt: int) -> float:
        base_delay = max(0.0, float(self.config.retry_base_delay_seconds))
        max_delay = max(base_delay, float(self.config.retry_max_delay_seconds))
        return min(max_delay, base_delay * (2 ** max(0, attempt - 1)))

    def _is_retryable_status(self, status_code: Optional[int]) -> bool:
        if status_code is None:
            return False
        return status_code in {403, 408, 409, 423, 425, 429} or status_code >= 500

    def _retry_after_seconds(self, headers: Optional[Mapping[str, Any]]) -> Optional[float]:
        if not self.config.respect_retry_after or not headers:
            return None
        raw_value = headers.get("Retry-After")
        if raw_value is None:
            return None
        text = to_plain_text(raw_value).strip()
        if not text:
            return None
        try:
            return max(0.0, float(text))
        except ValueError:
            pass
        try:
            retry_at = parsedate_to_datetime(text)
            return max(0.0, retry_at.timestamp() - time.time())
        except Exception:
            return None

    def _sleep_before_retry(self, attempt: int, retry_after_seconds: Optional[float] = None) -> None:
        delay_seconds = retry_after_seconds if retry_after_seconds is not None else self._retry_delay_seconds(attempt)
        time.sleep(max(0.0, delay_seconds))

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
        max_attempts = self._max_attempts()
        LOGGER.info(
            "[llm-request-start] endpoint=%s api_mode=chat_completions request_mode=%s max_attempts=%s timeout_seconds=%s url=%s",
            self.config.name,
            "multimodal" if has_images else "text",
            max_attempts,
            self.config.timeout_seconds,
            url,
        )
        for attempt in range(1, max_attempts + 1):
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
                    status_code = getattr(response, "status", None) or response.getcode()
                    content_type = response.headers.get("Content-Type", "")
                    raw_body = response.read().decode("utf-8", errors="replace")
                    body = None
                    streamed_content = None
                    if "text/event-stream" in content_type.lower():
                        stream_chunks: List[str] = []
                        for raw_line in raw_body.splitlines():
                            line = raw_line.strip()
                            if not line.startswith("data:"):
                                continue
                            data = line[5:].strip()
                            if not data or data == "[DONE]":
                                continue
                            try:
                                event = json.loads(data)
                            except json.JSONDecodeError:
                                continue
                            choices = event.get("choices") or []
                            if not choices:
                                continue
                            delta = choices[0].get("delta") or {}
                            piece = delta.get("content", "")
                            if isinstance(piece, list):
                                piece = "".join(item.get("text", "") for item in piece if isinstance(item, dict))
                            piece_text = to_plain_text(piece)
                            if piece_text:
                                stream_chunks.append(piece_text)
                        streamed_content = "".join(stream_chunks)
                    else:
                        body = json.loads(raw_body)
            except urllib.error.HTTPError as exc:
                elapsed = time.perf_counter() - started
                with self._usage_lock:
                    self.usage_totals["failed_request_count"] += 1
                    self.usage_totals["total_request_seconds"] += elapsed
                try:
                    error_body = exc.read().decode("utf-8", errors="ignore")
                except Exception:
                    error_body = ""
                retry_after_seconds = self._retry_after_seconds(getattr(exc, "headers", None))
                last_error_text = f"HTTP {exc.code}: {error_body[:240] or exc.reason}"
                retryable = self._is_retryable_status(exc.code)
                LOGGER.warning(
                    "[llm-request-http-error] endpoint=%s api_mode=chat_completions request_mode=%s attempt=%s/%s retryable=%s retry_after_seconds=%s elapsed_seconds=%.3f error=%s",
                    self.config.name,
                    "multimodal" if has_images else "text",
                    attempt,
                    max_attempts,
                    retryable,
                    retry_after_seconds,
                    elapsed,
                    last_error_text,
                )
                if retryable and attempt < max_attempts:
                    with self._usage_lock:
                        self.usage_totals["retry_count"] += 1
                    self._sleep_before_retry(attempt, retry_after_seconds=retry_after_seconds)
                    continue
                with self._usage_lock:
                    self.usage_totals["last_error"] = last_error_text
                return None
            except (urllib.error.URLError, http.client.RemoteDisconnected, ConnectionResetError, BrokenPipeError, ssl.SSLError, TimeoutError) as exc:
                elapsed = time.perf_counter() - started
                with self._usage_lock:
                    self.usage_totals["failed_request_count"] += 1
                    self.usage_totals["total_request_seconds"] += elapsed
                last_error_text = f"{type(exc).__name__}: {exc}"
                LOGGER.warning(
                    "[llm-request-transport-error] endpoint=%s api_mode=chat_completions request_mode=%s attempt=%s/%s elapsed_seconds=%.3f error=%s",
                    self.config.name,
                    "multimodal" if has_images else "text",
                    attempt,
                    max_attempts,
                    elapsed,
                    last_error_text,
                )
                if attempt < max_attempts:
                    with self._usage_lock:
                        self.usage_totals["retry_count"] += 1
                    self._sleep_before_retry(attempt)
                    continue
                with self._usage_lock:
                    self.usage_totals["last_error"] = last_error_text
                return None
            except json.JSONDecodeError as exc:
                elapsed = time.perf_counter() - started
                body_preview = (raw_body[:500] if isinstance(raw_body, str) else "").replace("\n", "\\n")
                with self._usage_lock:
                    self.usage_totals["failed_request_count"] += 1
                    self.usage_totals["total_request_seconds"] += elapsed
                last_error_text = (
                    f"JSONDecodeError: {exc}; status={status_code}; content_type={content_type!r}; body_preview={body_preview!r}"
                )
                LOGGER.warning(
                    "[llm-request-json-error] endpoint=%s api_mode=chat_completions request_mode=%s attempt=%s/%s elapsed_seconds=%.3f error=%s",
                    self.config.name,
                    "multimodal" if has_images else "text",
                    attempt,
                    max_attempts,
                    elapsed,
                    last_error_text,
                )
                if attempt < max_attempts:
                    with self._usage_lock:
                        self.usage_totals["retry_count"] += 1
                    self._sleep_before_retry(attempt)
                    continue
                with self._usage_lock:
                    self.usage_totals["last_error"] = last_error_text
                return None
            elapsed = time.perf_counter() - started
            usage = self._extract_usage(body or {})
            with self._usage_lock:
                self.usage_totals["total_request_seconds"] += elapsed
                if usage["total_tokens"] > 0:
                    self.usage_totals["requests_with_usage"] += 1
                for key, value in usage.items():
                    self.usage_totals[key] += value
            if streamed_content is not None:
                parsed = extract_json_object(to_plain_text(streamed_content))
                if not parsed:
                    with self._usage_lock:
                        self.usage_totals["failed_request_count"] += 1
                    last_error_text = "Response missing JSON object in streamed content."
                    LOGGER.warning(
                        "[llm-request-parse-miss] endpoint=%s api_mode=chat_completions request_mode=%s attempt=%s/%s elapsed_seconds=%.3f error=%s",
                        self.config.name,
                        "multimodal" if has_images else "text",
                        attempt,
                        max_attempts,
                        elapsed,
                        last_error_text,
                    )
                    if attempt < max_attempts:
                        with self._usage_lock:
                            self.usage_totals["retry_count"] += 1
                            self.usage_totals["last_error"] = last_error_text
                        self._sleep_before_retry(attempt)
                        continue
                    with self._usage_lock:
                        self.usage_totals["last_error"] = last_error_text
                    return None
            else:
                choices = body.get("choices") or []
                if not choices:
                    with self._usage_lock:
                        self.usage_totals["failed_request_count"] += 1
                    last_error_text = "Response missing choices."
                    LOGGER.warning(
                        "[llm-request-parse-miss] endpoint=%s api_mode=chat_completions request_mode=%s attempt=%s/%s elapsed_seconds=%.3f error=%s",
                        self.config.name,
                        "multimodal" if has_images else "text",
                        attempt,
                        max_attempts,
                        elapsed,
                        last_error_text,
                    )
                    if attempt < max_attempts:
                        with self._usage_lock:
                            self.usage_totals["retry_count"] += 1
                            self.usage_totals["last_error"] = last_error_text
                        self._sleep_before_retry(attempt)
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
                    with self._usage_lock:
                        self.usage_totals["failed_request_count"] += 1
                    last_error_text = "Response missing JSON object."
                    LOGGER.warning(
                        "[llm-request-parse-miss] endpoint=%s api_mode=chat_completions request_mode=%s attempt=%s/%s elapsed_seconds=%.3f error=%s",
                        self.config.name,
                        "multimodal" if has_images else "text",
                        attempt,
                        max_attempts,
                        elapsed,
                        last_error_text,
                    )
                    if attempt < max_attempts:
                        with self._usage_lock:
                            self.usage_totals["retry_count"] += 1
                            self.usage_totals["last_error"] = last_error_text
                        self._sleep_before_retry(attempt)
                        continue
                    with self._usage_lock:
                        self.usage_totals["last_error"] = last_error_text
                    return None
            with self._usage_lock:
                self.usage_totals["successful_request_count"] += 1
                self.usage_totals["last_error"] = None
            LOGGER.info(
                "[llm-request-success] endpoint=%s api_mode=chat_completions request_mode=%s attempt=%s/%s elapsed_seconds=%.3f total_tokens=%s",
                self.config.name,
                "multimodal" if has_images else "text",
                attempt,
                max_attempts,
                elapsed,
                usage.get("total_tokens", 0),
            )
            parsed["_llm_usage"] = usage
            parsed["_llm_elapsed_seconds"] = round(elapsed, 3)
            parsed["_llm_request_mode"] = "multimodal" if has_images else "text"
            parsed["_llm_endpoint_name"] = self.config.name
            return parsed
        with self._usage_lock:
            self.usage_totals["last_error"] = last_error_text
        return None

    def _build_responses_payload(self, system_prompt: str, user_content: Any) -> Dict[str, Any]:
        def to_responses_parts(content: Any) -> List[Dict[str, Any]]:
            parts: List[Dict[str, Any]] = []
            if isinstance(content, list):
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    item_type = item.get("type")
                    if item_type == "text":
                        text_value = to_plain_text(item.get("text"))
                        if text_value:
                            parts.append({"type": "input_text", "text": text_value})
                    elif item_type == "image_url":
                        image_url = item.get("image_url") or {}
                        url_value = to_plain_text(image_url.get("url"))
                        if url_value:
                            parts.append({"type": "input_image", "image_url": url_value})
            else:
                text_value = to_plain_text(content)
                if text_value:
                    parts.append({"type": "input_text", "text": text_value})
            return parts or [{"type": "input_text", "text": "{}"}]

        return {
            "model": self.config.model,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_prompt or ""}],
                },
                {
                    "role": "user",
                    "content": to_responses_parts(user_content),
                },
            ],
            "reasoning": {"effort": self.config.reasoning_effort},
            "stream": True,
        }

    def _read_sse_text(self, response: Any) -> str:
        chunks: List[str] = []
        for raw_line in response:
            try:
                if isinstance(raw_line, bytes):
                    line = raw_line.decode("utf-8", errors="ignore").strip()
                else:
                    line = str(raw_line).strip()
            except Exception:
                continue
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if not data or data == "[DONE]":
                continue
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                continue
            event_type = event.get("type")
            if event_type == "response.output_text.delta":
                delta = to_plain_text(event.get("delta"))
                if delta:
                    chunks.append(delta)
            elif event_type in {"response.completed", "response.output_text.done"}:
                continue
        return "".join(chunks)

    def _post_responses(self, payload: Dict[str, Any], has_images: bool = False) -> Optional[Dict[str, Any]]:
        if not self.config.enabled or not self.config.api_key:
            return None
        with self._usage_lock:
            self.usage_totals["request_count"] += 1
            if has_images:
                self.usage_totals["multimodal_request_count"] += 1
            else:
                self.usage_totals["text_request_count"] += 1
        url = self.config.base_url.rstrip("/") + "/responses"
        last_error_text = None
        max_attempts = self._max_attempts()
        LOGGER.info(
            "[llm-request-start] endpoint=%s api_mode=responses request_mode=%s max_attempts=%s timeout_seconds=%s url=%s",
            self.config.name,
            "multimodal" if has_images else "text",
            max_attempts,
            self.config.timeout_seconds,
            url,
        )
        for attempt in range(1, max_attempts + 1):
            started = time.perf_counter()
            try:
                session = requests.Session()
                session.trust_env = False
                with session.post(
                    url,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "text/event-stream",
                        "Connection": "close",
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                        "Authorization": f"Bearer {self.config.api_key}",
                    },
                    data=json.dumps(payload),
                    stream=True,
                    timeout=self.config.timeout_seconds,
                ) as response:
                    response.raise_for_status()
                    content = self._read_sse_text(response.iter_lines(decode_unicode=True))
            except requests.HTTPError as exc:
                elapsed = time.perf_counter() - started
                with self._usage_lock:
                    self.usage_totals["failed_request_count"] += 1
                    self.usage_totals["total_request_seconds"] += elapsed
                try:
                    error_body = exc.response.text[:240] if exc.response is not None else ""
                    status_code = exc.response.status_code if exc.response is not None else None
                    response_headers = exc.response.headers if exc.response is not None else None
                except Exception:
                    error_body = ""
                    status_code = None
                    response_headers = None
                retry_after_seconds = self._retry_after_seconds(response_headers)
                last_error_text = f"HTTP {status_code}: {error_body or exc}"
                retryable = self._is_retryable_status(status_code)
                LOGGER.warning(
                    "[llm-request-http-error] endpoint=%s api_mode=responses request_mode=%s attempt=%s/%s retryable=%s retry_after_seconds=%s elapsed_seconds=%.3f error=%s",
                    self.config.name,
                    "multimodal" if has_images else "text",
                    attempt,
                    max_attempts,
                    retryable,
                    retry_after_seconds,
                    elapsed,
                    last_error_text,
                )
                if retryable and attempt < max_attempts:
                    with self._usage_lock:
                        self.usage_totals["retry_count"] += 1
                    self._sleep_before_retry(attempt, retry_after_seconds=retry_after_seconds)
                    continue
                with self._usage_lock:
                    self.usage_totals["last_error"] = last_error_text
                return None
            except (requests.RequestException, json.JSONDecodeError, ssl.SSLError, TimeoutError) as exc:
                elapsed = time.perf_counter() - started
                with self._usage_lock:
                    self.usage_totals["failed_request_count"] += 1
                    self.usage_totals["total_request_seconds"] += elapsed
                last_error_text = f"{type(exc).__name__}: {exc}"
                LOGGER.warning(
                    "[llm-request-transport-error] endpoint=%s api_mode=responses request_mode=%s attempt=%s/%s elapsed_seconds=%.3f error=%s",
                    self.config.name,
                    "multimodal" if has_images else "text",
                    attempt,
                    max_attempts,
                    elapsed,
                    last_error_text,
                )
                if attempt < max_attempts:
                    with self._usage_lock:
                        self.usage_totals["retry_count"] += 1
                    self._sleep_before_retry(attempt)
                    continue
                with self._usage_lock:
                    self.usage_totals["last_error"] = last_error_text
                return None
            elapsed = time.perf_counter() - started
            parsed = extract_json_object(to_plain_text(content))
            if not parsed:
                with self._usage_lock:
                    self.usage_totals["failed_request_count"] += 1
                    self.usage_totals["total_request_seconds"] += elapsed
                last_error_text = "Response missing JSON object."
                LOGGER.warning(
                    "[llm-request-parse-miss] endpoint=%s api_mode=responses request_mode=%s attempt=%s/%s elapsed_seconds=%.3f error=%s",
                    self.config.name,
                    "multimodal" if has_images else "text",
                    attempt,
                    max_attempts,
                    elapsed,
                    last_error_text,
                )
                if attempt < max_attempts:
                    with self._usage_lock:
                        self.usage_totals["retry_count"] += 1
                        self.usage_totals["last_error"] = last_error_text
                    self._sleep_before_retry(attempt)
                    continue
                with self._usage_lock:
                    self.usage_totals["last_error"] = last_error_text
                return None
            with self._usage_lock:
                self.usage_totals["successful_request_count"] += 1
                self.usage_totals["total_request_seconds"] += elapsed
                self.usage_totals["last_error"] = None
            LOGGER.info(
                "[llm-request-success] endpoint=%s api_mode=responses request_mode=%s attempt=%s/%s elapsed_seconds=%.3f total_tokens=%s",
                self.config.name,
                "multimodal" if has_images else "text",
                attempt,
                max_attempts,
                elapsed,
                0,
            )
            parsed["_llm_usage"] = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "cached_tokens": 0,
                "reasoning_tokens": 0,
            }
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
        if self.config.api_mode == "responses":
            return self._post_responses(self._build_responses_payload(system_prompt, content_parts), has_images=has_images)
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

    @staticmethod
    def _shares_resource_pool(primary: ModelEndpointConfig, fallback: Optional[ModelEndpointConfig]) -> bool:
        if fallback is None:
            return False
        if not (primary.enabled and fallback.enabled and primary.api_key and fallback.api_key):
            return False
        return (
            primary.base_url.rstrip("/") == fallback.base_url.rstrip("/")
            and primary.api_key == fallback.api_key
            and primary.api_mode == fallback.api_mode
        )

    @classmethod
    def from_configs(cls, primary: ModelEndpointConfig, fallback: Optional[ModelEndpointConfig] = None) -> "ModelRouter":
        fallback_client: Optional[OpenAICompatibleClient] = None
        if fallback is not None:
            if cls._shares_resource_pool(primary, fallback):
                LOGGER.warning(
                    "[llm-fallback-disabled] primary and fallback share the same base_url/api_key/api_mode; disabling duplicate fallback endpoint=%s",
                    fallback.name,
                )
            else:
                fallback_client = OpenAICompatibleClient(fallback)
        return cls(
            primary=OpenAICompatibleClient(primary),
            fallback=fallback_client,
        )

    def chat_json(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        result = self.primary.chat_json(system_prompt, user_prompt)
        if result is not None:
            return result
        if self.fallback is not None:
            LOGGER.warning(
                "[llm-fallback] request_mode=text primary_endpoint=%s fallback_endpoint=%s primary_last_error=%s",
                self.primary.config.name,
                self.fallback.config.name,
                self.primary.snapshot_usage().get("last_error"),
            )
            return self.fallback.chat_json(system_prompt, user_prompt)
        return None

    def chat_json_with_images(self, system_prompt: str, user_prompt: str, images: Sequence[Image.Image]) -> Optional[Dict[str, Any]]:
        result = self.primary.chat_json_with_images(system_prompt, user_prompt, images)
        if result is not None:
            return result
        if self.fallback is not None:
            LOGGER.warning(
                "[llm-fallback] request_mode=multimodal primary_endpoint=%s fallback_endpoint=%s primary_last_error=%s",
                self.primary.config.name,
                self.fallback.config.name,
                self.primary.snapshot_usage().get("last_error"),
            )
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
