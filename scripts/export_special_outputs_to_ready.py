#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RECORD_NAMES = [
    "alignment_records.jsonl",
    "asset_records.jsonl",
    "asset_registry_records.jsonl",
    "candidate_pool_entries.jsonl",
    "candidate_problem_records.jsonl",
    "candidate_registration_records.jsonl",
    "clean_pool_entries.jsonl",
    "clean_problem_records.jsonl",
    "cleaning_records.jsonl",
    "field_audit_records.jsonl",
    "initial_scoring_records.jsonl",
    "node_records.jsonl",
    "normalization_records.jsonl",
    "normalized_assets.jsonl",
    "open_ended_problem_variants.jsonl",
    "problem_main_records.jsonl",
    "raw_asset_bundles.jsonl",
    "reject_records.jsonl",
    "rewrite_reports.jsonl",
    "solvability_reports.jsonl",
    "source_intake_records.jsonl",
    "text_structure_records.jsonl",
    "visual_structure_records.jsonl",
]

CONFIG = {
    "eee_bench": {
        "package_name": "run_merged_eee_bench_1000_2860_dedup",
        "dataset_name": "EEE-Bench",
        "subject": "电气电子工程领域",
        "source_runs": [
            PROJECT_ROOT / "outputs/eee_bench_1000_2860/run_9ab7b7c008590714",
        ],
        "detail": "Ready export from special EEE-Bench output 1000:2860 with exact dedup by problem_id, then exact content dedup on normalized question+answer; high-similarity pairs are only flagged for review.",
        "selection_file": PROJECT_ROOT / "plans/eee_bench_1000_2860_ready_selected_ids.json",
        "duplicate_manifest_file": PROJECT_ROOT / "plans/eee_bench_1000_2860_duplicate_manifest.json",
        "suspected_duplicates_file": PROJECT_ROOT / "plans/eee_bench_1000_2860_suspected_duplicates.json",
    },
    "mathvision": {
        "package_name": "run_merged_mathvision_300_3040_dedup",
        "dataset_name": "MathVision",
        "subject": "数学",
        "source_runs": [
            PROJECT_ROOT / "outputs/mathvision_300_3040/run_053a22a217c324a7",
        ],
        "detail": "Ready export from special MathVision output 300:3040 with exact dedup by problem_id, then exact content dedup on normalized question+answer; high-similarity pairs are only flagged for review.",
        "selection_file": PROJECT_ROOT / "plans/mathvision_300_3040_ready_selected_ids.json",
        "duplicate_manifest_file": PROJECT_ROOT / "plans/mathvision_300_3040_duplicate_manifest.json",
        "suspected_duplicates_file": PROJECT_ROOT / "plans/mathvision_300_3040_suspected_duplicates.json",
    },
}


@dataclass
class SampleEntry:
    dataset_key: str
    problem_id: str
    normalized_question: str
    normalized_answer: str
    run_dir: Path
    dataset_root: Path
    sample_path: Path
    sample: Dict[str, Any]
    sample_created_at: str
    question_fingerprint: str
    answer_fingerprint: str
    content_fingerprint: str


@dataclass
class DuplicateGroup:
    stage: str
    key: str
    kept: SampleEntry
    dropped: List[SampleEntry]


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


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


def pick_first_dict(items: Any) -> Dict[str, Any]:
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                return item
    return {}


def normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", value or "")
    text = text.replace("\r", "\n")
    text = "\n".join(" ".join(line.split()) for line in text.split("\n"))
    return "\n".join(line for line in text.split("\n") if line).strip()


