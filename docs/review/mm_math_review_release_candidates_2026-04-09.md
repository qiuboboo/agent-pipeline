# mm_math review 放行候选（2026-04-09）

- canonical ready 包：`ready/mm_math/run_outputs_merged_by_source_problem_id__mm_math`
- 候选来源：`docs/review/mm_math_A_bucket_candidates_2026-04-09.json`
- 放行模板：`docs/review/review_release_template.md`
- 当前执行策略：仅执行 **A档**，即 exact `clean_decision_reason_codes == ["alignment_requires_review"]`。
- 执行结果（2026-04-09）：本页 `A档` 已执行 manual release，`人工接受状态=1`。相邻 `相邻_text_sufficient_桶` 仅保留观察，本次未执行。
- 执行前汇总：`pass=159 / review=440 / reject=1`
- 执行后汇总：`pass=276 / review=323 / reject=1`
- 放行 basis：alignment-only_review_gate_under_post-ready_waiver_policy_not_build-stage_auto-pass

## 分层规则

### A档：本次执行放行
仅纳入以下 exact reason 组合：
- `alignment_requires_review`

**A档数量：`117`**

### 相邻_text_sufficient_桶：保留观察，本次不执行
仅纳入以下 exact reason 组合：
- `alignment_requires_review + text_sufficient`

**相邻_text_sufficient_桶 数量：`7`**

### 模板化口径（可复用）
- 先构建 canonical ready，不在 `output -> ready` 里改状态。
- 单独导出候选 ledger。
- 用户确认后再做 manual override，并保留 provenance。
- 回写后刷新 `summary.json`，要求 `selection_validation.ok = true` 且 `write_validation.ok = true`。

人工接受状态说明：`1=pass`，`0=reject`，空白表示未执行。

## A档（本次已执行）

