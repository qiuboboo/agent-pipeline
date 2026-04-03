#!/usr/bin/env bash
set -euo pipefail

WORKDIR="/root/.openclaw/workspace/agent-pipeline"
LOG_FILE="$WORKDIR/.runlogs/eee_bench_autochain_0500_0700.log"
TARGET_PID_FILE="$WORKDIR/.runlogs/eee_bench_current.pid"

CURRENT_PATTERN='python3 scripts/eee_bench_batch_launcher.py --start 320 --end 500 --step 20 --api-mode responses'
NEXT_CMD='python3 scripts/eee_bench_batch_launcher.py --start 500 --end 700 --step 20 --base-url ${CUSTOM_OPENAI_BASE_URL:-https://cf.cuylerchen.uk/openai/v1} --api-key "${CUSTOM_OPENAI_API_KEY:?CUSTOM_OPENAI_API_KEY is required}" --api-mode ${CUSTOM_OPENAI_API_MODE:-responses}'

mkdir -p "$WORKDIR/.runlogs"

echo "[$(date '+%F %T')] watcher start" >> "$LOG_FILE"
echo "[$(date '+%F %T')] waiting current job to finish" >> "$LOG_FILE"

while pgrep -af "$CURRENT_PATTERN" >/dev/null 2>&1; do
  sleep 60
done

echo "[$(date '+%F %T')] detected current job finished" >> "$LOG_FILE"

if pgrep -af "python3 scripts/eee_bench_batch_launcher.py --start 500 --end 700 --step 20" >/dev/null 2>&1; then
  echo "[$(date '+%F %T')] next job already running, exit" >> "$LOG_FILE"
  exit 0
fi

cd "$WORKDIR"
nohup bash -lc "$NEXT_CMD" >> "$WORKDIR/.runlogs/eee_bench_responses_0500_0700.log" 2>&1 &
echo $! > "$TARGET_PID_FILE"
echo "[$(date '+%F %T')] started next job pid=$(cat "$TARGET_PID_FILE")" >> "$LOG_FILE"
