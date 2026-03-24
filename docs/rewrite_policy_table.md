# Rewrite 策略表（工作草案）

_最后更新：2026-03-24_

这份文档是基于全候选 remote smoke 与后续 benchmark 总结出的**当前工作版本**，还不是最终定稿，但已经足够指导下一轮 rewrite-policy 对齐。

## 核心原则

**不要**把所有“看起来像选择题”的题都送进同一条 rewrite 路径。

当前更合理的方向是：
- `blank_open`：适合标准视觉选择题、单一目标问题
- `keep_open`：适合天然开放题、多步题、已经本质开放的题
- `split_open`：适合结构化数学目标、可拆分目标

---

## 数据集级别的当前判断

| 数据集 | 当前常见形态 | 图像依赖 | 常见答案形态 | 当前主导 rewrite | 当前结果快照 | 当前建议 |
|---|---|---:|---|---|---|---|
| SCEMQA | 视觉科学/数学题，题干较短 | 高 | numeric | `blank_open` | 小样本里 reject 偏多 | 先保留 `blank_open`，但要检查阈值与是否存在天然开放型题 |
| Geometry3K | 短几何题，例如 “Find x” | 高 | numeric | `blank_open` | review / reject 混合 | 先保留 `blank_open`，更优先考虑 source-specific 质量放宽 |
| CMM-Math | 文本数学题，集合/范围/结构化目标较多 | 低 | set / range | `split_open` | review 较多 | 保持 `split_open`；当前它是最清晰的 split-open 数据集 |
| MathVision | 视觉 numeric 与视觉 option 混合 | 高 | numeric / option | `keep_open` + `blank_open` 混合 | review / reject 混合 | 必须按题型与答案形态分流，不能强行统一 |
| MM-Math | 带图数学求解题 | 高 | open solution / set | `keep_open` | 小样本里通过率较高 | 保持 `keep_open`；不要强推成 blank-open |
| SeePhys | 带图物理开放题 | 高 | short_text / numeric | `keep_open` | pass / reject 混合 | 保持 `keep_open`；当前质量阈值影响较大 |
| Multi-Physics | 带选项但文字推理较重的物理题 | 高 | option | `keep_open` | pass / reject 混合 | 当前先按 `keep_open` 更稳，后面再根据样本细分 |
| PhysReason | 长 context + 多子问物理推理题 | 高 | short_text / set | `keep_open` | pass / reject 混合 | 保持 `keep_open`；结构上就是 multi-subquestion |
| EEE-Bench | 标准工程视觉选择题 | 高 | option | `blank_open` | pass 较强 | 保持 `blank_open`；它是当前很强的正对照数据集 |
| EMMA-Math | 视觉选择 / 空间图形类数学题 | 高 | option | `blank_open` | pass 较强 | 保持 `blank_open` |
| EMMA-Physics | 视觉物理选择 / 光路图类题 | 高 | short_text / option-like target | `blank_open` | pass 较强 | 保持 `blank_open` |

---

## 按题型理解的当前规则草案

### 1. 标准视觉选择题
**建议策略：** `blank_open`

典型特征：
- 单图或单主图
- 只有一个核心目标
- 题面是典型 MCQ 形式
- 选项是 distractor，而不是多个真实子目标

典型数据集：
- EEE-Bench
- EMMA-Math
- EMMA-Physics
- Geometry3K / MathVision 的一部分

---

### 2. 天然开放的 numeric / derivation 问题
**建议策略：** `keep_open`

典型特征：
- 本来就在问一个值、一个推导结果、一个结论
- 即使源数据里有选项，本质目标还是开放式的
- 强行改成 blank-open 收益不大，反而容易丢语义

典型数据集：
- MM-Math
- MathVision 的一部分 numeric 题
- SeePhys 的一部分题

---

### 3. 多子问结构推理题
**建议策略：** `keep_open`

典型特征：
- 明确存在子问列表
- 一个共享 context 对应多个目标
- 答案天然是列表 / 元组 / 多行结构
- 子部分之间有强依赖

典型数据集：
- PhysReason

---

### 4. 结构化数学目标题
**建议策略：** `split_open`

典型特征：
- 解集 / 区间 / 范围 / 分类讨论
- 外层是一个题，但内部有多个结构化目标
- 拆分后更利于标注和验证

典型数据集：
- CMM-Math

---

## 当前需要特别警惕的点

### 不要只看“表面像 MCQ”
有些题虽然外观上有选项，但本质上已经更像开放题或结构化推理题。

### 不要因为有图就默认 `blank_open`
有些图像依赖题并不是标准视觉选择题，而是更适合保留开放结构。

### 当前质量门槛仍然是混杂因素
有些数据集当前表现差，不一定是 rewrite 策略本身错了，而可能是被以下问题主导：
- `low_resolution`
- `low_text_completeness`

目前受影响最明显的包括：
- SCEMQA
- Geometry3K
- MathVision
- PhysReason / SeePhys / Multi-Physics 的一部分样本

---

## 已记录但暂未实现的 rewrite 改进建议

这一部分是当前推荐的修改方向，**先记入文档，暂不直接改代码实现**。

### 为什么当前策略需要改

核心问题**不是** rewrite prompt 太弱，
而是当前 rewrite 分流太粗。

目前 fallback 逻辑大致还是：
- 没 choices -> `keep_open`
- 纯图片索引题 -> `drop_image_index`
- compound answer -> `split_open`
- 其他有 choices 的题 -> 默认 `blank_open`

