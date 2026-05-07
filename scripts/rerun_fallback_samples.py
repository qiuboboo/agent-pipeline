#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from benchmarkallinone.pipeline import (  # noqa: E402
    DatasetSpec,
    MultiDatasetCleaningPipeline,
    PipelineConfig,
    UnifiedSample,
    ensure_dir,
    utc_now,
    write_json,
    write_jsonl,
)


@dataclass
class SourceCandidate:
    dataset_key: str
    source_run_dir: Path
    source_dataset_root: Path
    sample_path: Path
    sample: Dict[str, Any]
    problem_id: str
    source_problem_id: str
    created_at: str
    fallback_stages: List[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rerun only fallback samples from an existing pipeline1 outputs directory. "
            "The rerun is written as a new run_* under the same outputs root so that "
            "build_ready_from_outputs_content_dedup.py can naturally prefer the rerun."
        )
    )
    parser.add_argument("--config", required=True, help="Pipeline1 YAML config used for the original run.")
    parser.add_argument("--output-dir", required=True, help="Existing outputs/<range-folder> directory.")
    parser.add_argument("--dataset", required=True, help="Dataset key under datasets/<dataset>.")
    parser.add_argument(
        "--source-run-dir",
        default="",
        help="Optional specific source run_* directory to scan. Default: latest run under output-dir.",
    )
    parser.add_argument(
        "--fallback-scope",
        choices=["final", "any"],
        default="any",
        help="Which samples count as fallback. `final` means final gate fallback only; `any` means any tracked stage fallback.",
    )
    parser.add_argument(
        "--duplicate-strategy",
        choices=["newest", "error"],
        default="newest",
        help="How to handle duplicate source_problem_id candidates before rerun.",
    )
    parser.add_argument("--limit", type=int, default=0, help="Optional max number of deduped fallback samples to rerun.")
    parser.add_argument("--dry-run", action="store_true", help="Analyze only; do not create a rerun run_* directory.")
    return parser.parse_args()


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def pick_first_nonempty(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            if value.strip():
                return value
            continue
        text = str(value)
        if text.strip():
            return text
    return ""


def build_spec_lookup(config: PipelineConfig) -> Dict[str, DatasetSpec]:
    lookup: Dict[str, DatasetSpec] = {}
    for spec in config.datasets:
        lookup[spec.key] = spec
    return lookup


def find_latest_run(output_dir: Path) -> Path:
    run_dirs = sorted(
        (path for path in output_dir.glob("run_*") if path.is_dir()),
        key=lambda item: (item.stat().st_mtime_ns, item.as_posix()),
        reverse=True,
    )
    if not run_dirs:
        raise FileNotFoundError(f"No run_* directories found under {output_dir}")
    return run_dirs[0]


def sample_problem_id(sample: Dict[str, Any], sample_path: Path) -> str:
    problem_main = sample.get("problem_main_record") or {}
    clean_problem = sample.get("clean_problem_record") or {}
    normalization = sample.get("normalization_record") or {}
    candidate = sample.get("candidate_problem_record") or {}
    source = sample.get("source_intake_record") or {}
    return pick_first_nonempty(
        problem_main.get("problem_id"),
        clean_problem.get("problem_id"),
        normalization.get("problem_id"),
        candidate.get("problem_id"),
        source.get("problem_id"),
        sample_path.stem,
    )


def sample_source_problem_id(sample: Dict[str, Any], sample_path: Path) -> str:
    problem_main = sample.get("problem_main_record") or {}
    clean_problem = sample.get("clean_problem_record") or {}
    normalization = sample.get("normalization_record") or {}
    candidate = sample.get("candidate_problem_record") or {}
    source = sample.get("source_intake_record") or {}
    value = pick_first_nonempty(
        problem_main.get("source_problem_id"),
        clean_problem.get("source_problem_id"),
        normalization.get("source_problem_id"),
        candidate.get("source_problem_id"),
        source.get("source_problem_id"),
    )
    return value or sample_problem_id(sample, sample_path)


def sample_created_at(sample: Dict[str, Any]) -> str:
    problem_main = sample.get("problem_main_record") or {}
    clean_problem = sample.get("clean_problem_record") or {}
    normalization = sample.get("normalization_record") or {}
    candidate = sample.get("candidate_problem_record") or {}
    source = sample.get("source_intake_record") or {}
    return pick_first_nonempty(
        problem_main.get("updated_at"),
        problem_main.get("created_at"),
        clean_problem.get("created_at"),
        normalization.get("created_at"),
        candidate.get("created_at"),
        source.get("created_at"),
    )


def fallback_stages(sample: Dict[str, Any]) -> List[str]:
    stages: List[str] = []
    normalization = sample.get("normalization_record") or {}
    if normalization.get("llm_used") is False:
        stages.append("normalization")
    asset_registry = sample.get("asset_registry_record") or {}
    if asset_registry.get("llm_used") is False:
        stages.append("asset_registry")
    scoring = sample.get("initial_scoring_record") or {}
    if scoring.get("llm_used") is False:
        stages.append("initial_scoring")
    registration = sample.get("candidate_registration_record") or {}
    if registration.get("llm_used") is False:
        stages.append("candidate_registration")
    rewrite_reports = sample.get("rewrite_reports") or []
    if rewrite_reports and isinstance(rewrite_reports[0], dict) and rewrite_reports[0].get("llm_used") is False:
        stages.append("rewrite")
    cleaning_records = sample.get("cleaning_records") or []
    if cleaning_records and isinstance(cleaning_records[-1], dict):
        agent_assessment = cleaning_records[-1].get("agent_assessment") or {}
        if agent_assessment.get("llm_used") is False:
            stages.append("sample_understanding")
    problem_main = sample.get("problem_main_record") or {}
    if problem_main.get("agent_decision_source") == "fallback":
        stages.append("gate_decision")
    return stages


def iter_source_candidates(source_run_dir: Path, dataset_key: str, fallback_scope: str) -> Iterable[SourceCandidate]:
    dataset_root = source_run_dir / "datasets" / dataset_key
    samples_dir = dataset_root / "samples"
    if not samples_dir.exists():
        raise FileNotFoundError(f"Samples directory not found: {samples_dir}")
    for sample_path in sorted(samples_dir.glob("prob_*.json")):
        sample = read_json(sample_path)
        stages = fallback_stages(sample)
        if fallback_scope == "final":
            keep = "gate_decision" in stages
        else:
            keep = bool(stages)
        if not keep:
            continue
        yield SourceCandidate(
            dataset_key=dataset_key,
            source_run_dir=source_run_dir,
            source_dataset_root=dataset_root,
            sample_path=sample_path,
            sample=sample,
            problem_id=sample_problem_id(sample, sample_path),
            source_problem_id=sample_source_problem_id(sample, sample_path),
            created_at=sample_created_at(sample),
            fallback_stages=stages,
        )


def candidate_sort_key(item: SourceCandidate) -> Tuple[str, int, str]:
    try:
        run_ts = item.source_run_dir.stat().st_mtime_ns
    except FileNotFoundError:
        run_ts = 0
    return (item.created_at or "", run_ts, item.sample_path.as_posix())


def dedupe_candidates(candidates: Sequence[SourceCandidate], strategy: str) -> Tuple[List[SourceCandidate], List[Dict[str, Any]]]:
    grouped: Dict[str, List[SourceCandidate]] = defaultdict(list)
    for candidate in candidates:
        dedup_key = candidate.source_problem_id or candidate.problem_id
        grouped[dedup_key].append(candidate)

    selected: List[SourceCandidate] = []
    duplicate_groups: List[Dict[str, Any]] = []
    for dedup_key, items in sorted(grouped.items(), key=lambda pair: pair[0]):
        ordered = sorted(items, key=candidate_sort_key, reverse=True)
        if len(ordered) > 1:
            duplicate_groups.append(
                {
                    "dedup_key": dedup_key,
                    "count": len(ordered),
                    "selected_sample_path": ordered[0].sample_path.as_posix(),
                    "members": [
                        {
                            "problem_id": item.problem_id,
                            "source_problem_id": item.source_problem_id,
                            "created_at": item.created_at,
                            "sample_path": item.sample_path.as_posix(),
                            "fallback_stages": list(item.fallback_stages),
                        }
                        for item in ordered
                    ],
                }
            )
            if strategy == "error":
                raise RuntimeError(
                    f"Duplicate source_problem_id detected for rerun key={dedup_key}. "
                    "Re-run with --duplicate-strategy newest to keep the latest entry."
                )
        selected.append(ordered[0])
    selected.sort(key=candidate_sort_key)
    return selected, duplicate_groups


def resolve_existing_image_paths(sample: Dict[str, Any], dataset_root: Path, problem_id: str) -> List[Path]:
    image_roles: List[Tuple[int, Path]] = []
    for asset in sample.get("asset_records") or []:
        if not isinstance(asset, dict):
            continue
        if asset.get("asset_type") != "image":
            continue
        role = str(asset.get("asset_role") or "")
        if not role.startswith("primary_image") and not role.startswith("aux_image"):
            continue
        storage_uri = str(asset.get("storage_uri") or "")
        if not storage_uri:
            continue
        candidate = Path(storage_uri)
        if not candidate.is_absolute():
            candidate = PROJECT_ROOT / candidate
            if not candidate.exists():
                candidate = dataset_root / storage_uri
        if not candidate.exists():
            continue
        order = 1
        if role.startswith("aux_image_"):
            suffix = role.split("aux_image_", 1)[1]
            try:
                order = int(suffix)
            except ValueError:
                order = 999
        image_roles.append((order, candidate))
    if image_roles:
        return [path for _, path in sorted(image_roles, key=lambda item: item[0])]

    artifact_dir = dataset_root / "artifacts" / "images"
    fallback_paths = sorted(artifact_dir.glob(f"{problem_id}_*.png"))
    return fallback_paths


def reconstruct_sample(spec: DatasetSpec, candidate: SourceCandidate) -> UnifiedSample:
    sample = candidate.sample
    source = sample.get("source_intake_record") or {}
    problem_main = sample.get("problem_main_record") or {}
    candidate_problem = sample.get("candidate_problem_record") or {}

    image_paths = resolve_existing_image_paths(sample, candidate.source_dataset_root, candidate.problem_id)
    images: List[Image.Image] = []
    for path in image_paths:
        with Image.open(path) as image:
            images.append(image.convert("RGB"))

    metadata = dict(candidate_problem.get("metadata") or {})
    metadata.update(
        {
            "image_paths": list(source.get("image_paths") or metadata.get("image_paths") or []),
            "extraction_notes": list(source.get("extraction_notes") or metadata.get("extraction_notes") or []),
            "question_field": source.get("question_field"),
            "answer_field": source.get("answer_field"),
            "image_field": source.get("image_field"),
            "choice_field": source.get("choice_field"),
            "reasoning_chain": problem_main.get("reasoning_chain") or "",
        }
    )

    return UnifiedSample(
        dataset_key=spec.key,
        dataset_display_name=spec.display_name,
        subject=spec.subject,
        source_dataset=spec.display_name,
        source_split=pick_first_nonempty(problem_main.get("source_split"), candidate_problem.get("source_split"), spec.split, "unknown"),
        source_problem_id=pick_first_nonempty(source.get("source_problem_id"), problem_main.get("source_problem_id"), candidate.problem_id),
        raw_question_text=pick_first_nonempty(source.get("raw_question_text"), problem_main.get("raw_question_text")),
        raw_answer_text=pick_first_nonempty(source.get("raw_answer_text"), problem_main.get("raw_answer_text")),
        images=images,
        image_sources=list(source.get("image_paths") or metadata.get("image_paths") or []),
        raw_record={},
        metadata=metadata,
        choice_map=dict(source.get("choice_map") or {}),
        force_requires_image=bool(source.get("force_requires_image", False)),
    )


def build_result_mapping() -> Dict[str, str]:
    return {
        "source_intake_record": "source_intake_records",
        "asset_registry_record": "asset_registry_records",
        "initial_scoring_record": "initial_scoring_records",
        "candidate_registration_record": "candidate_registration_records",
        "normalization_record": "normalization_records",
        "candidate_problem_record": "candidate_problem_records",
        "raw_asset_bundle": "raw_asset_bundles",
        "candidate_pool_entry": "candidate_pool_entries",
        "clean_pool_entries": "clean_pool_entries",
        "clean_problem_record": "clean_problem_records",
        "normalized_assets": "normalized_assets",
        "problem_main_record": "problem_main_records",
        "asset_records": "asset_records",
        "text_structure_records": "text_structure_records",
        "visual_structure_records": "visual_structure_records",
        "solvability_reports": "solvability_reports",
        "node_records": "node_records",
        "cleaning_records": "cleaning_records",
        "reject_records": "reject_records",
        "alignment_records": "alignment_records",
        "field_audit_records": "field_audit_records",
        "rewrite_reports": "rewrite_reports",
        "open_ended_problem_variants": "open_ended_problem_variants",
    }


def init_bundle() -> Dict[str, List[Any]]:
    return {value: [] for value in build_result_mapping().values()}


def consume_result(bundle: Dict[str, List[Any]], result: Dict[str, Any]) -> None:
    for result_key, bundle_key in build_result_mapping().items():
        value = result.get(result_key)
        if isinstance(value, list):
            bundle[bundle_key].extend(value)
        elif value is not None:
            bundle[bundle_key].append(value)


def write_dataset_outputs(
    dataset_dir: Path,
    bundle: Dict[str, List[Any]],
    pipeline: MultiDatasetCleaningPipeline,
    spec: DatasetSpec,
    selected_count: int,
    source_run_dir: Path,
    duplicate_groups: List[Dict[str, Any]],
    fallback_scope: str,
) -> None:
    records_dir = dataset_dir / "records"
    ensure_dir(records_dir)
    for key, rows in bundle.items():
        write_jsonl(records_dir / f"{key}.jsonl", rows)

    decision_counts = {"pass": 0, "review": 0, "reject": 0}
    rewrite_strategy_counts: Dict[str, int] = {}
    for record in bundle["problem_main_records"]:
        decision = str(record.get("clean_decision") or "unknown")
        if decision in decision_counts:
            decision_counts[decision] += 1
        strategy = str(record.get("rewrite_strategy") or "unknown")
        rewrite_strategy_counts[strategy] = rewrite_strategy_counts.get(strategy, 0) + 1

    summary = {
        "dataset_key": spec.key,
        "dataset_name": spec.display_name,
        "subject": spec.subject,
        "source_status": "rerun_fallback_only",
        "detail": f"fallback_scope={fallback_scope}",
        "requested_samples": selected_count,
        "processed_samples": len(bundle["problem_main_records"]),
        "decision_counts": decision_counts,
        "rewrite_strategy_counts": rewrite_strategy_counts,
        "records_dir": str(records_dir.relative_to(pipeline.run_dir)),
        "sample_concurrency": 1,
        "started_at": pipeline.aggregate_summary.get("created_at"),
        "finished_at": utc_now(),
        "elapsed_seconds": None,
        "llm_usage": pipeline.client.get_usage_summary(),
        "source_run_dir": source_run_dir.as_posix(),
        "duplicate_source_problem_id_groups": len(duplicate_groups),
    }
    write_json(dataset_dir / "summary.json", summary)


def write_run_summary(
    pipeline: MultiDatasetCleaningPipeline,
    spec: DatasetSpec,
    selected_count: int,
    source_run_dir: Path,
    duplicate_groups: List[Dict[str, Any]],
    fallback_scope: str,
) -> None:
    payload = {
        "pipeline_run_id": pipeline.pipeline_run_id,
        "created_at": pipeline.aggregate_summary.get("created_at"),
        "rerun_mode": "fallback_only",
        "dataset_key": spec.key,
        "dataset_name": spec.display_name,
        "source_run_dir": source_run_dir.as_posix(),
        "source_output_dir": source_run_dir.parent.as_posix(),
        "fallback_scope": fallback_scope,
        "selected_source_problem_ids": selected_count,
        "duplicate_source_problem_id_groups": len(duplicate_groups),
        "llm_usage": pipeline.client.get_usage_summary(),
    }
    write_json(pipeline.run_dir / "summary.json", payload)


def main() -> None:
    args = parse_args()
    config = PipelineConfig.from_yaml(args.config)
    spec_lookup = build_spec_lookup(config)
    if args.dataset not in spec_lookup:
        raise KeyError(f"Dataset {args.dataset!r} not found in config {args.config}")
    spec = spec_lookup[args.dataset]

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = (PROJECT_ROOT / output_dir).resolve()
    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")

    source_run_dir = Path(args.source_run_dir) if args.source_run_dir else find_latest_run(output_dir)
    if not source_run_dir.is_absolute():
        source_run_dir = (PROJECT_ROOT / source_run_dir).resolve()
    if not source_run_dir.exists():
        raise FileNotFoundError(f"Source run directory does not exist: {source_run_dir}")

    candidates = list(iter_source_candidates(source_run_dir, spec.key, args.fallback_scope))
    deduped, duplicate_groups = dedupe_candidates(candidates, args.duplicate_strategy)
    if args.limit > 0:
        deduped = deduped[: args.limit]

    manifest = {
        "config_path": str(Path(args.config).resolve()),
        "output_dir": output_dir.as_posix(),
        "source_run_dir": source_run_dir.as_posix(),
        "dataset_key": spec.key,
        "fallback_scope": args.fallback_scope,
        "duplicate_strategy": args.duplicate_strategy,
        "candidate_count_before_dedup": len(candidates),
        "selected_count_after_dedup": len(deduped),
        "duplicate_source_problem_id_groups": duplicate_groups,
        "selected_samples": [
            {
                "problem_id": item.problem_id,
                "source_problem_id": item.source_problem_id,
                "created_at": item.created_at,
                "sample_path": item.sample_path.as_posix(),
                "fallback_stages": list(item.fallback_stages),
            }
            for item in deduped
        ],
    }

    if args.dry_run:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return

    config.output_root = output_dir.as_posix()
    config.datasets = [spec]
    config.resume = False
    pipeline = MultiDatasetCleaningPipeline(config)
    pipeline.progress(
        f"[FallbackRerun] run_id={pipeline.pipeline_run_id} dataset={spec.key} "
        f"source_run={source_run_dir.name} selected={len(deduped)} duplicates={len(duplicate_groups)}"
    )

    dataset_dir = pipeline.dataset_root / spec.key
    sample_dir = dataset_dir / "samples"
    image_dir = dataset_dir / "artifacts" / "images"
    crop_dir = dataset_dir / "artifacts" / "crops"
    ensure_dir(sample_dir)
    ensure_dir(image_dir)
    ensure_dir(crop_dir)

    bundle = init_bundle()
    rerun_rows: List[Dict[str, Any]] = []
    for index, candidate in enumerate(deduped, start=1):
        unified_sample = reconstruct_sample(spec, candidate)
        result = pipeline.process_sample(spec, unified_sample, image_dir, crop_dir)
        consume_result(bundle, result)
        sample_file = sample_dir / f"{result['problem_main_record']['problem_id']}.json"
        write_json(sample_file, result)
        rerun_rows.append(
            {
                "source_problem_id": candidate.source_problem_id,
                "original_problem_id": candidate.problem_id,
                "rerun_problem_id": result["problem_main_record"]["problem_id"],
                "original_sample_path": candidate.sample_path.as_posix(),
                "rerun_sample_path": sample_file.as_posix(),
                "fallback_stages": list(candidate.fallback_stages),
            }
        )
        pipeline.progress(
            f"[FallbackRerun] sample {index}/{len(deduped)} source_problem_id={candidate.source_problem_id} "
            f"original_problem_id={candidate.problem_id} rerun_problem_id={result['problem_main_record']['problem_id']}"
        )

    write_dataset_outputs(
        dataset_dir=dataset_dir,
        bundle=bundle,
        pipeline=pipeline,
        spec=spec,
        selected_count=len(deduped),
        source_run_dir=source_run_dir,
        duplicate_groups=duplicate_groups,
        fallback_scope=args.fallback_scope,
    )
    manifest["rerun_run_dir"] = pipeline.run_dir.as_posix()
    manifest["rerun_rows"] = rerun_rows
    write_json(pipeline.run_dir / "fallback_rerun_manifest.json", manifest)
    write_run_summary(
        pipeline=pipeline,
        spec=spec,
        selected_count=len(deduped),
        source_run_dir=source_run_dir,
        duplicate_groups=duplicate_groups,
        fallback_scope=args.fallback_scope,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
