#!/usr/bin/env bash
set -Eeuo pipefail

# Build a filtered READY root and run pipeline2 immediately with 19 workers.
#
# Excluded dataset directory basenames:
#   - cmmmath / cmm_math
#   - msearth / msearth_* / msearth-*
#   - scemqa exactly (the plain no-suffix SCEMQA dataset)
#
# Usage on another server from the agent-pipeline repo root:
#   export PIPELINE2_SOURCE_READY_ROOT=/path/to/ready
#   export ANNOTATION_API_KEY=...
#   export ANNOTATION_API_BASE_URL=https://www.msutools.cn
#   export ANNOTATION_MODEL=gpt-5.5
#   export ANNOTATION_REASONING_EFFORT=high
#   export ANNOTATION_API_MODE=responses
#   bash scripts/run_ready_filtered_19w_exclude_cmmmath_msearth_scemqa_plain.sh
#
# Optional overrides:
#   PIPELINE2_FILTERED_READY_ROOT=/tmp/pipeline2_ready_filtered_19w
#   PIPELINE2_OUTPUT_ROOT=pipeline2/outputs_ready_filtered_19w_$(date +%Y%m%d_%H%M%S)
#   PIPELINE2_CHECKPOINT_DB_PATH=pipeline2/runtime/pipeline_langgraph_ready_filtered_19w.sqlite
#   PIPELINE2_CONFIG=src/benchmarkallinone/pipeline2/configs/ready_filtered_19w_exclude_cmmmath_msearth_scemqa_plain.yaml
#   PIPELINE2_DRY_RUN=1   # build filtered ready root and print counts, then exit before annotation

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if [[ -f "$HOME/.bashrc" ]]; then
  # Keep compatibility with the existing agent-pipeline environment convention.
  # Do this before strict unbound-variable-sensitive operations matter.
  set +u
  source "$HOME/.bashrc" >/dev/null 2>&1 || true
  set -u
fi

