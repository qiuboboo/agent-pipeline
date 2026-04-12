#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_ROOT = PROJECT_ROOT / "outputs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill SCEMQA subject into output sample JSON files.")
    parser.add_argument("--mapping", required=True, help="Path to mapping JSON/JSONL/CSV file.")
    parser.add_argument("--outputs-root", default=str(OUTPUTS_ROOT), help="Outputs root to scan.")
    parser.add_argument("--dataset", default="scemqa", help="Dataset key to patch. Default: scemqa")
    parser.add_argument("--key-field", default="source_problem_id", choices=["source_problem_id", "problem_id", "sample_filename"], help="Which sample key to match against mapping.")
    parser.add_argument("--subject-field", default="subject", help="Field name in mapping records that stores the subject.")
    parser.add_argument("--write", action="store_true", help="Actually write changes. Default is dry-run.")
    return parser.parse_args()


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def pick_first_nonempty(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            if value.strip():
                return value.strip()
            continue
        return str(value)
    return ""


def sample_problem_id(sample: Dict[str, Any], sample_path: Path) -> str:
    for block_name in ["problem_main_record", "clean_problem_record", "normalization_record", "candidate_problem_record", "source_intake_record"]:
        block = sample.get(block_name) or {}
        value = block.get("problem_id")
        if value:
            return str(value)
    return sample_path.stem


def sample_source_problem_id(sample: Dict[str, Any], sample_path: Path) -> str:
    for block_name in ["problem_main_record", "clean_problem_record", "normalization_record", "candidate_problem_record", "source_intake_record"]:
        block = sample.get(block_name) or {}
        value = block.get("source_problem_id")
        if value:
            return str(value)
    return sample_problem_id(sample, sample_path)


def iter_mapping_rows(path: Path) -> Iterable[Dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        payload = read_json(path)
        if isinstance(payload, list):
            for row in payload:
                if isinstance(row, dict):
                    yield row
        elif isinstance(payload, dict):
            for key, value in payload.items():
                if isinstance(value, dict):
                    row = dict(value)
                    row.setdefault("key", key)
                    yield row
                else:
                    yield {"key": key, "subject": value}
        return
    if suffix == ".jsonl":
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if isinstance(row, dict):
                    yield row
        return
    if suffix == ".csv":
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield dict(row)
        return
    raise ValueError(f"Unsupported mapping format: {path}")


def load_mapping(path: Path, subject_field: str) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for row in iter_mapping_rows(path):
        subject = pick_first_nonempty(row.get(subject_field), row.get("subject"))
        if not subject:
            continue
        keys = [
            pick_first_nonempty(row.get("source_problem_id")),
            pick_first_nonempty(row.get("problem_id")),
            pick_first_nonempty(row.get("sample_filename")),
            pick_first_nonempty(row.get("key")),
        ]
        for key in keys:
            if key:
                mapping[key] = subject
    return mapping


def set_subject(sample: Dict[str, Any], subject: str) -> None:
    block = sample.get("source_intake_record")
    if isinstance(block, dict):
        block["subject"] = subject


def sample_lookup_key(sample: Dict[str, Any], sample_path: Path, key_field: str) -> str:
    if key_field == "sample_filename":
        return sample_path.name
    if key_field == "problem_id":
        return sample_problem_id(sample, sample_path)
    return sample_source_problem_id(sample, sample_path)


def main() -> None:
    args = parse_args()
    mapping_path = Path(args.mapping)
    outputs_root = Path(args.outputs_root)
    mapping = load_mapping(mapping_path, args.subject_field)

    sample_paths = sorted(outputs_root.glob(f"**/datasets/{args.dataset}/samples/*.json"))
    matched = 0
    updated = 0
    missing = 0
    unchanged = 0
    preview: List[Tuple[str, str, str]] = []

    for sample_path in sample_paths:
        sample = read_json(sample_path)
        key = sample_lookup_key(sample, sample_path, args.key_field)
        subject = mapping.get(key)
        if not subject:
            missing += 1
            continue
        matched += 1
        current = pick_first_nonempty(
            (sample.get("source_intake_record") or {}).get("subject"),
        )
        if current == subject:
            unchanged += 1
            continue
        set_subject(sample, subject)
        updated += 1
        if len(preview) < 20:
            preview.append((sample_path.as_posix(), current, subject))
        if args.write:
            write_json(sample_path, sample)

    result = {
        "dataset": args.dataset,
        "outputs_root": outputs_root.as_posix(),
        "mapping_path": mapping_path.as_posix(),
        "mapping_size": len(mapping),
        "sample_count": len(sample_paths),
        "matched": matched,
        "updated": updated,
        "unchanged": unchanged,
        "missing": missing,
        "write": bool(args.write),
        "preview": [
            {"sample_path": path, "old_subject": old, "new_subject": new}
            for path, old, new in preview
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
