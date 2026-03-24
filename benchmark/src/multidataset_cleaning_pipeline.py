#!/usr/bin/env python3
"""多数据集数据采集与清洗智能体流水线。

本脚本面向清洗阶段的全自动实现，覆盖：
1. 多数据集公开源接入（Hugging Face / GitHub / source_unavailable）
2. 样本抽样（每个数据集最多抽样固定数量）
3. 文本规范化、图像质量检测、图文对齐、可解性门控
4. 选择题开放化改写、依赖干扰项题目挖空改写、纯图编号题剔除
5. 基于 OpenAI 兼容接口的 Rewrite Agent / Decision Agent
6. 统一产出 problem_main_record / asset_record / cleaning_record / reject_record /
   alignment_record / field_audit_record / rewrite_report / open_ended_problem_variants
7. 多数据集汇总评测报告
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
import time
import unicodedata
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import yaml
from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict, load_dataset
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMPT_ROOT = PROJECT_ROOT / "prompts"
UNIFIED_EXTRACTION_PROMPT_PATH = PROMPT_ROOT / "extract_unified_sample.md"
LEGACY_EXTRACTION_PROMPT_PATH = PROMPT_ROOT / "extract_question_answer_image.md"
ASSET_REGISTRY_PROMPT_PATH = PROMPT_ROOT / "collection" / "asset_registry.md"
POTENTIAL_SCORER_PROMPT_PATH = PROMPT_ROOT / "collection" / "potential_scorer.md"
CANDIDATE_REGISTRAR_PROMPT_PATH = PROMPT_ROOT / "collection" / "candidate_registrar.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (bytes, bytearray)):
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


NULL_LIKE_STRINGS = {"null", "none", "nan", "n/a", "na", "[]", "{}"}


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


def read_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def build_unified_extraction_user_prompt(record: Dict[str, Any]) -> str:
    record_json = json.dumps(record, ensure_ascii=False, indent=2, default=json_default)
    return f"""下面是一条原始 JSON 记录。
请按照 system prompt 的规则提取 UnifiedSample 所需的关键字段。
只返回 JSON 对象。

