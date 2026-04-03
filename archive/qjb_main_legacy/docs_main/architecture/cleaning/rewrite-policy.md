# Rewrite Policy（基于 prompt 与代码证据）

> 本文档用于记录 **rewrite 策略对齐说明**。
>
> 当前口径基于本仓库内可验证证据：
> - rewrite prompt：[prompts/cleaning/rewrite_agent.md](prompts/cleaning/rewrite_agent.md)
> - 当前 rewrite 实现：[benchmark/src/pipeline_rewrite.py](benchmark/src/pipeline_rewrite.py)
> - pre-ler 快照参考：[archive/pre-ler-main-python-2026-03-25/run_pipeline.py](archive/pre-ler-main-python-2026-03-25/run_pipeline.py)
>
> 说明：若后续拿到明确的 ler 分支实现快照，应再做一次逐条对齐并更新本文档。
>
> - 总体架构与阶段划分请看：[docs/architecture/overview/pipeline-architecture.md](docs/architecture/overview/pipeline-architecture.md)
> - 字段级稳定契约（rewrite report / gate / records）请看：[docs/contracts/PIPELINE_MODULE_CONTRACTS.md](docs/contracts/PIPELINE_MODULE_CONTRACTS.md)

_最后更新：2026-03-29（prompt/code 对齐版本）_

## 1. 核心目标

rewrite 的目标不是“把所有题统一改成同一种形态”，而是：

- 对**标准视觉选择题**：把 option-target 显式转换成开放式 blank（`blank_open`）
- 对**天然开放题 / 推导题 / 多步推理题**：尽量保留开放结构（`keep_open`）
- 对**结构化数学目标（解集/区间/范围/多原子答案）**：拆分成可标注的子目标（`split_open`）
- 对**纯图片索引/标号选择**：
	- 能保留有效开放目标时优先 `blank_open`
	- 仅在不可恢复为有效开放目标时使用 `drop_image_index`

## 2. 三条底线（避免最常见误分流）

1) **不要只因为“看起来像 MCQ”就走 `blank_open`**
- 有些题虽然有选项，但语义核心仍是开放目标（例如求值/推导/结论）。

2) **不要只因为“依赖图像”就默认 `blank_open`**
- 图像依赖并不等于标准视觉选择题。

3) **质量阈值是混杂因素**
- 有些数据集表现差不一定是 rewrite 策略错了，可能主要被 `low_resolution` / `low_text_completeness` 等质量问题主导。

## 3. 数据集级别的当前判断（弱 prior）

> 这些 prior 只能当 tie-breaker，不应硬覆盖明显的题型证据。

| 数据集 | 当前常见形态 | 图像依赖 | 常见答案形态 | 当前主导 rewrite | 当前建议 |
|---|---|---:|---|---|---|
| SCEMQA | 视觉科学/数学题，题干较短 | 高 | numeric | `blank_open` | 先保留 `blank_open`，但需检查阈值与天然开放型题占比 |
| Geometry3K | 短几何题（“Find x”） | 高 | numeric | `blank_open` | 继续 `blank_open`；更优先排查 quality/threshold |
| CMM-Math | 文本数学，集合/范围/结构化目标多 | 低 | set / range | `split_open` | 保持 `split_open`（当前最清晰的 split-open 数据集） |
| MathVision | 视觉 numeric 与视觉 option 混合 | 高 | numeric / option | 混合 | 必须按题型分流，不能强行统一 |
| MM-Math | 带图数学求解 | 高 | open solution / set | `keep_open` | 保持 `keep_open` |
| SeePhys | 带图物理开放题 | 高 | short_text / numeric | `keep_open` | 保持 `keep_open`（阈值影响大） |
| Multi-Physics | 推理较重、表面 option 的物理题 | 高 | option | `keep_open` | 目前先 `keep_open` 更稳，后续再细分 |
| PhysReason | 长 context + 多子问推理 | 高 | short_text / set | `keep_open` | 保持 `keep_open`（结构上就是 multi-subquestion） |
| EEE-Bench | 标准工程视觉选择题 | 高 | option | `blank_open` | 保持 `blank_open`（强正对照） |
| EMMA-Math | 视觉选择/空间图形数学题 | 高 | option | `blank_open` | 保持 `blank_open` |
| EMMA-Physics | 视觉物理选择题（光路图等） | 高 | short_text / option-like target | `blank_open` | 保持 `blank_open` |

## 4. 按题型理解的规则（工作草案）

### 4.1 标准视觉选择题 → `blank_open`

特征：
- 单图/单主图
- 单一核心目标
- 典型 MCQ wording
- 选项是 distractor，而不是多个真实子目标

典型数据集：EEE-Bench、EMMA-*、Geometry3K/MathVision 的一部分。

### 4.2 天然开放 numeric / derivation → `keep_open`

特征：
- 本来就在问一个值/一个推导结论
- 即使源数据有选项，语义核心仍是开放目标
- 强行改成 blank-open 可能丢语义

典型数据集：MM-Math、MathVision 的一部分、SeePhys 的一部分。

### 4.3 多子问结构推理题 → `keep_open`

特征：
- 明确存在子问列表
- 一个共享 context 对应多个目标
- 答案天然是列表/多段/多行结构

典型数据集：PhysReason。

### 4.4 结构化数学目标（解集/区间/范围/多原子答案）→ `split_open`

特征：
- set / interval / range 输出
- 一个题壳内包含多个结构化目标
- 拆分后更利于标注与验证

典型数据集：CMM-Math（以及 SCEMQA 的一部分）。

### 4.5 纯图片索引题：优先 `blank_open`，必要时 `drop_image_index`

特征：
- 问题本质是在选某个图/某个 figure index
- 若题目仍可转成可评测的开放问答目标，则保留并走 `blank_open`
- 仅当语义不可恢复、无法形成稳定开放目标时，才走 `drop_image_index`

## 5. 当前代码对齐的决策顺序（实现优先）

当前 `RewriteAgent.fallback_rewrite(...)` 的实际优先级可归纳为：

1. `choices` 为空：
	- 常规走 `keep_open`
	- 若是图像标签选择语义（`which picture/figure/diagram/...`）则走 `blank_open`
2. `choices` 非空且命中 pure image index：优先 `blank_open`
3. 命中复合答案（compound answer）：走 `split_open`
4. 其他多选题兜底：走 `blank_open`

补充：
- `drop_image_index` 仍是允许策略，并且 LLM 返回该策略时可被接受。
- 但当前 fallback 主路径并不主动产出 `drop_image_index`。

## 6. 代码对应关系

- 策略集合定义：`ALLOWED_REWRITE_STRATEGIES`
- fallback 主逻辑：`RewriteAgent.fallback_rewrite(...)`
- LLM 结果校验与回退：`RewriteAgent.rewrite(...)`

对应代码文件：
- [benchmark/src/pipeline_rewrite.py](benchmark/src/pipeline_rewrite.py)

## 7. 说明

本文档用于帮助当前分支在“prompt + 代码 + 已归档快照”之间保持一致；当可获得明确 ler 分支实现时，再做一次证据化对齐更新。
