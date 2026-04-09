# 2026-03-28 candidate_200_remote rerun analysis (`run_38bce3437874d962`)

- Date: 2026-03-28
- Run: `outputs/candidate_200_remote/run_38bce3437874d962`
- Config: `configs/candidate_200_remote.yaml`
- Scope: proxy-enabled rerun of the 200-sample long task after the earlier interrupted / incomplete attempt

## Executive summary

这次 rerun 的核心结论很明确：

1. **任务完整跑完了**，不是中途停止的半截结果。
2. **网络链路问题没有再次成为主阻塞**；此前的 `Network is unreachable` 未复现，代理接入后任务正常推进。
3. 这次真正暴露出来的主要问题已经不是“跑不通”，而是**不同数据集与当前清洗范式的兼容性差异非常大**。

整体结果为：

- `processed=200`
- `pass=114`
- `review=64`
- `reject=22`

按 200 样本计：

- **Pass rate**: `57.0%`
- **Review rate**: `32.0%`
- **Reject rate**: `11.0%`

与之前那次未完成 run 相比，这次最大的差异不是某个数据集小幅涨跌，而是：

> **这次拿到的是一份真正完整、可用于决策的全量结果。**

## Runtime

- Start: `2026-03-27 19:41:01 UTC`
- End: `2026-03-27 23:29:40 UTC`
- Total runtime: `13719 seconds`
- Approx. `228.7 minutes`
- Approx. `3 hours 48 minutes 39 seconds`
- Average per processed sample: `68.6 seconds / sample`

## Decision totals

- Processed: `200`
- Pass: `114`
- Review: `64`
- Reject: `22`

## Per-dataset results

| Dataset | Pass | Review | Reject | Main interpretation |
|---|---:|---:|---:|---|
| `scemqa` | 17 | 3 | 0 | 健康，少量 `split_open` 需要复核 |
| `geometry3k` | 7 | 10 | 3 | 高图依赖，review/reject 合理偏高 |
| `cmm_math` | 18 | 1 | 1 | 质量很高，可作为优先保留集 |
| `mathvision` | 17 | 3 | 0 | 整体稳定，少量隐式图依赖 |
| `mm_math` | 2 | 17 | 1 | **高度保守 review，疑似被 alignment 风险规则过度压制** |
| `seephys` | 19 | 1 | 0 | 本轮最稳之一 |
| `multi_physics` | 4 | 0 | 16 | **系统性不兼容，明显应降权甚至剔除** |
| `physreason` | 7 | 13 | 0 | 高 review，像是可解但系统信心不足 |
| `eee_bench` | 13 | 6 | 1 | 中等偏稳，少量图示/裁剪问题 |
| `emma_physics` | 10 | 10 | 0 | 可保留，但 review 成本高 |

## Rewrite strategy distribution

- `mm_math`: `keep_open=20`
- `seephys`: `keep_open=20`
- `physreason`: `keep_open=20`
- `multi_physics`: `blank_open=16, keep_open=2, split_open=1, rewrite_open=1`
- `cmm_math`: `blank_open=18, rewrite_open=1, split_open=1`
- `scemqa`: `blank_open=17, split_open=3`
- `emma_physics`: `blank_open=14, split_open=4, keep_open=2`

这组分布说明：

- `mm_math / physreason / seephys` 并不是被激进 rewrite 弄坏，而多数是 **keep_open 后进入后段判定**。
- `multi_physics` 则大量走 `blank_open`，但结果仍大面积 reject，说明问题主要在**源数据与清洗目标不兼容**，而不是某个单独 rewrite 策略选错。

## Deep interpretation by dataset

### Tier A — healthy and directly useful

#### `seephys`

- `19 / 1 / 0`
- pass 主因高度集中在 `meets_cleaning_requirements`
- 即便部分样本带 `low_resolution`，也没有破坏可解性

结论：

- 数据源与当前流程匹配度高
- 可作为优先保留集

#### `cmm_math`

- `18 / 1 / 1`
- 大多数样本结构稳定、文本足够、答案可验
- 唯一 reject 更像个别坏样本，而不是系统性问题

结论：

- 是这次 rerun 中最值得保留的数学集之一

#### `scemqa`

- `17 / 3 / 0`
- 少量 review 主要来自 `split_variant_needs_review`
- 不是大规模图文错位问题

结论：

- 基础质量好，review 成本可接受

#### `mathvision`

- `17 / 3 / 0`
- 少量 review 主要由 `implicit_visual_dependency / low_text_completeness / weak_visual_anchor` 引起

结论：

- 整体可用性强
- 风险集中在少数边缘样本

### Tier B — usable, but review cost is clearly higher

#### `eee_bench`

- `13 / 6 / 1`
- review 原因主要包括：
  - `split_variant_needs_review`
  - `implicit_visual_dependency`
  - `severe_crop_loss`
  - `low_text_completeness`

结论：

- 值得留
- 但应接受一定人工抽查成本

#### `emma_physics`

- `10 / 10 / 0`
- 典型“不是坏，但系统不放心”型数据集
- 高频原因：
  - `alignment_risky`
  - `major_visual_reference_density_mismatch`
  - `major_alignment_conflict`

结论：

- 可以保留
- 但需要人工 review 兜底

### Tier C — likely over-conservative review rather than truly bad data

#### `mm_math`

