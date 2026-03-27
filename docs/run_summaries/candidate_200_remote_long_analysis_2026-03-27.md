# 2026-03-27 candidate_200_remote long-run analysis

- Date: 2026-03-27
- Run: `outputs/candidate_200_remote_long/run_cf4370b4bf405a34`
- Config: `configs/candidate_200_remote.yaml`
- Scope: long-running 200-sample benchmark analysis before Geometry3K official-zip ingest fix is folded into a new full rerun

## Executive summary

这轮长任务已经证明：**pipeline 主流程可以稳定跑完整轮 200 样本 benchmark**，当前的主要瓶颈已经从“远端模型调用不稳定、流程容易中断”转移到“对高视觉依赖题目偏保守，导致 review 偏多”。

本轮最重要的两个结论是：

1. **稳定性问题已基本解决**
   - 长任务自然结束，exit code 0。
   - 远端模型链路没有再次把整轮任务打死。
   - 除 `Geometry3K` 外，其余数据集都完成了 20 个样本处理。

2. **当前主要问题是保守性，而不是崩溃或大面积误放行**
   - 本轮整体 `reject` 只有 12 个，不算高。
   - 但 `review` 达到 55 个，说明系统更倾向于在不确定时挂人工复核，而不是直接放行。
   - 这对早期质量控制是好事，但也意味着后续需要针对高视觉依赖数据集继续拆解 review 根因。

## Run metadata

- Top-level summary: `outputs/candidate_200_remote_long/run_cf4370b4bf405a34/summary.json`
- Dataset summaries:
  - `outputs/candidate_200_remote_long/run_cf4370b4bf405a34/datasets/*/summary.json`
- Records:
  - `outputs/candidate_200_remote_long/run_cf4370b4bf405a34/datasets/*/records/*.jsonl`

## Aggregate result

### Runtime

- Total runtime: **9311 seconds**
- Approx. **155.2 minutes**
- Approx. **2 hours 35 minutes**
- Average per processed sample (`190` samples): **49.0 seconds / sample**

说明：本次长任务的精确起点可从 run summary 中读取 `created_at = 2026-03-27T08:50:34Z`；结束时间结合运行完成时的进程观测计算，整体耗时约 **9311 秒**。这里采用本轮运行过程中的实际长任务监测结果作为耗时口径。

### Requested / processed

- Requested: **200**
- Processed: **190**

这里缺失的 **10** 不是运行中途丢样本，而是当时 `Geometry3K` ingest 入口仍然只吃到了 demo examples，因此只提供了 10 个可处理样本。

### Decision totals

- Pass: **123**
- Review: **55**
- Reject: **12**

按本轮实际 processed=190 计算：

- Pass rate: **64.7%**
- Review rate: **28.9%**
- Reject rate: **6.3%**

## Per-dataset result table

| Dataset | Processed | Pass | Review | Reject | Comment |
|---|---:|---:|---:|---:|---|
| `scemqa` | 20 | 17 | 2 | 1 | 整体健康，少量隐式视觉依赖题仍会触发 review/reject |
| `geometry3k` | 10 | 2 | 1 | 7 | **当时 ingest 入口错误，结果不应作为正式 Geometry3K 结论** |
| `cmm_math` | 20 | 18 | 2 | 0 | 结果健康，说明 `split_open` 误伤修复生效 |
| `mathvision` | 20 | 16 | 4 | 0 | 中等偏稳，review 略高但无 reject |
| `mm_math` | 20 | 2 | 18 | 0 | 极高 review，明显偏保守 |
| `seephys` | 20 | 19 | 1 | 0 | 本轮最佳之一，说明当前链路在该数据集上匹配度很高 |
| `multi_physics` | 20 | 17 | 2 | 1 | 整体健康 |
| `physreason` | 20 | 7 | 12 | 1 | review 明显过高，需要重点拆解 |
| `eee_bench` | 20 | 14 | 4 | 2 | 中等偏稳，仍有少量 reject |
| `emma_physics` | 20 | 11 | 9 | 0 | 几乎不 reject，但 review 偏高 |

## Interpretation by dataset tier

### Tier A: already healthy / high-confidence

#### `seephys`

- `pass 19 / review 1 / reject 0`
- 这是本轮最健康的数据集之一。
- 说明在该数据集上，当前 extraction / rewrite / alignment / gate 组合已经比较匹配。

#### `cmm_math`

- `pass 18 / review 2 / reject 0`
- 这一结果是对前面修复 `split_open` 误伤的强验证。
- 也就是说，`CMM-Math` 之前的问题确实更偏规则误伤，而不是样本本身质量差。

