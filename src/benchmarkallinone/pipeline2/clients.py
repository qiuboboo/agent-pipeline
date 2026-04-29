from __future__ import annotations

import base64
import http.client
import io
import json
import logging
import re
import ssl
import threading
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Sequence

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

    def _wire_api(self) -> str:
        normalized = str(self.config.wire_api or "responses").strip().lower().replace("-", "_")
        return "responses" if normalized in {"responses", "response"} else "chat_completions"

    def _endpoint_url(self) -> str:
        suffix = "/responses" if self._wire_api() == "responses" else "/chat/completions"
        return self.config.base_url.rstrip("/") + suffix

    def _build_chat_completions_payload(
        self,
        system_prompt: str,
        user_content: Any,
        response_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "temperature": self.config.temperature,
            "reasoning_effort": self.config.reasoning_effort,
        }
        if response_schema:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": response_schema.get("name", "structured_output"),
                    "strict": bool(response_schema.get("strict", True)),
                    "schema": response_schema.get("schema") or {},
                },
            }
        else:
            payload["response_format"] = {"type": "json_object"}
        return payload

    def _build_responses_content(self, user_content: Any) -> List[Dict[str, Any]]:
        if isinstance(user_content, str):
            text_value = to_plain_text(user_content)
            return [{"type": "input_text", "text": text_value or "{}"}]

        content_parts: List[Dict[str, Any]] = []
        if isinstance(user_content, list):
            for item in user_content:
                if not isinstance(item, dict):
                    continue
                part_type = item.get("type")
                if part_type == "text":
                    text_value = to_plain_text(item.get("text"))
                    if text_value:
                        content_parts.append({"type": "input_text", "text": text_value})
                elif part_type == "image_url":
                    image_url = item.get("image_url") or {}
                    url_value = to_plain_text(image_url.get("url"))
                    if url_value:
                        content_parts.append({"type": "input_image", "image_url": url_value})
        return content_parts or [{"type": "input_text", "text": "{}"}]

    def _build_responses_payload(
        self,
        system_prompt: str,
        user_content: Any,
        response_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        input_items: List[Dict[str, Any]] = []
        system_text = to_plain_text(system_prompt)
        if system_text:
            input_items.append(
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_text}],
                }
            )
        input_items.append(
            {
                "role": "user",
                "content": self._build_responses_content(user_content),
            }
        )
        payload: Dict[str, Any] = {
            "model": self.config.model,
            "input": input_items,
            "reasoning": {"effort": self.config.reasoning_effort},
            "temperature": self.config.temperature,
        }
        if response_schema:
            payload["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": response_schema.get("name", "structured_output"),
                    "strict": bool(response_schema.get("strict", True)),
                    "schema": response_schema.get("schema") or {},
                }
            }
        else:
            payload["text"] = {"format": {"type": "json_object"}}
        if self.config.disable_response_storage:
            payload["store"] = False
        return payload

    def _build_payload(
        self,
        system_prompt: str,
        user_content: Any,
        response_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if self._wire_api() == "responses":
            return self._build_responses_payload(system_prompt, user_content, response_schema=response_schema)
        return self._build_chat_completions_payload(system_prompt, user_content, response_schema=response_schema)

    def _extract_response_text(self, body: Dict[str, Any]) -> str:
        if self._wire_api() == "responses":
            output_text = body.get("output_text")
            if isinstance(output_text, str) and output_text.strip():
                return output_text
            fragments: List[str] = []
            for item in body.get("output") or []:
                if not isinstance(item, dict):
                    continue
                if item.get("type") in {"output_text", "text"}:
                    text_value = item.get("text")
                    if isinstance(text_value, dict):
                        text_value = text_value.get("value") or text_value.get("text")
                    if isinstance(text_value, str) and text_value:
                        fragments.append(text_value)
                for content_item in item.get("content") or []:
                    if not isinstance(content_item, dict):
                        continue
                    if content_item.get("type") not in {"output_text", "text"}:
                        continue
                    text_value = content_item.get("text")
                    if isinstance(text_value, dict):
                        text_value = text_value.get("value") or text_value.get("text")
                    if isinstance(text_value, str) and text_value:
                        fragments.append(text_value)
            return "\n".join(fragment for fragment in fragments if fragment)

        choices = body.get("choices") or []
        if not choices:
            return ""
        message = choices[0].get("message") or {}
        content = message.get("content", "")
        if isinstance(content, list):
            content = "\n".join(item.get("text", "") for item in content if isinstance(item, dict))
        return to_plain_text(content)

    def _read_response_bytes(self, response: Any, *, request_timeout: float) -> bytes:
        raw_chunks: List[bytes] = []
        total_bytes = 0
        while True:
            try:
                raw_socket = getattr(getattr(getattr(response, "fp", None), "raw", None), "_sock", None)
                if raw_socket is not None:
                    raw_socket.settimeout(max(0.1, float(request_timeout)))
            except Exception:
                pass
            chunk = response.read(65536)
            if not chunk:
                break
            raw_chunks.append(chunk)
            total_bytes += len(chunk)
            if total_bytes > 8_000_000:
                raise ValueError("Model response body exceeded 8MB and was treated as invalid.")
        return b"".join(raw_chunks)

    def _read_sse_response_body(self, response: Any, *, request_timeout: float) -> Dict[str, Any]:
        """Read a streaming SSE body and return a JSON-like body.

        Supports two wire formats:

        1. Responses API SSE (used by msutools.cn, cf.cuylerchen.uk in
           ``responses`` mode):
           ``event: response.output_text.delta``
           ``data: {"type":"response.output_text.delta","delta":"..."}``

        2. Chat Completions API SSE (used by cf.cuylerchen.uk in
           ``chat_completions`` mode):
           ``data: {"choices":[{"delta":{"content":"..."},"index":0}]}``

        In both cases the stream is collapsed into ``{output_text, usage}``
        while preserving a compact raw-event preview for diagnostics.
        """
        delta_fragments: List[str] = []
        final_text_fragments: List[str] = []
        raw_events: List[Dict[str, Any]] = []
        usage: Dict[str, Any] = {}
        total_bytes = 0
        current_event = "message"
        data_lines: List[str] = []

        def _consume_event(event_name: str, lines: List[str]) -> None:
            nonlocal usage
            if not lines:
                return
            data = "\n".join(lines).strip()
            if not data or data == "[DONE]":
                return
            parsed: Any = None
            try:
                parsed = json.loads(data)
            except json.JSONDecodeError:
                raw_events.append({"event": event_name, "data": data[:500]})
                return
            if isinstance(parsed, dict):
                raw_events.append({"event": event_name, "data": parsed})
                parsed_usage = parsed.get("usage")
                if isinstance(parsed_usage, dict) and parsed_usage:
                    usage = parsed_usage
                # Chat Completions SSE: delta is nested in choices[0].delta.content
                choices = parsed.get("choices")
                if isinstance(choices, list) and choices:
                    delta = choices[0].get("delta")
                    if isinstance(delta, dict):
                        content = delta.get("content", "")
                        if isinstance(content, str) and content:
                            delta_fragments.append(content)
                # Responses API SSE: delta is a top-level string
                delta = parsed.get("delta")
                if isinstance(delta, str) and delta:
                    delta_fragments.append(delta)
                # Fallback: top-level text field
                text_value = parsed.get("text")
                if isinstance(text_value, str) and text_value:
                    if event_name == "response.output_text.delta":
                        delta_fragments.append(text_value)
                    elif event_name in {"response.output_text.done", "response.output_text.completed"}:
                        final_text_fragments.append(text_value)
                if event_name in {"response.completed", "response.done"}:
                    completed_text = self._extract_response_text(parsed)
                    if completed_text:
                        final_text_fragments.append(completed_text)
            else:
                raw_events.append({"event": event_name, "data": parsed})

        while True:
            try:
                raw_socket = getattr(getattr(getattr(response, "fp", None), "raw", None), "_sock", None)
                if raw_socket is not None:
                    raw_socket.settimeout(max(0.1, float(request_timeout)))
            except Exception:
                pass
            line_bytes = response.readline(65536)
            if not line_bytes:
                _consume_event(current_event, data_lines)
                break
            total_bytes += len(line_bytes)
            if total_bytes > 8_000_000:
                raise ValueError("Model SSE response body exceeded 8MB and was treated as invalid.")
            line = line_bytes.decode("utf-8", errors="replace").rstrip("\r\n")
            if line == "":
                _consume_event(current_event, data_lines)
                current_event = "message"
                data_lines = []
                continue
            if line.startswith(":"):
                continue
            if line.startswith("event:"):
                current_event = line[len("event:") :].strip() or "message"
                continue
            if line.startswith("data:"):
                data_lines.append(line[len("data:") :].lstrip())

        # Prefer the concatenated deltas because they preserve the exact streamed
        # model text. Use final/done text only when no deltas were emitted.
        output_text = "".join(delta_fragments) if delta_fragments else "".join(final_text_fragments)
        return {
            "output_text": output_text,
            "usage": usage,
            "_sse_event_count": len(raw_events),
            "_sse_events_preview": raw_events[:20],
        }

    def _should_stream(self) -> bool:
        """Whether the API call should use streaming.

        Returns True when the backend requires stream=true, regardless of
        whether we are using the Responses API or Chat Completions API wire format.
        """
        base_url = str(self.config.base_url or "").lower()
        return any(host in base_url for host in {"cf.cuylerchen.uk", "msutools.cn"})

    def _response_is_event_stream(self, response: Any) -> bool:
        content_type = ""
        headers = getattr(response, "headers", None)
        if headers is not None:
            get_content_type = getattr(headers, "get_content_type", None)
            if callable(get_content_type):
                try:
                    content_type = get_content_type() or ""
                except Exception:
                    content_type = ""
            if not content_type:
                try:
                    content_type = headers.get("Content-Type", "") or headers.get("content-type", "")
                except Exception:
                    content_type = ""
        if not content_type:
            getheader = getattr(response, "getheader", None)
            if callable(getheader):
                try:
                    content_type = getheader("Content-Type") or ""
                except Exception:
                    content_type = ""
        return "text/event-stream" in str(content_type).lower()

    def _post_json(
        self,
        payload: Dict[str, Any],
        has_images: bool = False,
        *,
        deadline_monotonic: float | None = None,
        max_attempts: int = 3,
    ) -> Optional[Dict[str, Any]]:
        if not self.config.enabled or not self.config.api_key:
            return None
        with self._usage_lock:
            self.usage_totals["request_count"] += 1
            if has_images:
                self.usage_totals["multimodal_request_count"] += 1
            else:
                self.usage_totals["text_request_count"] += 1
        url = self._endpoint_url()
        use_streaming = self._should_stream()
        request_payload = dict(payload)
        if use_streaming:
            request_payload["stream"] = True
        last_error_text = None
        effective_max_attempts = max(1, int(max_attempts))
        deadline = deadline_monotonic
        LOGGER.info(
            "[llm-request-start] endpoint=%s wire_api=%s request_mode=%s max_attempts=%s timeout_seconds=%s deadline_seconds=%s url=%s",
            self.config.name,
            self._wire_api(),
            "multimodal" if has_images else "text",
            effective_max_attempts,
            self.config.timeout_seconds,
            round(max(0.0, deadline - time.monotonic()), 3) if deadline is not None else None,
            url,
        )
        for attempt in range(1, effective_max_attempts + 1):
            remaining_seconds = (deadline - time.monotonic()) if deadline is not None else None
            if remaining_seconds is not None and remaining_seconds <= 0:
                last_error_text = last_error_text or "Retry deadline exceeded before a successful model response was received."
                LOGGER.warning(
                    "[llm-request-deadline-exhausted] endpoint=%s wire_api=%s request_mode=%s attempt=%s/%s error=%s",
                    self.config.name,
                    self._wire_api(),
                    "multimodal" if has_images else "text",
                    attempt,
                    effective_max_attempts,
                    last_error_text,
                )
                break
            started = time.perf_counter()
            req = urllib.request.Request(
                url,
                data=json.dumps(request_payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream" if use_streaming else "application/json",
                    "Connection": "close",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "Authorization": f"Bearer {self.config.api_key}",
                },
                method="POST",
            )
            request_timeout = (
                max(0.1, min(float(self.config.timeout_seconds), float(remaining_seconds)))
                if remaining_seconds is not None
                else max(0.1, float(self.config.timeout_seconds))
            )
            try:
                with urllib.request.urlopen(req, timeout=request_timeout) as response:
                    response_is_event_stream = use_streaming or self._response_is_event_stream(response)
                    if response_is_event_stream:
                        body = self._read_sse_response_body(
                            response,
                            request_timeout=request_timeout,
                        )
                    else:
                        response_bytes = self._read_response_bytes(
                            response,
                            request_timeout=request_timeout,
                        )
                        response_text = response_bytes.decode("utf-8", errors="replace")
                        stripped_response_text = response_text.lstrip()
                        if stripped_response_text[:1] not in {"{", "["}:
                            elapsed = time.perf_counter() - started
                            with self._usage_lock:
                                self.usage_totals["failed_request_count"] += 1
                                self.usage_totals["total_request_seconds"] += elapsed
                            preview = " ".join(stripped_response_text[:240].split())
                            last_error_text = f"Non-JSON HTTP response. body_preview={preview}"
                            with self._usage_lock:
                                self.usage_totals["last_error"] = last_error_text
                            LOGGER.warning(
                                "[llm-request-non-json] endpoint=%s wire_api=%s request_mode=%s attempt=%s/%s elapsed_seconds=%.3f error=%s",
                                self.config.name,
                                self._wire_api(),
                                "multimodal" if has_images else "text",
                                attempt,
                                effective_max_attempts,
                                elapsed,
                                last_error_text,
                            )
                            return None
                        body = json.loads(response_text)
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
                can_retry = attempt < effective_max_attempts and (deadline is None or (deadline - time.monotonic()) > 0)
                LOGGER.warning(
                    "[llm-request-http-error] endpoint=%s wire_api=%s request_mode=%s attempt=%s/%s retryable=%s elapsed_seconds=%.3f error=%s",
                    self.config.name,
                    self._wire_api(),
                    "multimodal" if has_images else "text",
                    attempt,
                    effective_max_attempts,
                    retryable,
                    elapsed,
                    last_error_text,
                )
                if retryable and can_retry:
                    with self._usage_lock:
                        self.usage_totals["retry_count"] += 1
                    if deadline is None:
                        time.sleep(min(2.0, 0.5 * attempt))
                    else:
                        time.sleep(min(2.0, 0.5 * attempt, max(0.0, deadline - time.monotonic())))
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
                can_retry = attempt < effective_max_attempts and (deadline is None or (deadline - time.monotonic()) > 0)
                LOGGER.warning(
                    "[llm-request-transport-error] endpoint=%s wire_api=%s request_mode=%s attempt=%s/%s elapsed_seconds=%.3f error=%s",
                    self.config.name,
                    self._wire_api(),
                    "multimodal" if has_images else "text",
                    attempt,
                    effective_max_attempts,
                    elapsed,
                    last_error_text,
                )
                if can_retry:
                    with self._usage_lock:
                        self.usage_totals["retry_count"] += 1
                    if deadline is None:
                        time.sleep(min(2.0, 0.5 * attempt))
                    else:
                        time.sleep(min(2.0, 0.5 * attempt, max(0.0, deadline - time.monotonic())))
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
            response_text = self._extract_response_text(body)
            if not response_text:
                last_error_text = "Response missing text content."
                with self._usage_lock:
                    self.usage_totals["failed_request_count"] += 1
                can_retry = attempt < effective_max_attempts and (deadline is None or (deadline - time.monotonic()) > 0)
                LOGGER.warning(
                    "[llm-request-parse-miss] endpoint=%s wire_api=%s request_mode=%s attempt=%s/%s elapsed_seconds=%.3f error=%s",
                    self.config.name,
                    self._wire_api(),
                    "multimodal" if has_images else "text",
                    attempt,
                    effective_max_attempts,
                    elapsed,
                    last_error_text,
                )
                if can_retry:
                    with self._usage_lock:
                        self.usage_totals["retry_count"] += 1
                        self.usage_totals["last_error"] = last_error_text
                    if deadline is None:
                        time.sleep(min(2.0, 0.5 * attempt))
                    else:
                        time.sleep(min(2.0, 0.5 * attempt, max(0.0, deadline - time.monotonic())))
                    continue
                with self._usage_lock:
                    self.usage_totals["last_error"] = last_error_text
                return None
            parsed = extract_json_object(response_text)
            if not parsed:
                raw_preview = json.dumps(body, ensure_ascii=False)[:400]
                last_error_text = f"Response missing JSON object. body_preview={raw_preview}"
                with self._usage_lock:
                    self.usage_totals["failed_request_count"] += 1
                can_retry = attempt < effective_max_attempts and (deadline is None or (deadline - time.monotonic()) > 0)
                LOGGER.warning(
                    "[llm-request-parse-miss] endpoint=%s wire_api=%s request_mode=%s attempt=%s/%s elapsed_seconds=%.3f error=%s",
                    self.config.name,
                    self._wire_api(),
                    "multimodal" if has_images else "text",
                    attempt,
                    effective_max_attempts,
                    elapsed,
                    last_error_text,
                )
                if can_retry:
                    with self._usage_lock:
                        self.usage_totals["retry_count"] += 1
                        self.usage_totals["last_error"] = last_error_text
                    if deadline is None:
                        time.sleep(min(2.0, 0.5 * attempt))
                    else:
                        time.sleep(min(2.0, 0.5 * attempt, max(0.0, deadline - time.monotonic())))
                    continue
                with self._usage_lock:
                    self.usage_totals["last_error"] = last_error_text
                return None
            with self._usage_lock:
                self.usage_totals["successful_request_count"] += 1
                self.usage_totals["last_error"] = None
            LOGGER.info(
                "[llm-request-success] endpoint=%s wire_api=%s request_mode=%s attempt=%s/%s elapsed_seconds=%.3f total_tokens=%s",
                self.config.name,
                self._wire_api(),
                "multimodal" if has_images else "text",
                attempt,
                effective_max_attempts,
                elapsed,
                usage.get("total_tokens", 0),
            )
            parsed["_llm_usage"] = usage
            parsed["_llm_elapsed_seconds"] = round(elapsed, 3)
            parsed["_llm_request_mode"] = "multimodal" if has_images else "text"
            parsed["_llm_endpoint_name"] = self.config.name
            return parsed
        with self._usage_lock:
            self.usage_totals["last_error"] = last_error_text or (
                "Retry deadline exceeded before a successful model response was received."
                if deadline is not None
                else "Exhausted retry attempts without a successful model response."
            )
        return None

    def image_to_data_url(self, image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.convert("RGB").save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"

    def chat_json_parts(
        self,
        system_prompt: str,
        user_parts: Sequence[Dict[str, Any]],
        response_schema: Optional[Dict[str, Any]] = None,
        *,
        deadline_monotonic: float | None = None,
        max_attempts: int = 3,
    ) -> Optional[Dict[str, Any]]:
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
        return self._post_json(
            self._build_payload(system_prompt, content_parts, response_schema=response_schema),
            has_images=has_images,
            deadline_monotonic=deadline_monotonic,
            max_attempts=max_attempts,
        )

    def chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Optional[Dict[str, Any]] = None,
        *,
        deadline_monotonic: float | None = None,
        max_attempts: int = 3,
    ) -> Optional[Dict[str, Any]]:
        return self.chat_json_parts(
            system_prompt,
            [{"type": "text", "text": user_prompt}],
            response_schema=response_schema,
            deadline_monotonic=deadline_monotonic,
            max_attempts=max_attempts,
        )

    def chat_json_with_images(
        self,
        system_prompt: str,
        user_prompt: str,
        images: Sequence[Image.Image],
        response_schema: Optional[Dict[str, Any]] = None,
        *,
        deadline_monotonic: float | None = None,
        max_attempts: int = 3,
    ) -> Optional[Dict[str, Any]]:
        user_parts: List[Dict[str, Any]] = [{"type": "text", "text": user_prompt}]
        for image in list(images)[:3]:
            if isinstance(image, Image.Image):
                user_parts.append({"type": "image", "image": image})
        return self.chat_json_parts(
            system_prompt,
            user_parts,
            response_schema=response_schema,
            deadline_monotonic=deadline_monotonic,
            max_attempts=max_attempts,
        )


class ModelRouter:
    def __init__(self, primary: OpenAICompatibleClient, fallback: Optional[OpenAICompatibleClient] = None):
        self.primary = primary
        self.fallback = None

    @classmethod
    def from_configs(cls, primary: ModelEndpointConfig) -> "ModelRouter":
        return cls(
            primary=OpenAICompatibleClient(primary),
            fallback=None,
        )

    def _enabled_clients(self) -> List[OpenAICompatibleClient]:
        clients: List[OpenAICompatibleClient] = []
        if self.primary.config.enabled and self.primary.config.api_key:
            clients.append(self.primary)
        return clients

    def _router_retry_deadline(self) -> float:
        clients = self._enabled_clients()
        timeout_budget = sum(max(1.0, float(client.config.timeout_seconds)) for client in clients) or 60.0
        return time.monotonic() + max(30.0, timeout_budget * 3.0)

    def _client_call_timeout(self, client: OpenAICompatibleClient) -> float:
        return max(10.0, float(client.config.timeout_seconds) + 90.0)

    def _last_error_is_permanent(self, client: OpenAICompatibleClient) -> bool:
        last_error = client.snapshot_usage().get("last_error")
        if not isinstance(last_error, str):
            return False
        permanent_markers = (
            "Non-JSON HTTP response.",
            "browser_signature_banned",
            "Access denied",
            "无效的令牌",
            "invalid token",
        )
        if any(marker in last_error for marker in permanent_markers):
            return True
        match = re.search(r"\bHTTP\s+(\d{3})\b", last_error)
        if match is None:
            return False
        status_code = int(match.group(1))
        return 400 <= status_code < 500 and status_code not in {408, 409, 429}

    def _mark_client_timeout(self, client: OpenAICompatibleClient, operation_name: str, timeout_seconds: float) -> None:
        with client._usage_lock:
            client.usage_totals["failed_request_count"] += 1
            client.usage_totals["last_error"] = (
                f"{operation_name} timed out after {round(timeout_seconds, 1)}s before the client returned a response."
            )
        LOGGER.warning(
            "[llm-client-timeout] endpoint=%s operation=%s timeout_seconds=%.1f",
            client.config.name,
            operation_name,
            timeout_seconds,
        )

    def _invoke_client_method_with_timeout(
        self,
        client: OpenAICompatibleClient,
        method_name: str,
        *args: Any,
    ) -> Optional[Dict[str, Any]]:
        timeout_seconds = self._client_call_timeout(client)
        result_holder: Dict[str, Optional[Dict[str, Any]]] = {"value": None}
        error_holder: Dict[str, BaseException] = {}
        LOGGER.info(
            "[llm-client-call-start] endpoint=%s operation=%s timeout_seconds=%.1f",
            client.config.name,
            method_name,
            timeout_seconds,
        )

        def _target() -> None:
            try:
                method = getattr(client, method_name)
                deadline = time.monotonic() + max(30.0, float(client.config.timeout_seconds) + 60.0)
                result_holder["value"] = method(*args, deadline_monotonic=deadline, max_attempts=2)
            except BaseException as exc:  # pragma: no cover - defensive bridge for unexpected client failures
                error_holder["error"] = exc

        worker = threading.Thread(target=_target, daemon=True)
        started = time.perf_counter()
        worker.start()
        worker.join(timeout_seconds)
        elapsed = time.perf_counter() - started
        if worker.is_alive():
            self._mark_client_timeout(client, method_name, timeout_seconds)
            return None
        if "error" in error_holder:
            LOGGER.exception(
                "[llm-client-call-error] endpoint=%s operation=%s elapsed_seconds=%.3f",
                client.config.name,
                method_name,
                elapsed,
                exc_info=error_holder["error"],
            )
            raise error_holder["error"]
        LOGGER.info(
            "[llm-client-call-done] endpoint=%s operation=%s elapsed_seconds=%.3f success=%s last_error=%s",
            client.config.name,
            method_name,
            elapsed,
            result_holder["value"] is not None,
            client.snapshot_usage().get("last_error"),
        )
        return result_holder["value"]

    def chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        return self._invoke_client_method_with_timeout(self.primary, "chat_json", system_prompt, user_prompt, response_schema)

    def chat_json_with_images(
        self,
        system_prompt: str,
        user_prompt: str,
        images: Sequence[Image.Image],
        response_schema: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        return self._invoke_client_method_with_timeout(
            self.primary,
            "chat_json_with_images",
            system_prompt,
            user_prompt,
            images,
            response_schema,
        )

    def has_available_endpoint(self) -> bool:
        return bool(self.primary.config.enabled and self.primary.config.api_key)

    def ensure_available(self, operation_name: str) -> None:
        if self.has_available_endpoint():
            return
        raise RuntimeError(
            f"[{operation_name}] No enabled model endpoint has an API key. "
            "Set `OPENAI_API_KEY` or provide endpoint-specific `models.*.api_key` values before running the live pipeline."
        )

    def last_error_summary(self) -> Dict[str, Any]:
        return {
            "primary_last_error": self.primary.snapshot_usage().get("last_error"),
        }

    def usage_summary(self) -> Dict[str, Any]:
        return {
            "primary": self.primary.snapshot_usage(),
        }
