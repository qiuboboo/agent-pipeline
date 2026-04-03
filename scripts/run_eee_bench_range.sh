#!/usr/bin/env bash
set -euo pipefail

START="${1:-}"
END="${2:-}"
STEP="${3:-20}"

if [[ -z "$START" || -z "$END" ]]; then
  echo "Usage: bash scripts/run_eee_bench_range.sh <start> <end> [step]"
  echo "Example: bash scripts/run_eee_bench_range.sh 320 500 20"
  exit 1
fi

if [[ -z "${CUSTOM_OPENAI_API_KEY:-}" ]]; then
  echo "ERROR: CUSTOM_OPENAI_API_KEY is not set"
  exit 1
fi

BASE_URL="${CUSTOM_OPENAI_BASE_URL:-https://cf.cuylerchen.uk/openai/v1}"
API_MODE="${CUSTOM_OPENAI_API_MODE:-responses}"

mkdir -p .runlogs
LOG_FILE=".runlogs/eee_bench_${START}_${END}.responses.log"

echo "[run_eee_bench_range] start=$START end=$END step=$STEP"
echo "[run_eee_bench_range] base_url=$BASE_URL api_mode=$API_MODE"
echo "[run_eee_bench_range] log=$LOG_FILE"

nohup python3 scripts/eee_bench_batch_launcher.py \
  --start "$START" \
  --end "$END" \
  --step "$STEP" \
  --base-url "$BASE_URL" \
  --api-key "$CUSTOM_OPENAI_API_KEY" \
  --api-mode "$API_MODE" \
  > "$LOG_FILE" 2>&1 &

PID=$!
echo "[run_eee_bench_range] pid=$PID"
echo "[run_eee_bench_range] tail -f $LOG_FILE"
