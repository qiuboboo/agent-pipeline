# mathvision 改写样例分析

- 生成时间：`2026-04-07T10:10:09Z`
- ready 包：`ready/mathvision/run_merged_mathvision_300_3040_dedup`
- 自动结果分布：`pass=481 / review=433 / reject=4`

## Pass 样本分析

- pass 样本数：`481`
- 改写策略分布：`blank_open=76, drop_image_index=182, keep_open=631, split_open=29`

### Pass 案例 1：`prob_003d5dccf98c6d6570c76cc0`

- source_problem_id：`724`
- rewrite_strategy：`keep_open`
- 图片：![](../ready/mathvision/run_merged_mathvision_300_3040_dedup/datasets/mathvision/artifacts/crops/prob_003d5dccf98c6d6570c76cc0_primary_roi.png)

**原题**

In the diagram you see the rectangular garden of Green's family. It has an area of $30 \mathrm{~m}^{2}$ and is divided into three rectangular parts. One side of the part where flowers are growing has a length of $2 \mathrm{~m}$. Its area is $10 \mathrm{~m}^{2}$. The part with strawberries has one side of length $3 \mathrm{~m}$. What is the area of the part where vegetables are growing?
<image1>

**改写**

In the diagram, you see the rectangular garden of Green's family. It has an area of $30 \mathrm{~m}^{2}$ and is divided into three rectangular parts. One side of the part where flowers are growing has a length of $2 \mathrm{~m}$. Its area is $10 \mathrm{~m}^{2}$. The part with strawberries has one side of length $3 \mathrm{~m}$. What is the area of the part where vegetables are growing?

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

### Pass 案例 2：`prob_002f3120961445c9004e5cc2`

- source_problem_id：`357`
- rewrite_strategy：`blank_open`
- 图片：![](../ready/mathvision/run_merged_mathvision_300_3040_dedup/datasets/mathvision/artifacts/images/prob_002f3120961445c9004e5cc2_primary.png)

**原题**

A piece of string is lying on the table. It is partially covered by three coins as seen in the figure. Under each coin the string is equally likely to pass over itself like this: <image1>
or like this: <image2>. What is the probability that the string is knotted after its ends are pulled?
<image3>

**改写**

A piece of string is lying on the table. It is partially covered by three coins as seen in the figure. Under each coin the string is equally likely to pass over itself in either of the two ways shown. What is the probability that the string is knotted after its ends are pulled?

**分析**

该样本自动结果为 `pass`，改写策略是 `blank_open`。 改写把原始素材整理成开放问答形式，但没有引入新的审查风险信号。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

### Pass 案例 3：`prob_110033bc166298589f2faeba`

- source_problem_id：`934`
- rewrite_strategy：`split_open`
- 图片：![](../ready/mathvision/run_merged_mathvision_300_3040_dedup/datasets/mathvision/artifacts/crops/prob_110033bc166298589f2faeba_primary_roi.png)

**原题**

Ten people order an ice cream for each one. They ask for four vanilla ice creams, three chocolate ice creams, two lemon ice creams and one mango ice cream. As a topping, they ask for four umbrellas, three cherries, two wafers and a chocolate gum, one topping for each ice cream. Since they don't want two ice creams the same, which of the following combinations is possible?
<image1>

**改写**

Ten people each order one ice cream: 4 vanilla, 3 chocolate, 2 lemon, and 1 mango. They also order toppings: 4 umbrellas, 3 cherries, 2 wafers, and 1 chocolate gum, with one topping on each ice cream. No two complete ice creams can be the same. A possible combination uses the flavor that was ordered twice and the topping that was ordered three times. What is the flavor?

**分析**

该样本自动结果为 `pass`，改写策略是 `split_open`。 虽然经过拆分式改写，但仍通过了自动检查，说明题意保持较稳定。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

### Pass 案例 4：`prob_012a75a52e70cb9ecd0c5c06`

- source_problem_id：`888`
- rewrite_strategy：`keep_open`
- 图片：![](../ready/mathvision/run_merged_mathvision_300_3040_dedup/datasets/mathvision/artifacts/crops/prob_012a75a52e70cb9ecd0c5c06_primary_roi.png)

**原题**

A figure is made up of three squares. The side length of the smallest square is $6 \mathrm{~cm}$. How long is the side length of the biggest square?
<image1>

**改写**

A figure is made up of three squares. The side length of the smallest square is $6 \mathrm{~cm}$. How long is the side length of the biggest square?

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

### Pass 案例 5：`prob_017b2865036845c29f987a7c`

- source_problem_id：`1161`
- rewrite_strategy：`keep_open`
- 图片：![](../ready/mathvision/run_merged_mathvision_300_3040_dedup/datasets/mathvision/artifacts/crops/prob_017b2865036845c29f987a7c_primary_roi.png)

**原题**