#### `scemqa`

- `pass 17 / review 2 / reject 1`
- 已经进入健康区间。
- 剩余风险主要仍来自“隐式依赖图像但题干显式视觉锚点不足”的题目，而不是 rewrite 主链路失效。

#### `multi_physics`

- `pass 17 / review 2 / reject 1`
- 与 `SCEMQA` 类似，表现已可接受。
- 少量 review/reject 更像局部样本复杂性，而非系统性 ingest / rewrite 问题。

#### `mathvision`

- `pass 16 / review 4 / reject 0`
- 整体可接受。
- review 稍多，但没有 reject，说明系统在该数据集上更偏谨慎而非失真。

### Tier B: usable but clearly over-conservative

#### `emma_physics`

- `pass 11 / review 9 / reject 0`
- 这种分布很典型：样本不是“坏”，而是系统对其不够自信。
- 重点应放在 alignment / solvability / final gate 的保守性，而不是 ingestion 或 rewrite 基础故障。

#### `physreason`

- `pass 7 / review 12 / reject 1`
- review 明显过高。
- 结合 `rewrite_strategy_counts.keep_open = 20`，更像是 rewrite 没有造成破坏，而是后段 gate 不愿直接 pass。
- 这类数据集更值得进一步统计 review reason codes 和 alignment status 分布。

#### `mm_math`

- `pass 2 / review 18 / reject 0`
- 这是本轮 review 最高的数据集。
- 但不能简单将其视为 bug，因为已确认至少存在“应保留的合理 review”案例：高视觉锚点密度几何题在图文对齐风险较高时，确实不应轻易 pass。
- 因此 `MM-Math` 的下一步不是简单“降 review”，而是**区分合理 review 与过度保守 review**。

### Tier C: current result not valid as official quality judgement

#### `geometry3k`

- `processed 10 / pass 2 / review 1 / reject 7`
- 这轮结果**不能直接用于判断正式 Geometry3K 表现**。
- 根因不是 Cleaning 主链路，而是 ingest 入口在本轮运行时仍然错误地走到了：
  - `annotation_tool/data_collection/data_examples/11..20/data.json`
- 它没有接上 README 所要求的：
  - `data/geometry3k/test.zip`
  - `data/geometry3k/val.zip`
  - `data/geometry3k/train.zip`
  解压后的正式主数据。
- 因此，本轮 Geometry3K 的坏结果主要反映 ingest 入口错误，而不反映正式 3002 题主数据上的真实性能。

## Rewrite strategy distribution

从 summary 看，这轮 rewrite 行为有几个明显特征：

1. **`keep_open` 在高视觉依赖数据集上占比高**
   - `mm_math: keep_open = 20`
   - `physreason: keep_open = 20`
   - `seephys: keep_open = 20`
   - 这说明 rewrite 并未强行改写这些题，而是多数保持 open-ended 形态。

2. **`blank_open` 在若干文本主导或结构较规整数据集上较常见**
   - `scemqa: blank_open = 16`
   - `cmm_math: blank_open = 18`
   - `eee_bench: blank_open = 9`
   - `emma_physics: blank_open = 11`

3. **`split_open` 已经不再在 `CMM-Math` 上大面积误伤**
   - `cmm_math: split_open = 1`
   - 且总体结果仍为 `18 pass / 2 review / 0 reject`
   - 说明之前的修复方向是正确的。

## Rewrite strategy distribution

从 summary 看，这轮 rewrite 行为有几个明显特征：

1. **`keep_open` 在高视觉依赖数据集上占比高**
   - `mm_math: keep_open = 20`
   - `physreason: keep_open = 20`
   - `seephys: keep_open = 20`
   - 这说明 rewrite 并未强行改写这些题，而是多数保持 open-ended 形态。

2. **`blank_open` 在若干文本主导或结构较规整数据集上较常见**
   - `scemqa: blank_open = 16`
   - `cmm_math: blank_open = 18`
   - `eee_bench: blank_open = 9`
   - `emma_physics: blank_open = 11`

3. **`split_open` 已经不再在 `CMM-Math` 上大面积误伤**
   - `cmm_math: split_open = 1`
   - 且总体结果仍为 `18 pass / 2 review / 0 reject`
   - 说明之前的修复方向是正确的。

## Additional issue found during post-run inspection: Rewrite LLM was effectively inactive

在这轮 run 的后续排查中，还确认了一个需要单独记录的问题：

