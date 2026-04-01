from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple


def default_image_quality() -> Dict[str, Any]:
    return {
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


def connector_for(pipeline: Any, spec: Any):
    if spec.source_kind == "local_file":
        return pipeline.local_file_connector_cls(spec, pipeline.config)
    if spec.source_kind == "huggingface":
        return pipeline.huggingface_connector_cls(spec, pipeline.config)
    if spec.source_kind == "github":
        return pipeline.github_connector_cls(spec, pipeline.config)
    return pipeline.source_unavailable_connector_cls(spec, pipeline.config)


def is_multimodal_sample(sample: Any) -> bool:
    return bool(getattr(sample, "images", None))


def ingest_dataset_samples(pipeline: Any, spec: Any):
    connector = connector_for(pipeline, spec)
    source_status, samples, detail = connector.sample()
    if source_status != "available":
        return source_status, samples, detail
    kept_samples = [sample for sample in samples if is_multimodal_sample(sample)]
    dropped_count = len(samples) - len(kept_samples)
    if dropped_count and getattr(pipeline, "logger", None) is not None:
        pipeline.logger.log(
            "DATASET",
            f"drop_text_only_samples dropped={dropped_count} kept={len(kept_samples)} source_samples={len(samples)}",
            dataset=spec.key,
        )
    return source_status, kept_samples, detail


def compute_collection_priority(pipeline: Any, initial_scores: Dict[str, Any]) -> Dict[str, Any]:
    priority_score = round(
        pipeline.clamp(
            0.4 * initial_scores["initial_image_dependency_score"]
            + 0.3 * initial_scores["initial_multi_solution_score"]
            + 0.3 * initial_scores["initial_verifiability_score"]
        ),
        4,
    )
    return {
        "priority_score": priority_score,
        "priority_tier": "high" if priority_score >= 0.72 else "normal",
    }


def determine_multi_solution_policy(spec: Any) -> Dict[str, Any]:
    mode = (spec.multi_solution_mode or "auto").strip().lower()
    if mode == "auto":
        if spec.key in {"scemqa", "seephy", "multi_physics", "emma"}:
            mode = "conservative"
        elif spec.key in {"geometry3k", "cmm_math", "mathvision", "mm_math", "eee_bench", "physreason", "geosqa"}:
            mode = "aggressive"
        elif any(token in spec.subject for token in ["生物", "化学"]):
            mode = "conservative"
        elif any(token in spec.subject for token in ["数学", "电气", "物理"]):
            mode = "balanced"
        else:
            mode = "balanced"
    rationale_map = {
        "aggressive": "该数据集被视为具备较稳定的多解潜力，可进入更强的多解挖掘链路。",
        "balanced": "该数据集保留多解潜力评估，但不默认强推多解 agent。",
        "conservative": "该数据集更可能以单解题为主，不强推多解 agent，只保留基础可验证性与可标注性检查。",
    }
    return {"mode": mode, "should_push_multi_solution_agent": mode == "aggressive", "rationale": rationale_map.get(mode, rationale_map["balanced"])}


def compute_initial_collection_scores(
    pipeline: Any,
    normalized_question_text: str,
    normalized_answer_text: str,
    answer_type: str,
    requires_image: bool,
    text_dominant: bool,
    image_qualities: Any,
    choices: Dict[str, str],
    multi_solution_policy: Dict[str, Any],
) -> Dict[str, Any]:
    best_readability = max((quality.get("readability_score", 0.0) for quality in image_qualities), default=0.0)
    image_dependency = 0.9 if requires_image else 0.2 + 0.08 * int(bool(choices))
    multi_solution = 0.18
    if multi_solution_policy["mode"] == "aggressive":
        multi_solution += 0.28
    elif multi_solution_policy["mode"] == "balanced":
        multi_solution += 0.14
    if any(token in normalized_question_text.lower() for token in ["prove", "different", "all possible", "另一种", "不同", "证明"]):
        multi_solution += 0.18
    if len(choices) >= 4 and not text_dominant:
        multi_solution += 0.06
    verifiability = 0.2 + 0.42 * int(bool(normalized_answer_text))
    if answer_type in {"numeric", "option", "short_text"}:
        verifiability += 0.16
    if requires_image:
        verifiability += 0.12 * pipeline.clamp(best_readability)
    return {
        "initial_image_dependency_score": round(pipeline.clamp(image_dependency), 4),
        "initial_multi_solution_score": round(pipeline.clamp(multi_solution), 4),
        "initial_verifiability_score": round(pipeline.clamp(verifiability), 4),
    }
def run_initial_collection_scoring(
    pipeline: Any,
    spec: Any,
    normalized_question_text: str,
    normalized_answer_text: str,
    original_answer_type: str,
    requires_image: bool,
    text_dominant: bool,
    image_qualities: Any,
    choices: Dict[str, str],
) -> Dict[str, Any]:
    multi_solution_policy = determine_multi_solution_policy(spec)
    initial_scores = compute_initial_collection_scores(
        pipeline,
        normalized_question_text,
        normalized_answer_text,
        original_answer_type,
        requires_image,
        text_dominant,
        image_qualities,
        choices,
        multi_solution_policy,
    )
    return {
        "multi_solution_policy": multi_solution_policy,
        "initial_scores": initial_scores,
        "priority": compute_collection_priority(pipeline, initial_scores),
    }





def persist_images(pipeline: Any, problem_id: str, images: Any, image_dir: Path) -> Tuple[List[Path], List[bytes], List[Dict[str, Any]]]:
    pipeline.ensure_dir(image_dir)
    image_paths: List[Path] = []
    image_bytes_list: List[bytes] = []
    image_qualities: List[Dict[str, Any]] = []
    for index, image in enumerate(images, start=1):
        image_bytes = pipeline.image_analyzer.pil_to_png_bytes(image)
        suffix = "primary" if index == 1 else f"aux_{index}"
        path = image_dir / f"{problem_id}_{suffix}.png"
        with path.open("wb") as file:
            file.write(image_bytes)
        image_paths.append(path)
        image_bytes_list.append(image_bytes)
        image_qualities.append(pipeline.image_analyzer.analyze(image))
    return image_paths, image_bytes_list, image_qualities


def build_candidate_problem_record(pipeline: Any, candidate_id: str, sample: Any, initial_scores: Dict[str, Any], requires_image: bool, text_dominant: bool, cleaning_path: str, multi_solution_policy: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "source_dataset": sample.dataset_display_name,
        "source_split": sample.source_split,
        "source_problem_id": sample.source_problem_id,
        "subject": sample.subject,
        "raw_question_text": sample.raw_question_text,
        "raw_answer_text": sample.raw_answer_text,
        "has_image": bool(sample.images),
        "image_count": len(sample.images),
        "requires_image": requires_image,
        "text_dominant": text_dominant,
        "recommended_cleaning_path": cleaning_path,
        "initial_image_dependency_score": initial_scores["initial_image_dependency_score"],
        "initial_multi_solution_score": initial_scores["initial_multi_solution_score"],
        "initial_verifiability_score": initial_scores["initial_verifiability_score"],
        "multi_solution_mining_policy": multi_solution_policy["mode"],
        "should_push_multi_solution_agent": multi_solution_policy["should_push_multi_solution_agent"],
        "multi_solution_policy_rationale": multi_solution_policy["rationale"],
        "metadata": sample.metadata,
        "created_at": pipeline.utc_now(),
    }


def build_raw_asset_bundle(pipeline: Any, candidate_id: str, problem_id: str, sample: Any, image_qualities: Any, initial_scores: Dict[str, Any]) -> Dict[str, Any]:
    assets = [
        {"asset_role": "question_text_raw", "storage_uri": f"inline://{problem_id}/question_source", "is_present": bool(sample.raw_question_text)},
        {"asset_role": "answer_text_raw", "storage_uri": f"inline://{problem_id}/answer_source", "is_present": bool(sample.raw_answer_text)},
    ]
    image_total = max(len(sample.images), len(sample.image_sources), len(image_qualities))
    for index in range(image_total):
        quality = image_qualities[index] if index < len(image_qualities) else default_image_quality()
        source = sample.image_sources[index] if index < len(sample.image_sources) else f"inline://{problem_id}/image_{index + 1}"
        assets.append(
            {
                "asset_role": "image_raw" if index == 0 else f"aux_image_raw_{index + 1}",
                "storage_uri": source,
                "is_present": index < len(sample.images),
                "width": quality.get("width"),
                "height": quality.get("height"),
            }
        )
    return {
        "raw_asset_bundle_id": f"bundle_{pipeline.stable_digest([candidate_id, 'raw_assets'])}",
        "candidate_id": candidate_id,
        "source_dataset": sample.dataset_display_name,
        "source_problem_id": sample.source_problem_id,
        "assets": assets,
        "core_asset_completeness": {
            "has_question_text": bool(sample.raw_question_text),
            "has_answer_text": bool(sample.raw_answer_text),
            "image_count": len(sample.images),
            "has_multiple_images": len(sample.images) > 1,
        },
        "initial_scores": initial_scores,
        "created_at": pipeline.utc_now(),
    }


def build_candidate_pool_entry(pipeline: Any, candidate_id: str, sample: Any, initial_scores: Dict[str, Any], cleaning_path: str, multi_solution_policy: Dict[str, Any], priority: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "candidate_pool_entry_id": f"cpool_{pipeline.stable_digest([candidate_id, pipeline.pipeline_run_id])}",
        "candidate_id": candidate_id,
        "source_dataset": sample.dataset_display_name,
        "source_problem_id": sample.source_problem_id,
        "candidate_status": "ready_for_cleaning",
        "priority_score": priority["priority_score"],
        "priority_tier": priority["priority_tier"],
        "recommended_cleaning_path": cleaning_path,
        "multi_solution_mining_policy": multi_solution_policy["mode"],
        "initial_scores": initial_scores,
        "created_at": pipeline.utc_now(),
    }


def build_normalized_assets(pipeline: Any, problem_id: str, sample: Any, question_norm: Dict[str, Any], answer_norm: Dict[str, Any], image_qualities: Any, text_dominant: bool, cleaning_path: str) -> Dict[str, Any]:
    image_regions = [
        {
            "image_index": index + 1,
            "source_uri": sample.image_sources[index] if index < len(sample.image_sources) else None,
            "roi_bbox": quality.get("roi_bbox"),
            "readability_score": quality.get("readability_score"),
            "contrast_score": quality.get("contrast_score"),
        }
        for index, quality in enumerate(image_qualities)
    ]
    return {
        "normalized_assets_id": f"nassets_{pipeline.stable_digest([problem_id, pipeline.pipeline_run_id])}",
        "problem_id": problem_id,
        "normalized_question_text": question_norm["normalized_text"],
        "normalized_answer_text": answer_norm["normalized_text"],
        "question_unit_normalization_map": question_norm.get("unit_normalization_map", []),
        "answer_unit_normalization_map": answer_norm.get("unit_normalization_map", []),
        "variable_aliases": question_norm.get("variable_aliases", []),
        "sentence_segments": question_norm.get("sentence_segments", []),
        "image_regions": image_regions,
        "text_dominant": text_dominant,
        "cleaning_path": cleaning_path,
        "created_at": pipeline.utc_now(),
    }


def preprocess_sample(pipeline: Any, spec: Any, sample: Any, image_dir: Path) -> Dict[str, Any]:
    created_at = pipeline.utc_now()
    raw_question_text = sample.raw_question_text
    raw_answer_text = "" if pipeline.is_null_like_text(sample.raw_answer_text) else sample.raw_answer_text
    normalized_question_base = pipeline.text_normalizer.strip_hint(pipeline.text_normalizer.normalize_text(raw_question_text))
    normalized_answer_base = pipeline.text_normalizer.normalize_answer(raw_answer_text)
    question_norm = pipeline.normalize_structured_text(normalized_question_base)
    answer_norm = pipeline.normalize_structured_text(normalized_answer_base)
    normalized_question_text = question_norm["normalized_text"]
    normalized_answer_text = answer_norm["normalized_text"]
    language = pipeline.text_normalizer.detect_language(normalized_question_text)
    original_answer_type = pipeline.text_normalizer.infer_answer_type(normalized_answer_text)
    choices = dict(sample.choice_map)
    if not choices:
        choices = pipeline.text_normalizer.extract_choice_map(normalized_question_text)
    digest_seed = [
        spec.key,
        sample.source_split or "unknown",
        sample.source_problem_id or normalized_question_text or raw_question_text or "empty",
        "||".join(sample.image_sources) if sample.image_sources else str(len(sample.images)),
    ]
    candidate_id = f"cand_{pipeline.stable_digest(digest_seed)}"
    problem_id = f"prob_{pipeline.stable_digest(digest_seed)}"
    image_paths, image_bytes_list, image_qualities = persist_images(pipeline, problem_id=problem_id, images=sample.images, image_dir=image_dir)
    image_count = len(sample.images)
    requires_image = sample.force_requires_image or pipeline.text_normalizer.infer_requires_image(normalized_question_text, image_count)
    text_dominant = not requires_image
    cleaning_path = "text_lightweight" if text_dominant else "multimodal_full"
    text_completeness = pipeline.text_normalizer.text_completeness_score(raw_question_text, normalized_question_text)
    if not image_paths:
        image_qualities = []
    scoring = run_initial_collection_scoring(
        pipeline,
        spec,
        normalized_question_text,
        normalized_answer_text,
        original_answer_type,
        requires_image,
        text_dominant,
        image_qualities,
        choices,
    )
    multi_solution_policy = scoring["multi_solution_policy"]
    initial_scores = scoring["initial_scores"]
    candidate_problem_record = build_candidate_problem_record(pipeline, candidate_id, sample, initial_scores, requires_image, text_dominant, cleaning_path, multi_solution_policy)
    raw_asset_bundle = build_raw_asset_bundle(pipeline, candidate_id, problem_id, sample, image_qualities, initial_scores)
    candidate_pool_entry = build_candidate_pool_entry(pipeline, candidate_id, sample, initial_scores, cleaning_path, multi_solution_policy, scoring["priority"])
    normalized_assets = build_normalized_assets(pipeline, problem_id, sample, question_norm, answer_norm, image_qualities, text_dominant, cleaning_path)
    return {
        "created_at": created_at,
        "raw_question_text": raw_question_text,
        "raw_answer_text": raw_answer_text,
        "question_norm": question_norm,
        "answer_norm": answer_norm,
        "normalized_question_text": normalized_question_text,
        "normalized_answer_text": normalized_answer_text,
        "language": language,
        "original_answer_type": original_answer_type,
        "choices": choices,
        "candidate_id": candidate_id,
        "problem_id": problem_id,
        "image_paths": image_paths,
        "image_bytes_list": image_bytes_list,
        "image_qualities": image_qualities,
        "image_count": image_count,
        "requires_image": requires_image,
        "text_dominant": text_dominant,
        "cleaning_path": cleaning_path,
        "text_completeness": text_completeness,
        "multi_solution_policy": multi_solution_policy,
        "initial_scores": initial_scores,
        "candidate_problem_record": candidate_problem_record,
        "raw_asset_bundle": raw_asset_bundle,
        "candidate_pool_entry": candidate_pool_entry,
        "normalized_assets": normalized_assets,
    }


def build_alignment_record(pipeline: Any, problem_id: str, normalized_question_text: str, requires_image: bool, text_structure: Dict[str, Any], visual_structures: Any, image_qualities: Any) -> Dict[str, Any]:
    record = pipeline.alignment_engine.align(problem_id, requires_image, text_structure, visual_structures, image_qualities, normalized_question_text)
    record["alignment_id"] = f"align_{pipeline.stable_digest([problem_id, pipeline.pipeline_run_id])}"
    return record


def build_quality_flags(pipeline: Any, raw_question_text: str, raw_answer_text: str, text_completeness: float, image_qualities: Any, requires_image: bool):
    flags = []
    th = pipeline.config.thresholds
    if not raw_question_text:
        flags.append("missing_question_text")
    if not raw_answer_text:
        flags.append("missing_answer")
    if requires_image and not image_qualities:
        flags.append("missing_core_image")
    if requires_image and image_qualities:
        if all(
            quality.get("width") is not None
            and quality.get("height") is not None
            and quality["width"] < th.min_width
            and quality["height"] < th.min_height
            for quality in image_qualities
        ):
            flags.append("low_resolution")
        if all(pipeline.clamp(pipeline.math.log1p(max(quality.get("blur_score", 0.0), 0.0)) / 8.0) < th.min_sharpness_score for quality in image_qualities):
            flags.append("severe_global_blur")
        if all(quality.get("readability_score", 0.0) < th.min_readability_score for quality in image_qualities):
            flags.append("key_text_unreadable")
        if all(quality.get("contrast_score", 0.0) < th.min_contrast_score for quality in image_qualities):
            flags.append("contrast_too_low")
        if any(quality.get("crop_integrity_score", 1.0) < 0.45 for quality in image_qualities):
            flags.append("severe_crop_loss")
        if len(image_qualities) > 1 and max(quality.get("readability_score", 0.0) for quality in image_qualities) - min(quality.get("readability_score", 0.0) for quality in image_qualities) > 0.35:
            flags.append("multi_image_quality_variance")
    if text_completeness < th.min_text_completeness_score:
        flags.append("low_text_completeness")
    return sorted(set(flags))


def build_text_structure_record(pipeline: Any, problem_id: str, text_structure: Dict[str, Any], question_norm: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "text_structure_id": text_structure["text_structure_id"],
        "problem_id": problem_id,
        "question_type": text_structure["question_type"],
        "conditions": text_structure.get("conditions", []),
        "targets": text_structure.get("targets", []),
        "answer_slots": text_structure.get("answer_slots", []),
        "entity_mentions": text_structure.get("entity_mentions", []),
        "variable_aliases": text_structure.get("variable_aliases", []),
        "unit_mentions": text_structure.get("unit_mentions", []),
        "sentence_segments": question_norm.get("sentence_segments", []),
        "requires_visual_grounding": text_structure.get("requires_visual_grounding", False),
        "text_structure_status": text_structure.get("text_structure_status"),
        "parser_confidence": text_structure.get("parser_confidence", 0.0),
        "created_at": text_structure.get("created_at") or pipeline.utc_now(),
    }


def extract_sample_structure(pipeline: Any, sample: Any, preprocessed: Dict[str, Any], open_variants: Any) -> Dict[str, Any]:
    text_structure = pipeline.text_parser.parse(
        preprocessed["problem_id"],
        preprocessed["normalized_question_text"],
        open_variants,
        preprocessed["requires_image"],
        preprocessed["question_norm"],
        preprocessed["answer_norm"],
        preprocessed["choices"],
    )
    visual_structures = [] if preprocessed["text_dominant"] else pipeline.visual_parser.parse_many(
        preprocessed["problem_id"],
        sample.images,
        preprocessed["image_qualities"],
        preprocessed["normalized_question_text"],
    )
    alignment_record = build_alignment_record(
        pipeline,
        preprocessed["problem_id"],
        preprocessed["normalized_question_text"],
        preprocessed["requires_image"],
        text_structure,
        visual_structures,
        preprocessed["image_qualities"],
    )
    quality_flags = build_quality_flags(
        pipeline,
        preprocessed["raw_question_text"],
        preprocessed["raw_answer_text"],
        preprocessed["text_completeness"],
        preprocessed["image_qualities"],
        preprocessed["requires_image"],
    )
    solvability_report = pipeline.solvability_checker.evaluate(
        preprocessed["problem_id"],
        preprocessed["normalized_answer_text"],
        preprocessed["original_answer_type"],
        preprocessed["requires_image"],
        open_variants,
        text_structure,
        visual_structures,
        alignment_record,
        quality_flags,
    )
    return {
        "text_structure": text_structure,
        "visual_structures": visual_structures,
        "alignment_record": alignment_record,
        "quality_flags": quality_flags,
        "solvability_report": solvability_report,
        "text_structure_records": [build_text_structure_record(pipeline, preprocessed["problem_id"], text_structure, preprocessed["question_norm"])],
    }
