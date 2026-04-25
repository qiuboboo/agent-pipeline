from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .models import LoadedReadyProblem
from .utils import normalize_whitespace, read_json, safe_float, unique_list


class ReadyDataContractError(RuntimeError):
    """Raised when a ready sample cannot satisfy the strict stage-two input contract."""


_ALLOWED_STATUSES_DEFAULT = {"ready_for_annotation"}
_ALLOWED_STATUSES_WITH_REVIEW = {"ready_for_annotation", "manual_review"}


def _iter_sample_paths(ready_root: Path) -> Iterable[Path]:
    if not ready_root.exists():
        return []
    sample_paths = sorted(path for path in ready_root.rglob("samples/*.json") if path.is_file())
    if sample_paths:
        return sample_paths
    return sorted(path for path in ready_root.rglob("*.json") if path.name.startswith("prob_"))


def _first_non_empty(*values: Any) -> Any:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value
        if value not in (None, "", [], {}):
            return value
    return None


def _allowed_statuses(include_manual_review: bool) -> set[str]:
    return set(_ALLOWED_STATUSES_WITH_REVIEW if include_manual_review else _ALLOWED_STATUSES_DEFAULT)


def _resolve_candidate_path(raw_path: str, sample_path: Path, workspace_root: Path) -> Optional[Path]:
    if not raw_path or raw_path.startswith("inline://"):
        return None
    normalized_raw_path = raw_path.replace("\\", "/")
    candidate = Path(normalized_raw_path)
    workspace_parent = workspace_root.parent
    dataset_root = sample_path.parent.parent
    ready_run_root = sample_path.parents[3] if len(sample_path.parents) > 3 else sample_path.parent
    search_roots = [
        workspace_root,
        workspace_parent,
        sample_path.parent,
        sample_path.parent.parent,
        dataset_root,
        dataset_root / "artifacts",
        dataset_root / "artifacts" / "images",
        dataset_root / "artifacts" / "crops",
        ready_run_root,
        workspace_root / "benchmarkallinone",
        workspace_parent / "benchmarkallinone",
    ]
    trial_paths: List[Path] = []
    if candidate.is_absolute():
        trial_paths.append(candidate)
    else:
        trial_paths.extend(root / candidate for root in search_roots)
        if "datasets/" in normalized_raw_path:
            suffix_after_datasets = normalized_raw_path.split("datasets/", 1)[1]
            trial_paths.append(ready_run_root / "datasets" / suffix_after_datasets)
        if "artifacts/images/" in normalized_raw_path:
            suffix = normalized_raw_path.split("artifacts/images/", 1)[1]
            filename = Path(suffix).name
            trial_paths.append(dataset_root / "artifacts" / "images" / suffix)
            trial_paths.append(dataset_root / "artifacts" / "images" / filename)
            trial_paths.append(dataset_root / "artifacts" / "images" / f"{sample_path.stem}{Path(filename).suffix}")
            trial_paths.append(ready_run_root / "datasets" / dataset_root.name / "artifacts" / "images" / suffix)
            trial_paths.append(ready_run_root / "datasets" / dataset_root.name / "artifacts" / "images" / filename)
        if "artifacts/crops/" in normalized_raw_path:
            suffix = normalized_raw_path.split("artifacts/crops/", 1)[1]
            filename = Path(suffix).name
            trial_paths.append(dataset_root / "artifacts" / "crops" / suffix)
            trial_paths.append(dataset_root / "artifacts" / "crops" / filename)
            trial_paths.append(ready_run_root / "datasets" / dataset_root.name / "artifacts" / "crops" / suffix)
            trial_paths.append(ready_run_root / "datasets" / dataset_root.name / "artifacts" / "crops" / filename)
    for trial in unique_list(trial_paths):
        if isinstance(trial, Path) and trial.exists():
            return trial.resolve()
    return None