原始 JSON:
{record_json}
"""


def build_asset_registry_user_prompt(problem_id: str, question_text: str, answer_text: str, image_paths: List[str], metadata: Dict[str, Any], asset_integrity: Dict[str, Any]) -> str:
    payload = {
        "problem_id": problem_id,
        "question_text": question_text,
        "answer_text": answer_text,
        "image_paths": image_paths,
        "metadata": metadata,
        "asset_integrity": asset_integrity,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, default=json_default)


def build_potential_scorer_user_prompt(problem_id: str, question_text: str, answer_text: str, metadata: Dict[str, Any], asset_registry_record: Dict[str, Any]) -> str:
    payload = {
        "problem_id": problem_id,
        "question_text": question_text,
        "answer_text": answer_text,
        "metadata": metadata,
        "asset_registry_record": asset_registry_record,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, default=json_default)


def build_candidate_registrar_user_prompt(problem_id: str, asset_registry_record: Dict[str, Any], initial_scoring_record: Dict[str, Any]) -> str:
    payload = {
        "problem_id": problem_id,
        "asset_registry_record": asset_registry_record,
        "initial_scoring_record": initial_scoring_record,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, default=json_default)


def infer_language_hint(text: str) -> str:
    has_zh = bool(re.search(r"[\u4e00-\u9fff]", text))
    has_en = bool(re.search(r"[A-Za-z]", text))
    if has_zh and has_en:
        return "mixed"
    if has_zh:
        return "zh"
    if has_en:
        return "en"
    return "unknown"


def infer_answer_manifest_type(answer_text: str) -> str:
    answer = normalize_whitespace(answer_text)
    if not answer:
        return "unknown"
    if re.fullmatch(r"[A-Z]", answer):
        return "choice"
    if re.fullmatch(r"[+-]?(?:\d+(?:\.\d+)?|\.\d+)", answer):
        return "number"
    if len(answer.split()) <= 8:
        return "short_text"
    return "long_text"


def heuristic_asset_registry_record(problem_id: str, question_text: str, answer_text: str, image_paths: List[str], metadata: Dict[str, Any], image_quality: Dict[str, Any]) -> Dict[str, Any]:
    image_manifest = []
    source_file = metadata.get("source_file")
    base_dir = Path(source_file).parent if source_file else PROJECT_ROOT
    for raw_path in image_paths:
        candidate = resolve_image_candidate_path(raw_path, base_dir)
        exists = candidate is not None
        path_obj = candidate if candidate is not None else Path(raw_path)
        suffix = path_obj.suffix.lower().lstrip(".") or None
        width = image_quality.get("width") if exists else 0
        height = image_quality.get("height") if exists else 0
        file_size = path_obj.stat().st_size if exists and path_obj.exists() else 0
        image_manifest.append(
            {
                "path": str(path_obj),
                "exists": exists,
                "format": suffix,
                "width": width,
                "height": height,
                "file_size": file_size,
            }
        )
    question_present = bool(normalize_whitespace(question_text))
    answer_present = bool(normalize_whitespace(answer_text))
    image_required = bool(metadata.get("force_requires_image", False))
    issues: List[str] = []
    if not question_present:
        issues.append("missing_question_text")
    if not answer_present:
        issues.append("missing_answer_text")
    if image_required:
        if not image_manifest:
            issues.append("missing_image_path")
        elif not any(item["exists"] for item in image_manifest):
            issues.append("image_not_found")
    else:
        if image_manifest and not any(item["exists"] for item in image_manifest):
            issues.append("image_optional_not_found")
    registry_passed = question_present and answer_present and (not image_required or any(item["exists"] for item in image_manifest))
    return {
        "problem_id": problem_id,
        "image_manifest": image_manifest,
        "text_manifest": {
            "question_present": question_present,
            "question_char_length": len(question_text or ""),
            "language_hint": infer_language_hint(question_text or ""),
        },
        "answer_manifest": {
            "answer_present": answer_present,
            "answer_type": infer_answer_manifest_type(answer_text),
            "answer_char_length": len(answer_text or ""),
        },
        "issues": issues,
        "registry_passed": registry_passed,
    }


def heuristic_initial_scoring_record(problem_id: str, question_text: str, answer_text: str, metadata: Dict[str, Any], asset_registry_record: Dict[str, Any], potential_scores: Dict[str, Any], quality_flags: List[str]) -> Dict[str, Any]:
    return {
        "problem_id": problem_id,
        "image_dependency_score": round(clamp(potential_scores.get("multimodal_strength_score", 0.0)), 4),
        "multi_step_score": round(clamp(potential_scores.get("multi_step_score", 0.0)), 4),
        "verifiability_score": round(clamp(potential_scores.get("verifiability_score", 0.0)), 4),
        "score_evidence": {
            "image_dependency": ["requires_image=true" if potential_scores.get("requires_image") else "requires_image=false"],
            "multi_step": [f"question_length={len(question_text or '')}", f"metadata_keys={len(metadata or {})}"],
            "verifiability": [f"answer_present={bool(normalize_whitespace(answer_text))}", f"registry_passed={asset_registry_record.get('registry_passed', False)}"],
        },
        "risk_flags": sorted(set(list(asset_registry_record.get("issues", [])) + list(quality_flags))),
        "scoring_version": "v1-heuristic",
    }


def heuristic_candidate_registrar_record(problem_id: str, asset_registry_record: Dict[str, Any], initial_scoring_record: Dict[str, Any]) -> Dict[str, Any]:
    registry_passed = bool(asset_registry_record.get("registry_passed", False))
    issues = list(asset_registry_record.get("issues", []))
    risk_flags = list(initial_scoring_record.get("risk_flags", []))
    image_dep = float(initial_scoring_record.get("image_dependency_score", 0.0))
    avg_score = (
        float(initial_scoring_record.get("image_dependency_score", 0.0))
        + float(initial_scoring_record.get("multi_step_score", 0.0))
        + float(initial_scoring_record.get("verifiability_score", 0.0))
    ) / 3.0
    if not registry_passed:
        text_ready = asset_registry_record.get("text_manifest", {}).get("question_present") and asset_registry_record.get("answer_manifest", {}).get("answer_present")
        image_missing = any(flag in issues for flag in ["missing_image_path", "image_not_found", "image_optional_not_found"])
        if text_ready and image_missing and image_dep < 0.75:
            return {
                "problem_id": problem_id,
                "priority": round(max(avg_score, 0.35), 4),
                "decision": "low_priority",
                "decision_reasons": ["text_complete_but_image_missing_or_optional"],
            }
        return {
            "problem_id": problem_id,
            "priority": 0.0,
            "decision": "reject",
            "decision_reasons": ["asset_registry_failed"],
        }
    if avg_score >= 0.72 and not risk_flags:
        return {
            "problem_id": problem_id,
            "priority": round(avg_score, 4),
            "decision": "keep",
            "decision_reasons": ["high_preliminary_value"],
        }
    return {
        "problem_id": problem_id,
        "priority": round(max(avg_score, 0.3), 4),
        "decision": "low_priority",
        "decision_reasons": ["borderline_preliminary_value"],
    }


def llm_asset_registry_record(problem_id: str, question_text: str, answer_text: str, image_paths: List[str], metadata: Dict[str, Any], asset_integrity: Dict[str, Any], client: "OpenAICompatibleClient") -> Optional[Dict[str, Any]]:
    if not client.config.enabled or not ASSET_REGISTRY_PROMPT_PATH.exists():
        return None
    result = client.chat_json(
        read_prompt(ASSET_REGISTRY_PROMPT_PATH),
        build_asset_registry_user_prompt(problem_id, question_text, answer_text, image_paths, metadata, asset_integrity),
    )
    return result if isinstance(result, dict) else None


def llm_initial_scoring_record(problem_id: str, question_text: str, answer_text: str, metadata: Dict[str, Any], asset_registry_record: Dict[str, Any], client: "OpenAICompatibleClient") -> Optional[Dict[str, Any]]:
    if not client.config.enabled or not POTENTIAL_SCORER_PROMPT_PATH.exists():
        return None
    result = client.chat_json(
        read_prompt(POTENTIAL_SCORER_PROMPT_PATH),
        build_potential_scorer_user_prompt(problem_id, question_text, answer_text, metadata, asset_registry_record),
    )
    return result if isinstance(result, dict) else None


def llm_candidate_registrar_record(problem_id: str, asset_registry_record: Dict[str, Any], initial_scoring_record: Dict[str, Any], client: "OpenAICompatibleClient") -> Optional[Dict[str, Any]]:
    if not client.config.enabled or not CANDIDATE_REGISTRAR_PROMPT_PATH.exists():
        return None
    result = client.chat_json(
        read_prompt(CANDIDATE_REGISTRAR_PROMPT_PATH),
        build_candidate_registrar_user_prompt(problem_id, asset_registry_record, initial_scoring_record),
    )
    return result if isinstance(result, dict) else None


def normalize_image_path_list(value: Any) -> List[str]:
    if is_missing_value(value):
        return []
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    return []


def resolve_image_candidate_path(path_str: str, base_dir: Path) -> Optional[Path]:
    candidate = Path(path_str)
    candidate_paths: List[Path] = []
    if candidate.is_absolute():
        candidate_paths.append(candidate)
    else:
        candidate_paths.append(base_dir / candidate)
        workspace_root = Path(__file__).resolve().parents[2]
        candidate_paths.append(workspace_root / candidate)
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


def heuristic_extract_record_content(row: Dict[str, Any], spec: "DatasetSpec") -> Dict[str, Any]:
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
        force_requires_image = force_requires_image or bool(re.search(r"\b(figure|diagram|graph|chart|image|shown|below|sample|下图|图中|示意图)\b", raw_question, flags=re.I))
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


def prompt_extract_record_content(row: Dict[str, Any], spec: "DatasetSpec", client: "OpenAICompatibleClient") -> Dict[str, Any]:
    fallback = heuristic_extract_record_content(row, spec)
    prompt_path = UNIFIED_EXTRACTION_PROMPT_PATH if UNIFIED_EXTRACTION_PROMPT_PATH.exists() else LEGACY_EXTRACTION_PROMPT_PATH
    if not client.config.enabled or not prompt_path.exists():
        return fallback
    system_prompt = read_prompt(prompt_path)
    result = client.chat_json(system_prompt, build_unified_extraction_user_prompt(row))
    if not result:
        return fallback
    raw_question_text = normalize_whitespace(to_plain_text(result.get("raw_question_text") or result.get("question_text") or fallback["raw_question_text"]))
    raw_answer_text = normalize_whitespace(to_plain_text(result.get("raw_answer_text") or result.get("answer_text") or fallback["raw_answer_text"]))
    choice_map = parse_choice_map(result.get("choice_map")) or fallback["choice_map"]
    image_paths = normalize_image_path_list(result.get("image_paths")) or fallback["image_paths"]
    force_requires_image = result.get("force_requires_image")
    if not isinstance(force_requires_image, bool):
        force_requires_image = fallback["force_requires_image"]
    extraction_notes = result.get("extraction_notes")
    if not isinstance(extraction_notes, list):
        extraction_notes = []
    extraction_notes = [to_plain_text(item) for item in extraction_notes if to_plain_text(item)]
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


def resolve_multiple_choice_answer_text(answer_text: str, choice_map: Dict[str, str]) -> str:
    answer = normalize_whitespace(answer_text)
    if not answer:
        return ""
    upper = answer.upper().strip()
    letter_match = re.fullmatch(r"\(?([A-Z])\)?", upper)
    if letter_match:
        key = letter_match.group(1)
        if key in choice_map:
            return normalize_whitespace(choice_map[key])
    mixed_match = re.match(r"^\(?([A-Z])\)?[\s.、:_-]+(.+)$", answer, flags=re.I)
    if mixed_match:
        answer = mixed_match.group(2).strip()
    return normalize_whitespace(answer)


@dataclass
class ModelConfig:
    base_url: str = "https://synai996.space/v1"
    api_key: str = os.environ.get("OPENAI_API_KEY", "")
    model: str = "gpt-5.4"
    reasoning_effort: str = "xhigh"
    temperature: float = 0.1
    timeout_seconds: int = 180
    enabled: bool = True


@dataclass
class ThresholdConfig:
    min_width: int = 256
    min_height: int = 256
    min_sharpness_score: float = 0.22
    min_readability_score: float = 0.35
    min_contrast_score: float = 18.0
    reject_clean_score_below: float = 0.45
    review_clean_score_below: float = 0.62
    min_text_completeness_score: float = 0.60
    min_alignment_consistency: float = 0.55


@dataclass
class DatasetSpec:
    key: str
    display_name: str
    subject: str
    note: str
    source_kind: str
    source_locator: str
    split: Optional[str] = None
    hf_config_name: Optional[str] = None
    question_fields: List[str] = field(default_factory=list)
    answer_fields: List[str] = field(default_factory=list)
    image_fields: List[str] = field(default_factory=list)
    choice_fields: List[str] = field(default_factory=list)
    metadata_fields: List[str] = field(default_factory=list)
    force_requires_image: bool = False


@dataclass
class PipelineConfig:
    sample_per_dataset: int = 30
    sample_strategy: str = "head"
    shuffle_seed: int = 42
    output_root: str = "outputs/multidataset_cleaning"
    cleaning_version: str = "v2.0.0"
    batch_id_prefix: str = "multidataset-clean"
    save_sample_bundle: bool = True
    git_cache_root: str = "outputs/repo_cache"
    model: ModelConfig = field(default_factory=ModelConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    datasets: List[DatasetSpec] = field(default_factory=list)

    @classmethod
    def default_dataset_specs(cls) -> List[DatasetSpec]:
        return [
            DatasetSpec(
                key="geosqa",
                display_name="GeoSQA",
                subject="地理",
                note="论文页公开，但当前未配置稳定程序化下载入口",
                source_kind="source_unavailable",
                source_locator="https://aclanthology.org/D19-1597/",
            ),
            DatasetSpec(
                key="scemqa",
                display_name="SCEMQA",
                subject="数学、物理、生物、化学",
                note="GitHub 公开仓库，尝试自动发现数据文件",
                source_kind="github",
                source_locator="https://github.com/SceMQA/SceMQA",
                question_fields=["question", "problem", "query", "text"],
                answer_fields=["answer", "solution", "label"],
                image_fields=["image", "image_path", "img_path", "diagram"],
            ),
            DatasetSpec(
                key="geometry3k",
                display_name="Geometry3K",
                subject="数学",
                note="GitHub 公开仓库，尝试自动发现数据文件",
                source_kind="github",
                source_locator="https://github.com/lupantech/InterGPS",
                question_fields=["problem_text", "compact_text", "annotat_text", "problem", "question", "text"],
                answer_fields=["answer", "solution", "label"],
                image_fields=["img_diagram", "img_problem", "diagram", "image", "img_path", "image_path"],
                choice_fields=["choices", "compact_choices", "options"],
                force_requires_image=True,
            ),
            DatasetSpec(
                key="cmm_math",
                display_name="CMM-Math",
                subject="数学",
                note="Hugging Face 数据集",
                source_kind="huggingface",
                source_locator="ecnu-icalk/cmm-math",
                split="train",
                question_fields=["question"],
                answer_fields=["answer", "solution"],
                image_fields=["decoded_image", "image"],
                choice_fields=["options", "choices"],
            ),
            DatasetSpec(
                key="mathvision",
                display_name="MathVision",
                subject="数学",
                note="Hugging Face 数据集",
                source_kind="huggingface",
                source_locator="MathLLMs/MathVision",
                split="test",
                question_fields=["question"],
                answer_fields=["answer", "solution"],
                image_fields=["decoded_image", "image"],
                choice_fields=["options", "choices"],
            ),
            DatasetSpec(
                key="mm_math",
                display_name="MM-Math",
                subject="数学",
                note="Hugging Face 数据集",
                source_kind="huggingface",
                source_locator="THU-KEG/MM_Math",
                split="train",
            ),
            DatasetSpec(
                key="seephy",
                display_name="Seephy",
                subject="物理",
                note="当前仅论文入口，未配置稳定程序化下载源",
                source_kind="source_unavailable",
                source_locator="https://arxiv.org/abs/2509.06079",
            ),
            DatasetSpec(
                key="multi_physics",
                display_name="muti- physics",
                subject="物理",
                note="GitHub 公开仓库，尝试自动发现数据文件",
                source_kind="github",
                source_locator="https://github.com/luozhongze/Multi-Physics",
                question_fields=["question", "problem", "query", "text"],
                answer_fields=["answer", "solution", "label"],
                image_fields=["image", "image_path", "img_path", "figure"],
            ),
            DatasetSpec(
                key="physreason",
                display_name="PhysReason",
                subject="物理",
                note="GitHub 公开仓库，尝试自动发现数据文件",
                source_kind="github",
                source_locator="https://github.com/dxzxy12138/PhysReason",
                question_fields=["question", "problem", "query", "text"],
                answer_fields=["answer", "solution", "label"],
                image_fields=["image", "image_path", "img_path", "figure"],
            ),
            DatasetSpec(
                key="eee_bench",
                display_name="EEE-Bench",
                subject="电气电子工程领域",
                note="Hugging Face 数据集",
                source_kind="huggingface",
                source_locator="afdsafas/EEE-Bench",
                split="test",
                question_fields=["problem"],
                answer_fields=["solution"],
                image_fields=["image"],
            ),
            DatasetSpec(
                key="emma",
                display_name="EMMA",
                subject="数学、物理、代码、化学",
                note="当前仅论文入口，未配置稳定程序化下载源",
                source_kind="source_unavailable",
                source_locator="https://arxiv.org/abs/2501.05444",
            ),
        ]

    @classmethod
    def from_yaml(cls, path: Optional[str]) -> "PipelineConfig":
        if not path:
            return cls(datasets=cls.default_dataset_specs())
        with open(path, "r", encoding="utf-8") as file:
            raw = yaml.safe_load(file) or {}
        runtime = raw.get("runtime", {})
        model_raw = raw.get("model", {})
        threshold_raw = raw.get("thresholds", {})
        datasets_raw = raw.get("datasets", [])
        datasets = []
        if datasets_raw:
            for item in datasets_raw:
                datasets.append(DatasetSpec(**item))
        else:
            datasets = cls.default_dataset_specs()
        return cls(
            sample_per_dataset=runtime.get("sample_per_dataset", 30),
            sample_strategy=runtime.get("sample_strategy", "head"),
            shuffle_seed=runtime.get("shuffle_seed", 42),
            output_root=runtime.get("output_root", "outputs/multidataset_cleaning"),
            cleaning_version=runtime.get("cleaning_version", "v2.0.0"),
            batch_id_prefix=runtime.get("batch_id_prefix", "multidataset-clean"),
            save_sample_bundle=runtime.get("save_sample_bundle", True),
            git_cache_root=runtime.get("git_cache_root", "outputs/repo_cache"),
            model=ModelConfig(**{**asdict(ModelConfig()), **model_raw}),
            thresholds=ThresholdConfig(**{**asdict(ThresholdConfig()), **threshold_raw}),
            datasets=datasets,
        )


@dataclass
class UnifiedSample:
    dataset_key: str
    dataset_display_name: str
    subject: str
    source_dataset: str
    source_split: str
    source_problem_id: str
    raw_question_text: str
    raw_answer_text: str
    image: Optional[Image.Image]
    image_source: Optional[str]
    raw_record: Dict[str, Any]
    metadata: Dict[str, Any]
    choice_map: Dict[str, str] = field(default_factory=dict)
    force_requires_image: bool = False


class OpenAICompatibleClient:
    def __init__(self, config: ModelConfig):
        self.config = config

    def chat_json(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        if not self.config.enabled:
            return None
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
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
            return None
        choices = body.get("choices") or []
        if not choices:
            return None
        message = choices[0].get("message") or {}
        content = message.get("content", "")
        if isinstance(content, list):
            content = "\n".join(item.get("text", "") for item in content if isinstance(item, dict))
        return extract_json_object(to_plain_text(content))


class TextNormalizer:
    IMAGE_HINT_PATTERN = re.compile(
        r"\b(figure|fig\.?|diagram|graph|chart|circuit|schematic|shown in the figure|shown below|waveform|table|image)\b",
        re.IGNORECASE,
    )
    NUMERIC_PATTERN = re.compile(r"^[+-]?(?:\d+(?:\.\d+)?|\.\d+)$")
    PURE_IMAGE_INDEX_PATTERN = re.compile(
        r"^(diagram|graph|figure|waveform|plot|curve|option|image)\s*[A-H0-9]+$",
        re.IGNORECASE,
    )
    EXAM_HEADER_PATTERNS = [
        re.compile(r"^【[^】]*(?:试题|试卷|考试|模拟|联考|月考|期中|期末|诊断|测验|练习|专题)[^】]*】\s*"),
        re.compile(r"^[\(（][^\)）]*(?:年|届|高考|中考|模拟|联考|月考|期中|期末|诊断|测试|试题|试卷|理|文)[^\)）]*[\)）]\s*"),
        re.compile(r"^(?:\d{4}\s*年[^。；，,:：]{0,40}(?:模拟|联考|月考|期中|期末|诊断|测试|试题|试卷))[:：\s]*"),
        re.compile(r"^(?:来源|出自|题源)[:：]\s*[^。；\n]+"),
    ]
    SCORE_ANNOTATION_PATTERN = re.compile(
        r"(?:^|(?<=[\s，。；;:：]))[\(（【\[]?\s*(?:本题|此题)?\s*(?:满分\s*)?\d+\s*分\s*[】\)）\]]?(?=$|[\s，。；;:：])"
    )

    def strip_exam_boilerplate(self, text: str) -> str:
        value = text.strip()
        changed = True
        while value and changed:
            changed = False
            for pattern in self.EXAM_HEADER_PATTERNS:
                updated = pattern.sub("", value, count=1).strip()
                if updated != value:
                    value = updated
                    changed = True
        value = self.SCORE_ANNOTATION_PATTERN.sub(" ", value)
        value = re.sub(r"^[\)\]】）\-—–:：\s]+", "", value)
        return normalize_whitespace(value)

    def normalize_text(self, text: Any) -> str:
        value = unicodedata.normalize("NFKC", to_plain_text(text))
        value = value.replace("\u00a0", " ")
        value = value.replace("_x000C_", "")
        value = re.sub(r"<\s*image\s*>", " ", value, flags=re.IGNORECASE)
        value = re.sub(r"\*\*Choices:\*\*", "Choices:", value, flags=re.IGNORECASE)
        value = self.strip_exam_boilerplate(value)
        value = normalize_whitespace(value)
        return value

    def strip_hint(self, text: str) -> str:
        text = re.sub(r"^Hint\s*:\s.*?(?=Question\s*:)", "", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"Please answer[^\n]*", "", text, flags=re.IGNORECASE)
        return normalize_whitespace(text)

    def normalize_answer(self, answer: Any) -> str:
        value = self.normalize_text(answer).strip(". ")
        if not value or is_null_like_text(value):
            return ""
        if re.fullmatch(r"[A-Za-z]", value):
            return value.upper()
        if self.NUMERIC_PATTERN.fullmatch(value):
            number = float(value)
            if number.is_integer():
                return str(int(number))
            return f"{number:.6f}".rstrip("0").rstrip(".")
        return value

    def detect_language(self, text: str) -> str:
        if re.search(r"[\u4e00-\u9fff]", text):
            return "zh"
        if re.search(r"[A-Za-z]", text):
            return "en"
        return "unknown"

    def infer_answer_type(self, answer: str) -> str:
        if not answer:
            return "unknown"
        if re.fullmatch(r"[A-Z]", answer):
            return "option"
        if self.NUMERIC_PATTERN.fullmatch(answer):
            return "numeric"
        if any(sep in answer for sep in [",", ";", "，", "；"]):
            return "set"
        if len(answer.split()) <= 8:
            return "short_text"
        return "text"

    def extract_question_body(self, text: str) -> str:
        match = re.search(r"Question\s*:\s*(.*)", text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return normalize_whitespace(match.group(1))
        return text

    def split_question_and_choices(self, text: str) -> Tuple[str, str]:
        match = re.search(r"\bChoices?\b\s*:?", text, flags=re.IGNORECASE)
        if not match:
            return text, ""
        return normalize_whitespace(text[: match.start()]), normalize_whitespace(text[match.end() :])

    def extract_choice_map(self, text: str) -> Dict[str, str]:
        _, choice_block = self.split_question_and_choices(text)
        if not choice_block:
            return {}
        choices: Dict[str, str] = {}
        current_key: Optional[str] = None
        current_value: List[str] = []
        for line in choice_block.splitlines():
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
        return choices

    def infer_requires_image(self, question_text: str, image_count: int) -> bool:
        if image_count > 0:
            return True
        if self.IMAGE_HINT_PATTERN.search(question_text):
            return True
        return bool(re.search(r"<image\d*>|imagehere", question_text, flags=re.IGNORECASE))

    def text_completeness_score(self, raw_text: str, normalized_text: str) -> float:
        if not raw_text:
            return 0.0
        length_score = clamp(min(len(normalized_text), 500) / 280.0)
        question_bonus = 0.15 if "question" in normalized_text.lower() else 0.0
        choice_penalty = -0.05 if "choices" in normalized_text.lower() else 0.0
        return round(clamp(0.55 + 0.25 * length_score + question_bonus + choice_penalty), 4)

    def is_pure_image_index_question(self, question_text: str, choices: Dict[str, str]) -> bool:
        if not choices:
            return False
        if not any(token in question_text.lower() for token in ["graph", "diagram", "waveform", "figure", "plot", "curve"]):
            return False
        return all(self.PURE_IMAGE_INDEX_PATTERN.fullmatch(value or "") for value in choices.values())

    def is_compound_answer_question(self, question_text: str, choices: Dict[str, str]) -> bool:
        if not choices:
            return False
        if any(token in question_text.lower() for token in ["respectively", "each", "for (a)", "for a", "for output", "outputs"]):
            return True
        return any(value.count(",") >= 1 or value.count(";") >= 1 for value in choices.values())


class ImageQualityAnalyzer:
    def pil_to_png_bytes(self, image: Image.Image) -> bytes:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def grayscale_array(self, image: Image.Image) -> np.ndarray:
        return np.asarray(image.convert("L"), dtype=np.float32)

    def perceptual_hash(self, image: Image.Image, size: int = 8) -> str:
        resized = image.convert("L").resize((size, size), Image.Resampling.LANCZOS)
        pixels = np.asarray(resized, dtype=np.float32)
        avg = float(pixels.mean())
        bits = "".join("1" if value >= avg else "0" for value in pixels.flatten())
        return f"{int(bits, 2):0{size * size // 4}x}"

    def laplacian_variance(self, gray: np.ndarray) -> float:
        padded = np.pad(gray, ((1, 1), (1, 1)), mode="edge")
        center = padded[1:-1, 1:-1]
        lap = (
            padded[:-2, 1:-1]
            + padded[2:, 1:-1]
            + padded[1:-1, :-2]
            + padded[1:-1, 2:]
            - 4.0 * center
        )
        return float(np.var(lap))

    def contrast_score(self, gray: np.ndarray) -> float:
        return float(np.std(gray))

    def noise_score(self, gray: np.ndarray) -> float:
        coarse = np.asarray(
            Image.fromarray(gray.clip(0, 255).astype(np.uint8)).resize(
                (max(1, gray.shape[1] // 4), max(1, gray.shape[0] // 4)),
                Image.Resampling.BILINEAR,
            ).resize((gray.shape[1], gray.shape[0]), Image.Resampling.BILINEAR),
            dtype=np.float32,
        )
        return float(np.std(gray - coarse))

    def detect_content_bbox(self, gray: np.ndarray) -> Optional[Dict[str, int]]:
        mask = (gray / 255.0) < 0.97
        if mask.sum() == 0:
            return None
        ys, xs = np.where(mask)
        x1, x2 = int(xs.min()), int(xs.max())
        y1, y2 = int(ys.min()), int(ys.max())
        return {"x": x1, "y": y1, "width": int(x2 - x1 + 1), "height": int(y2 - y1 + 1)}

    def crop_integrity_score(self, bbox: Optional[Dict[str, int]], width: int, height: int) -> float:
        if bbox is None:
            return 0.0
        margins = [
            bbox["x"],
            bbox["y"],
            width - (bbox["x"] + bbox["width"]),
            height - (bbox["y"] + bbox["height"]),
        ]
        clipped_edges = sum(margin <= 1 for margin in margins)
        return round(clamp(1.0 - 0.22 * clipped_edges), 4)

    def readability_score(
        self,
        blur_score: float,
        contrast_score: float,
        width: int,
        height: int,
        crop_integrity: float,
    ) -> float:
        sharpness = clamp(math.log1p(max(blur_score, 0.0)) / 8.0)
        contrast = clamp(contrast_score / 64.0)
        resolution = clamp(min(width / 512.0, height / 512.0))
        return round(clamp(0.4 * sharpness + 0.25 * contrast + 0.2 * resolution + 0.15 * crop_integrity), 4)

    def analyze(self, image: Image.Image) -> Dict[str, Any]:
        rgb = image.convert("RGB")
        gray = self.grayscale_array(rgb)
        width, height = rgb.size
        blur_score = self.laplacian_variance(gray)
        contrast = self.contrast_score(gray)
        noise = self.noise_score(gray)
        bbox = self.detect_content_bbox(gray)
        crop_integrity = self.crop_integrity_score(bbox, width, height)
        readability = self.readability_score(blur_score, contrast, width, height, crop_integrity)
        return {
            "width": width,
            "height": height,
            "blur_score": round(blur_score, 4),
            "contrast_score": round(contrast, 4),
            "noise_score": round(noise, 4),
            "readability_score": readability,
            "crop_integrity_score": crop_integrity,
            "roi_bbox": bbox,
            "perceptual_hash": self.perceptual_hash(rgb),
        }


class BaseConnector:
    def __init__(self, spec: DatasetSpec, config: PipelineConfig):
        self.spec = spec
        self.config = config

    def sample(self) -> Tuple[str, List[UnifiedSample], Optional[str]]:
        raise NotImplementedError


class SourceUnavailableConnector(BaseConnector):
    def sample(self) -> Tuple[str, List[UnifiedSample], Optional[str]]:
        return "source_unavailable", [], "No stable programmatic public source configured"


class LocalFileConnector(BaseConnector):
    def iter_records(self, path: Path) -> Iterable[Dict[str, Any]]:
        suffix = path.suffix.lower()
        if suffix == ".jsonl":
            with path.open("r", encoding="utf-8", errors="ignore") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(row, dict):
                        yield row
            return
        if suffix == ".json":
            with path.open("r", encoding="utf-8", errors="ignore") as file:
                data = json.load(file)
            if isinstance(data, list):
                for row in data:
                    if isinstance(row, dict):
                        yield row
                return
            if isinstance(data, dict):
                for key in ["data", "dataset", "datasets", "records", "items", "problems", "questions", "annotations"]:
                    value = data.get(key)
                    if isinstance(value, list):
                        for row in value:
                            if isinstance(row, dict):
                                yield row
                        return
                yield data
            return
        if suffix == ".parquet":
            import pandas as pd
            df = pd.read_parquet(path)
            for row in df.to_dict(orient="records"):
                if isinstance(row, dict):
                    yield row
            return
        raise ValueError(f"Unsupported input format: {path.suffix}")

    def resolve_image(self, path_str: str, base_dir: Path) -> Tuple[Optional[Image.Image], Optional[str]]:
        candidate = resolve_image_candidate_path(path_str, base_dir)
        if candidate is None:
            return None, None
        try:
            return Image.open(candidate).convert("RGB"), str(candidate)
        except Exception:
            return None, None

    def load_inline_image(self, value: Any, base_dir: Path) -> Tuple[Optional[Image.Image], Optional[str]]:
        if is_missing_value(value):
            return None, None
        if isinstance(value, np.ndarray):
            value = value.tolist()
        if isinstance(value, list):
            for item in value:
                image, source = self.load_inline_image(item, base_dir)
                if image is not None:
                    return image, source
            return None, None
        if isinstance(value, Image.Image):
            return value.convert("RGB"), "inline://pil_image"
        if isinstance(value, dict):
            bytes_data = value.get("bytes")
            path = value.get("path")
            if bytes_data is not None:
                try:
                    return Image.open(io.BytesIO(bytes(bytes_data))).convert("RGB"), path or "inline://image_bytes"
                except Exception:
                    pass
            if path:
                return self.resolve_image(str(path), base_dir)
        if isinstance(value, str):
            return self.resolve_image(value, base_dir)
        return None, None

    def sample(self) -> Tuple[str, List[UnifiedSample], Optional[str]]:
        path = Path(self.spec.source_locator)
        if not path.exists():
            return "source_unavailable", [], f"Input not found: {path}"
        samples: List[UnifiedSample] = []
        prompt_client = OpenAICompatibleClient(self.config.model)
        for index, row in enumerate(self.iter_records(path)):
            extracted = prompt_extract_record_content(row, self.spec, prompt_client)
            raw_question = extracted["raw_question_text"]
            raw_answer = resolve_multiple_choice_answer_text(extracted["raw_answer_text"], extracted["choice_map"])
            image = None
            image_source = None
            for path_str in extracted["image_paths"]:
                image, image_source = self.resolve_image(path_str, path.parent)
                if image is not None:
                    break
            if not raw_question and not image:
                continue
            samples.append(
                UnifiedSample(
                    dataset_key=self.spec.key,
                    dataset_display_name=self.spec.display_name,
                    subject=self.spec.subject,
                    source_dataset=self.spec.display_name,
                    source_split=self.spec.split or "local_file",
                    source_problem_id=str(row.get("id", row.get("problem_id", index))),
                    raw_question_text=raw_question,
                    raw_answer_text=raw_answer,
                    image=image,
                    image_source=image_source or (extracted["image_paths"][0] if extracted["image_paths"] else None),
                    raw_record=row,
                    metadata={
                        "row_index": index,
                        "source_file": str(path),
                        "image_paths": extracted["image_paths"],
                        "extraction_notes": extracted.get("extraction_notes", []),
                    },
                    choice_map=extracted["choice_map"],
                    force_requires_image=extracted["force_requires_image"],
                )
            )
            if len(samples) >= self.config.sample_per_dataset:
                break
        if self.config.sample_strategy == "random" and samples:
            rng = np.random.default_rng(self.config.shuffle_seed)
            indices = rng.permutation(len(samples)).tolist()[: self.config.sample_per_dataset]
            samples = [samples[i] for i in indices]
        else:
            samples = samples[: self.config.sample_per_dataset]
        return "available", samples, None


class HuggingFaceConnector(BaseConnector):
    def candidate_splits(self) -> List[str]:
        raw = [self.spec.split, "test", "validation", "val", "train"]
        return [item for item in raw if item]

    def load_dataset_any(self) -> Tuple[Optional[Dataset], Optional[str]]:
        last_error = None
        for split in self.candidate_splits():
            try:
                dataset = load_dataset(
                    self.spec.source_locator,
                    self.spec.hf_config_name,
                    split=split,
                )
                if isinstance(dataset, Dataset):
                    return dataset, split
            except Exception as exc:
                last_error = str(exc)
        try:
            dataset_obj = load_dataset(self.spec.source_locator, self.spec.hf_config_name)
            if isinstance(dataset_obj, DatasetDict):
                for split_name in dataset_obj.keys():
                    return dataset_obj[split_name], split_name
            if isinstance(dataset_obj, IterableDatasetDict):
                for split_name in dataset_obj.keys():
                    iterable = list(dataset_obj[split_name].take(self.config.sample_per_dataset))
                    return Dataset.from_list(iterable), split_name
        except Exception as exc:
            last_error = str(exc)
        return None, last_error

    def choose_field(self, row: Dict[str, Any], candidates: List[str], fallback_regex: str) -> Optional[str]:
        for key in candidates:
            if key in row and not is_missing_value(row[key]):
                return key
        for key, value in row.items():
            if is_missing_value(value):
                continue
            if re.search(fallback_regex, key, flags=re.IGNORECASE):
                return key
        return None

    def load_image(self, value: Any) -> Tuple[Optional[Image.Image], Optional[str]]:
        if is_missing_value(value):
            return None, None
        if isinstance(value, list):
            for item in value:
                image, source = self.load_image(item)
                if image is not None:
                    return image, source
            return None, None
        if isinstance(value, Image.Image):
            return value.convert("RGB"), "inline://pil_image"
        if isinstance(value, dict):
            path = value.get("path")
            bytes_data = value.get("bytes")
            if bytes_data:
                image = Image.open(io.BytesIO(bytes_data)).convert("RGB")
                return image, path or "inline://hf_image_bytes"
            if path and Path(path).exists():
                return Image.open(path).convert("RGB"), path
        if isinstance(value, str) and not is_null_like_text(value) and Path(value).exists():
            return Image.open(value).convert("RGB"), value
        return None, None

    def sample(self) -> Tuple[str, List[UnifiedSample], Optional[str]]:
        dataset, detail = self.load_dataset_any()
        if dataset is None:
            return "source_unavailable", [], detail or "load_dataset failed"
        if self.config.sample_strategy == "random":
            dataset = dataset.shuffle(seed=self.config.shuffle_seed)
        rows = dataset.select(range(min(self.config.sample_per_dataset, len(dataset))))
        samples: List[UnifiedSample] = []
        for index, row in enumerate(rows):
            row = dict(row)
            extracted = prompt_extract_record_content(row, self.spec, OpenAICompatibleClient(self.config.model))
            image_source_hint = extracted["image_paths"][0] if extracted["image_paths"] else None

            image = None
            image_source = None
            image_field_candidates: List[str] = []
            explicit_image_field = extracted.get("image_field")
            if explicit_image_field:
                image_field_candidates.append(str(explicit_image_field))
            image_field_candidates.extend(self.spec.image_fields or [])
            if "image" in row:
                image_field_candidates.append("image")
            if "decoded_image" in row:
                image_field_candidates.append("decoded_image")

            seen_fields: set[str] = set()
            for field_name in image_field_candidates:
                if not field_name or field_name in seen_fields:
                    continue
                seen_fields.add(field_name)
                if field_name not in row:
                    continue
                image, image_source = self.load_image(row.get(field_name))
                if image is not None:
                    if image_source is None:
                        image_source = f"inline://hf_field/{field_name}"
                    break

            if image is None:
                for path_str in extracted["image_paths"]:
                    image, image_source = self.load_image(path_str)
                    if image is not None:
                        break
            if image_source is None:
                image_source = image_source_hint
            raw_question = extracted["raw_question_text"]
            raw_answer = resolve_multiple_choice_answer_text(extracted["raw_answer_text"], extracted["choice_map"])
            if not raw_question and not image:
                continue
            samples.append(
                UnifiedSample(
                    dataset_key=self.spec.key,
                    dataset_display_name=self.spec.display_name,
                    subject=self.spec.subject,
                    source_dataset=self.spec.display_name,
                    source_split=detail or self.spec.split or "unknown",
                    source_problem_id=str(row.get("id", row.get("problem_id", index))),
                    raw_question_text=raw_question,
                    raw_answer_text=raw_answer,
                    image=image,
                    image_source=image_source,
                    raw_record=row,
                    metadata={
                        "row_index": index,
                        "image_paths": extracted["image_paths"],
                        "extraction_notes": extracted.get("extraction_notes", []),
                        "image_field": extracted.get("image_field"),
                    },
                    choice_map=extracted["choice_map"],
                    force_requires_image=extracted["force_requires_image"],
                )
            )
        return "available", samples, None


class GitHubConnector(BaseConnector):
    def ensure_repo(self) -> Tuple[Optional[Path], Optional[str]]:
        cache_root = Path(self.config.git_cache_root)
        ensure_dir(cache_root)
        target = cache_root / self.spec.key
        if target.exists() and (target / ".git").exists():
            return target, None
        if target.exists():
            shutil.rmtree(target)
        clone = subprocess.run(
            ["git", "clone", "--depth", "1", self.spec.source_locator, str(target)],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if clone.returncode != 0:
            detail = (clone.stderr or clone.stdout or "git clone failed").strip()
            return None, detail
        return target, None

    def discover_data_files(self, repo_dir: Path) -> List[Path]:
        scored: List[Tuple[int, Path]] = []
        for path in repo_dir.rglob("*"):
            if not path.is_file():
                continue
            suffix = path.suffix.lower()
            if suffix not in {".json", ".jsonl", ".csv", ".tsv"}:
                continue
            rel = str(path.relative_to(repo_dir)).lower()
            score = 0
            if any(token in rel for token in ["train", "test", "valid", "val", "dataset", "data", "problem", "question"]):
                score += 3
            if any(token in rel for token in ["image", "img", "diagram", "figure"]):
                score += 1
            if path.stat().st_size > 0:
                score += 1
            if self.spec.key == "geometry3k":
                if re.search(r"annotation_tool/data_collection/data_examples/\d+/data\.json$", rel):
                    score += 30
                if rel.endswith("logic_form.json"):
                    score -= 10
            scored.append((score, path))
        scored.sort(key=lambda item: (-item[0], str(item[1])))
        return [path for _, path in scored]

    def parse_records_from_json(self, path: Path) -> List[Dict[str, Any]]:
        with path.open("r", encoding="utf-8", errors="ignore") as file:
            data = json.load(file)
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            for key in ["data", "dataset", "datasets", "records", "items", "problems", "questions", "annotations", "example"]:
                value = data.get(key)
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    records = []
                    for item in value:
                        if not isinstance(item, dict):
                            continue
                        merged = dict(item)
                        if "keywords" in data and "keywords" not in merged:
                            merged["keywords"] = data.get("keywords")
                        records.append(merged)
                    if records:
                        return records
            if any(
                key in data
                for key in [
                    "question",
                    "problem",
                    "problem_text",
                    "compact_text",
                    "annotat_text",
                    "answer",
                    "solution",
                    "label",
                    "choices",
                    "options",
                    "image",
                    "diagram",
                ]
            ):
                return [data]
        return []

    def parse_records_from_jsonl(self, path: Path) -> List[Dict[str, Any]]:
        rows = []
        with path.open("r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(row, dict):
                    rows.append(row)
        return rows

    def parse_records_from_csv(self, path: Path, delimiter: str) -> List[Dict[str, Any]]:
        with path.open("r", encoding="utf-8", errors="ignore") as file:
            reader = csv.DictReader(file, delimiter=delimiter)
            return [dict(row) for row in reader]

    def load_records(self, path: Path) -> List[Dict[str, Any]]:
        if path.suffix.lower() == ".json":
            return self.parse_records_from_json(path)
        if path.suffix.lower() == ".jsonl":
            return self.parse_records_from_jsonl(path)
        if path.suffix.lower() == ".csv":
            return self.parse_records_from_csv(path, ",")
        if path.suffix.lower() == ".tsv":
            return self.parse_records_from_csv(path, "\t")
        return []

    def choose_field(self, row: Dict[str, Any], candidates: List[str], fallback_regex: str) -> Optional[str]:
        for key in candidates:
            if key in row and not is_missing_value(row[key]):
                return key
        for key, value in row.items():
            if is_missing_value(value):
                continue
            if re.search(fallback_regex, key, flags=re.IGNORECASE):
                return key
        return None

    def resolve_image(self, value: Any, base_dir: Path) -> Tuple[Optional[Image.Image], Optional[str]]:
        if value is None:
            return None, None
        if isinstance(value, list):
            for item in value:
                image, source = self.resolve_image(item, base_dir)
                if image is not None:
                    return image, source
            return None, None
        if isinstance(value, dict):
            if "path" in value:
                return self.resolve_image(value["path"], base_dir)
            return None, None
        if isinstance(value, str):
            candidate = Path(value)
            if not candidate.is_absolute():
                candidate = base_dir / candidate
            if candidate.exists() and candidate.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".webp"}:
                try:
                    return Image.open(candidate).convert("RGB"), str(candidate)
                except Exception:
                    return None, None
        return None, None

    def sample(self) -> Tuple[str, List[UnifiedSample], Optional[str]]:
        repo_dir, error = self.ensure_repo()
        if repo_dir is None:
            return "source_unavailable", [], error or "git clone failed"
        files = self.discover_data_files(repo_dir)
        if not files:
            return "source_unavailable", [], "No structured data files discovered in repository"
        samples: List[UnifiedSample] = []
        detail_errors: List[str] = []
        prompt_client = OpenAICompatibleClient(self.config.model)
        for file_path in files[:40]:
            try:
                records = self.load_records(file_path)
            except Exception as exc:
                detail_errors.append(f"{file_path.name}: {exc}")
                continue
            if not records:
                continue
            for index, row in enumerate(records):
                extracted = prompt_extract_record_content(row, self.spec, prompt_client)
                raw_question = extracted["raw_question_text"]
                raw_answer = resolve_multiple_choice_answer_text(extracted["raw_answer_text"], extracted["choice_map"])
                image = None
                image_source = None
                for path_str in extracted["image_paths"]:
                    image, image_source = self.resolve_image(path_str, file_path.parent)
                    if image is not None:
                        break
                if image is None and self.spec.key == "geometry3k":
                    for candidate_name in ["img_diagram.png", "img_problem.png", "img_diagram_point.png"]:
                        candidate = file_path.parent / candidate_name
                        if candidate.exists():
                            try:
                                image = Image.open(candidate).convert("RGB")
                                image_source = str(candidate)
                                break
                            except Exception:
                                continue
                if not raw_question and not image:
                    continue
                samples.append(
                    UnifiedSample(
                        dataset_key=self.spec.key,
                        dataset_display_name=self.spec.display_name,
                        subject=self.spec.subject,
                        source_dataset=self.spec.display_name,
                        source_split="repo_discovered",
                        source_problem_id=str(row.get("id", row.get("problem_id", len(samples)))),
                        raw_question_text=raw_question,
                        raw_answer_text=raw_answer,
                        image=image,
                        image_source=image_source or (extracted["image_paths"][0] if extracted["image_paths"] else None),
                        raw_record=row,
                        metadata={
                            "data_file": str(file_path),
                            "image_paths": extracted["image_paths"],
                            "extraction_notes": extracted.get("extraction_notes", []),
                        },
                        choice_map=extracted["choice_map"],
                        force_requires_image=extracted["force_requires_image"],
                    )
                )
                if len(samples) >= self.config.sample_per_dataset:
                    break
            if len(samples) >= self.config.sample_per_dataset:
                break
        if not samples:
            reason = "; ".join(detail_errors[:3]) if detail_errors else "No usable records extracted"
            return "source_unavailable", [], reason
        if self.config.sample_strategy == "random":
            rng = np.random.default_rng(self.config.shuffle_seed)
            indices = rng.permutation(len(samples)).tolist()[: self.config.sample_per_dataset]
            samples = [samples[i] for i in indices]
        else:
            samples = samples[: self.config.sample_per_dataset]
        return "available", samples, None


class RewriteAgent:
    def __init__(self, client: OpenAICompatibleClient, normalizer: TextNormalizer):
        self.client = client
        self.normalizer = normalizer

    def fallback_rewrite(
        self,
        dataset_name: str,
        question_text: str,
        normalized_answer: str,
        answer_type: str,
        choices: Dict[str, str],
    ) -> Dict[str, Any]:
        question_only, _ = self.normalizer.split_question_and_choices(question_text)
        question_only = self.normalizer.strip_hint(question_only)
        if not choices:
            if answer_type == "option" and any(
                token in question_only.lower()
                for token in ["which picture", "in which picture", "which figure", "which diagram", "which graph", "shown below", "illustrated"]
            ):
                return {
                    "strategy": "drop_image_index",
                    "rationale": "Visual selection question without textual choices should be dropped.",
                    "variants": [],
                    "discard_reason_codes": ["pure_image_index_choice"],
                }
            return {
                "strategy": "keep_open",
                "rationale": "Question is already open-ended.",
                "variants": [
                    {
                        "variant_id": "open_1",
                        "title": f"{dataset_name} 开放题",
                        "rewritten_question_text": question_only,
                        "expected_answer_type": answer_type,
                        "expected_answer": normalized_answer,
                        "split_role": "single",
                    }
                ],
                "discard_reason_codes": [],
            }
        if self.normalizer.is_pure_image_index_question(question_only, choices):
            return {
                "strategy": "drop_image_index",
                "rationale": "Pure image-index multiple choice question should be dropped.",
                "variants": [],
                "discard_reason_codes": ["pure_image_index_choice"],
            }
        if self.normalizer.is_compound_answer_question(question_only, choices):
            correct_text = choices.get(normalized_answer, "")
            pieces = [piece.strip() for piece in re.split(r"[;；]", correct_text) if piece.strip()]
            if not pieces:
                pieces = [correct_text] if correct_text else []
            variants = []
            for idx, piece in enumerate(pieces or [normalized_answer], start=1):
                variants.append(
                    {
                        "variant_id": f"open_{idx}",
                        "title": f"{dataset_name} 子题 {idx}",
                        "rewritten_question_text": f"{question_only}\n请只回答第 {idx} 个目标量。",
                        "expected_answer_type": "short_text",
                        "expected_answer": piece,
                        "split_role": f"part_{idx}",
                    }
                )
            return {
                "strategy": "split_open",
                "rationale": "Compound choice answer was split into multiple open-ended targets.",
                "variants": variants,
                "discard_reason_codes": [],
            }
        return {
            "strategy": "blank_open",
            "rationale": "Converted multiple choice into blank-style open-ended question.",
            "variants": [
                {
                    "variant_id": "open_1",
                    "title": f"{dataset_name} 开放题",
                    "rewritten_question_text": question_only,
                    "expected_answer_type": "numeric" if answer_type == "option" and choices.get(normalized_answer, "") else answer_type,
                    "expected_answer": choices.get(normalized_answer, normalized_answer),
                    "split_role": "single",
                }
            ],
            "discard_reason_codes": [],
        }

    def rewrite(
        self,
        dataset_name: str,
        normalized_question_text: str,
        normalized_answer_text: str,
        answer_type: str,
        choices: Dict[str, str],
    ) -> Dict[str, Any]:
        fallback = self.fallback_rewrite(
            dataset_name=dataset_name,
            question_text=normalized_question_text,
            normalized_answer=normalized_answer_text,
            answer_type=answer_type,
            choices=choices,
        )
        if not self.client.config.enabled or not choices:
            return fallback
        system_prompt = (
            "You are the Question Rewrite Agent in a multimodal dataset cleaning pipeline. "
            "Your task is to convert multiple-choice questions into open-ended variants under strict rules. "
            "Rules: 1) If the question is already open-ended, keep it. "
            "2) If it is a pure graph/diagram/waveform/figure label selection question such as graph A/B/C/D or diagram A/B/C/D, drop it. "
            "3) If it is a concept-discrimination question whose target was originally carried by the options, rewrite it as a blank-style open question without showing the options. "
            "4) If one option contains multiple atomic answers, split into multiple subquestions. "
            "5) Output strict JSON only."
        )
        user_prompt = json.dumps(
            {
                "dataset_name": dataset_name,
                "question_text": normalized_question_text,
                "choices": choices,
                "correct_option_letter": normalized_answer_text if answer_type == "option" else None,
                "correct_option_text": choices.get(normalized_answer_text, normalized_answer_text),
                "answer_type": answer_type,
                "fallback_result": fallback,
            },
            ensure_ascii=False,
            indent=2,
        )
        llm_result = self.client.chat_json(system_prompt, user_prompt)
        if not llm_result:
            return fallback
        strategy = to_plain_text(llm_result.get("strategy")).strip() or fallback["strategy"]
        variants = llm_result.get("variants")
        if not isinstance(variants, list):
            variants = fallback["variants"]
        if strategy == "drop_image_index":
            variants = []
        if not variants and strategy != "drop_image_index":
            return fallback
        return {
            "strategy": strategy,
            "rationale": to_plain_text(llm_result.get("rationale")) or fallback["rationale"],
            "variants": variants,
            "discard_reason_codes": llm_result.get("discard_reason_codes", fallback["discard_reason_codes"]),
            "llm_used": True,
        }


class DecisionAgent:
    def __init__(self, client: OpenAICompatibleClient):
        self.client = client

    def review_override(
        self,
        quality_components: Dict[str, Any],
        rewrite_report: Dict[str, Any],
        alignment_record: Dict[str, Any],
        quality_flags: List[str],
    ) -> Optional[Dict[str, Any]]:
        if not self.client.config.enabled:
            return None
        system_prompt = (
            "You are the Cleaning Decision Agent. Read the structured signals and decide one of pass/review/reject. "
            "Be conservative. If rewrite strategy is drop_image_index, reject. If quality is borderline or alignment risky, review. "
            "Return strict JSON with keys: decision, reason_codes, rationale."
        )
        user_prompt = json.dumps(
            {
                "quality_components": quality_components,
                "rewrite_report": rewrite_report,
                "alignment_record": alignment_record,
                "quality_flags": quality_flags,
            },
            ensure_ascii=False,
            indent=2,
        )
        result = self.client.chat_json(system_prompt, user_prompt)
        if not result:
            return None
        decision = to_plain_text(result.get("decision")).strip().lower()
        if decision not in {"pass", "review", "reject"}:
            return None
        reason_codes = result.get("reason_codes")
        if not isinstance(reason_codes, list):
            reason_codes = []
        return {
            "decision": decision,
            "reason_codes": [to_plain_text(code) for code in reason_codes if to_plain_text(code)],
            "rationale": to_plain_text(result.get("rationale")),
        }


class MultiDatasetCleaningPipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.text_normalizer = TextNormalizer()
        self.image_analyzer = ImageQualityAnalyzer()
        self.client = OpenAICompatibleClient(config.model)
        self.rewrite_agent = RewriteAgent(self.client, self.text_normalizer)
        self.decision_agent = DecisionAgent(self.client)
        self.pipeline_run_id = f"run_{stable_digest([utc_now(), 'multidataset-clean'], 16)}"
        self.ingest_batch_id = f"{config.batch_id_prefix}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        self.output_root = Path(config.output_root)
        self.run_dir = self.output_root / self.pipeline_run_id
        self.records_dir = self.run_dir / "records"
        self.dataset_root = self.run_dir / "datasets"
        ensure_dir(self.records_dir)
        ensure_dir(self.dataset_root)
        self.aggregate_summary: Dict[str, Any] = {
            "pipeline_run_id": self.pipeline_run_id,
            "created_at": utc_now(),
            "datasets": [],
        }

    def connector_for(self, spec: DatasetSpec) -> BaseConnector:
        if spec.source_kind == "local_file":
            return LocalFileConnector(spec, self.config)
        if spec.source_kind == "huggingface":
            return HuggingFaceConnector(spec, self.config)
        if spec.source_kind == "github":
            return GitHubConnector(spec, self.config)
        return SourceUnavailableConnector(spec, self.config)

    def run(self) -> Dict[str, Any]:
        dataset_summaries = []
        for spec in self.config.datasets:
            dataset_summary = self.run_single_dataset(spec)
            dataset_summaries.append(dataset_summary)
        self.aggregate_summary["datasets"] = dataset_summaries
        write_json(self.run_dir / "summary.json", self.aggregate_summary)
        return self.aggregate_summary

    def run_single_dataset(self, spec: DatasetSpec) -> Dict[str, Any]:
        connector = self.connector_for(spec)
        source_status, samples, detail = connector.sample()
        dataset_dir = self.dataset_root / spec.key
        ensure_dir(dataset_dir)
        if source_status != "available":
            summary = {
                "dataset_key": spec.key,
                "dataset_name": spec.display_name,
                "subject": spec.subject,
                "source_status": "source_unavailable",
                "detail": detail,
                "requested_samples": self.config.sample_per_dataset,
                "processed_samples": 0,
                "decision_counts": {"pass": 0, "review": 0, "reject": 0},
                "rewrite_strategy_counts": {},
            }
            write_json(dataset_dir / "summary.json", summary)
            return summary
        bundle = {
            "problem_main_records": [],
            "asset_records": [],
            "node_records": [],
            "cleaning_records": [],
            "reject_records": [],
            "alignment_records": [],
            "field_audit_records": [],
            "rewrite_reports": [],
            "open_ended_problem_variants": [],
            "asset_registry_records": [],
            "initial_scoring_records": [],
            "candidate_registrar_records": [],
        }
        result_mapping = {
            "problem_main_record": "problem_main_records",
            "asset_records": "asset_records",
            "node_records": "node_records",
            "cleaning_records": "cleaning_records",
            "reject_records": "reject_records",
            "alignment_records": "alignment_records",
            "field_audit_records": "field_audit_records",
            "rewrite_reports": "rewrite_reports",
            "open_ended_problem_variants": "open_ended_problem_variants",
            "asset_registry_record": "asset_registry_records",
            "initial_scoring_record": "initial_scoring_records",
            "candidate_registrar_record": "candidate_registrar_records",
        }
        sample_dir = dataset_dir / "samples"
        artifact_dir = dataset_dir / "artifacts"
        image_dir = artifact_dir / "images"
        crop_dir = artifact_dir / "crops"
        ensure_dir(sample_dir)
        ensure_dir(image_dir)
        ensure_dir(crop_dir)
        for index, sample in enumerate(samples):
            result = self.process_sample(spec, sample, image_dir, crop_dir)
            for result_key, bundle_key in result_mapping.items():
                value = result.get(result_key)
                if isinstance(value, list):
                    bundle[bundle_key].extend(value)
                elif value is not None:
                    bundle[bundle_key].append(value)
            if self.config.save_sample_bundle:
                sample_file = sample_dir / f"{result['problem_main_record']['problem_id']}.json"
                write_json(sample_file, result)
        records_dir = dataset_dir / "records"
        ensure_dir(records_dir)
        for key, rows in bundle.items():
            write_jsonl(records_dir / f"{key}.jsonl", rows)
        decision_counts = {"pass": 0, "review": 0, "reject": 0}
        rewrite_strategy_counts: Dict[str, int] = {}
        candidate_intake_counts: Dict[str, int] = {"keep": 0, "low_priority": 0, "reject": 0}
        for record in bundle["problem_main_records"]:
            decision_counts[record["clean_decision"]] += 1
            strategy = record.get("rewrite_strategy", "unknown")
            rewrite_strategy_counts[strategy] = rewrite_strategy_counts.get(strategy, 0) + 1
        for record in bundle["candidate_registrar_records"]:
            decision = to_plain_text(record.get("decision")).strip().lower()
            if decision in candidate_intake_counts:
                candidate_intake_counts[decision] += 1
        summary = {
            "dataset_key": spec.key,
            "dataset_name": spec.display_name,
            "subject": spec.subject,
            "source_status": "available",
            "detail": detail,
            "requested_samples": self.config.sample_per_dataset,
            "processed_samples": len(bundle["problem_main_records"]),
            "candidate_intake_counts": candidate_intake_counts,
            "decision_counts": decision_counts,
            "rewrite_strategy_counts": rewrite_strategy_counts,
            "records_dir": str(records_dir.relative_to(self.run_dir)),
        }
        write_json(dataset_dir / "summary.json", summary)
        return summary

    def process_sample(
        self,
        spec: DatasetSpec,
        sample: UnifiedSample,
        image_dir: Path,
        crop_dir: Path,
    ) -> Dict[str, Any]:
        created_at = utc_now()
        raw_question_text = sample.raw_question_text
        raw_answer_text = "" if is_null_like_text(sample.raw_answer_text) else sample.raw_answer_text
        normalized_question_text = self.text_normalizer.normalize_text(raw_question_text)
        normalized_question_text = self.text_normalizer.strip_hint(normalized_question_text)
        normalized_answer_text = self.text_normalizer.normalize_answer(raw_answer_text)
        language = self.text_normalizer.detect_language(normalized_question_text)
        original_answer_type = self.text_normalizer.infer_answer_type(normalized_answer_text)
        choices = dict(sample.choice_map)
        if not choices:
            choices = self.text_normalizer.extract_choice_map(normalized_question_text)
        image = sample.image
        image_count = 1 if image is not None else 0
        requires_image = sample.force_requires_image or self.text_normalizer.infer_requires_image(normalized_question_text, image_count)
        text_completeness = self.text_normalizer.text_completeness_score(raw_question_text, normalized_question_text)
        image_quality = self.image_analyzer.analyze(image) if image is not None else {
            "width": None,
            "height": None,
            "blur_score": 0.0,
            "contrast_score": 0.0,
            "noise_score": 0.0,
            "readability_score": 0.0,
            "crop_integrity_score": 0.0,
            "roi_bbox": None,
            "perceptual_hash": None,
        }
        image_bytes = self.image_analyzer.pil_to_png_bytes(image) if image is not None else b""
        problem_id = f"prob_{stable_digest([spec.key, sample.source_split, sample.source_problem_id, sha256_bytes(image_bytes) if image_bytes else raw_question_text])}"
        image_path: Optional[Path] = None
        if image is not None:
            image_path = image_dir / f"{problem_id}_primary.png"
            with image_path.open("wb") as file:
                file.write(image_bytes)
        rewrite_report = self.rewrite_agent.rewrite(
            dataset_name=spec.display_name,
            normalized_question_text=normalized_question_text,
            normalized_answer_text=normalized_answer_text,
            answer_type=original_answer_type,
            choices=choices,
        )
        open_variants = self.build_open_variants(problem_id, rewrite_report)
        alignment_record = self.build_alignment_record(problem_id, normalized_question_text, image_quality, requires_image)
        potential_scores = self.compute_potential_scores(
            normalized_question_text,
            normalized_answer_text,
            original_answer_type,
            requires_image,
            image_quality,
            choices,
            len(open_variants),
        )
        quality_flags = self.build_quality_flags(raw_question_text, raw_answer_text, text_completeness, image_quality, requires_image)
        asset_integrity = {
            "image_exists": image is not None,
            "image_width": image_quality.get("width"),
            "image_height": image_quality.get("height"),
            "text_completeness_score": text_completeness,
            "requires_image": requires_image,
        }
        asset_registry_record = llm_asset_registry_record(
            problem_id,
            normalized_question_text,
            normalized_answer_text,
            list(sample.metadata.get("image_paths", [])),
            dict(sample.metadata),
            asset_integrity,
            self.client,
        ) or heuristic_asset_registry_record(
            problem_id,
            normalized_question_text,
            normalized_answer_text,
            list(sample.metadata.get("image_paths", [])),
            dict(sample.metadata),
            image_quality,
        )
        initial_scoring_record = llm_initial_scoring_record(
            problem_id,
            normalized_question_text,
            normalized_answer_text,
            dict(sample.metadata),
            asset_registry_record,
            self.client,
        ) or heuristic_initial_scoring_record(
            problem_id,
            normalized_question_text,
            normalized_answer_text,
            dict(sample.metadata),
            asset_registry_record,
            potential_scores,
            quality_flags,
        )
        candidate_registrar_record = llm_candidate_registrar_record(
            problem_id,
            asset_registry_record,
            initial_scoring_record,
            self.client,
        ) or heuristic_candidate_registrar_record(problem_id, asset_registry_record, initial_scoring_record)
        candidate_decision = to_plain_text(candidate_registrar_record.get("decision")).strip().lower()
        if candidate_decision == "reject":
            gate = {
                "decision": "reject",
                "decision_reason_codes": ["candidate_intake_reject"],
                "clean_score": 0.0,
                "score_breakdown": {},
            }
            problem_main_record = self.build_problem_main_record(
                problem_id=problem_id,
                sample=sample,
                language=language,
                normalized_question_text=normalized_question_text,
                normalized_answer_text=normalized_answer_text,
                answer_type=original_answer_type,
                image_count=image_count,
                requires_image=requires_image,
                potential_scores=potential_scores,
                quality_flags=quality_flags,
                gate=gate,
                rewrite_report={"strategy": "candidate_reject", "rationale": "Rejected during candidate intake.", "discard_reason_codes": ["candidate_intake_reject"]},
                open_variants=[],
                created_at=created_at,
            )
            reject_record = {
                "reject_id": f"reject_{stable_digest([problem_id, self.pipeline_run_id, 'candidate_intake'])}",
                "problem_id": problem_id,
                "stage": "candidate_intake",
                "reject_level": "problem",
                "reject_reason_codes": candidate_registrar_record.get("decision_reasons", ["candidate_intake_reject"]),
                "reject_reason_detail": "Rejected by candidate registrar before cleaning.",
                "blocking_fields": list(asset_registry_record.get("issues", [])),
                "evidence_refs": [],
                "recoverable": True,
                "recommended_action": "drop_or_revisit_assets",
                "reviewed_by": None,
                "created_at": utc_now(),
            }
            return {
                "problem_main_record": problem_main_record,
                "asset_records": [],
                "node_records": [],
                "cleaning_records": [],
                "reject_records": [reject_record],
                "alignment_records": [],
                "field_audit_records": [],
                "rewrite_reports": [],
                "open_ended_problem_variants": [],
                "asset_registry_record": asset_registry_record,
                "initial_scoring_record": initial_scoring_record,
                "candidate_registrar_record": candidate_registrar_record,
            }
        gate = self.clean_gate(
            raw_question_text=raw_question_text,
            raw_answer_text=raw_answer_text,
            normalized_question_text=normalized_question_text,
            normalized_answer_text=normalized_answer_text,
            text_completeness=text_completeness,
            requires_image=requires_image,
            image_quality=image_quality,
            alignment_record=alignment_record,
            potential_scores=potential_scores,
            quality_flags=quality_flags,
            rewrite_report=rewrite_report,
            open_variants=open_variants,
        )
        roi_asset = self.create_roi_asset(problem_id, image, image_quality, crop_dir) if image is not None else None
        asset_records = self.build_asset_records(
            spec=spec,
            problem_id=problem_id,
            sample=sample,
            image_path=image_path,
            image_bytes=image_bytes,
            normalized_question_text=normalized_question_text,
            normalized_answer_text=normalized_answer_text,
            text_completeness=text_completeness,
            image_quality=image_quality,
            quality_flags=quality_flags,
            roi_asset=roi_asset,
            open_variants=open_variants,
        )
        node_records = self.build_node_records(
            problem_id=problem_id,
            normalized_question_text=normalized_question_text,
            normalized_answer_text=normalized_answer_text,
            original_answer_type=original_answer_type,
            quality_flags=quality_flags,
            image_quality=image_quality,
            open_variants=open_variants,
            gate=gate,
        )
        field_audits = self.build_field_audit_records(
            problem_id=problem_id,
            raw_question_text=raw_question_text,
            normalized_question_text=normalized_question_text,
            raw_answer_text=raw_answer_text,
            normalized_answer_text=normalized_answer_text,
            rewrite_report=rewrite_report,
            gate=gate,
        )
        cleaning_record = self.build_cleaning_record(
            problem_id=problem_id,
            spec=spec,
            asset_records=asset_records,
            alignment_record=alignment_record,
            quality_flags=quality_flags,
            gate=gate,
            rewrite_report=rewrite_report,
            open_variants=open_variants,
            text_completeness=text_completeness,
            image_quality=image_quality,
        )
        reject_record = self.build_reject_record(problem_id, gate, quality_flags, rewrite_report, alignment_record)
        problem_main_record = self.build_problem_main_record(
            problem_id=problem_id,
            sample=sample,
            language=language,
            normalized_question_text=normalized_question_text,
            normalized_answer_text=normalized_answer_text,
            answer_type=original_answer_type,
            image_count=image_count,
            requires_image=requires_image,
            potential_scores=potential_scores,
            quality_flags=quality_flags,
            gate=gate,
            rewrite_report=rewrite_report,
            open_variants=open_variants,
            created_at=created_at,
        )
        return {
            "problem_main_record": problem_main_record,
            "asset_records": asset_records,
            "node_records": node_records,
            "cleaning_records": [cleaning_record],
            "reject_records": [reject_record] if reject_record else [],
            "alignment_records": [alignment_record],
            "field_audit_records": field_audits,
            "rewrite_reports": [self.build_rewrite_record(problem_id, sample, rewrite_report, open_variants)],
            "open_ended_problem_variants": open_variants,
            "asset_registry_record": asset_registry_record,
            "initial_scoring_record": initial_scoring_record,
            "candidate_registrar_record": candidate_registrar_record,
        }

    def build_open_variants(self, problem_id: str, rewrite_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        variants: List[Dict[str, Any]] = []
        for idx, variant in enumerate(rewrite_report.get("variants", []), start=1):
            variants.append(
                {
                    "open_variant_id": f"open_{stable_digest([problem_id, str(idx)])}",
                    "parent_problem_id": problem_id,
                    "variant_index": idx,
                    "title": to_plain_text(variant.get("title") or f"开放题 {idx}"),
                    "rewritten_question_text": to_plain_text(variant.get("rewritten_question_text")),
                    "expected_answer_type": to_plain_text(variant.get("expected_answer_type") or "short_text"),
                    "expected_answer": to_plain_text(variant.get("expected_answer")),
                    "split_role": to_plain_text(variant.get("split_role") or "single"),
                }
            )
        return variants

    def create_roi_asset(
        self,
        problem_id: str,
        image: Optional[Image.Image],
        image_quality: Dict[str, Any],
        crop_dir: Path,
    ) -> Optional[Dict[str, Any]]:
        if image is None or not image_quality.get("roi_bbox"):
            return None
        bbox = image_quality["roi_bbox"]
        width, height = image_quality["width"], image_quality["height"]
        if bbox["width"] * bbox["height"] >= 0.98 * width * height:
            return None
        x1, y1 = bbox["x"], bbox["y"]
        x2, y2 = x1 + bbox["width"], y1 + bbox["height"]
        crop = image.convert("RGB").crop((x1, y1, x2, y2))
        crop_path = crop_dir / f"{problem_id}_roi.png"
        crop.save(crop_path, format="PNG")
        crop_bytes = crop_path.read_bytes()
        return {
            "asset_id": f"asset_{stable_digest([problem_id, 'region_crop'])}",
            "problem_id": problem_id,
            "asset_type": "crop",
            "asset_role": "region_crop",
            "source_uri": None,
            "storage_uri": str(crop_path),
            "file_format": "png",
            "file_size_bytes": crop_path.stat().st_size,
            "width": crop.width,
            "height": crop.height,
            "sha256": sha256_bytes(crop_bytes),
            "perceptual_hash": self.image_analyzer.perceptual_hash(crop),
            "source_text_snapshot": None,
            "normalized_text_snapshot": None,
            "text_completeness_score": None,
            "blur_score": image_quality["blur_score"],
            "readability_score": image_quality["readability_score"],
            "noise_score": image_quality["noise_score"],
            "cropped_from_asset_id": f"asset_{stable_digest([problem_id, 'primary_image'])}",
            "roi_bbox": bbox,
            "asset_quality_flags": [],
            "is_usable": True,
            "discard_reason_codes": [],
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }

    def compute_potential_scores(
        self,
        normalized_question_text: str,
        normalized_answer_text: str,
        answer_type: str,
        requires_image: bool,
        image_quality: Dict[str, Any],
        choices: Dict[str, str],
        variant_count: int,
    ) -> Dict[str, Any]:
        keyword_hits = len(re.findall(r"\b(calculate|determine|find|derive|prove|which|what|if|compute|write)\b", normalized_question_text, flags=re.IGNORECASE))
        math_hits = len(re.findall(r"[=+\-*/^()]", normalized_question_text))
        multimodal_strength = 0.25 + 0.45 * int(requires_image) + 0.08 * int(bool(choices)) + 0.15 * clamp(image_quality["readability_score"])
        multi_step = 0.2 + 0.2 * clamp(keyword_hits / 4.0) + 0.25 * clamp(math_hits / 20.0) + 0.1 * clamp(variant_count / 3.0)
        if len(normalized_question_text) > 120:
            multi_step += 0.15
        verifiability = 0.25
        if answer_type == "numeric":
            verifiability += 0.35
        elif answer_type == "option":
            verifiability += 0.4
        elif answer_type == "short_text":
            verifiability += 0.2
        verifiability += 0.15 * clamp(image_quality["readability_score"])
        verifiability += 0.1 if normalized_answer_text else -0.2
        return {
            "requires_image": requires_image,
            "multimodal_strength_score": round(clamp(multimodal_strength), 4),
            "multi_step_score": round(clamp(multi_step), 4),
            "verifiability_score": round(clamp(verifiability), 4),
            "review_priority": "high" if image_quality["readability_score"] < 0.45 or variant_count > 1 else "normal",
        }

    def build_quality_flags(
        self,
        raw_question_text: str,
        raw_answer_text: str,
        text_completeness: float,
        image_quality: Dict[str, Any],
        requires_image: bool,
    ) -> List[str]:
        flags: List[str] = []
        th = self.config.thresholds
        if not raw_question_text:
            flags.append("missing_question_text")
        if not raw_answer_text:
            flags.append("missing_answer")
        if requires_image and (image_quality["width"] is None or image_quality["height"] is None):
            flags.append("missing_core_image")
        if requires_image and image_quality["width"] is not None and image_quality["width"] < th.min_width:
            flags.append("low_resolution")
        if requires_image and image_quality["height"] is not None and image_quality["height"] < th.min_height:
            flags.append("low_resolution")
        sharpness_score = clamp(math.log1p(max(image_quality["blur_score"], 0.0)) / 8.0)
        if requires_image and image_quality["width"] is not None and sharpness_score < th.min_sharpness_score:
            flags.append("severe_global_blur")
        if requires_image and image_quality["width"] is not None and image_quality["readability_score"] < th.min_readability_score:
            flags.append("key_text_unreadable")
        if requires_image and image_quality["width"] is not None and image_quality["contrast_score"] < th.min_contrast_score:
            flags.append("contrast_too_low")
        if requires_image and image_quality["width"] is not None and image_quality["crop_integrity_score"] < 0.45:
            flags.append("severe_crop_loss")
        if text_completeness < th.min_text_completeness_score:
            flags.append("low_text_completeness")
        return sorted(set(flags))

    def build_alignment_record(
        self,
        problem_id: str,
        normalized_question_text: str,
        image_quality: Dict[str, Any],
        requires_image: bool,
    ) -> Dict[str, Any]:
        coverage_score = 0.9 if requires_image else 1.0
        consistency_score = 0.88 if requires_image else 1.0
        conflict_pairs = []
        if requires_image and image_quality["readability_score"] < 0.4:
            coverage_score -= 0.18
            consistency_score -= 0.2
            conflict_pairs.append({"type": "visual_readability_risk", "detail": "image readability below threshold", "confidence": 0.85})
        if requires_image and "figure" not in normalized_question_text.lower() and "image" not in normalized_question_text.lower():
            consistency_score -= 0.08
        coverage_score = round(clamp(coverage_score), 4)
        consistency_score = round(clamp(consistency_score), 4)
        status = "good"
        if consistency_score < self.config.thresholds.min_alignment_consistency:
            status = "bad"
        elif consistency_score < self.config.thresholds.min_alignment_consistency + 0.15:
            status = "risky"
        return {
            "alignment_id": f"align_{stable_digest([problem_id, self.pipeline_run_id])}",
            "problem_id": problem_id,
            "image_entity_refs": [f"asset_{stable_digest([problem_id, 'primary_image'])}"] if requires_image else [],
            "text_span_refs": [f"asset_{stable_digest([problem_id, 'question_text_normalized'])}"],
            "alignment_pairs": [
                {
                    "text_ref": f"asset_{stable_digest([problem_id, 'question_text_normalized'])}",
                    "image_ref": f"asset_{stable_digest([problem_id, 'primary_image'])}",
                    "relation": "global_figure_reference",
                    "confidence": 0.88,
                }
            ] if requires_image else [],
            "conflict_pairs": conflict_pairs,
            "coverage_score": coverage_score,
            "consistency_score": consistency_score,
            "alignment_status": status,
            "created_at": utc_now(),
        }

    def clean_gate(
        self,
        raw_question_text: str,
        raw_answer_text: str,
        normalized_question_text: str,
        normalized_answer_text: str,
        text_completeness: float,
        requires_image: bool,
        image_quality: Dict[str, Any],
        alignment_record: Dict[str, Any],
        potential_scores: Dict[str, Any],
        quality_flags: List[str],
        rewrite_report: Dict[str, Any],
        open_variants: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        th = self.config.thresholds
        hard_reject_codes: List[str] = []
        reason_codes: List[str] = []
        strategy = rewrite_report.get("strategy")
        if strategy == "drop_image_index":
            hard_reject_codes.append("pure_image_index_choice")
        if not raw_answer_text:
            hard_reject_codes.append("missing_answer")
        if not raw_question_text and not requires_image:
            hard_reject_codes.append("missing_question_text")
        if requires_image and "missing_core_image" in quality_flags:
            hard_reject_codes.append("missing_core_image")
        if requires_image and "low_resolution" in quality_flags:
            hard_reject_codes.append("low_resolution")
        if requires_image and "severe_global_blur" in quality_flags:
            hard_reject_codes.append("severe_blur")
        if requires_image and "key_text_unreadable" in quality_flags:
            hard_reject_codes.append("image_unreadable")
        if alignment_record["alignment_status"] == "bad":
            hard_reject_codes.append("text_image_misaligned")
        if strategy != "drop_image_index" and not open_variants:
            hard_reject_codes.append("rewrite_failed")
        quality_components = {
            "text_completeness": text_completeness,
            "image_readability": image_quality["readability_score"] if requires_image else 1.0,
            "alignment_consistency": alignment_record["consistency_score"] if requires_image else 1.0,
            "multimodal_strength": potential_scores["multimodal_strength_score"],
            "verifiability": potential_scores["verifiability_score"],
            "rewrite_quality": 0.0 if strategy == "drop_image_index" else 0.85 if open_variants else 0.2,
        }
        clean_score = round(
            clamp(
                0.2 * quality_components["text_completeness"]
                + 0.22 * quality_components["image_readability"]
                + 0.18 * quality_components["alignment_consistency"]
                + 0.14 * quality_components["multimodal_strength"]
                + 0.14 * quality_components["verifiability"]
                + 0.12 * quality_components["rewrite_quality"]
            ),
            4,
        )
        if hard_reject_codes:
            decision = "reject"
            reason_codes.extend(sorted(set(hard_reject_codes)))
        elif clean_score < th.reject_clean_score_below:
            decision = "reject"
            reason_codes.append("low_clean_score")
        elif (
            clean_score < th.review_clean_score_below
            or text_completeness < th.min_text_completeness_score
            or alignment_record["alignment_status"] == "risky"
            or "contrast_too_low" in quality_flags
            or rewrite_report.get("strategy") == "split_open"
        ):
            decision = "review"
            if clean_score < th.review_clean_score_below:
                reason_codes.append("borderline_clean_score")
            if text_completeness < th.min_text_completeness_score:
                reason_codes.append("normalized_question_incomplete")
            if alignment_record["alignment_status"] == "risky":
                reason_codes.append("alignment_risky")
            if "contrast_too_low" in quality_flags:
                reason_codes.append("contrast_too_low")
            if rewrite_report.get("strategy") == "split_open":
                reason_codes.append("split_variant_needs_review")
        else:
            decision = "pass"
            reason_codes.append("meets_cleaning_requirements")
        llm_override = self.decision_agent.review_override(quality_components, rewrite_report, alignment_record, quality_flags)
        if llm_override and decision == "review" and llm_override["decision"] in {"review", "reject"}:
            decision = llm_override["decision"]
            reason_codes.extend(llm_override["reason_codes"])
        return {
            "decision": decision,
            "decision_reason_codes": sorted(set(reason_codes)),
            "clean_score": clean_score,
            "score_breakdown": quality_components,
            "suggested_next_action": {"pass": "send_to_annotation", "review": "manual_review", "reject": "archive_reject_record"}[decision],
            "review_required": decision == "review",
        }

    def build_asset_records(
        self,
        spec: DatasetSpec,
        problem_id: str,
        sample: UnifiedSample,
        image_path: Optional[Path],
        image_bytes: bytes,
        normalized_question_text: str,
        normalized_answer_text: str,
        text_completeness: float,
        image_quality: Dict[str, Any],
        quality_flags: List[str],
        roi_asset: Optional[Dict[str, Any]],
        open_variants: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        created_at = utc_now()
        assets = [
            {
                "asset_id": f"asset_{stable_digest([problem_id, 'question_text_source'])}",
                "problem_id": problem_id,
                "asset_type": "text",
                "asset_role": "question_text_source",
                "source_uri": f"source://{spec.key}/{sample.source_split}/{sample.source_problem_id}/question",
                "storage_uri": f"inline://{problem_id}/question_source",
                "file_format": "txt",
                "file_size_bytes": len(sample.raw_question_text.encode('utf-8')),
                "width": None,
                "height": None,
                "sha256": sha256_bytes(sample.raw_question_text.encode('utf-8')),
                "perceptual_hash": None,
                "source_text_snapshot": sample.raw_question_text,
                "normalized_text_snapshot": None,
                "text_completeness_score": text_completeness,
                "blur_score": None,
                "readability_score": None,
                "noise_score": None,
                "cropped_from_asset_id": None,
                "roi_bbox": None,
                "asset_quality_flags": [],
                "is_usable": bool(sample.raw_question_text),
                "discard_reason_codes": [],
                "created_at": created_at,
                "updated_at": created_at,
            },
            {
                "asset_id": f"asset_{stable_digest([problem_id, 'question_text_normalized'])}",
                "problem_id": problem_id,
                "asset_type": "text",
                "asset_role": "question_text_normalized",
                "source_uri": None,
                "storage_uri": f"inline://{problem_id}/question_normalized",
                "file_format": "txt",
                "file_size_bytes": len(normalized_question_text.encode('utf-8')),
                "width": None,
                "height": None,
                "sha256": sha256_bytes(normalized_question_text.encode('utf-8')),
                "perceptual_hash": None,
                "source_text_snapshot": sample.raw_question_text,
                "normalized_text_snapshot": normalized_question_text,
                "text_completeness_score": text_completeness,
                "blur_score": None,
                "readability_score": None,
                "noise_score": None,
                "cropped_from_asset_id": None,
                "roi_bbox": None,
                "asset_quality_flags": [],
                "is_usable": bool(normalized_question_text),
                "discard_reason_codes": [],
                "created_at": created_at,
                "updated_at": created_at,
            },
            {
                "asset_id": f"asset_{stable_digest([problem_id, 'answer_raw'])}",
                "problem_id": problem_id,
                "asset_type": "answer",
                "asset_role": "answer_raw",
                "source_uri": f"source://{spec.key}/{sample.source_split}/{sample.source_problem_id}/answer",
                "storage_uri": f"inline://{problem_id}/answer_raw",
                "file_format": "txt",
                "file_size_bytes": len(sample.raw_answer_text.encode('utf-8')),
                "width": None,
                "height": None,
                "sha256": sha256_bytes(sample.raw_answer_text.encode('utf-8')),
                "perceptual_hash": None,
                "source_text_snapshot": sample.raw_answer_text,
                "normalized_text_snapshot": None,
                "text_completeness_score": 1.0 if sample.raw_answer_text else 0.0,
                "blur_score": None,
                "readability_score": None,
                "noise_score": None,
                "cropped_from_asset_id": None,
                "roi_bbox": None,
                "asset_quality_flags": [],
                "is_usable": bool(sample.raw_answer_text),
                "discard_reason_codes": [],
                "created_at": created_at,
                "updated_at": created_at,
            },
            {
                "asset_id": f"asset_{stable_digest([problem_id, 'answer_normalized'])}",
                "problem_id": problem_id,
                "asset_type": "answer",
                "asset_role": "answer_normalized",
                "source_uri": None,
                "storage_uri": f"inline://{problem_id}/answer_normalized",
                "file_format": "txt",
                "file_size_bytes": len(normalized_answer_text.encode('utf-8')),
                "width": None,
                "height": None,
                "sha256": sha256_bytes(normalized_answer_text.encode('utf-8')),
                "perceptual_hash": None,
                "source_text_snapshot": sample.raw_answer_text,
                "normalized_text_snapshot": normalized_answer_text,
                "text_completeness_score": 1.0 if normalized_answer_text else 0.0,
                "blur_score": None,
                "readability_score": None,
                "noise_score": None,
                "cropped_from_asset_id": None,
                "roi_bbox": None,
                "asset_quality_flags": [],
                "is_usable": bool(normalized_answer_text),
                "discard_reason_codes": [],
                "created_at": created_at,
                "updated_at": created_at,
            },
        ]
        if image_path is not None:
            assets.append(
                {
                    "asset_id": f"asset_{stable_digest([problem_id, 'primary_image'])}",
                    "problem_id": problem_id,
                    "asset_type": "image",
                    "asset_role": "primary_image",
                    "source_uri": sample.image_source,
                    "storage_uri": str(image_path),
                    "file_format": image_path.suffix.lstrip('.') or 'png',
                    "file_size_bytes": len(image_bytes),
                    "width": image_quality["width"],
                    "height": image_quality["height"],
                    "sha256": sha256_bytes(image_bytes),
                    "perceptual_hash": image_quality["perceptual_hash"],
                    "source_text_snapshot": None,
                    "normalized_text_snapshot": None,
                    "text_completeness_score": None,
                    "blur_score": image_quality["blur_score"],
                    "readability_score": image_quality["readability_score"],
                    "noise_score": image_quality["noise_score"],
                    "cropped_from_asset_id": None,
                    "roi_bbox": image_quality["roi_bbox"],
                    "asset_quality_flags": quality_flags,
                    "is_usable": True,
                    "discard_reason_codes": [],
                    "created_at": created_at,
                    "updated_at": created_at,
                }
            )
        if roi_asset is not None:
            assets.append(roi_asset)
        for variant in open_variants:
            assets.append(
                {
                    "asset_id": f"asset_{stable_digest([variant['open_variant_id'], 'open_text'])}",
                    "problem_id": problem_id,
                    "asset_type": "text",
                    "asset_role": "question_text_open_variant",
                    "source_uri": None,
                    "storage_uri": f"inline://{variant['open_variant_id']}",
                    "file_format": "txt",
                    "file_size_bytes": len(variant['rewritten_question_text'].encode('utf-8')),
                    "width": None,
                    "height": None,
                    "sha256": sha256_bytes(variant['rewritten_question_text'].encode('utf-8')),
                    "perceptual_hash": None,
                    "source_text_snapshot": sample.raw_question_text,
                    "normalized_text_snapshot": variant['rewritten_question_text'],
                    "text_completeness_score": text_completeness,
                    "blur_score": None,
                    "readability_score": None,
                    "noise_score": None,
                    "cropped_from_asset_id": None,
                    "roi_bbox": None,
                    "asset_quality_flags": [],
                    "is_usable": True,
                    "discard_reason_codes": [],
                    "created_at": created_at,
                    "updated_at": created_at,
                }
            )
        return assets

    def build_node_records(
        self,
        problem_id: str,
        normalized_question_text: str,
        normalized_answer_text: str,
        original_answer_type: str,
        quality_flags: List[str],
        image_quality: Dict[str, Any],
        open_variants: List[Dict[str, Any]],
        gate: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        created_at = utc_now()
        nodes: List[Dict[str, Any]] = []
        snippets = [item.strip() for item in re.split(r"(?<=[.!?])\s+|\n+", normalized_question_text) if item.strip()]
        for idx, snippet in enumerate(snippets[:5]):
            nodes.append(
                {
                    "node_id": f"node_{stable_digest([problem_id, 'text_fact', str(idx)])}",
                    "problem_id": problem_id,
                    "node_type": "text_fact",
                    "canonical_value": snippet,
                    "surface_forms": [snippet],
                    "origin_kind": "text",
                    "cognitive_level": "objective",
                    "source_refs": [f"asset_{stable_digest([problem_id, 'question_text_normalized'])}"],
                    "evidence_refs": [f"asset_{stable_digest([problem_id, 'question_text_normalized'])}"],
                    "upstream_node_ids": [],
                    "value_type": "text",
                    "normalized_value": {"text": snippet},
                    "unit": None,
                    "confidence": 0.92,
                    "verifiability": "high",
                    "ambiguity_level": "low",
                    "is_direct_from_source": True,
                    "is_generated_by_system": False,
                    "is_reviewed_by_human": False,
                    "stage_created": "cleaning",
                    "status": "active",
                    "version": 1,
                    "created_at": created_at,
                    "updated_at": created_at,
                }
            )
        nodes.append(
            {
                "node_id": f"node_{stable_digest([problem_id, 'answer_claim'])}",
                "problem_id": problem_id,
                "node_type": "answer_claim",
                "canonical_value": normalized_answer_text,
                "surface_forms": [normalized_answer_text],
                "origin_kind": "text",
                "cognitive_level": "objective",
                "source_refs": [f"asset_{stable_digest([problem_id, 'answer_normalized'])}"],
                "evidence_refs": [f"asset_{stable_digest([problem_id, 'answer_normalized'])}"],
                "upstream_node_ids": [],
                "value_type": original_answer_type,
                "normalized_value": {"answer": normalized_answer_text},
                "unit": None,
                "confidence": 0.98 if normalized_answer_text else 0.0,
                "verifiability": "high" if normalized_answer_text else "unverifiable",
                "ambiguity_level": "none" if normalized_answer_text else "high",
                "is_direct_from_source": True,
                "is_generated_by_system": False,
                "is_reviewed_by_human": False,
                "stage_created": "cleaning",
                "status": "active",
                "version": 1,
                "created_at": created_at,
                "updated_at": created_at,
            }
        )
        if image_quality["width"]:
            nodes.append(
                {
                    "node_id": f"node_{stable_digest([problem_id, 'image_width'])}",
                    "problem_id": problem_id,
                    "node_type": "derived_value",
                    "canonical_value": f"image_width={image_quality['width']} px",
                    "surface_forms": [str(image_quality["width"])],
                    "origin_kind": "calculation",
                    "cognitive_level": "computed",
                    "source_refs": [f"asset_{stable_digest([problem_id, 'primary_image'])}"],
                    "evidence_refs": [f"asset_{stable_digest([problem_id, 'primary_image'])}"],
                    "upstream_node_ids": [],
                    "value_type": "number",
                    "normalized_value": {"name": "image_width", "value": image_quality['width']},
                    "unit": "px",
                    "confidence": 1.0,
                    "verifiability": "high",
                    "ambiguity_level": "none",
                    "is_direct_from_source": False,
                    "is_generated_by_system": True,
                    "is_reviewed_by_human": False,
                    "stage_created": "cleaning",
                    "status": "active",
                    "version": 1,
                    "created_at": created_at,
                    "updated_at": created_at,
                }
            )
        for idx, variant in enumerate(open_variants):
            nodes.append(
                {
                    "node_id": f"node_{stable_digest([variant['open_variant_id'], 'open_variant'])}",
                    "problem_id": problem_id,
                    "node_type": "text_fact",
                    "canonical_value": variant["rewritten_question_text"],
                    "surface_forms": [variant["rewritten_question_text"]],
                    "origin_kind": "reasoning",
                    "cognitive_level": "computed",
                    "source_refs": [f"asset_{stable_digest([variant['open_variant_id'], 'open_text'])}"],
                    "evidence_refs": [f"asset_{stable_digest([variant['open_variant_id'], 'open_text'])}"],
                    "upstream_node_ids": [],
                    "value_type": "text",
                    "normalized_value": variant,
                    "unit": None,
                    "confidence": 0.88,
                    "verifiability": "medium",
                    "ambiguity_level": "low",
                    "is_direct_from_source": False,
                    "is_generated_by_system": True,
                    "is_reviewed_by_human": False,
                    "stage_created": "cleaning",
                    "status": "active",
                    "version": 1,
                    "created_at": created_at,
                    "updated_at": created_at,
                }
            )
        for idx, flag in enumerate(quality_flags):
            nodes.append(
                {
                    "node_id": f"node_{stable_digest([problem_id, 'quality_flag', str(idx)])}",
                    "problem_id": problem_id,
                    "node_type": "quality_signal",
                    "canonical_value": flag,
                    "surface_forms": [flag],
                    "origin_kind": "system_quality",
                    "cognitive_level": "computed",
                    "source_refs": [],
                    "evidence_refs": [],
                    "upstream_node_ids": [],
                    "value_type": "text",
                    "normalized_value": {"flag": flag},
                    "unit": None,
                    "confidence": 1.0,
                    "verifiability": "high",
                    "ambiguity_level": "none",
                    "is_direct_from_source": False,
                    "is_generated_by_system": True,
                    "is_reviewed_by_human": False,
                    "stage_created": "cleaning",
                    "status": "active",
                    "version": 1,
                    "created_at": created_at,
                    "updated_at": created_at,
                }
            )
        nodes.append(
            {
                "node_id": f"node_{stable_digest([problem_id, 'clean_decision'])}",
                "problem_id": problem_id,
                "node_type": "quality_signal",
                "canonical_value": f"clean_decision={gate['decision']}",
                "surface_forms": [gate["decision"]],
                "origin_kind": "system_quality",
                "cognitive_level": "computed",
                "source_refs": [],
                "evidence_refs": [],
                "upstream_node_ids": [],
                "value_type": "text",
                "normalized_value": {"decision": gate["decision"], "reasons": gate["decision_reason_codes"]},
                "unit": None,
                "confidence": 1.0,
                "verifiability": "high",
                "ambiguity_level": "none",
                "is_direct_from_source": False,
                "is_generated_by_system": True,
                "is_reviewed_by_human": False,
                "stage_created": "cleaning",
                "status": "active",
                "version": 1,
                "created_at": created_at,
                "updated_at": created_at,
            }
        )
        return nodes

    def build_field_audit_records(
        self,
        problem_id: str,
        raw_question_text: str,
        normalized_question_text: str,
        raw_answer_text: str,
        normalized_answer_text: str,
        rewrite_report: Dict[str, Any],
        gate: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        timestamp = utc_now()
        return [
            {
                "audit_id": f"audit_{stable_digest([problem_id, 'normalized_question_text'])}",
                "problem_id": problem_id,
                "record_type": "problem_main_record",
                "field_name": "normalized_question_text",
                "before_value": raw_question_text,
                "after_value": normalized_question_text,
                "change_type": "text_normalized",
                "trigger": "NormalizationAgent",
                "operator_type": "system",
                "created_at": timestamp,
            },
            {
                "audit_id": f"audit_{stable_digest([problem_id, 'normalized_answer_text'])}",
                "problem_id": problem_id,
                "record_type": "problem_main_record",
                "field_name": "normalized_answer_text",
                "before_value": raw_answer_text,
                "after_value": normalized_answer_text,
                "change_type": "answer_canonicalized",
                "trigger": "NormalizationAgent",
                "operator_type": "system",
                "created_at": timestamp,
            },
            {
                "audit_id": f"audit_{stable_digest([problem_id, 'rewrite_strategy'])}",
                "problem_id": problem_id,
                "record_type": "rewrite_report",
                "field_name": "rewrite_strategy",
                "before_value": None,
                "after_value": rewrite_report.get("strategy"),
                "change_type": "question_rewritten",
                "trigger": "QuestionRewriteAgent",
                "operator_type": "system",
                "created_at": timestamp,
            },
            {
                "audit_id": f"audit_{stable_digest([problem_id, 'clean_decision'])}",
                "problem_id": problem_id,
                "record_type": "cleaning_record",
                "field_name": "decision",
                "before_value": None,
                "after_value": gate.get("decision"),
                "change_type": "gate_decision",
                "trigger": "CleanGateAgent",
                "operator_type": "system",
                "created_at": timestamp,
            },
        ]

    def build_rewrite_record(
        self,
        problem_id: str,
        sample: UnifiedSample,
        rewrite_report: Dict[str, Any],
        open_variants: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "rewrite_id": f"rewrite_{stable_digest([problem_id, self.pipeline_run_id])}",
            "problem_id": problem_id,
            "source_problem_id": sample.source_problem_id,
            "strategy": rewrite_report.get("strategy"),
            "rationale": rewrite_report.get("rationale"),
            "discard_reason_codes": rewrite_report.get("discard_reason_codes", []),
            "variant_count": len(open_variants),
            "variants": open_variants,
            "created_at": utc_now(),
        }

    def build_cleaning_record(
        self,
        problem_id: str,
        spec: DatasetSpec,
        asset_records: List[Dict[str, Any]],
        alignment_record: Dict[str, Any],
        quality_flags: List[str],
        gate: Dict[str, Any],
        rewrite_report: Dict[str, Any],
        open_variants: List[Dict[str, Any]],
        text_completeness: float,
        image_quality: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "cleaning_id": f"clean_{stable_digest([problem_id, self.pipeline_run_id])}",
            "problem_id": problem_id,
            "cleaning_version": self.config.cleaning_version,
            "pipeline_run_id": self.pipeline_run_id,
            "dataset_name": spec.display_name,
            "input_asset_ids": [asset["asset_id"] for asset in asset_records],
            "normalization_actions": [
                {"action_type": "text_normalized", "trigger": "NormalizationAgent", "confidence": text_completeness, "human_confirmed": False},
                {"action_type": "answer_canonicalized", "trigger": "NormalizationAgent", "confidence": 0.98, "human_confirmed": False},
                {"action_type": "question_rewritten", "trigger": "QuestionRewriteAgent", "confidence": 0.85, "human_confirmed": False},
            ],
            "quality_checks": [
                {
                    "check": "image_quality",
                    "result": image_quality,
                    "passed": gate["decision"] != "reject",
                }
            ],
            "alignment_summary": {
                "alignment_id": alignment_record["alignment_id"],
                "coverage_score": alignment_record["coverage_score"],
                "consistency_score": alignment_record["consistency_score"],
                "alignment_status": alignment_record["alignment_status"],
            },
            "rewrite_summary": {
                "strategy": rewrite_report.get("strategy"),
                "variant_count": len(open_variants),
                "discard_reason_codes": rewrite_report.get("discard_reason_codes", []),
            },
            "risk_flags": quality_flags,
            "clean_score": gate["clean_score"],
            "decision": gate["decision"],
            "decision_reason_codes": gate["decision_reason_codes"],
            "review_ticket_id": f"review_{problem_id}" if gate["decision"] == "review" else None,
            "operator_type": "system",
            "started_at": utc_now(),
            "finished_at": utc_now(),
        }

    def build_reject_record(
        self,
        problem_id: str,
        gate: Dict[str, Any],
        quality_flags: List[str],
        rewrite_report: Dict[str, Any],
        alignment_record: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if gate["decision"] != "reject":
            return None
        return {
            "reject_id": f"reject_{stable_digest([problem_id, self.pipeline_run_id])}",
            "problem_id": problem_id,
            "stage": "cleaning",
            "reject_level": "problem",
            "reject_reason_codes": gate["decision_reason_codes"],
            "reject_reason_detail": rewrite_report.get("rationale") or "Rejected by cleaning gate.",
            "blocking_fields": quality_flags,
            "evidence_refs": [alignment_record["alignment_id"]],
            "recoverable": False,
            "recommended_action": "drop",
            "reviewed_by": None,
            "created_at": utc_now(),
        }

    def build_problem_main_record(
        self,
        problem_id: str,
        sample: UnifiedSample,
        language: str,
        normalized_question_text: str,
        normalized_answer_text: str,
        answer_type: str,
        image_count: int,
        requires_image: bool,
        potential_scores: Dict[str, Any],
        quality_flags: List[str],
        gate: Dict[str, Any],
        rewrite_report: Dict[str, Any],
        open_variants: List[Dict[str, Any]],
        created_at: str,
    ) -> Dict[str, Any]:
        return {
            "problem_id": problem_id,
            "source_dataset": sample.dataset_display_name,
            "source_split": sample.source_split,
            "source_problem_id": sample.source_problem_id,
            "ingest_batch_id": self.ingest_batch_id,
            "problem_type": "multimodal_reasoning",
            "domain_tags": [sample.subject],
            "language": language,
            "raw_question_text": sample.raw_question_text,
            "normalized_question_text": normalized_question_text,
            "raw_answer_text": sample.raw_answer_text,
            "normalized_answer_text": normalized_answer_text,
            "answer_type": answer_type,
            "image_count": image_count,
            "has_multiple_images": False,
            "requires_image": requires_image,
            "multimodal_strength_score": potential_scores["multimodal_strength_score"],
            "multi_step_score": potential_scores["multi_step_score"],
            "verifiability_score": potential_scores["verifiability_score"],
            "quality_risk_flags": quality_flags,
            "current_status": {"pass": "clean_passed", "review": "cleaning_review", "reject": "clean_rejected"}[gate["decision"]],
            "clean_decision": gate["decision"],
            "clean_decision_reason_codes": gate["decision_reason_codes"],
            "review_priority": potential_scores["review_priority"],
            "annotation_ready": gate["decision"] == "pass",
            "qa_precheck_ready": bool(open_variants) and gate["decision"] != "reject",
            "release_reserved": {},
            "rewrite_strategy": rewrite_report.get("strategy"),
            "open_variant_count": len(open_variants),
            "created_at": created_at,
            "updated_at": utc_now(),
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="多数据集采集与清洗智能体流水线")
    parser.add_argument("--config", type=str, default=None, help="YAML 配置文件路径")
    parser.add_argument("--output-dir", type=str, default=None, help="输出目录")
    parser.add_argument("--sample-per-dataset", type=int, default=None, help="每个数据集抽样数")
    parser.add_argument("--sample-strategy", type=str, choices=["head", "random"], default=None, help="抽样策略")
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    parser.add_argument("--disable-llm", action="store_true", help="禁用 LLM Agent，仅使用规则回退")
    parser.add_argument("--base-url", type=str, default=None, help="OpenAI 兼容接口 base url")
    parser.add_argument("--api-key", type=str, default=None, help="OpenAI 兼容接口 key")
    parser.add_argument("--model", type=str, default=None, help="模型名称")
    parser.add_argument("--reasoning-effort", type=str, default=None, help="推理强度，如 xhigh")
    return parser.parse_args()


def merge_cli_overrides(config: PipelineConfig, args: argparse.Namespace) -> PipelineConfig:
    if args.output_dir:
        config.output_root = args.output_dir
    if args.sample_per_dataset is not None:
        config.sample_per_dataset = args.sample_per_dataset
    if args.sample_strategy:
        config.sample_strategy = args.sample_strategy
    if args.seed is not None:
        config.shuffle_seed = args.seed
    if args.disable_llm:
        config.model.enabled = False
    if args.base_url:
        config.model.base_url = args.base_url
    if args.api_key:
        config.model.api_key = args.api_key
    if args.model:
        config.model.model = args.model
    if args.reasoning_effort:
        config.model.reasoning_effort = args.reasoning_effort
    return config


def main() -> None:
    args = parse_args()
    config = PipelineConfig.from_yaml(args.config)
    config = merge_cli_overrides(config, args)
    ensure_dir(Path(config.output_root))
    pipeline = MultiDatasetCleaningPipeline(config)
    summary = pipeline.run()
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
