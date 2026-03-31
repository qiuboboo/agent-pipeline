# ler-reasoning-chain-msearth：MSEarth 样本 caption 消失原因定位

## 结论
在当前 `ler-reasoning-chain-msearth` 分支中，MSEarth 第一个样本里 `Caption:` 的消失，**主要发生在 normalization 阶段，而不是 rewrite 阶段。**

更具体地说：
- 原始 `raw_question_text` 中有 `Caption:`
- 到 `problem_main_record.normalized_question_text` 时，caption 已经消失
- 因此 rewrite 阶段即使继续 `keep_open`，也只能基于已经被裁剪后的问题文本继续往下走

---

## 直接证据

### 1. 原始输入中有 caption
样本 `prob_d15cedaaf690d60a9e4d4150` 的原始题面为：

```text
<image>Caption:
The site of Suoyang Ancient City showing ( a ) the inner-city walls (photo credit: Dunhuang Academy) and ( ) the Ta’er temple (photo: author’s own).
Question:
Which historical periods contributed to the construction of Suoyang Ancient City?
```

### 2. 在 `problem_main_record` 中 caption 已消失
该样本的 `problem_main_record.normalized_question_text` 为：

```text
Which historical periods contributed to the construction of Suoyang Ancient City?
```

这说明 caption 的丢失发生在 rewrite 之前。

### 3. 该样本中的 rewrite 报告并不是证据来源
当前样本文件中 `rewrite_report` 未体现为导致 caption 删除的直接证据；且从代码实现看，`keep_open` 分支主要是保留输入问题文本。

因此不能把锅甩给 rewrite。

---

## 代码层面的原因分析

### 1. rewrite fallback 本身不会主动删除 caption
`RewriteAgent.fallback_rewrite(...)` 的关键逻辑是：

```python
question_only, _ = self.normalizer.split_question_and_choices(question_text)
question_only = self.normalizer.strip_hint(question_only)
```

其中：
- `split_question_and_choices` 只处理 `Choices:`
- `strip_hint` 只删除 `Hint:` / `Please answer ...`

它并没有写“删除 `Caption:`”的显式规则。

### 2. caption 消失发生在 `NormalizationAgent`
`NormalizationAgent.process(...)` 中，如果 LLM 开启：

```python
llm_result = self.call_json(...)
normalized_question_text = llm_result.get("normalized_question_text") or fallback["normalized_question_text"]
```

也就是说：
- fallback 本来是规则归一化结果
- 但只要 LLM 返回了 `normalized_question_text`
- 最终就优先采用 LLM 的结果

因此，caption 被删，更像是 **LLM normalization 输出把它裁掉了。**

### 3. Prompt 中存在容易诱发误删的模糊指令
当前 `prompts/cleaning/normalization_agent.md` 中有一条：

> 删除明显噪声标记，如 `<image>`、重复包装说明、无语义考试头。

这条规则的问题在于：
- 对模型而言，`Caption:` 可能被误认为“包装说明”
- 尤其当 `Question:` 后面有一个看起来更像“核心问题”的句子时
- 模型会倾向于只保留问题句

因此，**caption 被删的直接诱因，很可能是 NormalizationAgent 的 LLM 输出 + prompt 中“删除包装说明”的模糊表述。**

---

## 为什么这是个问题
第一个样本的 reasoning chain 明确写到：

```text
The caption specifically attributes its construction to the Han and Tang dynasties.
```

也就是说：
- gold answer 的关键证据来自 caption
- 但 normalization 后题面把 caption 删除了

于是会出现一个链路不一致问题：

- 题面更干净了
- 但支撑答案的证据更少了

如果后续标注或 QA 只看到简化后的题面，可能无法判断答案依据是否充分。

---

## 根因归纳
一句话概括：

**不是 rewrite 把 caption 删除了，而是 ler 的 LLM NormalizationAgent 把 caption 当成可清洗掉的包装信息删掉了。**

---

## 建议修复方向

### 方向 A：改 prompt
在 `normalization_agent.md` 中明确增加：
- 不要删除承载答案证据的 caption / figure description / supporting context
- 若原文中同时存在 `Caption:` 和 `Question:`，默认保留 caption，或拆分为 supporting context

### 方向 B：加代码 guard
在接收 LLM normalization 结果后增加检查：
- 原文含 `Caption:`
- 输出不含 `Caption:`
- 且长度显著缩短

则：
- 标记 `context_loss_risk = high`
- 回退到 fallback
- 或把 caption 单独保留为 supporting 字段

### 方向 C：结构化拆分
不要把是否保留 caption 完全交给 `normalized_question_text` 单字段处理。建议拆分为：
- `normalized_question_text`
- `supporting_caption_text`
- `context_loss_risk`

---

## 一句话结论
当前 `ler-reasoning-chain-msearth` 分支中，MSEarth 样本 caption 消失的根因是：

**LLM 驱动的 NormalizationAgent 在 prompt 引导下，把 `Caption:` 误当成可删除的包装信息，从而在 normalization 阶段提前裁掉了关键 supporting context。**
