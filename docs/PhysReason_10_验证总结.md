# PhysReason 10 条验证总结

## 1. 运行概览

- 运行目录：`outputs/physreason_validation_10_rerun/run_45692c67ba13ca88`
- 数据集：PhysReason
- 请求样本数：10
- 实际处理样本数：10
- 结果分布：`pass=5`，`review=5`，`reject=0`
- 改写策略分布：`keep_open=10`
- 清洗路径分布：`multimodal_full=9`，`text_lightweight=1`
- `requires_image` 分布：`true=9`，`false=1`
- 题型分布：`calculation=6`，`open=3`，`proof=1`

## 2. 整体结论

这 10 条 PhysReason 样本的数据源、图像资产与清洗链路均已跑通。

从结果看：

- PhysReason 样本本身已经是开放题表达，因此这 10 条全部采用 `keep_open`，没有出现额外的题型改写。
- 样本整体以 **长题干、多子问、图文联合求解** 为主，绝大多数都走了 `multimodal_full`。
- 进入 `review` 的 5 条并不是因为没有答案、没有图像或改写失败，而主要是因为图文对齐仍带有风险，典型原因包括：
  - `alignment_requires_review`
  - `metadata_inconsistency`
  - `image_reference_mismatch`
  - `visual_text_consistency_risk`
- 直接 `pass` 的 5 条中，既有图文对应关系较清晰的多模态物理题，也有一条纯文本可解的样本走了 `text_lightweight`。

因此，这轮结果可以作为 **PhysReason 可跑、可改写、可产出开放题样本** 的验证依据；但对于结构复杂、强依赖示意图或轨迹图的题，还需要继续提高图文一致性检查的稳定性。

## 3. 改写前后汇总

| source_problem_id | cleaning_path | 策略 | 结果 | 改写前 | 改写后 | 图片名 |
| --- | --- | --- | --- | --- | --- | --- |
| cal_problem_00035 | multimodal_full | keep_open | pass | An L-shaped skateboard A is initially at rest on a rough horizontal surface ... | An L-shaped skateboard A is initially at rest on a rough horizontal surface ... | `prob_01a437b145f0376c39e3c023_primary.png` |
| cal_problem_00045 | multimodal_full | keep_open | review | In a vertical plane, a block $a$ of mass $m$ is initially at rest at point $A$ directly below the suspension point $O$ ... | In a vertical plane, a block $a$ of mass $m$ is initially at rest at point $A$ directly below the suspension point $O$ ... | `prob_7f8a40f70e2614f26f18c94b_primary.png` |
| cal_problem_00049 | multimodal_full | keep_open | review | A basketball of mass $m$ is dropped from rest at a height $H$ above the ground ... | A basketball of mass $m$ is dropped from rest at a height $H$ above the ground ... | `prob_a857581cd681b52185e46c3b_primary.png` |
| cal_problem_00057 | multimodal_full | keep_open | pass | A simple harmonic transverse wave propagates along the positive direction of the $x$-axis ... | A simple harmonic transverse wave propagates along the positive direction of the $x$-axis ... | `prob_7c5896fc8ee4c3f482175e14_primary.png` |
| cal_problem_00066 | multimodal_full | keep_open | review | A horizontal platform of height $H=0.4m$ is placed on a level ground, on which a rough straight track $AB$ ... | A horizontal platform of height $H=0.4m$ is placed on a level ground, on which a rough straight track $AB$ ... | `prob_c7c80add61e033fda5c0f109_primary.png` |
| cal_problem_00069 | text_lightweight | keep_open | pass | A basketball with a mass of $m = 0.60\mathrm{kg}$ is released from rest at a height of $h_1 = 1.8\mathrm{m}$ above the ground ... | A basketball with a mass of $m = 0.60\mathrm{kg}$ is released from rest at a height of $h_1 = 1.8\mathrm{m}$ above the ground ... |  |
| cal_problem_00080 | multimodal_full | keep_open | pass | As shown in the figure, an elastic bumper is installed at the bottom of a fixed inclined plane with an inclination angle of $\theta$ ... | As shown in the figure, an elastic bumper is installed at the bottom of a fixed inclined plane with an inclination angle of $\theta$ ... | `prob_abee1b6763abe8c5bc46fdce_primary.png` |
| cal_problem_00121 | multimodal_full | keep_open | review | Electromagnetic aircraft launch is the most advanced catapult technology for aircraft carriers ... | Electromagnetic aircraft launch is the most advanced catapult technology for aircraft carriers ... | `prob_1de3cadd4760801be164f51b_primary.png` |
| cal_problem_00122 | multimodal_full | keep_open | pass | Millikan proved the quantization of electric charge by observing the motion of oil droplets ... | Millikan proved the quantization of electric charge by observing the motion of oil droplets ... | `prob_8ff2691d45cdfe92a6e73a5d_primary.png` |
| cal_problem_00128 | multimodal_full | keep_open | review | A horizontal metal ring with a radius of $r=0.2\mathsf{m}$ is fixed. Two metal rods ... | A horizontal metal ring with a radius of $r=0.2\mathsf{m}$ is fixed. Two metal rods ... | `prob_3b609192383fdf1b3340f3bd_primary.png` |

