# mm_math 改写样例分析

- 生成时间：`2026-04-07T10:10:13Z`
- ready 包：`ready/mm_math_000_300`
- 自动结果分布：`pass=71 / review=229 / reject=0`

## Pass 样本分析

- pass 样本数：`71`
- 改写策略分布：`keep_open=300`

### Pass 案例 1：`prob_003535887710f4181084a54b`

- source_problem_id：`52719959.png`
- rewrite_strategy：`keep_open`
- 图片：![](../ready/mm_math_000_300/datasets/mm_math/artifacts/crops/prob_003535887710f4181084a54b_primary_roi.png)

**原题**

According to legend, the ancient Greek mathematician and astronomer Thales once used the principle of similar triangles by erecting a wooden pole at the top of the shadow of a pyramid. With the help of sunlight, he constructed two similar triangles to measure the height of the pyramid. Given that the wooden pole $EF$ is $2m$ long and its shadow $FD$ is $3m$ long, and $OA$ is measured to be $201m$, what is the height of the pyramid $BO$?

**改写**

According to legend, the ancient Greek mathematician and astronomer Thales once used the principle of similar triangles by erecting a wooden pole at the top of the shadow of a pyramid. With the help of sunlight, he constructed two similar triangles to measure the height of the pyramid. Given that the wooden pole $EF$ is $2m$ long and its shadow $FD$ is $3m$ long, and $OA$ is measured to be $201m$, what is the height of the pyramid $BO$?

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。

### Pass 案例 2：`prob_00d9e224e4ded99f67fb1ab4`

- source_problem_id：`55138467.png`
- rewrite_strategy：`keep_open`
- 图片：![](../ready/mm_math_000_300/datasets/mm_math/artifacts/crops/prob_00d9e224e4ded99f67fb1ab4_primary_roi.png)

**原题**

As shown in the figure, what will be the shape after the planar figure is pulled into a three-dimensional form?

**改写**

As shown in the figure, what will be the shape after the planar figure is pulled into a three-dimensional form?

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。

### Pass 案例 3：`prob_05e10aeab052542dbe66bd96`

- source_problem_id：`51435436.png`
- rewrite_strategy：`keep_open`
- 图片：![](../ready/mm_math_000_300/datasets/mm_math/artifacts/crops/prob_05e10aeab052542dbe66bd96_primary_roi.png)

**原题**

As shown in the figure, what is the sum of $ \angle 1+\angle 2+\angle 3+\angle 4+\angle 5+\angle 6$ in degrees?

**改写**

As shown in the figure, what is the sum of $\angle 1+\angle 2+\angle 3+\angle 4+\angle 5+\angle 6$ in degrees?

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。

### Pass 案例 4：`prob_07ce132e213e83cf55e4715c`

- source_problem_id：`51369188.png`
- rewrite_strategy：`keep_open`
- 图片：![](../ready/mm_math_000_300/datasets/mm_math/artifacts/crops/prob_07ce132e213e83cf55e4715c_primary_roi.png)

**原题**

As shown in the figure, \( \triangle ADE \cong \triangle BCF \), \( AD = 10 \) cm, \( CD = 6 \) cm, then what is the length of \( BD \)?

**改写**

As shown in the figure, \(\triangle ADE \cong \triangle BCF\), \(AD = 10\) cm, \(CD = 6\) cm. What is the length of \(BD\)?

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。

### Pass 案例 5：`prob_1123ecdd917acab9a2736b95`

- source_problem_id：`51435316.png`
- rewrite_strategy：`keep_open`
- 图片：![](../ready/mm_math_000_300/datasets/mm_math/artifacts/crops/prob_1123ecdd917acab9a2736b95_primary_roi.png)

**原题**

As shown in the figure, in $\triangle ABC$, point E is on the extension line of BC. The angle bisectors of $\angle ABC$ and $\angle ACE$ intersect at point D, $\angle D=15^\circ$. What is the degree measure of $\angle A$?

**改写**

In $\triangle ABC$, point $E$ is on the extension of $BC$. The angle bisectors of $\angle ABC$ and $\angle ACE$ intersect at point $D$. Given $\angle D = 15^\circ$, what is the measure of $\angle A$?

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。

## Review 原因分析

| review reason | count |
| --- | --- |
| alignment_requires_review | 221 |
| visual_evidence_uncertain | 56 |
| metadata_inconsistency | 35 |
| small_image | 8 |
| minor_visual_risk | 5 |
| metadata_mismatch | 5 |
| metadata_image_path_mismatch | 5 |
| image_reference_mismatch | 5 |

### Review 案例 1：`prob_00ba32265539e415e7d49167`

- source_problem_id：`53151323.png`
- review reasons：`alignment_requires_review, visual_evidence_uncertain`
- 图片：![](../ready/mm_math_000_300/datasets/mm_math/artifacts/crops/prob_00ba32265539e415e7d49167_primary_roi.png)

**原题**

As shown in the figure, in rectangle $ABCD$, $AB = 5$, $BC = 6$, point $E$ is on side $BC$, and $BE = 2$. $F$ is a moving point on side $AB$. Connect $EF$, and construct an equilateral $\triangle EFG$ with $EF$ as a side, and point $G$ is inside rectangle $ABCD$. Connect $CG$. What is the minimum value of $CG$?

