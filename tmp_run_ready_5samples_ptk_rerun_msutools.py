from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from benchmarkallinone.pipeline2.config import Pipeline2Config
from benchmarkallinone.pipeline2.pipeline import initialize_runtime, run_annotation_pipeline
import run_pipeline2_repair as repair


CONFIG_PATH = PROJECT_ROOT / "pipeline2/configs/tmp_ready_5samples_20260428_w5_repair_on_cache.yaml"
BATCH_ID = "tmp_ready_5samples_20260428_w5_rerun"
CLEAR_STAGES = (
    "ptk_foundation",
    "ptk_foundation_progress",
    "method_results",
    "claim_bundles",
    "claim_bundle_progress",
)


def _remove_path(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_dir():
        count = sum(1 for _ in path.rglob("*"))
        shutil.rmtree(path)
        return count + 1
    path.unlink()
    return 1


def main() -> None:
    config = Pipeline2Config.from_yaml(str(CONFIG_PATH))
    ctx = initialize_runtime(config, PROJECT_ROOT)

    stage_cache_root = ctx.runtime_dir / "stage_cache" / BATCH_ID
    cleared_items = 0
    problem_ids: list[str] = []
    if stage_cache_root.exists():
        for problem_dir in sorted(stage_cache_root.iterdir()):
            if not problem_dir.is_dir():
                continue
            problem_ids.append(problem_dir.name)
            for stage_name in CLEAR_STAGES:
                cleared_items += _remove_path(problem_dir / stage_name)

    for directory in (ctx.output_root / "problem_errors", ctx.output_root / "problems"):
        if directory.exists():
            for item in directory.glob("*.json"):
                cleared_items += _remove_path(item)

    repair._clear_checkpoint(ctx.checkpoint_db_path)

    print(
        json.dumps(
            {
                "status": "starting",
                "batch_id": BATCH_ID,
                "problem_ids": problem_ids,
                "cleared_items": cleared_items,
                "checkpoint_db_path": str(ctx.checkpoint_db_path),
                "output_root": str(ctx.output_root),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    result = run_annotation_pipeline(config, PROJECT_ROOT, batch_id=BATCH_ID)
    print(json.dumps({"status": "finished", "result": result}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
