# Pipeline1 / Outputs / Review Release / Ready Data PPT Plan

生成时间：2026-05-13

## 1. 汇报主线

本次 PPT 不以脚本和文件细节为主，而是围绕“数据资产是如何生产出来的，以及最终数据有什么特征”展开。

建议主线：

1. Pipeline1 如何把原始样本加工成结构化 outputs。
2. outputs 层面的平均请求与耗时量级。
3. 从 outputs 到 ready 的选择、合并、去重和质量门控。
4. 重点说明 review release / 放行规则。
5. 最后重点讲 ready 数据资产的 taxonomy 与数据特征。

推荐页数：6 页左右。

## 2. 推荐 PPT 结构

### 第 1 页：Pipeline1 简单流程

标题建议：

> Pipeline1: 从原始样本到结构化 outputs

流程：

```text
Raw source samples
        ↓
Source intake / normalization
        ↓
Prompt construction
        ↓
Model rewrite / answer normalization
        ↓
Image artifact collection
        ↓
Cleaning & validation
        ↓
outputs/
```

重点说明：

- Pipeline1 的目标不是直接得到最终 ready，而是生成带有改写、图片资产、质量标记和 provenance 的结构化 outputs。
- outputs 中包含 rewritten question、expected answer、image artifacts、cleaning decision、reason codes、metadata / provenance 等。

### 第 2 页：Pipeline1 outputs 平均成本

由于本地 outputs 不完整，且包含历史 run、重复 run、preview run，因此不建议使用 outputs 总量作为正式成本口径。更适合使用平均口径。

当前本地有效 run summary 统计口径：

- 仅统计 `outputs/**/summary.json` 中 `processed_samples > 0` 的 top-level run summary。
- 有效 run summary：113
- processed samples：9,768
- request_count：73,556
- total_request_seconds：880,942.2 秒

平均指标：

| 指标 | 值 |
| --- | ---: |
| 平均请求 / sample | 7.53 |
| 平均文本请求 / sample | 5.62 |
| 平均多模态请求 / sample | 1.91 |
| 平均请求耗时 / sample | 90.2 秒 |
| 平均请求耗时 / request | 12.0 秒 |

Token 统计口径：

- 早期 run 很多 token 字段为 0，只有部分 run 返回 usage。
- 只看有 token usage 的 run：37 个 run，730 个 processed samples。
- total tokens：8,631,428
- 平均 tokens / sample：11,824
- 平均 tokens / request：1,672

PPT 表述建议：

> outputs 记录了 run-level LLM usage。由于本地 outputs 不完整且历史 run 混杂，成本采用平均口径：每个样本约 7.5 次 LLM 请求，其中约 5.6 次文本请求、1.9 次多模态请求，累计请求耗时约 90 秒。有 usage 记录的子集中，每样本约 11.8k tokens。

### 第 3 页：Pipeline 节点平均请求数

在成功、无 retry、无 fallback 的理想条件下，每个主要 LLM agent 对一个样本通常只有 1 个请求。

典型主要 LLM agent：

| Agent / 节点 | 成功条件下请求数 |
| --- | ---: |
| NormalizationAgent | 1 |
| AssetRegistryAgent | 1 |
| PotentialScorerAgent | 1 |
| CandidateRegistrarAgent | 1 |
| RewriteAgent | 1 |
| SampleUnderstandingAgent | 1 |
| DecisionAgent | 1 |
| Text parser / visual parser / alignment / solvability | 0，本地/规则为主 |
| Image persistence / crop | 0，本地处理 |
| Source intake | 通常 connector/heuristic；某些路径可能 1 |

理论成功路径：

```text
7 个主要 LLM agent × 1 request ≈ 7 requests / sample
```

本地实测：

- 平均请求 / sample：7.53

解释：

- 理论成功路径约 7 次请求。
- 实测均值 7.53 次请求，多出的部分主要来自 retry、失败重试、JSON 解析失败、少量路径差异、历史 run 配置差异等。

若按 7 个主要 LLM 节点平均分摊：

| 指标 | 估计值 |
| --- | ---: |
| 请求 / 节点 / sample | 约 1.08 |
| 请求耗时 / 节点 / sample | 约 12.9 秒 |
| usage 子集 token / 节点 / sample | 约 1,689 tokens |

