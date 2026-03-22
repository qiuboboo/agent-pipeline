from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "outputs"
UNIFIED_PROMPT_PATH = PROJECT_ROOT / "prompts" / "extract_unified_sample.md"
SCORING_PROMPT_PATH = PROJECT_ROOT / "prompts" / "preliminary_value_scoring.md"


@dataclass
class ModelConfig:
    base_url: str
    api_key: str
    model: str = "gpt-5.4"


@dataclass
class ThresholdConfig:
    pass_score_threshold: float = 14.0
    reject_score_threshold: float = 10.0
    min_alignment_consistency: float = 0.55


@dataclass
class PipelineConfig:
    output_root: Path = DEFAULT_OUTPUT_ROOT
    cleaning_version: str = "v0.4.0"
    batch_id_prefix: str = "candidate-clean"
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)


api_key = os.environ.get("OPENAI_API_KEY_AGENT")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY_AGENT is not set")

model_config = ModelConfig(
    api_key=api_key,
    base_url="https://synai996.space/v1",
)

client = OpenAI(
    api_key=model_config.api_key,
    base_url=model_config.base_url,
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
    image: str | None
    image_source: str | None
    raw_record: dict[str, Any]
    metadata: dict[str, Any]
    choice_map: dict[str, str] = field(default_factory=dict)
    force_requires_image: bool = False


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def read_prompt(prompt_path: Path) -> str:
    return prompt_path.read_text(encoding="utf-8").strip()


def strip_code_fence(text: str) -> str:
    text = text.strip()
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def parse_json_response(text: str) -> dict:
    cleaned = strip_code_fence(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_unified_extraction_user_prompt(record: dict) -> str:
    record_json = json.dumps(record, ensure_ascii=False, indent=2)
    return f"""下面是一条原始 JSON 记录。
请按照 system prompt 的规则提取 UnifiedSample 所需的关键字段。
只返回 JSON 对象。

原始 JSON:
{record_json}
"""


def build_scoring_user_prompt(sample: dict) -> str:
    sample_json = json.dumps(sample, ensure_ascii=False, indent=2)
    return f"""下面是一个已经抽取出的候选样本，请你根据 system prompt 中的评分标准进行初步价值评分。
如果附带了图片，请结合图片一起判断；如果图片缺失，则仅根据文本保守评分。
只返回 JSON 对象。

候选样本:
{sample_json}
"""


def encode_image_as_data_url(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(image_path.name)
    mime_type = mime_type or "application/octet-stream"
    data = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{data}"


def build_user_content(user_prompt: str, image_paths: list[str] | None = None, asset_base_dir: Path | None = None):
    if not image_paths:
        return user_prompt
    content_blocks = [{"type": "text", "text": user_prompt}]
    for raw_path in image_paths:
        image_path = Path(raw_path)
        if not image_path.is_absolute() and asset_base_dir is not None:
            image_path = asset_base_dir / image_path
        if not image_path.exists():
            continue
        content_blocks.append({
            "type": "image_url",
            "image_url": {"url": encode_image_as_data_url(image_path)},
        })
    if len(content_blocks) == 1:
        return user_prompt
    return content_blocks


def call_model(system_prompt: str, user_prompt: str, image_paths: list[str] | None = None, asset_base_dir: Path | None = None) -> str:
    response = client.chat.completions.create(
        model=model_config.model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": build_user_content(user_prompt, image_paths=image_paths, asset_base_dir=asset_base_dir)},
        ],
    )
    return response.choices[0].message.content or ""


def iter_records(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        with path.open("r", encoding="utf-8") as fh:
            for index, line in enumerate(fh):
                line = line.strip()
                if not line:
                    continue
                yield index, json.loads(line)
        return
    if suffix == ".json":
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            for index, record in enumerate(data):
                yield index, record
            return
        if isinstance(data, dict):
            yield 0, data
            return
        raise ValueError(f"Unsupported JSON root type: {type(data).__name__}")
    raise ValueError(f"Unsupported input format: {path.suffix}")


def make_problem_id(prefix: str, record: dict, index: int) -> str:
    source_id = record.get("id") or record.get("image_id") or f"{index:06d}"
    return f"{prefix}_{str(source_id).replace('/', '_')}"


def normalize_choice_text(text: str) -> str:
    value = (text or "").strip()
    value = re.sub(r"^\(?[A-Za-z0-9]\)?[\s.、:_-]+", "", value)
    return value.strip()


def normalize_answer_text(text: str) -> str:
    return normalize_whitespace(normalize_choice_text(text))


def infer_answer_type(answer: str) -> str:
    if not answer:
        return "unknown"
    if re.fullmatch(r"[A-Z]", answer):
        return "option"
    if re.fullmatch(r"[+-]?(?:\d+(?:\.\d+)?|\.\d+)", answer):
        return "numeric"
    if len(answer.split()) <= 8:
        return "short_text"
    return "text"


def detect_language(text: str) -> str:
    if re.search(r"[\u4e00-\u9fff]", text):
        return "zh"
    if re.search(r"[A-Za-z]", text):
        return "en"
    return "unknown"


def resolve_choice_map(record: dict, extracted_choice_map: dict | None) -> dict[str, str]:
    if extracted_choice_map and isinstance(extracted_choice_map, dict):
        out = {}
        for key, value in extracted_choice_map.items():
            k = str(key).strip().upper()
            v = str(value).strip()
            if re.fullmatch(r"[A-H]", k) and v:
                out[k] = v
        if out:
            return out
    choices = record.get("choices")
    if isinstance(choices, list):
        return {chr(ord('A') + i): str(choice).strip() for i, choice in enumerate(choices) if str(choice).strip()}
    return {}


def resolve_multiple_choice_answer(record: dict, extracted_answer: str, choice_map: dict[str, str] | None = None) -> str:
    answer = (extracted_answer or "").strip()
    effective_choice_map = choice_map or resolve_choice_map(record, None)
    if not effective_choice_map:
        return normalize_answer_text(answer)

    ordered_choices = [effective_choice_map[k] for k in sorted(effective_choice_map.keys())]
    answer_upper = answer.upper().strip()
    letter_match = re.fullmatch(r"\(?([A-Z])\)?", answer_upper)
    if letter_match:
        key = letter_match.group(1)
        if key in effective_choice_map:
            return normalize_answer_text(effective_choice_map[key])
    mixed_match = re.match(r"^\(?([A-Z])\)?[\s.、:_-]+(.+)$", answer, flags=re.I)
    if mixed_match:
        answer = mixed_match.group(2).strip()
    normalized_answer = normalize_answer_text(answer)
    for choice in ordered_choices:
        if normalized_answer == normalize_answer_text(choice):
            return normalize_answer_text(choice)
    return normalized_answer


def resolve_image_paths(record: dict) -> list[str]:
    raw_images = record.get("images")
    if raw_images is None:
        raw_images = record.get("image")
    if not raw_images:
        return []
    if isinstance(raw_images, str):
        raw_images = [raw_images]
    return [str(Path(image_value)) for image_value in raw_images if str(image_value).strip()]


def score_sample(sample: dict, scoring_prompt_path: Path, asset_base_dir: Path | None = None) -> dict:
    system_prompt = read_prompt(scoring_prompt_path)
    user_prompt = build_scoring_user_prompt(sample)
    response_text = call_model(system_prompt, user_prompt, image_paths=sample.get("image_paths", []), asset_base_dir=asset_base_dir)
    assessment = parse_json_response(response_text)
    return {
        "preliminary_value_score": assessment.get("preliminary_value_score"),
        "preliminary_value_level": assessment.get("value_level", ""),
        "preliminary_value_reason": (assessment.get("short_reason") or "").strip(),
        "preliminary_value_dimensions": assessment.get("dimension_scores") or {},
    }


def build_unified_sample(record: dict, index: int, prefix: str, asset_base_dir: Path | None = None, scoring_prompt_path: Path | None = None) -> dict:
    system_prompt = read_prompt(UNIFIED_PROMPT_PATH)
    user_prompt = build_unified_extraction_user_prompt(record)
    response_text = call_model(system_prompt, user_prompt)
    extracted = parse_json_response(response_text)

    choice_map = resolve_choice_map(record, extracted.get("choice_map"))
    raw_answer_text = resolve_multiple_choice_answer(record, (extracted.get("raw_answer_text") or "").strip(), choice_map=choice_map)
    image_paths = extracted.get("image_paths") if isinstance(extracted.get("image_paths"), list) else resolve_image_paths(record)
    if not image_paths:
        image_paths = resolve_image_paths(record)
    image_paths = [str(Path(p)) for p in image_paths if str(p).strip()]

    problem_id = make_problem_id(prefix, record, index)
    raw_question_text = normalize_whitespace((extracted.get("raw_question_text") or record.get("question") or "").strip())

    unified = UnifiedSample(
        dataset_key=record.get("mini_test_subject") or record.get("domain") or prefix,
        dataset_display_name=record.get("mini_test_subject") or record.get("domain") or prefix,
        subject=record.get("mini_test_subject") or record.get("domain") or "unknown",
        source_dataset=prefix,
        source_split=str(record.get("split") or "unknown"),
        source_problem_id=str(record.get("id") or record.get("image_id") or index),
        raw_question_text=raw_question_text,
        raw_answer_text=raw_answer_text,
        image=image_paths[0] if image_paths else None,
        image_source=image_paths[0] if image_paths else None,
        raw_record=record,
        metadata={
            "problem_id": problem_id,
            "image_paths": image_paths,
            "extraction_notes": extracted.get("extraction_notes") or [],
        },
        choice_map=choice_map,
        force_requires_image=bool(extracted.get("force_requires_image")),
    )

    unified_dict = asdict(unified)
    sample_for_scoring = {
        "problem_id": problem_id,
        "question_text": unified_dict["raw_question_text"],
        "answer_text": unified_dict["raw_answer_text"],
        "image_paths": image_paths,
    }
    if scoring_prompt_path is not None:
        unified_dict["preliminary_scoring"] = score_sample(sample_for_scoring, scoring_prompt_path, asset_base_dir=asset_base_dir)
    return unified_dict


def decide_from_signals(
    scoring: dict,
    rewrite_report: dict,
    requires_image: bool,
    image_count: int,
    alignment_record: dict | None,
    thresholds: ThresholdConfig,
) -> str:
    score = scoring.get("preliminary_value_score")
    dims = scoring.get("preliminary_value_dimensions") or {}
    multimodal = dims.get("multimodal_necessity")
    decomposability = dims.get("node_decomposability")
    answer_stability = dims.get("answer_stability")

    if rewrite_report.get("strategy") == "drop_image_index":
        return "reject"

    if requires_image and image_count <= 0:
        return "reject"

    alignment_status = (alignment_record or {}).get("alignment_status")
    if alignment_status == "bad":
        return "reject"

    if isinstance(multimodal, (int, float)) and isinstance(decomposability, (int, float)):
        if multimodal >= 4 and decomposability >= 4:
            if isinstance(score, (int, float)) and score >= thresholds.reject_score_threshold:
                if alignment_status == "risky":
                    return "review"
                if isinstance(answer_stability, (int, float)) and answer_stability >= 4:
                    return "pass"
                if isinstance(score, (int, float)) and score >= thresholds.pass_score_threshold:
                    return "pass"
                return "review"

    if isinstance(score, (int, float)):
        if score >= thresholds.pass_score_threshold:
            return "pass"
        if score >= thresholds.reject_score_threshold:
            return "review"
        return "reject"
    return "review"


def build_alignment_record(unified: dict, problem_main_record: dict, pipeline_run_id: str, config: PipelineConfig) -> dict:
    question_text = problem_main_record["normalized_question_text"]
    requires_image = problem_main_record["requires_image"]
    image_count = problem_main_record["image_count"]

    image_hint = bool(re.search(r"\b(figure|diagram|graph|chart|image|shown|below|sample)\b", question_text, flags=re.I))
    coverage_score = 0.9 if requires_image else 1.0
    consistency_score = 0.88 if requires_image else 1.0
    conflict_pairs: list[dict[str, Any]] = []

    if requires_image and image_count <= 0:
        coverage_score -= 0.45
        consistency_score -= 0.45
        conflict_pairs.append({"type": "missing_image", "detail": "Question appears image-dependent but no image asset is present.", "confidence": 0.98})
    if requires_image and not image_hint:
        consistency_score -= 0.08
    if not requires_image and image_count > 0 and image_hint:
        consistency_score -= 0.04

    coverage_score = round(clamp(coverage_score), 4)
    consistency_score = round(clamp(consistency_score), 4)
    status = "good"
    if consistency_score < config.thresholds.min_alignment_consistency:
        status = "bad"
    elif consistency_score < config.thresholds.min_alignment_consistency + 0.15:
        status = "risky"

    return {
        "alignment_id": f"align_{problem_main_record['problem_id']}",
        "problem_id": problem_main_record["problem_id"],
        "pipeline_run_id": pipeline_run_id,
        "image_entity_refs": [f"asset_{problem_main_record['problem_id']}_image_1"] if image_count > 0 else [],
        "text_span_refs": [f"asset_{problem_main_record['problem_id']}_question_text_source"],
        "alignment_pairs": [
            {
                "text_ref": f"asset_{problem_main_record['problem_id']}_question_text_source",
                "image_ref": f"asset_{problem_main_record['problem_id']}_image_1" if image_count > 0 else None,
                "relation": "question_depends_on_image" if requires_image else "question_may_be_answered_without_image",
                "confidence": consistency_score,
            }
        ],
        "coverage_score": coverage_score,
        "consistency_score": consistency_score,
        "alignment_status": status,
        "conflict_pairs": conflict_pairs,
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }


def fallback_rewrite(question_text: str, normalized_answer: str, answer_type: str, choices: dict[str, str]) -> dict:
    question_only = question_text.strip()
    lower_q = question_only.lower()
    pure_image_index = bool(choices) and bool(re.search(r"\b(figure|diagram|graph|waveform|image)\s*[a-h0-9]\b", lower_q))
    if pure_image_index:
        return {
            "strategy": "drop_image_index",
            "rationale": "Pure image-index style multiple-choice question should be dropped.",
            "variants": [],
            "discard_reason_codes": ["pure_image_index_choice"],
        }
    if not choices:
        return {
            "strategy": "keep_open",
            "rationale": "Question is already open-ended.",
            "variants": [
                {
                    "variant_id": "open_1",
                    "title": "开放题 1",
                    "rewritten_question_text": question_only,
                    "expected_answer_type": answer_type,
                    "expected_answer": normalized_answer,
                    "split_role": "single",
                }
            ],
            "discard_reason_codes": [],
        }
    return {
        "strategy": "blank_open",
        "rationale": "Converted multiple-choice question into blank-style open-ended question.",
        "variants": [
            {
                "variant_id": "open_1",
                "title": "开放题 1",
                "rewritten_question_text": question_only,
                "expected_answer_type": answer_type if answer_type != "option" else "short_text",
                "expected_answer": normalized_answer,
                "split_role": "single",
            }
        ],
        "discard_reason_codes": [],
    }


def build_open_variants(problem_id: str, rewrite_report: dict) -> list[dict]:
    variants: list[dict] = []
    for idx, variant in enumerate(rewrite_report.get("variants", []), start=1):
        variants.append(
            {
                "open_variant_id": f"open_{problem_id}_{idx}",
                "parent_problem_id": problem_id,
                "variant_index": idx,
                "title": str(variant.get("title") or f"开放题 {idx}"),
                "rewritten_question_text": str(variant.get("rewritten_question_text") or ""),
                "expected_answer_type": str(variant.get("expected_answer_type") or "short_text"),
                "expected_answer": str(variant.get("expected_answer") or ""),
                "split_role": str(variant.get("split_role") or "single"),
            }
        )
    return variants


def build_rewrite_record(problem_main_record: dict, unified: dict, rewrite_report: dict, open_variants: list[dict], pipeline_run_id: str) -> dict:
    return {
        "rewrite_id": f"rewrite_{problem_main_record['problem_id']}",
        "problem_id": problem_main_record["problem_id"],
        "pipeline_run_id": pipeline_run_id,
        "source_problem_id": unified["source_problem_id"],
        "strategy": rewrite_report.get("strategy"),
        "rationale": rewrite_report.get("rationale"),
        "discard_reason_codes": rewrite_report.get("discard_reason_codes", []),
        "variant_count": len(open_variants),
        "variants": open_variants,
        "created_at": utc_now(),
    }


def build_problem_main_record(unified: dict, pipeline_run_id: str, config: PipelineConfig) -> dict:
    scoring = unified.get("preliminary_scoring") or {}
    normalized_answer = normalize_answer_text(unified["raw_answer_text"])
    answer_type = infer_answer_type(normalized_answer)
    rewrite_report = fallback_rewrite(unified["raw_question_text"], normalized_answer, answer_type, unified.get("choice_map") or {})
    open_variants = build_open_variants(unified["metadata"]["problem_id"], rewrite_report)
    return {
        "problem_id": unified["metadata"]["problem_id"],
        "source_dataset": unified["dataset_display_name"],
        "source_split": unified["source_split"],
        "source_problem_id": unified["source_problem_id"],
        "ingest_batch_id": pipeline_run_id,
        "problem_type": "multimodal_reasoning_candidate",
        "domain_tags": [unified.get("subject") or "unknown"],
        "language": detect_language(unified["raw_question_text"]),
        "raw_question_text": unified["raw_question_text"],
        "normalized_question_text": unified["raw_question_text"],
        "raw_answer_text": unified["raw_answer_text"],
        "normalized_answer_text": normalized_answer,
        "answer_type": answer_type,
        "image_count": len(unified["metadata"].get("image_paths", [])),
        "has_multiple_images": len(unified["metadata"].get("image_paths", [])) > 1,
        "requires_image": bool(unified.get("force_requires_image")) or bool(unified["metadata"].get("image_paths")),
        "multimodal_strength_score": (unified.get("preliminary_scoring", {}).get("preliminary_value_dimensions") or {}).get("multimodal_necessity"),
        "multi_step_score": (unified.get("preliminary_scoring", {}).get("preliminary_value_dimensions") or {}).get("node_decomposability"),
        "verifiability_score": (unified.get("preliminary_scoring", {}).get("preliminary_value_dimensions") or {}).get("answer_stability"),
        "quality_risk_flags": [],
        "current_status": None,
        "clean_decision": None,
        "clean_decision_reason_codes": [],
        "review_priority": unified.get("preliminary_scoring", {}).get("preliminary_value_level"),
        "annotation_ready": False,
        "qa_precheck_ready": bool(open_variants),
        "release_reserved": {},
        "rewrite_strategy": rewrite_report.get("strategy"),
        "open_variant_count": len(open_variants),
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }


def build_asset_records(unified: dict) -> list[dict]:
    created_at = utc_now()
    problem_id = unified["metadata"]["problem_id"]
    assets: list[dict] = [
        {
            "asset_id": f"asset_{problem_id}_question_text_source",
            "problem_id": problem_id,
            "asset_type": "text",
            "asset_role": "question_text_source",
            "source_uri": None,
            "storage_uri": f"inline://{problem_id}/question_source",
            "file_format": "txt",
            "file_size_bytes": len(unified["raw_question_text"].encode("utf-8")),
            "width": None,
            "height": None,
            "sha256": None,
            "perceptual_hash": None,
            "source_text_snapshot": unified["raw_question_text"],
            "normalized_text_snapshot": unified["raw_question_text"],
            "text_completeness_score": None,
            "blur_score": None,
            "readability_score": None,
            "noise_score": None,
            "cropped_from_asset_id": None,
            "roi_bbox": None,
            "asset_quality_flags": [],
            "is_usable": bool(unified["raw_question_text"]),
            "discard_reason_codes": [],
            "created_at": created_at,
            "updated_at": created_at,
        },
        {
            "asset_id": f"asset_{problem_id}_answer_text_source",
            "problem_id": problem_id,
            "asset_type": "text",
            "asset_role": "answer_text_source",
            "source_uri": None,
            "storage_uri": f"inline://{problem_id}/answer_source",
            "file_format": "txt",
            "file_size_bytes": len(unified["raw_answer_text"].encode("utf-8")),
            "width": None,
            "height": None,
            "sha256": None,
            "perceptual_hash": None,
            "source_text_snapshot": unified["raw_answer_text"],
            "normalized_text_snapshot": normalize_answer_text(unified["raw_answer_text"]),
            "text_completeness_score": None,
            "blur_score": None,
            "readability_score": None,
            "noise_score": None,
            "cropped_from_asset_id": None,
            "roi_bbox": None,
            "asset_quality_flags": [],
            "is_usable": bool(unified["raw_answer_text"]),
            "discard_reason_codes": [],
            "created_at": created_at,
            "updated_at": created_at,
        },
    ]
    for i, image_path in enumerate(unified["metadata"].get("image_paths", []), start=1):
        assets.append(
            {
                "asset_id": f"asset_{problem_id}_image_{i}",
                "problem_id": problem_id,
                "asset_type": "image",
                "asset_role": "primary_image" if i == 1 else f"aux_image_{i}",
                "source_uri": image_path,
                "storage_uri": image_path,
                "file_format": Path(image_path).suffix.lstrip(".") or None,
                "file_size_bytes": None,
                "width": None,
                "height": None,
                "sha256": None,
                "perceptual_hash": None,
                "source_text_snapshot": None,
                "normalized_text_snapshot": None,
                "text_completeness_score": None,
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


def build_cleaning_record(unified: dict, problem_main_record: dict, asset_records: list[dict], alignment_record: dict, rewrite_report: dict, open_variants: list[dict], pipeline_run_id: str, config: PipelineConfig) -> dict:
    scoring = unified.get("preliminary_scoring") or {}
    decision = problem_main_record["clean_decision"]
    score = scoring.get("preliminary_value_score")
    if decision == "pass":
        reason_codes = ["meets_candidate_threshold"]
    elif decision == "review":
        reason_codes = ["borderline_candidate_score"]
    else:
        reason_codes = ["below_candidate_threshold"]
    return {
        "cleaning_id": f"clean_{unified['metadata']['problem_id']}",
        "problem_id": unified["metadata"]["problem_id"],
        "cleaning_version": config.cleaning_version,
        "pipeline_run_id": pipeline_run_id,
        "dataset_name": unified["dataset_display_name"],
        "input_asset_ids": [asset["asset_id"] for asset in asset_records],
        "normalization_actions": [
            {"action_type": "text_normalized", "trigger": "NormalizationAgent", "confidence": 0.90, "human_confirmed": False},
            {"action_type": "answer_canonicalized", "trigger": "NormalizationAgent", "confidence": 0.95, "human_confirmed": False},
            {"action_type": "llm_unified_extraction", "trigger": "UnifiedSampleExtractionAgent", "confidence": 0.85, "human_confirmed": False},
            {"action_type": "question_rewritten", "trigger": "QuestionRewriteAgent", "confidence": 0.70, "human_confirmed": False},
        ],
        "quality_checks": [
            {"check": "preliminary_value_scoring", "result": scoring, "passed": decision != "reject"}
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
        "risk_flags": [],
        "clean_score": score,
        "decision": decision,
        "decision_reason_codes": reason_codes,
        "review_ticket_id": f"review_{unified['metadata']['problem_id']}" if decision == "review" else None,
        "operator_type": "system",
        "started_at": utc_now(),
        "finished_at": utc_now(),
    }


def build_reject_record(problem_main_record: dict, cleaning_record: dict, pipeline_run_id: str) -> dict | None:
    if problem_main_record["clean_decision"] != "reject":
        return None
    return {
        "reject_id": f"reject_{problem_main_record['problem_id']}",
        "problem_id": problem_main_record["problem_id"],
        "pipeline_run_id": pipeline_run_id,
        "stage": "candidate_cleaning",
        "reject_level": "problem",
        "reject_reason_codes": cleaning_record["decision_reason_codes"],
        "reject_reason_detail": "Rejected by preliminary candidate cleaning gate.",
        "blocking_fields": [],
        "evidence_refs": [cleaning_record["cleaning_id"]],
        "recoverable": False,
        "recommended_action": "drop",
        "reviewed_by": None,
        "created_at": utc_now(),
    }


def build_field_audit_records(unified: dict, problem_main_record: dict, cleaning_record: dict, rewrite_report: dict) -> list[dict]:
    timestamp = utc_now()
    problem_id = problem_main_record["problem_id"]
    raw_question = unified["raw_record"].get("question") or ""
    raw_answer = unified["raw_record"].get("answer") or ""
    return [
        {
            "audit_id": f"audit_{problem_id}_normalized_question_text",
            "problem_id": problem_id,
            "record_type": "problem_main_record",
            "field_name": "normalized_question_text",
            "before_value": raw_question,
            "after_value": problem_main_record["normalized_question_text"],
            "change_type": "text_normalized",
            "trigger": "UnifiedSampleExtractionAgent",
            "operator_type": "system",
            "created_at": timestamp,
        },
        {
            "audit_id": f"audit_{problem_id}_normalized_answer_text",
            "problem_id": problem_id,
            "record_type": "problem_main_record",
            "field_name": "normalized_answer_text",
            "before_value": raw_answer,
            "after_value": problem_main_record["normalized_answer_text"],
            "change_type": "answer_canonicalized",
            "trigger": "NormalizationAgent",
            "operator_type": "system",
            "created_at": timestamp,
        },
        {
            "audit_id": f"audit_{problem_id}_rewrite_strategy",
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
            "audit_id": f"audit_{problem_id}_clean_decision",
            "problem_id": problem_id,
            "record_type": "cleaning_record",
            "field_name": "decision",
            "before_value": None,
            "after_value": cleaning_record["decision"],
            "change_type": "gate_decision",
            "trigger": "CandidateCleanGate",
            "operator_type": "system",
            "created_at": timestamp,
        },
    ]


def build_paths(output_root: Path) -> dict[str, Path]:
    return {
        "sample": output_root / "samples.jsonl",
        "unified": output_root / "unified_samples.jsonl",
        "problem_main": output_root / "problem_main_records.jsonl",
        "asset": output_root / "asset_records.jsonl",
        "alignment": output_root / "alignment_records.jsonl",
        "rewrite": output_root / "rewrite_reports.jsonl",
        "open_variants": output_root / "open_ended_problem_variants.jsonl",
        "cleaning": output_root / "cleaning_records.jsonl",
        "reject": output_root / "reject_records.jsonl",
        "field_audit": output_root / "field_audit_records.jsonl",
        "summary": output_root / "summary.json",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract UnifiedSample-like records and multidataset-cleaning-style minimal records")
    parser.add_argument("input", type=Path, help="Path to a JSON or JSONL file that contains raw dataset records")
    parser.add_argument("--prefix", default="m3cot")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--reset-output", action="store_true")
    parser.add_argument("--scoring-prompt", type=Path, default=SCORING_PROMPT_PATH, help="Path to the value-scoring prompt document")
    parser.add_argument("--no-scoring", action="store_true", help="Skip preliminary value scoring")
    parser.add_argument("--write-unified", action="store_true", help="Also write UnifiedSample-like outputs to unified_samples.jsonl")
    args = parser.parse_args()

    config = PipelineConfig()
    output_root = config.output_root
    paths = build_paths(output_root)
    pipeline_run_id = f"{config.batch_id_prefix}_{utc_now()}"

    if args.reset_output:
        for path in paths.values():
            if path.exists() and path.is_file():
                path.unlink()

    scoring_prompt_path = None if args.no_scoring else args.scoring_prompt
    processed = 0
    decision_counts = {"pass": 0, "review": 0, "reject": 0}
    rewrite_strategy_counts: dict[str, int] = {}

    for index, record in iter_records(args.input):
        unified = build_unified_sample(record, index, args.prefix, asset_base_dir=args.input.parent, scoring_prompt_path=scoring_prompt_path)
        scoring = unified.get("preliminary_scoring") or {}
        sample = {
            "problem_id": unified["metadata"]["problem_id"],
            "question_text": unified["raw_question_text"],
            "answer_text": unified["raw_answer_text"],
            "image_paths": unified["metadata"]["image_paths"],
        }
        if scoring:
            sample.update(scoring)
        append_jsonl(paths["sample"], sample)
        if args.write_unified:
            append_jsonl(paths["unified"], unified)

        problem_main_record = build_problem_main_record(unified, pipeline_run_id, config)
        rewrite_report = fallback_rewrite(
            problem_main_record["normalized_question_text"],
            problem_main_record["normalized_answer_text"],
            problem_main_record["answer_type"],
            unified.get("choice_map") or {},
        )
        open_variants = build_open_variants(problem_main_record["problem_id"], rewrite_report)
        rewrite_record = build_rewrite_record(problem_main_record, unified, rewrite_report, open_variants, pipeline_run_id)
        asset_records = build_asset_records(unified)
        alignment_record = build_alignment_record(unified, problem_main_record, pipeline_run_id, config)

        final_decision = decide_from_signals(
            scoring=scoring,
            rewrite_report=rewrite_report,
            requires_image=problem_main_record["requires_image"],
            image_count=problem_main_record["image_count"],
            alignment_record=alignment_record,
            thresholds=config.thresholds,
        )
        problem_main_record["clean_decision"] = final_decision
        problem_main_record["current_status"] = {"pass": "clean_passed", "review": "cleaning_review", "reject": "clean_rejected"}[final_decision]
        problem_main_record["annotation_ready"] = final_decision == "pass"
        problem_main_record["qa_precheck_ready"] = bool(open_variants) and final_decision != "reject"

        cleaning_record = build_cleaning_record(unified, problem_main_record, asset_records, alignment_record, rewrite_report, open_variants, pipeline_run_id, config)
        reject_record = build_reject_record(problem_main_record, cleaning_record, pipeline_run_id)
        field_audits = build_field_audit_records(unified, problem_main_record, cleaning_record, rewrite_report)

        append_jsonl(paths["problem_main"], problem_main_record)
        for asset in asset_records:
            append_jsonl(paths["asset"], asset)
        append_jsonl(paths["alignment"], alignment_record)
        append_jsonl(paths["rewrite"], rewrite_record)
        for variant in open_variants:
            append_jsonl(paths["open_variants"], variant)
        append_jsonl(paths["cleaning"], cleaning_record)
        for audit in field_audits:
            append_jsonl(paths["field_audit"], audit)
        if reject_record:
            append_jsonl(paths["reject"], reject_record)

        decision_counts[problem_main_record["clean_decision"]] += 1
        strategy = rewrite_record.get("strategy") or "unknown"
        rewrite_strategy_counts[strategy] = rewrite_strategy_counts.get(strategy, 0) + 1
        print(f"built sample: {sample['problem_id']}")
        processed += 1
        if args.limit and processed >= args.limit:
            break

    summary = {
        "pipeline_run_id": pipeline_run_id,
        "created_at": utc_now(),
        "input_path": str(args.input),
        "requested_samples": args.limit or processed,
        "processed_samples": processed,
        "decision_counts": decision_counts,
        "rewrite_strategy_counts": rewrite_strategy_counts,
        "records_dir": str(output_root),
    }
    write_json(paths["summary"], summary)

    print(f"Saved {processed} sample(s) to {paths['sample']}")
    if args.write_unified:
        print(f"Saved {processed} unified sample(s) to {paths['unified']}")
    print(f"Saved {processed} problem main record(s) to {paths['problem_main']}")
    print(f"Saved asset records to {paths['asset']}")
    print(f"Saved alignment records to {paths['alignment']}")
    print(f"Saved rewrite reports to {paths['rewrite']}")
    print(f"Saved open-ended variants to {paths['open_variants']}")
    print(f"Saved cleaning records to {paths['cleaning']}")
    print(f"Saved field audit records to {paths['field_audit']}")
    if paths['reject'].exists():
        print(f"Saved reject records to {paths['reject']}")
    print(f"Saved summary to {paths['summary']}")


if __name__ == "__main__":
    main()
