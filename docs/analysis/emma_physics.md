# emma_physics 改写样例分析

- 生成时间：`2026-04-07T10:10:09Z`
- ready 包：`ready/emma_physics/run_filtered_emma_physics_safe`
- 自动结果分布：`pass=180 / review=0 / reject=0`

## Pass 样本分析

- pass 样本数：`180`
- 改写策略分布：`blank_open=61, keep_open=117, split_open=2`

### Pass 案例 1：`prob_051562b68ad54fcaff6c7df9`

- source_problem_id：`12`
- rewrite_strategy：`keep_open`
- 图片：![](../ready/emma_physics/run_filtered_emma_physics_safe/datasets/emma_physics/artifacts/crops/prob_051562b68ad54fcaff6c7df9_primary_roi.png)

**原题**

A quarantined physics student decides to perform an experiment to land a small box of mass $m=60 \mathrm{~g}$ onto the center of a target a distance $\Delta d$ away. The student puts the box on a top of a frictionless ramp with height $h_{2}=0.5 \mathrm{~m}$ that is angled $\theta=30^{\circ}$ to the horizontal on a table that is $h_{1}=4 \mathrm{~m}$ above the floor. If the student pushes the spring with spring constant $k=6.5 \mathrm{~N} / \mathrm{m}$ down by $\Delta x=0.3 \mathrm{~m}$ compared to its rest length and lands the box exactly on the target, what is $\Delta d$ ? Answer in meters. You may assume friction is negligible.

<image_1>

**改写**

A quarantined physics student decides to perform an experiment to land a small box of mass $m=60 \mathrm{~g}$ onto the center of a target a distance $\Delta d$ away. The student puts the box on top of a frictionless ramp with height $h_{2}=0.5 \mathrm{~m}$ that is angled $\theta=30^{\circ}$ to the horizontal on a table that is $h_{1}=4 \mathrm{~m}$ above the floor. If the student pushes the spring with spring constant $k=6.5 \mathrm{~N} / \mathrm{m}$ down by $\Delta x=0.3 \mathrm{~m}$ compared to its rest length and lands the box exactly on the target, what is $\Delta d$? Answer in meters. You may assume friction is negligible.

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

### Pass 案例 2：`prob_002fcf6a6a21a0b815ecb7a9`

- source_problem_id：`77`
- rewrite_strategy：`blank_open`
- 图片：![](../ready/emma_physics/run_filtered_emma_physics_safe/datasets/emma_physics/artifacts/crops/prob_002fcf6a6a21a0b815ecb7a9_primary_roi.png)

**原题**

A block (B) is attached to two unstretched springs S1 and S2 with spring constants $k$ and $4k$, respectively (see figure I). The other ends are attached to identical supports M1 and M2 not attached to the walls. The springs and supports have negligible mass. There is no friction anywhere. The block B is displaced towards wall 1 by a small distance $x$ (figure II) and released. The block returns and moves a maximum distance $y$ towards wall 2. Displacements $x$ and $y$ are measured with respect to the equilibrium position of the block B. The ratio $\frac{y}{x}$ is
<image_1>

**改写**

A block (B) is attached to two unstretched springs S1 and S2 with spring constants $k$ and $4k$, respectively (see figure I). The other ends are attached to identical supports M1 and M2 not attached to the walls. The springs and supports have negligible mass. There is no friction anywhere. The block B is displaced towards wall 1 by a small distance $x$ (figure II) and released. The block returns and moves a maximum distance $y$ towards wall 2. Displacements $x$ and $y$ are measured with respect to the equilibrium position of the block B. What is the ratio $\frac{y}{x}$?

**分析**

该样本自动结果为 `pass`，改写策略是 `blank_open`。 改写把原始素材整理成开放问答形式，但没有引入新的审查风险信号。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

### Pass 案例 3：`prob_b1597f12ed12843d69855691`

- source_problem_id：`108`
- rewrite_strategy：`split_open`
- 图片：![](../ready/emma_physics/run_filtered_emma_physics_safe/datasets/emma_physics/artifacts/crops/prob_b1597f12ed12843d69855691_primary_roi.png)

