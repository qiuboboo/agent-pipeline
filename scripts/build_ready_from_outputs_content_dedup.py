#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_ROOT = PROJECT_ROOT / "outputs"
READY_ROOT = PROJECT_ROOT / "ready"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}


@dataclass
class CandidateSample:
    dataset_key: str
    run_dir: Path
    dataset_root: Path
    sample_path: Path
    sample: Dict[str, Any]
    problem_id: str
    question_text: str
    normalized_question: str
    created_at: str


@dataclass
class DuplicateHit:
    skipped_problem_id: str
    kept_problem_id: str
    similarity: float
    skipped_sample_path: str
    kept_sample_path: str
    skipped_run: str
    kept_run: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build ready datasets from outputs only. Deduplicate while adding by comparing "
            "the incoming sample's question content against already accepted question content."
        )
    )
    parser.add_argument(
        "--dataset",
        action="append",
        default=[],
        help="Dataset key to include. Can be passed multiple times, e.g. --dataset physreason --dataset eee_bench",
    )
    parser.add_argument(
        "--output-glob",
        action="append",
        default=[],
        help="Optional output folder glob relative to outputs/, e.g. 'physreason_*' or 'eee_bench_*'",
    )
    parser.add_argument(
        "--package-prefix",
        default="run_outputs_similarity_dedup",
        help="Prefix for generated ready package directories.",
    )
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.90,
        help="Question similarity threshold for duplicate rejection, default 0.90.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze and print manifest only; do not write ready output.",
    )
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


def normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", value or "")
    text = text.replace("\r", "\n")
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def sortable_time(value: str) -> Tuple[int, str]:
    return (1 if value else 0, value or "")


def question_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


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


def sample_question_text(sample: Dict[str, Any]) -> str:
    problem_main = sample.get("problem_main_record") or {}
    clean_problem = sample.get("clean_problem_record") or {}
    normalized_assets = sample.get("normalized_assets") or {}
    normalization = sample.get("normalization_record") or {}
    candidate = sample.get("candidate_problem_record") or {}
    source = sample.get("source_intake_record") or {}
    return pick_first_nonempty(
        problem_main.get("normalized_question_text"),
        problem_main.get("raw_question_text"),
        clean_problem.get("normalized_question_text"),
        normalized_assets.get("normalized_question_text"),
        normalization.get("normalized_question_text"),
        candidate.get("raw_question_text"),
        source.get("raw_question_text"),
    )


def discover_run_dataset_roots(output_globs: List[str]) -> Iterable[Tuple[Path, Path, str]]:
    if output_globs:
        output_dirs: List[Path] = []
        for pattern in output_globs:
            output_dirs.extend(sorted(OUTPUTS_ROOT.glob(pattern)))
    else:
        output_dirs = sorted(path for path in OUTPUTS_ROOT.iterdir() if path.is_dir())

    seen: set[Tuple[str, str]] = set()
    for output_dir in output_dirs:
        for summary_path in sorted(output_dir.glob("**/datasets/*/summary.json")):
            dataset_root = summary_path.parent
            run_dir = dataset_root.parent.parent
            dataset_key = dataset_root.name
            key = (run_dir.as_posix(), dataset_key)
            if key in seen:
                continue
            seen.add(key)
            yield run_dir, dataset_root, dataset_key


def iter_candidate_samples(dataset_filter: set[str], output_globs: List[str]) -> Iterable[CandidateSample]:
    for run_dir, dataset_root, dataset_key in discover_run_dataset_roots(output_globs):
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
            question_text = sample_question_text(sample)
            normalized_question = normalize_text(question_text)
            if not normalized_question:
                continue
            yield CandidateSample(
                dataset_key=dataset_key,
                run_dir=run_dir,
                dataset_root=dataset_root,
                sample_path=sample_path,
                sample=sample,
                problem_id=sample_problem_id(sample, sample_path),
                question_text=question_text,
                normalized_question=normalized_question,
                created_at=sample_created_at(sample),
            )


