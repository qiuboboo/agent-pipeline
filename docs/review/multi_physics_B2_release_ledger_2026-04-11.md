# multi_physics review 放行候选（2026-04-11）

- canonical ready 包：`ready/multi_physics/run_outputs_merged_by_source_problem_id__multi_physics`
- 候选来源：`/root/.openclaw/workspace/agent-pipeline/docs/review/multi_physics_B2_bucket_candidates_2026-04-11.json`
- 放行模板：`docs/review/review_release_template.md`
- 当前执行策略：仅执行 **B2档**，即 未配置 reason-code 匹配规则。
- 执行结果（2026-04-11）：本页 `B2档` 已执行 manual release，`人工接受状态=1`。相邻 `adjacent other-risk split_variant bucket` 仅保留观察，本次未执行。
- 执行前汇总：`pass=282 / review=205 / reject=13`
- 执行后汇总：`pass=287 / review=200 / reject=13`
- 放行 basis：exact alignment+missing_grounded_visual_path+split_variant_needs_review bucket with only low_resolution risk

## 分层规则

### B2档：本次执行放行
仅纳入以下规则：
- 未配置 reason-code 匹配规则

**B2档数量：`5`**

### adjacent other-risk split_variant bucket：保留观察，本次不执行
仅纳入以下规则：
- 未配置 reason-code 匹配规则

**adjacent other-risk split_variant bucket 数量：`20`**

### 模板化口径（可复用）
- 先构建 canonical ready，不在 `output -> ready` 里改状态。
- 单独导出候选 ledger。
- 用户确认后再做 manual override，并保留 provenance。
- 回写后刷新 `summary.json`，要求 `selection_validation.ok = true` 且 `write_validation.ok = true`。

人工接受状态说明：`1=pass`，`0=reject`，空白表示未执行。

## B2档（本次已执行）

| # | file | source_split | source_problem_id | problem_id | candidate_id | reason_codes | quality_risk_flags | 人工接受状态 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `multi_physics_000_300__spid_183__prob_2cc801b82ce539fd9ee36e4d.json` | `repo_discovered` | `183` | `prob_2cc801b82ce539fd9ee36e4d` | `cand_2cc801b82ce539fd9ee36e4d` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `low_resolution` | 1 | matched configured review-release policy；按 post-ready waiver policy 放行。 |
| 2 | `multi_physics_300_500__spid_139__prob_ced4ffd63343b7e963b43304.json` | `repo_discovered` | `139` | `prob_ced4ffd63343b7e963b43304` | `cand_ced4ffd63343b7e963b43304` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `low_resolution` | 1 | matched configured review-release policy；按 post-ready waiver policy 放行。 |
| 3 | `multi_physics_300_500__spid_26__prob_899d951486c6776a0e8ae961.json` | `repo_discovered` | `26` | `prob_899d951486c6776a0e8ae961` | `cand_899d951486c6776a0e8ae961` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `low_resolution` | 1 | matched configured review-release policy；按 post-ready waiver policy 放行。 |
| 4 | `multi_physics_300_500__spid_58__prob_b2db72f4c20d13987f2aefb3.json` | `repo_discovered` | `58` | `prob_b2db72f4c20d13987f2aefb3` | `cand_b2db72f4c20d13987f2aefb3` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `low_resolution` | 1 | matched configured review-release policy；按 post-ready waiver policy 放行。 |
| 5 | `multi_physics_300_500__spid_78__prob_a2cc3eb5e3c4fdbc2f669a7a.json` | `repo_discovered` | `78` | `prob_a2cc3eb5e3c4fdbc2f669a7a` | `cand_a2cc3eb5e3c4fdbc2f669a7a` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `low_resolution` | 1 | matched configured review-release policy；按 post-ready waiver policy 放行。 |

## adjacent other-risk split_variant bucket（本次未执行）