**原题**

17. Four charges $Q_1$, $Q_2$, $Q_3$ and $Q_4$ of same magnitude are fixed along the $x$ axis at $x = -2a$, $-a$, $+a$ and $+2a$, respectively. A positive charge $q$ is placed on the positive $y$ axis at a distance $b > 0$. Four options of the signs of these charges are given in List I. The direction of the forces on the charge $q$ is given in List II. Match List I with List II and select the correct answer using the code given below the lists.

List I
P. $Q_1$, $Q_2$, $Q_3$, $Q_4$ all positive
Q. $Q_1$, $Q_2$ positive; $Q_3$, $Q_4$ negative
R. $Q_1$, $Q_4$ positive; $Q_2$, $Q_3$ negative
S. $Q_1$, $Q_3$ positive; $Q_2$, $Q_4$ negative

List II
1. $+x$
2. $-x$
3. $+y$
4. $-y$
<image_1>

**改写**

Four charges $Q_1$, $Q_2$, $Q_3$ and $Q_4$ of equal magnitude are fixed on the $x$ axis at $x=-2a$, $-a$, $+a$ and $+2a$, respectively. A positive charge $q$ is placed on the positive $y$ axis at a distance $b>0$. If $Q_1$, $Q_2$, $Q_3$, and $Q_4$ are all positive, what is the direction of the net force on $q$?

**分析**

该样本自动结果为 `pass`，改写策略是 `split_open`。 虽然经过拆分式改写，但仍通过了自动检查，说明题意保持较稳定。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

### Pass 案例 4：`prob_03caa28f2784f47d3ea59757`

- source_problem_id：`34`
- rewrite_strategy：`blank_open`
- 图片：![](../ready/emma_physics/run_filtered_emma_physics_safe/datasets/emma_physics/artifacts/crops/prob_03caa28f2784f47d3ea59757_primary_roi.png)

**原题**

Three point charges of \( +Q \), \( +2Q \), and \( -Q \) are each located a distance \( r \) away from the origin, as shown above. The magnitude of the electric field at the origin due to these charges is:

<image_1>

**改写**

Three point charges of \( +Q \), \( +2Q \), and \( -Q \) are each located a distance \( r \) away from the origin, as shown above. What is the magnitude of the electric field at the origin due to these charges?

**分析**

该样本自动结果为 `pass`，改写策略是 `blank_open`。 改写把原始素材整理成开放问答形式，但没有引入新的审查风险信号。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

### Pass 案例 5：`prob_05d06e75b6875eb4a995de22`

- source_problem_id：`138`
- rewrite_strategy：`blank_open`
- 图片：![](../ready/emma_physics/run_filtered_emma_physics_safe/datasets/emma_physics/artifacts/crops/prob_05d06e75b6875eb4a995de22_primary_roi.png)

**原题**

A wheel consists of three uniform spokes, with length \( R \) and mass \( M \), mounted 120 degrees apart on a horizontal frictionless axle and connected by a rim of negligible mass. Consider the counterclockwise direction to be positive. When the spokes are oriented as shown in the diagram above, the net Torque on the wheel due to the weight of the spokes is
<image_1>

**改写**

A wheel consists of three uniform spokes, each with length \(R\) and mass \(M\), mounted 120 degrees apart on a horizontal frictionless axle and connected by a rim of negligible mass. Consider the counterclockwise direction to be positive. When the spokes are oriented as shown in the diagram above, what is the net torque on the wheel due to the weight of the spokes?

**分析**

该样本自动结果为 `pass`，改写策略是 `blank_open`。 改写把原始素材整理成开放问答形式，但没有引入新的审查风险信号。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

## Review 原因分析

当前 ready 包没有可统计的 review reason codes。

当前 ready 包没有 `clean_decision=review` 的样本；该数据集当前只能分析 pass 改写例子。

## 小结

当前 ready 包以 `pass` 为主（pass=180, review=0, reject=0），更适合当作稳定改写样本集来观察。
