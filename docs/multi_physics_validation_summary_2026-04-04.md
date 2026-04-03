# Multi-Physics 验证总结（2026-04-04）

## 结论

`multi_physics` **可以继续保留并做后续验证**，但当前自动评估结果明显偏向 `review`，说明它在现有清洗/对齐策略下更适合作为“可用但需人工复核”的数据集，而不是直接高通过率的数据集。

---

## 已完成验证

### 1. 1 条 smoke

运行结果：

- `processed_samples = 1`
- `decision = review`
- `rewrite_strategy = blank_open`
- `successful_request_count = 8`
- `failed_request_count = 0`

观察：

- 数据源可读
- 图像可提取
- 样本可清洗
- 模型调用稳定
- 结果可落盘

### 2. 3 条小验证

运行结果：

- `processed_samples = 3`
- `pass = 0`
- `review = 3`
- `reject = 0`
- `rewrite_strategy_counts = { blank_open: 2, split_open: 1 }`
- `successful_request_count = 24`
- `failed_request_count = 0`
- `last_error = null`

观察：

- 三条全部可跑通
- 三条都没有 reject
- 重写可以稳定完成
- 但三条全部被判为 `review`

---

## 改写质量判断

`multi_physics` 当前的改写风格主要是将原始题面中的：

- 隐含判断题
- 选择题结论
- 图像支撑下的比较题

改成更直接的开放问答形式。

已观察到的主要改写策略：

- `blank_open`
- `split_open`

从 smoke 样本看，这类改写通常是合理的：

- 会把原来需要从选项里判断的内容，改写成直接询问答案
- 保留图像上下文
- 保留可验证答案

因此目前没有看到明显“乱改题意”的问题。

---

## 为什么现在更容易进 review

当前 `multi_physics` 的问题不像是：

- 数据源不可用
- 题干坏掉
- 图像缺失
- 答案缺失

而更像是：

> **样本可用，但视觉 grounding 与 alignment 的强度还不足以让系统放心直接 pass。**

从已查看样本结果来看，系统的保守点主要在：

- 对视觉证据链是否足够扎实持谨慎态度
- 对“图像支撑了什么推理”这一层不够自信
- 因此即便可解，也倾向进入 `review`

这和 `mm_math` 的“几何锚点太密导致 risky”不完全一样，但本质上仍然属于：

- **样本可用**
- **自动审查偏保守**

---

## 当前判断

### 优点

- GitHub 数据源已可程序化读取
- 图像资产可正常产出
- 清洗链条能走通
- responses API 下运行稳定
- 改写风格整体合理

### 问题

- 当前通过率偏低（3/3 review）
- 图像 grounding / alignment 说服力不够强
- 需要更多样本验证 review 是否普遍存在

---

## 建议

### 1. 继续保留 `multi_physics`

目前没有理由移除它。

### 2. 继续做 10 条级别验证

重点观察：

- `review` 是否持续占主导
- 哪类题最容易进入 `review`
- `blank_open` 和 `split_open` 哪类表现更稳定

### 3. 暂时不要因为 review 多就否掉它

因为目前看到的是：

- 样本并非不可用
- 更像自动审查门槛较高

---

## 目前建议的操作

- 保留 `multi_physics`
- 继续使用 responses API
- 先做单数据集 10 条验证
- 后续再决定是否需要针对该数据集放宽 review 门槛