Bernd produces steps for a staircase which are $15 \mathrm{~cm}$ high and $15 \mathrm{~cm}$ deep (see diagram). The staircase should reach from the ground floor to the first floor which is $3 \mathrm{~m}$ higher. How many steps does Bernd have to produce?
<image1>

**改写**

Bernd produces steps for a staircase which are $15 \mathrm{~cm}$ high and $15 \mathrm{~cm}$ deep. The staircase should reach from the ground floor to the first floor which is $3 \mathrm{~m}$ higher. How many steps does Bernd have to produce?

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

## Review 原因分析

| review reason | count |
| --- | --- |
| alignment_requires_review | 221 |
| missing_grounded_visual_path | 163 |
| pure_image_choice_task | 50 |
| pure_image_option_selection | 46 |
| rewrite_variant_invalid | 45 |
| rewrite_unusable | 44 |
| pure_image_choice_needs_review | 37 |
| rewrite_unavailable | 23 |

### Review 案例 1：`prob_03544214ca53dc00eb9a05a1`

- source_problem_id：`458`
- review reasons：`alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review`
- 图片：![](../ready/mathvision/run_merged_mathvision_300_3040_dedup/datasets/mathvision/artifacts/crops/prob_03544214ca53dc00eb9a05a1_primary_roi.png)

**原题**

Where is the Kangaroo?
<image1>

**改写**

Is the Kangaroo in the circle?

**分析**

该样本同时触发了多个 review 原因：`alignment_requires_review, missing_grounded_visual_path, split_variant_needs_review`，属于复合风险案例，不适合直接自动放行。

### Review 案例 2：`prob_03683d77442f4cddc247f12f`

- source_problem_id：`1039`
- review reasons：`alignment_requires_review, missing_grounded_visual_path, visual_evidence_uncertain`
- 图片：![](../ready/mathvision/run_merged_mathvision_300_3040_dedup/datasets/mathvision/artifacts/crops/prob_03683d77442f4cddc247f12f_primary_roi.png)

**原题**

How many pieces of string are there in the picture?
<image1>

**改写**

How many pieces of string are there in the picture?

**分析**

该样本同时触发了多个 review 原因：`alignment_requires_review, missing_grounded_visual_path, visual_evidence_uncertain`，属于复合风险案例，不适合直接自动放行。

### Review 案例 3：`prob_03ec1ccdf6e19dd34bddb5a7`

- source_problem_id：`938`
- review reasons：`pure_image_choice_task, rewrite_variant_missing, semantic_value_recoverable`
- 图片：![](../ready/mathvision/run_merged_mathvision_300_3040_dedup/datasets/mathvision/artifacts/crops/prob_03ec1ccdf6e19dd34bddb5a7_primary_roi.png)

**原题**

Which of the following solid shapes can be made with these 6 bricks?
<image1>
<image2>

**改写**

Which of the following solid shapes can be made with these 6 bricks?

**分析**

该样本同时触发了多个 review 原因：`pure_image_choice_task, rewrite_variant_missing, semantic_value_recoverable`，属于复合风险案例，不适合直接自动放行。

### Review 案例 4：`prob_08e6e9ea133c5a2f40a616eb`

- source_problem_id：`379`
- review reasons：`index_only_answer, pure_image_option_selection, rewrite_unavailable`
- 图片：![](../ready/mathvision/run_merged_mathvision_300_3040_dedup/datasets/mathvision/artifacts/crops/prob_08e6e9ea133c5a2f40a616eb_primary_roi.png)

**原题**

A square is placed in a co-ordinate system as shown. Each point $(x \mid y)$ of the square is deleted and replaced by the point $\left(\frac{1}{x} \mid \frac{1}{y}\right)$. Which diagram shows the resulting shape?
<image1>
<image2>

**改写**

A square is placed in a co-ordinate system as shown. Each point $(x \mid y)$ of the square is deleted and replaced by the point $\left(\frac{1}{x} \mid \frac{1}{y}\right)$. Which diagram shows the resulting shape?

**分析**

该样本同时触发了多个 review 原因：`index_only_answer, pure_image_option_selection, rewrite_unavailable`，属于复合风险案例，不适合直接自动放行。

### Review 案例 5：`prob_018d5ab2170d3160008ccf7f`

- source_problem_id：`544`
- review reasons：`pure_image_choice_needs_review, rewrite_variant_invalid`
- 图片：![](../ready/mathvision/run_merged_mathvision_300_3040_dedup/datasets/mathvision/artifacts/crops/prob_018d5ab2170d3160008ccf7f_primary_roi.png)

**原题**

Which picture shows a single large loop?
<image1>

**改写**

Which picture shows a single large loop?

**分析**

该样本同时触发了多个 review 原因：`pure_image_choice_needs_review, rewrite_variant_invalid`，属于复合风险案例，不适合直接自动放行。

## 小结

当前数据集同时存在稳定通过样本与需人工复核样本（pass=481, review=433, reject=4）；review 主要集中在 `alignment_requires_review` 一类问题。
