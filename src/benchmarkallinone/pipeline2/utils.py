from __future__ import annotations

import json
import os
import re
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


NULL_LIKE_STRINGS = {"null", "none", "nan", "n/a", "na", "[]", "{}", ""}
_ENV_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}")
_SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[。！？!?\.])\s+")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value)!r} is not JSON serializable")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


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


def to_plain_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return "\n".join(part for part in (to_plain_text(item) for item in value) if part)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def normalize_whitespace(text: Any) -> str:
    value = to_plain_text(text).replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def canonicalize_free_text(text: Any) -> str:
    value = normalize_whitespace(text).casefold()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[`*_~]", "", value)
    value = re.sub(r"[，。；;：:、,.!?！？]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def canonicalize_answer_text(text: Any) -> str:
    value = normalize_whitespace(text)
    if not value:
        return ""
    value = re.sub(r"[。．\.,，；;:：!?！？]+$", "", value)
    value = value.replace(" ", "")
    return value.casefold()


def is_null_like(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return canonicalize_free_text(value) in NULL_LIKE_STRINGS
    if isinstance(value, (list, tuple, set)):
        return len(value) == 0 or all(is_null_like(item) for item in value)
    if isinstance(value, dict):
        return not value
    return False


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def stable_digest(parts: Sequence[str], length: int = 24) -> str:
    payload = "||".join(parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:length]


def env_expand(value: Any, env: Optional[Dict[str, str]] = None) -> Any:
    env_map = env or os.environ
    if isinstance(value, dict):
        return {key: env_expand(item, env_map) for key, item in value.items()}
    if isinstance(value, list):
        return [env_expand(item, env_map) for item in value]
    if not isinstance(value, str):
        return value

    def _replace(match: re.Match[str]) -> str:
        return env_map.get(match.group(1), "")

    return _ENV_PATTERN.sub(_replace, value)


def _sanitize_json_like_text(text: str) -> str:
    value = text.strip()
    if value.startswith("```"):
        value = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", value)
        value = re.sub(r"\s*```$", "", value)
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"\\(?![\"\\/bfnrtu])", r"\\\\", value)
    value = re.sub(r",\s*([}\]])", r"\1", value)
    return value


def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    text = text.strip()
    candidates = [text, _sanitize_json_like_text(text)]
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        snippet = text[start : end + 1]
        snippet_candidates = [snippet, _sanitize_json_like_text(snippet)]
        for candidate in snippet_candidates:
            try:
                parsed = json.loads(candidate)
                return parsed if isinstance(parsed, dict) else None
            except json.JSONDecodeError:
                continue
    return None


def split_sentences(text: Any) -> List[str]:
    value = normalize_whitespace(text)
    if not value:
        return []
    raw = _SENTENCE_SPLIT_PATTERN.split(value)
    items: List[str] = []
    for chunk in raw:
        chunk = chunk.strip()
        if not chunk:
            continue
        sub_parts = [part.strip() for part in chunk.split("\n") if part.strip()]
        items.extend(sub_parts)
    return items


def split_multiline_answer(text: Any) -> List[str]:
    value = normalize_whitespace(text)
    if not value:
        return []
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    return lines or [value]


def split_or_alternatives(text: str) -> List[str]:
    value = normalize_whitespace(text)
    if not value:
        return []
    parts = re.split(r"\s+(?:or|OR|Or|或者|或)\s+", value)
    return [part.strip() for part in parts if part.strip()]


def unique_list(items: Sequence[Any]) -> List[Any]:
    output: List[Any] = []
    seen = set()
    for item in items:
        marker = json.dumps(item, ensure_ascii=False, sort_keys=True) if isinstance(item, (dict, list)) else repr(item)
        if marker in seen:
            continue
        seen.add(marker)
        output.append(item)
    return output


def truncate_text(text: Any, limit: int = 200) -> str:
    value = normalize_whitespace(text)
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 3)] + "..."


def lexical_overlap_score(a: Any, b: Any) -> float:
    left = {token for token in re.split(r"\W+", canonicalize_free_text(a)) if token}
    right = {token for token in re.split(r"\W+", canonicalize_free_text(b)) if token}
    if not left or not right:
        return 0.0
    inter = len(left & right)
    union = len(left | right)
    return inter / union if union else 0.0


def best_string_match(query: str, candidates: Sequence[str]) -> Tuple[int, float]:
    best_index = -1
    best_score = 0.0
    for index, candidate in enumerate(candidates):
        score = lexical_overlap_score(query, candidate)
        if score > best_score:
            best_index = index
            best_score = score
    return best_index, best_score
