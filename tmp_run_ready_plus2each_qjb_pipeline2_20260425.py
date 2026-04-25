#!/usr/bin/env python3
import subprocess
import sys

cmd = (
    "source ~/.bashrc >/dev/null 2>&1; "
    "set -a; source src/benchmarkallinone/pipeline2/configs/pipeline2.local.env; set +a; "
    ".venv/bin/python run_pipeline2.py annotate --config /root/.openclaw/workspace/agent-pipeline/tmp_ready_plus2each_qjb_pipeline2_20260425.yaml"
)
completed = subprocess.run(["bash", "-lc", cmd], cwd="/root/.openclaw/workspace/agent-pipeline")
sys.exit(completed.returncode)
