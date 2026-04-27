# 汇报文档：Verified CoT 与 r_nodes（中间节点）保证正确的机制解析

**汇报目标：**
本报告旨在系统性梳理当前 Pipeline 中关于 **“求解与验证视角 (Verified CoT)”** 阶段的核心设计，并重点说明一个新的强约束：**凡是图像依赖题，所有参与决策的 agent 都必须真正看到图片，而且请求必须实际走 multimodal；如果做不到，就直接失败，不能退化成 text-only 推理。**

本文使用最新一次 live smoke 运行中的真实样例 `prob_live_smoke_mm_001` 进行说明，对应 batch 为 `live_smoke_20260412T120600Z_all_mm`。

相关的历史备份代码仍存放在：[`benchmarkallinone/pipeline2/verified_cot_code_backup/`](../pipeline2/verified_cot_code_backup/) 文件夹下。

---

## 1. 核心架构与业务工作流

Verified CoT 流程的核心是一个基于状态机的 **LangGraph** 工作流，主入口为 `pipeline2/pipeline.py`。整体逻辑是：从 `ready` 阶段读取题目，为每道题规划方法、生成 CoT、进行答案核对、做多轮质检，再把通过质检的推理切分成可验证的 claims，最后归纳成标准中间节点 `r_nodes`。

状态流转的核心节点如下：

0. **Method Planner（方法规划器）**：在正式求解前，为当前题目规划一条或多条宏观解题策略草稿（Method Draft）。
1. **Solver（求解器）**：严格依据 Method Draft 生成最初的 CoT 与答案。
2. **Answer Check / Repair（答案核对与修复）**：如果答案与标准答案不一致，则进入修复。
3. **Verify / Polish Loop（验证与润色闭环）**：Critic 对 CoT 做严格图文一致性校验，必要时进入 Polish，再重复验证。
4. **PTK Foundation Builder（基石抽取）**：抽取 P 视觉事实、T 文本事实、K 知识点。
5. **Claim Extraction（原子断言抽取）**：把通过验证的 CoT 切分为具备依赖关系的 claims。
6. **Node Induction（节点归纳）**：把 claims 归并成标准化的 `r_nodes`。

### 1.1 当前新增的硬约束：图题必须真看图

现在的设计不是“有图就尽量传图”，而是：

- 只要题目 `requires_image = true`，相关 agent 就必须收到真实图片；
- 请求必须实际走 multimodal；
- 如果图片打不开、没传上去，或最终接口返回的 `_llm_request_mode` 不是 `multimodal`，则该 agent 直接报错；
- 不允许静默回退到纯文本推理。

### 1.2 当前纳入“必须看图”约束的决策型 agent

对于图像依赖题，目前已经统一要求以下决策链路必须真看图：

- Method Planner
- Solver
- Answer Equivalence Judge
- Answer Repair
- CoT Verify（Critic）
- CoT Polish
- Perception Extraction
- Text Condition
- Knowledge Librarian
- Claim Extraction
- Node Induction
- Solution Grouper
- Evidence Binder
- Trace Mapper
- Novelty Detector

也就是说，现在不只是 `Solver` 和 `Critic`，而是**整条参与决策的主链路**都被纳入了图像可见性约束。

---

## 2. 新运行实例：`Solver` 与 `Critic` 都真正看到了图片

本节使用最新 live smoke 运行的题目 `prob_live_smoke_mm_001` 说明当前机制已经按要求生效。

### 2.1 题目概况

该题是一个极简 OCR 型图题：

- **题目文本**：`Read the digit shown in the image and answer with that digit only.`
- **标准答案**：`7`
- **题目属性**：`requires_image = true`

它非常适合做“模型到底有没有真的看到图片”的冒烟验证，因为如果不看图，就不应该稳定给出可信的视觉型 CoT。

### 2.2 Solver 的真实输出

本次运行中，`Solver` 给出的 `CoT_raw` 为：

> "I inspected the attached image directly. It shows a single black digit on a white background. The numeral has a top horizontal stroke and a descending diagonal/right-leaning stem, which matches the digit 7. Following the instruction to answer with that digit only, the result is 7."

这段 CoT 的关键特征是：

1. 明确声明自己直接检查了附带图片；
2. 给出了具体视觉属性，而不是泛泛而谈；
3. 视觉描述与最终答案之间存在明确桥接；
4. 没有只复述结构化摘要，而是按“黑色数字 + 白底 + 7 的笔画形状”来组织推理。

### 2.3 Solver 真正看图的证据

本次运行对应的 method 快照中，`solver_metadata` 记录了：

- `_llm_request_mode = "multimodal"`
- `_llm_endpoint_name = "primary"`

这意味着 `Solver` 不是在纯文本模式下生成 CoT，而是确实通过多模态请求完成推理。

### 2.4 Critic 的真实输出

本次运行中，`Critic`（即 `CoTVerify`）给出的 `critic_suggestions` 为：

> "The trace is sound. Its visual claims are directly supported by the image: there is a single black digit on a white background, and its shape matches a 7. The conclusion is consistent with both the question and the standard answer, and the reasoning follows the assigned direct visual recognition method. No revision is needed."

这段 `critic_suggestions` 的意义非常关键：

1. 它没有只说“答案对了”；
2. 它明确检查了视觉 claim 是否被图片直接支持；
3. 它明确指出“单个黑色数字、白色背景、形状匹配 7”这些都是图像支持的事实；
4. 它确认当前推理路径与方法草稿一致，因此允许直接通过。

### 2.5 Critic 真正看图的证据

在同一份 method 快照中的 `verify_reports[0]` 里，已经额外记录：