注意：sample record 中通常没有保存 per-node usage / elapsed_seconds，因此节点级成本是基于代码路径和 run-level usage 的估算；更可靠的实测口径是每样本约 7.5 次请求、90 秒累计请求耗时。

### 第 4 页：Outputs → Ready 构建规则

标题建议：

> Outputs → Ready: selection, merge, dedup, quality gate

流程：

```text
outputs from multiple runs
        ↓
select canonical runs / ranges
        ↓
merge by source_problem_id
        ↓
deduplicate by problem_id and content
        ↓
apply quality gate
        ↓
ready dataset
```

核心规则：

1. Selection：从多个 run/range 中选择 canonical 输出，避免历史 run 重复进入。
2. Merge & dedup：按 `source_problem_id`、`problem_id`、question+answer 内容等去重。
3. Quality gate：
   - `pass` 直接进入 ready；
   - `review` 默认不进入 ready；
   - 只有命中 release policy 的 review 才能进入 ready；
   - `reject` 不放行。

### 第 5 页：Review Release / 放行规则

标题建议：

> Review release policy: 释放非致命工程风险，保留语义风险

总规则：

```text
pass   → ready
review → ready only if matched release policy
reject → dropped
```

release policy 不是全局默认放行 review，而是统一框架 + 各数据集配置 release bucket / candidate subset。

#### 5.1 Structured release bucket

以 reason code 精确匹配为主，例如：

- `alignment_requires_review`
- `alignment_requires_review + missing_grounded_visual_path`

典型规则：

- MM-Math A：exact alignment-only review bucket。
- PhysReason A：exact alignment-only review bucket。
- AI2D / GeoQA-Plus / Multi-Physics A：exact alignment + missing grounded visual path bucket。

口径：

> 如果 review 只有轻度 alignment 或 grounding path 问题，且没有其它风险码，可以通过结构化规则放行。

#### 5.2 Explicit candidate subset

人工/规则挑选出的候选子集，例如：

- GeoQA-Plus rewrite release
- MM-Math strict rewrite release
- Multi-Physics visual-grounding rewrite release
- SeePhys A1

这类 release 通常需要检查：

- 改写题是否完整；
- 答案是否可验证；
- agent 是否理解；
- 是否排除了答案冲突、关键条件缺失、图文冲突等真实语义风险。

#### 5.3 不放行边界

以下风险不放行：

- 关键条件缺失；
- 答案冲突；
- 图文冲突；
- split variant 未确认；
- 选项缺失且答案只剩字母；
- rewrite 不完整或不可理解。

核心汇报句：

> Review release 不是放水，而是释放非致命工程/记录风险，保留真实语义风险。

#### 5.4 关键 release 数字

- GeoQA-Plus rewrite release：扫描 1000，候选 813，release review 812，最终 ready 2132。
- MM-Math strict rewrite release：release 前选中 4000，候选 1610，已有 A 桶释放 849，预计 ready 3750。
- Multi-Physics：原始选中 1412，原始 review 1220，已有 A/B1/B2 释放 260，visual grounding rewrite 候选 90，预计 ready 525，仍丢弃 review 870。
- 没有配置 release bucket 的数据集，例如 EEE-Bench，review 默认不放行，主要依赖原始 pass。

## 3. 没有 release rule 的 review 如何通过

结论：没有添加 release rule 的数据集，review 默认不能通过 ready gate。进入 ready 的样本主要是原始 clean decision 已经是 `pass` 的样本，而不是 review 被默认放行。

示例：`eee_bench`

- `configs/review_release_policies.yaml` 中 `eee_bench.release_buckets = {}`。
- 早期文档 `docs/review/eee_bench.md` 记录：
  - ready 包：`ready/eee_bench/run_merged_eee_bench_1000_2860_dedup`
  - review 样本数：285
  - 自动结果分布：`pass=667 / review=285 / reject=4`
- 因为没有 release bucket，285 个 review 默认不放行。

注意：后续 taxonomy 统计中 `eee_bench` 出现 2023 条，应该来自更完整的后续 ready/final taxonomy 统计，不是早期 review 台账中的 285 个 review 通过当前 release rule 放行得到。

## 4. Review 原因诊断