| # | file | source_split | source_problem_id | problem_id | candidate_id | quality_risk_flags | 人工接受状态 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `mm_math_000_300__spid_51351726.png__prob_de52a8dfd5b1db5831164179.json` | `train[0:300]` | `51351726.png` | `prob_de52a8dfd5b1db5831164179` | `cand_de52a8dfd5b1db5831164179` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 2 | `mm_math_000_300__spid_51385932.png__prob_e95440127b45151666a00504.json` | `train[0:300]` | `51385932.png` | `prob_e95440127b45151666a00504` | `cand_e95440127b45151666a00504` | `metadata.image_field is null` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 3 | `mm_math_000_300__spid_51407073.png__prob_279c3400b01c3a773a7f9c48.json` | `train[0:300]` | `51407073.png` | `prob_279c3400b01c3a773a7f9c48` | `cand_279c3400b01c3a773a7f9c48` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 4 | `mm_math_000_300__spid_51434958.png__prob_7a40adcbcf27c738475af365.json` | `train[0:300]` | `51434958.png` | `prob_7a40adcbcf27c738475af365` | `cand_7a40adcbcf27c738475af365` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 5 | `mm_math_000_300__spid_51491918.png__prob_857089fc88f812eb2a8ee429.json` | `train[0:300]` | `51491918.png` | `prob_857089fc88f812eb2a8ee429` | `cand_857089fc88f812eb2a8ee429` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 6 | `mm_math_000_300__spid_51540105.png__prob_6d2c785c0339362f360c1a70.json` | `train[0:300]` | `51540105.png` | `prob_6d2c785c0339362f360c1a70` | `cand_6d2c785c0339362f360c1a70` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 7 | `mm_math_000_300__spid_51654883.png__prob_9f87f92bcd2485ce7a00f857.json` | `train[0:300]` | `51654883.png` | `prob_9f87f92bcd2485ce7a00f857` | `cand_9f87f92bcd2485ce7a00f857` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 8 | `mm_math_000_300__spid_51918244.png__prob_ef9d8b64e30941d753e598fe.json` | `train[0:300]` | `51918244.png` | `prob_ef9d8b64e30941d753e598fe` | `cand_ef9d8b64e30941d753e598fe` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 9 | `mm_math_000_300__spid_52354486.png__prob_1a4a5d6552d58584658e4922.json` | `train[0:300]` | `52354486.png` | `prob_1a4a5d6552d58584658e4922` | `cand_1a4a5d6552d58584658e4922` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 10 | `mm_math_000_300__spid_52386625.png__prob_13c1000bc9577c1a5303757f.json` | `train[0:300]` | `52386625.png` | `prob_13c1000bc9577c1a5303757f` | `cand_13c1000bc9577c1a5303757f` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 11 | `mm_math_000_300__spid_52387151.png__prob_905d0f617487e7d302444fb6.json` | `train[0:300]` | `52387151.png` | `prob_905d0f617487e7d302444fb6` | `cand_905d0f617487e7d302444fb6` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 12 | `mm_math_000_300__spid_52387190.png__prob_2e9617e9be5202993baedaa3.json` | `train[0:300]` | `52387190.png` | `prob_2e9617e9be5202993baedaa3` | `cand_2e9617e9be5202993baedaa3` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 13 | `mm_math_000_300__spid_52422247.png__prob_07bce4a291d8689f61995cb6.json` | `train[0:300]` | `52422247.png` | `prob_07bce4a291d8689f61995cb6` | `cand_07bce4a291d8689f61995cb6` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 14 | `mm_math_000_300__spid_52422738.png__prob_9b15aab904de1e00fa2d7c52.json` | `train[0:300]` | `52422738.png` | `prob_9b15aab904de1e00fa2d7c52` | `cand_9b15aab904de1e00fa2d7c52` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 15 | `mm_math_000_300__spid_52423423.png__prob_b9f86ef6882fc09540b9209e.json` | `train[0:300]` | `52423423.png` | `prob_b9f86ef6882fc09540b9209e` | `cand_b9f86ef6882fc09540b9209e` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 16 | `mm_math_000_300__spid_52551715.png__prob_90a8638a916e5c72e51cd9fc.json` | `train[0:300]` | `52551715.png` | `prob_90a8638a916e5c72e51cd9fc` | `cand_90a8638a916e5c72e51cd9fc` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 17 | `mm_math_000_300__spid_52634676.png__prob_093b96ae57e2c273ad4fa9e4.json` | `train[0:300]` | `52634676.png` | `prob_093b96ae57e2c273ad4fa9e4` | `cand_093b96ae57e2c273ad4fa9e4` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 18 | `mm_math_000_300__spid_52653333.png__prob_4e11c6c653752b23731a9afc.json` | `train[0:300]` | `52653333.png` | `prob_4e11c6c653752b23731a9afc` | `cand_4e11c6c653752b23731a9afc` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 19 | `mm_math_000_300__spid_52653732.png__prob_442546c61b794e0be4338291.json` | `train[0:300]` | `52653732.png` | `prob_442546c61b794e0be4338291` | `cand_442546c61b794e0be4338291` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 20 | `mm_math_000_300__spid_52655011.png__prob_73b7b12c139d2117867d4fc2.json` | `train[0:300]` | `52655011.png` | `prob_73b7b12c139d2117867d4fc2` | `cand_73b7b12c139d2117867d4fc2` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 21 | `mm_math_000_300__spid_52655234.png__prob_0c9c34c0ca8d908c700be2f1.json` | `train[0:300]` | `52655234.png` | `prob_0c9c34c0ca8d908c700be2f1` | `cand_0c9c34c0ca8d908c700be2f1` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 22 | `mm_math_000_300__spid_52836849.png__prob_3a03c3a85c2cc0063529a319.json` | `train[0:300]` | `52836849.png` | `prob_3a03c3a85c2cc0063529a319` | `cand_3a03c3a85c2cc0063529a319` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 23 | `mm_math_000_300__spid_52873807.png__prob_28185fbf213cf85cc1b6a2c9.json` | `train[0:300]` | `52873807.png` | `prob_28185fbf213cf85cc1b6a2c9` | `cand_28185fbf213cf85cc1b6a2c9` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 24 | `mm_math_000_300__spid_52905597.png__prob_395a3943ab9bb0b821c0fea4.json` | `train[0:300]` | `52905597.png` | `prob_395a3943ab9bb0b821c0fea4` | `cand_395a3943ab9bb0b821c0fea4` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 25 | `mm_math_000_300__spid_52914190.png__prob_03f697578435f3d105d54fa9.json` | `train[0:300]` | `52914190.png` | `prob_03f697578435f3d105d54fa9` | `cand_03f697578435f3d105d54fa9` | `low_resolution` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 26 | `mm_math_000_300__spid_52950677.png__prob_87bab32f653c7f50c3044893.json` | `train[0:300]` | `52950677.png` | `prob_87bab32f653c7f50c3044893` | `cand_87bab32f653c7f50c3044893` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 27 | `mm_math_000_300__spid_52978392.png__prob_b4d4197b3d9e2ccbb0997b19.json` | `train[0:300]` | `52978392.png` | `prob_b4d4197b3d9e2ccbb0997b19` | `cand_b4d4197b3d9e2ccbb0997b19` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 28 | `mm_math_000_300__spid_52991478.png__prob_6228c887f2d1492024dbe7ab.json` | `train[0:300]` | `52991478.png` | `prob_6228c887f2d1492024dbe7ab` | `cand_6228c887f2d1492024dbe7ab` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 29 | `mm_math_000_300__spid_53009847.png__prob_766c7be3f9a9cea1b1c267d4.json` | `train[0:300]` | `53009847.png` | `prob_766c7be3f9a9cea1b1c267d4` | `cand_766c7be3f9a9cea1b1c267d4` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 30 | `mm_math_000_300__spid_53009848.png__prob_2dbdbdb3371dd04135cfd23f.json` | `train[0:300]` | `53009848.png` | `prob_2dbdbdb3371dd04135cfd23f` | `cand_2dbdbdb3371dd04135cfd23f` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 31 | `mm_math_000_300__spid_53033451.png__prob_f2d11c005f6da7ba0dd32950.json` | `train[0:300]` | `53033451.png` | `prob_f2d11c005f6da7ba0dd32950` | `cand_f2d11c005f6da7ba0dd32950` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 32 | `mm_math_000_300__spid_53033454.png__prob_0c0d16407860b773c4cc455e.json` | `train[0:300]` | `53033454.png` | `prob_0c0d16407860b773c4cc455e` | `cand_0c0d16407860b773c4cc455e` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 33 | `mm_math_000_300__spid_53044021.png__prob_19ba3160a8c6a6d001e428bd.json` | `train[0:300]` | `53044021.png` | `prob_19ba3160a8c6a6d001e428bd` | `cand_19ba3160a8c6a6d001e428bd` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 34 | `mm_math_000_300__spid_53058709.png__prob_7391d0320f408fd008615ad9.json` | `train[0:300]` | `53058709.png` | `prob_7391d0320f408fd008615ad9` | `cand_7391d0320f408fd008615ad9` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 35 | `mm_math_000_300__spid_53065559.png__prob_f21ca7a796ea17e6dfd7b9db.json` | `train[0:300]` | `53065559.png` | `prob_f21ca7a796ea17e6dfd7b9db` | `cand_f21ca7a796ea17e6dfd7b9db` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 36 | `mm_math_000_300__spid_53078877.png__prob_87c4bc721772b783782ce358.json` | `train[0:300]` | `53078877.png` | `prob_87c4bc721772b783782ce358` | `cand_87c4bc721772b783782ce358` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 37 | `mm_math_000_300__spid_53078880.png__prob_d7495291f7d6ed817cad0ff6.json` | `train[0:300]` | `53078880.png` | `prob_d7495291f7d6ed817cad0ff6` | `cand_d7495291f7d6ed817cad0ff6` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 38 | `mm_math_000_300__spid_53080285.png__prob_d19b4773f8403809a2e90cbb.json` | `train[0:300]` | `53080285.png` | `prob_d19b4773f8403809a2e90cbb` | `cand_d19b4773f8403809a2e90cbb` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 39 | `mm_math_000_300__spid_53080709.png__prob_74c523fc33b8162e07595080.json` | `train[0:300]` | `53080709.png` | `prob_74c523fc33b8162e07595080` | `cand_74c523fc33b8162e07595080` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 40 | `mm_math_000_300__spid_53080813.png__prob_8f44c02fd4fa02e49953f145.json` | `train[0:300]` | `53080813.png` | `prob_8f44c02fd4fa02e49953f145` | `cand_8f44c02fd4fa02e49953f145` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 41 | `mm_math_000_300__spid_53102440.png__prob_1d9cca5b45a747bfb63aa1a7.json` | `train[0:300]` | `53102440.png` | `prob_1d9cca5b45a747bfb63aa1a7` | `cand_1d9cca5b45a747bfb63aa1a7` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 42 | `mm_math_000_300__spid_53105790.png__prob_294c38d418dbe3ef2076d848.json` | `train[0:300]` | `53105790.png` | `prob_294c38d418dbe3ef2076d848` | `cand_294c38d418dbe3ef2076d848` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 43 | `mm_math_000_300__spid_53105794.png__prob_d2dd34d0232f1d12dcb9da5d.json` | `train[0:300]` | `53105794.png` | `prob_d2dd34d0232f1d12dcb9da5d` | `cand_d2dd34d0232f1d12dcb9da5d` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 44 | `mm_math_000_300__spid_53107076.png__prob_ed065f8d87385f3208af6ce7.json` | `train[0:300]` | `53107076.png` | `prob_ed065f8d87385f3208af6ce7` | `cand_ed065f8d87385f3208af6ce7` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 45 | `mm_math_000_300__spid_53110752.png__prob_0ba76979913fce07b6a23b1b.json` | `train[0:300]` | `53110752.png` | `prob_0ba76979913fce07b6a23b1b` | `cand_0ba76979913fce07b6a23b1b` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 46 | `mm_math_000_300__spid_53110858.png__prob_3138b6a159d33693cfff6ede.json` | `train[0:300]` | `53110858.png` | `prob_3138b6a159d33693cfff6ede` | `cand_3138b6a159d33693cfff6ede` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 47 | `mm_math_000_300__spid_55190294.png__prob_0f75ef2ed0e29b7b104cc32c.json` | `train[0:300]` | `55190294.png` | `prob_0f75ef2ed0e29b7b104cc32c` | `cand_0f75ef2ed0e29b7b104cc32c` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 48 | `mm_math_000_300__spid_55192327.png__prob_ae6931e65736a00b2a0ede43.json` | `train[0:300]` | `55192327.png` | `prob_ae6931e65736a00b2a0ede43` | `cand_ae6931e65736a00b2a0ede43` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 49 | `mm_math_000_300__spid_55377877.png__prob_a73c132c50ae522e44f82ec4.json` | `train[0:300]` | `55377877.png` | `prob_a73c132c50ae522e44f82ec4` | `cand_a73c132c50ae522e44f82ec4` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 50 | `mm_math_000_300__spid_55393326.png__prob_f5dfe13752d5d57e0d1cb177.json` | `train[0:300]` | `55393326.png` | `prob_f5dfe13752d5d57e0d1cb177` | `cand_f5dfe13752d5d57e0d1cb177` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 51 | `mm_math_000_300__spid_55497782.png__prob_c95994cfbbcd078253b77367.json` | `train[0:300]` | `55497782.png` | `prob_c95994cfbbcd078253b77367` | `cand_c95994cfbbcd078253b77367` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 52 | `mm_math_000_300__spid_55604325.png__prob_a62a3341d2e04458b77ee973.json` | `train[0:300]` | `55604325.png` | `prob_a62a3341d2e04458b77ee973` | `cand_a62a3341d2e04458b77ee973` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 53 | `mm_math_300_600__spid_50584300.png__prob_be766adb0c36ae417e529157.json` | `train[300:600]` | `50584300.png` | `prob_be766adb0c36ae417e529157` | `cand_be766adb0c36ae417e529157` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 54 | `mm_math_300_600__spid_51368820.png__prob_0a946b5e47e501b23f8c5f2c.json` | `train[300:600]` | `51368820.png` | `prob_0a946b5e47e501b23f8c5f2c` | `cand_0a946b5e47e501b23f8c5f2c` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 55 | `mm_math_300_600__spid_51379110.png__prob_68570e65d8577fe208d31096.json` | `train[300:600]` | `51379110.png` | `prob_68570e65d8577fe208d31096` | `cand_68570e65d8577fe208d31096` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 56 | `mm_math_300_600__spid_51385606.png__prob_719fe5433157b3c0b8d97de0.json` | `train[300:600]` | `51385606.png` | `prob_719fe5433157b3c0b8d97de0` | `cand_719fe5433157b3c0b8d97de0` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 57 | `mm_math_300_600__spid_51385683.png__prob_764bf5da840741f5f851923e.json` | `train[300:600]` | `51385683.png` | `prob_764bf5da840741f5f851923e` | `cand_764bf5da840741f5f851923e` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 58 | `mm_math_300_600__spid_51403188.png__prob_8d7404a59c33c154f366e7f2.json` | `train[300:600]` | `51403188.png` | `prob_8d7404a59c33c154f366e7f2` | `cand_8d7404a59c33c154f366e7f2` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 59 | `mm_math_300_600__spid_51419892.png__prob_4707d06316bbc1c55e4f274e.json` | `train[300:600]` | `51419892.png` | `prob_4707d06316bbc1c55e4f274e` | `cand_4707d06316bbc1c55e4f274e` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 60 | `mm_math_300_600__spid_51434958.png__prob_cd539e0bd28811ae7b4ea69d.json` | `train[300:600]` | `51434958.png` | `prob_cd539e0bd28811ae7b4ea69d` | `cand_cd539e0bd28811ae7b4ea69d` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 61 | `mm_math_300_600__spid_51435251.png__prob_fb35645c313e8277b1e45522.json` | `train[300:600]` | `51435251.png` | `prob_fb35645c313e8277b1e45522` | `cand_fb35645c313e8277b1e45522` | `small_image` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 62 | `mm_math_300_600__spid_51457856.png__prob_5c4083aea7b5861c6ffc4d3b.json` | `train[300:600]` | `51457856.png` | `prob_5c4083aea7b5861c6ffc4d3b` | `cand_5c4083aea7b5861c6ffc4d3b` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 63 | `mm_math_300_600__spid_51457863.png__prob_12d8e2536e1621a49ebd0c23.json` | `train[300:600]` | `51457863.png` | `prob_12d8e2536e1621a49ebd0c23` | `cand_12d8e2536e1621a49ebd0c23` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 64 | `mm_math_300_600__spid_51491918.png__prob_caf6f4b12247ecee1a3f7463.json` | `train[300:600]` | `51491918.png` | `prob_caf6f4b12247ecee1a3f7463` | `cand_caf6f4b12247ecee1a3f7463` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 65 | `mm_math_300_600__spid_51638142.png__prob_06330a3f61c5d9591d3289c4.json` | `train[300:600]` | `51638142.png` | `prob_06330a3f61c5d9591d3289c4` | `cand_06330a3f61c5d9591d3289c4` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 66 | `mm_math_300_600__spid_51654675.png__prob_12efe393416eb70a01d999b5.json` | `train[300:600]` | `51654675.png` | `prob_12efe393416eb70a01d999b5` | `cand_12efe393416eb70a01d999b5` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 67 | `mm_math_300_600__spid_51806942.png__prob_9fb5668ca6c5c61bbc256904.json` | `train[300:600]` | `51806942.png` | `prob_9fb5668ca6c5c61bbc256904` | `cand_9fb5668ca6c5c61bbc256904` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 68 | `mm_math_300_600__spid_51910248.png__prob_8d3c48d0c1ad17dc554bce7f.json` | `train[300:600]` | `51910248.png` | `prob_8d3c48d0c1ad17dc554bce7f` | `cand_8d3c48d0c1ad17dc554bce7f` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 69 | `mm_math_300_600__spid_52354486.png__prob_182f1d5e4a440f9caa423b19.json` | `train[300:600]` | `52354486.png` | `prob_182f1d5e4a440f9caa423b19` | `cand_182f1d5e4a440f9caa423b19` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 70 | `mm_math_300_600__spid_52354640.png__prob_57aee357b44fecd938f7bafe.json` | `train[300:600]` | `52354640.png` | `prob_57aee357b44fecd938f7bafe` | `cand_57aee357b44fecd938f7bafe` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 71 | `mm_math_300_600__spid_52355086.png__prob_7c5fd155c48a3fdfc7f3ad9b.json` | `train[300:600]` | `52355086.png` | `prob_7c5fd155c48a3fdfc7f3ad9b` | `cand_7c5fd155c48a3fdfc7f3ad9b` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 72 | `mm_math_300_600__spid_52381887.png__prob_e65b4e4863bbf99eb1ad8d0d.json` | `train[300:600]` | `52381887.png` | `prob_e65b4e4863bbf99eb1ad8d0d` | `cand_e65b4e4863bbf99eb1ad8d0d` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 73 | `mm_math_300_600__spid_52386627.png__prob_2f0905753581be5f475822f3.json` | `train[300:600]` | `52386627.png` | `prob_2f0905753581be5f475822f3` | `cand_2f0905753581be5f475822f3` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 74 | `mm_math_300_600__spid_52386771.png__prob_594638d864a50fcb8d9d87a7.json` | `train[300:600]` | `52386771.png` | `prob_594638d864a50fcb8d9d87a7` | `cand_594638d864a50fcb8d9d87a7` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 75 | `mm_math_300_600__spid_52387151.png__prob_90dc0365456d089a2324978b.json` | `train[300:600]` | `52387151.png` | `prob_90dc0365456d089a2324978b` | `cand_90dc0365456d089a2324978b` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 76 | `mm_math_300_600__spid_52395428.png__prob_2147da216077a7c388e44bc1.json` | `train[300:600]` | `52395428.png` | `prob_2147da216077a7c388e44bc1` | `cand_2147da216077a7c388e44bc1` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 77 | `mm_math_300_600__spid_52422738.png__prob_1cf1cb44baac109ed8f3aae3.json` | `train[300:600]` | `52422738.png` | `prob_1cf1cb44baac109ed8f3aae3` | `cand_1cf1cb44baac109ed8f3aae3` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 78 | `mm_math_300_600__spid_52602477.png__prob_0bd8fe2769439cfc66be0973.json` | `train[300:600]` | `52602477.png` | `prob_0bd8fe2769439cfc66be0973` | `cand_0bd8fe2769439cfc66be0973` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 79 | `mm_math_300_600__spid_52653732.png__prob_a5e4681278520e41915e664b.json` | `train[300:600]` | `52653732.png` | `prob_a5e4681278520e41915e664b` | `cand_a5e4681278520e41915e664b` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 80 | `mm_math_300_600__spid_52655011.png__prob_a0e705a4764cec87edfc4f13.json` | `train[300:600]` | `52655011.png` | `prob_a0e705a4764cec87edfc4f13` | `cand_a0e705a4764cec87edfc4f13` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 81 | `mm_math_300_600__spid_52774652.png__prob_ac1c1f4626b4b70ce1ed6fda.json` | `train[300:600]` | `52774652.png` | `prob_ac1c1f4626b4b70ce1ed6fda` | `cand_ac1c1f4626b4b70ce1ed6fda` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 82 | `mm_math_300_600__spid_52836211.png__prob_8a61687e9710d19e30c1dc3c.json` | `train[300:600]` | `52836211.png` | `prob_8a61687e9710d19e30c1dc3c` | `cand_8a61687e9710d19e30c1dc3c` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 83 | `mm_math_300_600__spid_52836352.png__prob_7bb0005c973df2120d40a2ab.json` | `train[300:600]` | `52836352.png` | `prob_7bb0005c973df2120d40a2ab` | `cand_7bb0005c973df2120d40a2ab` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 84 | `mm_math_300_600__spid_52836686.png__prob_ad9479f8b7385edf668dfc5d.json` | `train[300:600]` | `52836686.png` | `prob_ad9479f8b7385edf668dfc5d` | `cand_ad9479f8b7385edf668dfc5d` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 85 | `mm_math_300_600__spid_52836781.png__prob_90223e95cbcc5e6cdfa19b7b.json` | `train[300:600]` | `52836781.png` | `prob_90223e95cbcc5e6cdfa19b7b` | `cand_90223e95cbcc5e6cdfa19b7b` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 86 | `mm_math_300_600__spid_52836818.png__prob_64bf8ba887fd787f626fa4c6.json` | `train[300:600]` | `52836818.png` | `prob_64bf8ba887fd787f626fa4c6` | `cand_64bf8ba887fd787f626fa4c6` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 87 | `mm_math_300_600__spid_52873807.png__prob_0625f1588501207baf3f50ff.json` | `train[300:600]` | `52873807.png` | `prob_0625f1588501207baf3f50ff` | `cand_0625f1588501207baf3f50ff` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 88 | `mm_math_300_600__spid_52905589.png__prob_a974558af84d7dc2b1dc5d32.json` | `train[300:600]` | `52905589.png` | `prob_a974558af84d7dc2b1dc5d32` | `cand_a974558af84d7dc2b1dc5d32` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 89 | `mm_math_300_600__spid_52905597.png__prob_cd4a676e952200d8c5c4dc2c.json` | `train[300:600]` | `52905597.png` | `prob_cd4a676e952200d8c5c4dc2c` | `cand_cd4a676e952200d8c5c4dc2c` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 90 | `mm_math_300_600__spid_52905802.png__prob_69a8cfda33de2ad956aeca99.json` | `train[300:600]` | `52905802.png` | `prob_69a8cfda33de2ad956aeca99` | `cand_69a8cfda33de2ad956aeca99` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 91 | `mm_math_300_600__spid_52905905.png__prob_181e796e0552732350103334.json` | `train[300:600]` | `52905905.png` | `prob_181e796e0552732350103334` | `cand_181e796e0552732350103334` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 92 | `mm_math_300_600__spid_52907826.png__prob_2a51ac4b159c2a755b5db05d.json` | `train[300:600]` | `52907826.png` | `prob_2a51ac4b159c2a755b5db05d` | `cand_2a51ac4b159c2a755b5db05d` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 93 | `mm_math_300_600__spid_52950309.png__prob_92319aa03f125907e98aedbf.json` | `train[300:600]` | `52950309.png` | `prob_92319aa03f125907e98aedbf` | `cand_92319aa03f125907e98aedbf` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 94 | `mm_math_300_600__spid_52978392.png__prob_a88f34c2d899229b5284371e.json` | `train[300:600]` | `52978392.png` | `prob_a88f34c2d899229b5284371e` | `cand_a88f34c2d899229b5284371e` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 95 | `mm_math_300_600__spid_52978596.png__prob_f19a9d580bb55880fa9b5998.json` | `train[300:600]` | `52978596.png` | `prob_f19a9d580bb55880fa9b5998` | `cand_f19a9d580bb55880fa9b5998` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 96 | `mm_math_300_600__spid_52978712.png__prob_1d5d95fe948121adc7ee00d8.json` | `train[300:600]` | `52978712.png` | `prob_1d5d95fe948121adc7ee00d8` | `cand_1d5d95fe948121adc7ee00d8` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 97 | `mm_math_300_600__spid_52991477.png__prob_7ae99febeb4a1d35e929d84a.json` | `train[300:600]` | `52991477.png` | `prob_7ae99febeb4a1d35e929d84a` | `cand_7ae99febeb4a1d35e929d84a` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 98 | `mm_math_300_600__spid_53009847.png__prob_79ffab3b9d405b148353104d.json` | `train[300:600]` | `53009847.png` | `prob_79ffab3b9d405b148353104d` | `cand_79ffab3b9d405b148353104d` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 99 | `mm_math_300_600__spid_53009908.png__prob_bc1a2e1520f7a2c07d7d9db2.json` | `train[300:600]` | `53009908.png` | `prob_bc1a2e1520f7a2c07d7d9db2` | `cand_bc1a2e1520f7a2c07d7d9db2` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 100 | `mm_math_300_600__spid_53033284.png__prob_1a237fa48f412a120262b8dc.json` | `train[300:600]` | `53033284.png` | `prob_1a237fa48f412a120262b8dc` | `cand_1a237fa48f412a120262b8dc` | `small_image` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 101 | `mm_math_300_600__spid_53044345.png__prob_73ee92e2476e2c4e8bcef639.json` | `train[300:600]` | `53044345.png` | `prob_73ee92e2476e2c4e8bcef639` | `cand_73ee92e2476e2c4e8bcef639` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 102 | `mm_math_300_600__spid_53058709.png__prob_e68a9a2796964275073fa3be.json` | `train[300:600]` | `53058709.png` | `prob_e68a9a2796964275073fa3be` | `cand_e68a9a2796964275073fa3be` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 103 | `mm_math_300_600__spid_53080285.png__prob_da93b5a39f31fb4a507ceb84.json` | `train[300:600]` | `53080285.png` | `prob_da93b5a39f31fb4a507ceb84` | `cand_da93b5a39f31fb4a507ceb84` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 104 | `mm_math_300_600__spid_53081475.png__prob_2a423cef23034dee4b474289.json` | `train[300:600]` | `53081475.png` | `prob_2a423cef23034dee4b474289` | `cand_2a423cef23034dee4b474289` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 105 | `mm_math_300_600__spid_53102443.png__prob_62002132fc9fa47b119b7744.json` | `train[300:600]` | `53102443.png` | `prob_62002132fc9fa47b119b7744` | `cand_62002132fc9fa47b119b7744` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 106 | `mm_math_300_600__spid_53105794.png__prob_5594e2bf46ae605096b14ce4.json` | `train[300:600]` | `53105794.png` | `prob_5594e2bf46ae605096b14ce4` | `cand_5594e2bf46ae605096b14ce4` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 107 | `mm_math_300_600__spid_53107076.png__prob_57024b14a88f9f3443faa238.json` | `train[300:600]` | `53107076.png` | `prob_57024b14a88f9f3443faa238` | `cand_57024b14a88f9f3443faa238` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 108 | `mm_math_300_600__spid_53110752.png__prob_14967357e159b450de101451.json` | `train[300:600]` | `53110752.png` | `prob_14967357e159b450de101451` | `cand_14967357e159b450de101451` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 109 | `mm_math_300_600__spid_53110836.png__prob_10b6fb6ce363bd8d21decc24.json` | `train[300:600]` | `53110836.png` | `prob_10b6fb6ce363bd8d21decc24` | `cand_10b6fb6ce363bd8d21decc24` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 110 | `mm_math_300_600__spid_53110858.png__prob_f1cbd25f57b944be032db677.json` | `train[300:600]` | `53110858.png` | `prob_f1cbd25f57b944be032db677` | `cand_f1cbd25f57b944be032db677` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 111 | `mm_math_300_600__spid_53124716.png__prob_348cdac32cf01399cfd1764f.json` | `train[300:600]` | `53124716.png` | `prob_348cdac32cf01399cfd1764f` | `cand_348cdac32cf01399cfd1764f` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 112 | `mm_math_300_600__spid_53151323.png__prob_ce586f5d03bec9adb6a10b49.json` | `train[300:600]` | `53151323.png` | `prob_ce586f5d03bec9adb6a10b49` | `cand_ce586f5d03bec9adb6a10b49` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 113 | `mm_math_300_600__spid_53273961.png__prob_ec2ce7c39d9ae31c84071603.json` | `train[300:600]` | `53273961.png` | `prob_ec2ce7c39d9ae31c84071603` | `cand_ec2ce7c39d9ae31c84071603` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 114 | `mm_math_300_600__spid_55190294.png__prob_52680012bca93339e734fd71.json` | `train[300:600]` | `55190294.png` | `prob_52680012bca93339e734fd71` | `cand_52680012bca93339e734fd71` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 115 | `mm_math_300_600__spid_55192327.png__prob_873b0961d3b3c9e31c88f40c.json` | `train[300:600]` | `55192327.png` | `prob_873b0961d3b3c9e31c88f40c` | `cand_873b0961d3b3c9e31c88f40c` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 116 | `mm_math_300_600__spid_55393326.png__prob_880b6b5fb0a10a979d1d96b6.json` | `train[300:600]` | `55393326.png` | `prob_880b6b5fb0a10a979d1d96b6` | `cand_880b6b5fb0a10a979d1d96b6` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |
| 117 | `mm_math_300_600__spid_55604325.png__prob_03764cffe20a0d3c609ec934.json` | `train[300:600]` | `55604325.png` | `prob_03764cffe20a0d3c609ec934` | `cand_03764cffe20a0d3c609ec934` | `-` | 1 | alignment-only review gate；按 post-ready waiver policy 放行。 |

