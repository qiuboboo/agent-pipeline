from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import numpy as np
from PIL import Image


NULL_LIKE_STRINGS = {"null", "none", "nan", "n/a", "na", "[]", "{}"}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, bytes):
        return f"<bytes:{len(value)}>"
    if isinstance(value, Image.Image):
        return f"<PIL.Image mode={value.mode} size={value.size}>"
    raise TypeError(f"Object of type {type(value)!r} is not JSON serializable")


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2, default=json_default)


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False, default=json_default))
            file.write("\n")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_digest(parts: Sequence[str], length: int = 24) -> str:
    payload = "||".join(parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:length]


def to_plain_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return "\n".join(to_plain_text(item) for item in value if to_plain_text(item))
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def is_null_like_text(text: str) -> bool:
    normalized = normalize_whitespace(text).strip().lower()
    return normalized in NULL_LIKE_STRINGS


def is_missing_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip() or is_null_like_text(value)
    if isinstance(value, (list, tuple, set)):
        if not value:
            return True
        return all(is_missing_value(item) for item in value)
    if isinstance(value, dict):
        return not value
    return False


def parse_choice_map(value: Any) -> Dict[str, str]:
    if is_missing_value(value):
        return {}
    if isinstance(value, dict):
        choices: Dict[str, str] = {}
        for key, item in value.items():
            label = normalize_whitespace(str(key)).strip().upper()
            text = normalize_whitespace(to_plain_text(item))
            if re.fullmatch(r"[A-H]", label) and text and not is_null_like_text(text):
                choices[label] = text
        return choices
    if isinstance(value, (list, tuple)):
        choices = {}
        for index, item in enumerate(value):
            label = chr(ord("A") + index)
            text = normalize_whitespace(to_plain_text(item))
            if text and not is_null_like_text(text):
                choices[label] = text
        return choices
    text = normalize_whitespace(to_plain_text(value))
    if not text or is_null_like_text(text):
        return {}
    choices: Dict[str, str] = {}
    current_key: Optional[str] = None
    current_value: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        match = re.match(r"^[\(\[]?([A-H])[\)\].:]?\s*(.*)$", stripped)
        if match:
            if current_key is not None:
                choices[current_key] = normalize_whitespace(" ".join(current_value))
            current_key = match.group(1).upper()
            current_value = [match.group(2).strip()]
        elif current_key is not None and stripped:
            current_value.append(stripped)
    if current_key is not None:
        choices[current_key] = normalize_whitespace(" ".join(current_value))
    return {key: item for key, item in choices.items() if item and not is_null_like_text(item)}


def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        snippet = text[start : end + 1]
        try:
            return json.loads(snippet)
        except json.JSONDecodeError:
            return None
    return None


def expand_env_placeholders(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    pattern = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
    return pattern.sub(lambda match: os.environ.get(match.group(1), match.group(0)), value)


def is_unresolved_env_placeholder(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"\$\{[A-Za-z_][A-Za-z0-9_]*\}", value.strip()))
