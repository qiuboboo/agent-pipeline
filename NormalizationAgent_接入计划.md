# qjb 分支：NormalizationAgent 引入与使用计划

## 背景
当前 qjb 分支的样本规范化路径总体更保守，能较好保留 `Caption:` / supporting context，但也因此容易把 `Caption + Question` 整段一起留在 `normalized_question_text` 或 open rewrite 中，导致题面不够干净。

相比之下，ler 路线已经引入了 `NormalizationAgent`，可以通过 LLM 对 `normalized_question_text` 做更主动的规整，但也暴露出一个问题：如果约束不够清楚，模型会把关键 caption 误当作包装信息删掉。

因此，qjb 分支后续如果要引入这套 NormalizationAgent，不建议直接照搬，而应采用“受控接入”的方式。

---

## 目标
在 qjb 分支中引入/对齐 `NormalizationAgent` 能力时，实现以下目标：

1. 保持题面更干净、更统一。
2. 不丢失 caption、supporting context、图像说明等关键信息。
3. 对多模态样本维持稳定的 `requires_image` / `cleaning_path` 判断。
4. 让 normalization 结果可审计、可回退、可发现 context loss 风险。

---

## 当前观察
### qjb 当前优势
- 对 `Caption:` 更保守，信息不容易丢。
- 对 MSEarth 这类带 supporting text 的样本更安全。

### qjb 当前问题
- `normalized_question_text` 容易保留整段 `Caption + Question`。
- rewrite 结果可能直接继承这段文本，导致标注题面偏脏。

### ler 给出的经验教训
- 单纯让 LLM 做 normalization，如果 prompt 只说“删除包装说明/噪声”，容易把 caption 一起删掉。
- 因此 qjb 若接入 NormalizationAgent，必须把“保留 supporting context”写进显式规则里。

---

## 建议接入方式

### 方案原则：先并行、后替换
不要一上来就让 NormalizationAgent 全面替换 qjb 当前 normalization 路径。建议分三步：

#### 第 1 步：并行输出，不切流
对同一样本同时产出：
- `normalized_question_text_rule`
- `normalized_question_text_agent`
- `context_loss_risk`

先比较 agent 输出是否明显优于当前 rule 输出，而不是立即替换。

#### 第 2 步：增加保护规则
当满足以下任一条件时，不允许 agent 输出直接覆盖规则结果：
- `raw_question_text` 含 `Caption:`
- `raw_question_text` 含 `<image>` 且同时有自然语言说明块
- `reasoning_chain` / gold answer 明显依赖 supporting text
- agent 输出比 rule 输出短很多，且删掉了 `Caption:` / `Question:` 之前的文本块

此时：
- 保留 rule 版本，或
- 将 supporting context 单独拆出后再使用 agent 版本题面

#### 第 3 步：受控切换
当经过一轮样本验证后，再决定是否：
- 默认使用 `normalized_question_text_agent`
- 但对高风险样本保留 rule 版本或启用 fallback

---

## 建议的输出结构
如果 qjb 接入 NormalizationAgent，建议不要只保留一个 `normalized_question_text`，而是扩成：

```json
{
  "normalized_question_text": "主题面",
  "supporting_caption_text": "可选，支撑说明",
  "context_loss_risk": "low|medium|high",
  "normalization_source": "rule|agent|agent_with_guard"
}
```

这样可以把：
- 干净题面
- supporting context
- 风险评估
拆开管理。

---

## Prompt 设计要求
如果在 qjb 引入 NormalizationAgent，prompt 里必须明确补这些规则：

### 必须新增的约束
1. **不要删除承载答案证据的 caption / figure description / supporting text。**
2. 如果题目文本中同时包含 `Caption:` 和 `Question:`：
   - 可以提炼更干净的问题主体
   - 但必须保留 supporting caption，不能直接丢失
3. 如果无法判断 caption 是否关键，优先保留，而不是删除。
4. 若输出题面比原文短很多，必须检查是否发生 evidence loss。

### 不建议继续保留的模糊表述
像下面这种说法风险很高：
- “删除重复包装说明”
- “清理噪声前后缀”

因为模型很容易把 `Caption:` 误判成“包装说明”。

---

## 代码接入建议

### 1. 增加保护函数
建议增加类似：
- `detect_caption_context(raw_question_text)`
- `detect_context_loss(raw_question_text, normalized_question_text)`

例如：
- 原文含 `Caption:`，但归一化后不含且文本长度显著下降 -> `context_loss_risk = high`

### 2. agent 输出后加 guard
即使 agent 返回了 `normalized_question_text`，也不要立即信任。先做检查：
- 是否删除了 caption
- 是否删除了题目关键说明块
- 是否改变了图像依赖判断

若触发风险：
- 回退到 rule 输出
- 或拆分为 question + supporting caption

### 3. 记录审计字段
建议多记：
- `normalization_source`
- `normalization_guard_triggered`
- `context_loss_risk`
- `supporting_caption_preserved`

便于后续查问题。

---

## 试运行建议
正式切换前，建议在 qjb 做一轮小样本 AB 对比：

### 对比对象
- 纯规则 normalization
- agent normalization（带 guard）

### 抽样建议
至少覆盖：
- MSEarth Open Ended（caption-rich）
- EEE-Bench（Hint / Question 包装明显）
- EMMA-Physics（长文本 + 图像依赖）

### 重点观察指标
- `Caption:` 是否被误删
- `normalized_question_text` 是否更干净
- `requires_image` 是否稳定
- `clean_decision` / `alignment_status` 是否异常波动

---

## 推荐落地策略
当前最推荐的不是“让 qjb 直接照搬 ler 的 NormalizationAgent”，而是：

1. 在 qjb 中引入同类能力，但默认走 **agent + guard**
2. 对 caption-rich 样本显式保留 supporting context
3. 将题面清理与证据保留分成两个字段管理
4. 先小样本验证，再考虑替换当前主链路

---

## 一句话结论
qjb 可以用这套 NormalizationAgent，但**必须带保护栏使用**：

- 让 agent 负责“把题面弄干净”
- 让 guard 负责“别把 caption 和证据洗没了”
