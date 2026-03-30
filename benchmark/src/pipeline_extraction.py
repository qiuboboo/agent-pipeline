from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from .pipeline_utils import is_missing_value, is_null_like_text, json_default, normalize_whitespace, parse_choice_map, to_plain_text
except ImportError:
    from pipeline_utils import is_missing_value, is_null_like_text, json_default, normalize_whitespace, parse_choice_map, to_plain_text


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = PROJECT_ROOT.parent
PROMPT_ROOT = PROJECT_ROOT / "prompts"
UNIFIED_EXTRACTION_PROMPT_PATH = PROMPT_ROOT / "extract_unified_sample.md"
LEGACY_EXTRACTION_PROMPT_PATH = PROMPT_ROOT / "extract_question_answer_image.md"


def normalize_image_path_list(value: Any) -> List[str]:
    if is_missing_value(value):
        return []
    if isinstance(value, (list, tuple)):
        normalized: List[str] = []
        for item in value:
            normalized.extend(normalize_image_path_list(item))
        return normalized
    if isinstance(value, dict):
        return normalize_image_path_list(value.get("path") or value.get("paths") or value.get("image") or value.get("url"))
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        if stripped.startswith("[") and stripped.endswith("]"):
            try:
                parsed = json.loads(stripped)
                if isinstance(parsed, list):
                    return normalize_image_path_list(parsed)
            except Exception:
                pass
        return [stripped]
    return []


def resolve_image_candidate_path(path_str: str, base_dir: Path) -> Optional[Path]:
    candidate = Path(path_str)
    candidate_paths: List[Path] = []
    if candidate.is_absolute():
        candidate_paths.append(candidate)
    else:
        candidate_paths.append(base_dir / candidate)
        candidate_paths.append(PROJECT_ROOT / candidate)
        candidate_paths.append(WORKSPACE_ROOT / candidate)
    seen: set[str] = set()
    for item in candidate_paths:
        key = str(item)
        if key in seen:
            continue
        seen.add(key)
        if item.exists() and item.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".webp"}:
            return item
    return None


def choose_candidate_field(row: Dict[str, Any], candidates: List[str], fallback_regex: str) -> Optional[str]:
    for key in candidates:
        if key in row and not is_missing_value(row[key]):
            return key
    for key, value in row.items():
        if is_missing_value(value):
            continue
        if re.search(fallback_regex, key, flags=re.IGNORECASE):
            return key
    return None


REASONING_FIELD_CANDIDATES = [
    "reasoning_chain",
    "reasoning",
    "analysis",
    "explanation",
    "derivation",
    "proof",
    "steps",
    "step_by_step",
    "worked_solution",
    "solution_text",
    "solution_process",
    "rationale",
    "解析",
    "题解",
    "推理",
    "证明",
    "步骤",
    "过程",
    "思路",
    "说明",
]
REASONING_FIELD_REGEX = (
    r"reasoning(?:_chain)?|analysis|explanation|derivation|proof|step(?:_by_step)?s?|"
    r"worked_solution|solution_text|solution_process|rationale|解析|题解|推理|证明|步骤|过程|思路|说明"
)
SOLUTION_FIELD_CANDIDATES = ["solution", "worked_solution", "solution_text", "solution_process", "解答", "题解", "解析"]
SOLUTION_FIELD_REGEX = r"(?:^|_)(?:solution)(?:$|_)|解答|题解|解析"
REASONING_CONNECTOR_REGEX = (
    r"\b(because|therefore|thus|hence|so|first|then|next|finally|assume|let|proof|derive)\b|"
    r"因为|所以|因此|先|再|然后|由此|可得|证明|步骤|解[:：]"
)
STEP_MARKER_REGEX = r"(?:^|\n|\r|\s)(?:step\s*\d+|\d+\s*[\.\)]|[(（]?\d+[)）]|第[一二三四五六七八九十]+步)"


def normalize_reasoning_text(value: Any) -> str:
    return to_plain_text(value).strip()


def is_explicit_reasoning_field(field_name: Optional[str]) -> bool:
    return bool(field_name and re.search(REASONING_FIELD_REGEX, field_name, flags=re.IGNORECASE))


def is_atomic_final_answer(text: str) -> bool:
    normalized = normalize_whitespace(text)
    if not normalized:
        return True
    if re.fullmatch(r"[A-Z]", normalized, flags=re.IGNORECASE):
        return True
    if re.fullmatch(r"-?\d+(?:\.\d+)?(?:/\d+)?", normalized):
        return True
    if re.fullmatch(r"[A-Za-z]\s*=\s*[-+]?\d+(?:\.\d+)?", normalized):
        return True
    if re.fullmatch(r"(?:true|false|yes|no|正确|错误)", normalized, flags=re.IGNORECASE):
        return True
    return False