- 实际 processed 样本数为 **190**。
- 对应的 `rewrite_reports.jsonl` 总数也是 **190**。
- 但汇总所有 `datasets/*/records/rewrite_reports.jsonl` 后发现：
  - `llm_used = True` 的样本数：**0**
  - 这轮所有 rewrite report 的 `llm_used` 都是空值（落盘表现为 `null/None`）。

也就是说：

> **这轮 200 样本长任务中，rewrite 阶段虽然有产出 strategy（如 `keep_open` / `blank_open` / `split_open`），但这些结果全部来自 fallback / rule-based rewrite，而不是 LLM rewrite。**

### Why this matters

这意味着本轮 benchmark 的结果应被理解为：

- extraction 正常运行
- cleaning / decision 正常运行
- 但 rewrite 增强没有真正发挥作用

因此，本轮结果更接近：

> **fallback-only rewrite baseline**

而不是“rewrite LLM fully active”的最终上限表现。

### What we verified

后续排查已经确认两点：

1. **并不是因为所有样本都没有 choices**
   - 例如：
     - `cmm_math` 的 `choice_field = "options"`（20/20）
     - `emma_physics` 的 `choice_field = "options"`（20/20）
     - `scemqa` 的 `choice_field = "choices"`（20/20）
     - `geometry3k` 的 `choice_field = "choices"`（10/10）
   - 所以不能简单归因为“没有选项，导致全都不走 rewrite LLM”。

2. **当前最可疑的是 RewriteAgent 没有真正拿到 enabled 的 client，或其 LLM 返回从未成功写回**
   - `benchmark/src/multidataset_cleaning_pipeline.py` 中 `RewriteAgent.rewrite(...)` 的逻辑是：
     - 若 `not self.client.config.enabled or not choices`，则直接 `return fallback`
     - 只有在 LLM rewrite 成功时，才会显式写入 `"llm_used": True`
   - 但本轮 run 中没有任何一条 record 出现 `"llm_used": True`。

### Current confidence level

到目前为止，我们已经有足够证据确认：

- **本轮 190 条 processed 样本全部没有走 LLM rewrite。**
- **这不是因为所有数据集都没有 choices。**

但“究竟是 RewriteAgent 全局 disabled、配置传递错误，还是 `chat_json(...)` 全部返回空”这一层，仍需要继续沿着以下路径深挖：

- `run_pipeline.py`
- `configs/candidate_200_remote.yaml`
- `PipelineConfig.from_dict(...)`
- `RewriteAgent` 的实例化位置
- `OpenAICompatibleClient` 在 rewrite 阶段拿到的实际 `config.enabled`

因此，本问题目前应在文档里作为：

> **已确认存在的运行限制（confirmed issue），但根因还需进一步定位。**

### Update from follow-up focused rerun (`cmm_math_rewrite_debug`)

在后续为 `CMM-Math` 做的定点长任务验证中，我们已经把这个问题进一步钉死。

- 验证 run：`outputs/cmm_math_rewrite_debug/run_ab67e5950c2f21c8`
- 结果：`processed=20 / pass=17 / review=3 / reject=0`
- 新增证据文件：
  - `outputs/cmm_math_rewrite_debug/run_ab67e5950c2f21c8/logs/run.log`
  - `outputs/cmm_math_rewrite_debug/launcher/chat_json_debug.log`

这次验证加入了第一版纯文本运行日志 `run.log`，并对 `chat_json` 打开了调试日志。由此确认：

1. **RewriteAgent 的入口条件本身没有问题**
   - `run.log` 显示：
     - `client_enabled=True`
     - `choice_count=3/4`
     - 已正常进入 `RewriteAgent.rewrite(...)`
   - 因此可以排除：
     - `client.config.enabled=False`
     - `choices empty`

2. **rewrite fallback 的直接原因是 `chat_json returned empty`**
   - `run.log` 中每条样本都先记录 `entered ...`，随后记录：
     - `fallback ... reason=chat_json returned empty`

3. **`chat_json returned empty` 的底层真实原因已经被 debug log 钉成 `401 Unauthorized`**
   - `chat_json_debug.log` 中出现多条：
     - `caller=rewrite HTTPError status=401 reason=Unauthorized`
     - body 中明确包含：`无效的令牌`
   - 也就是说，rewrite 请求并不是“没发出”，也不是“返回缺少 JSON”，而是**被接口直接按无效令牌拒绝**。

