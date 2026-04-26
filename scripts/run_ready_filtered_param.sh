#!/usr/bin/env bash
set -Eeuo pipefail

# Parameterized ready-root filter + pipeline2 runner.
#
# Goal: from a normal READY tree, build a symlink-filtered READY tree and run pipeline2.
# You should only need to edit/export environment variables, not edit YAML.
#
# Default excluded dataset directory basenames/patterns:
#   - cmmmath / cmm_math
#   - msearth / msearth_* / msearth-*
#   - scemqa exactly (plain no-suffix SCEMQA); scemqa_biology/scemqa_chemistry/scemqa_math are kept
#
# Minimal usage from agent-pipeline repo root:
#   export PIPELINE2_SOURCE_READY_ROOT=/path/to/ready
#   export ANNOTATION_API_KEY=...
#   bash scripts/run_ready_filtered_param.sh
#
# Typical 20-sample / 5-worker msutools run:
#   PIPELINE2_SOURCE_READY_ROOT=/path/to/ready \
#   PIPELINE2_MAX_PROBLEMS=20 \
#   PIPELINE2_MAX_PROBLEM_WORKERS=5 \
#   ANNOTATION_API_KEY=... \
#   ANNOTATION_API_BASE_URL=https://www.msutools.cn \
#   ANNOTATION_MODEL=gpt-5.5 \
#   ANNOTATION_REASONING_EFFORT=high \
#   ANNOTATION_API_MODE=responses \
#   bash scripts/run_ready_filtered_param.sh
#
# Optional:
#   PIPELINE2_DRY_RUN=1                    # build filtered tree and print config, then exit
#   PIPELINE2_RUN_ID=my_run_name           # controls default output/checkpoint names
#   PIPELINE2_EXCLUDE_DATASETS=a,b,c       # extra exact dataset directory basenames to exclude
#   PIPELINE2_EXCLUDE_PREFIXES=foo,bar_    # extra normalized basename prefixes to exclude
#   PIPELINE2_LOAD_LOCAL_ENV=1             # opt-in source of pipeline2.local.env; default 0 to avoid accidental override

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if [[ "${PIPELINE2_SOURCE_BASHRC:-0}" == "1" && -f "$HOME/.bashrc" ]]; then
  set +u
  source "$HOME/.bashrc" >/dev/null 2>&1 || true
  set -u
fi