- `llm_request_mode = "multimodal"`
- `llm_endpoint_name = "primary"`
- `llm_elapsed_seconds = 15.534`

同时该轮验证结果为：

- `verify_pass = true`
- `grounding_score = 0.98`
- `method_fidelity_score = 1.0`
- `extractability_score = 1.0`

这说明现在不只是 `Solver` 看图，**质检员 Critic 也是真正带图审查**，而不是只读 CoT 文本和结构化摘要。

### 2.6 为什么这能证明“当前结果是正确的”

对于这个图题，正确性不只是“最终答案 = 7”，还必须满足以下三件事同时成立：

1. `Solver` 的请求模式是 `multimodal`；
2. `Critic` 的请求模式也是 `multimodal`；
3. CoT 与 critic_suggestions 都显式围绕图片中的真实视觉特征展开。

本次新运行已经同时满足这三点，因此可以判断：**现在的图题 CoT 生成与质检链路，已经真正满足“必须结合图片推理”的设计目标。**

---

## 3. 为什么现在不能再“假装看图”

旧风险在于：模型可能只读结构化视觉摘要，就写出“我看到了图片中的……”这类貌似合理的 CoT。但现在这条路被明确堵住了。

当前机制的关键约束如下：

1. **图题必须有可加载图片**：如果 `requires_image = true`，但图片为空或打不开，直接报错。
2. **图题请求必须是 multimodal**：如果最终 `_llm_request_mode` 不是 `multimodal`，直接报错。
3. **prompt 明确要求直接查看附件图片**：不是只允许参考上游摘要，而是要求视觉 claim 必须直接落在图像上。
4. **验证链路也必须看图**：即使 `Solver` 给出了 CoT，后续 `Critic`、`Polish` 等也必须带图审查。

因此，现在系统不是“鼓励看图”，而是“**不看图就不允许继续**”。

---

## 4. Claim Extraction：新样例中的原子级断言切分

在本次 live smoke 样例中，通过验证的 `CoT_final` 会继续被切分成具备依赖关系的 claims。当前样例中可观察到如下 6 条 claims：

- **c1（视觉感知）**：`The image shows a single black symbol on a white background.`
- **c2（视觉感知）**：`The symbol has a straight horizontal top bar and a descending slanted stroke.`
- **c3（知识调用）**：`A numeral with a straight horizontal top bar and a descending slanted stroke is the digit 7.`
- **c4（推导）**：`The symbol in the image is the digit 7.`
- **c5（文本条件）**：`The prompt requires answering with the digit only.`
- **c6（最终答案）**：`7`

其依赖关系非常清晰：

- `c4` 依赖于视觉观察 `c2` 与知识调用 `c3`；
- `c6` 依赖于图像识别结果 `c4` 与文本输出要求 `c5`。

这意味着最终答案不再是“直接拍脑袋得出 7”，而是明确经历了：

**看图 → 识别笔画形状 → 调用数字识别知识 → 得到 7 → 按文本要求只输出该数字**。

---

## 5. Node Induction：`r_nodes` 如何承接这条推理链

在当前样例中，上述 claims 进一步被归纳为标准化的 `r_nodes`。其中几个关键节点如下：

- **视觉节点**：`The image contains a single black symbol on a white background.`
- **视觉节点**：`The symbol has a horizontal top bar and a descending diagonal stroke.`
- **知识节点**：`A numeral with a horizontal top bar and a descending diagonal stroke is the digit 7.`
- **推导节点**：`The depicted symbol is the digit 7.`
- **文本条件节点**：`The response must contain only the digit, with no extra text.`
- **最终答案节点**：`Return 7 as the entire answer.`

这些节点共同组成了一条非常短但非常干净的解题链：

**视觉识别节点 → 数字知识节点 → 识别结论节点 → 输出约束节点 → 最终答案节点**

对于这种极简图题，这条路径已经足够说明：`r_nodes` 并不是简单复述答案，而是在保留“看图—识别—作答”这一中间推理结构。

---

## 6. 本次运行的额外统计信号

本次 live smoke 运行结束后，`usage_summary.json` 中记录：

- `multimodal_request_count = 12`
- `text_request_count = 4`

这说明当前整条图题处理链路里，多模态调用已经占据主导，而不是像旧版本那样主要落在 text-only 模式。

需要注意的是，不是所有请求都必须是多模态：

- 某些纯文本性质的步骤在逻辑上可以保留 text；
- 但只要该步骤属于图题上的关键决策链路，并且需要判断视觉事实，就必须真正带图。

当前新设计已经把这一点落实为明确的工程约束，而不是口头约定。

---

## 7. 总结

本次最新运行说明，当前 Pipeline 已经从“图题尽量带图”升级为“**图题必须带图，而且必须实际走多模态请求**”的严格模式。

以 `prob_live_smoke_mm_001` 为例：

- `Solver` 给出的 CoT 明确来自对附件图片的直接观察；
- `Solver` 的 `_llm_request_mode` 明确记录为 `multimodal`；
- `Critic` 的 `critic_suggestions` 明确围绕图像中的可见事实展开；
- `Critic` 的验证记录里同样明确写入了 `llm_request_mode = "multimodal"`；
- 最终生成的 claims 与 `r_nodes` 也保持了“视觉事实 → 知识识别 → 最终作答”的完整结构。

因此，现在的 Verified CoT 机制已经满足你的核心设计目标：

> **所有参与决策的关键 agent，在图像依赖题上都必须真正看到图片；如果看不到，就不是降级继续推理，而是直接报错阻断。**

这使得最终产出的 CoT、claims 和 `r_nodes` 不仅答案正确，而且其中的中间过程也真正具备图像 grounding，可用于后续更严格的评测、回流和中间奖励建模。