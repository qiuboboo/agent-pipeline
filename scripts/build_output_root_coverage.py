#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_ROOT = PROJECT_ROOT / "outputs"
MANIFEST_PATH = PROJECT_ROOT / "manifests" / "sample_roster.json"
REPORT_PATH = PROJECT_ROOT / "manifests" / "output_root_coverage.json"
IGNORED_OUTPUT_ROOTS = {"repo_cache"}


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def count_glob(root: Path, pattern: str) -> int:
    return sum(1 for _ in root.glob(pattern))


def main() -> None:
    manifest = read_json(MANIFEST_PATH)
    covered_roots = {
        record["source_run_dir"].split("/")[1]
        for record in manifest.get("records", [])
        if isinstance(record.get("source_run_dir"), str) and record["source_run_dir"].startswith("outputs/")
    }

    output_roots: List[Dict[str, Any]] = []
    covered_count = 0
    ignored_count = 0
    empty_count = 0

    for root in sorted(path for path in OUTPUTS_ROOT.iterdir() if path.is_dir()):
        root_name = root.name
        run_dirs = count_glob(root, "**/run_*")
        dataset_summaries = count_glob(root, "**/datasets/*/summary.json")
        sample_dirs = count_glob(root, "**/datasets/*/samples")
        sample_files = count_glob(root, "**/datasets/*/samples/prob_*.json")

        ignored = root_name in IGNORED_OUTPUT_ROOTS
        covered_by_manifest = root_name in covered_roots
        empty_shell = dataset_summaries == 0 and sample_dirs == 0 and sample_files == 0

        if covered_by_manifest:
            covered_count += 1
        if ignored:
            ignored_count += 1
        if empty_shell:
            empty_count += 1

        status = "covered"
        if ignored:
            status = "ignored"
        elif empty_shell:
            status = "empty_shell"
        elif not covered_by_manifest:
            status = "not_covered"

        output_roots.append(
            {
                "output_root": root_name,
                "status": status,
                "covered_by_manifest": covered_by_manifest,
                "ignored": ignored,
                "empty_shell": empty_shell,
                "run_dir_count": run_dirs,
                "dataset_summary_count": dataset_summaries,
                "sample_dir_count": sample_dirs,
                "sample_file_count": sample_files,
            }
        )

    payload = {
        "manifest_path": str(MANIFEST_PATH.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "outputs_root": str(OUTPUTS_ROOT.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "total_output_roots": len(output_roots),
        "covered_output_roots": covered_count,
        "ignored_output_roots": ignored_count,
        "empty_shell_output_roots": empty_count,
        "output_roots": output_roots,
    }
    write_json(REPORT_PATH, payload)
    print(f"WROTE_REPORT={REPORT_PATH}")
    print(f"TOTAL_OUTPUT_ROOTS={payload['total_output_roots']}")
    print(f"COVERED_OUTPUT_ROOTS={payload['covered_output_roots']}")


if __name__ == "__main__":
    main()
