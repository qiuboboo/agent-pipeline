#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

CONFIG_PATH="${EEE_BENCH_BATCH_CONFIG:-./configs/eee_bench_20_batch.yaml}"
OUTPUT_ROOT="${EEE_BENCH_BATCH_OUTPUT_ROOT:-outputs/eee_bench_20_batches}"
LOG_DIR="${EEE_BENCH_BATCH_LOG_DIR:-./logs}"
BATCH_SIZE="${EEE_BENCH_BATCH_SIZE:-20}"
START_OFFSET="${EEE_BENCH_START_OFFSET:-0}"
END_OFFSET="${EEE_BENCH_END_OFFSET:-300}"
BASE_URL="${OPENAI_BASE_URL:-http://9854399.xyz:8888/v1}"
MODEL_NAME="${OPENAI_MODEL:-gpt-5.4}"
REASONING_EFFORT="${OPENAI_REASONING_EFFORT:-high}"
API_KEY="${OPENAI_API_KEY_AGENT:-${OPENAI_API_KEY_FOR_AGENT:-${OPENAI_API_KEY:-${EEE_BENCH_OPENAI_API_KEY:-}}}}"
PYTHON_BIN="${EEE_BENCH_PYTHON_BIN:-D:/anaconda3/envs/agent/python.exe}"

if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "ERROR: config not found: $CONFIG_PATH" >&2
  exit 1
fi

if [[ -z "$API_KEY" ]]; then
  echo "ERROR: missing API key. Set OPENAI_API_KEY_AGENT, OPENAI_API_KEY_FOR_AGENT, OPENAI_API_KEY, or EEE_BENCH_OPENAI_API_KEY." >&2
  exit 1
fi

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "ERROR: python not executable: $PYTHON_BIN" >&2
  exit 1
fi

mkdir -p "$LOG_DIR"
mkdir -p "$OUTPUT_ROOT"

for ((start=START_OFFSET; start<END_OFFSET; start+=BATCH_SIZE)); do
  end=$((start + BATCH_SIZE))
  if (( end > END_OFFSET )); then
    end=$END_OFFSET
  fi

  split="test[${start}:${end}]"
  batch_tag="${start}_${end}"
  temp_config="$LOG_DIR/eee_bench_batch_${batch_tag}.yaml"
  log_file="$LOG_DIR/eee_bench_batch_${batch_tag}.log"

  "$PYTHON_BIN" - "$CONFIG_PATH" "$temp_config" "$split" <<'PY'
import sys
from pathlib import Path
import yaml

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
split = sys.argv[3]
raw = yaml.safe_load(src.read_text(encoding='utf-8')) or {}
raw.setdefault('runtime', {})
raw['runtime']['batch_id_prefix'] = f"benchmarkallinone-eee-bench20-{split.replace('[', '_').replace(':', '_').replace(']', '')}"
datasets = raw.get('datasets') or []
if not datasets:
    raise SystemExit('No datasets configured')
datasets[0]['split'] = split
dst.write_text(yaml.safe_dump(raw, allow_unicode=True, sort_keys=False), encoding='utf-8')
PY

  echo "[EEE-Bench] Running batch $split"
  echo "[EEE-Bench] Temp config: $temp_config"
  echo "[EEE-Bench] Log: $log_file"

  PYTHONUNBUFFERED=1 "$PYTHON_BIN" -u -m src.benchmarkallinone.pipeline \
    --config "$temp_config" \
    --base-url "$BASE_URL" \
    --api-key "$API_KEY" \
    --model "$MODEL_NAME" \
    --reasoning-effort "$REASONING_EFFORT" 2>&1 | tee "$log_file"
done
