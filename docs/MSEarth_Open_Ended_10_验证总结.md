# MSEarth Open Ended 前 10 条验证总结

## 1. 运行概览

> 说明：本总结参照 10 条验证总结的写法整理，但当前并不是一个单独命名为 `validation_10` 的 run；而是基于以下合并产物中的前 10 条样本（`source_problem_id=0~9`）做同口径验证汇总。

- 基础产物目录：`outputs/msearth_open_ended_merged_0000_0120_ler_reasoning_chain/run_merged_msearth_open_ended_0000_0120_ler_reasoning_chain`
- 数据集：MSEarth Open Ended
- 验证样本数：10
- 实际处理样本数：10
- 结果分布：`pass=6`，`review=4`，`reject=0`
- 改写策略分布：`keep_open=10`
- 清洗路径分布：`multimodal_full=7`，`text_lightweight=3`
- `requires_image` 分布：`true=7`，`false=3`

## 2. 整体结论

这 10 条样本的接入、清洗、改写与记录链路均已跑通。

从结果看：

- MSEarth Open Ended 的原始题型本身就接近开放问答，因此这 10 条全部采用 `keep_open`，没有出现 `blank_open` / `split_open`。
- 样本内部明显分成两类：
  - **text_lightweight**：题面本身已足够表达问题，图像不是必需输入；
  - **multimodal_full**：问题依赖图中标签、区域、曲线或地理对象，需要保留图像 grounding。
- 进入 `review` 的 4 条，不是因为缺图、缺答案或改写失败，而主要是因为：
  - `alignment_requires_review`
  - `missing_grounded_visual_path`
- `pass` 的 6 条中，既包含 **文本已足够的 text-dominant 样本**，也包含 **图文对应关系较清楚的 multimodal 样本**。

因此，这轮结果可以作为 **MSEarth Open Ended 已可稳定产出开放题样本** 的验证依据；但对于强视觉依赖、视觉锚点较弱的题，还需要进一步补 grounding 约束。

## 3. 改写前后汇总

| source_problem_id | cleaning_path | 策略 | 结果 | 改写前 | 改写后 | 图片名 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | text_lightweight | keep_open | pass | Which historical periods contributed to the construction of Suoyang Ancient City? | Which historical periods contributed to the construction of Suoyang Ancient City? | `prob_d15cedaaf690d60a9e4d4150_primary.png` |
| 1 | multimodal_full | keep_open | pass | What do the annotated lines in the echograms represent? | What do the annotated lines in the echograms represent? | `prob_b73948eb1c4accd9a3d48772_primary.png` |
| 2 | multimodal_full | keep_open | pass | What type of eddy is labeled 'FE'? | What type of eddy is labeled 'FE'? | `prob_c207cd31002b7ef2b68a59a3_primary.png` |
| 3 | multimodal_full | keep_open | review | What influences IMERG-FCal's smaller accumulation? | What influences IMERG-FCal's smaller accumulation? | `prob_cb78de621502a670ebeeb5ef_primary.png` |
| 4 | multimodal_full | keep_open | pass | Caption: Study area: FCC of a part of San Francisco city. Zoomed image of the urban area (marked with rectangles in inset) shows mixing of substrate with vegetation, roads, shadow and dark objects. Question: What type of landscape does the highlighted San Francisco area represent? | Caption: Study area: FCC of a part of San Francisco city. Zoomed image of the urban area (marked with rectangles in inset) shows mixing of substrate with vegetation, roads, shadow and dark objects. Question: What type of landscape does the highlighted San Francisco area represent? | `prob_e457d4df3974cabc6de72956_primary.png` |
| 5 | multimodal_full | keep_open | review | Which wetland type transitions into flooded wetlands? | Which wetland type transitions into flooded wetlands? | `prob_9c51aa977b211a2876d79f6a_primary.png` |
| 6 | multimodal_full | keep_open | review | What indicates the thermal boundary in winter? | What indicates the thermal boundary in winter? | `prob_ef3fe92608c514feb95c0e40_primary.png` |
| 7 | text_lightweight | keep_open | pass | What body of water borders the Lanyang Plain to the east? | What body of water borders the Lanyang Plain to the east? | `prob_f4668e231278f2c0f58a0168_primary.png` |
| 8 | multimodal_full | keep_open | review | What is the orientation of the transverse dunes? | What is the orientation of the transverse dunes? | `prob_0b1da42f819f17ad46476b6c_primary.png` |
| 9 | text_lightweight | keep_open | pass | What is the minimum horizontal sampling distance of the model results? | What is the minimum horizontal sampling distance of the model results? | `prob_04030acd59250a212145d242_primary.png` |

