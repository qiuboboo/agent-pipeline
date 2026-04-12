#!/usr/bin/env bash
set -euo pipefail
source ~/.bashrc >/dev/null 2>&1 || true
cd /root/.openclaw/workspace/agent-pipeline
exec python3 run_pipeline.py --config configs/geometry3k.yaml