if [[ -f "src/benchmarkallinone/pipeline2/configs/pipeline2.local.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "src/benchmarkallinone/pipeline2/configs/pipeline2.local.env"
  set +a
fi

: "${PIPELINE2_SOURCE_READY_ROOT:=${READY_ROOT:-ready}}"
: "${PIPELINE2_FILTERED_READY_ROOT:=tmp/ready_filtered_19w_exclude_cmmmath_msearth_scemqa_plain}"
: "${PIPELINE2_OUTPUT_ROOT:=pipeline2/outputs_ready_filtered_19w_exclude_cmmmath_msearth_scemqa_plain}"
: "${PIPELINE2_CHECKPOINT_DB_PATH:=pipeline2/runtime/pipeline_langgraph_ready_filtered_19w_exclude_cmmmath_msearth_scemqa_plain.sqlite}"
: "${PIPELINE2_CONFIG:=src/benchmarkallinone/pipeline2/configs/ready_filtered_19w_exclude_cmmmath_msearth_scemqa_plain.yaml}"
: "${ANNOTATION_API_BASE_URL:=https://www.msutools.cn}"
: "${ANNOTATION_MODEL:=gpt-5.5}"
: "${ANNOTATION_REASONING_EFFORT:=high}"
: "${ANNOTATION_API_MODE:=responses}"

export PIPELINE2_SOURCE_READY_ROOT
export PIPELINE2_FILTERED_READY_ROOT
export PIPELINE2_OUTPUT_ROOT
export PIPELINE2_CHECKPOINT_DB_PATH
export PIPELINE2_CONFIG
export ANNOTATION_API_BASE_URL
export ANNOTATION_MODEL
export ANNOTATION_REASONING_EFFORT
export ANNOTATION_API_MODE

if [[ -z "${ANNOTATION_API_KEY:-}" ]]; then
  if [[ -n "${OPENAI_API_KEY:-}" ]]; then
    export ANNOTATION_API_KEY="$OPENAI_API_KEY"
  else
    echo "ERROR: ANNOTATION_API_KEY is not set, and OPENAI_API_KEY is also empty." >&2
    exit 2
  fi
fi

if [[ ! -d "$PIPELINE2_SOURCE_READY_ROOT" ]]; then
  echo "ERROR: source ready root not found: $PIPELINE2_SOURCE_READY_ROOT" >&2
  exit 2
fi

if [[ ! -x ".venv/bin/python" ]]; then
  echo "ERROR: .venv/bin/python not found or not executable. Run from a prepared agent-pipeline checkout." >&2
  exit 2
fi

rm -rf "$PIPELINE2_FILTERED_READY_ROOT"
mkdir -p "$PIPELINE2_FILTERED_READY_ROOT"

.venv/bin/python - <<'PY'
from pathlib import Path
import os
import shutil

source = Path(os.environ["PIPELINE2_SOURCE_READY_ROOT"]).resolve()
dest = Path(os.environ["PIPELINE2_FILTERED_READY_ROOT"]).resolve()

excluded = []
kept = []

def is_excluded(parts):
    # parts are lower-case path components relative to ready root.
    for part in parts:
        token = part.replace("-", "_")
        if token in {"cmmmath", "cmm_math"}:
            return "cmmmath/cmm_math"
        if token == "msearth" or token.startswith("msearth_"):
            return "msearth"
    if parts and parts[-1] == "scemqa":
        return "plain_scemqa"
    return ""

sample_dirs = sorted({p.parent for p in source.rglob("samples/*.json") if p.is_file()})
for sample_dir in sample_dirs:
    dataset_root = sample_dir.parent
    rel = dataset_root.relative_to(source)
    parts = tuple(part.lower() for part in rel.parts)
    reason = is_excluded(parts)
    if reason:
        excluded.append((str(rel), reason))
        continue

    target_dataset = dest / rel
    target_dataset.mkdir(parents=True, exist_ok=True)
    target_samples = target_dataset / "samples"
    if target_samples.exists() or target_samples.is_symlink():
        target_samples.unlink() if target_samples.is_symlink() else shutil.rmtree(target_samples)
    target_samples.symlink_to(sample_dir.resolve(), target_is_directory=True)

    artifact_dir = dataset_root / "artifacts"
    if artifact_dir.exists():
        target_artifacts = target_dataset / "artifacts"
        if target_artifacts.exists() or target_artifacts.is_symlink():
            target_artifacts.unlink() if target_artifacts.is_symlink() else shutil.rmtree(target_artifacts)
        target_artifacts.symlink_to(artifact_dir.resolve(), target_is_directory=True)

    kept.append(str(rel))

print(f"[ready-filter] source={source}")
print(f"[ready-filter] dest={dest}")
print(f"[ready-filter] kept_dataset_count={len(kept)} excluded_dataset_count={len(excluded)}")
if excluded:
    print("[ready-filter] excluded:")
    for rel, reason in excluded:
        print(f"  - {rel} ({reason})")
if not kept:
    raise SystemExit("[ready-filter] no datasets left after filtering")
PY

sample_count="$(find -L "$PIPELINE2_FILTERED_READY_ROOT" -path '*/samples/*.json' -type f | wc -l | tr -d ' ')"
echo "[ready-filter] filtered_sample_count=$sample_count"

echo "[run] config=$PIPELINE2_CONFIG"
echo "[run] ready_root=$PIPELINE2_FILTERED_READY_ROOT"
echo "[run] output_root=$PIPELINE2_OUTPUT_ROOT"
echo "[run] checkpoint_db_path=$PIPELINE2_CHECKPOINT_DB_PATH"
echo "[run] workers=19 model=$ANNOTATION_MODEL effort=$ANNOTATION_REASONING_EFFORT api_mode=$ANNOTATION_API_MODE base_url=$ANNOTATION_API_BASE_URL"

if [[ "${PIPELINE2_DRY_RUN:-0}" == "1" ]]; then
  echo "[dry-run] exiting before annotation"
  exit 0
fi

export PYTHONPATH=src
exec .venv/bin/python run_pipeline2.py annotate --config "$PIPELINE2_CONFIG"
