# seephys review 放行候选（2026-04-11）

- canonical ready 包：`ready/seephys_000_300`
- 候选来源：`/root/.openclaw/workspace/agent-pipeline/docs/review/seephys_A1_alignment_metadata_candidates_2026-04-11.json`
- 放行模板：`docs/review/review_release_template.md`
- 当前执行策略：拟议 **A1档**，即 `alignment_requires_review` 中经人工审查筛出的 metadata / image-reference misfire 子集。
- 当前状态（2026-04-11）：**候选已导出，尚未执行 manual release**。
- 当前汇总：`pass=243 / review=56 / reject=1`
- 拟议放行 basis：hand-curated alignment metadata/image-reference misfire subset

## A1档（拟议首桶，尚未执行）

人工接受状态说明：`1=pass`，`0=reject`，空白表示尚未执行。

| # | file | source_split | source_problem_id | problem_id | candidate_id | reason_codes | quality_risk_flags | 人工接受状态 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `prob_cb06ae7fc6ad04249fbea340.json` | `train[0:300]` | `200` | `prob_cb06ae7fc6ad04249fbea340` | `cand_cb06ae7fc6ad04249fbea340` | `alignment_requires_review, visual_grounding_incomplete` | `metadata.image_paths contains a PIL image object string representation rather than a file path or URL` |  | 倾向 metadata / image-reference misfire；待最终确认是否放行。 |
| 2 | `prob_d126c8b2b5654b762edcf9f6.json` | `train[0:300]` | `248` | `prob_d126c8b2b5654b762edcf9f6` | `cand_d126c8b2b5654b762edcf9f6` | `alignment_requires_review, image_reference_metadata_issue` | `metadata.image_paths contains a PIL image object string rather than a concrete file path or URL` |  | 题面已显式给出大部分几何关系；待最终确认是否放行。 |
| 3 | `prob_ed70836971fe6a4d95fd6fe1.json` | `train[0:300]` | `95` | `prob_ed70836971fe6a4d95fd6fe1` | `cand_ed70836971fe6a4d95fd6fe1` | `alignment_requires_review, image_relevance_mismatch` | `image_relevance_mismatch, metadata.extraction_notes states the question text does not explicitly mention the figure while related metadata marks image relevance as essential, metadata.image_paths contains PIL object string representations rather than concrete file paths or URLs` |  | 题面基本自洽，图像看起来不像唯一信息源；待最终确认是否放行。 |
| 4 | `prob_ee96a4b7c08cafe5a4d0c742.json` | `train[0:300]` | `12` | `prob_ee96a4b7c08cafe5a4d0c742` | `cand_ee96a4b7c08cafe5a4d0c742` | `alignment_requires_review, image_reference_uncertain` | `metadata.image_paths contains a PIL image placeholder string rather than a file path or URL.` |  | 与 source 248 同类；待最终确认是否放行。 |
| 5 | `prob_f507ee59c5cd02ece288ae97.json` | `train[0:300]` | `198` | `prob_f507ee59c5cd02ece288ae97` | `cand_f507ee59c5cd02ece288ae97` | `alignment_requires_review, missing_grounded_visual_path` | `metadata.image_paths contains a PIL object string representation rather than a concrete file path or URL` |  | 题面文本已足以描述循环结构；待最终确认是否放行。 |

## 相邻观察样本（未执行）

| file | source_problem_id | reason_codes | 备注 |
| --- | --- | --- | --- |
| `prob_42a98da9e442b03ead20a6e3.json` | `66` | `alignment_requires_review, visual_evidence_uncertain` | 题面较完整，但仍保留一定图示语义依赖；不并入首桶。 |

## 继续 hold 的视觉依赖样本（未执行）

| file | source_problem_id | reason_codes | 备注 |
| --- | --- | --- | --- |
| `prob_2d7ca75d35bc56e3c74cf846.json` | `64` | `alignment_requires_review, visual_grounding_missing` | 题面过短，无法脱离图示成立。 |
| `prob_9c67d428639e52917a3a0cd9.json` | `74` | `alignment_requires_review, missing_grounded_visual_path, multi_image_coordination_needed` | 多图协调读数型样本，保留 hold。 |
| `prob_e4e2d4bf30ef874bea44e29a.json` | `242` | `alignment_requires_review, visual_grounding_uncertain` | `this system` 强依赖图像指代，保留 hold。 |