if [[ "${PIPELINE2_LOAD_LOCAL_ENV:-0}" == "1" && -f "src/benchmarkallinone/pipeline2/configs/pipeline2.local.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "src/benchmarkallinone/pipeline2/configs/pipeline2.local.env"
  set +a
fi

: "${PIPELINE2_RUN_ID:=ready_filtered_$(date +%Y%m%d_%H%M%S)}"
: "${PIPELINE2_SOURCE_READY_ROOT:=${READY_ROOT:-ready}}"
: "${PIPELINE2_FILTERED_READY_ROOT:=tmp/${PIPELINE2_RUN_ID}_ready}"
: "${PIPELINE2_OUTPUT_ROOT:=pipeline2/outputs_${PIPELINE2_RUN_ID}}"
: "${PIPELINE2_CHECKPOINT_DB_PATH:=pipeline2/runtime/pipeline_langgraph_${PIPELINE2_RUN_ID}.sqlite}"
: "${PIPELINE2_CONFIG_TEMPLATE:=src/benchmarkallinone/pipeline2/configs/ready_filtered_param_template.yaml}"
: "${PIPELINE2_RENDERED_CONFIG:=tmp/${PIPELINE2_RUN_ID}.yaml}"

: "${PIPELINE2_INCLUDE_MANUAL_REVIEW:=true}"
: "${PIPELINE2_MAX_PROBLEMS:=0}"
: "${PIPELINE2_MAX_PROBLEM_WORKERS:=19}"
: "${PIPELINE2_MAX_IMAGES_PER_PROBLEM:=3}"
: "${PIPELINE2_SAVE_RUNTIME_SNAPSHOTS:=true}"
: "${PIPELINE2_SAVE_PROBLEM_BUNDLES:=true}"
: "${PIPELINE2_ENABLE_TRACE_PATCH_WRITES:=true}"
: "${PIPELINE2_ENABLE_PROBLEM_STRUCTURE_VALIDATION:=true}"
: "${PIPELINE2_FAIL_ON_PROBLEM_STRUCTURE_VALIDATION:=true}"
: "${PIPELINE2_STAGE_RETRY_ATTEMPTS:=3}"
: "${PIPELINE2_STAGE_RETRY_BACKOFF_SECONDS:=1.0}"
: "${PIPELINE2_PROBLEM_RETRY_ATTEMPTS:=10}"
: "${PIPELINE2_CONTINUE_ON_PROBLEM_ERROR:=true}"
: "${PIPELINE2_METHOD_SCORE_THRESHOLD_LOW:=0.33}"
: "${PIPELINE2_METHOD_SCORE_THRESHOLD_HIGH:=0.67}"
: "${PIPELINE2_NOVELTY_TOTAL_THRESHOLD:=0.55}"
: "${PIPELINE2_NOVELTY_REQUIRED_THRESHOLD:=0.50}"

: "${ANNOTATION_API_BASE_URL:=https://www.msutools.cn}"
: "${ANNOTATION_MODEL:=gpt-5.5}"
: "${ANNOTATION_REASONING_EFFORT:=high}"
: "${ANNOTATION_API_MODE:=responses}"
: "${ANNOTATION_REQUIRES_OPENAI_AUTH:=true}"
: "${ANNOTATION_DISABLE_RESPONSE_STORAGE:=true}"
: "${ANNOTATION_TEMPERATURE:=0.1}"
: "${ANNOTATION_TIMEOUT_SECONDS:=180}"

export PIPELINE2_RUN_ID PIPELINE2_SOURCE_READY_ROOT PIPELINE2_FILTERED_READY_ROOT PIPELINE2_OUTPUT_ROOT PIPELINE2_CHECKPOINT_DB_PATH
export PIPELINE2_CONFIG_TEMPLATE PIPELINE2_RENDERED_CONFIG
export PIPELINE2_INCLUDE_MANUAL_REVIEW PIPELINE2_MAX_PROBLEMS PIPELINE2_MAX_PROBLEM_WORKERS PIPELINE2_MAX_IMAGES_PER_PROBLEM
export PIPELINE2_SAVE_RUNTIME_SNAPSHOTS PIPELINE2_SAVE_PROBLEM_BUNDLES PIPELINE2_ENABLE_TRACE_PATCH_WRITES
export PIPELINE2_ENABLE_PROBLEM_STRUCTURE_VALIDATION PIPELINE2_FAIL_ON_PROBLEM_STRUCTURE_VALIDATION
export PIPELINE2_STAGE_RETRY_ATTEMPTS PIPELINE2_STAGE_RETRY_BACKOFF_SECONDS PIPELINE2_PROBLEM_RETRY_ATTEMPTS PIPELINE2_CONTINUE_ON_PROBLEM_ERROR
export PIPELINE2_METHOD_SCORE_THRESHOLD_LOW PIPELINE2_METHOD_SCORE_THRESHOLD_HIGH PIPELINE2_NOVELTY_TOTAL_THRESHOLD PIPELINE2_NOVELTY_REQUIRED_THRESHOLD
export ANNOTATION_API_BASE_URL ANNOTATION_MODEL ANNOTATION_REASONING_EFFORT ANNOTATION_API_MODE
export ANNOTATION_REQUIRES_OPENAI_AUTH ANNOTATION_DISABLE_RESPONSE_STORAGE ANNOTATION_TEMPERATURE ANNOTATION_TIMEOUT_SECONDS

if [[ -z "${ANNOTATION_API_KEY:-}" ]]; then
  if [[ -n "${OPENAI_API_KEY:-}" ]]; then
    export ANNOTATION_API_KEY="$OPENAI_API_KEY"
  else
    echo "ERROR: ANNOTATION_API_KEY is not set, and OPENAI_API_KEY is also empty." >&2
    exit 2
  fi
fi
export ANNOTATION_API_KEY

if [[ ! -d "$PIPELINE2_SOURCE_READY_ROOT" ]]; then
  echo "ERROR: source ready root not found: $PIPELINE2_SOURCE_READY_ROOT" >&2
  exit 2
fi

if [[ ! -x ".venv/bin/python" ]]; then
  echo "ERROR: .venv/bin/python not found or not executable. Run from a prepared agent-pipeline checkout." >&2
  exit 2
fi

rm -rf "$PIPELINE2_FILTERED_READY_ROOT"
mkdir -p "$PIPELINE2_FILTERED_READY_ROOT" "$(dirname "$PIPELINE2_RENDERED_CONFIG")"

.venv/bin/python - <<'PY'
from pathlib import Path
import os
import shutil

source = Path(os.environ["PIPELINE2_SOURCE_READY_ROOT"]).resolve()
dest = Path(os.environ["PIPELINE2_FILTERED_READY_ROOT"]).resolve()
extra_exact = {
    item.strip().lower().replace("-", "_")
    for item in os.environ.get("PIPELINE2_EXCLUDE_DATASETS", "").split(",")
    if item.strip()
}
extra_prefixes = tuple(
    item.strip().lower().replace("-", "_")
    for item in os.environ.get("PIPELINE2_EXCLUDE_PREFIXES", "").split(",")
    if item.strip()
)

excluded = []
kept = []

def is_excluded(parts):
    for part in parts:
        token = part.replace("-", "_")
        if token in {"cmmmath", "cmm_math"}:
            return "cmmmath/cmm_math"
        if token == "msearth" or token.startswith("msearth_"):
            return "msearth"
        if token in extra_exact:
            return "extra_exact"
        if extra_prefixes and any(token.startswith(prefix) for prefix in extra_prefixes):
            return "extra_prefix"
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

.venv/bin/python - <<'PY'
from pathlib import Path
import os
import re

template = Path(os.environ["PIPELINE2_CONFIG_TEMPLATE"])
out = Path(os.environ["PIPELINE2_RENDERED_CONFIG"])
text = template.read_text(encoding="utf-8")

def repl(match):
    name = match.group(1)
    if name not in os.environ:
        raise SystemExit(f"missing environment variable for config template: {name}")
    return os.environ[name]

rendered = re.sub(r"\$\{([A-Z0-9_]+)\}", repl, text)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(rendered, encoding="utf-8")
print(f"[config] rendered={out}")
PY

sample_count="$(find -L "$PIPELINE2_FILTERED_READY_ROOT" -path '*/samples/*.json' -type f | wc -l | tr -d ' ')"
echo "[ready-filter] filtered_sample_count=$sample_count"
echo "[run] run_id=$PIPELINE2_RUN_ID"
echo "[run] config=$PIPELINE2_RENDERED_CONFIG"
echo "[run] ready_root=$PIPELINE2_FILTERED_READY_ROOT"
echo "[run] output_root=$PIPELINE2_OUTPUT_ROOT"
echo "[run] checkpoint_db_path=$PIPELINE2_CHECKPOINT_DB_PATH"
echo "[run] max_problems=$PIPELINE2_MAX_PROBLEMS workers=$PIPELINE2_MAX_PROBLEM_WORKERS model=$ANNOTATION_MODEL effort=$ANNOTATION_REASONING_EFFORT api_mode=$ANNOTATION_API_MODE base_url=$ANNOTATION_API_BASE_URL"

if [[ "${PIPELINE2_DRY_RUN:-0}" == "1" ]]; then
  echo "[dry-run] rendered config preview:"
  sed -n '1,120p' "$PIPELINE2_RENDERED_CONFIG"
  echo "[dry-run] exiting before annotation"
  exit 0
fi

export PYTHONPATH=src
exec .venv/bin/python run_pipeline2.py annotate --config "$PIPELINE2_RENDERED_CONFIG"
