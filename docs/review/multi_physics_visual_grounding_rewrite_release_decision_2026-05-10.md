# Multi-Physics 视觉落点类改写题放行决策记录（2026-05-10）

## 适用范围

本记录适用于当前本地正式 `multi_physics_*` outputs。构建候选时显式排除了 `smoke_multi_physics*` 测试输出，避免测试样本抢占正式 `source_problem_id`。

本次判断的核心问题是：`multi_physics` 的 review 比 `geoqa_plus` 和 `mm_math` 更复杂，剩余 review 中大量样本涉及选择题选项缺失、答案 key 冲突、split-open 拆分题、rewrite target mismatch、文本缺字或图文语义冲突。这些不能按“改写后看起来可用”直接放行。

因此本次只放行一个白名单式的小桶：题目必须是非 split 的开放改写，且 review 原因只属于 alignment / visual grounding / low resolution 这类非致命风险。

## 放行策略

本次新增显式候选桶，而不是按 reason code 一刀切：

- 候选文件：`docs/review/multi_physics_visual_grounding_rewrite_candidates_2026-05-10.json`
- 候选 key：`multi_physics_visual_grounding_rewrite_candidates`
- policy bucket：`multi_physics.release_buckets.visual_grounding_rewrite_release`

候选样本必须满足：

- 来自正式 `multi_physics_*` 输出，不来自 smoke/test 输出。
- 原始 decision 为尚未被 A/B1/B2 释放的 `review`。
- 改写策略不是 `split_open`，且没有 `split_variant_needs_review`。
- 存在开放题改写，题干和 expected answer 都非空。
- `answer_verifiable=true`、`target_clear=true`、`rewrite_complete=true`。
- cleaning agent 判断为 `complete` 且 `understandable`。
- 图片支持状态为 `clear_enough` 或 `not_needed`。
- 仅允许 alignment、visual grounding、missing grounded visual path、low resolution、小图等非致命风险。

以下情况继续不放行：

- split-open 拆分题或 split variant 需要人工确认。
- 原始答案只是选择项字母/组合，且改写依赖选项内容恢复。
- 选项文本缺失、choice field 缺失、choice context 不完整。
- answer annotation / gold answer / rewrite expected answer 不一致。
- rewrite target mismatch、answer unit mismatch、notation ambiguity、partial answer signal。
- 题干关键条件缺失、文本 OCR 缺字、图文语义冲突、图片不可用或目标图无法定位。

## 数量统计

正式 `multi_physics_*` 输出按 `source_problem_id` 全局去重后：

- release 前选中：`1412`
- 原始 pass：`175`
- 原始 review：`1220`
- 原始 reject：`17`
- 已有 A/B1/B2 桶释放 review：`260`
- 本次 `visual_grounding_rewrite_release` 候选：`90`
- 预计 release 后可进入 ready：`525`
- 预计仍丢弃 review：`870`
- reject 仍不放行：`17`

已有桶释放分布：

- `A`：`194`
- `B1`：`61`
- `B2`：`5`

本次候选桶主要 reason code 组合：

- `alignment_requires_review + visual_grounding_uncertain`：`33`
- `alignment_requires_review + grounding_path_uncertain`：`11`
- `alignment_requires_review + missing_grounded_visual_path + visual_evidence_uncertain`：`8`
- `alignment_requires_review + missing_grounded_visual_path + visual_evidence_weak`：`6`
- `alignment_requires_review + visual_grounding_weak`：`4`

本次候选桶主要风险标记：

- 无额外 `quality_risk_flags`：`52`
- `visual_evidence_weak`：`20`
- `low_resolution`：`7`
- 其它小图/低清/小字类风险：少量。

## 抽样例子

### `prob_9c68f1d5d2d91a3145ac9f81` / source `180`

- 自动状态：`review`
- 风险标记：`alignment_requires_review`, `grounding_path_missing`
- 原题：磁铁从螺线管正上方由静止释放，向下穿过螺线管，判断相关物理现象。
- 改写题：磁铁刚离开螺线管时，其加速度与重力加速度有什么关系？
- expected answer：磁铁刚离开螺线管时的加速度小于重力加速度。
- 判断：改写目标清楚，答案不是选项字母，风险主要是视觉/落点证据不足，可放行。

### `prob_95298421bbf0f5af19f8ebe3` / source `743`

- 自动状态：`review`
- 风险标记：`alignment_requires_review`, `grounding_path_uncertain`
- 原题：两个半圆形光滑圆管相切，小球从一个圆管进入另一个圆管后判断运动变化。
- 改写题：小球由圆管 `ab` 进入圆管 `bc` 后，向心加速度如何变化？
- expected answer：向心加速度变小。
- 判断：开放题目标和答案明确，不依赖缺失选项；视觉落点不确定但不改变题意。

### `prob_5a2135b7cacd7b79c1dd709f` / source `581`

- 自动状态：`review`
- 风险标记：`alignment_requires_review`, `grounded_visual_path_missing`, `visual_evidence_weak`
- 原题：台秤上有盛水杯和被细绳系住的木球，细线断裂后判断台秤示数。
- 改写题：小木球上浮到水面的过程中，台秤示数如何变化？
- expected answer：变小。
- 判断：题干和答案自洽，图像风险是弱视觉证据，不是语义冲突。

### `prob_17a4de2676ab51413e84ef80` / source `data_7_00096`

- 自动状态：`review`
- 风险标记：`alignment_requires_review`, `visual_evidence_uncertain`, `visual_evidence_weak`
- 原题：静电除尘装置，判断 A、B 两端应接高压正负极。
- 改写题：A 端和 B 端应分别接高压的什么极？
- expected answer：A 端、B 端都接高压负极。
- 判断：选项文本在题干中可见，改写题给出具体目标和答案，不是仅保留选项字母。

## 不放行边界

本次明确不把以下更宽松候选纳入：

- `split_open` 或 `split_variant_needs_review`：虽然很多样本看起来可恢复，但拆分后的多个子题需要人工确认。
- 原始答案为 `AC`、`BD`、`D` 等选择项，而选项文本缺失或不稳定：这类不能只依赖模型补全。
- `answer_annotation_inconsistent`、`gold_answer_mismatch`、`rewrite_expected_answer_mismatch`：答案冲突风险高。
- `rewrite_target_mismatch`、`answer_unit_mismatch`、`notation_formatting_ambiguous`：看似小问题，但会直接影响物理量或答案表达。
- `text_extraction_missing_chars`、`question_text_incomplete`：题干条件可能缺失，不能自动放行。

## 执行结论

本次可以放行 `multi_physics_visual_grounding_rewrite_candidates` 中的 `90` 条。它们是白名单式显式候选，不代表所有 `multi_physics` review 都可释放。剩余 review 中仍有大量选择题上下文、答案一致性和 split-open 风险，应继续保留。
