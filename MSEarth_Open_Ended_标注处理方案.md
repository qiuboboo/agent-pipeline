# MSEarth Open Ended 标注处理方案

## 背景
在当前 `MSEarth/MSEarth_Open_Ended` 样本中，已确认部分题目存在以下情况：

1. 原始 `query` 中同时包含：
   - 图像占位符（如 `<image>`）
   - caption 文本
   - Question 文本
2. rewrite 阶段会将题面清洗成更短的开放题。
3. 但 reasoning chain / gold answer 有时仍然依赖 caption 中提供的关键信息。

这意味着：**如果标注阶段只看到清洗后的短问题，而看不到 caption/supporting context，就可能丢失关键证据。**

---

## 标注目标
对 MSEarth Open Ended 这类样本，标注阶段应同时保证：

- 题面简洁可读
- 证据来源可追溯
- 标注员不会因为上下文丢失而误判
- 后续 QA 能检查“答案是否确实由题面+支撑材料推出”

---

## 建议方案

### 方案核心：题面与支撑上下文分离保存
不要把 caption 直接粗暴并回 rewritten question，也不要在 rewrite 时直接丢弃。

建议在标注侧采用两层结构：

#### A. 主题面（annotation prompt question）
保留 rewrite 后的简洁开放题，例如：
- `Which historical periods contributed to the construction of Suoyang Ancient City?`

#### B. 支撑上下文（supporting context）
单独提供：
- 原始 caption
- 必要的图像说明
- 如有需要，保留 reasoning chain 作为审计字段，但默认不直接暴露给标注员作答案提示

这样做的好处是：
- 题面保持干净
- 证据不丢
- 可以区分“题目本身”和“支撑材料”

---

## 标注界面/样本建议字段
对于每条待标注样本，建议至少提供：

- `problem_id`
- `rewritten_question_text`
- `expected_answer`（仅 gold / 内部可见）
- `primary_image`
- `supporting_caption_text`（若存在）
- `has_reasoning_chain`
- `reasoning_chain`（内部审计字段，不建议默认前台展示）

其中：

### 标注员默认可见
- `rewritten_question_text`
- `primary_image`
- `supporting_caption_text`（如果答案依赖 caption）

### 质检/审计可见
- `reasoning_chain`
- 原始 query
- normalization / rewrite rationale

---

## 是否展示 reasoning_chain
### 建议：
**不要默认展示给一线标注员。**

原因：
- reasoning chain 容易变成“提示答案”
- 会污染人工独立判断
- 更适合作为 QA / 审计 / 纠纷复核材料

### 可以展示给谁
- 质检人员
- 错题复核人员
- 数据工程排障人员

---

## caption 处理规则建议

### 应保留 caption 的情况
若满足以下任一条件，标注输入中应保留 caption：

1. gold answer 明显来自 caption 文本，而非纯视觉内容
2. reasoning chain 明确引用 caption 作为关键证据
3. 删除 caption 后，题面会变得信息不足或歧义明显

### 可不展示 caption 的情况
若问题主要依赖：
- 图像显式标注
- 图形结构
- 图中对象识别
- 空间关系判断

且 caption 不提供关键新增信息，则 caption 可仅作为后台资产保存，不前台展示。

---

## QA 检查建议
建议为这类样本增加一个 QA 检查项：

### `context_loss_risk`
用于判断 rewrite 后是否因移除 caption / supporting text 导致信息损失。

可用简单规则先做首版：
- 如果 `reasoning_chain` 中显式出现 `caption`，则标记 `context_loss_risk = high`
- 如果 rewritten question 比 raw question 明显变短，且 raw question 包含 `Caption:`，则标记 `context_loss_risk = medium/high`

对应处理：
- `high`：标注时必须展示 supporting caption
- `medium`：建议展示 supporting caption
- `low`：caption 可隐藏

---

## 落地建议

### 短期
1. 不修改 rewrite 主逻辑，先在标注侧补 supporting caption 展示规则
2. 对 `has_reasoning_chain = true` 的样本做抽样复核
3. 增加 `context_loss_risk` 检查

### 中期
1. 在资产层单独拆出 `caption_text` 字段/资产
2. 区分：
   - `question_text`
   - `caption_text`
   - `image_annotation_text`
3. 让标注系统按规则决定展示哪些 supporting fields

### 长期
1. 将 reasoning chain 拆为更结构化的 evidence nodes
2. 在 QA 阶段校验“答案证据是否来自图像 / caption / 两者结合”
3. 对 MSEarth 这类数据集建立更细的标注策略模板

---

## 结论
对于 MSEarth Open Ended，推荐采用：

- **简洁 rewritten question 作为主题面**
- **caption 作为可控展示的 supporting context**
- **reasoning_chain 作为后台审计字段，而非默认标注输入**

这样既不会把题面弄得太脏，也不会把关键证据洗掉。
