# 2026-03-28 rewrite LLM recovery and run-log verification

- Date: 2026-03-28
- Scope: log installation, rewrite LLM failure root-cause confirmation, API key placeholder fix, and focused `CMM-Math` recovery verification

## What changed

这次补了三类东西：

1. **第一版纯文本运行日志 `run.log`**
   - 在 `benchmark/src/multidataset_cleaning_pipeline.py` 中新增 `RunLogger`
   - 第一版最小覆盖：
     - `RUN` start/finish
     - `DATASET` start/finish
     - `REWRITE` entered/fallback/llm_result
     - `DECISION` final decision

2. **第二层运行日志增强**
   - 补了 `SAMPLE` 级字段选取日志
   - `chat_json(...)` 新增 `caller` 参数
   - rewrite 路径通过 `caller="rewrite"` 把请求错误归因到具体阶段

3. **API key 配置保险**
   - `PipelineConfig.from_yaml(...)` 新增 `${VAR}` 环境变量展开
   - 当 `model.enabled=True` 且 `api_key` 缺失/仍是占位符时，直接 fail fast
   - 防止继续带着 `${OPENAI_API_KEY}` 这样的字面量 token 去请求远端接口

## Root cause that was confirmed

通过两轮 `cmm_math_rewrite_debug` 定点验证，已经把 rewrite LLM 未生效问题钉死：

### First focused validation

- Run: `outputs/cmm_math_rewrite_debug/run_ab67e5950c2f21c8`
- Result: `processed=20 / pass=17 / review=3 / reject=0`
- Evidence:
  - `outputs/cmm_math_rewrite_debug/run_ab67e5950c2f21c8/logs/run.log`
  - `outputs/cmm_math_rewrite_debug/launcher/chat_json_debug.log`

Confirmed facts:

- `RewriteAgent.rewrite(...)` 确实进入了
- `client_enabled=True`
- `choice_count=3/4`
- fallback 直接原因是：`chat_json returned empty`
- 底层真实原因是：
  - `caller=rewrite HTTPError status=401 reason=Unauthorized`
  - body 中明确包含：`无效的令牌`

### Why the 401 happened

最终根因不是 rewrite 逻辑本身，而是配置/环境注入：

- YAML 里写的是：`api_key: ${OPENAI_API_KEY}`
- 原始版本 `from_yaml()` **不会展开** 这个占位符
- 它只会在进程环境中真有 `OPENAI_API_KEY` 时，用环境值覆盖
- 某些 `nohup` 进程里没有带到真实 `OPENAI_API_KEY`
- 于是最终 `cfg.model.api_key` 变成字面量 `${OPENAI_API_KEY}`
- 由于这个字符串非空，所以 `api_key_present=True`
- 但发出的 Authorization 头实际是占位符 token
- 远端接口返回：`401 Unauthorized / 无效的令牌`

### Final confirmation run after the fix

在补上 env 展开和 fail-fast 后，又跑了一轮带真实环境变量注入的 `CMM-Math` 定点验证：

- Run: `outputs/cmm_math_rewrite_debug/run_43bac1c988f5f011`
- Result: `processed=20 / pass=18 / review=1 / reject=1`
- Runtime: about **1715 seconds** (~**28.6 minutes**)
- Average: about **85.8 seconds / sample**
- Rewrite strategies:
  - `blank_open = 18`
  - `direct_open = 1`
  - `split_open = 1`

### What this second run proves

1. **No more 401 unauthorized**
   - `chat_json_debug.log` no longer shows rewrite-side 401 failures

2. **Rewrite is no longer fallback-only**
   - `run.log` now repeatedly shows:
     - `entered client_enabled=True ...`
     - `llm_result strategy=... variant_count=...`

3. **LLM rewrite is now changing strategy outcomes**
   - Example: `prob_d74f71876f9e0f5717ba47af`
     - fallback pre-judgement: `split_open`
     - LLM result: `direct_open`
     - final decision: `pass`

This confirms that rewrite recovery is real, not cosmetic.

## Files touched

- `benchmark/src/multidataset_cleaning_pipeline.py`
- `benchmark/src/pipeline_cleaning.py`
- `configs/cmm_math_rewrite_debug.yaml`
- `README.md`
- `docs/run_summaries/candidate_200_remote_long_analysis_2026-03-27.md`

## Commits

- `490ee4b` — `feat: add run log for rewrite debugging`
- `49de646` — `fix: expand env api keys and fail fast on placeholders`
- `5c650c6` — `feat: add run logs and verify rewrite llm recovery`

## Bottom line

一句话总结：

> 这次已经把 rewrite LLM 未生效的根因从“猜测”推进到了“证据闭环”：原问题是 `${OPENAI_API_KEY}` 未展开且进程未继承真实环境变量，导致 rewrite 请求带着占位符 token 被 401 拒绝；补上 env 展开与 fail-fast 后，`CMM-Math` 定点验证已确认 rewrite LLM 恢复正常，并开始真实改变 rewrite strategy。
