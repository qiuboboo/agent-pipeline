# EMMA-Physics 验证总结（2026-04-04）

## 结论

`EMMA-Physics` **已经成功接通并可稳定运行**，但在当前自动评估策略下，样本更倾向被判为 `review`，而不是直接 `pass`。

当前观察表明，它的主要状态与 `mm_math` / `multi_physics` 相似：

- 数据源可用
- 配置正确
- 模型调用稳定
- 改写可完成
- 但自动质量门槛偏保守

因此，`EMMA-Physics` 当前适合被视为：

> **可跑、可用、值得继续评估，但不宜根据当前 3 条结果就期待高 pass 比例。**

---

## 已完成验证

### 1. 1 条 smoke

运行结果：

- `processed_samples = 1`
- `pass = 0`
- `review = 1`
- `reject = 0`
- `rewrite_strategy = blank_open`
- `successful_request_count = 8`
- `failed_request_count = 0`

观察：

- 数据源可读
- 图像字段可用
- 样本可完整进入清洗链
- responses API 路径稳定

### 2. 3 条验证

运行结果：

- `processed_samples = 3`
- `pass = 0`
- `review = 3`
- `reject = 0`
- `rewrite_strategy_counts = { blank_open: 1, drop_image_index: 2 }`
- `successful_request_count = 24`
- `failed_request_count = 0`
- `last_error = null`

观察：

- 三条都能完整跑通
- 没有 reject
- 但三条全部被判为 review

---

## 改写风格观察

`EMMA-Physics` 当前样本的重写主要体现为两类：

### 1. `blank_open`
将原本偏选择题/选项式题目改写成直接问答案的开放题。

### 2. `drop_image_index`
保留题目核心语义，但去掉或弱化原题中的 `<image_2> / <image_3> ...` 这类索引式表达，使问题更像自然语言开放题。

从已跑样本看，这两类改写本身并没有明显胡改题意的问题，说明：

- 改写链条是可用的
- EMMA-Physics 的多图题结构也能被当前系统处理

---

## 为什么更容易进 review

当前 `EMMA-Physics` 的问题不像是：

- 数据源坏了
- 图片读不出来
- 答案缺失
- pipeline 不兼容

而更像是：

> **题目可处理，但系统对多图、多选项、多视觉对象的对齐与可验证性判断仍然偏保守。**

从改写策略也能看出：

- `drop_image_index` 出现较多
- 说明系统在努力把多图索引式题面改写成更自然的开放问题

这类转换虽然能生成可用问题，但自动审查未必会给出很高置信度，因此更容易进入 `review`。

---

## 当前判断

### 优点

- Hugging Face `Physics` config 可直接读取
- `split: test` 可用且稳定
- 多图字段（`image_1` ~ `image_5`）已能进入现有流程
- responses API 下运行稳定
- 改写逻辑能覆盖多图多选题

### 问题

- 当前通过率低（3/3 review）
- 自动评估对多图结构偏谨慎
- 需要更多样本来确认这是普遍现象还是只出现在头部样本

---

## 建议

### 1. 保留 `EMMA-Physics`

当前没有理由移除它。

### 2. 如果继续跑，建议先做 10 条级别验证

重点看：

- `review` 是否持续高比例
- `drop_image_index` 是否成为主导策略
- 哪类题更容易被判为 review

### 3. 暂时不要因为 review 多就否掉它

因为目前看到的是：

- 它是“可用但保守”
- 不是“不可用”

---

## 目前建议的操作

- 保留 `EMMA-Physics`
- 如需继续推进，可补一个 `EMMA-Physics 10 条验证` YAML
- 后续再看是否值得单独调一版 review / alignment 策略
