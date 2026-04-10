#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

CONFIG_PATH="${SCEMQA_CONFIG_PATH:-./configs/scemqa_parallel_20.yaml}"
BASE_URL="${OPENAI_BASE_URL:-https://synai996.space/v1}"
MODEL_NAME="${OPENAI_MODEL:-gpt-5.4}"
REASONING_EFFORT="${OPENAI_REASONING_EFFORT:-high}"
API_KEY="${OPENAI_API_KEY:-${SCEMQA_OPENAI_API_KEY:-sk-uCj6YwOFEkv0YGfJQwVMLUMgXIcWZRUJqHGmMiYlPeQZzFVi}}"

if [[ $# -ge 1 && -n "$1" ]]; then
  CONFIG_PATH="$1"
fi

if [[ $# -ge 2 && -n "$2" ]]; then
  API_KEY="$2"
fi

if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "ERROR: config not found: $CONFIG_PATH" >&2
  exit 1
fi

if [[ -z "$API_KEY" ]]; then
  echo "ERROR: missing API key. Set OPENAI_API_KEY or SCEMQA_OPENAI_API_KEY, or pass the API key as the second argument." >&2
  exit 1
fi

echo "[SCEMQA] Installing dependencies..."
python3 -m pip install -r ./requirements.txt

echo "[SCEMQA] Running full collection + cleaning pipeline..."
python3 ./run_pipeline.py \
  --config "$CONFIG_PATH" \
  --base-url "$BASE_URL" \
  --api-key "$API_KEY" \
  --model "$MODEL_NAME" \
  --reasoning-effort "$REASONING_EFFORT"

OUTPUT_ROOT="$(python3 - "$CONFIG_PATH" <<'PY'
import sys
from pathlib import Path
import yaml

config_path = Path(sys.argv[1])
raw = yaml.safe_load(config_path.read_text(encoding='utf-8')) or {}
print(raw.get('runtime', {}).get('output_root', 'outputs/scemqa_parallel_20'))
PY
)"

LATEST_RUN="$(ls -td "$OUTPUT_ROOT"/run_* 2>/dev/null | head -n 1 || true)"

if [[ -n "$LATEST_RUN" ]]; then
  echo "[SCEMQA] Latest run directory: $LATEST_RUN"
  echo "[SCEMQA] Summary file: $LATEST_RUN/summary.json"
  if [[ -f "$LATEST_RUN/datasets/scemqa/summary.json" ]]; then
    echo "[SCEMQA] Dataset summary: $LATEST_RUN/datasets/scemqa/summary.json"
  fi
else
  echo "[SCEMQA] Run finished, but no run_* directory was found under $OUTPUT_ROOT" >&2
fi
