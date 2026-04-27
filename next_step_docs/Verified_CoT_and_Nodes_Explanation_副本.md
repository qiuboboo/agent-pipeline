# 汇报文档：Verified CoT 与 r_nodes（中间决策点）机制深度解析

**汇报目标：**
本报告旨在系统性地梳理并展示当前 Pipeline 中关于 **“求解与验证视角 (Verified CoT)”** 阶段的核心设计。通过真实的运行日志（以 `prob_016bc73dfd9342abef609367` 题目为例），详尽汇报 Answer Repair（答案修复）、多轮逻辑校验（Critic/Polish）、原子断言（Claims）抽取以及最终标准中间节点（r_nodes）的具体生成机制。从而展现系统是如何通过“四层漏斗”极致地保证模型推导中间过程的真实性。

相关的代码归档备份存放在：[`benchmarkallinone/pipeline2/verified_cot_code_backup/`](../pipeline2/verified_cot_code_backup/) 文件夹下。

---

## 1. 核心架构与业务工作流

Verified CoT 流程的核心是一个基于状态机的 **LangGraph** 工作流，其主入口为 [`verified_cot_pipeline.py`](../pipeline2/verified_cot_code_backup/verified_cot_pipeline.py)。其主要逻辑为：遍历 `ready` 阶段下发的每一种生成方法 (Method Draft)，将其作为解题指引，生成对应的思维链 (CoT) 并开展极其严苛的验证过滤。

状态流转的六大核心节点如下：
1. **Solver（求解器）**: 基于原题和方法草稿，输出模型最初的解答及其推导步骤 (`solver_answer` 和 `solver_cot`)。
2. **Answer Check / Repair（答案核对与修复）**: 核对求解步骤与专家答案。如果不一致，启动修复引擎。
3. **Verify/Polish Loop（验证与润色闭环）**: 长达 3 轮的批评、润色机制（消除模型幻觉、确保图文完全对齐）。
4. **PTK Foundation Builder（基石抽取）**: 抽取客观事实，包含 P视知觉 (Perception)、T文本事实 (Text)、K知识点 (Knowledge)。
5. **Claim Extraction（原子断言抽取）**: 抽取出多步推导链条，形成具备严谨依赖关系的原子图谱。
6. **Node Induction（节点归纳）**: 归一化原子图谱，生成规范化的 `r_nodes`（中间节点）图。

---

## 2. 答案修复引擎 (Answer Repair) 机制与实例展示

### 2.1 机制说明
由于 Solver 生成的 CoT 存在算错或发散的情况，当 Solver 答案与标准答案**不匹配** (`is_answer_match: false`) 时，触发 Answer Repair Agent。
其核心任务并不是**无中生有式地生造过程**，而是：顺着专家的正确答案，定位并修改原始推导中算错或推错的步骤，**使得最终推导自然通向正确的结论**，并尽可能保留原步骤中正确的逻辑。

如果 Solver 一次性解答正确 (`is_answer_match: true`)，则该路径将直接跳过修复，进入严格的逻辑质检阶段。

### 2.2 实例追踪：跳过答案修复后的“逻辑质检”
以备份中的题目 `prob_016bc73dfd9342abef609367` 为例。该题中，模型计算出的角度 `65` 与标准答案完全一致，因此跳过了 Answer Repair。**但这并不意味该步骤的推导是完美的。**
实际上，即使答案正确，系统仍对其推导过程进行了 **3 轮打磨 (3 rounds of Polish)** 才予以放行。

