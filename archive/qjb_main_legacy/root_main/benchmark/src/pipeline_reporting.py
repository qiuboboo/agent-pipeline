from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


RESULT_MAPPING = {
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


def init_dataset_bundle() -> Dict[str, List[Dict[str, Any]]]:
    return {bundle_key: [] for bundle_key in RESULT_MAPPING.values()}


def append_sample_result(bundle: Dict[str, List[Dict[str, Any]]], result: Dict[str, Any]) -> None:
    for result_key, bundle_key in RESULT_MAPPING.items():
        value = result.get(result_key)
        if isinstance(value, list):
            bundle[bundle_key].extend(value)
        elif value is not None:
            bundle[bundle_key].append(value)


def write_sample_bundle_if_needed(config: Any, sample_dir: Path, result: Dict[str, Any], write_json: Any) -> None:
    if not config.save_sample_bundle:
        return
    sample_file = sample_dir / f"{result['problem_main_record']['problem_id']}.json"
    write_json(sample_file, result)


def build_source_unavailable_summary(spec: Any, config: Any, detail: Any) -> Dict[str, Any]:
    return {
        "dataset_key": spec.key,
        "dataset_name": spec.display_name,
        "subject": spec.subject,
        "source_status": "source_unavailable",
        "detail": detail,
        "requested_samples": config.sample_per_dataset,
        "processed_samples": 0,
        "decision_counts": {"pass": 0, "review": 0, "reject": 0},
        "rewrite_strategy_counts": {},
        "records_written": {},
        "status": "source_unavailable",
    }


def finalize_dataset_report(spec: Any, config: Any, detail: Any, dataset_dir: Path, run_dir: Path, bundle: Dict[str, List[Dict[str, Any]]], ensure_dir: Any, write_json: Any, write_jsonl: Any) -> Dict[str, Any]:
    records_dir = dataset_dir / "records"
    ensure_dir(records_dir)
    records_written: Dict[str, int] = {}
    for key, rows in bundle.items():
        write_jsonl(records_dir / f"{key}.jsonl", rows)
        records_written[key] = len(rows)
    decision_counts = {"pass": 0, "review": 0, "reject": 0}
    rewrite_strategy_counts: Dict[str, int] = {}
    for record in bundle["problem_main_records"]:
        decision = record.get("clean_decision", "reject")
        if decision not in decision_counts:
            decision_counts[decision] = 0
        decision_counts[decision] += 1
        strategy = record.get("rewrite_strategy") or "unknown"
        rewrite_strategy_counts[strategy] = rewrite_strategy_counts.get(strategy, 0) + 1
    summary = {
        "dataset_key": spec.key,
        "dataset_name": spec.display_name,
        "processed_samples": len(bundle["problem_main_records"]),
        "decision_counts": decision_counts,
        "rewrite_strategy_counts": rewrite_strategy_counts,
        "records_written": records_written,
        "status": "completed",
    }
    write_json(dataset_dir / "summary.json", summary)
    return summary


def write_run_summary(run_dir: Path, aggregate_summary: Dict[str, Any], write_json: Any) -> Dict[str, Any]:
    dataset_summaries = aggregate_summary.get("dataset_summaries", [])
    totals = {
        "processed_samples": sum(item.get("processed_samples", 0) for item in dataset_summaries),
        "pass": sum(item.get("decision_counts", {}).get("pass", 0) for item in dataset_summaries),
        "review": sum(item.get("decision_counts", {}).get("review", 0) for item in dataset_summaries),
        "reject": sum(item.get("decision_counts", {}).get("reject", 0) for item in dataset_summaries),
    }
    summary = dict(aggregate_summary)
    summary["finished_at"] = summary.get("finished_at") or summary.get("started_at")
    summary["totals"] = totals
    write_json(run_dir / "summary.json", summary)
    return summary
