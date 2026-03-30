from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from .pipeline_clients import OpenAICompatibleClient
    from .pipeline_extraction import read_prompt
    from .pipeline_utils import to_plain_text
except ImportError:
    from pipeline_clients import OpenAICompatibleClient
    from pipeline_extraction import read_prompt
    from pipeline_utils import to_plain_text


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMPT_ROOT = PROJECT_ROOT / "prompts"
GATE_DECISION_PROMPT_PATH = PROMPT_ROOT / "cleaning" / "gate_decision_agent.md"
SAMPLE_UNDERSTANDING_PROMPT_PATH = PROMPT_ROOT / "cleaning" / "sample_understanding_agent.md"


class DecisionOverrideProtocol:
    def review_override(
        self,
        quality_components: Dict[str, Any],
        rewrite_report: Dict[str, Any],
        alignment_record: Dict[str, Any],
        solvability_report: Dict[str, Any],
        quality_flags: List[str],
        sample_understanding: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        ...


class SampleUnderstandingAgent:
    def __init__(self, client: OpenAICompatibleClient):
        self.client = client
        self.system_prompt = read_prompt(SAMPLE_UNDERSTANDING_PROMPT_PATH) if SAMPLE_UNDERSTANDING_PROMPT_PATH.exists() else (
            "You are the Multimodal Sample Understanding Agent in a cleaning pipeline. "
            "Judge whether the sample is semantically understandable enough for downstream annotation or review. "
            "Prefer semantic usefulness over hard visual thresholds and return strict JSON only."
        )

    def fallback_assess(
        self,
        raw_question_text: str,
        raw_answer_text: str,
        requires_image: bool,
        quality_flags: List[str],
        alignment_record: Dict[str, Any],
        solvability_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        question_complete = bool(raw_question_text)
        answer_complete = bool(raw_answer_text)
        if not question_complete or (requires_image and "missing_core_image" in quality_flags):
            completeness_status = "broken"
        elif not answer_complete or "low_text_completeness" in quality_flags:
            completeness_status = "partial"
        else:
            completeness_status = "complete"
        if not requires_image:
            image_support_status = "not_needed"
        elif "missing_core_image" in quality_flags or "key_text_unreadable" in quality_flags:
            image_support_status = "missing_or_unusable"
        elif alignment_record.get("alignment_status") in {"bad", "risky"} or "low_resolution" in quality_flags:
            image_support_status = "uncertain_but_usable"
        else:
            image_support_status = "clear_enough"
        if completeness_status == "broken" or (requires_image and image_support_status == "missing_or_unusable"):
            joint_understanding_status = "not_understandable"
        elif completeness_status == "partial" or image_support_status == "uncertain_but_usable" or solvability_report.get("decision_hint") != "pass":
            joint_understanding_status = "partially_understandable"
        else:
            joint_understanding_status = "understandable"
        reason_codes: List[str] = []
        if not question_complete:
            reason_codes.append("missing_question_text")
        if not answer_complete:
            reason_codes.append("missing_answer")
        if requires_image and image_support_status == "missing_or_unusable":
            reason_codes.append("missing_required_image")
        if alignment_record.get("alignment_status") in {"bad", "risky"}:
            reason_codes.append("alignment_requires_review")
        if not reason_codes:
            reason_codes.append(
                "jointly_understandable"
                if joint_understanding_status == "understandable"
                else "joint_understanding_partial"
            )
        risk_flags = [flag for flag in quality_flags if flag in {"low_resolution", "severe_global_blur", "key_text_unreadable", "contrast_too_low", "multi_image_quality_variance"}]
        rationale = (
            "The sample is understandable for downstream cleaning."
            if joint_understanding_status == "understandable"
            else "The sample remains partially understandable but carries review risk."
            if joint_understanding_status == "partially_understandable"
            else "The sample lacks enough jointly understandable signal for confident downstream handling."
        )
        confidence = 0.9 if joint_understanding_status == "understandable" else 0.65 if joint_understanding_status == "partially_understandable" else 0.35
        return {
            "question_complete": question_complete,
            "answer_complete": answer_complete,
            "completeness_status": completeness_status,
            "image_support_status": image_support_status,
            "joint_understanding_status": joint_understanding_status,
            "reason_codes": sorted(set(reason_codes)),
            "risk_flags": sorted(set(risk_flags)),
            "rationale": rationale,
            "confidence": confidence,
            "llm_used": False,
        }

    def assess(
        self,
        dataset_name: str,
        raw_question_text: str,
        raw_answer_text: str,
        normalized_question_text: str,
        normalized_answer_text: str,
        requires_image: bool,
        text_dominant: bool,
        cleaning_path: str,
        quality_flags: List[str],
        rewrite_report: Dict[str, Any],
        open_variants: List[Dict[str, Any]],
        text_structure: Dict[str, Any],
        alignment_record: Dict[str, Any],
        solvability_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        fallback = self.fallback_assess(
            raw_question_text,
            raw_answer_text,
            requires_image,
            quality_flags,
            alignment_record,
            solvability_report,
        )
        if not self.client.config.enabled:
            return fallback
        payload = {
            "dataset_name": dataset_name,
            "raw_question_text": raw_question_text,
            "raw_answer_text": raw_answer_text,
            "normalized_question_text": normalized_question_text,
            "normalized_answer_text": normalized_answer_text,
            "requires_image": requires_image,
            "text_dominant": text_dominant,
            "cleaning_path": cleaning_path,
            "quality_flags": quality_flags,
            "rewrite_report": rewrite_report,
            "open_variants": open_variants[:2],
            "text_structure": {
                "question_type": text_structure.get("question_type"),
                "status": text_structure.get("text_structure_status"),
                "parser_confidence": text_structure.get("parser_confidence"),
            },
            "alignment_record": {
                "alignment_status": alignment_record.get("alignment_status"),
                "coverage_score": alignment_record.get("coverage_score"),
                "consistency_score": alignment_record.get("consistency_score"),
            },
            "solvability_report": {
                "decision_hint": solvability_report.get("decision_hint"),
                "solvability_score": solvability_report.get("solvability_score"),
                "failure_codes": solvability_report.get("failure_codes", []),
            },
            "fallback": fallback,
        }
        result = self.client.chat_json(self.system_prompt, json.dumps(payload, ensure_ascii=False, indent=2))
        if not isinstance(result, dict):
            return fallback
        completeness_status = to_plain_text(result.get("completeness_status")).strip() or fallback["completeness_status"]
        image_support_status = to_plain_text(result.get("image_support_status")).strip() or fallback["image_support_status"]
        joint_understanding_status = to_plain_text(result.get("joint_understanding_status")).strip() or fallback["joint_understanding_status"]
        if completeness_status not in {"complete", "partial", "broken"}:
            return fallback
        if image_support_status not in {"not_needed", "clear_enough", "uncertain_but_usable", "missing_or_unusable"}:
            return fallback
        if joint_understanding_status not in {"understandable", "partially_understandable", "not_understandable"}:
            return fallback
        reason_codes = result.get("reason_codes") if isinstance(result.get("reason_codes"), list) else fallback["reason_codes"]
        risk_flags = result.get("risk_flags") if isinstance(result.get("risk_flags"), list) else fallback["risk_flags"]
        return {
            "question_complete": bool(result.get("question_complete", fallback["question_complete"])),
            "answer_complete": bool(result.get("answer_complete", fallback["answer_complete"])),
            "completeness_status": completeness_status,
            "image_support_status": image_support_status,
            "joint_understanding_status": joint_understanding_status,
            "reason_codes": [to_plain_text(code) for code in reason_codes if to_plain_text(code)],
            "risk_flags": [to_plain_text(flag) for flag in risk_flags if to_plain_text(flag)],
            "rationale": to_plain_text(result.get("rationale")) or fallback["rationale"],
            "confidence": float(result.get("confidence", fallback["confidence"])),
            "llm_used": True,
        }


class DecisionAgent:
    def __init__(self, client: OpenAICompatibleClient):
        self.client = client
        self.system_prompt = read_prompt(GATE_DECISION_PROMPT_PATH) if GATE_DECISION_PROMPT_PATH.exists() else (
            "You are the Cleaning Decision Agent. Read the structured signals and decide one of pass/review/reject. "
            "Prefer semantic usability over hard threshold vetoes. If rewrite strategy is drop_image_index, prefer review unless the sample is clearly unrecoverable. "
            "If alignment is risky, solvability is weak, or quality is borderline, review or reject. "
            "Return strict JSON with keys: decision, reason_codes, rationale."
        )

    def review_override(
        self,
        quality_components: Dict[str, Any],
        rewrite_report: Dict[str, Any],
        alignment_record: Dict[str, Any],
        solvability_report: Dict[str, Any],
        quality_flags: List[str],
        sample_understanding: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        if not self.client.config.enabled:
            return None
        user_prompt = json.dumps(
            {
                "quality_components": quality_components,
                "rewrite_report": rewrite_report,
                "alignment_record": alignment_record,
                "solvability_report": solvability_report,
                "quality_flags": quality_flags,
                "sample_understanding": sample_understanding,
            },
            ensure_ascii=False,
            indent=2,
        )
        result = self.client.chat_json(self.system_prompt, user_prompt)
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


def build_open_variants(pipeline: Any, problem_id: str, rewrite_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    variants: List[Dict[str, Any]] = []
    rewrite_variants = rewrite_report.get("variants")
    if not isinstance(rewrite_variants, list):
        rewrite_variants = []
    for idx, variant in enumerate(rewrite_variants, start=1):
        variants.append(
            {
                "open_variant_id": f"open_{pipeline.stable_digest([problem_id, str(idx)])}",
                "parent_problem_id": problem_id,
                "variant_index": idx,
                "title": pipeline.to_plain_text(variant.get("title") or f"开放题 {idx}"),
                "rewritten_question_text": pipeline.to_plain_text(variant.get("rewritten_question_text")),
                "expected_answer_type": pipeline.to_plain_text(variant.get("expected_answer_type") or "short_text"),
                "expected_answer": pipeline.to_plain_text(variant.get("expected_answer")),
                "split_role": pipeline.to_plain_text(variant.get("split_role") or "single"),
            }
        )
    return variants


def build_clean_problem_record(pipeline: Any, problem_id: str, sample: Any, normalized_assets: Dict[str, Any], text_structure: Dict[str, Any], alignment_record: Dict[str, Any], solvability_report: Dict[str, Any], gate: Dict[str, Any], open_variants: Any, requires_image: bool, cleaning_path: str) -> Dict[str, Any]:
    return {
        "clean_problem_record_id": f"cleanprob_{pipeline.stable_digest([problem_id, pipeline.pipeline_run_id])}",
        "problem_id": problem_id,
        "source_dataset": sample.dataset_display_name,
        "source_problem_id": sample.source_problem_id,
        "normalized_question_text": normalized_assets["normalized_question_text"],
        "normalized_answer_text": normalized_assets["normalized_answer_text"],
        "image_count": len(sample.images),
        "has_multiple_images": len(sample.images) > 1,
        "requires_image": requires_image,
        "text_dominant": normalized_assets["text_dominant"],
        "cleaning_path": cleaning_path,
        "question_type": text_structure.get("question_type"),
        "open_variant_count": len(open_variants),
        "alignment_status": alignment_record.get("alignment_status"),
        "solvability_score": solvability_report.get("solvability_score"),
        "solvability_path_mode": solvability_report.get("path_mode"),
        "clean_decision": gate["decision"],
        "decision_reason_codes": gate["decision_reason_codes"],
        "created_at": pipeline.utc_now(),
    }


def create_roi_assets(pipeline: Any, problem_id: str, images: Any, image_qualities: Any, crop_dir: Path) -> List[Dict[str, Any]]:
    pipeline.ensure_dir(crop_dir)
    roi_assets: List[Dict[str, Any]] = []
    for index, image in enumerate(images, start=1):
        quality = image_qualities[index - 1]
        bbox = quality.get("roi_bbox")
        if image is None or not bbox:
            continue
        width, height = quality["width"], quality["height"]
        if bbox["width"] * bbox["height"] >= 0.98 * width * height:
            continue
        x1, y1 = bbox["x"], bbox["y"]
        x2, y2 = x1 + bbox["width"], y1 + bbox["height"]
        crop = image.convert("RGB").crop((x1, y1, x2, y2))
        suffix = "primary" if index == 1 else f"aux_{index}"
        crop_path = crop_dir / f"{problem_id}_{suffix}_roi.png"
        crop.save(crop_path, format="PNG")
        crop_bytes = crop_path.read_bytes()
        roi_assets.append(
            {
                "asset_id": f"asset_{pipeline.stable_digest([problem_id, f'region_crop_{index}'])}",
                "problem_id": problem_id,
                "asset_type": "crop",
                "asset_role": "region_crop" if index == 1 else f"aux_region_crop_{index}",
                "source_uri": None,
                "storage_uri": str(crop_path),
                "file_format": "png",
                "file_size_bytes": crop_path.stat().st_size,
                "width": crop.width,
                "height": crop.height,
                "sha256": pipeline.sha256_bytes(crop_bytes),
                "perceptual_hash": pipeline.image_analyzer.perceptual_hash(crop),
                "source_text_snapshot": None,
                "normalized_text_snapshot": None,
                "text_completeness_score": None,
                "blur_score": quality["blur_score"],
                "readability_score": quality["readability_score"],
                "noise_score": quality["noise_score"],
                "cropped_from_asset_id": f"asset_{pipeline.stable_digest([problem_id, f'primary_image_{index}'])}",
                "roi_bbox": bbox,
                "asset_quality_flags": [],
                "is_usable": True,
                "discard_reason_codes": [],
                "created_at": pipeline.utc_now(),
                "updated_at": pipeline.utc_now(),
            }
        )
    return roi_assets


def build_asset_records(pipeline: Any, spec: Any, problem_id: str, sample: Any, image_paths: Any, image_bytes_list: Any, normalized_question_text: str, normalized_answer_text: str, question_norm: Dict[str, Any], answer_norm: Dict[str, Any], text_completeness: float, image_qualities: Any, quality_flags: List[str], roi_assets: List[Dict[str, Any]], open_variants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    created_at = pipeline.utc_now()
    assets = [
        {
            "asset_id": f"asset_{pipeline.stable_digest([problem_id, 'question_text_source'])}",
            "problem_id": problem_id,
            "asset_type": "text",
            "asset_role": "question_text_source",
            "source_uri": f"source://{spec.key}/{sample.source_split}/{sample.source_problem_id}/question",
            "storage_uri": f"inline://{problem_id}/question_source",
            "file_format": "txt",
            "file_size_bytes": len(sample.raw_question_text.encode('utf-8')),
            "width": None,
            "height": None,
            "sha256": pipeline.sha256_bytes(sample.raw_question_text.encode('utf-8')),
            "perceptual_hash": None,
            "source_text_snapshot": sample.raw_question_text,
            "normalized_text_snapshot": None,
            "text_completeness_score": text_completeness,
            "blur_score": None,
            "readability_score": None,
            "noise_score": None,
            "cropped_from_asset_id": None,
            "roi_bbox": None,
            "unit_normalization_map": question_norm.get("unit_normalization_map", []),
            "variable_aliases": question_norm.get("variable_aliases", []),
            "asset_quality_flags": [],
            "is_usable": bool(sample.raw_question_text),
            "discard_reason_codes": [],
            "created_at": created_at,
            "updated_at": created_at,
        },
        {
            "asset_id": f"asset_{pipeline.stable_digest([problem_id, 'question_text_normalized'])}",
            "problem_id": problem_id,
            "asset_type": "text",
            "asset_role": "question_text_normalized",
            "source_uri": None,
            "storage_uri": f"inline://{problem_id}/question_normalized",
            "file_format": "txt",
            "file_size_bytes": len(normalized_question_text.encode('utf-8')),
            "width": None,
            "height": None,
            "sha256": pipeline.sha256_bytes(normalized_question_text.encode('utf-8')),
            "perceptual_hash": None,
            "source_text_snapshot": sample.raw_question_text,
            "normalized_text_snapshot": normalized_question_text,
            "text_completeness_score": text_completeness,
            "blur_score": None,
            "readability_score": None,
            "noise_score": None,
            "cropped_from_asset_id": None,
            "roi_bbox": None,
            "unit_normalization_map": question_norm.get("unit_normalization_map", []),
            "variable_aliases": question_norm.get("variable_aliases", []),
            "asset_quality_flags": [],
            "is_usable": bool(normalized_question_text),
            "discard_reason_codes": [],
            "created_at": created_at,
            "updated_at": created_at,
        },
        {
            "asset_id": f"asset_{pipeline.stable_digest([problem_id, 'answer_raw'])}",
            "problem_id": problem_id,
            "asset_type": "answer",
            "asset_role": "answer_raw",
            "source_uri": f"source://{spec.key}/{sample.source_split}/{sample.source_problem_id}/answer",
            "storage_uri": f"inline://{problem_id}/answer_raw",
            "file_format": "txt",
            "file_size_bytes": len(sample.raw_answer_text.encode('utf-8')),
            "width": None,
            "height": None,
            "sha256": pipeline.sha256_bytes(sample.raw_answer_text.encode('utf-8')),
            "perceptual_hash": None,
            "source_text_snapshot": sample.raw_answer_text,
            "normalized_text_snapshot": None,
            "text_completeness_score": 1.0 if sample.raw_answer_text else 0.0,
            "blur_score": None,
            "readability_score": None,
            "noise_score": None,
            "cropped_from_asset_id": None,
            "roi_bbox": None,
            "unit_normalization_map": answer_norm.get("unit_normalization_map", []),
            "variable_aliases": answer_norm.get("variable_aliases", []),
            "asset_quality_flags": [],
            "is_usable": bool(sample.raw_answer_text),
            "discard_reason_codes": [],
            "created_at": created_at,
            "updated_at": created_at,
        },
        {
            "asset_id": f"asset_{pipeline.stable_digest([problem_id, 'answer_normalized'])}",
            "problem_id": problem_id,
            "asset_type": "answer",
            "asset_role": "answer_normalized",
            "source_uri": None,
            "storage_uri": f"inline://{problem_id}/answer_normalized",
            "file_format": "txt",
            "file_size_bytes": len(normalized_answer_text.encode('utf-8')),
            "width": None,
            "height": None,
            "sha256": pipeline.sha256_bytes(normalized_answer_text.encode('utf-8')),
            "perceptual_hash": None,
            "source_text_snapshot": sample.raw_answer_text,
            "normalized_text_snapshot": normalized_answer_text,
            "text_completeness_score": 1.0 if normalized_answer_text else 0.0,
            "blur_score": None,
            "readability_score": None,
            "noise_score": None,
            "cropped_from_asset_id": None,
            "roi_bbox": None,
            "unit_normalization_map": answer_norm.get("unit_normalization_map", []),
            "variable_aliases": answer_norm.get("variable_aliases", []),
            "asset_quality_flags": [],
            "is_usable": bool(normalized_answer_text),
            "discard_reason_codes": [],
            "created_at": created_at,
            "updated_at": created_at,
        },
    ]
    for index, image_path in enumerate(image_paths, start=1):
        quality = image_qualities[index - 1]
        image_bytes = image_bytes_list[index - 1]
        role = "primary_image" if index == 1 else f"aux_image_{index}"
        assets.append(
            {
                "asset_id": f"asset_{pipeline.stable_digest([problem_id, f'primary_image_{index}'])}",
                "problem_id": problem_id,
                "asset_type": "image",
                "asset_role": role,
                "source_uri": sample.image_sources[index - 1] if index - 1 < len(sample.image_sources) else None,
                "storage_uri": str(image_path),
                "file_format": image_path.suffix.lstrip('.') or 'png',
                "file_size_bytes": len(image_bytes),
                "width": quality["width"],
                "height": quality["height"],
                "sha256": pipeline.sha256_bytes(image_bytes),
                "perceptual_hash": quality["perceptual_hash"],
                "source_text_snapshot": None,
                "normalized_text_snapshot": None,
                "text_completeness_score": None,
                "blur_score": quality["blur_score"],
                "readability_score": quality["readability_score"],
                "noise_score": quality["noise_score"],
                "cropped_from_asset_id": None,
                "roi_bbox": quality["roi_bbox"],
                "unit_normalization_map": [],
                "variable_aliases": [],
                "asset_quality_flags": quality_flags,
                "is_usable": True,
                "discard_reason_codes": [],
                "created_at": created_at,
                "updated_at": created_at,
            }
        )
    assets.extend(roi_assets)
    for variant in open_variants:
        assets.append(
            {
                "asset_id": f"asset_{pipeline.stable_digest([variant['open_variant_id'], 'open_text'])}",
                "problem_id": problem_id,
                "asset_type": "text",
                "asset_role": "question_text_open_variant",
                "source_uri": None,
                "storage_uri": f"inline://{variant['open_variant_id']}",
                "file_format": "txt",
                "file_size_bytes": len(variant['rewritten_question_text'].encode('utf-8')),
                "width": None,
                "height": None,
                "sha256": pipeline.sha256_bytes(variant['rewritten_question_text'].encode('utf-8')),
                "perceptual_hash": None,
                "source_text_snapshot": sample.raw_question_text,
                "normalized_text_snapshot": variant['rewritten_question_text'],
                "text_completeness_score": text_completeness,
                "blur_score": None,
                "readability_score": None,
                "noise_score": None,
                "cropped_from_asset_id": None,
                "roi_bbox": None,
                "unit_normalization_map": question_norm.get("unit_normalization_map", []),
                "variable_aliases": question_norm.get("variable_aliases", []),
                "asset_quality_flags": [],
                "is_usable": True,
                "discard_reason_codes": [],
                "created_at": created_at,
                "updated_at": created_at,
            }
        )
    return assets


def build_node_records(pipeline: Any, problem_id: str, normalized_question_text: str, normalized_answer_text: str, original_answer_type: str, quality_flags: List[str], text_structure: Dict[str, Any], visual_structures: Any, open_variants: List[Dict[str, Any]], gate: Dict[str, Any], solvability_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    created_at = pipeline.utc_now()
    nodes: List[Dict[str, Any]] = []
    for condition in text_structure.get("conditions", []):
        nodes.append(
            {
                "node_id": f"node_{pipeline.stable_digest([problem_id, 'condition', str(condition['segment_index'])])}",
                "problem_id": problem_id,
                "node_type": "text_fact",
                "canonical_value": condition["text"],
                "surface_forms": [condition["text"]],
                "origin_kind": "text",
                "cognitive_level": "objective",
                "source_refs": [f"asset_{pipeline.stable_digest([problem_id, 'question_text_normalized'])}"],
                "evidence_refs": [f"asset_{pipeline.stable_digest([problem_id, 'question_text_normalized'])}"],
                "upstream_node_ids": [],
                "value_type": "condition",
                "normalized_value": condition,
                "unit": ",".join(condition.get("unit_mentions", [])) or None,
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
    for slot in text_structure.get("answer_slots", []):
        nodes.append(
            {
                "node_id": f"node_{pipeline.stable_digest([problem_id, slot['slot_id'], 'target'])}",
                "problem_id": problem_id,
                "node_type": "target_slot",
                "canonical_value": slot["target_text"],
                "surface_forms": [slot["target_text"]],
                "origin_kind": "text_structure",
                "cognitive_level": "computed",
                "source_refs": [f"asset_{pipeline.stable_digest([problem_id, 'question_text_normalized'])}"],
                "evidence_refs": [f"asset_{pipeline.stable_digest([problem_id, 'question_text_normalized'])}"],
                "upstream_node_ids": [],
                "value_type": slot["slot_type"],
                "normalized_value": slot,
                "unit": None,
                "confidence": text_structure.get("parser_confidence", 0.8),
                "verifiability": "high" if slot.get("expected_answer") else "medium",
                "ambiguity_level": "low" if len(slot["target_text"]) >= 3 else "high",
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
            "node_id": f"node_{pipeline.stable_digest([problem_id, 'answer_claim'])}",
            "problem_id": problem_id,
            "node_type": "answer_claim",
            "canonical_value": normalized_answer_text,
            "surface_forms": [normalized_answer_text],
            "origin_kind": "text",
            "cognitive_level": "objective",
            "source_refs": [f"asset_{pipeline.stable_digest([problem_id, 'answer_normalized'])}"],
            "evidence_refs": [f"asset_{pipeline.stable_digest([problem_id, 'answer_normalized'])}"],
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
    for visual in visual_structures:
        for entity in visual.get("visual_entities", [])[:8]:
            nodes.append(
                {
                    "node_id": f"node_{pipeline.stable_digest([problem_id, visual['visual_structure_id'], entity['entity_id']])}",
                    "problem_id": problem_id,
                    "node_type": "perception_fact",
                    "canonical_value": f"{visual['image_asset_role']}::{entity['entity_type']}::{entity['entity_id']}",
                    "surface_forms": [entity['entity_id']],
                    "origin_kind": "vision",
                    "cognitive_level": "objective",
                    "source_refs": [visual['visual_structure_id']],
                    "evidence_refs": [visual['visual_structure_id']],
                    "upstream_node_ids": [],
                    "value_type": entity['entity_type'],
                    "normalized_value": entity,
                    "unit": None,
                    "confidence": visual.get("parser_confidence", 0.7),
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
    for variant in open_variants:
        nodes.append(
            {
                "node_id": f"node_{pipeline.stable_digest([variant['open_variant_id'], 'open_variant'])}",
                "problem_id": problem_id,
                "node_type": "text_fact",
                "canonical_value": variant["rewritten_question_text"],
                "surface_forms": [variant["rewritten_question_text"]],
                "origin_kind": "reasoning",
                "cognitive_level": "computed",
                "source_refs": [f"asset_{pipeline.stable_digest([variant['open_variant_id'], 'open_text'])}"],
                "evidence_refs": [f"asset_{pipeline.stable_digest([variant['open_variant_id'], 'open_text'])}"],
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
                "node_id": f"node_{pipeline.stable_digest([problem_id, 'quality_flag', str(idx)])}",
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
            "node_id": f"node_{pipeline.stable_digest([problem_id, 'solvability'])}",
            "problem_id": problem_id,
            "node_type": "quality_signal",
            "canonical_value": f"solvability={solvability_report['decision_hint']}",
            "surface_forms": [solvability_report["decision_hint"]],
            "origin_kind": "system_quality",
            "cognitive_level": "computed",
            "source_refs": [],
            "evidence_refs": [],
            "upstream_node_ids": [],
            "value_type": "text",
            "normalized_value": solvability_report,
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
            "node_id": f"node_{pipeline.stable_digest([problem_id, 'clean_decision'])}",
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


def build_rewrite_record(pipeline: Any, problem_id: str, sample: Any, rewrite_report: Dict[str, Any], open_variants: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "rewrite_id": f"rewrite_{pipeline.stable_digest([problem_id, pipeline.pipeline_run_id])}",
        "problem_id": problem_id,
        "source_problem_id": sample.source_problem_id,
        "strategy": rewrite_report.get("strategy"),
        "rationale": rewrite_report.get("rationale"),
        "llm_used": rewrite_report.get("llm_used"),
        "fallback_used": rewrite_report.get("fallback_used"),
        "fallback_reason": rewrite_report.get("fallback_reason"),
        "schema_valid": rewrite_report.get("schema_valid"),
        "normalization_warnings": rewrite_report.get("normalization_warnings", []),
        "discard_reason_codes": rewrite_report.get("discard_reason_codes", []),
        "variant_count": len(open_variants),
        "variants": open_variants,
        "created_at": pipeline.utc_now(),
    }


def build_cleaning_record(pipeline: Any, problem_id: str, spec: Any, asset_records: List[Dict[str, Any]], alignment_record: Dict[str, Any], quality_flags: List[str], gate: Dict[str, Any], rewrite_report: Dict[str, Any], open_variants: List[Dict[str, Any]], question_norm: Dict[str, Any], answer_norm: Dict[str, Any], image_qualities: Any, text_structure: Dict[str, Any], solvability_report: Dict[str, Any], sample_understanding: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "cleaning_id": f"clean_{pipeline.stable_digest([problem_id, pipeline.pipeline_run_id])}",
        "problem_id": problem_id,
        "cleaning_version": pipeline.config.cleaning_version,
        "pipeline_run_id": pipeline.pipeline_run_id,
        "dataset_name": spec.display_name,
        "input_asset_ids": [asset["asset_id"] for asset in asset_records],
        "normalization_actions": [
            {"action_type": "text_normalized", "trigger": "NormalizationAgent", "confidence": len(question_norm.get("sentence_segments", [])) / max(len(question_norm.get("sentence_segments", [])), 1), "human_confirmed": False},
            {"action_type": "answer_canonicalized", "trigger": "NormalizationAgent", "confidence": 0.98, "human_confirmed": False},
            {"action_type": "unit_normalized", "trigger": "NormalizationAgent", "confidence": 0.92, "human_confirmed": False, "question_unit_count": len(question_norm.get("unit_normalization_map", [])), "answer_unit_count": len(answer_norm.get("unit_normalization_map", []))},
            {"action_type": "variable_canonicalized", "trigger": "NormalizationAgent", "confidence": 0.88, "human_confirmed": False, "variable_alias_count": len(question_norm.get("variable_aliases", []))},
            {"action_type": "question_rewritten", "trigger": "QuestionRewriteAgent", "confidence": 0.85, "human_confirmed": False},
        ],
        "quality_checks": [{"check": f"image_quality_{index + 1}", "result": quality, "passed": quality.get("readability_score", 0.0) >= pipeline.config.thresholds.min_readability_score or gate["decision"] != "reject"} for index, quality in enumerate(image_qualities)] or [{"check": "image_quality", "result": None, "passed": True}],
        "alignment_summary": {
            "alignment_id": alignment_record["alignment_id"],
            "coverage_score": alignment_record["coverage_score"],
            "consistency_score": alignment_record["consistency_score"],
            "alignment_status": alignment_record["alignment_status"],
            "conflict_count": len(alignment_record.get("conflict_pairs", [])),
        },
        "text_structure_summary": {
            "text_structure_id": text_structure["text_structure_id"],
            "question_type": text_structure["question_type"],
            "condition_count": len(text_structure.get("conditions", [])),
            "target_count": len(text_structure.get("targets", [])),
            "answer_slot_count": len(text_structure.get("answer_slots", [])),
            "status": text_structure.get("text_structure_status"),
        },
        "solvability_summary": {
            "solvability_id": solvability_report["solvability_id"],
            "solvability_score": solvability_report["solvability_score"],
            "reasoning_path_exists": solvability_report["reasoning_path_exists"],
            "decision_hint": solvability_report["decision_hint"],
            "failure_codes": solvability_report.get("failure_codes", []),
        },
        "sample_understanding_summary": sample_understanding,
        "rewrite_summary": {"strategy": rewrite_report.get("strategy"), "variant_count": len(open_variants), "discard_reason_codes": rewrite_report.get("discard_reason_codes", [])},
        "missing_field_summary": {
            "missing_question_text": not bool(question_norm["normalized_text"]),
            "missing_answer_text": not bool(answer_norm["normalized_text"]),
            "missing_image_count": 0 if image_qualities else (1 if "missing_core_image" in quality_flags else 0),
        },
        "risk_flags": quality_flags,
        "clean_score": gate["clean_score"],
        "decision": gate["decision"],
        "decision_reason_codes": gate["decision_reason_codes"],
        "review_ticket_id": f"review_{problem_id}" if gate["decision"] == "review" else None,
        "operator_type": "system",
        "started_at": pipeline.utc_now(),
        "finished_at": pipeline.utc_now(),
    }


def clean_gate(pipeline: Any, raw_question_text: str, raw_answer_text: str, text_completeness: float, requires_image: bool, image_qualities: List[Dict[str, Any]], alignment_record: Dict[str, Any], potential_scores: Dict[str, Any], quality_flags: List[str], rewrite_report: Dict[str, Any], open_variants: List[Dict[str, Any]], text_structure: Dict[str, Any], solvability_report: Dict[str, Any], sample_understanding: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    th = pipeline.config.thresholds
    risk_reason_codes: List[str] = []
    reason_codes: List[str] = []
    strategy = rewrite_report.get("strategy")
    if strategy == "drop_image_index":
        risk_reason_codes.append("pure_image_index_choice")
    if not raw_answer_text:
        risk_reason_codes.append("missing_answer")
    if not raw_question_text and not requires_image:
        risk_reason_codes.append("missing_question_text")
    if requires_image and "missing_core_image" in quality_flags:
        risk_reason_codes.append("missing_core_image")
    if requires_image and "low_resolution" in quality_flags:
        risk_reason_codes.append("low_resolution")
    if requires_image and "severe_global_blur" in quality_flags:
        risk_reason_codes.append("severe_blur")
    if requires_image and "key_text_unreadable" in quality_flags:
        risk_reason_codes.append("image_unreadable")
    if alignment_record["alignment_status"] == "bad":
        risk_reason_codes.append("text_image_misaligned")
    if strategy != "drop_image_index" and not open_variants:
        risk_reason_codes.append("rewrite_failed")
    if not solvability_report.get("reasoning_path_exists") and solvability_report.get("decision_hint") == "reject":
        risk_reason_codes.extend(solvability_report.get("failure_codes", []))
    if sample_understanding and sample_understanding.get("joint_understanding_status") == "not_understandable":
        risk_reason_codes.append("sample_not_understandable")
    best_readability = max((quality.get("readability_score", 0.0) for quality in image_qualities), default=1.0 if not requires_image else 0.0)
    quality_components = {
        "text_completeness": text_completeness,
        "image_readability": best_readability if requires_image else 1.0,
        "alignment_consistency": alignment_record["consistency_score"] if requires_image else 1.0,
        "multimodal_strength": potential_scores["multimodal_strength_score"],
        "verifiability": potential_scores["verifiability_score"],
        "rewrite_quality": 0.55 if strategy == "drop_image_index" else 0.9 if open_variants else 0.2,
        "solvability": solvability_report.get("solvability_score", 0.0),
        "text_structure_quality": text_structure.get("parser_confidence", 0.0),
    }
    clean_score = round(
        pipeline.clamp(
            0.16 * quality_components["text_completeness"]
            + 0.16 * quality_components["image_readability"]
            + 0.14 * quality_components["alignment_consistency"]
            + 0.12 * quality_components["multimodal_strength"]
            + 0.12 * quality_components["verifiability"]
            + 0.12 * quality_components["rewrite_quality"]
            + 0.12 * quality_components["solvability"]
            + 0.06 * quality_components["text_structure_quality"]
        ),
        4,
    )
    reason_codes.extend(sorted(set(risk_reason_codes)))
    sample_joint_status = sample_understanding.get("joint_understanding_status") if sample_understanding else None
    sample_completeness = sample_understanding.get("completeness_status") if sample_understanding else None
    sample_image_support = sample_understanding.get("image_support_status") if sample_understanding else None
    sample_reason_codes = sample_understanding.get("reason_codes", []) if sample_understanding else []
    if sample_joint_status == "not_understandable":
        if sample_completeness == "broken" or sample_image_support == "missing_or_unusable":
            decision = "reject"
            reason_codes.append("sample_semantics_broken")
        else:
            decision = "review"
            reason_codes.append("sample_understanding_review_required")
        reason_codes.extend(sample_reason_codes)
    elif clean_score < th.reject_clean_score_below:
        if strategy == "drop_image_index" and raw_question_text:
            decision = "review"
            reason_codes.append("pure_image_choice_needs_review")
        else:
            decision = "reject"
            reason_codes.append("low_clean_score")
    elif (
        clean_score < th.review_clean_score_below
        or text_completeness < th.min_text_completeness_score
        or alignment_record["alignment_status"] == "risky"
        or "contrast_too_low" in quality_flags
        or "multi_image_quality_variance" in quality_flags
        or rewrite_report.get("strategy") == "split_open"
        or text_structure.get("text_structure_status") != "complete"
        or sample_completeness == "broken"
        or (sample_understanding and sample_understanding.get("joint_understanding_status") == "partially_understandable")
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
        if "multi_image_quality_variance" in quality_flags:
            reason_codes.append("multi_image_quality_variance")
        if rewrite_report.get("strategy") == "split_open":
            reason_codes.append("split_variant_needs_review")
        if text_structure.get("text_structure_status") != "complete":
            reason_codes.append("text_structure_partial")
        if solvability_report.get("decision_hint") != "pass":
            reason_codes.extend(solvability_report.get("failure_codes", []))
        if sample_completeness == "broken":
            reason_codes.append("sample_completeness_broken")
        if sample_understanding and sample_understanding.get("joint_understanding_status") == "partially_understandable":
            reason_codes.extend(sample_reason_codes)
    else:
        decision = "pass"
        reason_codes.append("meets_cleaning_requirements")
    llm_override = apply_decision_override(
        getattr(pipeline, "decision_agent", None),
        quality_components,
        rewrite_report,
        alignment_record,
        solvability_report,
        quality_flags,
        sample_understanding,
    )
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


def apply_decision_override(
    decision_agent: Optional[DecisionOverrideProtocol],
    quality_components: Dict[str, Any],
    rewrite_report: Dict[str, Any],
    alignment_record: Dict[str, Any],
    solvability_report: Dict[str, Any],
    quality_flags: List[str],
    sample_understanding: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    if decision_agent is None:
        return None
    return decision_agent.review_override(
        quality_components,
        rewrite_report,
        alignment_record,
        solvability_report,
        quality_flags,
        sample_understanding,
    )
def build_reject_record(pipeline: Any, problem_id: str, gate: Dict[str, Any], quality_flags: List[str], rewrite_report: Dict[str, Any], alignment_record: Dict[str, Any], solvability_report: Dict[str, Any]):
    if gate["decision"] != "reject":
        return None
    return {
        "reject_id": f"reject_{pipeline.stable_digest([problem_id, pipeline.pipeline_run_id])}",
        "problem_id": problem_id,
        "stage": "cleaning",
        "reject_level": "problem",
        "reject_reason_codes": gate["decision_reason_codes"],
        "reject_reason_detail": rewrite_report.get("rationale") or "Rejected by cleaning gate.",
        "blocking_fields": quality_flags,
        "evidence_refs": [alignment_record["alignment_id"], solvability_report["solvability_id"]],
        "recoverable": False,
        "recommended_action": "drop",
        "reviewed_by": None,
        "created_at": pipeline.utc_now(),
    }


def build_problem_main_record(pipeline: Any, problem_id: str, sample: Any, language: str, normalized_question_text: str, normalized_answer_text: str, answer_type: str, image_count: int, requires_image: bool, potential_scores: Dict[str, Any], quality_flags: List[str], gate: Dict[str, Any], rewrite_report: Dict[str, Any], open_variants: List[Dict[str, Any]], normalized_assets: Dict[str, Any], alignment_record: Dict[str, Any], solvability_report: Dict[str, Any], created_at: str) -> Dict[str, Any]:
    return {
        "problem_id": problem_id,
        "source_dataset": sample.dataset_display_name,
        "source_split": sample.source_split,
        "source_problem_id": sample.source_problem_id,
        "ingest_batch_id": pipeline.ingest_batch_id,
        "problem_type": "multimodal_reasoning",
        "domain_tags": [sample.subject],
        "language": language,
        "raw_question_text": sample.raw_question_text,
        "normalized_question_text": normalized_question_text,
        "raw_answer_text": sample.raw_answer_text,
        "normalized_answer_text": normalized_answer_text,
        "answer_type": answer_type,
        "image_count": image_count,
        "has_multiple_images": image_count > 1,
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
        "candidate_id": None,
        "text_dominant": normalized_assets["text_dominant"],
        "cleaning_path": normalized_assets["cleaning_path"],
        "alignment_status": alignment_record["alignment_status"],
        "solvability_score": solvability_report["solvability_score"],
        "solvability_decision_hint": solvability_report["decision_hint"],
        "created_at": created_at,
        "updated_at": pipeline.utc_now(),
    }


def build_field_audit_records(pipeline: Any, problem_id: str, raw_question_text: str, normalized_question_text: str, raw_answer_text: str, normalized_answer_text: str, rewrite_report: Dict[str, Any], gate: Dict[str, Any], question_norm: Dict[str, Any], answer_norm: Dict[str, Any]) -> List[Dict[str, Any]]:
    timestamp = pipeline.utc_now()
    records = [
        {
            "audit_id": f"audit_{pipeline.stable_digest([problem_id, 'normalized_question_text'])}",
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
            "audit_id": f"audit_{pipeline.stable_digest([problem_id, 'normalized_answer_text'])}",
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
            "audit_id": f"audit_{pipeline.stable_digest([problem_id, 'rewrite_strategy'])}",
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
            "audit_id": f"audit_{pipeline.stable_digest([problem_id, 'clean_decision'])}",
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
    if question_norm.get("unit_normalization_map"):
        records.append(
            {
                "audit_id": f"audit_{pipeline.stable_digest([problem_id, 'question_unit_map'])}",
                "problem_id": problem_id,
                "record_type": "normalized_assets",
                "field_name": "question_unit_normalization_map",
                "before_value": raw_question_text,
                "after_value": question_norm.get("unit_normalization_map"),
                "change_type": "unit_normalized",
                "trigger": "NormalizationAgent",
                "operator_type": "system",
                "created_at": timestamp,
            }
        )
    if answer_norm.get("unit_normalization_map"):
        records.append(
            {
                "audit_id": f"audit_{pipeline.stable_digest([problem_id, 'answer_unit_map'])}",
                "problem_id": problem_id,
                "record_type": "normalized_assets",
                "field_name": "answer_unit_normalization_map",
                "before_value": raw_answer_text,
                "after_value": answer_norm.get("unit_normalization_map"),
                "change_type": "unit_normalized",
                "trigger": "NormalizationAgent",
                "operator_type": "system",
                "created_at": timestamp,
            }
        )
    if question_norm.get("variable_aliases"):
        records.append(
            {
                "audit_id": f"audit_{pipeline.stable_digest([problem_id, 'variable_aliases'])}",
                "problem_id": problem_id,
                "record_type": "normalized_assets",
                "field_name": "variable_aliases",
                "before_value": None,
                "after_value": question_norm.get("variable_aliases"),
                "change_type": "variable_canonicalized",
                "trigger": "NormalizationAgent",
                "operator_type": "system",
                "created_at": timestamp,
            }
        )
    return records


def rewrite_sample(pipeline: Any, spec: Any, sample: Any, preprocessed: Dict[str, Any]) -> Dict[str, Any]:
    rewrite_report = pipeline.rewrite_agent.rewrite(
        spec.display_name,
        preprocessed["normalized_question_text"],
        preprocessed["normalized_answer_text"],
        preprocessed["original_answer_type"],
        preprocessed["choices"],
    )
    open_variants = build_open_variants(pipeline, preprocessed["problem_id"], rewrite_report)
    rewrite_record = build_rewrite_record(pipeline, preprocessed["problem_id"], sample, rewrite_report, open_variants)
    return {
        "rewrite_report": rewrite_report,
        "open_variants": open_variants,
        "rewrite_record": rewrite_record,
        "sample_understanding": None,
    }





def build_potential_scores(
    pipeline: Any,
    normalized_question_text: str,
    normalized_answer_text: str,
    answer_type: str,
    requires_image: bool,
    image_qualities: List[Dict[str, Any]],
    variant_count: int,
    text_structure: Dict[str, Any],
    alignment_record: Dict[str, Any],
    solvability_report: Dict[str, Any],
) -> Dict[str, Any]:
    keyword_hits = len(re.findall(r"\b(calculate|determine|find|derive|prove|which|what|if|compute|write|求|计算|判断)\b", normalized_question_text, flags=re.IGNORECASE))
    math_hits = len(re.findall(r"[=+\-*/^()]", normalized_question_text))
    best_readability = max((quality.get("readability_score", 0.0) for quality in image_qualities), default=0.0)
    multimodal_strength = 0.18 + 0.42 * int(requires_image) + 0.15 * bool(text_structure.get("requires_visual_grounding")) + 0.15 * alignment_record.get("consistency_score", 0.0) + 0.10 * pipeline.clamp(best_readability)
    multi_step = 0.18 + 0.18 * pipeline.clamp(keyword_hits / 4.0) + 0.18 * pipeline.clamp(math_hits / 20.0) + 0.18 * pipeline.clamp(len(text_structure.get("conditions", [])) / 4.0) + 0.10 * pipeline.clamp(len(text_structure.get("targets", [])) / 2.0) + 0.08 * pipeline.clamp(variant_count / 3.0)
    verifiability = 0.22 + 0.20 * solvability_report.get("score_breakdown", {}).get("answer_verifiable", 0.0) + 0.16 * solvability_report.get("score_breakdown", {}).get("target_clear", 0.0) + 0.14 * solvability_report.get("score_breakdown", {}).get("rewrite_complete", 0.0) + 0.14 * alignment_record.get("consistency_score", 0.0) + 0.14 * int(bool(normalized_answer_text))
    if answer_type == "numeric":
        verifiability += 0.08
    elif answer_type == "option":
        verifiability += 0.06
    review_priority = "high" if alignment_record.get("alignment_status") != "good" or solvability_report.get("decision_hint") != "pass" or len(image_qualities) > 1 or variant_count > 1 else "normal"
    return {
        "requires_image": requires_image,
        "multimodal_strength_score": round(pipeline.clamp(multimodal_strength), 4),
        "multi_step_score": round(pipeline.clamp(multi_step), 4),
        "verifiability_score": round(pipeline.clamp(verifiability), 4),
        "review_priority": review_priority,
    }


def finalize_cleaning_sample(pipeline: Any, spec: Any, sample: Any, crop_dir: Path, preprocessed: Dict[str, Any], extracted: Dict[str, Any], rewritten: Dict[str, Any]) -> Dict[str, Any]:
    sample_understanding = rewritten.get("sample_understanding")
    if getattr(pipeline, "sample_understanding_agent", None) is not None:
        sample_understanding = pipeline.sample_understanding_agent.assess(
            dataset_name=spec.display_name,
            raw_question_text=preprocessed["raw_question_text"],
            raw_answer_text=preprocessed["raw_answer_text"],
            normalized_question_text=preprocessed["normalized_question_text"],
            normalized_answer_text=preprocessed["normalized_answer_text"],
            requires_image=preprocessed["requires_image"],
            text_dominant=preprocessed["text_dominant"],
            cleaning_path=preprocessed["cleaning_path"],
            quality_flags=extracted["quality_flags"],
            rewrite_report=rewritten["rewrite_report"],
            open_variants=rewritten["open_variants"],
            text_structure=extracted["text_structure"],
            alignment_record=extracted["alignment_record"],
            solvability_report=extracted["solvability_report"],
        )
    potential_scores = build_potential_scores(
        pipeline,
        preprocessed["normalized_question_text"],
        preprocessed["normalized_answer_text"],
        preprocessed["original_answer_type"],
        preprocessed["requires_image"],
        preprocessed["image_qualities"],
        len(rewritten["open_variants"]),
        extracted["text_structure"],
        extracted["alignment_record"],
        extracted["solvability_report"],
    )
    gate = clean_gate(
        pipeline,
        preprocessed["raw_question_text"],
        preprocessed["raw_answer_text"],
        preprocessed["text_completeness"],
        preprocessed["requires_image"],
        preprocessed["image_qualities"],
        extracted["alignment_record"],
        potential_scores,
        extracted["quality_flags"],
        rewritten["rewrite_report"],
        rewritten["open_variants"],
        extracted["text_structure"],
        extracted["solvability_report"],
        sample_understanding,
    )
    clean_problem_record = build_clean_problem_record(
        pipeline,
        preprocessed["problem_id"],
        sample,
        preprocessed["normalized_assets"],
        extracted["text_structure"],
        extracted["alignment_record"],
        extracted["solvability_report"],
        gate,
        rewritten["open_variants"],
        preprocessed["requires_image"],
        preprocessed["cleaning_path"],
    )
    if getattr(pipeline, "logger", None):
        pipeline.logger.log(
            "DECISION",
            f"rewrite={rewritten['rewrite_report'].get('strategy')} alignment={extracted['alignment_record'].get('alignment_status')} final={gate.get('decision')} reasons={','.join(gate.get('decision_reason_codes', []))}",
            dataset=spec.key,
            problem_id=preprocessed["problem_id"],
        )
    roi_assets = create_roi_assets(pipeline, preprocessed["problem_id"], sample.images, preprocessed["image_qualities"], crop_dir)
    asset_records = build_asset_records(
        pipeline,
        spec,
        preprocessed["problem_id"],
        sample,
        preprocessed["image_paths"],
        preprocessed["image_bytes_list"],
        preprocessed["normalized_question_text"],
        preprocessed["normalized_answer_text"],
        preprocessed["question_norm"],
        preprocessed["answer_norm"],
        preprocessed["text_completeness"],
        preprocessed["image_qualities"],
        extracted["quality_flags"],
        roi_assets,
        rewritten["open_variants"],
    )
    node_records = build_node_records(
        pipeline,
        preprocessed["problem_id"],
        preprocessed["normalized_question_text"],
        preprocessed["normalized_answer_text"],
        preprocessed["original_answer_type"],
        extracted["quality_flags"],
        extracted["text_structure"],
        extracted["visual_structures"],
        rewritten["open_variants"],
        gate,
        extracted["solvability_report"],
    )
    field_audits = build_field_audit_records(
        pipeline,
        preprocessed["problem_id"],
        preprocessed["raw_question_text"],
        preprocessed["normalized_question_text"],
        preprocessed["raw_answer_text"],
        preprocessed["normalized_answer_text"],
        rewritten["rewrite_report"],
        gate,
        preprocessed["question_norm"],
        preprocessed["answer_norm"],
    )
    cleaning_record = build_cleaning_record(
        pipeline,
        preprocessed["problem_id"],
        spec,
        asset_records,
        extracted["alignment_record"],
        extracted["quality_flags"],
        gate,
        rewritten["rewrite_report"],
        rewritten["open_variants"],
        preprocessed["question_norm"],
        preprocessed["answer_norm"],
        preprocessed["image_qualities"],
        extracted["text_structure"],
        extracted["solvability_report"],
        sample_understanding,
    )
    reject_record = build_reject_record(
        pipeline,
        preprocessed["problem_id"],
        gate,
        extracted["quality_flags"],
        rewritten["rewrite_report"],
        extracted["alignment_record"],
        extracted["solvability_report"],
    )
    problem_main_record = build_problem_main_record(
        pipeline,
        preprocessed["problem_id"],
        sample,
        preprocessed["language"],
        preprocessed["normalized_question_text"],
        preprocessed["normalized_answer_text"],
        preprocessed["original_answer_type"],
        preprocessed["image_count"],
        preprocessed["requires_image"],
        potential_scores,
        extracted["quality_flags"],
        gate,
        rewritten["rewrite_report"],
        rewritten["open_variants"],
        preprocessed["normalized_assets"],
        extracted["alignment_record"],
        extracted["solvability_report"],
        preprocessed["created_at"],
    )
    problem_main_record.update(
        {
            "candidate_id": preprocessed["candidate_id"],
            "initial_image_dependency_score": preprocessed["initial_scores"]["initial_image_dependency_score"],
            "initial_multi_solution_score": preprocessed["initial_scores"]["initial_multi_solution_score"],
            "initial_verifiability_score": preprocessed["initial_scores"]["initial_verifiability_score"],
            "multi_solution_mining_policy": preprocessed["multi_solution_policy"]["mode"],
        }
    )
    clean_pool_entry = None if gate["decision"] == "reject" else {
        "clean_pool_entry_id": f"cleanpool_{pipeline.stable_digest([preprocessed['problem_id'], pipeline.pipeline_run_id])}",
        "candidate_id": preprocessed["candidate_id"],
        "problem_id": preprocessed["problem_id"],
        "dataset_name": spec.display_name,
        "pool_status": "ready_for_annotation" if gate["decision"] == "pass" else "manual_review",
        "clean_decision": gate["decision"],
        "review_required": gate["review_required"],
        "rewrite_strategy": rewritten["rewrite_report"].get("strategy"),
        "open_variant_count": len(rewritten["open_variants"]),
        "text_dominant": preprocessed["text_dominant"],
        "cleaning_path": preprocessed["cleaning_path"],
        "created_at": pipeline.utc_now(),
    }
    cleaning_record.update({"candidate_id": preprocessed["candidate_id"], "cleaning_path": preprocessed["cleaning_path"], "text_dominant": preprocessed["text_dominant"]})
    extracted["alignment_record"].update({"cleaning_path": preprocessed["cleaning_path"], "text_dominant": preprocessed["text_dominant"]})
    return {
        "candidate_problem_record": preprocessed["candidate_problem_record"],
        "raw_asset_bundle": preprocessed["raw_asset_bundle"],
        "candidate_pool_entry": preprocessed["candidate_pool_entry"],
        "clean_pool_entries": [clean_pool_entry] if clean_pool_entry else [],
        "clean_problem_record": clean_problem_record,
        "normalized_assets": preprocessed["normalized_assets"],
        "problem_main_record": problem_main_record,
        "asset_records": asset_records,
        "text_structure_records": extracted["text_structure_records"],
        "visual_structure_records": list(extracted["visual_structures"]),
        "solvability_reports": [extracted["solvability_report"]],
        "node_records": node_records,
        "cleaning_records": [cleaning_record],
        "reject_records": [reject_record] if reject_record else [],
        "alignment_records": [extracted["alignment_record"]],
        "field_audit_records": field_audits,
        "rewrite_reports": [rewritten["rewrite_record"]],
        "open_ended_problem_variants": rewritten["open_variants"],
    }
