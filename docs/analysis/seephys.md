# seephys 改写样例分析

- 生成时间：`2026-04-07T10:10:12Z`
- ready 包：`ready/seephys_000_300`
- 自动结果分布：`pass=243 / review=56 / reject=1`

## Pass 样本分析

- pass 样本数：`243`
- 改写策略分布：`keep_open=299, split_open=1`

### Pass 案例 1：`prob_00e797bd7d9d310bd6142bef`

- source_problem_id：`140`
- rewrite_strategy：`keep_open`
- 图片：![](../ready/seephys_000_300/datasets/seephys/artifacts/crops/prob_00e797bd7d9d310bd6142bef_aux_2_roi.png)

**原题**

A disk of mass $M$ and radius $R$ slides without friction on a horizontal surface. Another disk of mass $m$ and radius $r$ is pinned through its center to a point off the center of the first disk by a distance $b$, so that it can rotate without friction on the first disk as shown in Fig. 2.2. Describe the motion and identify its constants.

**改写**

A disk of mass $M$ and radius $R$ slides without friction on a horizontal surface. Another disk of mass $m$ and radius $r$ is pinned through its center to a point off the center of the first disk by a distance $b$, so that it can rotate without friction on the first disk as shown in Fig. 2.2. Describe the motion and identify its constants.

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。

### Pass 案例 2：`prob_00f076483f3bb93af10fa642`

- source_problem_id：`100`
- rewrite_strategy：`keep_open`
- 图片：![](../ready/seephys_000_300/datasets/seephys/artifacts/crops/prob_00f076483f3bb93af10fa642_primary_roi.png)

**原题**

Name the lowest electric multipole in the radiation field emitted by the following time-varying charge distributions. A uniform charged spherical shell whose radius varies as $R=R_{0}+R_{1}\cos(\omega t)$.

**改写**

Name the lowest electric multipole in the radiation field emitted by the following time-varying charge distributions. A uniform charged spherical shell whose radius varies as $R=R_{0}+R_{1}\cos(\omega t)$.

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。

### Pass 案例 3：`prob_0578a15dad9f8774e9ab6da4`

- source_problem_id：`144`
- rewrite_strategy：`keep_open`
- 图片：![](../ready/seephys_000_300/datasets/seephys/artifacts/crops/prob_0578a15dad9f8774e9ab6da4_primary_roi.png)

**原题**

Two equal point masses $M$ are connected by a massless rigid rod of length $2A$ (a dumbbell) which is constrained to rotate about an axle fixed to the center of the rod at an angle $\theta$. The center of the rod is at the origin of coordinates, the axle along the $z$-axis, and the dumbbell lies in the $xz$-plane at $t=0$. The angular velocity $\omega$ is a constant in time and is directed along the $z$-axis. Using the equation $\mathbf{L}=\mathbf{r}\times\mathbf{p}$, calculate the angular momentum and show that it is equal to the answer for part (b).

**改写**

Two equal point masses $M$ are connected by a massless rigid rod of length $2A$ (a dumbbell) which is constrained to rotate about an axle fixed to the center of the rod at an angle $\theta$. The center of the rod is at the origin of coordinates, the axle along the $z$-axis, and the dumbbell lies in the $xz$-plane at $t=0$. The angular velocity $\omega$ is a constant in time and is directed along the $z$-axis. Using the equation $\mathbf{L}=\mathbf{r}\times\mathbf{p}$, calculate the angular momentum and show that it is equal to the answer for part (b).

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。

### Pass 案例 4：`prob_06c08a7cd4b90020402a5229`

- source_problem_id：`49`
- rewrite_strategy：`keep_open`
- 图片：![](../ready/seephys_000_300/datasets/seephys/artifacts/crops/prob_06c08a7cd4b90020402a5229_primary_roi.png)

**原题**

Four identical masses are connected by four identical springs and constrained to move on a frictionless circle of radius $b$ as shown in Fig. 2.30. What are the frequencies of small oscillations?

**改写**

