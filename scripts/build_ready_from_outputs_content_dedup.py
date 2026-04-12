#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from review_release_policy import get_dataset_policy, matches_rule, normalize_reason_list, resolve_project_path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_ROOT = PROJECT_ROOT / "outputs"
READY_ROOT = PROJECT_ROOT / "ready"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
RANGE_SUFFIX_RE = re.compile(r"^(?P<dataset>.+?)_(?P<start>\d+)_(?P<end>\d+)$")
PROGRESS_SAMPLE_INTERVAL = 200
PROGRESS_WRITE_INTERVAL = 200


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
    parser.add_argument("--release-policy-config", default="configs/review_release_policies.yaml", help="Unified review release policy config used to allow review buckets into ready.")
    parser.add_argument("--disable-review-release", action="store_true", help="Disable review-release gating and keep only clean_decision=pass samples in ready.")
    return parser.parse_args()


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def log_progress(message: str) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}", file=sys.stderr, flush=True)


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

    if dataset_key_from_summary == "physreason":
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

    if dataset_key_from_summary == "scemqa":
        if output_name == "candidate_200_remote":
            return OutputDirMatch(
                range_key=output_name,
                dataset_key=dataset_key_from_summary,
                range_start=0,
                range_end=0,
                source_kind="scemqa_candidate_remote",
            )
        if output_name == "scemqa_single_sample":
            return OutputDirMatch(
                range_key=output_name,
                dataset_key=dataset_key_from_summary,
                range_start=0,
                range_end=0,
                source_kind="scemqa_single_sample",
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

    token_pattern = re.compile(rf"(?:^|_){re.escape(dataset_key_from_summary)}(?:_|$)")
    if token_pattern.search(output_name):
        return OutputDirMatch(
            range_key=output_name,
            dataset_key=dataset_key_from_summary,
            range_start=0,
            range_end=0,
            source_kind="contains_dataset_token",
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
    scanned_files = 0
    scanned_roots = 0
    for output_dir, run_dir, dataset_root, dataset_key, range_key, range_start, range_end, source_kind in discover_run_dataset_roots(output_globs):
        if dataset_filter and dataset_key not in dataset_filter:
            continue
        samples_dir = dataset_root / "samples"
        if not samples_dir.exists():
            continue
        sample_paths = sorted(samples_dir.glob("prob_*.json"))
        scanned_roots += 1
        log_progress(
            f"scan-root dataset={dataset_key} range={range_key} run={run_dir.name} "
            f"files={len(sample_paths)} output={output_dir.name} root_index={scanned_roots}"
        )
        for sample_path in sample_paths:
            try:
                sample = read_json(sample_path)
            except Exception:
                continue
            scanned_files += 1
            if scanned_files == 1 or scanned_files % PROGRESS_SAMPLE_INTERVAL == 0:
                log_progress(
                    f"scan-progress scanned_files={scanned_files} dataset={dataset_key} "
                    f"range={range_key} run={run_dir.name}"
                )
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
    log_progress(
        f"grouped datasets={len(grouped)} ranges={sum(len(ranges) for ranges in grouped.values())} "
        f"dataset_keys={','.join(sorted(grouped)) or 'none'}"
    )
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
        "allowed_output_dirs": [],
        "blocked_output_dirs": [],
        "package_dataset_label": dataset_key,
        "dedup_rule": "latest_to_oldest_within_range_by_source_problem_id_then_merge_ranges",
        "selection_rule": "Use outputs folders whose names either match dataset_key_start_end (prefix/suffix allowed) or contain the dataset key as a standalone underscore-delimited token. For each matched range folder, scan runs newest to oldest; keep the first sample for each source_problem_id; after finishing each range, merge all ranges together.",
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
    elif dataset_key == "phyx":
        preferred = ["phyx_029_528_rerun", "phyx_029_528", "phyx_000_500"]
        available_names = {entry.output_dir.name for entries in ranges.values() for entry in entries}
        chosen_primary = next((name for name in preferred if name in available_names), None)
        allowed = []
        if chosen_primary:
            allowed.append(chosen_primary)
        if "phyx_529_1528_rerun" in available_names:
            allowed.append("phyx_529_1528_rerun")
        if allowed:
            policy.update(
                allowed_output_dirs=allowed,
                selection_rule=(
                    "Use only the canonical PhyX families: keep one primary 0-500 package "
                    f"({', '.join(allowed[:1])}) plus phyx_529_1528_rerun when present. "
                    "Exclude duplicate alias packages such as phyx_000_500 / phyx_029_528 / phyx_029_528_rerun from being combined together."
                ),
            )
    elif dataset_key == "scemqa":
        available_names = {entry.output_dir.name for entries in ranges.values() for entry in entries}
        allowed = []
        blocked = []
        if "candidate_200_remote" in available_names:
            allowed.append("candidate_200_remote")
        if "scemqa_single_sample" in available_names:
            blocked.append("scemqa_single_sample")
        if allowed or blocked:
            policy.update(
                allowed_output_dirs=allowed,
                blocked_output_dirs=blocked,
                selection_rule="Use candidate_200_remote as the canonical SCEMQA source package and exclude scemqa_single_sample debug/probe outputs from ready assembly.",
            )
    elif dataset_key == "sciverse":
        available_names = {entry.output_dir.name for entries in ranges.values() for entry in entries}
        allowed = []
        if "sciverse_000_500" in available_names:
            allowed.append("sciverse_000_500")
        elif "sciverse_500" in available_names:
            allowed.append("sciverse_500")
        if "sciverse_500_end_rerun" in available_names:
            allowed.append("sciverse_500_end_rerun")
        blocked = []
        if "sciverse_000_500" in available_names and "sciverse_500" in available_names:
            blocked.append("sciverse_500")
        if allowed or blocked:
            policy.update(
                allowed_output_dirs=allowed,
                blocked_output_dirs=blocked,
                selection_rule="Use sciverse_000_500 as the canonical first-half package when present, pair it with sciverse_500_end_rerun for the tail rerun, and drop the duplicate alias package sciverse_500 when sciverse_000_500 already exists.",
            )
    return policy


def filter_ranges_by_policy(
    ranges: Dict[str, List[CandidateSample]],
    selected_output_kind: Optional[str],
    allowed_output_dirs: List[str],
    blocked_output_dirs: List[str],
) -> Dict[str, List[CandidateSample]]:
    allowed_output_dir_set = set(allowed_output_dirs)
    blocked_output_dir_set = set(blocked_output_dirs)
    filtered: Dict[str, List[CandidateSample]] = {}
    for range_key, entries in ranges.items():
        kept_entries = entries
        if selected_output_kind:
            kept_entries = [entry for entry in kept_entries if entry.source_kind == selected_output_kind]
        if allowed_output_dir_set:
            kept_entries = [entry for entry in kept_entries if entry.output_dir.name in allowed_output_dir_set]
        if blocked_output_dir_set:
            kept_entries = [entry for entry in kept_entries if entry.output_dir.name not in blocked_output_dir_set]
        if kept_entries:
            filtered[range_key] = kept_entries
    return filtered


def build_selected_samples(dataset_filter: set[str], output_globs: List[str]) -> Tuple[Dict[str, List[CandidateSample]], Dict[str, Dict[str, Any]]]:
    grouped = group_by_dataset_and_range(dataset_filter, output_globs)
    selected: Dict[str, List[CandidateSample]] = {}
    stats: Dict[str, Dict[str, Any]] = {}

    for dataset_key, original_ranges in grouped.items():
        policy = build_policy_for_dataset(dataset_key, original_ranges)
        ranges = filter_ranges_by_policy(
            original_ranges,
            policy["selected_output_kind"],
            policy.get("allowed_output_dirs", []),
            policy.get("blocked_output_dirs", []),
        )
        if not ranges:
            log_progress(f"select-skip dataset={dataset_key} reason=no_ranges_after_policy")
            continue

        candidate_count = sum(len(entries) for entries in ranges.values())
        run_count = len({entry.run_dir.as_posix() for entries in ranges.values() for entry in entries})
        log_progress(
            f"select-start dataset={dataset_key} ranges={len(ranges)} runs={run_count} "
            f"candidate_samples={candidate_count} dedup_rule={policy['dedup_rule']}"
        )

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
                log_progress(
                    f"select-range dataset={dataset_key} range={range_key} runs={len(range_runs)} "
                    f"candidate_samples={len(range_entries)} mode=global_physreason"
                )

            run_keys = sorted(by_run.keys(), key=lambda k: run_sort_key(run_lookup[k]), reverse=True)
            for run_index, run_key in enumerate(run_keys, start=1):
                log_progress(
                    f"select-run dataset={dataset_key} run={Path(run_key).name} "
                    f"run_index={run_index}/{len(run_keys)} candidate_samples={len(by_run[run_key])}"
                )
                for entry in sorted(by_run[run_key], key=sample_sort_key, reverse=True):
                    range_summary = range_summary_map[entry.range_key]
                    range_summary["scanned_files"] += 1
                    dataset_scanned += 1
                    if dataset_scanned == 1 or dataset_scanned % PROGRESS_SAMPLE_INTERVAL == 0:
                        log_progress(
                            f"select-progress dataset={dataset_key} scanned={dataset_scanned} "
                            f"kept={len(accepted_all)} skipped={dataset_skipped} current_run={Path(run_key).name}"
                        )
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
                log_progress(
                    f"select-range dataset={dataset_key} range={range_key} runs={len(run_keys)} "
                    f"candidate_samples={len(range_entries)}"
                )

                for run_index, run_key in enumerate(run_keys, start=1):
                    kept_run_order.append(run_key)
                    log_progress(
                        f"select-run dataset={dataset_key} range={range_key} run={Path(run_key).name} "
                        f"run_index={run_index}/{len(run_keys)} candidate_samples={len(by_run[run_key])}"
                    )
                    for entry in sorted(by_run[run_key], key=sample_sort_key, reverse=True):
                        range_scanned += 1
                        dataset_scanned += 1
                        if dataset_scanned == 1 or dataset_scanned % PROGRESS_SAMPLE_INTERVAL == 0:
                            log_progress(
                                f"select-progress dataset={dataset_key} scanned={dataset_scanned} "
                                f"kept={len(accepted_all)} skipped={dataset_skipped} current_range={range_key} current_run={Path(run_key).name}"
                            )
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
        log_progress(
            f"select-done dataset={dataset_key} selected={len(accepted_all)} scanned={dataset_scanned} "
            f"duplicate_source_problem_id={dataset_skipped}"
        )

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


def pick_clean_decision(sample: Dict[str, Any]) -> str:
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
        return "missing"
    normalized = str(decision).strip().lower()
    return normalized if normalized else "missing"


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


def build_release_gate(dataset_key: str, policy_config: Path, disabled: bool) -> Dict[str, Any]:
    if disabled:
        return {"enabled": False, "dataset_key": dataset_key, "release_buckets": []}
    dataset_policy = get_dataset_policy(dataset_key, policy_config)
    release_buckets = []
    for bucket_key, bucket_cfg in sorted((dataset_policy.get("release_buckets") or {}).items()):
        if not bucket_cfg or not bucket_cfg.get("enabled", True):
            continue
        selection = bucket_cfg.get("selection") or None
        candidate_key = str(bucket_cfg.get("candidate_key") or f"{bucket_key}_candidates")
        selection_notes = str(bucket_cfg.get("selection_notes") or "")
        rule_type = "structured_selection" if selection else "explicit_candidate_subset"
        if rule_type != "structured_selection":
            continue
        release_buckets.append(
            {
                "bucket_key": bucket_key,
                "candidate_key": candidate_key,
                "selection": selection,
                "rule_type": rule_type,
                "selection_notes": selection_notes,
                "release_basis": str(bucket_cfg.get("release_basis") or ""),
                "pass_decision_reason_codes": normalize_reason_list(bucket_cfg.get("pass_decision_reason_codes")),
            }
        )
    return {
        "enabled": True,
        "dataset_key": dataset_key,
        "policy_config": policy_config.as_posix(),
        "release_buckets": release_buckets,
    }


def classify_entry_for_ready(entry: CandidateSample, release_gate: Dict[str, Any]) -> Dict[str, Any]:
    decision = pick_clean_decision(entry.sample)
    reason_codes = pick_reason_codes(entry.sample)
    if decision == "pass":
        return {
            "include": True,
            "final_decision": "pass",
            "source_decision": decision,
            "source_reason_codes": reason_codes,
            "release_bucket": "",
            "release_basis": "",
            "selection_notes": "",
            "released_from_review": False,
            "drop_reason": "",
        }
    if decision == "review" and release_gate.get("enabled"):
        for bucket in release_gate.get("release_buckets") or []:
            if matches_rule(reason_codes, str(bucket.get("rule_type") or "structured_selection"), bucket.get("selection")):
                return {
                    "include": True,
                    "final_decision": "pass",
                    "source_decision": decision,
                    "source_reason_codes": reason_codes,
                    "release_bucket": str(bucket.get("bucket_key") or ""),
                    "release_basis": str(bucket.get("release_basis") or ""),
                    "selection_notes": str(bucket.get("selection_notes") or ""),
                    "released_from_review": True,
                    "drop_reason": "",
                }
    return {
        "include": False,
        "final_decision": decision,
        "source_decision": decision,
        "source_reason_codes": reason_codes,
        "release_bucket": "",
        "release_basis": "",
        "selection_notes": "",
        "released_from_review": False,
        "drop_reason": "filtered_non_pass_or_unreleased_review",
    }


def pick_clean_decision_counts(entries: List[CandidateSample]) -> Dict[str, int]:
    counts = {"pass": 0, "review": 0, "reject": 0, "other": 0, "missing": 0}
    for entry in entries:
        decision = pick_clean_decision(entry.sample)
        if decision in counts:
            counts[decision] += 1
        else:
            counts["other"] += 1
    return counts


def build_selection_manifest(
    dataset_key: str,
    entries: List[CandidateSample],
    dataset_stats: Dict[str, Any],
    *,
    release_gate: Dict[str, Any],
) -> Tuple[Dict[str, Any], List[CandidateSample], Dict[str, int], Dict[str, int]]:
    kept_problem_ids: List[str] = []
    kept_source_problem_ids: List[str] = []
    kept_samples: List[Dict[str, Any]] = []
    dropped_samples: List[Dict[str, Any]] = []
    release_counts: Dict[str, int] = {"pass_original": 0, "released_review": 0, "dropped_review": 0, "dropped_reject": 0, "dropped_other": 0}
    selected_entries: List[CandidateSample] = []

    for entry in entries:
        release_info = classify_entry_for_ready(entry, release_gate)
        base_row = {
            "problem_id": entry.problem_id,
            "source_problem_id": entry.source_problem_id,
            "range_key": entry.range_key,
            "original_sample_filename": entry.sample_path.name,
            "source_output_dir": entry.output_dir.as_posix(),
            "source_run": entry.run_dir.as_posix(),
            "source_dataset_root": entry.dataset_root.as_posix(),
            "source_sample_path": entry.sample_path.as_posix(),
            "source_kind": entry.source_kind,
            "source_decision": release_info["source_decision"],
            "source_reason_codes": release_info["source_reason_codes"],
            "released_from_review": release_info["released_from_review"],
            "release_bucket": release_info["release_bucket"],
            "release_basis": release_info["release_basis"],
            "selection_notes": release_info["selection_notes"],
            "final_decision_for_ready": release_info["final_decision"],
        }
        if release_info["include"]:
            selected_entries.append(entry)
            kept_samples.append(base_row)
            kept_problem_ids.append(entry.problem_id)
            kept_source_problem_ids.append(entry.source_problem_id)
            if release_info["released_from_review"]:
                release_counts["released_review"] += 1
            else:
                release_counts["pass_original"] += 1
        else:
            dropped_samples.append({**base_row, "drop_reason": release_info["drop_reason"]})
            if release_info["source_decision"] == "review":
                release_counts["dropped_review"] += 1
            elif release_info["source_decision"] == "reject":
                release_counts["dropped_reject"] += 1
            else:
                release_counts["dropped_other"] += 1

    manifest = {
        "dataset_key": dataset_key,
        "selection_rule": dataset_stats.get(
            "selection_rule",
            "Use only outputs folders whose names contain dataset_key_start_end (prefix/suffix allowed). For each such range folder, scan runs newest to oldest; keep the first sample for each source_problem_id; after finishing each range, merge all ranges together.",
        ),
        "kept_problem_ids": kept_problem_ids,
        "kept_source_problem_ids": kept_source_problem_ids,
        "kept_samples": kept_samples,
        "dropped_samples": dropped_samples,
        "ranges": dataset_stats["ranges"],
        "release_gate": {
            "enabled": bool(release_gate.get("enabled")),
            "policy_config": release_gate.get("policy_config", ""),
            "structured_release_buckets": [bucket.get("bucket_key") for bucket in (release_gate.get("release_buckets") or [])],
            "counts": release_counts,
        },
    }
    return manifest, selected_entries, release_counts, pick_clean_decision_counts(entries)


def write_ready_dataset(
    package_root: Path,
    dataset_key: str,
    entries: List[CandidateSample],
    dataset_stats: Dict[str, Any],
    *,
    release_gate: Dict[str, Any],
) -> Dict[str, Any]:
    dataset_out = package_root / "datasets" / dataset_key
    samples_out = dataset_out / "samples"
    ensure_clean_dir(samples_out)

    artifact_images_out = dataset_out / "artifacts" / "images"
    artifact_crops_out = dataset_out / "artifacts" / "crops"

    log_progress(f"write-start dataset={dataset_key} package_root={package_root} samples={len(entries)}")

    source_runs = set()
    source_outputs = set()

    selection_manifest, selected_entries, release_counts, original_counts = build_selection_manifest(
        dataset_key,
        entries,
        dataset_stats,
        release_gate=release_gate,
    )
    write_json(dataset_out / "selection_manifest.json", selection_manifest)

    for index, entry in enumerate(selected_entries, start=1):
        target_name = f"{entry.range_key}__spid_{entry.source_problem_id}__{entry.problem_id}.json"
        target_sample = samples_out / target_name
        shutil.copy2(entry.sample_path, target_sample)
        source_runs.add(entry.run_dir.as_posix())
        source_outputs.add(entry.output_dir.as_posix())
        for row in selection_manifest["kept_samples"]:
            if row["problem_id"] == entry.problem_id and row["source_sample_path"] == entry.sample_path.as_posix():
                row["sample_path"] = target_sample.relative_to(package_root).as_posix()
                break
        for asset_path in collect_related_assets(entry.dataset_root, entry.problem_id):
            rel = asset_path.relative_to(entry.dataset_root)
            if rel.parts[:2] == ("artifacts", "images"):
                dst = artifact_images_out / Path(*rel.parts[2:])
            elif rel.parts[:2] == ("artifacts", "crops"):
                dst = artifact_crops_out / Path(*rel.parts[2:])
            else:
                dst = dataset_out / rel
            copy_tree_if_exists(asset_path, dst)
        if index == 1 or index % PROGRESS_WRITE_INTERVAL == 0 or index == len(selected_entries):
            log_progress(
                f"write-progress dataset={dataset_key} copied={index}/{len(selected_entries)} current_sample={target_name}"
            )

    counts = {"pass": len(selected_entries), "review": 0, "reject": 0, "other": 0, "missing": 0}
    selection_validation = validate_selection(entries, dataset_stats)
    summary = {
        "dataset_key": dataset_key,
        "processed_samples": len(selected_entries),
        "selected_samples": len(selected_entries),
        "input_selected_samples_before_release_gate": len(entries),
        "dedup_rule": dataset_stats.get("dedup_rule", "latest_to_oldest_within_range_by_source_problem_id_then_merge_ranges"),
        "scanned_files": dataset_stats["scanned_files"],
        "duplicate_source_problem_id": dataset_stats["duplicate_source_problem_id"],
        "unique_files": dataset_stats["unique_files"],
        "status_counts": counts,
        "original_status_counts_before_release_gate": original_counts,
        "release_gate": selection_manifest["release_gate"],
        "source_runs": sorted(source_runs),
        "source_output_dirs": sorted(source_outputs),
        "available_output_kinds": dataset_stats.get("available_output_kinds", []),
        "selected_output_kind": dataset_stats.get("selected_output_kind"),
        "selected_output_kinds": dataset_stats.get("selected_output_kinds", []),
        "ranges": dataset_stats["ranges"],
        "selection_validation": selection_validation,
    }
    write_json(dataset_out / "summary.json", summary)
    write_validation = validate_written_dataset(package_root, dataset_key, summary)
    summary["write_validation"] = write_validation
    write_json(dataset_out / "summary.json", summary)

    if not selection_validation["ok"] or not write_validation["ok"]:
        raise RuntimeError(
            f"validation failed for {dataset_key}: selection_ok={selection_validation['ok']} write_ok={write_validation['ok']}"
        )
    log_progress(
        f"write-done dataset={dataset_key} selected={summary['selected_samples']} pass={counts['pass']} "
        f"released_review={release_counts['released_review']} dropped_review={release_counts['dropped_review']} reject={original_counts['reject']}"
    )
    return summary


def write_run_summary(path: Path, package_prefix: str, dataset_summaries: Dict[str, Dict[str, Any]]) -> None:
    total_status_counts = {"pass": 0, "review": 0, "reject": 0, "other": 0, "missing": 0}
    total_original_status_counts = {"pass": 0, "review": 0, "reject": 0, "other": 0, "missing": 0}
    total_scanned_files = 0
    total_duplicate_source_problem_id = 0
    total_unique_files = 0
    total_selected_samples = 0

    datasets_payload: Dict[str, Dict[str, Any]] = {}
    for dataset_key, summary in sorted(dataset_summaries.items()):
        counts = summary.get("status_counts") or {}
        original_counts = summary.get("original_status_counts_before_release_gate") or {}
        for key in total_status_counts:
            total_status_counts[key] += int(counts.get(key, 0))
            total_original_status_counts[key] += int(original_counts.get(key, 0))
        total_scanned_files += int(summary.get("scanned_files", 0))
        total_duplicate_source_problem_id += int(summary.get("duplicate_source_problem_id", 0))
        total_unique_files += int(summary.get("unique_files", 0))
        total_selected_samples += int(summary.get("selected_samples", 0))
        datasets_payload[dataset_key] = {
            "dataset_key": dataset_key,
            "package_root": str(path.parent / dataset_key / f"{package_prefix}__{summary.get('selected_output_kind') or summary.get('dataset_key')}"),
            "scanned_files": summary.get("scanned_files", 0),
            "duplicate_source_problem_id": summary.get("duplicate_source_problem_id", 0),
            "unique_files": summary.get("unique_files", 0),
            "selected_samples": summary.get("selected_samples", 0),
            "status_counts": counts,
            "original_status_counts_before_release_gate": original_counts,
            "selection_validation": summary.get("selection_validation", {}),
            "write_validation": summary.get("write_validation", {}),
            "release_gate": summary.get("release_gate", {}),
            "selected_output_kind": summary.get("selected_output_kind"),
            "selected_output_kinds": summary.get("selected_output_kinds", []),
            "dedup_rule": summary.get("dedup_rule"),
        }

    payload = {
        "package_prefix": package_prefix,
        "dataset_count": len(datasets_payload),
        "totals": {
            "scanned_files": total_scanned_files,
            "duplicate_source_problem_id": total_duplicate_source_problem_id,
            "unique_files": total_unique_files,
            "selected_samples": total_selected_samples,
            "status_counts": total_status_counts,
            "original_status_counts_before_release_gate": total_original_status_counts,
        },
        "datasets": datasets_payload,
    }
    write_json(path, payload)


def main() -> None:
    args = parse_args()
    dataset_filter = set(args.dataset)
    log_progress(
        f"start dry_run={args.dry_run} datasets={','.join(sorted(dataset_filter)) or 'ALL'} "
        f"output_globs={','.join(args.output_glob) or '*'} package_prefix={args.package_prefix}"
    )
    selected, stats = build_selected_samples(dataset_filter=dataset_filter, output_globs=args.output_glob)
    log_progress(f"selection-finished datasets={len(selected)}")

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
        log_progress("dry-run complete")
        return

    dataset_summaries: Dict[str, Dict[str, Any]] = {}
    for dataset_key, entries in sorted(selected.items()):
        package_label = stats[dataset_key].get("package_dataset_label") or dataset_key
        package_name = f"{args.package_prefix}__{package_label}"
        package_root = READY_ROOT / dataset_key / package_name
        log_progress(f"package-start dataset={dataset_key} package_name={package_name}")
        ensure_clean_dir(package_root)
        release_gate = build_release_gate(
            dataset_key=dataset_key,
            policy_config=resolve_project_path(args.release_policy_config),
            disabled=args.disable_review_release,
        )
        summary = write_ready_dataset(
            package_root=package_root,
            dataset_key=dataset_key,
            entries=entries,
            dataset_stats=stats[dataset_key],
            release_gate=release_gate,
        )
        dataset_summaries[dataset_key] = {**summary, "package_name": package_name, "package_root": package_root.as_posix()}
        print(f"[done] {dataset_key}: {summary['selected_samples']} -> {package_root}")

    write_run_summary(READY_ROOT / "summary.json", args.package_prefix, dataset_summaries)
    log_progress(f"summary-written path={READY_ROOT / 'summary.json'} datasets={len(dataset_summaries)}")


if __name__ == "__main__":
    main()
