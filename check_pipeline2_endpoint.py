from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / 'src/benchmarkallinone/pipeline2/configs/pipeline2.local.env'

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

base_url = os.environ['ANNOTATION_API_BASE_URL'].rstrip('/')
api_key = os.environ['ANNOTATION_API_KEY']
model = os.environ['ANNOTATION_MODEL']

payload = {
    'model': model,
    'messages': [{'role': 'user', 'content': 'Reply with exactly: OK'}],
    'temperature': 0,
}
req = urllib.request.Request(
    base_url + '/chat/completions',
    data=json.dumps(payload).encode('utf-8'),
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    },
    method='POST',
)
print('BASE_URL', base_url)
print('MODEL', model)
print('API_KEY_PREFIX', api_key[:8] if api_key else '')
try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode('utf-8', errors='replace')
        print('STATUS', resp.status)
        print(body[:2000])
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='replace')
    print('HTTP_STATUS', e.code)
    print(body[:2000])
    raise
except Exception as e:
    print('EXC_TYPE', type(e).__name__)
    print('EXC', e)
    raise
