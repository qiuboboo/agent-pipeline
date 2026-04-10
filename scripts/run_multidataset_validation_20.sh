#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

CONFIG_PATH="${MULTIDATASET_CONFIG_PATH:-./configs/agent_multidataset_validation_20.yaml}"
BASE_URL="${OPENAI_BASE_URL:-https://synai996.space/v1}"
MODEL_NAME="${OPENAI_MODEL:-gpt-5.4}"
REASONING_EFFORT="${OPENAI_REASONING_EFFORT:-high}"
API_KEY="${OPENAI_API_KEY:-${MULTIDATASET_OPENAI_API_KEY:-sk-uCj6YwOFEkv0YGfJQwVMLUMgXIcWZRUJqHGmMiYlPeQZzFVi}}"

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
  print -n "请输入 OpenAI 兼容 API Key: "
  read -rs API_KEY
  echo
fi

if [[ -z "$API_KEY" ]]; then
  echo "ERROR: missing API key." >&2
  exit 1
fi

echo "[MultiDataset20] Installing dependencies..."
python3 -m pip install -r ./requirements.txt

OUTPUT_ROOT="$(python3 - "$CONFIG_PATH" <<'PY'
import sys
from pathlib import Path
import yaml
config_path = Path(sys.argv[1])
raw = yaml.safe_load(config_path.read_text(encoding='utf-8')) or {}
print(raw.get('runtime', {}).get('output_root', 'outputs/agent_multidataset_validation_20'))
PY
)"

LOG_DIR="$OUTPUT_ROOT/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/run_$(date +%Y%m%dT%H%M%S).log"

echo "[MultiDataset20] Config: $CONFIG_PATH"
echo "[MultiDataset20] Output root: $OUTPUT_ROOT"
echo "[MultiDataset20] Live log: $LOG_FILE"
echo "[MultiDataset20] Running full collection + cleaning pipeline..."

PYTHONUNBUFFERED=1 python3 -u ./run_pipeline.py \
  --config "$CONFIG_PATH" \
  --base-url "$BASE_URL" \
  --api-key "$API_KEY" \
  --model "$MODEL_NAME" \
  --reasoning-effort "$REASONING_EFFORT" 2>&1 | tee "$LOG_FILE"

LATEST_RUN="$(ls -td "$OUTPUT_ROOT"/run_* 2>/dev/null | head -n 1 || true)"

if [[ -n "$LATEST_RUN" ]]; then
  echo "[MultiDataset20] Latest run directory: $LATEST_RUN"
  echo "[MultiDataset20] Summary file: $LATEST_RUN/summary.json"
else
  echo "[MultiDataset20] Run finished, but no run_* directory was found under $OUTPUT_ROOT" >&2
fi