- `2 / 17 / 1`
- 几乎所有 review 样本都满足：
  - `solvability_score = 1.0`
  - `solvability_decision_hint = pass`
  - `rewrite_strategy = keep_open`
- 也就是说：
  - 题目通常已经是开放题
  - rewrite 没有把题改坏
  - 可解性系统认为样本可解
  - 但 alignment 风险模块因视觉锚点密度高而高频打成 risky

高频 reason code：

- `VISUAL_REFERENCE_DENSITY_MISMATCH`
- `MAJOR_ALIGNMENT_CONFLICT`
- `ALIGNMENT_RISKY`

结论：

> `mm_math` 更像是被当前 alignment 风险规则保守压制，而不是样本本身差。

它更适合作为：

- 规则调参验证集
- 人工抽样复核集

而不是直接整体降权。

#### `physreason`

- `7 / 13 / 0`
- 和 `mm_math` 类似，但程度稍轻
- 大量样本同时表现出：
  - 可解
  - 有 visual grounding
  - 但系统认为多模态依赖偏强，不敢直接 pass

结论：

- 更像“可用但系统置信度不足”
- 适合保留并做人审抽样，而不是简单丢弃

### Tier D — structurally incompatible with current cleaning target

#### `multi_physics`

- `4 / 0 / 16`
- 这是本轮最明确的失败数据集
- reject 样本高频原因高度一致：
  - `missing_grounded_visual_path`
  - `text_image_misaligned`
  - `bad_alignment`
  - `severe_crop_loss`
  - `low_text_completeness`
  - `normalized_question_incomplete`

深挖样本后能看到：

- 很多题题干只有“如图所示”“根据图中数据”之类表述
- 核心条件被外包给图像
- 一旦图像 grounding 不稳，开放式改写就会断链
- 多数 reject 记录已给出 `recommended_action = drop`

结论：

> `multi_physics` 不是简单“review 多一点”，而是源数据风格与当前 open-ended 清洗目标明显不兼容。

建议：

- 整体降权
- 或仅保留其中“抽象坐标图 / 明确变量定义”的少数子类

### Geometry-heavy middle case: `geometry3k`

- `7 / 10 / 3`
- 这个数据集不是整体坏，而是“好样本和坏样本分层明显”
- pass 样本通常 solvability / grounding 都成立
- reject 样本则常出现：
  - `missing_grounded_visual_path`
  - `low_text_completeness`
  - `normalized_question_incomplete`
  - `severe_crop_loss`

结论：

- `geometry3k` 的 review/reject 更像合理结果
- 不是系统性误伤主导

## Process / log anomaly check

## Overall conclusion

执行层面未见硬异常，属于**正常完成的一次长任务**。

明确正常的信号包括：

- 10 个 dataset 都出现 `start`
- 10 个 dataset 都出现 `finished`
- 顶层存在 `[RUN] finished ... processed=200 pass=114 review=64 reject=22`
- `latest_stdout.log` 不再出现 `Network is unreachable`
- 仅看到 HF unauthenticated warning，不构成致命错误
- 未见 traceback / exception / timed out / network error 爆栈

### Soft issues found in run.log

仍可见一些降级信号，但更像正常 fallback 而非故障：

- `chat_json returned empty`
- `invalid llm variants`
- `choices empty`

这些信号意味着：

- rewrite/LLM 部分并非完全稳定
- 某些样本会走 fallback 路径
- 可能带来：
  - 速度下降
  - review 比例上升

但因为 run 仍完整结束，所以应理解为：

> **存在降级与保守性问题，但没有程序级崩溃。**

### More important than runtime errors: policy tension inside the pipeline

这次最值得记录的不是程序报错，而是两个判定子系统之间的张力：

1. **solvability 子系统**经常给出：
   - `score = 1.0`
   - `decision_hint = pass`

2. **alignment 风险子系统**却同时给出：
   - `alignment_risky`
   - `visual_reference_density_mismatch`
   - `major_alignment_conflict`

这种现象在 `mm_math / physreason` 上最明显。

这说明当前 pipeline 存在一种系统行为：

> **样本在“可解性”上是通过的，但在“图文对齐风险”上被更保守地压到 review。**

这不是 crash，但它是后续调参最应该处理的“逻辑层异常”。

## Recommended next actions

### 1. For `mm_math`

不要直接剔除。建议：

- 抽样 review case 做人工复核
- 重点检查以下规则是否对几何题过于敏感：
  - `VISUAL_REFERENCE_DENSITY_MISMATCH`
  - `MAJOR_ALIGNMENT_CONFLICT`
  - `ALIGNMENT_RISKY`

### 2. For `physreason`

建议保留，但接受人工 review 成本；后续可尝试：

- 放宽部分 visual-density 风险阈值
- 对“文本足够 + 可解性满分”的题提高 pass 倾向

### 3. For `multi_physics`

建议：

- 直接降权
- 或先做预过滤，只保留：
  - 抽象坐标图
  - 明确变量定义的图像题
- 对“场景截图 / 图中隐式条件多 / 文本不自足”的样本直接过滤

### 4. For reporting / benchmarking

后续如果要做公开 benchmark 或阶段汇报，这次 rerun 的定位建议写成：

> **Pipeline execution is now stable under proxy-enabled long runs. The main remaining challenge is not runtime failure, but dataset-dependent conservatism: some geometry-heavy datasets are over-reviewed, while visually underspecified physics sets remain structurally incompatible with the current open-ended cleaning target.**
