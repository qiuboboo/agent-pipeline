from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / 'src/benchmarkallinone/pipeline2/configs/pipeline2.local.env'
SRC_ROOT = PROJECT_ROOT / 'src'
VENV_SITE_PACKAGES = PROJECT_ROOT / '.venv/lib/python3.12/site-packages'

if VENV_SITE_PACKAGES.exists() and str(VENV_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_SITE_PACKAGES))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

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

from benchmarkallinone.pipeline2.main import main

if __name__ == '__main__':
    sys.argv = [
        'run_pipeline2_with_local_env.py',
        'annotate',
        '--config',
        'src/benchmarkallinone/pipeline2/configs/live_smoke_pipeline2.yaml',
    ]
    main()
