from __future__ import annotations

import http.client
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

import os

try:
    from .pipeline_utils import ensure_dir, extract_json_object, to_plain_text
except ImportError:
    from pipeline_utils import ensure_dir, extract_json_object, to_plain_text


class OpenAICompatibleClient:
    def __init__(self, config: Any):
        self.config = config
        self.last_error_reason: str = ""

    def chat_json(self, system_prompt: str, user_prompt: str, caller: str = "") -> Optional[Dict[str, Any]]:
        self.last_error_reason = ""
        if not self.config.enabled or not self.config.api_key:
            self.last_error_reason = "client disabled or missing api_key"
            return None
        debug = str(__import__("os").environ.get("PIPELINE_DEBUG_CHAT_JSON", "")).strip().lower() in {"1", "true", "yes", "on"}
        debug_log_path = __import__("os").environ.get("PIPELINE_DEBUG_CHAT_JSON_LOG", "").strip()

        def emit_debug(message: str) -> None:
            if not debug:
                return
            if debug_log_path:
                path = Path(debug_log_path)
                ensure_dir(path.parent)
                with path.open("a", encoding="utf-8") as file:
                    file.write(message)
                    file.write("\n")
                return
            print(message, flush=True)

        url = self.config.base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.config.temperature,
            "response_format": {"type": "json_object"},
            "reasoning_effort": self.config.reasoning_effort,
        }
        attempts = max(1, int(getattr(self.config, "retry_attempts", 1) or 1))
        backoff = float(getattr(self.config, "retry_backoff_seconds", 0.0) or 0.0)
        for attempt in range(1, attempts + 1):
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
            if debug and attempts > 1 and attempt > 1:
                emit_debug(f"[chat_json debug] caller={caller or 'unknown'} retrying attempt={attempt}/{attempts}")
            try:
                with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                    raw_body = response.read().decode("utf-8")
                    body = json.loads(raw_body)
            except urllib.error.HTTPError as exc:
                error_body = exc.read().decode("utf-8", errors="replace") if hasattr(exc, "read") else ""
                self.last_error_reason = f"HTTPError attempt={attempt}/{attempts} status={getattr(exc, 'code', None)} reason={getattr(exc, 'reason', None)} body_preview={error_body[:200]}"
                emit_debug(
                    f"[chat_json debug] caller={caller or 'unknown'} attempt={attempt}/{attempts} HTTPError status={getattr(exc, 'code', None)} reason={getattr(exc, 'reason', None)} body_preview={error_body[:400]}"
                )
                if attempt < attempts and getattr(exc, "code", None) in {408, 409, 425, 429, 500, 502, 503, 504}:
                    if backoff > 0:
                        time.sleep(backoff * attempt)
                    continue
                return None
            except urllib.error.URLError as exc:
                self.last_error_reason = f"URLError attempt={attempt}/{attempts} reason={exc}"
                emit_debug(f"[chat_json debug] caller={caller or 'unknown'} attempt={attempt}/{attempts} URLError reason={exc}")
                if attempt < attempts:
                    if backoff > 0:
                        time.sleep(backoff * attempt)
                    continue
                return None
            except http.client.RemoteDisconnected as exc:
                self.last_error_reason = f"RemoteDisconnected attempt={attempt}/{attempts} reason={exc}"
                emit_debug(f"[chat_json debug] caller={caller or 'unknown'} attempt={attempt}/{attempts} RemoteDisconnected reason={exc}")
                if attempt < attempts:
                    if backoff > 0:
                        time.sleep(backoff * attempt)
                    continue
                return None
            except ConnectionResetError as exc:
                self.last_error_reason = f"ConnectionResetError attempt={attempt}/{attempts} reason={exc}"
                emit_debug(f"[chat_json debug] caller={caller or 'unknown'} attempt={attempt}/{attempts} ConnectionResetError reason={exc}")
                if attempt < attempts:
                    if backoff > 0:
                        time.sleep(backoff * attempt)
                    continue
                return None
            except TimeoutError as exc:
                self.last_error_reason = f"TimeoutError attempt={attempt}/{attempts} reason={exc}"
                emit_debug(f"[chat_json debug] caller={caller or 'unknown'} attempt={attempt}/{attempts} TimeoutError reason={exc}")
                if attempt < attempts:
                    if backoff > 0:
                        time.sleep(backoff * attempt)
                    continue
                return None
            except json.JSONDecodeError as exc:
                self.last_error_reason = f"Response JSON decode failed attempt={attempt}/{attempts} error={exc}"
                emit_debug(f"[chat_json debug] caller={caller or 'unknown'} attempt={attempt}/{attempts} Response JSON decode failed error={exc}")
                return None
            choices = body.get("choices") or []
            if not choices:
                self.last_error_reason = f"Missing choices attempt={attempt}/{attempts} body_preview={json.dumps(body, ensure_ascii=False)[:200]}"
                emit_debug(f"[chat_json debug] caller={caller or 'unknown'} attempt={attempt}/{attempts} Missing choices body_preview={json.dumps(body, ensure_ascii=False)[:400]}")
                return None
            message = choices[0].get("message") or {}
            content = message.get("content", "")
            if isinstance(content, list):
                content = "\n".join(item.get("text", "") for item in content if isinstance(item, dict))
            parsed = extract_json_object(to_plain_text(content))
            if parsed is None:
                self.last_error_reason = f"Content JSON extraction failed attempt={attempt}/{attempts} content_preview={to_plain_text(content)[:200]}"
                emit_debug(f"[chat_json debug] caller={caller or 'unknown'} attempt={attempt}/{attempts} Content JSON extraction failed content_preview={to_plain_text(content)[:400]}")
            return parsed
        return None
