# MM-Math 验证总结（2026-04-04）

## 结论

`mm_math` **值得继续保留并推进验证**。

当前 smoke / 小样本结果显示，它不是“配置有问题”或“数据不可用”，而是：

- 数据源可读
- 图像可落盘
- 问题可抽取
- 改写能完成
- 模型调用稳定
- 但自动评估在 `alignment` 上偏保守，导致样本更容易落到 `review`

换句话说，`mm_math` 的主要问题更像是 **审查门槛偏严**，而不是 **样本质量差**。

---

## 已完成验证

### 1. 1 条 smoke

运行结果：

- `processed_samples = 1`
- `decision = review`
- `rewrite_strategy = keep_open`
- `successful_request_count = 7`
- `failed_request_count = 0`

观察：

- 样本可以完整跑通
- 题目和答案都能正常抽取
- 图像产物、records、samples、artifacts 都齐全

### 2. 3 条小验证

运行结果：

- `processed_samples = 3`
- `pass = 0`
- `review = 3`
- `reject = 0`
- `rewrite_strategy = keep_open`（3/3）
- `successful_request_count = 20`
- `failed_request_count = 1`
- `last_error = null`

观察：

- 三条都不是 reject
- 三条都保留了原题开放结构，说明改写没有乱改题意
- 题目本身大多是典型几何图题，图像依赖明确，答案可恢复

---

## 改写质量判断

当前 `mm_math` 样本的重写风格以 **规范化** 为主，而不是重构题意：

- 原题已经是开放题 → `keep_open`
- 主要做语言整理、格式标准化
- 保留图像依赖
- 保留可验证答案

从已检查的 smoke 样本来看，改写质量是正常的，没有明显“瞎改”或“降质改写”。

---

## 为什么经常进 review，而不是 pass

### 核心原因：alignment 状态经常被判为 `risky`

已检查样本中，反复出现的共同模式是：

- 文本里有很多视觉锚点（点、线、角、三角形、标签）
- 图像侧当前只形成较粗的 ROI 对齐
- 系统判定：`visual_reference_density_mismatch`

典型冲突：

- `alignment_status = risky`
- `conflict_pairs.type = visual_reference_density_mismatch`
- `detail = 文本中的视觉锚点明显多于可识别视觉区域`

这说明当前对齐模块对几何图题偏保守：

> 不是题不能做，而是系统不能非常自信地确认“文本中每个几何对象都被图像证据充分支持”。

### 次要原因

部分样本还有轻微附加风险：

- `answer_type` 标注不一致
- 解答说明里存在轻微中间步骤不一致
- `metadata.image_field` 为空但图像资产实际存在

这些问题会进一步推动 `review`，但它们都不是致命缺陷。

---

## 当前判断

### `mm_math` 的优点

- 图像样本明确，视觉依赖较强
- 题目整体可解性高
- 答案可验证性较好
- 改写策略稳定
- 跑通率高

### `mm_math` 的问题

- alignment 模块对几何图题过严
- 自动判断偏向 `review`
- 因此 `pass` 比例可能被低估

---

## 建议

### 1. 继续保留 `mm_math`

当前没有证据表明它应该被移除。

### 2. 可以继续做 10 条或更多验证

目的是看：

- `review` 是否持续高比例
- 是否存在稳定的子类模式（例如纯几何作图题更容易被 `risky`）

### 3. 中期可考虑为 `mm_math` 放宽 review 门槛

若后续确认：

- assets 完整
- solvability = pass
- rewrite 完整
- 仅因 `visual_reference_density_mismatch` 被压成 review

则可以考虑为 `mm_math` 增加更宽松的通过策略。

---

## 目前建议的操作

- 保留 `mm_math`
- 继续使用 responses API 跑验证
- 先按单数据集 YAML 跑 10 条
- 后续再决定是否要调整 alignment / review 策略
