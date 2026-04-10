#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from review_release_policy import (
    format_reason_rule,
    get_dataset_policy,
    matches_selection,
    normalize_reason_list,
    resolve_project_path,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Export review-release candidate buckets from a canonical ready dataset using consolidated policy config.")
    p.add_argument("--policy-config", default="configs/review_release_policies.yaml", help="Path to consolidated review-release YAML config")
    p.add_argument("--dataset", required=True, help="Dataset key in review_release.datasets")
    p.add_argument("--release-bucket", required=True, help="Bucket key under dataset.release_buckets")
    p.add_argument("--out", required=True, help="Output JSON path")
    return p.parse_args()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def pick_reason_codes(sample: Dict[str, Any]) -> List[str]:
    pm = sample.get("problem_main_record") or {}
    clean_problem = sample.get("clean_problem_record") or {}
    cleaning_records = sample.get("cleaning_records") or []
    latest_cleaning = cleaning_records[-1] if cleaning_records else {}
    return (
        normalize_reason_list(pm.get("clean_decision_reason_codes"))
        or normalize_reason_list(clean_problem.get("decision_reason_codes"))
        or normalize_reason_list(latest_cleaning.get("decision_reason_codes"))
    )


def pick_original_reason_codes(sample: Dict[str, Any]) -> List[str]:
    pm = sample.get("problem_main_record") or {}
    release_reserved = pm.get("release_reserved") or {}
    manual_release = release_reserved.get("manual_release_decision") or {}
    original = normalize_reason_list(manual_release.get("original_decision_reason_codes"))
    if original:
        return original

    clean_pool_entries = sample.get("clean_pool_entries") or []
    if clean_pool_entries and isinstance(clean_pool_entries[0], dict):
        manual_override = clean_pool_entries[0].get("manual_override") or {}
        original = normalize_reason_list(manual_override.get("original_decision_reason_codes"))
        if original:
            return original

    cleaning_records = sample.get("cleaning_records") or []
    latest_cleaning = cleaning_records[-1] if cleaning_records else {}
    manual_override = latest_cleaning.get("manual_override") if isinstance(latest_cleaning, dict) else None
    original = normalize_reason_list((manual_override or {}).get("original_decision_reason_codes"))
    if original:
        return original

    return pick_reason_codes(sample)


def latest_decision(sample: Dict[str, Any]) -> str:
    cleaning = sample.get("cleaning_records") or []
    if cleaning and isinstance(cleaning, list):
        latest = cleaning[-1] or {}
        decision = latest.get("decision")
        if decision:
            return str(decision).strip().lower()
    for key in ("problem_main_record", "clean_problem_record"):
        record = sample.get(key) or {}
        for field in ("decision", "quality_decision", "clean_decision"):
            val = record.get(field)
            if val:
                return str(val).strip().lower()
    return "missing"


def pick_source_split(sample: Dict[str, Any]) -> str:
    for key in ("problem_main_record", "clean_problem_record", "source_intake_record", "candidate_problem_record"):
        record = sample.get(key) or {}
        for field in ("source_split", "split"):
            val = record.get(field)
            if val:
                return str(val)
    return ""


def pick_source_problem_id(sample: Dict[str, Any]) -> str:
    for key in ("problem_main_record", "clean_problem_record", "candidate_problem_record", "source_intake_record"):
        record = sample.get(key) or {}
        val = record.get("source_problem_id")
        if val:
            return str(val)
    return ""


def pick_quality_risk_flags(sample: Dict[str, Any]) -> List[str]:
    for key in ("problem_main_record", "clean_problem_record"):
        record = sample.get(key) or {}
        flags = record.get("quality_risk_flags")
        if isinstance(flags, list):
            return [str(x) for x in flags]
    return []


def export_bucket(dataset_root: Path, selection: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    samples_dir = dataset_root / "samples"
    for sample_path in sorted(samples_dir.glob("*.json")):
        sample = load_json(sample_path)
        current_decision = latest_decision(sample)
        reason_codes = pick_original_reason_codes(sample)
        if current_decision != "review" and not reason_codes:
            continue
        if not matches_selection(reason_codes, selection):
            continue
        pm = sample.get("problem_main_record") or {}
        rows.append(
            {
                "file": sample_path.name,
                "source_problem_id": pick_source_problem_id(sample),
                "source_split": pick_source_split(sample),
                "problem_id": pm.get("problem_id"),
                "candidate_id": pm.get("candidate_id"),
                "reason_codes": reason_codes,
                "quality_risk_flags": pick_quality_risk_flags(sample),
            }
        )
    return rows


def main() -> None:
    args = parse_args()
    policy_path = resolve_project_path(args.policy_config)
    dataset_policy = get_dataset_policy(args.dataset, policy_path)
    if not dataset_policy:
        raise ValueError(f"dataset policy not found: {args.dataset}")
    dataset_root_raw = dataset_policy.get("dataset_root")
    if not dataset_root_raw:
        raise ValueError(f"dataset_root not configured for dataset: {args.dataset}")
    dataset_root = resolve_project_path(dataset_root_raw)

    bucket_cfg = (dataset_policy.get("release_buckets") or {}).get(args.release_bucket) or {}
    if not bucket_cfg:
        raise ValueError(f"release bucket policy not found: dataset={args.dataset}, bucket={args.release_bucket}")

    selection = bucket_cfg.get("selection") or {}
    candidate_key = str(bucket_cfg.get("candidate_key") or f"{args.release_bucket}_candidates")
    adjacent_cfg = bucket_cfg.get("adjacent_observation") or {}
    adjacent_selection = adjacent_cfg.get("selection") or None
    adjacent_key = str(adjacent_cfg.get("candidate_key") or "")

    main_rows = export_bucket(dataset_root, selection)
    adjacent_rows = export_bucket(dataset_root, adjacent_selection) if adjacent_key and adjacent_selection else []

    payload: Dict[str, Any] = {
        "dataset": args.dataset,
        "canonical_ready_package": dataset_root.as_posix(),
        f"{args.release_bucket}_bucket_rule": format_reason_rule(selection),
        f"{args.release_bucket}_bucket_count": len(main_rows),
        candidate_key: main_rows,
    }
    if adjacent_key:
        payload["adjacent_bucket_rule"] = format_reason_rule(adjacent_selection)
        payload["adjacent_bucket_count"] = len(adjacent_rows)
        payload[adjacent_key] = adjacent_rows

    dump_json(resolve_project_path(args.out), payload)
    print(json.dumps({
        "dataset": args.dataset,
        "dataset_root": dataset_root.as_posix(),
        "release_bucket": args.release_bucket,
        "candidate_key": candidate_key,
        "main_candidate_count": len(main_rows),
        "adjacent_key": adjacent_key,
        "adjacent_candidate_count": len(adjacent_rows),
        "out": resolve_project_path(args.out).as_posix(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
