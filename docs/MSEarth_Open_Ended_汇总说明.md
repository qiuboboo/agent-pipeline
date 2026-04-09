# MSEarth Open Ended 汇总说明

## 1. 背景
当前在 `MSEarth/MSEarth_Open_Ended` 上的观察表明，这类样本通常同时包含：

- 图像
- 问题文本
- caption
- answer
- reasoning_chain

其中不少样本的答案证据并不只来自图像本身，而是来自：

- caption
- 图像 + caption 联合
- reasoning_chain 中引用的 supporting context

因此，MSEarth 不是“只有题和图”的普通 VQA 数据，而是**带 supporting context 的多模态问答数据**。

---

## 2. 目前确认的关键现象

### 2.1 rewrite 后题面会变短
在当前链路里，rewrite 后的开放题通常会变成一个较短的问题句，例如：

- `Which historical periods contributed to the construction of Suoyang Ancient City?`

这会让题面更简洁，但如果 supporting context 没有同步保留，就会带来证据丢失风险。

### 2.2 reasoning_chain 可能仍然依赖 caption
以第一个样本为例：

- 原始 query 含有 `<image>Caption: ... Question: ...`
- reasoning chain 明确写：
  - `The caption specifically attributes its construction to the Han and Tang dynasties.`

这说明：
**gold answer 的关键依据之一来自 caption。**

### 2.3 当前产物中 caption 可能消失
已确认在当前 `ler-reasoning-chain-msearth` 分支中，部分样本会出现：

- 原始 query 中有 caption
- normalized question 中 caption 消失
- rewrite 后的问题文本中也不再保留 caption

这会导致：
- 题面更干净
- 但答案依据更弱
- 下游标注/QA 可能看不到关键 supporting context

---

## 3. caption 消失的原因定位

## 结论
当前 `MSEarth Open Ended` 中 caption 的消失，**主要发生在 normalization 阶段，而不是 rewrite 阶段。**

### 直接证据

#### 3.1 原始输入中有 caption
例如样本 `prob_d15cedaaf690d60a9e4d4150` 的原始题面为：

```text
<image>Caption:
The site of Suoyang Ancient City showing ( a ) the inner-city walls ...
Question:
Which historical periods contributed to the construction of Suoyang Ancient City?
```

#### 3.2 normalized question 中 caption 已消失
在当前产物里，该样本的 `normalized_question_text` 变成：

```text
Which historical periods contributed to the construction of Suoyang Ancient City?
```

这说明 caption 在 rewrite 之前就已经没了。

#### 3.3 rewrite 并不是主要根因
当前 rewrite 对这类样本大多采用：

- `strategy = keep_open`

也就是说 rewrite 更多是在接收“已经变短的 normalized question”，而不是主动删除 caption。

---

## 4. 根因分析

### 4.1 rewrite fallback 没有显式删除 caption
从代码看，rewrite fallback 主要做的是：

- 拆 question / choices
- 去掉 hint
- 保留开放题本身

没有明确写“删除 `Caption:`”的规则。

### 4.2 caption 更像是被 NormalizationAgent 裁掉了
当前 normalization 在开启 LLM 时，会优先采用 LLM 返回的：

- `normalized_question_text`

因此只要模型把 `Caption:` 视为“包装信息”或“可以省掉的上下文”，最终题面里就会失去 caption。

### 4.3 prompt 中存在误删诱因
目前 normalization prompt 中有类似：

- 删除明显噪声标记
- 删除重复包装说明
- 删除无语义考试头

对模型来说，`Caption:` 很可能被误判成：
- 包装说明
- 附加文本
- 非核心问题内容

于是被清洗掉。

---

## 5. 当前主要问题汇总

### 5.1 MSEarth Open Ended 样本改写后可能丢失关键 caption 信息
#### 风险
如果下游只消费改写后的短问题，而没有同步保留 caption：

- 题目支撑信息不足
- 答案证据丢失
- 样本 grounding 变弱

#### 当前观察
当前资产记录里通常有：
- `question_text_source`
- `question_text_normalized`
- `primary_image`

但缺少结构化拆出的：
- `caption_text`
- `image_annotation`
- `ocr_text`

---

### 5.2 当前 rewrite 对已开放题样本偏保守
#### 现象
这轮 MSEarth Open Ended 样本大量是：

- `strategy = keep_open`
- `rationale = Question is already open-ended.`

#### 风险
- 虽然不容易误改
- 但对“题面本来就不够完整”的样本提升有限
- 容易留下悬空问题句

---

