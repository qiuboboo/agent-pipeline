# pipeline2 upstream config migration notes (qjb pipeline retained)

Date: 2026-04-26

## Decision

- `src/benchmarkallinone/pipeline2/config.py` is now copied directly from current upstream `pipeline2/pipeline2/config.py`.
- qjb `src/benchmarkallinone/pipeline2/pipeline.py` remains the base because it has richer runtime logging, problem/stage retry reporting, cache/salvage reporting, and failure persistence.

## Required compatibility changes

### 1. Config schema change

Upstream config removes the old qjb endpoint knobs:

- `api_mode` -> replaced by `wire_api`
- endpoint retry fields removed from `ModelEndpointConfig`:
  - `max_attempts`
  - `retry_base_delay_seconds`
  - `retry_max_delay_seconds`
  - `respect_retry_after`
- enabled `models.fallback` is rejected; upstream is single-primary.
- `RuntimeConfig.problem_retry_attempts` default is now `10`.
- `RuntimeConfig` no longer defines qjb-only `log_level` / `log_to_file`.

### 2. Preserve qjb logging without editing upstream config.py

Because `config.py` is intentionally upstream-exact, qjb logging controls were moved behind pipeline-side fallbacks:

- default log level: `INFO`
- default file logging: enabled
- `pipeline.py` uses helper accessors rather than direct `ctx.config.runtime.log_level` / `log_to_file` field access.

This preserves detailed operational logs while keeping `config.py` pure upstream.

### 3. Client/router compatibility

qjb `clients.py` had to be moved to upstream-style endpoint fields:

- use `config.wire_api` to choose `/responses` vs `/chat/completions`
- support upstream `disable_response_storage`
- remove qjb fallback routing assumptions from live router usage
- keep qjb-style request lifecycle logs and timeout/retry observability:
  - `[llm-request-start]`
  - `[llm-request-success]`
  - `[llm-request-http-error]`
  - `[llm-request-transport-error]`
  - `[llm-request-parse-miss]`
  - `[llm-client-call-start]`
  - `[llm-client-call-done]`
  - `[llm-client-timeout]`

### 4. Call-site changes

Updated active call sites to single-primary router construction:

- `pipeline.py`: `ModelRouter.from_configs(config.models.primary)`
- `verified_cot_pipeline.py`: `ModelRouter.from_configs(config.models.primary)`
- `output_verifier.py`: `ModelRouter.from_configs(config.models.primary)`

`verified_cot_code_backup/` still contains old backup-only references and was intentionally not treated as active runtime code.

### 5. YAML changes

Tracked YAML configs were normalized for upstream config compatibility:

- remove `models.fallback`
- rename `api_mode` to `wire_api` where present
- remove old endpoint retry fields where present

Untracked smoke configs may still need the same cleanup before use.

## Validation performed

- Confirmed `src/benchmarkallinone/pipeline2/config.py` byte-matches upstream current config:
  - `cmp -s src/benchmarkallinone/pipeline2/config.py /root/.openclaw/workspace/pipeline2/pipeline2/config.py`
- Compiled changed runtime files with `PYTHONPATH=src python3 -m compileall -q ...`.
- Loaded all tracked `src/benchmarkallinone/pipeline2/configs/*.yaml` through `Pipeline2Config.from_yaml(...)`.
- Ran client/router unit tests with unittest:
  - `PYTHONPATH=src python3 -m unittest src/benchmarkallinone/pipeline2/tests/test_clients.py src/benchmarkallinone/pipeline2/tests/test_clients_retry.py`
  - result: `Ran 10 tests ... OK`

## Remaining watch-outs

- Any external/untracked YAML still using `api_mode` or enabled `models.fallback` will fail under upstream config and needs manual cleanup.
- If the user wants configurable log level again, do not add it back to `config.py`; use pipeline-side defaults or a separate non-schema mechanism so `config.py` stays upstream-exact.
- The old fallback path is gone from active pipeline execution. If fallback is required again, it should be reintroduced deliberately around upstream `wire_api` semantics, not by restoring old `api_mode` config fields.
