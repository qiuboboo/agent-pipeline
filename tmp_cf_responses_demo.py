from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import requests


BASE_URL = os.environ.get("CF_BASE_URL", "https://cf.cuylerchen.uk/openai")
API_KEY = os.environ.get("CF_API_KEY", "YOUR_API_KEY_HERE")
MODEL = os.environ.get("CF_MODEL", "gpt-5.4")
REASONING_EFFORT = os.environ.get("CF_REASONING_EFFORT", "high")
TIMEOUT_SECONDS = float(os.environ.get("CF_TIMEOUT_SECONDS", "180"))


def build_payload(system_prompt: str, user_text: str) -> Dict[str, Any]:
    return {
        "model": MODEL,
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": system_prompt}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": user_text}],
            },
        ],
        "reasoning": {"effort": REASONING_EFFORT},
        "stream": True,
    }


def extract_json_object(text: str) -> Dict[str, Any] | None:
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        ch = text[index]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                snippet = text[start : index + 1]
                try:
                    return json.loads(snippet)
                except json.JSONDecodeError:
                    return None
    return None


def read_sse_text(response: requests.Response) -> str:
    chunks: List[str] = []
    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue
        line = line.strip()
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
            delta = event.get("delta") or ""
            if delta:
                chunks.append(str(delta))
    return "".join(chunks)


def main() -> int:
    if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
        raise SystemExit("Please set CF_API_KEY before running this demo.")

    system_prompt = "You are a JSON-only assistant. Return valid JSON only."
    user_text = 'Return exactly: {"ok": true, "source": "cf-demo"}'
    payload = build_payload(system_prompt, user_text)
    url = BASE_URL.rstrip("/") + "/responses"

    with requests.Session() as session:
        session.trust_env = False
        with session.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "Authorization": f"Bearer {API_KEY}",
            },
            data=json.dumps(payload),
            stream=True,
            timeout=TIMEOUT_SECONDS,
        ) as response:
            response.raise_for_status()
            text = read_sse_text(response)

    parsed = extract_json_object(text)
    print("RAW_TEXT:")
    print(text)
    print("\nPARSED_JSON:")
    print(json.dumps(parsed, ensure_ascii=False, indent=2) if parsed is not None else "<no json found>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
