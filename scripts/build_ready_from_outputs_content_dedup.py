#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_ROOT = PROJECT_ROOT / "outputs"
READY_ROOT = PROJECT_ROOT / "ready"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
RANGE_SUFFIX_RE = re.compile(r"^(?P<dataset>.+?)_(?P<start>\d+)_(?P<end>\d+)$")


@dataclass(frozen=True)
class OutputDirMatch:
    range_key: str
    dataset_key: str
    range_start: int
    range_end: int
    source_kind: str


@dataclass
class CandidateSample:
    dataset_key: str
    output_dir: Path
    run_dir: Path
    dataset_root: Path
    sample_path: Path
    sample: Dict[str, Any]
    problem_id: str
    source_problem_id: str
    created_at: str
    range_key: str
    range_start: int
    range_end: int
    source_kind: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build ready datasets from outputs only. No similarity dedup. "
            "Within each dataset range folder (dataset_aaa_bbb), traverse runs newest to oldest, "
            "keep the first sample for each source_problem_id, then merge all ranges."
        )
    )
    parser.add_argument("--dataset", action="append", default=[], help="Dataset key to include.")
    parser.add_argument("--output-glob", action="append", default=[], help="Optional output folder glob relative to outputs/.")
    parser.add_argument("--package-prefix", default="run_outputs_merged_by_source_problem_id", help="Prefix for generated ready package directories.")
    parser.add_argument("--dry-run", action="store_true", help="Analyze and print manifest only; do not write ready output.")
    return parser.parse_args()


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def pick_first_nonempty(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            if value.strip():
                return value
            continue
        return str(value)
    return ""


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


def parse_output_dir(output_dir: Path, dataset_key_from_summary: str) -> Optional[OutputDirMatch]:
    output_name = output_dir.name

    if dataset_key_from_summary == "emma_chemistry":
        if output_name == "emma_chemistry_full" or re.fullmatch(r"emma_chemistry_validation_\d+", output_name):
            return OutputDirMatch(
                range_key="emma_chemistry",
                dataset_key=dataset_key_from_summary,
                range_start=0,
                range_end=0,
                source_kind="emma_chemistry",
            )

    if dataset_key_from_summary == "eee_bench" and re.fullmatch(r"eee_bench_merged_\d+_\d+", output_name):
        return None

    if dataset_key_from_summary == "physreason":
        if re.fullmatch(r"physreason_batched_eval_rerun_\d+_\d+", output_name):
            return None
        m = re.fullmatch(r"physreason_full_(?P<start>\d+)_(?P<end>\d+)", output_name)
        if m:
            return OutputDirMatch(
                range_key=output_name,
                dataset_key=dataset_key_from_summary,
                range_start=int(m.group("start")),
                range_end=int(m.group("end")),
                source_kind="physreason_full",
            )
        m = re.fullmatch(r"physreason_full_(?P<index>\d+)", output_name)
        if m:
            index = int(m.group("index"))
            return OutputDirMatch(
                range_key=output_name,
                dataset_key=dataset_key_from_summary,
                range_start=index,
                range_end=index,
                source_kind="physreason_full",
            )
        m = re.fullmatch(r"physreason_merged_(?P<start>\d+)_(?P<end>\d+)", output_name)
        if m:
            return OutputDirMatch(
                range_key=output_name,
                dataset_key=dataset_key_from_summary,
                range_start=int(m.group("start")),
                range_end=int(m.group("end")),
                source_kind="physreason_merged",
            )

    pattern = re.compile(
        rf"(?:^|_)(?P<dataset>{re.escape(dataset_key_from_summary)})_(?P<start>\d+)_(?P<end>\d+)(?:_|$)"
    )
    m = pattern.search(output_name)
    if m:
        return OutputDirMatch(
            range_key=output_name,
            dataset_key=dataset_key_from_summary,
            range_start=int(m.group("start")),
            range_end=int(m.group("end")),
            source_kind="standard",
        )
    return None


def discover_run_dataset_roots(output_globs: List[str]) -> Iterable[Tuple[Path, Path, Path, str, str, int, int, str]]:
    if output_globs:
        output_dirs: List[Path] = []
        for pattern in output_globs:
            output_dirs.extend(sorted(OUTPUTS_ROOT.glob(pattern)))
    else:
        output_dirs = sorted(path for path in OUTPUTS_ROOT.iterdir() if path.is_dir())

    seen: set[Tuple[str, str]] = set()
    for output_dir in output_dirs:
        for dataset_root in sorted(output_dir.glob("**/datasets/*")):
            if not dataset_root.is_dir():
                continue
            run_dir = dataset_root.parent.parent
            dataset_key = dataset_root.name
            output_match = parse_output_dir(output_dir, dataset_key)
            if output_match is None:
                continue
            samples_dir = dataset_root / "samples"
            summary_path = dataset_root / "summary.json"
            if not samples_dir.exists() and not summary_path.exists():
                continue
            key = (run_dir.as_posix(), dataset_key)
            if key in seen:
                continue
            seen.add(key)
            yield (
                output_dir,
                run_dir,
                dataset_root,
                output_match.dataset_key,
                output_match.range_key,
                output_match.range_start,
                output_match.range_end,
                output_match.source_kind,
            )


def iter_candidate_samples(dataset_filter: set[str], output_globs: List[str]) -> Iterable[CandidateSample]:
    for output_dir, run_dir, dataset_root, dataset_key, range_key, range_start, range_end, source_kind in discover_run_dataset_roots(output_globs):
        if dataset_filter and dataset_key not in dataset_filter:
            continue
        samples_dir = dataset_root / "samples"
        if not samples_dir.exists():
            continue
        for sample_path in sorted(samples_dir.glob("prob_*.json")):
            try:
                sample = read_json(sample_path)
            except Exception:
                continue
            yield CandidateSample(
                dataset_key=dataset_key,
                output_dir=output_dir,
                run_dir=run_dir,
                dataset_root=dataset_root,
                sample_path=sample_path,
                sample=sample,
                problem_id=sample_problem_id(sample, sample_path),
                source_problem_id=sample_source_problem_id(sample, sample_path),
                created_at=sample_created_at(sample),
                range_key=range_key,
                range_start=range_start,
                range_end=range_end,
                source_kind=source_kind,
            )


def group_by_dataset_and_range(dataset_filter: set[str], output_globs: List[str]) -> Dict[str, Dict[str, List[CandidateSample]]]:
    grouped: Dict[str, Dict[str, List[CandidateSample]]] = {}
    for entry in iter_candidate_samples(dataset_filter, output_globs):
        grouped.setdefault(entry.dataset_key, {}).setdefault(entry.range_key, []).append(entry)
    return grouped


def run_sort_key(run_dir: Path) -> Tuple[int, str]:
    try:
        ts = run_dir.stat().st_mtime_ns
    except FileNotFoundError:
        ts = 0
    return (ts, run_dir.as_posix())


def sample_sort_key(entry: CandidateSample) -> Tuple[str, str, str]:
    return (entry.created_at or "", entry.sample_path.name, entry.sample_path.as_posix())


def build_policy_for_dataset(dataset_key: str, ranges: Dict[str, List[CandidateSample]]) -> Dict[str, Any]:
    available_output_kinds = sorted({entry.source_kind for entries in ranges.values() for entry in entries})
    policy = {
        "available_output_kinds": available_output_kinds,
        "selected_output_kind": None,
        "package_dataset_label": dataset_key,
        "dedup_rule": "latest_to_oldest_within_range_by_source_problem_id_then_merge_ranges",
        "selection_rule": "Use only outputs folders whose names contain dataset_key_start_end (prefix/suffix allowed). For each such range folder, scan runs newest to oldest; keep the first sample for each source_problem_id; after finishing each range, merge all ranges together.",
    }
    if dataset_key == "physreason":
        if "physreason_full" in available_output_kinds:
            policy.update(
                selected_output_kind="physreason_full",
                package_dataset_label="physreason_full",
                dedup_rule="physreason_full_global_newest_to_oldest_by_source_problem_id",
                selection_rule="Use only physreason_full_* output roots, including singleton suffix variants like physreason_full_1. Traverse all runs newest to oldest globally across all matched roots; keep the first sample for each source_problem_id across the full PhysReason selection.",
            )
        elif "physreason_merged" in available_output_kinds:
            policy.update(
                selected_output_kind="physreason_merged",
                package_dataset_label="physreason_merged",
                selection_rule="Use only documented adopted physreason_merged_* outputs. Do not mix them with physreason_batched_eval_rerun_* provenance roots.",
            )
    return policy


def filter_ranges_by_policy(ranges: Dict[str, List[CandidateSample]], selected_output_kind: Optional[str]) -> Dict[str, List[CandidateSample]]:
    if not selected_output_kind:
        return ranges
    filtered: Dict[str, List[CandidateSample]] = {}
    for range_key, entries in ranges.items():
        kept_entries = [entry for entry in entries if entry.source_kind == selected_output_kind]
        if kept_entries:
            filtered[range_key] = kept_entries
    return filtered


def build_selected_samples(dataset_filter: set[str], output_globs: List[str]) -> Tuple[Dict[str, List[CandidateSample]], Dict[str, Dict[str, Any]]]:
    grouped = group_by_dataset_and_range(dataset_filter, output_globs)
    selected: Dict[str, List[CandidateSample]] = {}
    stats: Dict[str, Dict[str, Any]] = {}

    for dataset_key, original_ranges in grouped.items():
        policy = build_policy_for_dataset(dataset_key, original_ranges)
        ranges = filter_ranges_by_policy(original_ranges, policy["selected_output_kind"])
        if not ranges:
            continue

        accepted_all: List[CandidateSample] = []
        dataset_scanned = 0
        dataset_skipped = 0
        range_summaries: List[Dict[str, Any]] = []

        def range_order(item: Tuple[str, List[CandidateSample]]) -> Tuple[int, int, str]:
            range_key, entries = item
            probe = entries[0]
            return (probe.range_start, probe.range_end, range_key)

        if policy["dedup_rule"] == "physreason_full_global_newest_to_oldest_by_source_problem_id":
            seen_source_problem_ids: set[str] = set()
            range_summary_map: Dict[str, Dict[str, Any]] = {}
            by_run: Dict[str, List[CandidateSample]] = {}
            run_lookup: Dict[str, Path] = {}

            for range_key, range_entries in ranges.items():
                probe = range_entries[0]
                range_runs: Dict[str, Path] = {}
                for entry in range_entries:
                    run_key = entry.run_dir.as_posix()
                    by_run.setdefault(run_key, []).append(entry)
                    run_lookup[run_key] = entry.run_dir
                    range_runs[run_key] = entry.run_dir
                range_summary_map[range_key] = {
                    "range_key": range_key,
                    "range_start": probe.range_start,
                    "range_end": probe.range_end,
                    "scanned_files": 0,
                    "kept_unique_source_problem_ids": 0,
                    "skipped_existing_source_problem_id": 0,
                    "runs_newest_to_oldest": sorted(range_runs.keys(), key=lambda k: run_sort_key(range_runs[k]), reverse=True),
                }

            run_keys = sorted(by_run.keys(), key=lambda k: run_sort_key(run_lookup[k]), reverse=True)
            for run_key in run_keys:
                for entry in sorted(by_run[run_key], key=sample_sort_key, reverse=True):
                    range_summary = range_summary_map[entry.range_key]
                    range_summary["scanned_files"] += 1
                    dataset_scanned += 1
                    if entry.source_problem_id in seen_source_problem_ids:
                        range_summary["skipped_existing_source_problem_id"] += 1
                        dataset_skipped += 1
                        continue
                    seen_source_problem_ids.add(entry.source_problem_id)
                    range_summary["kept_unique_source_problem_ids"] += 1
                    accepted_all.append(entry)

            for range_key, _range_entries in sorted(ranges.items(), key=range_order):
                range_summaries.append(range_summary_map[range_key])
        else:
            for range_key, range_entries in sorted(ranges.items(), key=range_order):
                seen_source_problem_ids: set[str] = set()
                by_run: Dict[str, List[CandidateSample]] = {}
                run_lookup: Dict[str, Path] = {}
                for entry in range_entries:
                    run_key = entry.run_dir.as_posix()
                    by_run.setdefault(run_key, []).append(entry)
                    run_lookup[run_key] = entry.run_dir

                run_keys = sorted(by_run.keys(), key=lambda k: run_sort_key(run_lookup[k]), reverse=True)
                range_scanned = 0
                range_kept = 0
                range_skipped = 0
                kept_run_order: List[str] = []

                for run_key in run_keys:
                    kept_run_order.append(run_key)
                    for entry in sorted(by_run[run_key], key=sample_sort_key, reverse=True):
                        range_scanned += 1
                        dataset_scanned += 1
                        if entry.source_problem_id in seen_source_problem_ids:
                            range_skipped += 1
                            dataset_skipped += 1
                            continue
                        seen_source_problem_ids.add(entry.source_problem_id)
                        accepted_all.append(entry)
                        range_kept += 1

                probe = range_entries[0]
                range_summaries.append(
                    {
                        "range_key": range_key,
                        "range_start": probe.range_start,
                        "range_end": probe.range_end,
                        "scanned_files": range_scanned,
                        "kept_unique_source_problem_ids": range_kept,
                        "skipped_existing_source_problem_id": range_skipped,
                        "runs_newest_to_oldest": kept_run_order,
                    }
                )

        accepted_all.sort(key=lambda e: (e.range_start, e.range_end, e.run_dir.as_posix(), e.sample_path.as_posix()))
        selected[dataset_key] = accepted_all
        stats[dataset_key] = {
            "dataset_key": dataset_key,
            "scanned_files": dataset_scanned,
            "duplicate_source_problem_id": dataset_skipped,
            "unique_files": len(accepted_all),
            "ranges": range_summaries,
            "dedup_rule": policy["dedup_rule"],
            "selection_rule": policy["selection_rule"],
            "available_output_kinds": policy["available_output_kinds"],
            "selected_output_kind": policy["selected_output_kind"],
            "selected_output_kinds": sorted({entry.source_kind for entry in accepted_all}),
            "package_dataset_label": policy["package_dataset_label"],
        }

    return selected, stats


def validate_selection(entries: List[CandidateSample], dataset_stats: Dict[str, Any]) -> Dict[str, Any]:
    range_scanned_sum = sum(item.get("scanned_files", 0) for item in dataset_stats["ranges"])
    range_kept_sum = sum(item.get("kept_unique_source_problem_ids", 0) for item in dataset_stats["ranges"])
    range_skipped_sum = sum(item.get("skipped_existing_source_problem_id", 0) for item in dataset_stats["ranges"])

    per_range_seen: Dict[str, set[str]] = {}
    per_range_duplicates: Dict[str, int] = {}
    cross_range_source_problem_id_occurrences: Dict[str, set[str]] = {}
    for entry in entries:
        per_range_seen.setdefault(entry.range_key, set())
        if entry.source_problem_id in per_range_seen[entry.range_key]:
            per_range_duplicates[entry.range_key] = per_range_duplicates.get(entry.range_key, 0) + 1
        per_range_seen[entry.range_key].add(entry.source_problem_id)
        cross_range_source_problem_id_occurrences.setdefault(entry.source_problem_id, set()).add(entry.range_key)

    cross_range_reused_source_problem_ids = sum(
        1 for ranges in cross_range_source_problem_id_occurrences.values() if len(ranges) > 1
    )

    checks = {
        "selected_matches_unique_files": len(entries) == dataset_stats["unique_files"],
        "scanned_equals_unique_plus_duplicates": dataset_stats["scanned_files"] == dataset_stats["unique_files"] + dataset_stats["duplicate_source_problem_id"],
        "range_scanned_sum_matches_dataset": range_scanned_sum == dataset_stats["scanned_files"],
        "range_kept_sum_matches_unique_files": range_kept_sum == dataset_stats["unique_files"],
        "range_skipped_sum_matches_duplicates": range_skipped_sum == dataset_stats["duplicate_source_problem_id"],
        "no_duplicate_source_problem_id_within_same_range": not per_range_duplicates,
    }

    return {
        "ok": all(checks.values()),
        "checks": checks,
        "cross_range_reused_source_problem_ids": cross_range_reused_source_problem_ids,
        "per_range_duplicate_source_problem_id_after_selection": per_range_duplicates,
    }


def validate_written_dataset(package_root: Path, dataset_key: str, summary: Dict[str, Any]) -> Dict[str, Any]:
    dataset_out = package_root / "datasets" / dataset_key
    samples_out = dataset_out / "samples"
    written_sample_files = sorted(samples_out.glob("*.json"))
    counts = summary.get("status_counts") or {}
    status_total = sum(int(counts.get(k, 0)) for k in ["pass", "review", "reject", "other", "missing"])
    checks = {
        "written_sample_file_count_matches_selected": len(written_sample_files) == summary["selected_samples"],
        "processed_matches_selected": summary["processed_samples"] == summary["selected_samples"],
        "status_sum_matches_selected": status_total == summary["selected_samples"],
        "scanned_equals_unique_plus_duplicates": summary["scanned_files"] == summary["unique_files"] + summary["duplicate_source_problem_id"],
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "written_sample_file_count": len(written_sample_files),
        "status_total": status_total,
    }


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_tree_if_exists(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def collect_related_assets(dataset_root: Path, problem_id: str) -> List[Path]:
    paths: List[Path] = []
    for artifact_dir in [dataset_root / "artifacts" / "images", dataset_root / "artifacts" / "crops", dataset_root / "assets", dataset_root / "images"]:
        if not artifact_dir.exists():
            continue
        for path in sorted(artifact_dir.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            if problem_id in path.name:
                paths.append(path)
    return paths


def status_counts(entries: List[CandidateSample]) -> Dict[str, int]:
    counts = {"pass": 0, "review": 0, "reject": 0, "other": 0, "missing": 0}
    for entry in entries:
        sample = entry.sample
        cleaning = sample.get("cleaning_records") or []
        decision = None
        if cleaning and isinstance(cleaning, list):
            latest = cleaning[-1] or {}
            decision = latest.get("decision")
        if not decision:
            pm = sample.get("problem_main_record") or {}
            decision = pm.get("decision") or pm.get("quality_decision") or pm.get("clean_decision")
        if not decision:
            clean_problem = sample.get("clean_problem_record") or {}
            decision = clean_problem.get("decision") or clean_problem.get("quality_decision") or clean_problem.get("clean_decision")
        if not decision:
            counts["missing"] += 1
            continue
        decision = str(decision).strip().lower()
        if decision in counts and decision not in {"other", "missing"}:
            counts[decision] += 1
        else:
            counts["other"] += 1
    return counts


def write_ready_dataset(package_root: Path, dataset_key: str, entries: List[CandidateSample], dataset_stats: Dict[str, Any]) -> Dict[str, Any]:
    dataset_out = package_root / "datasets" / dataset_key
    samples_out = dataset_out / "samples"
    ensure_clean_dir(samples_out)

    artifact_images_out = dataset_out / "artifacts" / "images"
    artifact_crops_out = dataset_out / "artifacts" / "crops"

    source_runs = set()
    source_outputs = set()
    kept_problem_ids: List[str] = []
    kept_source_problem_ids: List[str] = []
    kept_samples: List[Dict[str, Any]] = []

    for entry in entries:
        target_name = f"{entry.range_key}__spid_{entry.source_problem_id}__{entry.problem_id}.json"
        target_sample = samples_out / target_name
        shutil.copy2(entry.sample_path, target_sample)
        source_runs.add(entry.run_dir.as_posix())
        source_outputs.add(entry.output_dir.as_posix())
        kept_problem_ids.append(entry.problem_id)
        kept_source_problem_ids.append(entry.source_problem_id)
        kept_samples.append(
            {
                "problem_id": entry.problem_id,
                "source_problem_id": entry.source_problem_id,
                "range_key": entry.range_key,
                "sample_path": target_sample.relative_to(package_root).as_posix(),
                "original_sample_filename": entry.sample_path.name,
                "source_output_dir": entry.output_dir.as_posix(),
                "source_run": entry.run_dir.as_posix(),
                "source_dataset_root": entry.dataset_root.as_posix(),
                "source_sample_path": entry.sample_path.as_posix(),
                "source_kind": entry.source_kind,
            }
        )
        for asset_path in collect_related_assets(entry.dataset_root, entry.problem_id):
            rel = asset_path.relative_to(entry.dataset_root)
            if rel.parts[:2] == ("artifacts", "images"):
                dst = artifact_images_out / Path(*rel.parts[2:])
            elif rel.parts[:2] == ("artifacts", "crops"):
                dst = artifact_crops_out / Path(*rel.parts[2:])
            else:
                dst = dataset_out / rel
            copy_tree_if_exists(asset_path, dst)

    counts = status_counts(entries)
    selection_validation = validate_selection(entries, dataset_stats)
    summary = {
        "dataset_key": dataset_key,
        "processed_samples": len(entries),
        "selected_samples": len(entries),
        "dedup_rule": dataset_stats.get("dedup_rule", "latest_to_oldest_within_range_by_source_problem_id_then_merge_ranges"),
        "scanned_files": dataset_stats["scanned_files"],
        "duplicate_source_problem_id": dataset_stats["duplicate_source_problem_id"],
        "unique_files": dataset_stats["unique_files"],
        "status_counts": counts,
        "source_runs": sorted(source_runs),
        "source_output_dirs": sorted(source_outputs),
        "available_output_kinds": dataset_stats.get("available_output_kinds", []),
        "selected_output_kind": dataset_stats.get("selected_output_kind"),
        "selected_output_kinds": dataset_stats.get("selected_output_kinds", []),
        "ranges": dataset_stats["ranges"],
        "selection_validation": selection_validation,
    }
    write_json(dataset_out / "summary.json", summary)
    write_json(
        dataset_out / "selection_manifest.json",
        {
            "dataset_key": dataset_key,
            "selection_rule": dataset_stats.get(
                "selection_rule",
                "Use only outputs folders whose names contain dataset_key_start_end (prefix/suffix allowed). For each such range folder, scan runs newest to oldest; keep the first sample for each source_problem_id; after finishing each range, merge all ranges together.",
            ),
            "kept_problem_ids": kept_problem_ids,
            "kept_source_problem_ids": kept_source_problem_ids,
            "kept_samples": kept_samples,
            "ranges": dataset_stats["ranges"],
        },
    )
    write_validation = validate_written_dataset(package_root, dataset_key, summary)
    summary["write_validation"] = write_validation
    write_json(dataset_out / "summary.json", summary)

    if not selection_validation["ok"] or not write_validation["ok"]:
        raise RuntimeError(
            f"validation failed for {dataset_key}: selection_ok={selection_validation['ok']} write_ok={write_validation['ok']}"
        )
    return summary


def main() -> None:
    args = parse_args()
    dataset_filter = set(args.dataset)
    selected, stats = build_selected_samples(dataset_filter=dataset_filter, output_globs=args.output_glob)

    manifest = {
        key: {
            "count": len(entries),
            "scanned_files": stats[key]["scanned_files"],
            "duplicate_source_problem_id": stats[key]["duplicate_source_problem_id"],
            "source_output_dirs": sorted({entry.output_dir.as_posix() for entry in entries}),
        }
        for key, entries in sorted(selected.items())
    }
    print(json.dumps(manifest, ensure_ascii=False, indent=2))

    if args.dry_run:
        return

    for dataset_key, entries in sorted(selected.items()):
        package_label = stats[dataset_key].get("package_dataset_label") or dataset_key
        package_name = f"{args.package_prefix}__{package_label}"
        package_root = READY_ROOT / dataset_key / package_name
        ensure_clean_dir(package_root)
        summary = write_ready_dataset(package_root=package_root, dataset_key=dataset_key, entries=entries, dataset_stats=stats[dataset_key])
        print(f"[done] {dataset_key}: {summary['selected_samples']} -> {package_root}")


if __name__ == "__main__":
    main()