4. **进一步发现了配置/环境注入层面的具体风险点**
   - 当前版本 `PipelineConfig.from_yaml(...)` 并不会展开 YAML 里的 `${OPENAI_API_KEY}` 字面量。
   - 它只会在运行进程环境中存在真实 `OPENAI_API_KEY` 时，用环境值覆盖 `model.api_key`。
   - 因此，在 `nohup` 场景里如果环境没有带上真实 `OPENAI_API_KEY`，配置里的：
     - `api_key: ${OPENAI_API_KEY}`
     会被当作普通非空字符串保留下来。
   - 这会导致：
     - `run.log` 里看到 `api_key_present=True`
     - 但实际发送出去的 Authorization token 其实是无效的 `${OPENAI_API_KEY}` 字面量
     - 最终触发 `401 Unauthorized / 无效的令牌`

### Updated confidence level

到这一轮定点验证为止，关于 rewrite LLM 未生效的问题，已经可以把结论更新为：

> **在 `cmm_math_rewrite_debug` 验证中，rewrite 阶段并不是没有进入，也不是没有 choices，而是 `chat_json` 请求被接口以 `401 Unauthorized / 无效的令牌` 拒绝；其高概率根因是当前 `from_yaml()` 不展开 `${OPENAI_API_KEY}`，而 `nohup` 进程又没有拿到真实环境变量，导致发送了字面量占位符 token。**

## What this run proves

### 1. Long-run execution stability is now good enough

本轮最大的工程价值不是某个单数据集分数，而是：

- 长任务可以完整跑完
- 远端模型不会轻易把整轮打死
- 大多数数据集的 ingest / preprocess / cleaning / report 链路都能闭环

换句话说，**主流程已经具备继续做大样本迭代的稳定性基础**。

### 2. The bottleneck moved from reliability to calibration

当前最大短板已经不是：

- 网络抖动
- 远端 API 崩溃
- 流程中断

而是：

- 高视觉依赖题目被判得过于保守
- `review` 偏多
- 少数数据集的 final gate 过紧

### 3. Earlier targeted fixes are real, not smoke-only coincidences

本轮大样本结果支持了两个之前在 smoke 中形成的判断：

- `CMM-Math` 的 `split_open` 误伤修复是真有效的
- `MM-Math` 中确实存在“应该保留为 review”的高视觉密度几何题，不应一刀切地把 review 都视为误伤

## Known limitation of this specific run

### Geometry3K contamination

这轮 benchmark 的唯一明显结构性污染项，是 `Geometry3K` 当时还没有接入正式 zip 主数据。

因此这轮 benchmark 只能作为：

- pipeline 稳定性验证
- 大多数数据集上的保守性分析
- `CMM-Math` / `MM-Math` / `PhysReason` / `EMMA-Physics` 行为分析

而**不能作为修复后正式 Geometry3K 表现的最终结论**。

## Recommended next actions

基于本轮结果，推荐的后续优先级如下：

1. **先重跑修复后的 Geometry3K 定点验证**
   - 去掉旧 ingest 入口污染
   - 拿到正式主数据上的 Geometry3K 结果

2. **重点拆解 `MM-Math` review**
   - 区分“合理 review”与“过度保守 review”
   - 查看 `major_alignment_conflict` / `visual_reference_density_mismatch` 是否过紧

3. **抽样分析 `PhysReason` 与 `EMMA-Physics` 的 review 原因分布**
   - 这两者的模式都更像 gate 偏保守，而不是 ingestion 故障

4. **在上述定点修复后，再考虑重跑整轮 200 benchmark**
   - 否则新的 Geometry3K 结果与当前 run 不可直接横比

5. **为后续长任务增加统一纯文本运行日志 `outputs/<run_id>/logs/run.log`**
   - 第一版最小实现优先覆盖：run start/finish、dataset start/finish、sample 字段选取结果、rewrite 入口/分支/LLM 结果、final decision。
   - 重点要把“这一步干了什么、用了什么参数、为什么 fallback / 为什么这样判”直接写成可顺序阅读的文字日志。
   - 目标是下次遇到类似“190 条为什么全没走 rewrite LLM”时，不再依赖事后拼 records，而能直接从单个 run log 看出根因。

## Bottom line

一句话总结本轮 `run_cf4370b4bf405a34`：

> 这轮 200 样本长任务已经证明 pipeline 能稳定长跑；当前核心问题不再是“跑不通”，而是“对高视觉依赖题过于保守”，尤其集中在 `MM-Math`、`PhysReason`、`EMMA-Physics`；而 `Geometry3K` 的结果则由于旧 ingest 入口错误而不具正式评估意义。