def looks_like_short_final_answer(text: str) -> bool:
    normalized = normalize_whitespace(text)
    if not normalized:
        return True
    if is_atomic_final_answer(normalized):
        return True
    prefixed = re.fullmatch(r"(?:answer|final answer|答案|最终答案)\s*[:：]?\s*(.+)", normalized, flags=re.IGNORECASE)
    if not prefixed:
        return False
    tail = prefixed.group(1).strip()
    return not tail or is_atomic_final_answer(tail) or len(re.sub(r"\s+", "", tail)) <= 20


def is_reasoning_like_text(text: str, strict: bool = False) -> bool:
    raw_text = text.strip()
    normalized = normalize_whitespace(raw_text)
    compact_len = len(re.sub(r"\s+", "", normalized))
    if not normalized or looks_like_short_final_answer(normalized):
        return False
    if strict and compact_len < 24:
        return False
    if not strict and compact_len < 18:
        return False
    sentence_markers = sum(normalized.count(mark) for mark in [".", ";", ":", "。", "；", "："])
    newline_count = raw_text.count("\n") + raw_text.count("\r")
    equation_count = normalized.count("=") + normalized.count("⇒") + normalized.count("∴")
    has_connectors = bool(re.search(REASONING_CONNECTOR_REGEX, normalized, flags=re.IGNORECASE))
    has_steps = bool(re.search(STEP_MARKER_REGEX, raw_text, flags=re.IGNORECASE))
    return bool(
        has_steps
        or newline_count >= 1
        or has_connectors
        or sentence_markers >= 2
        or (sentence_markers >= 1 and compact_len >= 40)
        or (equation_count >= 2 and (has_connectors or sentence_markers >= 1 or newline_count >= 1))
    )


def extract_reasoning_chain_fields(row: Dict[str, Any], answer_field: Optional[str] = None) -> Dict[str, Any]:
    checked_fields: set[str] = set()
    candidate_fields = [
        choose_candidate_field(row, REASONING_FIELD_CANDIDATES, REASONING_FIELD_REGEX),
        choose_candidate_field(row, SOLUTION_FIELD_CANDIDATES, SOLUTION_FIELD_REGEX),
        answer_field,
    ]
    for field_name in candidate_fields:
        if not field_name or field_name in checked_fields:
            continue
        checked_fields.add(field_name)
        candidate_text = normalize_reasoning_text(row.get(field_name))
        strict = not is_explicit_reasoning_field(field_name)
        if is_reasoning_like_text(candidate_text, strict=strict):
            return {"has_reasoning_chain": True, "reasoning_chain": candidate_text}
    return {"has_reasoning_chain": False, "reasoning_chain": ""}


def heuristic_extract_record_content(row: Dict[str, Any], spec: Any) -> Dict[str, Any]:
    question_field = choose_candidate_field(row, spec.question_fields or ["problem", "question"], r"question|problem|query|prompt|text")
    answer_field = choose_candidate_field(row, spec.answer_fields or ["solution", "answer"], r"answer|solution|label|target")
    image_field = choose_candidate_field(row, spec.image_fields or ["image", "image_path"], r"image|img|diagram|figure|picture|decoded_image")
    choice_field = choose_candidate_field(row, spec.choice_fields or ["options", "choices"], r"options|choices")
    raw_question = to_plain_text(row.get(question_field)) if question_field else ""
    raw_answer = to_plain_text(row.get(answer_field)) if answer_field else ""
    if is_null_like_text(raw_answer):
        raw_answer = ""
    choice_map = parse_choice_map(row.get(choice_field) if choice_field else None)
    raw_images = row.get(image_field) if image_field else row.get("images")
    image_paths = normalize_image_path_list(raw_images)
    if not image_paths and isinstance(raw_images, dict):
        image_paths = normalize_image_path_list(raw_images.get("path") or raw_images.get("image") or raw_images.get("url"))
    force_requires_image = bool(spec.force_requires_image)
    if raw_question:
        force_requires_image = force_requires_image or bool(
            re.search(r"\b(figure|diagram|graph|chart|image|shown|below|sample|下图|图中|示意图)\b", raw_question, flags=re.IGNORECASE)
        )
    reasoning_fields = extract_reasoning_chain_fields(row, answer_field=answer_field)
    return {
        "raw_question_text": raw_question,
        "raw_answer_text": raw_answer,
        "choice_map": choice_map,
        "image_paths": image_paths,
        "force_requires_image": force_requires_image,
        "extraction_notes": ["heuristic_field_extraction"],
        "question_field": question_field,
        "answer_field": answer_field,
        "image_field": image_field,
        "choice_field": choice_field,
        **reasoning_fields,
    }