### 5.3 source_problem_id 当前使用的是行号，不是真实 question_id
#### 现象
当前很多记录里的 `source_problem_id` 是：
- `0`
- `1`
- `2`

但原始数据集实际上提供了更好的字段：
- `question_id`（如 `ON019244`）

#### 风险
- 不利于回源
- 不利于人工排查
- 不方便和数据集官方样本对齐

---

### 5.4 reasoning_chain 已透传，但下游是否真正消费仍待确认
#### 已确认
当前已经能透传：
- `has_reasoning_chain`
- `reasoning_chain`

#### 仍需确认
- Annotation 是否读取
- QA 是否读取
- 发布链路是否读取
- 是否需要拆成更结构化的 evidence nodes

---

## 6. 标注处理建议

## 核心建议
**题面与支撑上下文分离保存，而不是二选一。**

### A. 主题面
保留 rewrite 后的简洁开放题，例如：
- `Which historical periods contributed to the construction of Suoyang Ancient City?`

### B. 支撑上下文
单独提供：
- 原始 caption
- 必要的图像说明
- reasoning_chain 作为后台审计字段

这样做的好处：
- 题面保持干净
- supporting evidence 不丢
- 标注时可控展示
- QA 时可回溯

---

## 7. 标注字段建议
对于每条 MSEarth Open Ended 样本，建议至少保留：

- `problem_id`
- `source_problem_id`
- `question_id`（如有）
- `rewritten_question_text`
- `primary_image`
- `supporting_caption_text`
- `has_reasoning_chain`
- `reasoning_chain`
- `expected_answer`（内部可见）

### 标注员默认可见
- `rewritten_question_text`
- `primary_image`
- `supporting_caption_text`（当答案依赖 caption 时）

### QA / 审计可见
- `reasoning_chain`
- 原始 query
- normalization / rewrite 相关记录

---

## 8. reasoning_chain 是否应展示给标注员
### 建议
**不要默认展示给一线标注员。**

原因：
- reasoning_chain 容易变成答案提示
- 会污染独立标注判断
- 更适合作为后台审计字段

### 更适合给谁看
- QA 人员
- 复核人员
- 数据工程排障人员

---

## 9. caption 的处理规则建议

### 应保留 caption 的情况
若满足以下任一条件，应在标注输入中展示或保留 supporting caption：

1. gold answer 明显来自 caption
2. reasoning chain 明确引用 caption
3. 删除 caption 后，题面会变得信息不足或歧义明显

### 可隐藏 caption 的情况
若问题主要依赖：
- 图像显式标注
- 图形结构
- 图中对象识别
- 空间关系判断

且 caption 不提供关键新增信息，则 caption 可仅在后台保存。

---

## 10. 建议增加的 QA 检查项
建议新增：

### `context_loss_risk`
用于判断 rewrite / normalization 后是否丢失关键 supporting context。

### 首版简单规则
- 如果 `reasoning_chain` 中显式出现 `caption`，则标记 `context_loss_risk = high`
- 如果 raw query 包含 `Caption:`，但 normalized/rewritten question 不再包含，则标记 `context_loss_risk = high`
- 如果 raw 比 rewritten 明显长很多，且存在 supporting context，被删减后答案证据变弱，则标记 `medium/high`

### 对应处理
- `high`：标注时必须展示 supporting caption
- `medium`：建议展示 supporting caption
- `low`：caption 可隐藏

---

## 11. 落地建议

### 短期
1. 不先动 rewrite 主逻辑
2. 先在标注侧补 `supporting_caption_text` 展示规则
3. 增加 `context_loss_risk` 检查
4. 优先使用真实 `question_id` 作为数据源标识

### 中期
1. 在资产层单独拆出 `caption_text`
2. 明确区分：
   - `question_text`
   - `caption_text`
   - `image_annotation_text`
3. 标注系统按规则决定展示哪些 supporting fields

### 长期
1. 将 reasoning_chain 拆成结构化 evidence nodes
2. QA 阶段校验答案证据来自：
   - 图像
   - caption
   - 图像+caption
3. 为 MSEarth 这类数据集建立专门的标注策略模板

---

## 12. 最终结论
对于 `MSEarth Open Ended`，目前最合理的处理方式是：

- **简洁 rewritten question 作为主题面**
- **caption 作为 supporting context 单独保存与按需展示**
- **reasoning_chain 作为后台审计字段**
- **不要把 caption 是否保留完全交给单一 normalization 字段决定**

一句话总结：

**MSEarth 的 caption 是证据，不是噪声；当前问题的核心不是题面太短，而是 supporting context 在 normalization 阶段被误删。**
