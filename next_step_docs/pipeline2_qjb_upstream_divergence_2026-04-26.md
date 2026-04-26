# pipeline2 qjb vs upstream divergence notes (2026-04-26)

## Scope

Comparison target:

- local qjb: `/root/.openclaw/workspace/agent-pipeline/src/benchmarkallinone/pipeline2`
- upstream-style checkout: `/root/.openclaw/workspace/pipeline2/pipeline2`

Files inspected:

- `clients.py`
- `config.py`
- `pipeline.py`
- `annotation_modules.py`

This is an architectural divergence note, not a patch plan. Do not blindly port upstream code into qjb without checking local configs, router signatures, stage cache, salvage, and retry behavior.

## High-level conclusion

The branches are still meaningfully forked outside the PTK prompt/sanitizer area.

Current safest posture:

1. Keep qjb `pipeline.py` stage-cache / salvage / problem-error behavior.
2. Do not replace qjb `clients.py` / `config.py` with upstream wholesale; the API model and fallback policy differ.
3. Continue selectively porting upstream prompt/sanitizer/schema improvements only when they fit qjb router interfaces.
4. If upstream `response_schema=...` is desired, migrate `clients.py`, `config.py`, `agents.py`, and all `_call_router(...)` call sites together as a dedicated compatibility patch.

## `clients.py`

### qjb behavior

- Uses endpoint-level primary/fallback routing: `ModelRouter.from_configs(primary, fallback)`.
- Keeps fallback duplicate-resource detection via `_shares_resource_pool(...)`.
- Keeps endpoint retry knobs in `ModelEndpointConfig`: `api_mode`, `max_attempts`, `retry_base_delay_seconds`, `retry_max_delay_seconds`, `respect_retry_after`.
- Uses qjb logging around request start / retry / failure.
- Has qjb-specific response handling methods including `_read_sse_text(...)` and `_post_responses(...)`.
- Public router methods do **not** expose `response_schema=...`.

### upstream behavior

- Single-primary policy: `ModelRouter.from_configs(primary)`; enabled fallback config is rejected in `config.py`.
- `ModelEndpointConfig` uses `provider`, `wire_api`, `requires_openai_auth`, and `disable_response_storage` instead of qjb retry/fallback config fields.
- Client methods support `response_schema=...` and can emit OpenAI Responses API JSON schema payloads.
- Router has timeout/deadline helpers such as `_enabled_clients(...)`, `_router_retry_deadline(...)`, `_client_call_timeout(...)`, `_last_error_is_permanent(...)`, `_mark_client_timeout(...)`, and `_invoke_client_method_with_timeout(...)`.

### Current judgment

Do **not** wholesale inherit upstream `clients.py` into qjb yet. It would remove or invalidate qjb fallback config/tests and would require updating config files plus every router call-site that expects qjb signatures. The useful upstream feature is schema-bound responses, but that should be a deliberate migration.

## `config.py`

### qjb behavior

- Default base URL is `https://synai996.space/v1`.
- Model endpoint has `api_mode`, retry attempts/backoff, and `respect_retry_after`.
- Default fallback endpoint exists.
- Runtime config includes `log_level` and `log_to_file`.
- `problem_retry_attempts` default is `3`.

### upstream behavior

- Default base URL is `https://www.msutools.cn`.
- Model endpoint has `provider`, `wire_api`, `requires_openai_auth`, and `disable_response_storage`.
- Enabled fallback is intentionally rejected.
- Runtime config removed qjb logging knobs.
- `problem_retry_attempts` default is `10`.

### Current judgment

Keep qjb config for now because existing local configs still use `api_mode` and fallback fields. Upstream config cannot be copied alone without breaking many local YAMLs. Potential selective candidates later: `wire_api` naming, `disable_response_storage`, and stricter single-primary policy, but only if local run configs are updated.

## `pipeline.py`

### qjb-only / qjb-expanded areas

- `_resolve_log_level(...)` and `_setup_logging(...)` for file/console logging.
- Stage-cache summary helpers:
  - `_stage_cache_record_summary(...)`
  - `_stage_cache_method_item_keys(...)`
  - `_build_stage_cache_summary(...)`
- Extended problem-error records include `stage_cache_summary`.
- `_format_problem_failure(...)` exists to make failed problem summaries richer.
- Runtime init uses `ModelRouter.from_configs(config.models.primary, config.models.fallback)`.

### shared or similar areas

Both lines now have stage cache primitives:

- `_stage_cache_path(...)`
- `_load_stage_cache_record(...)`
- `_write_stage_cache_record(...)`

Both lines now have `problem_errors/<problem_id>.json` and problem-level retry structure, but qjb records richer stage-cache summaries.

### upstream behavior

- Uses single-primary router init: `ModelRouter.from_configs(config.models.primary)`.
- Has less qjb-specific logging/config plumbing.
- Does not include qjb's richer stage-cache summary helpers.

### Current judgment

Keep qjb `pipeline.py` as the base. The qjb stage cache / salvage reporting is valuable for interrupted long runs and was added specifically after failures where batch summaries did not land. Do not regress this unless replacing it with an equal or better upstream mechanism.

## `annotation_modules.py`

### qjb-only areas

- Claim sequence repair helpers:
  - `_coerce_string_list(...)`
  - `_topologically_reorder_claims(...)`
  - `_repair_claim_sequence_locally(...)`
- qjb compact/context selection path:
  - `_select_claim_context(...)`
- qjb progress-aware extraction/build paths:
  - `_extract_ptk_once(..., progress_state=..., save_progress=...)`
  - `build_ptk_foundation(..., progress_state=..., save_progress=...)`
  - claim bundle progress saving
- qjb generic section repair wrapper:
  - `_normalize_ptk_section_targets(...)`
  - `_polish_ptk_section(...)`
  - `polish_ptk_foundation(...)`
- qjb claim verification partial merge path:
  - `_normalize_claim_verify_partial(...)`
  - `_merge_claim_verify_partials(...)`
- qjb `_build_ptk_problem_record(...)` and `_cached_dict_list(...)` support cache/progress compatibility.

### upstream-only areas

- New compact prompt selectors:
  - `_rank_records_for_claim_prompt(...)`
  - `_compact_ptk_for_claim_prompt(...)`
  - `_compact_ptk_for_ptk_prompt(...)`
- Upstream claim polish prompt helper:
  - `_build_claim_polish_prompt(...)`
- Split PTK section polish functions:
  - `_polish_p_facts(...)`
  - `_polish_t_facts(...)`
  - `_polish_k_atoms(...)`
- Extensive `response_schema=...` use through `.response_schemas`.

### Already aligned by recent PTK patch

The PTK sanitizer / deterministic quality helpers are now mostly upstream-aligned:

- `_coerce_object_list(...)`
- `_normalize_p_facts(...)`
- `_normalize_t_facts(...)`
- `_normalize_k_atoms(...)`
- `_derive_text_facts_from_question(...)`
- `_sanitize_t_facts(...)`
- `_sanitize_ptk_foundation(...)`
- `_heuristic_ptk_foundation_report(...)`
- `_merge_ptk_critiques(...)`
- `_infer_ptk_issue_categories(...)`

Prompt text for PTK critic/polish is also upstream-aligned; remaining prompt differences are recorded separately in `next_step_docs/pipeline2_prompt_differences_qjb_2026-04-26.md`.

### Current judgment

Keep qjb orchestration/progress shape for now. Selectively consider upstream compact PTK/claim prompt builders later, but only after checking whether they reduce token cost without losing qjb salvage progress and without needing `response_schema` support.

## Migration risk list

High-risk to port directly:

- upstream `clients.py` + `config.py` single-primary / `wire_api` rewrite;
- upstream `response_schema=...` call sites;
- upstream `ModelRouter.from_configs(primary)` in qjb while local configs still define fallback;
- upstream `annotation_modules.py` wholesale, because it drops qjb progress/cache helpers and claim repair functions.

Lower-risk selective candidates:

- upstream compact prompt-selection helpers if adapted to qjb `_call_router(...)` signatures;
- schema-response support as a dedicated client/router migration;
- trimming qjb first-pass `KNOWLEDGE` prompt guardrails if token cost remains a concern.

## Recommended next steps

1. Do not change client/fallback in the PTK sanitize branch.
2. If token cost is the next priority, first revert/trim `KNOWLEDGE_LIBRARIAN_SYSTEM_PROMPT` and `build_knowledge_user_prompt(...)`, then run a <=20-sample smoke.
3. If stability/API correctness is the next priority, create a separate branch to migrate qjb router to upstream-style `response_schema` support while preserving qjb fallback or explicitly deciding to remove fallback.
4. If interruption recovery is the next priority, keep expanding qjb stage-cache salvage rather than inheriting upstream wholesale.