def sample_created_at(sample: Dict[str, Any]) -> str:
    problem_main = sample.get("problem_main_record") or {}
    clean_problem = sample.get("clean_problem_record") or {}
    normalization = sample.get("normalization_record") or {}
    candidate = sample.get("candidate_problem_record") or {}
    source = sample.get("source_intake_record") or {}
    clean_pool = pick_first_dict(sample.get("clean_pool_entries") or [])
    return pick_first_nonempty(
        problem_main.get("updated_at"),
        problem_main.get("created_at"),
        clean_problem.get("created_at"),
        normalization.get("created_at"),
        candidate.get("created_at"),
        clean_pool.get("created_at"),
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


def sample_question_answer(sample: Dict[str, Any]) -> Tuple[str, str]:
    problem_main = sample.get("problem_main_record") or {}
    clean_problem = sample.get("clean_problem_record") or {}
    normalized_assets = sample.get("normalized_assets") or {}
    normalization = sample.get("normalization_record") or {}
    candidate = sample.get("candidate_problem_record") or {}
    source = sample.get("source_intake_record") or {}

    question = pick_first_nonempty(
        problem_main.get("normalized_question_text"),
        clean_problem.get("normalized_question_text"),
        normalized_assets.get("normalized_question_text"),
        normalization.get("normalized_question_text"),
        candidate.get("raw_question_text"),
        source.get("raw_question_text"),
    )
    answer = pick_first_nonempty(
        problem_main.get("normalized_answer_text"),
        clean_problem.get("normalized_answer_text"),
        normalized_assets.get("normalized_answer_text"),
        normalization.get("normalized_answer_text"),
        candidate.get("raw_answer_text"),
        source.get("raw_answer_text"),
    )
    return question, answer


def sample_source_problem_id(sample: Dict[str, Any]) -> str:
    problem_main = sample.get("problem_main_record") or {}
    clean_problem = sample.get("clean_problem_record") or {}
    candidate = sample.get("candidate_problem_record") or {}
    source = sample.get("source_intake_record") or {}
    return pick_first_nonempty(
        problem_main.get("source_problem_id"),
        clean_problem.get("source_problem_id"),
        candidate.get("source_problem_id"),
        source.get("source_problem_id"),
    )


def sortable_time(value: str) -> Tuple[int, str]:
    return (1 if value else 0, value or "")


def choose_preferred(entries: List[SampleEntry]) -> SampleEntry:
    return max(entries, key=lambda entry: (sortable_time(entry.sample_created_at), entry.sample_path.as_posix()))


def iter_samples(dataset_key: str, source_runs: List[Path]) -> Iterable[SampleEntry]:
    for run_dir in source_runs:
        dataset_root = run_dir / "datasets" / dataset_key
        samples_dir = dataset_root / "samples"
        for sample_path in sorted(samples_dir.glob("prob_*.json")):
            sample = read_json(sample_path)
            problem_id = sample_problem_id(sample, sample_path)
            question, answer = sample_question_answer(sample)
            normalized_question = normalize_text(question)
            normalized_answer = normalize_text(answer)
            yield SampleEntry(
                dataset_key=dataset_key,
                problem_id=problem_id,
                normalized_question=normalized_question,
                normalized_answer=normalized_answer,
                run_dir=run_dir,
                dataset_root=dataset_root,
                sample_path=sample_path,
                sample=sample,
                sample_created_at=sample_created_at(sample),
                question_fingerprint=normalized_question,
                answer_fingerprint=normalized_answer,
                content_fingerprint=f"{normalized_question}\n===ANSWER===\n{normalized_answer}",
            )


def collect_related_assets(entry: SampleEntry) -> List[Path]:
    problem_id = entry.problem_id
    paths: List[Path] = [entry.sample_path]
    for artifact_dir in [entry.dataset_root / "artifacts" / "images", entry.dataset_root / "artifacts" / "crops"]:
        if not artifact_dir.exists():
            continue
        paths.extend(sorted(artifact_dir.glob(f"{problem_id}*")))
    return paths


def filter_record_lines(record_path: Path, selected_problem_ids: set[str]) -> List[str]:
    if not record_path.exists():
        return []
    needles = [json.dumps(problem_id) for problem_id in selected_problem_ids]
    matched: List[str] = []
    with record_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            raw = line.rstrip("\n")
            if not raw.strip():
                continue
            try:
                json.loads(raw)
            except Exception:
                continue
            if any(needle in raw for needle in needles):
                matched.append(raw)
    return matched


def detect_suspected_duplicates(entries: List[SampleEntry]) -> List[Dict[str, Any]]:
    buckets: Dict[str, List[SampleEntry]] = defaultdict(list)
    for entry in entries:
        if not entry.answer_fingerprint:
            continue
        buckets[entry.answer_fingerprint].append(entry)

    suspects: List[Dict[str, Any]] = []
    for answer_fingerprint, bucket in sorted(buckets.items()):
        if len(bucket) < 2 or len(bucket) > 50:
            continue
        ordered = sorted(bucket, key=lambda item: item.problem_id)
        for index, left in enumerate(ordered):
            for right in ordered[index + 1 :]:
                if left.content_fingerprint == right.content_fingerprint:
                    continue
                similarity = SequenceMatcher(None, left.question_fingerprint, right.question_fingerprint).ratio()
                if similarity < 0.97:
                    continue
                suspects.append(
                    {
                        "left_problem_id": left.problem_id,
                        "right_problem_id": right.problem_id,
                        "question_similarity": round(similarity, 6),
                        "answer_fingerprint": answer_fingerprint,
                        "left_sample_path": left.sample_path.relative_to(PROJECT_ROOT).as_posix(),
                        "right_sample_path": right.sample_path.relative_to(PROJECT_ROOT).as_posix(),
                    }
                )
    return suspects


def merge_llm_usage(summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    numeric: Counter[str] = Counter()
    last_error: Optional[Any] = None
    for summary in summaries:
        for key, value in (summary.get("llm_usage") or {}).items():
            if isinstance(value, (int, float)):
                numeric[key] += value
            elif key == "last_error" and value is not None:
                last_error = value
    result: Dict[str, Any] = dict(numeric)
    if "last_error" not in result:
        result["last_error"] = last_error
    return result


def first_existing_summary(run_dir: Path, dataset_key: str) -> Dict[str, Any]:
    dataset_summary_path = run_dir / "datasets" / dataset_key / "summary.json"
    if dataset_summary_path.exists():
        return read_json(dataset_summary_path)
    return {}


def build_duplicate_groups(stage: str, grouped: Dict[str, List[SampleEntry]]) -> Tuple[List[SampleEntry], List[DuplicateGroup]]:
    survivors: List[SampleEntry] = []
    duplicate_groups: List[DuplicateGroup] = []
    for key, entries in grouped.items():
        kept = choose_preferred(entries)
        survivors.append(kept)
        dropped = sorted([entry for entry in entries if entry.sample_path != kept.sample_path], key=lambda entry: entry.sample_path.as_posix())
        if dropped:
            duplicate_groups.append(DuplicateGroup(stage=stage, key=key, kept=kept, dropped=dropped))
    return survivors, sorted(duplicate_groups, key=lambda group: (group.stage, group.kept.problem_id, group.key))


def duplicate_group_payload(group: DuplicateGroup) -> Dict[str, Any]:
    kept_source_problem_id = sample_source_problem_id(group.kept.sample)
    payload = {
        "stage": group.stage,
        "key": group.key,
        "kept": {
            "problem_id": group.kept.problem_id,
            "source_problem_id": kept_source_problem_id,
            "sample_path": group.kept.sample_path.relative_to(PROJECT_ROOT).as_posix(),
            "source_run": group.kept.run_dir.relative_to(PROJECT_ROOT).as_posix(),
        },
        "dropped": [],
    }
    for entry in group.dropped:
        payload["dropped"].append(
            {
                "problem_id": entry.problem_id,
                "source_problem_id": sample_source_problem_id(entry.sample),
                "sample_path": entry.sample_path.relative_to(PROJECT_ROOT).as_posix(),
                "source_run": entry.run_dir.relative_to(PROJECT_ROOT).as_posix(),
            }
        )
    return payload


def build_ready_package(dataset_key: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
    package_root = PROJECT_ROOT / "ready" / dataset_key / cfg["package_name"]
    if package_root.exists():
        shutil.rmtree(package_root)

    all_entries = list(iter_samples(dataset_key, cfg["source_runs"]))

    by_problem_id: Dict[str, List[SampleEntry]] = defaultdict(list)
    for entry in all_entries:
        by_problem_id[entry.problem_id].append(entry)
    problem_id_survivors, problem_id_duplicate_groups = build_duplicate_groups("problem_id", by_problem_id)

    by_content: Dict[str, List[SampleEntry]] = defaultdict(list)
    for entry in problem_id_survivors:
        by_content[entry.content_fingerprint].append(entry)
    selected_entries, content_duplicate_groups = build_duplicate_groups("normalized_question_answer", by_content)
    selected_entries = sorted(selected_entries, key=lambda entry: entry.problem_id)

    selected_problem_ids = {entry.problem_id for entry in selected_entries}
    suspected_duplicates = detect_suspected_duplicates(selected_entries)

    dataset_dir = package_root / "datasets" / dataset_key
    (dataset_dir / "samples").mkdir(parents=True, exist_ok=True)
    (dataset_dir / "records").mkdir(parents=True, exist_ok=True)
    (dataset_dir / "artifacts" / "images").mkdir(parents=True, exist_ok=True)
    (dataset_dir / "artifacts" / "crops").mkdir(parents=True, exist_ok=True)

    copied_assets = 0
    for entry in selected_entries:
        for src_path in collect_related_assets(entry):
            if src_path == entry.sample_path:
                target = dataset_dir / "samples" / src_path.name
            elif "artifacts/images" in src_path.as_posix().replace("\\", "/"):
                target = dataset_dir / "artifacts" / "images" / src_path.name
            else:
                target = dataset_dir / "artifacts" / "crops" / src_path.name
            shutil.copy2(src_path, target)
            copied_assets += 1

    for record_name in RECORD_NAMES:
        merged_lines: List[str] = []
        for run_dir in cfg["source_runs"]:
            record_path = run_dir / "datasets" / dataset_key / "records" / record_name
            merged_lines.extend(filter_record_lines(record_path, selected_problem_ids))
        out_path = dataset_dir / "records" / record_name
        with out_path.open("w", encoding="utf-8", newline="\n") as handle:
            if merged_lines:
                handle.write("\n".join(merged_lines) + "\n")

    top_summaries = [read_json(run_dir / "summary.json") for run_dir in cfg["source_runs"] if (run_dir / "summary.json").exists()]
    dataset_summaries = [first_existing_summary(run_dir, dataset_key) for run_dir in cfg["source_runs"]]
    started_values = [value for summary in [*top_summaries, *dataset_summaries] for value in [summary.get("started_at")] if value]
    finished_values = [value for summary in [*top_summaries, *dataset_summaries] for value in [summary.get("finished_at")] if value]
    created_values = [entry.sample_created_at for entry in selected_entries if entry.sample_created_at]

    sample_count_before_problem_id = len(all_entries)
    sample_count_after_problem_id = len(problem_id_survivors)
    sample_count_after_content = len(selected_entries)

    rewrite_strategy_counts = Counter()
    decision_counts = Counter()
    for entry in selected_entries:
        problem_main = entry.sample.get("problem_main_record") or {}
        clean_problem = entry.sample.get("clean_problem_record") or {}
        clean_pool = pick_first_dict(entry.sample.get("clean_pool_entries") or [])
        rewrite_strategy = pick_first_nonempty(
            clean_pool.get("rewrite_strategy"),
            problem_main.get("rewrite_strategy"),
            clean_problem.get("rewrite_strategy"),
        )
        if rewrite_strategy:
            rewrite_strategy_counts[rewrite_strategy] += 1
        decision = pick_first_nonempty(
            clean_problem.get("clean_decision"),
            problem_main.get("clean_decision"),
            clean_pool.get("clean_decision"),
            "unknown",
        )
        decision_counts[decision] += 1

    duplicate_manifest_payload = {
        "dataset_key": dataset_key,
        "package_root": package_root.relative_to(PROJECT_ROOT).as_posix(),
        "strategy": [
            "dedupe_by_problem_id_across_runs",
            "dedupe_by_normalized_question_plus_answer_exact_match",
        ],
        "problem_id_duplicates": [duplicate_group_payload(group) for group in problem_id_duplicate_groups],
        "content_duplicates": [duplicate_group_payload(group) for group in content_duplicate_groups],
    }

    dedupe_payload = {
        "strategy": [
            "dedupe_by_problem_id_across_runs",
            "dedupe_by_normalized_question_plus_answer_exact_match",
            "high_similarity_pairs_flag_only",
        ],
        "input_samples": sample_count_before_problem_id,
        "after_problem_id_dedup": sample_count_after_problem_id,
        "after_content_dedup": sample_count_after_content,
        "dropped_problem_id_duplicates": sum(len(group.dropped) for group in problem_id_duplicate_groups),
        "dropped_content_duplicates": sum(len(group.dropped) for group in content_duplicate_groups),
        "suspected_duplicate_pairs": len(suspected_duplicates),
        "duplicate_manifest_file": cfg["duplicate_manifest_file"].relative_to(PROJECT_ROOT).as_posix(),
        "suspected_duplicates_file": cfg["suspected_duplicates_file"].relative_to(PROJECT_ROOT).as_posix(),
    }

    dataset_summary = {
        "dataset_key": dataset_key,
        "dataset_name": cfg["dataset_name"],
        "subject": cfg["subject"],
        "source_status": "available",
        "detail": cfg["detail"],
        "requested_samples": sample_count_after_content,
        "processed_samples": sample_count_after_content,
        "decision_counts": dict(sorted(decision_counts.items())),
        "rewrite_strategy_counts": dict(sorted(rewrite_strategy_counts.items())),
        "records_dir": f"datasets/{dataset_key}/records",
        "sample_concurrency": 1,
        "started_at": min(started_values) if started_values else "",
        "finished_at": max(finished_values) if finished_values else "",
        "elapsed_seconds": round(float(merge_llm_usage(top_summaries).get("total_request_seconds", 0.0)), 3),
        "llm_usage": merge_llm_usage(top_summaries),
        "filtered_from": {
            "source_runs": [run_dir.relative_to(PROJECT_ROOT).as_posix() for run_dir in cfg["source_runs"]],
            "selected_samples": sample_count_after_content,
            "selection_rule": "dedupe by problem_id across runs, then exact dedupe on normalized_question_text + normalized_answer_text; only flag high-similarity pairs",
            "selection_file": cfg["selection_file"].relative_to(PROJECT_ROOT).as_posix(),
        },
        "dedupe": dedupe_payload,
    }

    top_summary = {
        "pipeline_run_id": cfg["package_name"],
        "created_at": max(created_values) if created_values else "",
        "datasets": [
            {
                "dataset_key": dataset_key,
                "dataset_name": cfg["dataset_name"],
                "summary_path": f"datasets/{dataset_key}/summary.json",
            }
        ],
        "sample_concurrency": 1,
        "started_at": dataset_summary["started_at"],
        "finished_at": dataset_summary["finished_at"],
        "elapsed_seconds": dataset_summary["elapsed_seconds"],
        "llm_usage": dataset_summary["llm_usage"],
        "dedupe": dedupe_payload,
    }

    write_json(dataset_dir / "summary.json", dataset_summary)
    write_json(package_root / "summary.json", top_summary)
    write_json(cfg["selection_file"], [entry.problem_id for entry in selected_entries])
    write_json(cfg["duplicate_manifest_file"], duplicate_manifest_payload)
    write_json(cfg["suspected_duplicates_file"], suspected_duplicates)

    return {
        "dataset_key": dataset_key,
        "package_root": package_root.relative_to(PROJECT_ROOT).as_posix(),
        "selected_samples": sample_count_after_content,
        "input_samples": sample_count_before_problem_id,
        "problem_id_duplicates_removed": dedupe_payload["dropped_problem_id_duplicates"],
        "content_duplicates_removed": dedupe_payload["dropped_content_duplicates"],
        "suspected_duplicate_pairs": len(suspected_duplicates),
        "copied_files": copied_assets,
    }


def main() -> None:
    results = []
    for dataset_key, cfg in CONFIG.items():
        results.append(build_ready_package(dataset_key, cfg))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
