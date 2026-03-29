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
