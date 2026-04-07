# msearth_open_ended 改写样例分析

- 生成时间：`2026-04-07T10:10:11Z`
- ready 包：`ready/msearth_open_ended/run_merged_msearth_open_ended_0000_0120_ler_reasoning_chain`
- 自动结果分布：`pass=84 / review=84 / reject=12`

## Pass 样本分析

- pass 样本数：`84`
- 改写策略分布：`keep_open=180`

### Pass 案例 1：`prob_0145a16b4c906d011527c6f5`

- source_problem_id：`5`
- rewrite_strategy：`keep_open`
- 图片：无

**原题**

<image>Caption:
Se is mo generating zones (hatched) of Kerch-Taman region from instrumental, arch eos e is mo logical, and paleoseismolog- ical data, with epicenters determined from instrumental and macroseismic data, for 1800-2014 (Pustovitenko et al., 1989; She- balin and Leydecker, 1997; United Geophysical Survey, 2016); years of largest earthquakes are indicated. Expected magnitudes of further earthquakes in marked zones range from 6.0 to 7.0.
Question:
What data sources were used to identify the seismogenic zones?

**改写**

Caption:
Se is mo generating zones (hatched) of Kerch-Taman region from instrumental, arch eos e is mo logical, and paleoseismolog- ical data, with epicenters determined from instrumental and macroseismic data, for 1800-2014 (Pustovitenko et al., 1989; She- balin and Leydecker, 1997; United Geophysical Survey, 2016); years of largest earthquakes are indicated. Expected magnitudes of further earthquakes in marked zones range from 6.0 to 7.0.
Question:
What data sources were used to identify the seismogenic zones?

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。

### Pass 案例 2：`prob_01ef0e4e3447fa6086d1d9b3`

- source_problem_id：`4`
- rewrite_strategy：`keep_open`
- 图片：无

**原题**

What unit is used to measure PGA values in the figure?

**改写**

What unit is used to measure PGA values in the figure?

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。

### Pass 案例 3：`prob_023604d7190da6b4f223f02a`

- source_problem_id：`3`
- rewrite_strategy：`keep_open`
- 图片：无

**原题**

What does the orange area in panel B represent?

**改写**

What does the orange area in panel B represent?

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。

### Pass 案例 4：`prob_04030acd59250a212145d242`

- source_problem_id：`9`
- rewrite_strategy：`keep_open`
- 图片：无

**原题**

What is the minimum horizontal sampling distance of the model results?

**改写**

What is the minimum horizontal sampling distance of the model results?

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。

### Pass 案例 5：`prob_05b14c847a2ecd57e1c8c591`

- source_problem_id：`8`
- rewrite_strategy：`keep_open`
- 图片：无

**原题**

What is the lowest shear stress observed in the figure?

**改写**

What is the lowest shear stress observed in the figure?

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。

## Review 原因分析

| review reason | count |
| --- | --- |
| alignment_requires_review | 72 |
| missing_grounded_visual_path | 67 |
| visual_evidence_uncertain | 26 |
| domain_inference_required | 2 |
| requires_domain_inference | 2 |
| image_metadata_incomplete | 2 |
| answer_not_visually_grounded | 2 |
| answer_not_image_grounded | 1 |

### Review 案例 1：`prob_02f97d56cae50fb13abe3d1b`

- source_problem_id：`10`
- review reasons：`alignment_requires_review, missing_grounded_visual_path`
- 图片：无

**原题**

<image>Caption:
Esteiro de Estarreja site in Ria de Aveiro (Portugal).
Question:
What contaminant spreads from Esteiro de Estarreja?

**改写**

Caption:
Esteiro de Estarreja site in Ria de Aveiro (Portugal).
Question:
What contaminant spreads from Esteiro de Estarreja?

**分析**

该样本同时触发了多个 review 原因：`alignment_requires_review, missing_grounded_visual_path`，属于复合风险案例，不适合直接自动放行。

### Review 案例 2：`prob_092593b7dd95d760b8f3fa00`

- source_problem_id：`13`
- review reasons：`alignment_requires_review, missing_grounded_visual_path`
- 图片：无

**原题**

<image>Caption:
Map of Kersa sub-watershed
Question:
What is the elevation range of the Kersa sub-watershed?

**改写**

Caption:
Map of Kersa sub-watershed
Question:
What is the elevation range of the Kersa sub-watershed?

**分析**

该样本同时触发了多个 review 原因：`alignment_requires_review, missing_grounded_visual_path`，属于复合风险案例，不适合直接自动放行。

### Review 案例 3：`prob_051c1d4259e8df708b2cb9e2`

- source_problem_id：`11`
- review reasons：`alignment_requires_review, answer_not_image_grounded, external_context_needed, visual_evidence_uncertain`
- 图片：无

**原题**

What is the coordinate system used in the study?

**改写**

What is the coordinate system used in the study?

**分析**

该样本同时触发了多个 review 原因：`alignment_requires_review, answer_not_image_grounded, external_context_needed, visual_evidence_uncertain`，属于复合风险案例，不适合直接自动放行。

### Review 案例 4：`prob_0acdf1edc46d66b03c1f4706`

- source_problem_id：`4`
- review reasons：`domain_inference_required, figure_answer_link_ambiguous, limited_context`
- 图片：无

**原题**

What is the significance of the Frio No. 1 Sand layer in this figure?

**改写**

What is the significance of the Frio No. 1 Sand layer in this figure?

**分析**

该样本同时触发了多个 review 原因：`domain_inference_required, figure_answer_link_ambiguous, limited_context`，属于复合风险案例，不适合直接自动放行。

### Review 案例 5：`prob_3ca406755535f7f78845e8cc`

- source_problem_id：`8`
- review reasons：`alignment_requires_review, missing_grounded_visual_path, requires_domain_inference`
- 图片：无

**原题**

What phenomenon caused a significant increase in chlorophyll a in May 1997?

**改写**

What phenomenon caused a significant increase in chlorophyll a in May 1997?

**分析**

该样本同时触发了多个 review 原因：`alignment_requires_review, missing_grounded_visual_path, requires_domain_inference`，属于复合风险案例，不适合直接自动放行。

## 小结

当前数据集同时存在稳定通过样本与需人工复核样本（pass=84, review=84, reject=12）；review 主要集中在 `alignment_requires_review` 一类问题。
