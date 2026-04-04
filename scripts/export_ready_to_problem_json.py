#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
DIFFICULTY_KEYS = {
    "difficulty",
    "difficulty_level",
    "level",
    "cognitive_level",
    "ambiguity_level",
}
MULTI_SOLUTION_KEYS = {
    "initial_multi_solution_score",
    "multi_solution_score",
    "multi_solution_mining_policy",
    "should_push_multi_solution_agent",
    "multi_solution_policy_rationale",
}
MULTIMODAL_KEYS = {
    "multimodal_strength_score",
    "image_dependency_score",
    "initial_image_dependency_score",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export ready datasets into unified problem JSON files.")
    parser.add_argument("--ready-root", default="ready", help="Root ready directory.")
    parser.add_argument("--output-dir", default="ready_problem_exports", help="Directory for exported JSON files.")
    parser.add_argument("--dataset", default="", help="Optional ready package name filter, e.g. sciverse_000_500.")
    return parser.parse_args()


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def iter_jsonl(path: Path) -> Iterator[Dict[str, Any]]:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def to_posix_relative(path: Path, start: Path) -> str:
    return path.relative_to(start).as_posix()


def discover_dataset_roots(ready_root: Path, package_filter: str) -> List[Path]:
    best_roots: Dict[Tuple[str, str], Tuple[int, Path]] = {}
    for summary_path in sorted(ready_root.glob("**/datasets/*/summary.json")):
        dataset_root = summary_path.parent
        rel = dataset_root.relative_to(ready_root)
        if package_filter and rel.parts[0] != package_filter:
            continue
        package_name = rel.parts[0]
        dataset_key = dataset_root.name
        summary = read_json(summary_path)
        processed_samples = int(summary.get("processed_samples") or 0)
        dedupe_key = (package_name, dataset_key)
        current = best_roots.get(dedupe_key)
        if current is None or processed_samples > current[0]:
            best_roots[dedupe_key] = (processed_samples, dataset_root)
    return [item[1] for item in sorted(best_roots.values(), key=lambda entry: entry[1].as_posix())]


def build_record_index(records_path: Path, key: str) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    for row in iter_jsonl(records_path):
        row_key = row.get(key)
        if row_key:
            index[str(row_key)] = row
    return index


def build_variant_index(records_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    index: Dict[str, List[Dict[str, Any]]] = {}
    for row in iter_jsonl(records_path):
        parent_problem_id = row.get("parent_problem_id")
        if not parent_problem_id:
            continue
        index.setdefault(str(parent_problem_id), []).append(row)
    for rows in index.values():
        rows.sort(key=lambda item: int(item.get("variant_index") or 0))
    return index


def build_sample_index(samples_dir: Path) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    if not samples_dir.exists():
        return index
    for sample_path in sorted(samples_dir.glob("prob_*.json")):
        sample = read_json(sample_path)
        problem_main = sample.get("problem_main_record") or {}
        problem_id = str(problem_main.get("problem_id") or sample_path.stem)
        sample["__sample_path"] = str(sample_path)
        index[problem_id] = sample
    return index


def deep_find_values(data: Any, keys: Sequence[str], prefix: str = "") -> Dict[str, Any]:
    found: Dict[str, Any] = {}
    if isinstance(data, dict):
        for key, value in data.items():
            key_path = f"{prefix}.{key}" if prefix else key
            if key in keys and not isinstance(value, (dict, list)):
                found[key_path] = value
            nested = deep_find_values(value, keys, key_path)
            found.update(nested)
    elif isinstance(data, list):
        for idx, value in enumerate(data):
            key_path = f"{prefix}[{idx}]" if prefix else f"[{idx}]"
            nested = deep_find_values(value, keys, key_path)
            found.update(nested)
    return found


def pick_first_scalar(*candidates: Any) -> Any:
    for candidate in candidates:
        if candidate is None:
            continue
        if isinstance(candidate, str) and not candidate.strip():
            continue
        return candidate
    return None


def candidate_problem(sample: Dict[str, Any]) -> Dict[str, Any]:
    return sample.get("candidate_problem_record") or {}


def problem_main(sample: Dict[str, Any]) -> Dict[str, Any]:
    return sample.get("problem_main_record") or {}


def resolve_question_text(variant: Optional[Dict[str, Any]], main_record: Dict[str, Any], sample: Dict[str, Any]) -> str:
    return str(
        pick_first_scalar(
            (variant or {}).get("rewritten_question_text"),
            main_record.get("normalized_question_text"),
            main_record.get("raw_question_text"),
            (sample.get("normalized_assets") or {}).get("normalized_question_text"),
            (sample.get("clean_problem_record") or {}).get("normalized_question_text"),
            (sample.get("normalization_record") or {}).get("normalized_question_text"),
            candidate_problem(sample).get("raw_question_text"),
            (sample.get("source_intake_record") or {}).get("raw_question_text"),
            "",
        )
    )


def resolve_standard_answer(variant: Optional[Dict[str, Any]], main_record: Dict[str, Any], sample: Dict[str, Any]) -> str:
    return str(
        pick_first_scalar(
            (variant or {}).get("expected_answer"),
            main_record.get("normalized_answer_text"),
            main_record.get("raw_answer_text"),
            (sample.get("normalized_assets") or {}).get("normalized_answer_text"),
            (sample.get("clean_problem_record") or {}).get("normalized_answer_text"),
            (sample.get("normalization_record") or {}).get("normalized_answer_text"),
            candidate_problem(sample).get("raw_answer_text"),
            (sample.get("source_intake_record") or {}).get("raw_answer_text"),
            "",
        )
    )


def gather_existing_files(paths: Iterable[Path], ready_root: Path) -> List[str]:
    unique: List[str] = []
    seen = set()
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        rel = to_posix_relative(path, ready_root)
        if rel in seen:
            continue
        seen.add(rel)
        unique.append(rel)
    return sorted(unique)


def resolve_source_relative_path(raw_path: str, dataset_root: Path) -> Optional[Path]:
    if not raw_path:
        return None
    value = raw_path.replace("\\", "/")
    if value.startswith("inline://") or "://" in value:
        return None
    candidate = Path(value)
    if candidate.is_absolute() and candidate.exists():
        return candidate
    local = dataset_root / candidate
    if local.exists():
        return local
    if len(candidate.parts) > 1:
        trimmed = dataset_root / Path(*candidate.parts[1:])
        if trimmed.exists():
            return trimmed
    return None


def collect_image_paths(sample: Dict[str, Any], dataset_root: Path, ready_root: Path, problem_id: str) -> List[str]:
    candidates: List[Path] = []

    for asset in sample.get("asset_records") or []:
        if not isinstance(asset, dict):
            continue
        asset_type = str(asset.get("asset_type") or "")
        asset_role = str(asset.get("asset_role") or "")
        if asset_type != "image" and "image" not in asset_role:
            continue
        for key in ("storage_uri", "source_uri"):
            resolved = resolve_source_relative_path(str(asset.get(key) or ""), dataset_root)
            if resolved is not None:
                candidates.append(resolved)

    for image_path in (sample.get("source_intake_record") or {}).get("image_paths") or []:
        resolved = resolve_source_relative_path(str(image_path), dataset_root)
        if resolved is not None:
            candidates.append(resolved)

    candidate_meta = (candidate_problem(sample).get("metadata") or {})
    for image_path in candidate_meta.get("image_paths") or []:
        resolved = resolve_source_relative_path(str(image_path), dataset_root)
        if resolved is not None:
            candidates.append(resolved)

    for subdir in (
        dataset_root / "artifacts" / "images",
        dataset_root / "artifacts" / "crops",
        dataset_root / "assets",
        dataset_root / "images",
    ):
        if not subdir.exists():
            continue
        for path in sorted(subdir.rglob("*")):
            if path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            if problem_id in path.name:
                candidates.append(path)

    return gather_existing_files(candidates, ready_root)


def build_multi_solution_hint(sample: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    problem = problem_main(sample)
    candidate = candidate_problem(sample)
    hint = {
        "policy": pick_first_scalar(problem.get("multi_solution_mining_policy"), candidate.get("multi_solution_mining_policy")),
        "should_push_agent": pick_first_scalar(candidate.get("should_push_multi_solution_agent"), problem.get("should_push_multi_solution_agent")),
        "rationale": pick_first_scalar(candidate.get("multi_solution_policy_rationale"), problem.get("multi_solution_policy_rationale")),
    }
    if all(value is None for value in hint.values()):
        return None
    return hint


def resolve_multimodal_score(main_record: Dict[str, Any], sample: Dict[str, Any]) -> Tuple[Any, Optional[str]]:
    sample_main = problem_main(sample)
    sample_initial = sample.get("initial_scoring_record") or {}
    candidates = [
        (main_record.get("multimodal_strength_score"), "problem_main_record.multimodal_strength_score"),
        (sample_main.get("multimodal_strength_score"), "sample.problem_main_record.multimodal_strength_score"),
        (sample_initial.get("image_dependency_score"), "sample.initial_scoring_record.image_dependency_score"),
        (sample_main.get("initial_image_dependency_score"), "sample.problem_main_record.initial_image_dependency_score"),
        (candidate_problem(sample).get("initial_image_dependency_score"), "sample.candidate_problem_record.initial_image_dependency_score"),
    ]
    for value, source in candidates:
        if value is not None:
            return value, source
    return None, None


def resolve_multi_solution_score(main_record: Dict[str, Any], sample: Dict[str, Any]) -> Tuple[Any, Optional[str]]:
    sample_main = problem_main(sample)
    sample_initial = sample.get("initial_scoring_record") or {}
    candidates = [
        (main_record.get("initial_multi_solution_score"), "problem_main_record.initial_multi_solution_score"),
        (sample_main.get("initial_multi_solution_score"), "sample.problem_main_record.initial_multi_solution_score"),
        (sample_initial.get("multi_step_score"), "sample.initial_scoring_record.multi_step_score"),
        (candidate_problem(sample).get("initial_multi_solution_score"), "sample.candidate_problem_record.initial_multi_solution_score"),
    ]
    for value, source in candidates:
        if value is not None:
            return value, source
    return None, None


def resolve_difficulty(main_record: Dict[str, Any], sample: Dict[str, Any]) -> Tuple[Any, Dict[str, Any], Optional[str]]:
    candidate_meta = candidate_problem(sample).get("metadata") or {}
    direct_candidates = [
        (candidate_meta.get("difficulty"), "sample.candidate_problem_record.metadata.difficulty"),
        (main_record.get("difficulty"), "problem_main_record.difficulty"),
        (((sample.get("source_intake_record") or {}).get("difficulty")), "sample.source_intake_record.difficulty"),
    ]
    for value, source in direct_candidates:
        if value is not None:
            meta = deep_find_values(sample, sorted(DIFFICULTY_KEYS))
            return value, meta, source

    meta = deep_find_values(sample, sorted(DIFFICULTY_KEYS))
    if meta:
        first_key = sorted(meta.keys())[0]
        return meta[first_key], meta, first_key

    fallback = main_record.get("multi_step_score")
    if fallback is not None:
        return fallback, meta, "problem_main_record.multi_step_score"
    return None, meta, None


def build_source_meta(
    package_name: str,
    dataset_key: str,
    dataset_root: Path,
    ready_root: Path,
    main_record: Dict[str, Any],
    sample: Dict[str, Any],
    variant: Optional[Dict[str, Any]],
    difficulty_meta: Dict[str, Any],
    difficulty_source: Optional[str],
    multimodal_source: Optional[str],
    multi_solution_source: Optional[str],
) -> Dict[str, Any]:
    meta: Dict[str, Any] = {
        "ready_package": package_name,
        "dataset_key": dataset_key,
        "dataset_root": to_posix_relative(dataset_root, ready_root),
        "source_dataset": main_record.get("source_dataset") or candidate_problem(sample).get("source_dataset"),
        "source_split": main_record.get("source_split"),
        "source_problem_id": main_record.get("source_problem_id") or (sample.get("source_intake_record") or {}).get("source_problem_id"),
        "score_sources": {
            "difficulty": difficulty_source,
            "multimodal_score": multimodal_source,
            "multi_solution_score": multi_solution_source,
        },
        "difficulty_meta": difficulty_meta,
        "raw_multi_solution_meta": deep_find_values(sample, sorted(MULTI_SOLUTION_KEYS)),
        "raw_multimodal_meta": deep_find_values(sample, sorted(MULTIMODAL_KEYS)),
    }
    if variant:
        meta.update(
            {
                "parent_problem_id": variant.get("parent_problem_id"),
                "open_variant_id": variant.get("open_variant_id"),
                "variant_index": variant.get("variant_index"),
                "split_role": variant.get("split_role"),
            }
        )
    return meta


def export_dataset(dataset_root: Path, ready_root: Path, output_dir: Path) -> Tuple[Path, int]:
    rel = dataset_root.relative_to(ready_root)
    package_name = rel.parts[0]
    dataset_key = dataset_root.name
    file_id = f"{package_name}__{dataset_key}"
    source_file_name = f"{file_id}.json"

    records_dir = dataset_root / "records"
    samples_dir = dataset_root / "samples"

    main_records = build_record_index(records_dir / "problem_main_records.jsonl", "problem_id")
    variants = build_variant_index(records_dir / "open_ended_problem_variants.jsonl")
    samples = build_sample_index(samples_dir)

    problems: List[Dict[str, Any]] = []
    all_problem_ids = sorted(set(main_records.keys()) | set(samples.keys()))

    for base_problem_id in all_problem_ids:
        main_record = main_records.get(base_problem_id, {})
        sample = samples.get(base_problem_id, {})
        image_paths = collect_image_paths(sample, dataset_root, ready_root, base_problem_id)
        multimodal_score, multimodal_source = resolve_multimodal_score(main_record, sample)
        multi_solution_score, multi_solution_source = resolve_multi_solution_score(main_record, sample)
        difficulty, difficulty_meta, difficulty_source = resolve_difficulty(main_record, sample)
        multi_solution_hint = build_multi_solution_hint(sample)
        problem_variants = variants.get(base_problem_id) or [None]

        for variant in problem_variants:
            export_problem_id = base_problem_id
            if variant is not None:
                export_problem_id = f"{base_problem_id}__v{variant.get('variant_index') or 1}"
            problems.append(
                {
                    "problem_id": export_problem_id,
                    "question_text": resolve_question_text(variant, main_record, sample),
                    "standard_answer": resolve_standard_answer(variant, main_record, sample),
                    "images": image_paths,
                    "source_meta": build_source_meta(
                        package_name=package_name,
                        dataset_key=dataset_key,
                        dataset_root=dataset_root,
                        ready_root=ready_root,
                        main_record=main_record,
                        sample=sample,
                        variant=variant,
                        difficulty_meta=difficulty_meta,
                        difficulty_source=difficulty_source,
                        multimodal_source=multimodal_source,
                        multi_solution_source=multi_solution_source,
                    ),
                    "multi_solution_hint": multi_solution_hint,
                    "ingest_status": "ready",
                    "difficulty": difficulty,
                    "multimodal_score": multimodal_score,
                    "multi_solution_score": multi_solution_score,
                }
            )

    payload = {
        "file_id": file_id,
        "stage": "raw_to_problem",
        "source_file_name": source_file_name,
        "problems": problems,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / source_file_name
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.write("\n")
    return output_path, len(problems)


def main() -> None:
    args = parse_args()
    ready_root = Path(args.ready_root).resolve()
    output_dir = Path(args.output_dir).resolve()

    dataset_roots = discover_dataset_roots(ready_root, args.dataset)
    if not dataset_roots:
        raise SystemExit("No dataset roots found under ready root.")

    exported: List[Tuple[Path, int]] = []
    for dataset_root in dataset_roots:
        exported.append(export_dataset(dataset_root, ready_root, output_dir))

    print(json.dumps({
        "ready_root": str(ready_root),
        "output_dir": str(output_dir),
        "exported_files": [
            {"path": str(path), "problem_count": count}
            for path, count in exported
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
