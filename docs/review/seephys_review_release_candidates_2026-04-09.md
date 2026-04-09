# seephys review 放行候选（2026-04-09）

- canonical ready 包：`ready/seephys/run_outputs_merged_by_source_problem_id__seephys`
- 当前汇总：`pass=458 / review=126 / reject=16`
- 本页目的：从 `review=126` 中先导出 **相对可放行** 的候选，不等于全量放行。

## 分层规则

### A档：优先看，最保守
仅纳入以下 reason 组合：
- `alignment_requires_review`
- `alignment_requires_review + image_reference_metadata_issue`

**A档数量：`7`**

### B档：可扩展，但建议先抽查
仅纳入以下 reason 组合：
- `alignment_requires_review + missing_grounded_visual_path`

**B档数量：`21`**

### 暂不建议直接放行的类型
这些还不建议直接批量放：
- `multi_image_coordination_needed`
- 含 `visual_evidence_uncertain`
- 含 `missing_prior_context` / `question_incomplete`
- 含明显 `answer_*` 风险
- 图文不一致 / 目标不完整 / 上下文依赖类问题

人工接受状态说明：`1=pass`，`0=reject`，空白表示未看。

## A档（最保守，优先处理）

| problem_id | source_problem_id | 自动结果 | 人工接受状态 | reason codes | 原题简述 | 图片简略图 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| prob_d126c8b2b5654b762edcf9f6 | 248 | review |  | alignment_requires_review, image_reference_metadata_issue |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_d126c8b2b5654b762edcf9f6_primary.png) | alignment + 图像引用元数据问题；更像登记/引用瑕疵，不像实质内容缺失。 |
| prob_161ee87c7c2b428d2e7fad42 | 159 | review |  | alignment_requires_review |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_161ee87c7c2b428d2e7fad42_primary.png) | 仅剩 alignment review 标记；可作为首批最保守放行池。 |
| prob_8442b558d235997704d418d2 | 219 | review |  | alignment_requires_review |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_8442b558d235997704d418d2_primary.png) | 仅剩 alignment review 标记；可作为首批最保守放行池。 |
| prob_10f1623828cd1dcafabdc723 | 223 | review |  | alignment_requires_review |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_10f1623828cd1dcafabdc723_primary.png) | 仅剩 alignment review 标记；可作为首批最保守放行池。 |
| prob_b92e3d9a85794bcda58e0384 | 229 | review |  | alignment_requires_review |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_b92e3d9a85794bcda58e0384_primary.png) | 仅剩 alignment review 标记；可作为首批最保守放行池。 |
| prob_9bf1a290a2c7f3e3332edeb3 | 248 | review |  | alignment_requires_review |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_9bf1a290a2c7f3e3332edeb3_primary.png) | 仅剩 alignment review 标记；可作为首批最保守放行池。 |
| prob_243cad17ebb0785d5dc25918 | 41 | review |  | alignment_requires_review, image_reference_metadata_issue |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_243cad17ebb0785d5dc25918_primary.png) | alignment + 图像引用元数据问题；更像登记/引用瑕疵，不像实质内容缺失。 |

## B档（可扩展，建议先 spot-check）

| problem_id | source_problem_id | 自动结果 | 人工接受状态 | reason codes | 原题简述 | 图片简略图 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| prob_f507ee59c5cd02ece288ae97 | 198 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_f507ee59c5cd02ece288ae97_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_bfd56b3dae576cc89eaecc8e | 132 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_bfd56b3dae576cc89eaecc8e_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_205a361b37226df4e789e88d | 135 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_205a361b37226df4e789e88d_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_fb46368fb928b443a8748eb5 | 138 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_fb46368fb928b443a8748eb5_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_cd5deba11e082921b43251db | 141 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_cd5deba11e082921b43251db_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_f3da96f04962061ade2cbcc8 | 142 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_f3da96f04962061ade2cbcc8_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_407d1ce9fda0e74aa57982f2 | 144 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_407d1ce9fda0e74aa57982f2_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_392827b415a21290b058f035 | 158 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_392827b415a21290b058f035_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_b3c2798ff2028a43c837d45e | 200 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_b3c2798ff2028a43c837d45e_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_a82331fb6bbfdc320b9bb366 | 208 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_a82331fb6bbfdc320b9bb366_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_e6475b35d9071c4622c17065 | 217 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_e6475b35d9071c4622c17065_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_8c908645f223f65462e58466 | 220 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_8c908645f223f65462e58466_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_0046bd6c10f2b6068cb8c73d | 235 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_0046bd6c10f2b6068cb8c73d_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_a90bce8cefd1a3468e7d1dd3 | 236 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_a90bce8cefd1a3468e7d1dd3_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_6a4a1b5ae9c178908b05e528 | 239 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_6a4a1b5ae9c178908b05e528_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_c085e23336a7ef03e38000c4 | 240 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_c085e23336a7ef03e38000c4_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_1787323387b5dc036135a180 | 254 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_1787323387b5dc036135a180_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_deae10736bb795cb8d96a9f2 | 271 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_deae10736bb795cb8d96a9f2_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_b2b7b52260f6919f2eeb21ee | 282 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_b2b7b52260f6919f2eeb21ee_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_95e307143d22db188a52f5df | 284 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_95e307143d22db188a52f5df_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
| prob_fe2c263d645044b39722c09f | 286 | review |  | alignment_requires_review, missing_grounded_visual_path |  | ![](../ready/seephys/run_outputs_merged_by_source_problem_id__seephys/datasets/seephys/artifacts/images/prob_fe2c263d645044b39722c09f_primary.png) | 常见组合；从抽样看不少是 grounding/path 记录问题，但仍建议抽查后放。 |