| # | file | source_split | source_problem_id | problem_id | candidate_id | reason_codes | quality_risk_flags | 人工接受状态 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `multi_physics_000_300__spid_149__prob_ac516d7a7590f55e43d1d23e.json` | `repo_discovered` | `149` | `prob_ac516d7a7590f55e43d1d23e` | `cand_ac516d7a7590f55e43d1d23e` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `choice_count is 4, but option texts are not provided in the input and metadata.choice_field is null.` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 2 | `multi_physics_000_300__spid_166__prob_32ee276d708770fc911bc8d1.json` | `repo_discovered` | `166` | `prob_32ee276d708770fc911bc8d1` | `cand_32ee276d708770fc911bc8d1` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `Choice options are missing: `choice_count` is 4, but no option texts are provided and `metadata.choice_field` is null., minor_metadata_inconsistency` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 3 | `multi_physics_000_300__spid_230__prob_d25799f5280365bedb74313d.json` | `repo_discovered` | `230` | `prob_d25799f5280365bedb74313d` | `cand_d25799f5280365bedb74313d` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `visual_evidence_weak` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 4 | `multi_physics_000_300__spid_235__prob_fb0f61828e7f6753245bc6c9.json` | `repo_discovered` | `235` | `prob_fb0f61828e7f6753245bc6c9` | `cand_fb0f61828e7f6753245bc6c9` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `metadata.choice_field is null` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 5 | `multi_physics_000_300__spid_239__prob_aee71062de2a81cd65c2c36e.json` | `repo_discovered` | `239` | `prob_aee71062de2a81cd65c2c36e` | `cand_aee71062de2a81cd65c2c36e` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `diagram_is_schematic` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 6 | `multi_physics_000_300__spid_263__prob_21b1c7064e4df205bdd0cf85.json` | `repo_discovered` | `263` | `prob_21b1c7064e4df205bdd0cf85` | `cand_21b1c7064e4df205bdd0cf85` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `Choice texts are missing: the sample indicates a 4-choice question (`choice_count` = 4), but no option content is provided and `metadata.choice_field` is null., low_resolution` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 7 | `multi_physics_000_300__spid_274__prob_d429d0414de798b07bcf7d6c.json` | `repo_discovered` | `274` | `prob_d429d0414de798b07bcf7d6c` | `cand_d429d0414de798b07bcf7d6c` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `visual_evidence_weak` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 8 | `multi_physics_300_500__spid_116__prob_51e06652e50e85f9aed15453.json` | `repo_discovered` | `116` | `prob_51e06652e50e85f9aed15453` | `cand_51e06652e50e85f9aed15453` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `image_low_quality` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 9 | `multi_physics_300_500__spid_121__prob_2759a2c3e7d90143741bb191.json` | `repo_discovered` | `121` | `prob_2759a2c3e7d90143741bb191` | `cand_2759a2c3e7d90143741bb191` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `small_image` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 10 | `multi_physics_300_500__spid_141__prob_f49202319723e75a38621036.json` | `repo_discovered` | `141` | `prob_f49202319723e75a38621036` | `cand_f49202319723e75a38621036` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `choice_count is 4, but the option texts are not provided in the input fields.` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 11 | `multi_physics_300_500__spid_149__prob_ac516d7a7590f55e43d1d23e.json` | `repo_discovered` | `149` | `prob_ac516d7a7590f55e43d1d23e` | `cand_ac516d7a7590f55e43d1d23e` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `metadata.choice_field is null while choice_count is 4, so choice option assets are not provided in the input fields.` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 12 | `multi_physics_300_500__spid_15__prob_8d501a9e2dd30f769af9fde9.json` | `repo_discovered` | `15` | `prob_8d501a9e2dd30f769af9fde9` | `cand_8d501a9e2dd30f769af9fde9` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `minor_text_ocr_noise` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 13 | `multi_physics_300_500__spid_17__prob_bf39aaf2dd830cf48041e87f.json` | `repo_discovered` | `17` | `prob_bf39aaf2dd830cf48041e87f` | `cand_bf39aaf2dd830cf48041e87f` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `minor_text_format_issue` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 14 | `multi_physics_300_500__spid_191__prob_cf503231287309f4f6b2f8e7.json` | `repo_discovered` | `191` | `prob_cf503231287309f4f6b2f8e7` | `cand_cf503231287309f4f6b2f8e7` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `metadata.extraction_notes indicates the source text appears noisy/truncated: option A has a leading dot and option D ends with truncated text., minor_source_text_noise` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 15 | `multi_physics_300_500__spid_195__prob_59cb203407d9353733118cf0.json` | `repo_discovered` | `195` | `prob_59cb203407d9353733118cf0` | `cand_59cb203407d9353733118cf0` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `diagram_cropped_or_minimal, visual_evidence_weak` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 16 | `multi_physics_300_500__spid_32__prob_86967462cd5d029fadcf827f.json` | `repo_discovered` | `32` | `prob_86967462cd5d029fadcf827f` | `cand_86967462cd5d029fadcf827f` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `minor_answer_text_noise` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 17 | `multi_physics_300_500__spid_55__prob_e74a96e4916b54eae8397e66.json` | `repo_discovered` | `55` | `prob_e74a96e4916b54eae8397e66` | `cand_e74a96e4916b54eae8397e66` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `choice_count is 4 and answer_text is "AC", but no option texts are provided in the input., metadata.extraction_notes says the answer letters were mapped to option text, but answer_text remains "AC".` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 18 | `multi_physics_300_500__spid_8__prob_76daf91e34f038403954e938.json` | `repo_discovered` | `8` | `prob_76daf91e34f038403954e938` | `cand_76daf91e34f038403954e938` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `minor_crop_risk` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 19 | `multi_physics_300_500__spid_92__prob_b807be34e0e3a44d0eda0d4f.json` | `repo_discovered` | `92` | `prob_b807be34e0e3a44d0eda0d4f` | `cand_b807be34e0e3a44d0eda0d4f` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `Choice texts are not provided; `choice_count` is 4 but `metadata.choice_field` is null.` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |
| 20 | `multi_physics_300_500__spid_9__prob_66a5208237e0ae3b16dc2653.json` | `repo_discovered` | `9` | `prob_66a5208237e0ae3b16dc2653` | `cand_66a5208237e0ae3b16dc2653` | `alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review` | `metadata.choice_field is null, small_image, visual_evidence_weak` |  | 保留给下一轮；本次不与当前执行 bucket 混放。 |

## 说明

- provenance 写回字段记录在样本内：`problem_main_record.release_reserved.manual_release_decision`、`clean_pool_entries[0].manual_override`、`cleaning_records[-1].manual_override`。
- 本次 policy doc：`docs/review/multi_physics_B2_release_decision_2026-04-11.md`