Four identical masses are connected by four identical springs and constrained to move on a frictionless circle of radius $b$ as shown in Fig. 2.30. What are the frequencies of small oscillations?

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。

### Pass 案例 5：`prob_082aa83c6094b43a58a922e4`

- source_problem_id：`224`
- rewrite_strategy：`keep_open`
- 图片：![](../ready/seephys_000_300/datasets/seephys/artifacts/crops/prob_082aa83c6094b43a58a922e4_primary_roi.png)

**原题**

A uniform solid ball of radius $a$ rolling with velocity $v$ on a level surface collides inelastically with a step of height $h<a$, as shown in Fig. 1.172. Find, in terms of $h$ and $a$, the minimum velocity for which the ball will "trip" up over the step. Assume that no slipping occurs at the impact point, and remember that the moment of inertia of a solid sphere with respect to an axis through its center is $\frac{2}{5} M a^{2}$.

**改写**

A uniform solid ball of radius $a$ rolling with velocity $v$ on a level surface collides inelastically with a step of height $h<a$, as shown in Fig. 1.172. Find, in terms of $h$ and $a$, the minimum velocity for which the ball will "trip" up over the step. Assume that no slipping occurs at the impact point, and remember that the moment of inertia of a solid sphere with respect to an axis through its center is $\frac{2}{5} M a^{2}$.

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。

## Review 原因分析

| review reason | count |
| --- | --- |
| alignment_requires_review | 9 |
| missing_prior_context | 5 |
| visual_evidence_uncertain | 4 |
| answer_incomplete | 3 |
| partial_completeness | 3 |
| normalization_incomplete | 3 |
| notation_inconsistency | 3 |
| question_incomplete | 3 |

### Review 案例 1：`prob_2d7ca75d35bc56e3c74cf846`

- source_problem_id：`64`
- review reasons：`alignment_requires_review, visual_grounding_missing`
- 图片：![](../ready/seephys_000_300/datasets/seephys/artifacts/crops/prob_2d7ca75d35bc56e3c74cf846_primary_roi.png)

**原题**

Find the expression for the speed of the transverse elastic wave.

**改写**

Find the expression for the speed of the transverse elastic wave.

**分析**

该样本同时触发了多个 review 原因：`alignment_requires_review, visual_grounding_missing`，属于复合风险案例，不适合直接自动放行。

### Review 案例 2：`prob_1116c8393a536e242ac9805a`

- source_problem_id：`273`
- review reasons：`missing_prior_context, notation_partly_implicit`
- 图片：![](../ready/seephys_000_300/datasets/seephys/artifacts/crops/prob_1116c8393a536e242ac9805a_primary_roi.png)

**原题**

A spherical pendulum consists of a point mass $m$ tied by a string of length $l$ to a fixed point, so that it is constrained to move on a spherical surface as shown in Fig. 2.14. The mass in the circular orbit as in part (a) above receives an impulse perpendicular to its velocity, resulting in an orbit which has its highest point with the string making an angle $\theta_{1}$ with the vertical. Write down (but do not try to solve) the equation which may be solved for the angle the string makes with the vertical when the mass is at its lowest point.

**改写**

A spherical pendulum consists of a point mass $m$ tied by a string of length $l$ to a fixed point, so that it is constrained to move on a spherical surface as shown in Fig. 2.14. The mass in the circular orbit as in part (a) above receives an impulse perpendicular to its velocity, resulting in an orbit which has its highest point with the string making an angle $\theta_{1}$ with the vertical. Write down (but do not try to solve) the equation which may be solved for the angle the string makes with the vertical when the mass is at its lowest point.

**分析**

该样本同时触发了多个 review 原因：`missing_prior_context, notation_partly_implicit`，属于复合风险案例，不适合直接自动放行。

### Review 案例 3：`prob_2ebd17d487b7e454be433eca`

- source_problem_id：`262`
- review reasons：`figure_reference_mismatch, visual_evidence_uncertain`
- 图片：![](../ready/seephys_000_300/datasets/seephys/artifacts/crops/prob_2ebd17d487b7e454be433eca_primary_roi.png)