Review 原因不是单一“模型视觉识别错”，而是混合信号。

来源归因统计：

| 来源 | 原因出现次数占比 |
| --- | ---: |
| 文本/答案标注导致或相关 | 21.5% |
| 图片/视觉导致或相关 | 21.5% |
| 改写/结构处理导致或相关 | 18.1% |
| 混合 alignment 信号 | 14.7% |
| 原数据 metadata/path 导致 | 9.2% |
| 其他/需人工细看 | 15.0% |

解释：

1. 文本问题：选项缺失、答案字母映射不可靠、gold/annotation/rewrite answer 冲突。
2. 图片问题：低清、小图、小字、视觉证据弱、grounding path 不稳定。
3. 结构问题：split variant、多子题拆分、rewrite 不完整。
4. metadata/path 问题：原始图片路径、metadata 指向、source alignment 不稳定。

口径：

> 很多 review 来自原数据封装或选择题标注问题，改写成开放题后可以规避一部分；但关键条件缺失、答案冲突、图文冲突和 split 未确认仍然不放行。

改写/规则规避统计：

| 类型 | 占比 |
| --- | ---: |
| 通常可由改写/人工规则规避，若题干完整且答案可验 | 63.8% |
| 通常不能直接靠改写自动解决，需要继续 hold | 19.1% |
| 不确定，需要抽样判断 | 17.1% |

## 5. 最终 Ready 数据特征

总览：

- ready 总样本数：21,555
- 子数据集数：21
- 覆盖领域：Math、Physics、Chemistry、Biology、Geography、Circuit / Electronics
- 一级 taxonomy：14 类

14 个粗粒度一级 taxonomy：

1. 几何与空间推理
2. 代数、离散数学与应用数学
3. 实验、数据与图表解读
4. 力学与运动
5. 电磁、电路与电子系统
6. 波动、光学与声学
7. 热学、流体与气体
8. 物理综合与现代物理
9. 化学结构与分子表示
10. 化学反应、平衡与计算
11. 生命分子、细胞与遗传
12. 生态、生理与生命系统
13. 地球空间、气候与自然地理
14. 人文地理、资源与环境

Top taxonomy 分布：

- 几何与空间推理：40.9%
- 电磁、电路与电子系统：12.7%
- 力学与运动：12.3%
- 地球空间、气候与自然地理：5.9%
- 代数、离散数学与应用数学：5.5%
- 化学结构与分子表示：4.4%
- 生态、生理与生命系统：3.9%
- 生命分子、细胞与遗传：3.4%

结论：

> 最终 ready 集以视觉数学、物理力学、电磁电路为主体，同时覆盖化学结构、生命科学和地理类题目。

## 6. Dataset-level 特征

可以用 dataset × taxonomy heatmap 展示每个数据集的结构差异。

典型结论：

- `mm_math`：几乎全是几何与空间推理。
- `emma_chemistry`：几乎全是化学结构与分子表示。
- `physreason`：集中在力学与运动。
- `eee_bench`：集中在电磁、电路与电子系统。
- `geosqa`：自然地理 + 人文地理 + 图表。
- `phyx`：力学、波光声、热学、电磁都有。
- `sciverse_chemistry`：化学反应和化学结构都比较均衡。

口径：

> taxonomy 不只是分类，还能帮助识别数据集偏向，后续可用于采样平衡、模型能力诊断和低覆盖领域补齐。

## 7. 推荐最终 6 页版

1. Pipeline1 简单流程
2. Pipeline1 outputs 平均成本
3. Outputs → Ready 构建规则
4. Review release / 放行规则
5. Review 原因诊断
6. Ready taxonomy 与数据特征

如果需要 7 页，可以把第 6 页拆成：

6. Ready taxonomy 总体分布
7. Dataset-level heatmap / takeaway

## 8. 汇报关键词

- 结构化 outputs
- 平均每样本 7.5 次请求
- 成功路径每个主要 agent 约 1 次请求
- pass 直接进入 ready
- review 默认不进入 ready
- review 只有命中 release policy 才放行
- release 非致命工程风险，不释放真实语义风险
- ready 数据资产：21,555 samples / 21 datasets / 14 taxonomy classes
- taxonomy 支撑采样平衡、能力覆盖分析、错误归因和低覆盖领域补齐
