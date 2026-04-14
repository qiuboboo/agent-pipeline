from __future__ import annotations

import os
import subprocess
import sys
import traceback
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

from benchmarkallinone.pipeline2.config import Pipeline2Config
from benchmarkallinone.pipeline2.pipeline import initialize_runtime, _loaded_problems_to_runtime, _run_single_problem
from benchmarkallinone.pipeline2.ready_loader import discover_ready_problems

cfg = Pipeline2Config.from_yaml(str(PROJECT_ROOT / 'src/benchmarkallinone/pipeline2/configs/live_smoke_pipeline2.yaml'))
ctx = initialize_runtime(cfg, PROJECT_ROOT)
problems = discover_ready_problems(
    ready_root=ctx.ready_root,
    workspace_root=PROJECT_ROOT,
    include_manual_review=cfg.runtime.include_manual_review,
    max_problems=cfg.runtime.max_problems,
    max_images=cfg.runtime.max_images_per_problem,
)
print('READY_ROOT', ctx.ready_root)
print('LOADED', len(problems))
rt = _loaded_problems_to_runtime(problems)
print('RUNTIME_PROBLEMS', len(rt))
try:
    result = _run_single_problem('debug_live_smoke', rt[0])
    print('RESULT_KEYS', sorted(result.keys()))
    print('DONE')
except Exception as exc:
    print('EXC_TYPE', type(exc).__name__)
    print('EXC', exc)
    traceback.print_exc()
    raise
