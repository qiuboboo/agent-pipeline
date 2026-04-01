# EEE-Bench 图像样本在 text_lightweight 路径下未生成 visual_structure_records 的记录

## 问题概述

在 `EEE-Bench` 的批量运行结果中，发现少量样本存在如下现象：

- `has_image = true`
- `image_count = 1`
- 但 `visual_structure_records.jsonl` 中没有对应记录

初看像是视觉结构解析缺失，但进一步排查后确认，这不是运行失败，也不是图像资产丢失，而是当前 pipeline 在“原始资产是否有图”和“语义上是否需要视觉解析”之间使用了不同口径，导致完整性检查容易出现误报。

补充说明：本次发现的受影响样本均已正常 `clean pass`，并进入 `ready_for_annotation`，因此不影响当前产出的可用性。

---

## 影响范围

本次排查基于：

- 输出目录：`agent-pipeline/outputs/eee_bench_batched_eval`
- 批次范围：`30:300`

发现 2 个批次存在该现象：

1. `0130_0150`
2. `0190_0210`

对应表现：

- 两个批次都应有 20 个样本
- 但 `visual_structure_records.jsonl` 只有 19 行
- 其他核心记录（如 `candidate_problem_records.jsonl`、`clean_problem_records.jsonl`、`alignment_records.jsonl`、`rewrite_reports.jsonl`、`solvability_reports.jsonl`）仍然完整

---

## 受影响样本

### 批次 `0130_0150`

- 缺失 visual record 的样本：`source_problem_id = 15`
- `problem_id = prob_b3609cf48f268bf958982d2c`

该样本特征：

- 原始资产中存在 1 张图
- `requires_image = false`
- `text_dominant = true`
- `cleaning_path = text_lightweight`
- `solvability path_mode = text_only`

附加信息：

- metadata 中提到源记录包含 PIL image placeholder
- 未提取到显式 image path / URL
- 题目本身是文本即可求解的 buck converter 计算题

### 批次 `0190_0210`

- 缺失 visual record 的样本：`source_problem_id = 11`
- `problem_id = prob_e8b03232874c2e6e323b11c2`

该样本特征：

- 原始资产中存在 1 张图
- `requires_image = false`
- `text_dominant = true`
- `cleaning_path = text_lightweight`
- `solvability path_mode = text_only`

附加信息：

- 原始图像资产存在
- `asset_registry_records` 正常
- 题目内容本身可以按文本处理，不依赖图像求解

---

## 原因分析

当前 pipeline 中，存在两套容易混淆的语义：

### 1. 原始资产层面是否有图

由以下字段体现：

- `has_image`
- `image_count`

这表示源样本是否携带图像资产。

### 2. 清洗/求解语义层面是否需要图

由以下字段体现：

- `requires_image`
- `text_dominant`
- `cleaning_path`
- 是否生成 `visual_structure_records`

这表示在当前清洗策略下，样本是否真的需要图像解析。

这两者并不总是一致。

---

## 代码定位

相关逻辑位于：

- `agent-pipeline/src/benchmarkallinone/pipeline.py`

### 关键逻辑 1：`text_lightweight` 会强制视为不需要图

在 normalization 结果处理后：

- 如果 `cleaning_path == "text_lightweight"`
  - `text_dominant = True`
  - `requires_image = False`

也就是说，最终是否需要图，取决于 cleaning path，而不是原始是否带图。

### 关键逻辑 2：`text_dominant` 样本直接跳过视觉解析

后续代码中：

- `visual_structures = [] if text_dominant else self.visual_parser.parse_many(...)`

因此，只要样本被判定为 `text_lightweight`，即使原始样本中带图，也不会生成 `visual_structure_records`。

---

## 当前判断

这不是以下问题：

- 不是 pipeline 运行失败
- 不是 visual parser 崩溃
- 不是图像资产丢失
- 不是样本处理过程中断

更准确地说，这是一个：

> 记录语义与完整性校验口径不一致的问题

也就是：

- 样本原始资产里有图
- 但清洗阶段判定这题不依赖图
- 所以系统有意跳过视觉结构生成
- 但下游如果仅按 `image_count > 0` 检查，就会误判成 visual record 缺失

---

## 影响评估

目前看该问题：

### 不影响

- 最终样本可用性
- 批量任务完整跑通
- 题目通过/复核决策结果

### 会影响

- 完整性检查结果的可解释性
- QA / 调试时对 visual record 数量的理解
- 对“有图样本是否一定有 visual record”这一口径的统一认知

---

## 建议修复方向

### 方案 A：调整完整性校验口径

不要用 `image_count > 0` 来判断是否必须存在 `visual_structure_records`。

建议改为：

- 只有 `requires_image == true` 时，才要求必须存在视觉结构记录

### 方案 B：增加显式跳过原因字段

建议增加类似字段：

- `visual_parse_skipped = true`
- `visual_parse_skipped_reason = "text_lightweight"`

这样即使样本带图，但没有 visual record，也能明确知道是“有意跳过”，不是异常缺失。

### 方案 C：拆分原始图像与语义图像概念

例如区分：

- `raw_image_count`
- `requires_image`
- `parsed_visual_count`

这样统计、校验和调试时都会更清晰。

---

## 推荐方案

优先建议：

- **方案 A：调整校验口径**
- **方案 B：增加跳过原因字段**

这是最小改动、收益最高的方式。

---

## 结论

本问题本质上是：

> 样本原始资产中带图，但清洗阶段判定该题可按文本处理，因此没有生成 `visual_structure_records`

所以这是一个**记录语义与校验逻辑不一致**的问题，而不是运行故障。

后续如果需要，可直接基于本文档整理为 GitHub issue。