**原题**

A uniform thin rigid rod of mass $M$ is supported by two rapidly rotating rollers, whose axes are separated by a fixed distance $a$. The rod is initially placed at rest asymmetrically, as shown in Fig. 1.114. Now consider the case in which the directions of rotation of the rollers are reversed, as shown in Fig. 1.115. Calculate the displacement $x(t)$, again assuming $x(0)=x_{0}$ and $\dot{x}(0)=0$.

**改写**

A uniform thin rigid rod of mass $M$ is supported by two rapidly rotating rollers, whose axes are separated by a fixed distance $a$. The rod is initially placed at rest asymmetrically, as shown in Fig. 1.114. Now consider the case in which the directions of rotation of the rollers are reversed, as shown in Fig. 1.115. Calculate the displacement $x(t)$, assuming $x(0)=x_{0}$ and $\dot{x}(0)=0$.

**分析**

该样本同时触发了多个 review 原因：`figure_reference_mismatch, visual_evidence_uncertain`，属于复合风险案例，不适合直接自动放行。

### Review 案例 4：`prob_0e47956d455a1daebf8f5be8`

- source_problem_id：`160`
- review reasons：`answer_incomplete, question_answer_mismatch`
- 图片：![](../ready/seephys_000_300/datasets/seephys/artifacts/crops/prob_0e47956d455a1daebf8f5be8_primary_roi.png)

**原题**

Paris and London are connected by a straight subway tunnel (see Fig. 1.19). A train travels between the two cities powered only by the gravitational force of the earth. Calculate the maximum speed of the train and the time taken to travel from London to Paris. The distance between the two cities is 300 km and the radius of the earth is 6400 km. Neglect friction.

**改写**

Paris and London are connected by a straight subway tunnel (see Fig. 1.19). A train travels between the two cities powered only by the gravitational force of the earth. Calculate the maximum speed of the train and the time taken to travel from London to Paris. The distance between the two cities is 300 km and the radius of the earth is 6400 km. Neglect friction.

**分析**

该样本同时触发了多个 review 原因：`answer_incomplete, question_answer_mismatch`，属于复合风险案例，不适合直接自动放行。

### Review 案例 5：`prob_190214888a0a6dd9f9062df6`

- source_problem_id：`85`
- review reasons：`minor_symbol_definition_gap, partial_completeness`
- 图片：![](../ready/seephys_000_300/datasets/seephys/artifacts/crops/prob_190214888a0a6dd9f9062df6_primary_roi.png)

**原题**

In an experiment a beam of silver atoms emerges from an oven, which contains silver vapor at $T=1200 \, \mathrm{K}$. The beam is collimated by being passed through a small circular aperture. If the screen is at $L=1$ meter from the aperture, estimate numerically the smallest $D$ that can be obtained by varying $a$. (You may assume for simplicity that all atoms have the same momentum along the direction of the beam and have a mass of $\left.M_{\mathrm{Ag}}=1.8 \times 10^{-22} \, \mathrm{g}\right)$.

**改写**

In an experiment a beam of silver atoms emerges from an oven, which contains silver vapor at $T=1200 \, \mathrm{K}$. The beam is collimated by being passed through a small circular aperture. If the screen is at $L=1$ meter from the aperture, estimate numerically the smallest $D$ that can be obtained by varying $a$. (You may assume for simplicity that all atoms have the same momentum along the direction of the beam and have a mass of $\left.M_{\mathrm{Ag}}=1.8 \times 10^{-22} \, \mathrm{g}\right)$.

**分析**

该样本同时触发了多个 review 原因：`minor_symbol_definition_gap, partial_completeness`，属于复合风险案例，不适合直接自动放行。

## 小结

当前数据集同时存在稳定通过样本与需人工复核样本（pass=243, review=56, reject=1）；review 主要集中在 `alignment_requires_review` 一类问题。
