from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from benchmarkallinone.pipeline2.annotation_modules import build_ptk_foundation
from benchmarkallinone.pipeline2.config import Pipeline2Config
from benchmarkallinone.pipeline2.pipeline import (
    _build_stage_cache_summary,
    _load_stage_cache_record,
    _write_stage_cache_record,
    initialize_runtime,
)


def _load_local_env() -> None:
    env_path = PROJECT_ROOT / "src/benchmarkallinone/pipeline2/configs/pipeline2.local.env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        for env_key, env_value in os.environ.items():
            value = value.replace("${" + env_key + "}", env_value)
        os.environ[key.strip()] = value


def _hydrate_problem_from_sample(problem: dict) -> dict:
    sample_path = problem.get("sample_path")
    if not isinstance(sample_path, str) or not sample_path.strip():
        return problem
    path = Path(sample_path)
    if not path.exists():
        return problem
    sample = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(sample, dict):
        return problem
    hydrated = dict(problem)
    for key in ("visual_structure_records", "text_structure_records"):
        if key in sample and key not in hydrated:
            hydrated[key] = sample[key]
    if "sample_record" not in hydrated:
        hydrated["sample_record"] = {
            "visual_structure_records": sample.get("visual_structure_records") or [],
            "text_structure_records": sample.get("text_structure_records") or [],
        }
    return hydrated


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repair PTK foundation directly from existing stage cache progress.")
    parser.add_argument("--config", required=True, help="pipeline2 YAML config path")
    parser.add_argument("--batch-id", required=True, help="Existing batch id whose stage cache should be reused")
    parser.add_argument("--problem-id", required=True, help="Problem id to repair")
    parser.add_argument("--max-repair-rounds", type=int, default=4, help="Repair budget to use for this direct PTK rerun")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    _load_local_env()

    config = Pipeline2Config.from_yaml(args.config)
    ctx = initialize_runtime(config, PROJECT_ROOT)
    ctx.router.ensure_available("pipeline2 direct-ptk-repair")

    progress_state = _load_stage_cache_record(args.batch_id, args.problem_id, "ptk_foundation_progress", "bundle")
    if not isinstance(progress_state, dict) or not progress_state:
        raise RuntimeError(
            f"No PTK progress cache found for batch_id={args.batch_id} problem_id={args.problem_id}."
        )

    foundation = progress_state.get("foundation")
    if not isinstance(foundation, dict) or not foundation:
        raise RuntimeError(
            f"PTK progress cache for batch_id={args.batch_id} problem_id={args.problem_id} has no foundation payload."
        )

    problem = foundation.get("problem_record")
    if not isinstance(problem, dict) or not problem:
        raise RuntimeError(
            f"PTK progress cache for batch_id={args.batch_id} problem_id={args.problem_id} has no problem_record."
        )
    problem = _hydrate_problem_from_sample(problem)

    def _save_progress(payload: dict) -> None:
        _write_stage_cache_record(args.batch_id, args.problem_id, "ptk_foundation_progress", "bundle", payload)

    result = build_ptk_foundation(
        ctx.router,
        problem,
        max_repair_rounds=max(0, int(args.max_repair_rounds)),
        progress_state=progress_state,
        save_progress=_save_progress,
    )

    if isinstance(result, dict) and isinstance(result.get("audit"), dict) and result["audit"].get("passed"):
        _write_stage_cache_record(args.batch_id, args.problem_id, "ptk_foundation", "bundle", result)

    output = {
        "batch_id": args.batch_id,
        "problem_id": args.problem_id,
        "passed": bool((result.get("audit") or {}).get("passed")),
        "round_count": len((result.get("audit") or {}).get("rounds") or []),
        "stage_cache_summary": _build_stage_cache_summary(args.batch_id, args.problem_id),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