def _collect_image_paths(sample_record: Dict[str, Any], sample_path: Path, workspace_root: Path, max_images: int) -> List[str]:
    candidates: List[str] = []

    top_level_images = sample_record.get("images")
    if isinstance(top_level_images, str):
        candidates.append(top_level_images)
    else:
        for raw in top_level_images or []:
            if isinstance(raw, str):
                candidates.append(raw)

    top_level_image_path = sample_record.get("image_path")
    if isinstance(top_level_image_path, str):
        candidates.append(top_level_image_path)

    for raw in sample_record.get("image_paths") or []:
        if isinstance(raw, str):
            candidates.append(raw)

    source_intake_record = sample_record.get("source_intake_record") or {}
    for raw in source_intake_record.get("image_paths") or []:
        if isinstance(raw, str):
            candidates.append(raw)

    asset_registry_record = sample_record.get("asset_registry_record") or {}
    for manifest in asset_registry_record.get("image_manifest") or []:
        if isinstance(manifest, dict):
            path_value = manifest.get("path")
            if isinstance(path_value, str):
                candidates.append(path_value)

    raw_asset_bundle = sample_record.get("raw_asset_bundle") or {}
    for asset in raw_asset_bundle.get("assets") or []:
        if not isinstance(asset, dict):
            continue
        if asset.get("asset_role") == "image_raw":
            storage_uri = asset.get("storage_uri")
            if isinstance(storage_uri, str):
                candidates.append(storage_uri)

    normalized_assets = sample_record.get("normalized_assets") or {}
    for region in normalized_assets.get("image_regions") or []:
        if not isinstance(region, dict):
            continue
        for key in ("source_uri", "storage_uri"):
            value = region.get(key)
            if isinstance(value, str):
                candidates.append(value)

    for asset in sample_record.get("asset_records") or []:
        if not isinstance(asset, dict):
            continue
        if asset.get("asset_type") == "image":
            for key in ("storage_uri", "source_uri"):
                value = asset.get(key)
                if isinstance(value, str):
                    candidates.append(value)

    resolved: List[str] = []
    for raw_path in unique_list(candidates):
        final_path = _resolve_candidate_path(raw_path, sample_path, workspace_root)
        if final_path is None:
            continue
        final_path_str = str(final_path)
        if final_path_str in resolved:
            continue
        resolved.append(final_path_str)
        if len(resolved) >= max_images:
            break
    return resolved


def _extract_status(clean_pool_entries: Sequence[Dict[str, Any]], include_manual_review: bool) -> Tuple[bool, str, str]:
    allowed = _allowed_statuses(include_manual_review)
    if not clean_pool_entries:
        return False, "", ""
    for entry in clean_pool_entries:
        if not isinstance(entry, dict):
            continue
        status = str(entry.get("pool_status", "") or "")
        if status in allowed:
            return True, status, str(entry.get("clean_decision", "") or "")
    primary = clean_pool_entries[0] if clean_pool_entries and isinstance(clean_pool_entries[0], dict) else {}
    return False, str(primary.get("pool_status", "") or ""), str(primary.get("clean_decision", "") or "")


