#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path

SOURCE_READY_ROOT = Path("/root/.openclaw/workspace/ready_zip_extract/ready")
PREV_READY_ROOT = Path("/root/.openclaw/workspace/ready_2_each/ready")
TMP_READY_ROOT = Path("/root/.openclaw/workspace/agent-pipeline/tmp/pipeline2_ready_plus2each_20260425")
MANIFEST_PATH = Path("/root/.openclaw/workspace/agent-pipeline/tmp/pipeline2_ready_plus2each_20260425_manifest.json")
ALLOWED = {"ready_for_annotation"}
PER_DATASET = 2


def is_allowed(sample: dict) -> bool:
    entries = sample.get("clean_pool_entries") or []
    for entry in entries:
        if isinstance(entry, dict) and str(entry.get("pool_status") or "") in ALLOWED:
            return True
    return False


def main() -> None:
    if TMP_READY_ROOT.exists():
        shutil.rmtree(TMP_READY_ROOT)
    TMP_READY_ROOT.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    selected = []
    dataset_summaries = []

    prev_sample_dirs = sorted(PREV_READY_ROOT.rglob("samples"))
    for prev_sample_dir in prev_sample_dirs:
        if not prev_sample_dir.is_dir():
            continue
        rel_dataset_dir = prev_sample_dir.parent.relative_to(PREV_READY_ROOT)
        source_dataset_dir = SOURCE_READY_ROOT / rel_dataset_dir
        source_sample_dir = source_dataset_dir / "samples"
        previous_names = {p.name for p in sorted(prev_sample_dir.glob("*.json"))}
        chosen = []
        skipped_seen = []

        for sample_path in sorted(source_sample_dir.glob("*.json")):
            if sample_path.name in previous_names:
                skipped_seen.append(sample_path.name)
                continue
            try:
                sample = json.loads(sample_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if not is_allowed(sample):
                continue
            chosen.append(sample_path)
            if len(chosen) >= PER_DATASET:
                break

        target_samples_dir = TMP_READY_ROOT / rel_dataset_dir / "samples"
        target_samples_dir.mkdir(parents=True, exist_ok=True)
        for src in chosen:
            dst = target_samples_dir / src.name
            shutil.copy2(src, dst)
            selected.append(
                {
                    "dataset_dir": str(rel_dataset_dir),
                    "source": str(src),
                    "copied_to": str(dst),
                }
            )

        source_artifacts = source_dataset_dir / "artifacts"
        target_artifacts = TMP_READY_ROOT / rel_dataset_dir / "artifacts"
        if source_artifacts.exists() and not target_artifacts.exists():
            target_artifacts.parent.mkdir(parents=True, exist_ok=True)
            target_artifacts.symlink_to(source_artifacts)

        dataset_summaries.append(
            {
                "dataset_dir": str(rel_dataset_dir),
                "previous_names": sorted(previous_names),
                "selected_names": [p.name for p in chosen],
                "selected_count": len(chosen),
                "skipped_previous_names_seen_in_source": skipped_seen,
            }
        )

    payload = {
        "source_ready_root": str(SOURCE_READY_ROOT),
        "previous_ready_root": str(PREV_READY_ROOT),
        "tmp_ready_root": str(TMP_READY_ROOT),
        "per_dataset": PER_DATASET,
        "selected_count": len(selected),
        "selected": selected,
        "datasets": dataset_summaries,
    }
    MANIFEST_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
