#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple


DEFAULT_OUTPUTS_ROOT = "outputs"
DEFAULT_READY_ROOT = "ready"
DEFAULT_OUTPUT_PATH = "manifests/sample_roster.json"
STATUS_PRIORITY = {"pass": 3, "review": 2, "reject": 1, "unknown": 0}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a unified sample manifest from outputs/ and ready/.")
    parser.add_argument("--outputs-root", default=DEFAULT_OUTPUTS_ROOT, help="Root outputs directory.")
    parser.add_argument("--ready-root", default=DEFAULT_READY_ROOT, help="Root ready directory.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH, help="Output manifest JSON path.")
    parser.add_argument("--dataset", default="", help="Optional dataset_key filter.")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def to_posix(path: Path) -> str:
    return path.as_posix()


def to_posix_relative(path: Path, start: Path) -> str:
    return path.relative_to(start).as_posix()


def first_dict(items: Any) -> Dict[str, Any]:
    if isinstance(items, list) and items and isinstance(items[0], dict):
        return items[0]
    return {}


def pick_first_nonempty(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            if value.strip():
                return value
            continue
        if value != "":
            return str(value)
    return ""


def pick_first_bool(*values: Any) -> Optional[bool]:
    for value in values:
        if isinstance(value, bool):
            return value
    return None


def pick_first_int(*values: Any) -> int:
    for value in values:
        if value is None or value == "":
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return 0


def sortable_time(value: str) -> str:
    return value or ""


def sample_decision(sample: Dict[str, Any]) -> str:
    clean_problem_record = sample.get("clean_problem_record") or {}
    decision = clean_problem_record.get("clean_decision")
    if decision:
        return str(decision)
    problem_main_record = sample.get("problem_main_record") or {}
    decision = problem_main_record.get("clean_decision")
    if decision:
        return str(decision)
    clean_pool_entries = sample.get("clean_pool_entries") or []
    if clean_pool_entries and isinstance(clean_pool_entries[0], dict):
        decision = clean_pool_entries[0].get("clean_decision")
        if decision:
            return str(decision)
    return "unknown"


def sample_problem_id(sample: Dict[str, Any], sample_path: Path) -> str:
    problem_main_record = sample.get("problem_main_record") or {}
    clean_problem_record = sample.get("clean_problem_record") or {}
    clean_pool_entry = first_dict(sample.get("clean_pool_entries") or [])
    return pick_first_nonempty(
        problem_main_record.get("problem_id"),
        clean_problem_record.get("problem_id"),
        clean_pool_entry.get("problem_id"),
        (sample.get("source_intake_record") or {}).get("problem_id"),
        sample_path.stem,
    )


def sample_source_problem_id(sample: Dict[str, Any]) -> str:
    return pick_first_nonempty(
        (sample.get("source_intake_record") or {}).get("source_problem_id"),
        (sample.get("problem_main_record") or {}).get("source_problem_id"),
        (sample.get("clean_problem_record") or {}).get("source_problem_id"),
        (sample.get("candidate_problem_record") or {}).get("source_problem_id"),
    )


def sample_identity_id(sample: Dict[str, Any], sample_path: Path) -> str:
    return sample_problem_id(sample, sample_path)


def sample_identity_type(sample: Dict[str, Any]) -> str:
    return "problem_id"


def sample_rewrite_strategy(sample: Dict[str, Any]) -> str:
    clean_pool_entry = first_dict(sample.get("clean_pool_entries") or [])
    rewrite_report = first_dict(sample.get("rewrite_reports") or [])
    return pick_first_nonempty(
        clean_pool_entry.get("rewrite_strategy"),
        (sample.get("problem_main_record") or {}).get("rewrite_strategy"),
        rewrite_report.get("strategy"),
        "unknown",
    )


def sample_cleaning_path(sample: Dict[str, Any]) -> str:
    clean_pool_entry = first_dict(sample.get("clean_pool_entries") or [])
    return pick_first_nonempty(
        clean_pool_entry.get("cleaning_path"),
        (sample.get("problem_main_record") or {}).get("cleaning_path"),
        (sample.get("clean_problem_record") or {}).get("cleaning_path"),
        (sample.get("normalization_record") or {}).get("cleaning_path"),
    )


def sample_requires_image(sample: Dict[str, Any]) -> Optional[bool]:
    return pick_first_bool(
        (sample.get("problem_main_record") or {}).get("requires_image"),
        (sample.get("clean_problem_record") or {}).get("requires_image"),
        (sample.get("normalization_record") or {}).get("requires_image"),
        (sample.get("candidate_problem_record") or {}).get("requires_image"),
        (sample.get("source_intake_record") or {}).get("force_requires_image"),
    )


def sample_image_count(sample: Dict[str, Any]) -> int:
    return pick_first_int(
        (sample.get("problem_main_record") or {}).get("image_count"),
        (sample.get("clean_problem_record") or {}).get("image_count"),
        (sample.get("candidate_problem_record") or {}).get("image_count"),
        len((sample.get("asset_registry_record") or {}).get("image_manifest") or []),
    )


def sample_created_at(sample: Dict[str, Any]) -> str:
    clean_pool_entry = first_dict(sample.get("clean_pool_entries") or [])
    return pick_first_nonempty(
        (sample.get("problem_main_record") or {}).get("updated_at"),
        (sample.get("problem_main_record") or {}).get("created_at"),
        (sample.get("clean_problem_record") or {}).get("created_at"),
        clean_pool_entry.get("created_at"),
        (sample.get("normalized_assets") or {}).get("created_at"),
        (sample.get("normalization_record") or {}).get("created_at"),
        (sample.get("candidate_problem_record") or {}).get("created_at"),
        (sample.get("source_intake_record") or {}).get("created_at"),
    )


def iter_output_dataset_roots(outputs_root: Path, dataset_filter: str) -> Iterator[Path]:
    seen = set()

    for summary_path in sorted(outputs_root.glob("**/datasets/*/summary.json")):
        dataset_root = summary_path.parent
        dataset_key = dataset_root.name
        if dataset_filter and dataset_key != dataset_filter:
            continue
        key = dataset_root.resolve().as_posix()
        if key in seen:
            continue
        seen.add(key)
        yield dataset_root

    for samples_dir in sorted(outputs_root.glob("**/datasets/*/samples")):
        dataset_root = samples_dir.parent
        dataset_key = dataset_root.name
        if dataset_filter and dataset_key != dataset_filter:
            continue
        key = dataset_root.resolve().as_posix()
        if key in seen:
            continue
        seen.add(key)
        yield dataset_root


def iter_ready_dataset_roots(ready_root: Path, dataset_filter: str) -> Iterator[Path]:
    for summary_path in sorted(ready_root.glob("**/datasets/*/summary.json")):
        dataset_root = summary_path.parent
        if dataset_filter and dataset_root.name != dataset_filter:
            continue
        yield dataset_root


def gather_ready_metadata(ready_root: Path, dataset_filter: str) -> Tuple[Dict[Tuple[str, str], List[str]], Dict[str, Dict[str, Any]]]:
    ready_membership: Dict[Tuple[str, str], List[str]] = defaultdict(list)
    package_index: Dict[str, Dict[str, Any]] = {}

    for dataset_root in iter_ready_dataset_roots(ready_root, dataset_filter):
        dataset_summary = read_json(dataset_root / "summary.json")
        dataset_key = dataset_root.name
        package_root = dataset_root.parent.parent
        package_rel = to_posix_relative(package_root, ready_root)
        top_summary_path = package_root / "summary.json"
        top_summary = read_json(top_summary_path) if top_summary_path.exists() else {}
        filtered_from = dataset_summary.get("filtered_from") or top_summary.get("filtered_from") or {}
        source_runs = sorted({str(item) for item in (filtered_from.get("source_runs") or []) if item})

        package_index[package_rel] = {
            "dataset_key": dataset_key,
            "package_path": f"ready/{package_rel}",
            "source_runs": source_runs,
            "started_at": pick_first_nonempty(dataset_summary.get("started_at"), top_summary.get("started_at")),
            "finished_at": pick_first_nonempty(dataset_summary.get("finished_at"), top_summary.get("finished_at")),
            "created_at": pick_first_nonempty(top_summary.get("created_at"), dataset_summary.get("created_at")),
            "processed_samples": pick_first_int(dataset_summary.get("processed_samples"), top_summary.get("processed_samples")),
        }

        samples_dir = dataset_root / "samples"
        if not samples_dir.exists():
            continue
        for sample_path in sorted(samples_dir.glob("prob_*.json")):
            sample = read_json(sample_path)
            identity_id = sample_identity_id(sample, sample_path)
            ready_membership[(dataset_key, identity_id)].append(package_rel)

    for package_list in ready_membership.values():
        package_list.sort()

    return ready_membership, package_index


def choose_canonical_record(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    def score(record: Dict[str, Any]) -> Tuple[int, int, str, str]:
        return (
            STATUS_PRIORITY.get(record.get("status", "unknown"), 0),
            1 if record.get("ready_packages") else 0,
            sortable_time(record.get("sample_created_at", "")),
            sortable_time(record.get("run_created_at", "")),
        )

    return max(records, key=score)


def build_canonical_records(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    grouped: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[(record["dataset_key"], record["identity_id"])].append(record)

    canonical_records: List[Dict[str, Any]] = []
    canonical_status_counts: Dict[str, Counter[str]] = defaultdict(Counter)
    canonical_ready_package_counts: Dict[str, Counter[str]] = defaultdict(Counter)
    canonical_run_presence_counts: Dict[str, Counter[str]] = defaultdict(Counter)

    for (dataset_key, identity_id), rows in sorted(grouped.items()):
        chosen = choose_canonical_record(rows)
        status_candidates = sorted({row["status"] for row in rows})
        source_run_dirs = sorted({row["source_run_dir"] for row in rows})
        sample_paths = sorted({row["sample_path"] for row in rows})
        ready_packages = sorted({pkg for row in rows for pkg in row.get("ready_packages", [])})
        created_candidates = [value for row in rows for value in [row.get("sample_created_at"), row.get("run_created_at")] if value]
        first_seen_at = min(created_candidates) if created_candidates else ""
        last_seen_at = max(created_candidates) if created_candidates else ""

        canonical = {
            "dataset_key": dataset_key,
            "identity_id": identity_id,
            "identity_type": chosen.get("identity_type", "problem_id"),
            "problem_id": chosen.get("problem_id", ""),
            "source_problem_id": chosen.get("source_problem_id", ""),
            "status": chosen.get("status", "unknown"),
            "status_candidates": status_candidates,
            "source_run_dirs": source_run_dirs,
            "sample_paths": sample_paths,
            "ready_packages": ready_packages,
            "run_count": len(source_run_dirs),
            "sample_file_count": len(rows),
            "first_seen_at": first_seen_at,
            "last_seen_at": last_seen_at,
            "canonical_sample_created_at": chosen.get("sample_created_at", ""),
            "canonical_run_created_at": chosen.get("run_created_at", ""),
            "cleaning_path": chosen.get("cleaning_path", ""),
            "rewrite_strategy": chosen.get("rewrite_strategy", "unknown"),
            "requires_image": chosen.get("requires_image"),
            "image_count": chosen.get("image_count", 0),
        }
        canonical_records.append(canonical)

        canonical_status_counts[dataset_key][canonical["status"]] += 1
        canonical_run_presence_counts[dataset_key][str(canonical["run_count"])] += 1
        for package in ready_packages:
            canonical_ready_package_counts[dataset_key][package] += 1

    canonical_datasets: Dict[str, Dict[str, Any]] = {}
    all_dataset_keys = sorted(set(list(canonical_status_counts.keys()) + list(canonical_run_presence_counts.keys()) + list(canonical_ready_package_counts.keys())))
    for dataset_key in all_dataset_keys:
        canonical_datasets[dataset_key] = {
            "record_count": int(sum(canonical_status_counts[dataset_key].values())),
            "status_counts": dict(sorted(canonical_status_counts[dataset_key].items())),
            "ready_package_counts": dict(sorted(canonical_ready_package_counts[dataset_key].items())),
            "run_presence_counts": dict(sorted(canonical_run_presence_counts[dataset_key].items(), key=lambda item: int(item[0]))),
        }

    return canonical_records, canonical_datasets


def build_manifest(outputs_root: Path, ready_root: Path, dataset_filter: str) -> Dict[str, Any]:
    ready_membership, ready_packages = gather_ready_metadata(ready_root, dataset_filter)
    records: List[Dict[str, Any]] = []
    dataset_status_counts: Dict[str, Counter[str]] = defaultdict(Counter)
    dataset_source_run_counts: Dict[str, Counter[str]] = defaultdict(Counter)
    dataset_ready_package_counts: Dict[str, Counter[str]] = defaultdict(Counter)
    source_run_entries: Dict[str, Dict[str, Any]] = {}

    for dataset_root in iter_output_dataset_roots(outputs_root, dataset_filter):
        dataset_key = dataset_root.name
        run_dir = dataset_root.parent.parent
        run_summary_path = run_dir / "summary.json"
        dataset_summary_path = dataset_root / "summary.json"
        dataset_summary = read_json(dataset_summary_path) if dataset_summary_path.exists() else {}
        run_summary = read_json(run_summary_path) if run_summary_path.exists() else {}
        source_run_dir = f"outputs/{to_posix_relative(run_dir, outputs_root)}"

        source_run_entries.setdefault(
            source_run_dir,
            {
                "dataset_key": dataset_key,
                "source_run_dir": source_run_dir,
                "processed_sample_count": 0,
                "status_counts": Counter(),
                "ready_package_refs": set(),
                "run_started_at": pick_first_nonempty(dataset_summary.get("started_at"), run_summary.get("started_at")),
                "run_finished_at": pick_first_nonempty(dataset_summary.get("finished_at"), run_summary.get("finished_at")),
                "run_created_at": pick_first_nonempty(run_summary.get("created_at"), dataset_summary.get("created_at")),
            },
        )

        samples_dir = dataset_root / "samples"
        if not samples_dir.exists():
            continue

        for sample_path in sorted(samples_dir.glob("prob_*.json")):
            sample = read_json(sample_path)
            problem_id = sample_problem_id(sample, sample_path)
            source_problem_id = sample_source_problem_id(sample)
            identity_id = sample_identity_id(sample, sample_path)
            identity_type = sample_identity_type(sample)
            packages = list(ready_membership.get((dataset_key, identity_id), []))
            record = {
                "dataset_key": dataset_key,
                "identity_id": identity_id,
                "identity_type": identity_type,
                "problem_id": problem_id,
                "source_problem_id": source_problem_id,
                "status": sample_decision(sample),
                "source_run_dir": source_run_dir,
                "sample_path": f"outputs/{to_posix_relative(sample_path, outputs_root)}",
                "ready_packages": [f"ready/{item}" for item in packages],
                "run_started_at": pick_first_nonempty(dataset_summary.get("started_at"), run_summary.get("started_at")),
                "run_finished_at": pick_first_nonempty(dataset_summary.get("finished_at"), run_summary.get("finished_at")),
                "run_created_at": pick_first_nonempty(run_summary.get("created_at"), dataset_summary.get("created_at")),
                "sample_created_at": sample_created_at(sample),
                "cleaning_path": sample_cleaning_path(sample),
                "rewrite_strategy": sample_rewrite_strategy(sample),
                "requires_image": sample_requires_image(sample),
                "image_count": sample_image_count(sample),
            }
            records.append(record)

            dataset_status_counts[dataset_key][record["status"]] += 1
            dataset_source_run_counts[dataset_key][source_run_dir] += 1
            source_run_entries[source_run_dir]["processed_sample_count"] += 1
            source_run_entries[source_run_dir]["status_counts"][record["status"]] += 1

            for package_rel in packages:
                package_path = f"ready/{package_rel}"
                dataset_ready_package_counts[dataset_key][package_path] += 1
                package_meta = ready_packages.get(package_rel) or {}
                package_source_runs = package_meta.get("source_runs") or []
                if not package_source_runs or source_run_dir in package_source_runs:
                    source_run_entries[source_run_dir]["ready_package_refs"].add(package_path)

    datasets: Dict[str, Dict[str, Any]] = {}
    all_dataset_keys = sorted(set(list(dataset_status_counts.keys()) + list(dataset_source_run_counts.keys()) + list(dataset_ready_package_counts.keys())))
    for dataset_key in all_dataset_keys:
        datasets[dataset_key] = {
            "record_count": int(sum(dataset_status_counts[dataset_key].values())),
            "status_counts": dict(sorted(dataset_status_counts[dataset_key].items())),
            "source_run_counts": dict(sorted(dataset_source_run_counts[dataset_key].items())),
            "ready_package_counts": dict(sorted(dataset_ready_package_counts[dataset_key].items())),
        }

    source_runs: List[Dict[str, Any]] = []
    for source_run_dir in sorted(source_run_entries.keys()):
        row = source_run_entries[source_run_dir]
        source_runs.append(
            {
                "dataset_key": row["dataset_key"],
                "source_run_dir": row["source_run_dir"],
                "processed_sample_count": row["processed_sample_count"],
                "status_counts": dict(sorted(row["status_counts"].items())),
                "ready_package_refs": sorted(row["ready_package_refs"]),
                "run_started_at": row["run_started_at"],
                "run_finished_at": row["run_finished_at"],
                "run_created_at": row["run_created_at"],
            }
        )

    canonical_records, canonical_datasets = build_canonical_records(records)

    return {
        "generated_at": utc_now(),
        "outputs_root": to_posix(outputs_root),
        "ready_root": to_posix(ready_root),
        "dataset_filter": dataset_filter or None,
        "record_count": len(records),
        "canonical_record_count": len(canonical_records),
        "ready_package_count": len(ready_packages),
        "datasets": datasets,
        "canonical_datasets": canonical_datasets,
        "source_runs": source_runs,
        "records": records,
        "canonical_records": canonical_records,
    }


def main() -> None:
    args = parse_args()
    outputs_root = Path(args.outputs_root).resolve()
    ready_root = Path(args.ready_root).resolve()
    output_path = Path(args.output).resolve()
    manifest = build_manifest(outputs_root, ready_root, args.dataset.strip())
    write_json(output_path, manifest)
    print(f"WROTE_MANIFEST={output_path}")
    print(f"RECORD_COUNT={manifest['record_count']}")
    print(f"CANONICAL_RECORD_COUNT={manifest['canonical_record_count']}")
    print(f"DATASET_COUNT={len(manifest['datasets'])}")


if __name__ == "__main__":
    main()
