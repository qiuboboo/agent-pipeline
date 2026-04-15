from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path('/root/.openclaw/workspace/agent-pipeline')
ENV_PATH = PROJECT_ROOT / 'src/benchmarkallinone/pipeline2/configs/pipeline2.local.env'
SRC_ROOT = PROJECT_ROOT / 'src'
VENV_PYTHON = PROJECT_ROOT / '.venv/bin/python'
TARGET_CONFIG = PROJECT_ROOT / 'src/benchmarkallinone/pipeline2/configs/new_ready_single_eeebench00001.yaml'

shell_env: dict[str, str] = {}
proc = subprocess.run(
    ['bash', '-lc', 'source ~/.bashrc >/dev/null 2>&1; env'],
    capture_output=True,
    text=True,
    check=True,
)
for line in proc.stdout.splitlines():
    if '=' not in line:
        continue
    key, value = line.split('=', 1)
    shell_env[key] = value
os.environ.update(shell_env)

for line in ENV_PATH.read_text(encoding='utf-8').splitlines():
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    key, value = line.split('=', 1)
    value = value.strip()
    for env_key, env_value in os.environ.items():
        value = value.replace('${' + env_key + '}', env_value)
    os.environ[key.strip()] = value

cmd = [
    str(VENV_PYTHON),
    str(PROJECT_ROOT / 'run_pipeline2.py'),
    'annotate',
    '--config',
    str(TARGET_CONFIG),
    '--batch-id',
    'debug_new_ready_eeebench00001',
]
result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
sys.exit(result.returncode)
