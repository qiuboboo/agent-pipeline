# 优先数据集 20 条采集清洗功能报告

- pipeline_run_id：`run_f2958f3118292117`
- 运行目录：`benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117`
- 生成时间：`2026-03-25T08:55:40Z`
- 说明：本报告完全基于既有运行结果生成，只新增报告文件，不改动 pipeline 实现。

## 1. 总体结果概览

| 数据集 | 处理数 | pass | review | reject | 主要改写策略 | 主要对齐状态 | 常见原因码 | 逐样本报告 |
|---|---:|---:|---:|---:|---|---|---|---|
| SCEMQA | 20 | 2 | 0 | 18 | blank_open:11, split_open:9 | good:18, bad:2 | low_resolution:17, meets_cleaning_requirements:2, missing_grounded_visual_path:2 | [查看](datasets/scemqa.md) |
| Geometry3K | 20 | 2 | 1 | 17 | blank_open:10, keep_open:10 | bad:17, good:3 | missing_grounded_visual_path:17, text_image_misaligned:17, answer_not_verifiable:10 | [查看](datasets/geometry3k.md) |
| CMM-Math | 20 | 13 | 6 | 1 | split_open:7, blank_open:13 | good:19, bad:1 | meets_cleaning_requirements:13, split_variant_needs_review:6, missing_core_field:1 | [查看](datasets/cmm_math.md) |
| MathVision | 20 | 11 | 3 | 6 | keep_open:13, blank_open:6, split_open:1 | good:20 | meets_cleaning_requirements:11, low_resolution:6, normalized_question_incomplete:2 | [查看](datasets/mathvision.md) |
| PhysReason | 20 | 4 | 11 | 5 | keep_open:20 | risky:12, good:8 | alignment_risky:11, low_resolution:5, meets_cleaning_requirements:4 | [查看](datasets/physreason.md) |

## 2. 功能视角总结

### SCEMQA

- 清洗结果：`pass=2`，`review=0`，`reject=18`。
- 开放化改写：主要策略为 `blank_open:11, split_open:9`。
- 对齐状态：`good:18, bad:2`。
- 高频原因码：`low_resolution:17, meets_cleaning_requirements:2, missing_grounded_visual_path:2, text_image_misaligned:2`。
- 观察：该源可以稳定接入，但 20 条里大多数被清洗门控拒绝；说明当前主要问题不在“接不到数据”，而在图像质量与后续保留阈值较严格。

### Geometry3K

- 清洗结果：`pass=2`，`review=1`，`reject=17`。
- 开放化改写：主要策略为 `blank_open:10, keep_open:10`。
- 对齐状态：`bad:17, good:3`。
- 高频原因码：`missing_grounded_visual_path:17, text_image_misaligned:17, answer_not_verifiable:10, missing_answer:10, missing_core_field:10`。
- 观察：存在 `10` 条题面仍呈现 `text/bar` 等占位符，说明该源的结构化字段发现虽然能跑通，但部分题目仍会在题面抽取与图文对齐阶段失真。

### CMM-Math

- 清洗结果：`pass=13`，`review=6`，`reject=1`。
- 开放化改写：主要策略为 `split_open:7, blank_open:13`。
- 对齐状态：`good:19, bad:1`。
- 高频原因码：`meets_cleaning_requirements:13, split_variant_needs_review:6, missing_core_field:1, missing_core_image:1, missing_grounded_visual_path:1`。
- 观察：这是本轮最稳定的文本数学源之一，通过率最高，说明题面/答案字段抽取、规范化和开放化改写在该源上已经较成熟。

### MathVision

- 清洗结果：`pass=11`，`review=3`，`reject=6`。
- 开放化改写：主要策略为 `keep_open:13, blank_open:6, split_open:1`。
- 对齐状态：`good:20`。
- 高频原因码：`meets_cleaning_requirements:11, low_resolution:6, normalized_question_incomplete:2, split_variant_needs_review:1`。
- 观察：该源表现出明显的混合改写策略特征，既有 `keep_open`，也有 `blank_open` 与少量 `split_open`，符合“按题型分流”的预期。

### PhysReason

- 清洗结果：`pass=4`，`review=11`，`reject=5`。
- 开放化改写：主要策略为 `keep_open:20`。
- 对齐状态：`risky:12, good:8`。
- 高频原因码：`alignment_risky:11, low_resolution:5, meets_cleaning_requirements:4`。
- 观察：该源已经能稳定跑通 20 条，但以 `review` 为主，主因不是字段缺失，而是图文对齐风险偏高，说明它更像“可进入人工复核”的中间状态数据源。

## 3. 采集与清洗功能拆解

### 3.1 采集接入
- 五个优先数据集均已成功跑通到样本级输出，说明连接器、抽样、图片 materialization 与样本 bundle 写盘链路均可用。
- `SCEMQA / CMM-Math / MathVision / PhysReason` 本轮均达到了 `processed_samples = 20`；`Geometry3K` 也完整跑到 20 条。

### 3.2 规范化
- 每个样本都能产出原始题面/答案与规范化题面/答案，可直接对照“处理前 / 处理后”。
- 报告中逐条展示了 `raw_question_text`、`normalized_question_text`、`raw_answer_text`、`normalized_answer_text`。

### 3.3 开放化改写
- 每个样本都提供至少一个开放题变体，因此可以直接对照“改写前 / 改写后”。
- 不同数据集的主策略差异明显：`SCEMQA` 偏 `blank_open/split_open`，`CMM-Math` 偏 `blank_open/split_open`，`MathVision` 混合，`PhysReason` 基本全部 `keep_open`。

### 3.4 图像处理
- 对含图样本，报告展示了原始图像来源、持久化主图与 ROI 裁剪图。
- 对 Hugging Face inline image 样本，原始图像有时只有 `inline://pil_image` 这类源标记，因此报告将持久化主图作为主要可视证据。

### 3.5 图文对齐与可解性
- 本轮总体对齐状态分布：`{"good": 68, "bad": 20, "risky": 12}`。
- `Geometry3K` 与 `PhysReason` 更容易在这一层触发 `bad / risky`，前者偏字段异常，后者偏复杂图文联合。

### 3.6 清洗门控
- 本轮总体决策分布：`{"reject": 47, "pass": 32, "review": 21}`。
- `CMM-Math` 与 `MathVision` 的可保留比例相对更高；`SCEMQA` 与 `Geometry3K` 当前仍偏保守；`PhysReason` 更倾向进入 `review` 而非直接 `reject`。

## 4. 逐样本报告入口

- [SCEMQA](datasets/scemqa.md)
- [Geometry3K](datasets/geometry3k.md)
- [CMM-Math](datasets/cmm_math.md)
- [MathVision](datasets/mathvision.md)
- [PhysReason](datasets/physreason.md)