def load_ready_problem(sample_path: Path, workspace_root: Path, include_manual_review: bool = False, max_images: int = 3) -> Optional[LoadedReadyProblem]:
    sample_record = read_json(sample_path)
    clean_pool_entries = sample_record.get("clean_pool_entries") or []
    allowed, clean_pool_status, clean_decision = _extract_status(clean_pool_entries, include_manual_review)
    if not allowed:
        return None

    clean_problem_record = sample_record.get("clean_problem_record") or {}
    normalized_assets = sample_record.get("normalized_assets") or {}
    candidate_problem_record = sample_record.get("candidate_problem_record") or {}
    source_intake_record = sample_record.get("source_intake_record") or {}
    raw_asset_bundle = sample_record.get("raw_asset_bundle") or {}

    problem_id = str(_first_non_empty(clean_problem_record.get("problem_id"), candidate_problem_record.get("problem_id"), source_intake_record.get("problem_id"), sample_record.get("problem_id")) or "")
    if not problem_id:
        raise ReadyDataContractError(f"[ReadyLoader] Missing `problem_id` in `{sample_path}`.")

    question_text = str(
        _first_non_empty(
            clean_problem_record.get("normalized_question_text"),
            normalized_assets.get("normalized_question_text"),
            candidate_problem_record.get("raw_question_text"),
        )
        or ""
    )
    standard_answer = str(
        _first_non_empty(
            clean_problem_record.get("normalized_answer_text"),
            normalized_assets.get("normalized_answer_text"),
            candidate_problem_record.get("raw_answer_text"),
        )
        or ""
    )
    if not question_text:
        raise ReadyDataContractError(f"[ReadyLoader] Problem `{problem_id}` is missing normalized question text.")
    if not standard_answer:
        raise ReadyDataContractError(f"[ReadyLoader] Problem `{problem_id}` is missing normalized standard answer.")

    requires_image = bool(
        _first_non_empty(
            clean_problem_record.get("requires_image"),
            candidate_problem_record.get("requires_image"),
            source_intake_record.get("force_requires_image"),
            False,
        )
    )
    image_paths = _collect_image_paths(sample_record, sample_path, workspace_root, max_images=max_images)
    if requires_image and not image_paths:
        raise ReadyDataContractError(f"[ReadyLoader] Problem `{problem_id}` requires image grounding but no image file could be resolved.")

    return LoadedReadyProblem(
        problem_id=problem_id,
        question_text=normalize_whitespace(question_text),
        standard_answer=normalize_whitespace(standard_answer),
        images=image_paths,
        initial_multi_solution_score=safe_float(candidate_problem_record.get("initial_multi_solution_score"), 0.0),
        dataset_name=str(
            _first_non_empty(
                clean_problem_record.get("source_dataset"),
                source_intake_record.get("dataset_name"),
                candidate_problem_record.get("source_dataset"),
                raw_asset_bundle.get("source_dataset"),
                sample_record.get("dataset_name"),
                sample_path.parent.parent.name,
            )
            or ""
        ),
        source_problem_id=str(
            _first_non_empty(
                clean_problem_record.get("source_problem_id"),
                candidate_problem_record.get("source_problem_id"),
                source_intake_record.get("problem_id"),
                raw_asset_bundle.get("source_problem_id"),
            )
            or ""
        ),
        subject=str(
            _first_non_empty(
                source_intake_record.get("subject"),
                source_intake_record.get("category"),
                candidate_problem_record.get("subject"),
                sample_path.parent.parent.parent.name,
            )
            or ""
        ),
        requires_image=requires_image,
        text_dominant=bool(_first_non_empty(clean_problem_record.get("text_dominant"), candidate_problem_record.get("text_dominant"), False)),
        alignment_status=str(clean_problem_record.get("alignment_status", "unknown") or "unknown"),
        solvability_score=safe_float(clean_problem_record.get("solvability_score"), 0.0),
        clean_pool_status=clean_pool_status,
        clean_decision=clean_decision,
        sample_path=str(sample_path.resolve()),
        sample_record=sample_record,
        metadata={
            "question_type": clean_problem_record.get("question_type"),
            "open_variant_count": clean_problem_record.get("open_variant_count"),
            "multi_solution_policy": candidate_problem_record.get("multi_solution_mining_policy"),
            "collection_risk_flags": candidate_problem_record.get("collection_risk_flags") or [],
        },
    )


def discover_ready_problems(ready_root: Path, workspace_root: Path, include_manual_review: bool = False, max_problems: int = 0, max_images: int = 3) -> List[LoadedReadyProblem]:
    loaded: List[LoadedReadyProblem] = []
    for sample_path in _iter_sample_paths(ready_root):
        problem = load_ready_problem(
            sample_path=sample_path,
            workspace_root=workspace_root,
            include_manual_review=include_manual_review,
            max_images=max_images,
        )
        if problem is None:
            continue
        loaded.append(problem)
        if max_problems > 0 and len(loaded) >= max_problems:
            break
    return loaded