## 4. review 样本说明

以下 4 条进入 `review`：

- `source_problem_id=3`
- `source_problem_id=5`
- `source_problem_id=6`
- `source_problem_id=8`

它们的共同特点是：

- 都走了 `multimodal_full`
- 都是 **问题语义依赖图像**，但题干里的显式视觉锚点仍偏弱
- `alignment_status` 均为 `bad`
- 都命中了 `missing_grounded_visual_path`

更细一点看：

- `source_problem_id=3`：额外命中 `domain_inference_risk`，说明需要依赖领域推断才能把图与答案稳定对应起来。
- `source_problem_id=5`：额外命中 `answer_target_inferable_but_not_explicit`、`question_image_term_mismatch`，说明题面虽然可读，但图中真正对应的目标对象并不够直接。
- `source_problem_id=6`：额外命中 `domain_inference_required`，说明不是单纯看图即可，需要额外解释“thermal boundary / 20°C isotherm”的对应关系。
- `source_problem_id=8`：核心问题是方向类问题（orientation）对图像依赖很强，但当前视觉 grounding 还不够稳。

## 5. pass 样本说明

以下 6 条直接 `pass`：

- `source_problem_id=0`
- `source_problem_id=1`
- `source_problem_id=2`
- `source_problem_id=4`
- `source_problem_id=7`
- `source_problem_id=9`

这些样本可以进一步分成两类：

### 5.1 text_lightweight 直接通过
- `source_problem_id=0`
- `source_problem_id=7`
- `source_problem_id=9`

这类样本的共同特点是：

- 题面本身已经足够表达问题
- `requires_image=false`
- `alignment_status=good`
- 更适合走文本主导的轻量清洗路径

### 5.2 multimodal_full 但 grounding 较稳
- `source_problem_id=1`
- `source_problem_id=2`
- `source_problem_id=4`

这类样本的共同特点是：

- 问题确实依赖图像
- 但图文对应关系较清晰
- 可以稳定形成 `pass`

其中 `source_problem_id=4` 是一个比较好的正例：

- 题面保留了 `Caption + Question`
- 图像区域与问题对象的对应关系更明确
- 最终可以稳定通过

## 6. 本次发现的问题

### 6.1 MSEarth 内部同时存在“文本足够”和“强视觉依赖”两类样本
这说明后续不能把 MSEarth Open Ended 简单当成单一类型数据：

- 一部分样本更像 **text-dominant open QA**
- 一部分样本更像 **image-grounded science QA**

后续如果继续扩规模，建议分开统计：

- `text_lightweight` 的 pass / review / reject
- `multimodal_full` 的 pass / review / reject

### 6.2 review 的主阻塞不是改写失败，而是视觉 grounding 不足
当前前 10 条里：

- 没有出现 rewrite strategy 异常
- 没有出现 `llm_used: false` 的 normalization 失败样本
- review 的主因集中在图文对齐与视觉锚点不足

这说明当前 MSEarth Open Ended 的主要瓶颈不是“题不会改写”，而是：

> 对于依赖图中对象、方向、区域、曲线关系的问题，现有清洗链路还不够稳定地给出 grounded visual path。

### 6.3 supporting context / caption 是否保留，会直接影响 grounding 完整度
从当前样本可以看到两种情况并存：

- 有的样本题面只保留简短问题句；
- 有的样本会保留 `Caption + Question`，可为答案提供更完整支撑。

这意味着后续在处理 MSEarth Open Ended 时，需要继续关注：

- caption 是否在接入 / normalization 阶段被裁掉
- 当答案依赖 supporting context 时，是否应作为结构化字段保留，而不是只留下短问题句

## 7. 结论建议

MSEarth Open Ended 当前已经具备继续扩大样本规模的基础，但后续推进时建议分两类看：

- **text_lightweight + pass**：可直接进入后续链路
- **multimodal_full + review**：建议单独汇总复核，并重点补强视觉 grounding 证据

如果后续继续跑更大规模批次，优先建议关注：

1. 强图像依赖但视觉锚点表达较弱的样本；
2. 方向、区域、曲线、图中标签识别类问题；
3. caption / supporting context 对答案有关键贡献的样本。