## 4. review 样本说明

以下 5 条进入 `review`：

- `cal_problem_00045`
- `cal_problem_00049`
- `cal_problem_00066`
- `cal_problem_00121`
- `cal_problem_00128`

它们的共同特点是：

- 全部走了 `multimodal_full`
- 都是长题干、多参数、多子问的问题
- `alignment_status` 均为 `risky`
- review 的核心原因不是无答案，而是 **图文对应关系仍有检查风险**

更细一点看：

- `cal_problem_00045`：命中 `metadata_inconsistency`，说明题面与图示元信息之间仍存在不完全一致的地方。
- `cal_problem_00049`：命中 `image_reference_mismatch`，说明题目中提到的图（如 figure(b)）与当前链路识别到的视觉证据对应还不够稳。
- `cal_problem_00066`：命中 `visual_text_consistency_risk`，说明复杂轨道 / 路径类图示和文字描述的一致性仍需人工确认。
- `cal_problem_00121`、`cal_problem_00128`：都命中 `metadata_inconsistency`，说明在多部件、多图或多阶段装置题中，当前结构化解析还存在边界不稳定点。

## 5. pass 样本说明

以下 5 条直接 `pass`：

- `cal_problem_00035`
- `cal_problem_00057`
- `cal_problem_00069`
- `cal_problem_00080`
- `cal_problem_00122`

这些样本可以进一步分成两类：

### 5.1 multimodal_full 且图文对应较稳
- `cal_problem_00035`
- `cal_problem_00057`
- `cal_problem_00080`
- `cal_problem_00122`

这类样本的共同特点是：

- 虽然依赖图像
- 但图中对象、示意关系或图表含义与题面对应关系较明确
- 最终可以稳定形成 `pass`

### 5.2 text_lightweight 直接通过
- `cal_problem_00069`

这条样本的特点是：

- 题面本身已经足够完整
- 不依赖图像即可求解
- `requires_image=false`
- 说明 PhysReason 内部也存在少量可走文本轻量路径的样本

## 6. 本次发现的问题

### 6.1 PhysReason 整体高度偏向强图像依赖的多模态物理题
在本次 10 条验证样本中：

- `requires_image=true` 的有 9 条
- `multimodal_full` 的有 9 条

这说明 PhysReason 和 MathVision / MSEarth 不完全一样，它更稳定地属于：

> **长题干 + 示意图/装置图/轨迹图 + 多步物理求解**

后续如果继续扩规模，默认应按 **multimodal physics reasoning** 的标准来评估，而不是按轻量开放问答来处理。

### 6.2 review 的主因是复杂图示带来的图文一致性风险
当前 review 的 5 条并没有出现：

- rewrite strategy 异常
- normalization 失败
- 答案字段缺失

问题集中在：

- 图示与题干的精确对应
- 图中装置 / 轨迹 /部件与文本描述的一致性
- 复杂场景下的 metadata 稳定性

也就是说，PhysReason 当前的瓶颈不是“不会改写”，而是：

> **复杂物理场景图能否被稳定地结构化、并与长题干中的变量和子问一一对应。**

### 6.3 keep_open 是合理策略，但不等于后处理风险小
虽然这 10 条全部采用 `keep_open`，说明原题本身已是开放表达，改写压力不大；
但由于 PhysReason 题目往往：

- 题干长
- 参数多
- 子问多
- 图示依赖强

所以即使 rewrite 很稳定，后续的 alignment / review 压力仍然不小。

## 7. 结论建议

PhysReason 当前已经具备继续扩大样本规模的基础，但后续推进时建议重点关注：

- **multimodal_full + review** 的复杂装置图 / 轨迹图 / 电磁图样本
- 图中部件、变量、路径与题干子问的一一对应
- metadata inconsistency 类风险的专项排查

如果后续继续跑更大规模批次：

1. `pass` 样本可直接进入后续链路；
2. `review` 样本建议单独汇总复核；
3. 优先对复杂多子问物理题补强图文一致性检查，而不是只盯改写策略本身。