#### 第 0 轮体检 (Verify 0)：发现“幻觉跃进”
在初次生成的 CoT 中，模型跳步回答。系统中的 `CoT Verification Critic` 给出了**评判意见 (`critic_suggestions`)**：
> "Revise the trace to actually execute the local angle-chase at X using image-grounded facts. Specifically: (1) identify the rays XV and XW from the diagram, (2) name the adjacent marked angle(s) at X with their numeric measures, (3) state whether those angles and ∠VXW form a straight angle or full partition around X, and (4) perform the explicit subtraction/addition that yields 65. Do not reference the 'authoritative provided answer signal' or any external answer source. Every numeric and structural claim should be directly attributable to the diagram."
> (修改这部分推导，使其真实地利用基于图像的事实在顶点X处进行局部角度推导。具体来说：(1) 从图中识别出射线 XV 和 XW，(2) 明确指出在X点处标记的邻角的数值，(3) 说明这些角以及 ∠VXW 是否在X点处形成了一个平角或者完整的分割，(4) 进行显式的加减运算得出65。不要引用“提供的权威答案信号”或者任意的外部答案来源。每一个数值和结构的断言都应该直接归因于这幅图。)

#### 第 1-2 轮：修复与再体检
系统切入 `_polish_round`。在尝试修复后，第 2 轮审查时，Critic 再次指出致命问题 (`major_failures`)：
> "The key image-dependent claims are ungrounded in the provided multimodal context: the trace asserts a straight line through X involving ray XV and an adjacent 115° angle, but those facts are not extractable from the authoritative grounding data supplied here."
> (关键的基于图像的断言在提供的多模态上下文中并没有事实根据：推导中断言了经过X的一条直线包含射线XV以及相邻的115°角，但是这些事实无法从这里提供的权威参考数据中提取出来。)

#### 第 3 轮：最终通过 (Verify 3)
经过针对性地指导与打磨，模型给出极其严谨的推导：
> "Use the local angle-chase at vertex X. In the diagram, ray XV lies on a straight line through X, so there is an opposite ray to XV at X. The marked 115° angle at X is the angle between ray XW and that opposite ray. Therefore, the 115° angle and ∠VXW are adjacent angles forming a linear pair, so they sum to 180°. Hence,\n\nm∠VXW = 180° - 115° = 65°."
> (在顶点 X 处使用局部角度推导策略。在图中，射线 XV 位于穿过 X 的一直线上，因此在 X 处有一条与 XV 相反的射线。在 X 处标记的 115° 角是射线 XW 与那条相反射线之间的角。因此，115° 的角和 ∠VXW 是形成线性对的相邻角，它们的和为 180°。所以，\n\nm∠VXW = 180° - 115° = 65°。)

由于步步严丝合缝，Critic 最终给出了 `verify_pass: true`，并在总结 (`CoT_qualify_3`) 中写道：
> "The trace is consistent with the standard answer and follows the intended local angle-chase method at X. For maximal rigor, it could explicitly state that XV and the referenced opposite ray are collinear, and that the marked 115° angle is adjacent to ∠VXW, so the two form a linear pair summing to 180°."
> (该推导与标准答案一致，且遵循了预期的在X处的局部角度推导方法。为确保最大严谨性，它可以明确说明XV及其引用的相反射线共线，且标记的115°角与∠VXW相邻，由此这两个角组成了一个和为180°的线性对。)

到此，标记为最终的 `is_final_CoT_qualified: true` 的可信过程就确定了下来。

---

## 3. Claim Extraction：原子级声明的切分与依赖结构

获得打磨通过的 `CoT_final` 之后，系统并没有停止，而是将这段连贯的自然语言“解构”为了一个个具有逻辑层级的 **Claim（原子断言）**。通过分析 JSON 中的 `claim_sequences`，上述完美的 CoT 被提取为了 **7 条具备血缘依赖关系 (`depends_on`) 的 Claims**：

