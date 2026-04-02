#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, List

DEFAULT_READY_ROOT = Path("/Users/a1234/benchmarkall/benchmarkallinone/outputs/ready")


def normalize_image_paths(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        normalized: List[str] = []
        for item in value:
            normalized.extend(normalize_image_paths(item))
        return normalized
    if isinstance(value, dict):
        return normalize_image_paths(
            value.get("path")
            or value.get("paths")
            or value.get("image")
            or value.get("url")
        )
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        lowered = stripped.lower()
        if "<pil.image" in lowered or "pil.image.image" in lowered:
            return []
        if stripped.startswith("[") and stripped.endswith("]"):
            try:
                parsed = json.loads(stripped)
            except Exception:
                return [stripped]
            return normalize_image_paths(parsed)
        return [stripped]
    return []


def dedupe_keep_order(items: Iterable[str]) -> List[str]:
    ordered: List[str] = []
    seen: set[str] = set()
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def collected_image_paths(sample: dict[str, Any]) -> List[str]:
    candidates: List[Any] = []
    source_intake = sample.get("source_intake_record")
    if isinstance(source_intake, dict):
        candidates.append(source_intake.get("image_paths"))
        candidates.append(source_intake.get("image_path"))
    candidate_problem = sample.get("candidate_problem_record")
    if isinstance(candidate_problem, dict):
        metadata = candidate_problem.get("metadata")
        if isinstance(metadata, dict):
            candidates.append(metadata.get("image_paths"))
            candidates.append(metadata.get("image_path"))
    flattened: List[str] = []
    for value in candidates:
        flattened.extend(normalize_image_paths(value))
    return dedupe_keep_order(flattened)


def iter_sample_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.json")):
        if path.parent.name == "samples":
            yield path


def dataset_name_from_path(path: Path) -> str:
    parts = list(path.parts)
    if "datasets" in parts:
        index = parts.index("datasets")
        if index + 1 < len(parts):
            return parts[index + 1]
    return "unknown"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="统计并删除 ready 目录中图片路径为空的样本。",
    )
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=DEFAULT_READY_ROOT,
        help="ready 目录路径，默认使用 benchmarkallinone/outputs/ready",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="实际删除匹配样本；默认仅统计，不删除。",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="打印匹配样本列表。",
    )
    parser.add_argument(
        "--list-limit",
        type=int,
        default=200,
        help="限制打印的匹配样本数量，默认 200。",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if not root.exists():
        raise SystemExit(f"ready 目录不存在: {root}")

    total_samples = 0
    matched_paths: List[Path] = []
    per_dataset: Counter[str] = Counter()
    parse_errors: List[str] = []

    for sample_path in iter_sample_files(root):
        total_samples += 1
        try:
            sample = json.loads(sample_path.read_text(encoding="utf-8"))
        except Exception as exc:
            parse_errors.append(f"{sample_path}: {exc}")
            continue
        if not isinstance(sample, dict):
            continue
        image_paths = collected_image_paths(sample)
        if image_paths:
            continue
        matched_paths.append(sample_path)
        per_dataset[dataset_name_from_path(sample_path)] += 1

    removed = 0
    if args.apply:
        for sample_path in matched_paths:
            sample_path.unlink(missing_ok=True)
            removed += 1

    print(f"ready_root={root}")
    print(f"sample_files={total_samples}")
    print(f"text_only_samples={len(matched_paths)}")
    print(f"removed_samples={removed}")
    if per_dataset:
        print("per_dataset:")
        for dataset_name, count in sorted(per_dataset.items()):
            print(f"  {dataset_name}: {count}")
    if parse_errors:
        print(f"parse_errors={len(parse_errors)}")
        for item in parse_errors[:20]:
            print(f"  {item}")
    if args.list:
        print("matched_sample_files:")
        for sample_path in matched_paths[: max(args.list_limit, 0)]:
            print(f"  {sample_path}")
        remaining = len(matched_paths) - min(len(matched_paths), max(args.list_limit, 0))
        if remaining > 0:
            print(f"  ... and {remaining} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