def read_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def prompt_extract_record_content(row: Dict[str, Any], spec: Any, client: Any) -> Dict[str, Any]:
    fallback = heuristic_extract_record_content(row, spec)
    prompt_path = UNIFIED_EXTRACTION_PROMPT_PATH if UNIFIED_EXTRACTION_PROMPT_PATH.exists() else LEGACY_EXTRACTION_PROMPT_PATH
    agent_only = bool(getattr(client.config, "agent_only_extraction", False))
    if not client.config.enabled or not client.config.api_key or not prompt_path.exists():
        if agent_only:
            return {
                "raw_question_text": "",
                "raw_answer_text": "",
                "choice_map": {},
                "image_paths": [],
                "force_requires_image": False,
                "extraction_notes": ["agent_only_extraction", "agent_extraction_failed"],
                "question_field": None,
                "answer_field": None,
                "image_field": None,
                "choice_field": None,
                "has_reasoning_chain": False,
                "reasoning_chain": "",
            }
        return fallback
    user_prompt = json.dumps(
        {
            "dataset_name": spec.display_name,
            "source_kind": spec.source_kind,
            "raw_record": row,
            "fallback": fallback,
        },
        ensure_ascii=False,
        indent=2,
        default=json_default,
    )
    result = client.chat_json(read_prompt(prompt_path), user_prompt)
    if not result:
        if agent_only:
            return {
                "raw_question_text": "",
                "raw_answer_text": "",
                "choice_map": {},
                "image_paths": [],
                "force_requires_image": False,
                "extraction_notes": ["agent_only_extraction", "agent_extraction_failed"],
                "question_field": None,
                "answer_field": None,
                "image_field": None,
                "choice_field": None,
                "has_reasoning_chain": False,
                "reasoning_chain": "",
            }
        return fallback
    extraction_notes = result.get("extraction_notes")
    if not isinstance(extraction_notes, list):
        extraction_notes = []
    extraction_notes = [to_plain_text(item) for item in extraction_notes if to_plain_text(item)]
    if agent_only:
        raw_question_text = normalize_whitespace(to_plain_text(result.get("raw_question_text") or result.get("question_text")))
        raw_answer_text = normalize_whitespace(to_plain_text(result.get("raw_answer_text") or result.get("answer_text")))
        choice_map = parse_choice_map(result.get("choice_map")) or {}
        image_paths = normalize_image_path_list(result.get("image_paths"))
        force_requires_image = result.get("force_requires_image")
        if not isinstance(force_requires_image, bool):
            force_requires_image = False
        extraction_notes.extend(["agent_only_extraction", "agent_extraction_success"])
        return {
            "raw_question_text": raw_question_text,
            "raw_answer_text": raw_answer_text,
            "choice_map": choice_map,
            "image_paths": image_paths,
            "force_requires_image": force_requires_image,
            "extraction_notes": sorted(set(extraction_notes)),
            "question_field": result.get("question_field"),
            "answer_field": result.get("answer_field"),
            "image_field": result.get("image_field"),
            "choice_field": result.get("choice_field"),
            "has_reasoning_chain": False,
            "reasoning_chain": "",
        }
    raw_question_text = normalize_whitespace(to_plain_text(result.get("raw_question_text") or result.get("question_text") or fallback["raw_question_text"]))
    raw_answer_text = normalize_whitespace(to_plain_text(result.get("raw_answer_text") or result.get("answer_text") or fallback["raw_answer_text"]))
    choice_map = parse_choice_map(result.get("choice_map")) or fallback["choice_map"]
    image_paths = normalize_image_path_list(result.get("image_paths")) or fallback["image_paths"]
    force_requires_image = result.get("force_requires_image")
    if not isinstance(force_requires_image, bool):
        force_requires_image = fallback["force_requires_image"]
    extraction_notes.append("prompt_extraction")
    return {
        **fallback,
        "raw_question_text": raw_question_text or fallback["raw_question_text"],
        "raw_answer_text": raw_answer_text or fallback["raw_answer_text"],
        "choice_map": choice_map,
        "image_paths": image_paths,
        "force_requires_image": force_requires_image,
        "extraction_notes": extraction_notes,
    }