## 相邻_text_sufficient_桶（本次未执行）

| # | file | source_split | source_problem_id | problem_id | candidate_id | quality_risk_flags | 人工接受状态 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `mm_math_000_300__spid_55426225.png__prob_50301a6e49adede91bc4b72a.json` | `train[0:300]` | `55426225.png` | `prob_50301a6e49adede91bc4b72a` | `cand_50301a6e49adede91bc4b72a` | `-` |  | 保留给下一轮；本次不与 strict A-bucket 混放。 |
| 2 | `mm_math_300_600__spid_51403120.png__prob_f9fe054e1eb9f187d7bced77.json` | `train[300:600]` | `51403120.png` | `prob_f9fe054e1eb9f187d7bced77` | `cand_f9fe054e1eb9f187d7bced77` | `-` |  | 保留给下一轮；本次不与 strict A-bucket 混放。 |
| 3 | `mm_math_300_600__spid_51444993.png__prob_9b253d8bf44728dee07b8a59.json` | `train[300:600]` | `51444993.png` | `prob_9b253d8bf44728dee07b8a59` | `cand_9b253d8bf44728dee07b8a59` | `low_resolution_image` |  | 保留给下一轮；本次不与 strict A-bucket 混放。 |
| 4 | `mm_math_300_600__spid_51809615.png__prob_875671e15cd309711df0893b.json` | `train[300:600]` | `51809615.png` | `prob_875671e15cd309711df0893b` | `cand_875671e15cd309711df0893b` | `-` |  | 保留给下一轮；本次不与 strict A-bucket 混放。 |
| 5 | `mm_math_300_600__spid_52386464.png__prob_0711144ecd6e0a6c1c117981.json` | `train[300:600]` | `52386464.png` | `prob_0711144ecd6e0a6c1c117981` | `cand_0711144ecd6e0a6c1c117981` | `-` |  | 保留给下一轮；本次不与 strict A-bucket 混放。 |
| 6 | `mm_math_300_600__spid_52386539.png__prob_b4377d29980995b8f4075009.json` | `train[300:600]` | `52386539.png` | `prob_b4377d29980995b8f4075009` | `cand_b4377d29980995b8f4075009` | `-` |  | 保留给下一轮；本次不与 strict A-bucket 混放。 |
| 7 | `mm_math_300_600__spid_53043280.png__prob_77a347248c739ce7178338f5.json` | `train[300:600]` | `53043280.png` | `prob_77a347248c739ce7178338f5` | `cand_77a347248c739ce7178338f5` | `-` |  | 保留给下一轮；本次不与 strict A-bucket 混放。 |

## 说明

- provenance 写回字段记录在样本内：`problem_main_record.release_reserved.manual_release_decision`、`clean_pool_entries[0].manual_override`、`cleaning_records[-1].manual_override`。
- 本次 policy doc：`docs/review/mm_math_review_release_candidates_2026-04-09.md`
