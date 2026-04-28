"""
Generic pipeline2 repair mode.

Usage:
  python run_pipeline2_repair.py --config <yaml> --batch-id <batch_id>

Logic:
  1. Scan problem_errors/ for the given batch
  2. For each failed problem, parse error_message to extract the agent stage
  3. Clear the stage cache for that stage and all downstream stages
  4. Delete the problem_error file so the pipeline will retry
  5. Run the full annotation pipeline with the same batch_id
     → reuse cache for completed stages, re-run from the failure point
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from benchmarkallinone.pipeline2.config import Pipeline2Config
from benchmarkallinone.pipeline2.pipeline import (
    build_batch_graph,
    close_shared_checkpointer,
    discover_ready_problems,
    get_context,
    initialize_runtime,
    run_annotation_pipeline,
)


# ── stage→cache mapping ─────────────────────────────────────────────────
# When an agent fails, we need to clear its stage cache and all downstream
# caches so the pipeline re-runs from that point.
#
# Pipeline stage order (→ = has cache):
#   prepare_methods
#   build_ptk       → ptk_foundation, ptk_foundation_progress
#   run_methods     → method_results
#   extract_claims  → claim_bundles, claim_bundle_progress
#   induce_nodes      (no persistent cache)
#   group_solutions   (no persistent cache)
#   bind_evidence     (no persistent cache)
#   validate_problem_structure  (no persistent cache)
#   finalize_problem_bundle  (no persistent cache, writes problems/)

_AGENT_CACHE_CLEAR = {
    # PTK-level failures → clear everything from PTK forward
    "PerceptionExtraction":  ("ptk_foundation", "ptk_foundation_progress",
                              "method_results", "claim_bundles", "claim_bundle_progress"),
    "TextCondition":         ("ptk_foundation", "ptk_foundation_progress",
                              "method_results", "claim_bundles", "claim_bundle_progress"),
    "KnowledgeLibrarian":    ("ptk_foundation", "ptk_foundation_progress",
                              "method_results", "claim_bundles", "claim_bundle_progress"),
    "PTKFoundationCritic":   ("ptk_foundation", "ptk_foundation_progress",
                              "method_results", "claim_bundles", "claim_bundle_progress"),
    # Method-level failures → clear methods and downstream
    "MethodPlanner":         ("method_results", "claim_bundles", "claim_bundle_progress"),
    # Claim-level failures → clear claims only
    "ClaimExtraction":       ("claim_bundles", "claim_bundle_progress"),
    "ClaimVerifyStructure":  ("claim_bundles", "claim_bundle_progress"),
    # Downstream (no persistent cache) → nothing to clear
    "NodeInduction":         (),
    "SolutionGrouper":       (),
    "EvidenceBinder":        (),
    "ProblemStructureValidation": ("claim_bundles", "claim_bundle_progress"),
    "FinalCoTValidation":    (),
    "TraceMapper":           (),
}

# Stages that failed in sub-graph nodes (method internal agents)
# map them up to their parent cache level
_SUBGRAPH_AGENT_PARENT = {
    "generate_cot":   "method_results",
    "answer_check":   "method_results",
    "verify_round_0": "method_results",
    "polish_round_1": "method_results",
    "verify_round_1": "method_results",
    "polish_round_2": "method_results",
    "verify_round_2": "method_results",
    "polish_round_3": "method_results",
    "verify_round_3": "method_results",
    "finalize_method": "method_results",
}


def _load_local_env() -> None:
    """Load pipeline2.local.env into the current process environment."""
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pipeline2 smart repair: retry failed problems from their failure point.")
    parser.add_argument("--config", required=True, help="pipeline2 YAML config path")
    parser.add_argument("--batch-id", required=True, help="Existing batch id to repair")
    parser.add_argument("--list-errors", action="store_true", help="Only list errors, don't repair")
    return parser.parse_args()


# ── helpers ──────────────────────────────────────────────────────────────

def _parse_stage_from_error(error_message: str) -> Optional[str]:
    """Extract the [AgentName] from an error message like '[ClaimVerifyStructure] LLM ...'."""
    if not error_message:
        return None
    match = re.match(r"^\[([^\]]+)\]", error_message.strip())
    if match:
        return match.group(1)
    return None


def _cache_stage_dirs(runtime_dir: Path, batch_id: str, problem_id: str, stage: str) -> List[Path]:
    """Return all cache dir paths for a given cache stage and problem."""
    stage_dir = runtime_dir / "stage_cache" / batch_id / problem_id / stage
    if not stage_dir.exists() or not stage_dir.is_dir():
        return []
    return [p for p in stage_dir.iterdir() if p.is_dir() or p.suffix == ".json"]


def _clear_cache(stage_cache_root: Path, cache_stages: Tuple[str, ...]) -> int:
    """Delete all files/dirs under the given cache stage dirs. Returns count of items removed."""
    removed = 0
    for stage in cache_stages:
        stage_dir = stage_cache_root / stage
        if not stage_dir.exists():
            continue
        for item in list(stage_dir.iterdir()):
            if item.is_dir():
                for sub in item.iterdir():
                    sub.unlink(missing_ok=True)
                    removed += 1
                item.rmdir()
                removed += 1
            else:
                item.unlink(missing_ok=True)
                removed += 1
        # Remove the empty stage dir
        try:
            stage_dir.rmdir()
        except OSError:
            pass
    return removed


def _list_error_files(output_root: Path, batch_id: str) -> List[Path]:
    """List problem_error files for the given batch."""
    error_dir = output_root / "problem_errors"
    if not error_dir.exists():
        return []
    return sorted(error_dir.glob("*.json"))


# ── main repair logic ────────────────────────────────────────────────────

def repair_batch(config_path: str, batch_id: str, list_only: bool = False) -> Dict:
    _load_local_env()
    config = Pipeline2Config.from_yaml(config_path)
    ctx = initialize_runtime(config, PROJECT_ROOT)

    error_files = _list_error_files(ctx.output_root, batch_id)
    if not error_files:
        print(f"[repair] No problem errors found for batch `{batch_id}`. Nothing to repair.")
        return {"batch_id": batch_id, "repaired": 0, "cleared_stages": 0}

    stage_cache_root = ctx.runtime_dir / "stage_cache" / batch_id
    total_cleared = 0
    repaired_problems = 0

    for err_file in error_files:
        problem_id = err_file.stem
        error_data = json.loads(err_file.read_text(encoding="utf-8"))
        error_msg = error_data.get("error_message", "") or ""

        # Parse the agent stage from the error message
        agent_stage = _parse_stage_from_error(error_msg)

        # Determine cache stages to clear
        cache_stages = _resolve_cache_stages(agent_stage)

        if list_only:
            print(f"  [error] {problem_id}: stage={agent_stage or 'unknown'} "
                  f"cache_to_clear={cache_stages or 'none'} "
                  f"error_type={error_data.get('error_type','?')}")
            continue

        # Clear cache
        problem_cache_root = stage_cache_root / problem_id
        if cache_stages and problem_cache_root.exists():
            n = _clear_cache(problem_cache_root, cache_stages)
            total_cleared += n

        # Delete the error file so pipeline retries
        err_file.unlink(missing_ok=True)
        repaired_problems += 1

        print(f"  [repair] {problem_id}: stage={agent_stage or 'unknown'}, "
              f"cleared={cache_stages or 'none'} ({n} items), error_file=deleted")

    if list_only:
        return {"batch_id": batch_id, "error_count": len(error_files)}

    print(f"\n[repair] Repaired {repaired_problems} problems, cleared {total_cleared} cache items.")

    # ── Clear langgraph checkpoint so the batch graph re-runs ──
    # Without this, the checkpointer returns the cached "complete" state and skips execution.
    _clear_checkpoint(ctx.checkpoint_db_path)
    print(f"[repair] Checkpoint cleared: {ctx.checkpoint_db_path}")
    print(f"[repair] Now running full annotation pipeline with batch_id=`{batch_id}`...\n")

    # ── Run the full annotation pipeline ──
    # This reuses existing stage cache for completed stages and re-runs from failure points
    result = run_annotation_pipeline(config, PROJECT_ROOT, batch_id=batch_id)

    # Report results
    completed = len(result.get("problems", []))
    failed = len(result.get("failed_problems", []))
    new_errors = _list_error_files(ctx.output_root, batch_id)
    print(f"\n[repair-done] batch_id={batch_id} completed={completed} failed={failed} new_errors={len(new_errors)}")
    return {
        "batch_id": batch_id,
        "repaired": repaired_problems,
        "cleared_stages": total_cleared,
        "completed": completed,
        "failed": failed,
        "remaining_errors": len(new_errors),
    }


def _resolve_cache_stages(agent_stage: Optional[str]) -> Tuple[str, ...]:
    """Map an agent stage name to the cache stages that need clearing."""
    if agent_stage is None:
        # Unknown → clear all cache for safety
        return ("ptk_foundation", "ptk_foundation_progress",
                "method_results", "claim_bundles", "claim_bundle_progress")

    # Check explicit mapping
    cache = _AGENT_CACHE_CLEAR.get(agent_stage)
    if cache is not None:
        return cache

    # Check sub-graph stages (method internal)
    parent = _SUBGRAPH_AGENT_PARENT.get(agent_stage)
    if parent == "method_results":
        return ("method_results", "claim_bundles", "claim_bundle_progress")

    # Unknown agent → clear all cache for safety
    return ("ptk_foundation", "ptk_foundation_progress",
            "method_results", "claim_bundles", "claim_bundle_progress")


def _clear_checkpoint(checkpoint_db_path: Path) -> None:
    """Close the shared checkpointer and delete the checkpoint SQLite database."""
    try:
        close_shared_checkpointer()
    except Exception:
        pass
    try:
        if checkpoint_db_path.exists():
            checkpoint_db_path.unlink()
    except OSError as e:
        print(f"[repair] Warning: could not delete checkpoint DB: {e}")
    # Also clean up WAL and SHM files
    for suffix in ("-wal", "-shm"):
        aux = checkpoint_db_path.with_suffix(checkpoint_db_path.suffix + suffix)
        if aux.exists():
            try:
                aux.unlink()
            except OSError:
                pass


def main() -> None:
    args = parse_args()
    result = repair_batch(args.config, args.batch_id, list_only=args.list_errors)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
