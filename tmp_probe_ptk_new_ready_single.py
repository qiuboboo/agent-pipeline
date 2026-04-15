from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

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

from benchmarkallinone.pipeline2.annotation_modules import (
    _extract_ptk_once,
    critique_ptk_foundation,
    polish_ptk_foundation,
)
from benchmarkallinone.pipeline2.clients import ModelRouter
from benchmarkallinone.pipeline2.config import Pipeline2Config
from benchmarkallinone.pipeline2.ready_loader import discover_ready_problems


def main() -> int:
    config = Pipeline2Config.from_yaml(str(PROJECT_ROOT / 'src/benchmarkallinone/pipeline2/configs/new_ready_single_eeebench00001.yaml'))
    router = ModelRouter.from_configs(config.models.primary, config.models.fallback)

    ready_root = Path('/root/.openclaw/workspace/tmp_pipeline2_new_ready_single/ready')
    problems = discover_ready_problems(
        ready_root=ready_root,
        workspace_root=PROJECT_ROOT.parent,
        include_manual_review=config.runtime.include_manual_review,
        max_problems=10,
        max_images=config.runtime.max_images_per_problem,
    )
    target = None
    for problem in problems:
        if problem.problem_id == 'prob_52fad96dad32a829290d6e8c':
            target = problem
            break
    if target is None:
        raise RuntimeError('Target problem `prob_52fad96dad32a829290d6e8c` not found in new ready single set.')

    runtime_problem = {
        **target.to_runtime_problem(),
        'sample_record': target.sample_record,
    }
    foundation = _extract_ptk_once(router, runtime_problem)
    rounds: List[Dict[str, Any]] = []

    max_repair_rounds = 2
    for round_index in range(max_repair_rounds + 1):
        critique = critique_ptk_foundation(
            router,
            runtime_problem,
            foundation.get('p_facts', []),
            foundation.get('t_facts', []),
            foundation.get('k_atoms', []),
        )
        round_record: Dict[str, Any] = {'round_index': round_index, **critique}
        rounds.append(round_record)
        if critique.get('pass'):
            break
        if round_index >= max_repair_rounds:
            break
        polished = polish_ptk_foundation(
            router,
            runtime_problem,
            foundation,
            critique['revision_instructions'],
        )
        round_record['polish_summary'] = polished.get('revision_summary')
        foundation = {
            **foundation,
            'p_facts': polished['p_facts'],
            't_facts': polished['t_facts'],
            'k_atoms': polished['k_atoms'],
        }

    out = {
        'problem_id': runtime_problem['problem_id'],
        'sample_path': runtime_problem.get('sample_path'),
        'question_text': runtime_problem.get('question_text'),
        'standard_answer': runtime_problem.get('standard_answer'),
        'images': runtime_problem.get('images'),
        'foundation': foundation,
        'audit': {
            'component': 'PTKFoundationBuilder',
            'max_repair_rounds': max_repair_rounds,
            'passed': bool(rounds and rounds[-1].get('pass')),
            'rounds': rounds,
        },
        'router_last_error': router.last_error_summary(),
        'router_usage': router.usage_summary(),
    }

    out_path = PROJECT_ROOT / 'pipeline2/outputs_new_ready_single/ptk_probe_prob_52fad96dad32a829290d6e8c.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(out_path)
    print(json.dumps(out['audit'], ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
