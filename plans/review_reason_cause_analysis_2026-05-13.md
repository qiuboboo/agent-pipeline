# Review 原因来源与分布分析（2026-05-13）

## 1. 关键解释：alignment/review 不是单一原因

`alignment_requires_review` 或“对齐不一致”不是单纯等价于模型识别错误，而是一个混合 review 信号。它通常来自三类问题：

### 1.1 模型视觉识别 / grounding 问题

这类是真正和模型视觉理解相关的问题，包括：

- 图片里的关键对象、点、线、角、标签没有被稳定识别；
- 多图拼接时，模型无法判断题目对应哪个子图；
- 图片低清、裁切、小字、遮挡导致 OCR/视觉理解不稳定；
- grounded visual path 找不到、找错，或视觉证据偏弱；
- 图中文字或符号识别错误。

这类问题反映的是视觉模型或 grounding 模块的不确定性。

### 1.2 原始数据 / metadata 对齐问题

这类不是模型识别错，而是原始数据记录或导出格式不一致：

- metadata 中的 image path 和 top-level image path 不一致；
- 原始图片字段是 `<PIL.Image ...>` 这类对象字符串，不是稳定文件路径；
- 图片资产实际存在，但 metadata 没有正确指向；
- 图片、题干、答案字段来自不同导出链路，字段间不同步；
- image reference / image id / local artifact path 之间存在记录偏差。

这类更像数据工程问题，模型本身未必识别错。

### 1.3 原始选择题结构 / 答案映射问题

很多 review 来自原始选择题格式不完整或答案映射不可靠：

- 选项文本缺失；
- 答案只剩 `A/B/C/D` 或组合字母；
- gold answer、answer annotation、解析末尾“故选 X”不一致；
- 原题依赖选项，但 pipeline 没有拿到完整选项；
- rewrite expected answer 与原始 answer annotation 冲突。

这类问题通常不是视觉模型识别错误，而是原始选择题封装/标注不完整。

## 2. 改写对 review 问题的规避作用

改写成开放题后，确实可以规避一大部分原始选择题和 metadata/alignment 类问题。核心原因是：

- 改写题有完整 `rewritten_question_text`；
- 改写题有显式 `expected_answer`；
- 不再依赖 A/B/C/D 选项映射；
- 不再直接信任原始 gold answer 或解析末尾选择项；
- 如果题干完整、答案可验证、图片支持足够，则原始选择题的选项缺失/answer mapping 不一致可以变成非致命风险。

但改写不能自动修复真正的语义风险：

- 关键条件缺失；
- 图文语义冲突；
- 目标图不可定位；
- 答案冲突或多解；
- split variant 未确认；
- 单位、符号、相似对应顺序等会改变答案的歧义。

因此当前 release policy 的原则是：**释放非致命工程/记录风险，保留真实语义风险。**

## 3. 后续统计口径

为了汇报导致 review 的原因分布，可以把原始 reason code 归并为以下几类：

1. **alignment / grounding 类**：alignment_requires_review、missing_grounded_visual_path、visual_grounding_uncertain、grounding_path_uncertain 等；
2. **视觉质量类**：low_resolution、small_image、visual_evidence_weak、visual_evidence_uncertain、crop/label/small text 等；
3. **metadata / path 类**：metadata_inconsistency、image_path_mismatch、metadata_image_path_mismatch 等；
4. **答案/标注冲突类**：answer_annotation_inconsistent、gold_answer_mismatch、rewrite_expected_answer_mismatch、answer_key_conflict 等；
5. **选项/选择题结构类**：missing_choice_options、missing_option_text、choice_field null、letter-only answer 等；
6. **rewrite 完整性/可理解性类**：agent_complete、agent_understandable、rewrite_complete、target_clear、answer_verifiable 未通过；
7. **split / 多子题类**：split、split_variant_needs_review、split_open_rewrite、split_variant_incomplete；
8. **核心语义风险类**：semantic_core_bad、key_condition_requires_image_or_recovery、question_text_incomplete、image-text conflict、answer conflict 等。