*   **c1 (视觉感知发现)**: `"In the diagram, ray XV lies on a straight line through X."` (在图中，射线 XV 位于穿过 X 的一直线上。) —— 类型：`perception`
*   **c2 (初步逻辑推导)**: `"Because XV lies on a straight line through X, there is an opposite ray to XV at X."` (因为 XV 位于穿过 X 的一直线上，所以在 X 处有一条相对于 XV 的相反射线。) —— 类型：`derivation`，依赖：`["c1"]`
*   **c3 (后续视觉感知发现)**: `"The marked 115° angle at X is the angle between ray XW and the ray opposite to XV."` (在 X 处被标记为 115° 的角是射线 XW 和与 XV 相反的射线之间的角。) —— 类型：`perception`，依赖：`["c2"]`
*   **c4 (基于感知的组合推导)**: `"The 115° angle and ∠VXW are adjacent angles whose noncommon sides are opposite rays, so they form a linear pair."` (115° 的角和 ∠VXW 的非公共边是相反的射线，所以它们构成了一个线性对。) —— 类型：`derivation`，依赖：`["c2", "c3"]`
*   **c5 (知识点调用)**: `"Angles in a linear pair sum to 180°."` (线性对中的角和为 180°。) —— 类型：`knowledge_call`，依赖：`["c4"]`（*重点：触发了底层知识调用，没有此步骤后续无法减法*）
*   **c6 (算术计算)**: `"m∠VXW = 180° - 115° = 65°."` (m∠VXW = 180° - 115° = 65°。) —— 类型：`calculation`，依赖：`["c4", "c5"]`
*   **c7 (最终落定结论)**: `"m∠VXW = 65°."` (m∠VXW = 65°。) —— 类型：`final_answer`，依赖：`["c6"]`

这种通过有向图对每步逻辑（甚至每步的起因：视觉/常识/计算）进行溯源的设计，使得哪怕算错一步，系统都能准确抓取错误节点。

---

## 4. 中间节点提取与 “四层漏斗”

以上展示的过程，实际上反映了 Pipeline 系统通过“四层漏斗”最终提取出具备规范性质的**最终中间节点 (`r_nodes`)**。

### 漏斗第一、二、三层：
*   **第一层：Verify/Polish**（筛除模型幻觉）
*   **第二层：PTK 事实打桩**（剥离图像、文本和知识本身作为基础起点）
*   **第三层：Claim Extraction**（将推导切割为严格的原子判断）

### 漏斗第四层：Node Induction (生成归一化 `r_nodes`)
哪怕同一道题采取不同解法，或表述方法不一，这些 Claims 都需要被“熔炼合并”为系统中全局统一的 Canonical Reasoning Nodes (`r_nodes`)，充当中间奖励机制或截断的标准检查点。

*   **例如 c4**（线性对论证）：被归一化为了系统里对应的节点 `r_2bbdc70152f5ad1be1d272ea`：
    标准的教条说法 (`canonical_claim`)：`"∠VXW and the 115° angle form a linear pair."` (∠VXW 与 115° 角形成了一个线性对。)
*   **例如 c6**（算术步骤）：被归一化为了系统里的 `r_fdcb79431ef21b17dd95bdd2`：
    标准的计算结论 (`canonical_claim`)：`"m∠VXW = 180° - 115° = 65°."` (m∠VXW = 180° - 115° = 65°。)

最后，系统在 `evidence_bindings` 阶段，为这些孤立的节点寻找到了最坚实的地基证据支撑。
例如 `r_e5513a5ec16a73cf79138c26`：
被证实调用了底层知识：`"Angles in a linear pair sum to 180°."` (线性对中的角和为 180°。)，系统为其打上了 `"support_strength": "HIGH"`，并在 `binding_rationale` 指明：
> "This node is a direct invocation of the Linear Pair Rule, which is exactly captured by knowledge atom k2."
> (该节点直接调用了线性对规则，而该规则恰好被知识点k2所捕获。)

## 总结
我们构建了一套以“求对”为起点，以“求实”为终点的闭环机制。从 `Ready` 环节由 `Solver` 下手起，如果推导过程存在疏漏，会启动 `Answer Repair` 进行缝补修正；同时，长达多轮的 `Critic/Polish` 机制极其严苛地淘汰各种幻觉和不严谨问题。最终的过程被输入进行 `PTK` 证据抽离，切分为有先后依赖的 `Claims` 链条，并归一化聚合为 `r_nodes` 节点图谱。每一步的高标准严谨设计确保了产出的中间奖励过程不仅能在逻辑上绝对自洽，还能 100% 用于复杂的推导追踪甚至 RL 评估。这种架构保障了产出数据的质量达到非常严密的专家级水平。