def build_selected_samples(
    dataset_filter: set[str],
    output_globs: List[str],
    similarity_threshold: float,
) -> Tuple[Dict[str, List[CandidateSample]], Dict[str, List[DuplicateHit]]]:
    grouped: Dict[str, List[CandidateSample]] = {}
    for entry in iter_candidate_samples(dataset_filter, output_globs):
        grouped.setdefault(entry.dataset_key, []).append(entry)

    selected: Dict[str, List[CandidateSample]] = {}
    duplicate_hits: Dict[str, List[DuplicateHit]] = {}

    for dataset_key, entries in grouped.items():
        entries.sort(
            key=lambda item: (sortable_time(item.created_at), item.run_dir.as_posix(), item.sample_path.as_posix()),
            reverse=True,
        )
        accepted: List[CandidateSample] = []
        hits: List[DuplicateHit] = []

        for entry in entries:
            best_match: Optional[CandidateSample] = None
            best_similarity = 0.0
            for kept in accepted:
                sim = question_similarity(entry.normalized_question, kept.normalized_question)
                if sim > best_similarity:
                    best_similarity = sim
                    best_match = kept
            if best_match is not None and best_similarity >= similarity_threshold:
                hits.append(
                    DuplicateHit(
                        skipped_problem_id=entry.problem_id,
                        kept_problem_id=best_match.problem_id,
                        similarity=best_similarity,
                        skipped_sample_path=entry.sample_path.as_posix(),
                        kept_sample_path=best_match.sample_path.as_posix(),
                        skipped_run=entry.run_dir.as_posix(),
                        kept_run=best_match.run_dir.as_posix(),
                    )
                )
                continue
            accepted.append(entry)

        accepted.sort(key=lambda item: (item.run_dir.as_posix(), item.sample_path.as_posix()))
        selected[dataset_key] = accepted
        duplicate_hits[dataset_key] = hits

    return selected, duplicate_hits


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
    for artifact_dir in [
        dataset_root / "artifacts" / "images",
        dataset_root / "artifacts" / "crops",
        dataset_root / "assets",
        dataset_root / "images",
    ]:
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


def write_ready_dataset(
    package_root: Path,
    dataset_key: str,
    entries: List[CandidateSample],
    hits: List[DuplicateHit],
    similarity_threshold: float,
) -> Dict[str, Any]:
    dataset_out = package_root / "datasets" / dataset_key
    samples_out = dataset_out / "samples"
    ensure_clean_dir(samples_out)

    artifact_images_out = dataset_out / "artifacts" / "images"
    artifact_crops_out = dataset_out / "artifacts" / "crops"

    source_runs = set()
    kept_problem_ids: List[str] = []
    kept_samples: List[Dict[str, Any]] = []

    for entry in entries:
        target_sample = samples_out / entry.sample_path.name
        shutil.copy2(entry.sample_path, target_sample)
        source_runs.add(entry.run_dir.as_posix())
        kept_problem_ids.append(entry.problem_id)
        kept_samples.append(
            {
                "problem_id": entry.problem_id,
                "sample_path": target_sample.relative_to(package_root).as_posix(),
                "source_run": entry.run_dir.as_posix(),
                "source_dataset_root": entry.dataset_root.as_posix(),
                "source_sample_path": entry.sample_path.as_posix(),
                "normalized_question": entry.normalized_question,
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

    summary = {
        "dataset_key": dataset_key,
        "processed_samples": len(entries),
        "selected_samples": len(entries),
        "dedup_rule": "outputs_only_similarity_question_dedup_on_insert",
        "similarity_threshold": similarity_threshold,
        "duplicate_hits": len(hits),
        "source_runs": sorted(source_runs),
    }
    write_json(dataset_out / "summary.json", summary)
    write_json(
        dataset_out / "selection_manifest.json",
        {
            "dataset_key": dataset_key,
            "selection_rule": "Only outputs are scanned. Samples are added in sorted order; when adding a sample, its normalized question text is compared against already accepted normalized question text. Samples with similarity above threshold are skipped.",
            "similarity_threshold": similarity_threshold,
            "kept_problem_ids": kept_problem_ids,
            "kept_samples": kept_samples,
            "duplicate_hits": [
                {
                    "skipped_problem_id": hit.skipped_problem_id,
                    "kept_problem_id": hit.kept_problem_id,
                    "similarity": round(hit.similarity, 6),
                    "skipped_sample_path": hit.skipped_sample_path,
                    "kept_sample_path": hit.kept_sample_path,
                    "skipped_run": hit.skipped_run,
                    "kept_run": hit.kept_run,
                }
                for hit in hits
            ],
        },
    )
    return summary


def main() -> None:
    args = parse_args()
    dataset_filter = set(args.dataset)
    selected, duplicate_hits = build_selected_samples(
        dataset_filter=dataset_filter,
        output_globs=args.output_glob,
        similarity_threshold=args.similarity_threshold,
    )

    manifest = {
        key: {
            "count": len(entries),
            "duplicate_hits": len(duplicate_hits.get(key, [])),
            "source_runs": sorted({entry.run_dir.as_posix() for entry in entries}),
        }
        for key, entries in sorted(selected.items())
    }

    print(json.dumps(manifest, ensure_ascii=False, indent=2))

    if args.dry_run:
        return

    for dataset_key, entries in sorted(selected.items()):
        package_name = f"{args.package_prefix}__{dataset_key}"
        package_root = READY_ROOT / dataset_key / package_name
        ensure_clean_dir(package_root)
        summary = write_ready_dataset(
            package_root=package_root,
            dataset_key=dataset_key,
            entries=entries,
            hits=duplicate_hits.get(dataset_key, []),
            similarity_threshold=args.similarity_threshold,
        )
        print(f"[done] {dataset_key}: {summary['processed_samples']} -> {package_root}")


if __name__ == "__main__":
    main()