最后这一条太激进，会把很多“只是表面像选择题”的题，粗暴送进 `blank_open`，而它们本质上更接近开放题、多步题或结构化目标题。

---

## 建议的 rewrite 类型分层

### 1. 标准视觉选择题
**建议策略：** `blank_open`

典型特征：
- 单图 / 单主图
- 单一目标
- 典型 MCQ wording
- 选项是 distractor，而非真实子问题

典型数据集：
- `EEE-Bench`
- `EMMA-Math`
- `EMMA-Physics`
- `Geometry3K` 的一部分
- `MathVision` 的一部分

---

### 2. 天然开放 numeric / derivation 题
**建议策略：** `keep_open`

典型特征：
- 本来就在问结果、推导、结论
- 就算有选项，语义核心仍然是开放目标
- 改成 blank-open 收益不大

典型数据集：
- `MM-Math`
- `MathVision` 的一部分
- `SeePhys` 的一部分
- `Multi-Physics` 的一部分

---

### 3. 多子问结构推理题
**建议策略：** `keep_open`

典型特征：
- 明确的子问题结构
- 共享 context + 多目标
- 答案天然是多行 / 多段
- 子部分之间相互依赖

典型数据集：
- `PhysReason`

备注：
- 不要把这类题强行改成 `blank_open`
- 也不要默认拆成多个独立题，除非后续 workflow 明确需要子题抽取

---

### 4. 结构化数学目标拆分题
**建议策略：** `split_open`

典型特征：
- set / interval / range 结果
- 一个壳里包含多个内部目标
- 拆开更方便标注与验证

典型数据集：
- `CMM-Math`
- `SCEMQA` 的一部分

---

### 5. 纯图片索引题
**建议策略：** `drop_image_index`

典型特征：
- 问题本质是在选某个图 / 某个 figure index
- 选项语义无法稳定文本化
- rewrite 后很容易退化

---

## 建议的 dataset prior

这些 prior 应该被理解成**弱偏好**，而不是硬编码死规则。

### 偏向 `blank_open`
- `EEE-Bench`
- `EMMA-Math`
- `EMMA-Physics`
- `Geometry3K`（默认如此，但允许例外）

### 偏向 `keep_open`
- `MM-Math`
- `SeePhys`
- `Multi-Physics`
- `PhysReason`

### 偏向 `split_open`
- `CMM-Math`

### 必须按题型分流
- `MathVision`
- `SCEMQA`

---

## 重点数据集的具体建议

### MathVision
当前观察：
- 视觉 numeric 问题更适合 `keep_open`
- 标准视觉 option 问题更适合 `blank_open`

建议：
- 如果题面像 `how many` / `which number` / `what value` / `calculate` / `determine`，并且答案是 numeric / expression -> `keep_open`
- 如果题面是标准对象 / 图形 / figure discrimination -> `blank_open`

### SCEMQA
当前观察：
- 当前 smoke 里 `blank_open` 和 `split_open` 混合出现
- 但很多样本仍然 reject，因此 rewrite 与 quality 还在互相干扰

建议：
- numeric 单目标题 -> `blank_open`
- set / range / structured target 题 -> `split_open`
- 不要把所有 SCEMQA 题都强行走同一条 rewrite 路径

### Geometry3K
当前观察：
- 很多题还是标准的短视觉 numeric 目标，比如 “Find x”
- 当前更像是 quality / threshold 问题，而不是 rewrite 本身的问题

建议：
- 继续把 `blank_open` 作为主默认策略
- 暂时不要在 rewrite 上做大改动
- 先优先处理 threshold / quality 分析

---

## 建议新增的轻量分类函数

理想状态下，rewrite 前应该先做一个很轻量的题型分类。

### `is_multi_subquestion(question_text)`
识别：
- `1. 2. 3.` 样式子题
- `sub-question` 关键词
- `(1)(2)(3)` 这类分解结构

建议动作：
- 路由到 `keep_open`

### `is_set_or_range_target(answer_text, answer_type)`
识别：
- 区间 / 范围 / union / set 这类输出
- 典型数学解集模式

建议动作：
- 路由到 `split_open`

### `is_visual_numeric_open(question_text, answer_type, choices)`
识别：
- `how many`
- `which number`
- `what value`
- `calculate`
- `determine`
- 答案像 numeric 或 expression

建议动作：
- 路由到 `keep_open`

### `is_standard_visual_mcq(question_text, choices, answer_type)`
识别：
- 标准单目标视觉 MCQ
- 选项更像 distractor，而不是多个内部目标

建议动作：
- 路由到 `blank_open`

### `dataset_prior(dataset_name)`
提供一个弱 dataset prior。

建议动作：
- 只作为 tie-breaker，不要硬覆盖明显的题型证据

---

## 建议的 rewrite 决策顺序

1. 纯图片索引题 -> `drop_image_index`
2. 多子问结构 -> `keep_open`
3. set / range / structured target -> `split_open`
4. 视觉 numeric 开放题 -> `keep_open`
5. 数据集 prior 明显偏 `keep_open` 且没有标准 MCQ 证据 -> `keep_open`
6. 标准视觉 MCQ -> `blank_open`
7. 默认兜底 -> `blank_open`

---

## 建议优先实现的第一批改动

如果后续只先改几处，当前最值得优先做的是：

1. 去掉“有 choices 就默认 `blank_open`”这一条过粗规则
2. 显式给：
   - `PhysReason` -> `keep_open`
   - `CMM-Math` -> `split_open`
3. 给 `MathVision` 增加混合型分流逻辑

这些改动目前**只记录在文档中，暂未实现到代码里**。
