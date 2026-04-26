# Notes

## 2026-04-26

- `pipeline2` gained a minimal checkpoint-aware **stage retry** layer on top of the earlier problem-level retry port.
- Added runtime config knobs in `default_pipeline2.yaml` / `config.py`:
  - `runtime.stage_retry_attempts`
  - `runtime.stage_retry_backoff_seconds`
- Current intended behavior:
  - method-graph execution and problem-graph execution now retry only when the thrown error looks transient (for example timeout / 429 / 5xx / connection reset);
  - retries resume from langgraph checkpoint state instead of restarting the whole stage graph from scratch;
  - if the same stage keeps failing until budget exhaustion, the failure is surfaced as `StageRetryBudgetExhaustedError`, which is then handled by the existing problem-level retry / `problem_errors` path.
- This was kept as a **scheme-B minimal port**: it does not try to wholesale replace `qjb` routing/client behavior, but it restores the upstream-style guardrail where transient stage failures get a bounded same-stage resume path before the whole problem is marked failed.

- Added runtime config knobs in `default_pipeline2.yaml` / `config.py`:
  - `runtime.log_level`
  - `runtime.log_to_file`
- Current logging coverage is intentionally lightweight but useful for debugging hangs and failure concentration:
  - runtime initialization;
  - annotate / resume / trace-eval start and end;
  - batch start / end;
  - per-problem start / success;
  - per-problem exception logging with inferred failure stage;
  - LLM request start / success / retryable HTTP failure / transport failure / parse miss;
  - fallback activation from primary to fallback endpoint.
- When `runtime.log_to_file: true`, logs are written to `output_root/annotation_runtime/pipeline2.log`.

## 2026-04-26

- `pipeline2` `ready_loader.py::_collect_image_paths(...)` now also consumes top-level ready-sample `images` and `image_path`, not only nested `image_paths` / asset-registry-derived fields.
- Reason for the change: some ready samples store the actually usable subset-relative path only at the top level (for example `artifacts/images/...`), while nested fields may still contain empty `image_paths`, `inline://...`, or source-run `outputs/...` paths that are less reliable inside the subset runtime.
- This is a compatibility fix so ready subsets do not miss images that are physically present under the dataset folder just because the usable path lived only in the top-level sample fields.

## 2026-04-26

- `pipeline2` PTK prompt tuning direction for current `p_facts` failures: do **not** start with broad subject-classification prompts.
- Current preferred strategy is a low-token visual-grounding upgrade:
  - strengthen the first-pass perception prompt with a short coverage checklist;
  - keep broad subject routing out for now;
  - place only tiny `bad -> better` micro few-shots in the `p_facts` patch prompt, because that path is paid only on failed samples.
- If later routing becomes necessary, prefer routing by **visual archetype** (for example diagram/topology vs chart/curve) rather than by school subject labels such as physics / chemistry / math.

## 2026-04-09

- `mm_math` review 放行口径当前采用 **B方案（稍激进）**。
- 具体来说：在保留纯 `alignment_requires_review` 低风险样本的基础上，额外纳入“**只有 `metadata_inconsistency`、但没有额外视觉/答案坏信号**”的样本。
- 按当前统计，候选池可从约 **51 条**扩到约 **74 条**。
- 这项记录是决策摘要；正式说明见：`docs/mm_math_review_release_decision_2026-04-09.md`。