**改写**

In rectangle $ABCD$, $AB = 5$, $BC = 6$, point $E$ is on side $BC$, and $BE = 2$. Point $F$ is a moving point on side $AB$. Connect $EF$, and construct an equilateral $\triangle EFG$ with $EF$ as a side, where point $G$ is inside rectangle $ABCD$. Connect $CG$. What is the minimum value of $CG$?

**分析**

该样本同时触发了多个 review 原因：`alignment_requires_review, visual_evidence_uncertain`，属于复合风险案例，不适合直接自动放行。

### Review 案例 2：`prob_0151d63459e9a09f52c78632`

- source_problem_id：`51379110.png`
- review reasons：`alignment_requires_review, visual_evidence_uncertain`
- 图片：![](../ready/mm_math_000_300/datasets/mm_math/artifacts/crops/prob_0151d63459e9a09f52c78632_primary_roi.png)

**原题**

As shown in the figure, the grid is a square grid, and A, B, C, D, E, F are the intersections of the grid lines. What is the ratio of the area of $\triangle ABC$ to the area of $\triangle DEF$?

**改写**

As shown in the figure, the grid is a square grid, and A, B, C, D, E, F are the intersections of the grid lines. What is the ratio of the area of $\triangle ABC$ to the area of $\triangle DEF$?

**分析**

该样本同时触发了多个 review 原因：`alignment_requires_review, visual_evidence_uncertain`，属于复合风险案例，不适合直接自动放行。

### Review 案例 3：`prob_1c85bdcf26d625900bdcbd25`

- source_problem_id：`53065844.png`
- review reasons：`alignment_requires_review, metadata_inconsistency`
- 图片：![](../ready/mm_math_000_300/datasets/mm_math/artifacts/images/prob_1c85bdcf26d625900bdcbd25_primary.png)

**原题**

As shown in the figure, the graphs of the inverse proportion functions $y_{1}=-\frac{1}{x}$ and $y_{2}=-\frac{4}{x}$ are depicted. Points A and C are located on the x-axis and y-axis, respectively. Quadrilateral $OABC$ is a square. The sides $AB$ and $BC$ intersect the graphs of the inverse proportion functions $y_{2}$ and $y_{1}$ at points F, H and points E, G, respectively. If $OA=3$, what is the value of $\frac{EF}{GH}$?

**改写**

As shown in the figure, the graphs of the inverse proportion functions $y_{1}=-\frac{1}{x}$ and $y_{2}=-\frac{4}{x}$ are depicted. Points A and C are located on the x-axis and y-axis, respectively. Quadrilateral $OABC$ is a square. The sides $AB$ and $BC$ intersect the graphs of the inverse proportion functions $y_{2}$ and $y_{1}$ at points F, H and points E, G, respectively. If $OA=3$, what is the value of $\frac{EF}{GH}$?

**分析**

该样本同时触发了多个 review 原因：`alignment_requires_review, metadata_inconsistency`，属于复合风险案例，不适合直接自动放行。

### Review 案例 4：`prob_1b928273c881a1ad23cd8359`

- source_problem_id：`52550870.png`
- review reasons：`small_image, visual_evidence_uncertain`
- 图片：![](../ready/mm_math_000_300/datasets/mm_math/artifacts/crops/prob_1b928273c881a1ad23cd8359_primary_roi.png)

**原题**

As shown in the figure, what is the sum of $\angle 1 + \angle 2 + \angle 3 + \angle 4 + \angle 5 + \angle 6 + \angle 7$?

**改写**

As shown in the figure, what is the sum of $\angle 1 + \angle 2 + \angle 3 + \angle 4 + \angle 5 + \angle 6 + \angle 7$?

**分析**

该样本同时触发了多个 review 原因：`small_image, visual_evidence_uncertain`，属于复合风险案例，不适合直接自动放行。

### Review 案例 5：`prob_186b9aa7645e8a7fce717d1b`

- source_problem_id：`52836781.png`
- review reasons：`alignment_requires_review, minor_visual_risk`
- 图片：![](../ready/mm_math_000_300/datasets/mm_math/artifacts/images/prob_186b9aa7645e8a7fce717d1b_primary.png)

**原题**

As shown in the figure, point C is on the line segment BG. With BC and CG as sides, squares are constructed on both sides, with areas denoted by $S_{1}$ and $S_{2}$ respectively. The sum of the areas of the two squares is $S_{1}+S_{2}=40$. Given that BG=8, what is the area of the shaded part in the figure?

**改写**

As shown in the figure, point C is on the line segment BG. With BC and CG as sides, squares are constructed on both sides, with areas denoted by $S_{1}$ and $S_{2}$ respectively. The sum of the areas of the two squares is $S_{1}+S_{2}=40$. Given that BG=8, what is the area of the shaded part in the figure?

**分析**

该样本同时触发了多个 review 原因：`alignment_requires_review, minor_visual_risk`，属于复合风险案例，不适合直接自动放行。

## 小结

当前数据集 `review` 数量高于 `pass`（pass=71, review=229, reject=0），更像是审核偏严或对齐风险较高；高频原因集中在 `alignment_requires_review`。
