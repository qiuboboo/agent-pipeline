# CMM-Math：20 条采集清洗逐样本报告

- pipeline_run_id：`run_f2958f3118292117`
- 数据集 key：`cmm_math`
- processed_samples：`20` / requested `20`
- 决策计数：`pass=13`，`review=6`，`reject=1`
- 改写策略计数：`{"split_open": 7, "blank_open": 13}`
- 对齐状态计数：`good:19, bad:1`
- 高频原因码：`meets_cleaning_requirements:13, split_variant_needs_review:6, missing_core_field:1, missing_core_image:1, missing_grounded_visual_path:1, text_image_misaligned:1`
- 占位符题面（`text/bar`）样本数：`0`
- 文本主导样本数：`19`

## 01. prob_0db135e9e3e5c300251d3e64

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_0db135e9e3e5c300251d3e64.json](../../datasets/cmm_math/samples/prob_0db135e9e3e5c300251d3e64.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`19900`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`pass`
- 决策原因码：`meets_cleaning_requirements`
- 开放化改写策略：`blank_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.78
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\left\{\begin{array}{l}2 x-y-2 \geq 0, \\ x+2 y-1 \geq 0, \\ 3 x+y-8 \leq 0\end{array}\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )
```

**原始答案**

```text
$-\frac{1}{3}$
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\left\{\begin{array}{l}2 x-y-2 \geq 0, \\ x+2 y-1 \geq 0, \\ 3 x+y-8 \leq 0\end{array}\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )
```

**规范化答案**

```text
$-\frac{1}{3}$
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\left\{\begin{array}{l}2 x-y-2 \geq 0, \\ x+2 y-1 \geq 0, \\ 3 x+y-8 \leq 0\end{array}\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )
```

**改写后（开放题变体）**

```text
在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\left\{\begin{array}{l}2 x-y-2 \geq 0, \\ x+2 y-1 \geq 0, \\ 3 x+y-8 \leq 0\end{array}\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )
```

- 期望答案类型：`short_text`
- 期望答案：`$-\frac{1}{3}$`
- 改写 rationale：`Converted multiple choice into blank-style open-ended question.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8709,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "alignment_summary": {
    "alignment_id": "align_c38060f574f5bb755b062090",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_0db135e9e3e5c300251d3e64",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 02. prob_116e812e838d2a9406b18c44

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_116e812e838d2a9406b18c44.json](../../datasets/cmm_math/samples/prob_116e812e838d2a9406b18c44.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`19880`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`review`
- 决策原因码：`split_variant_needs_review`
- 开放化改写策略：`split_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.62
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
若实数 $x 、 y$ 满足 $\left\{\begin{array}{l}x+2 y-4 \leq 0, \\ x \geq 0, \\ y \geq 0,\end{array}\right.$ 则 $z=\frac{y+2}{x-1}$ 的取值范围为 ( )
```

**原始答案**

```text
$(-\infty,-2] \cup\left[\frac{2}{3},+\infty\right)$
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
若实数 $x 、 y$ 满足 $\left\{\begin{array}{l}x+2 y-4 \leq 0, \\ x \geq 0, \\ y \geq 0,\end{array}\right.$ 则 $z=\frac{y+2}{x-1}$ 的取值范围为 ( )
```

**规范化答案**

```text
$(-\infty,-2] \cup\left[\frac{2}{3},+\infty\right)$
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
若实数 $x 、 y$ 满足 $\left\{\begin{array}{l}x+2 y-4 \leq 0, \\ x \geq 0, \\ y \geq 0,\end{array}\right.$ 则 $z=\frac{y+2}{x-1}$ 的取值范围为 ( )
```

**改写后（开放题变体）**

```text
若实数 $x 、 y$ 满足 $\left\{\begin{array}{l}x+2 y-4 \leq 0, \\ x \geq 0, \\ y \geq 0,\end{array}\right.$ 则 $z=\frac{y+2}{x-1}$ 的取值范围为 ( )
请只回答第 1 个目标量。
```

- 期望答案类型：`short_text`
- 期望答案：`$(-\infty,-2] \cup\left[\frac{2}{3},+\infty\right)$`
- 改写 rationale：`Compound choice answer was split into multiple open-ended targets.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8497,
  "decision": "review",
  "decision_reason_codes": [
    "split_variant_needs_review"
  ],
  "alignment_summary": {
    "alignment_id": "align_8fc01362775d78a32af38a6d",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_116e812e838d2a9406b18c44",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 03. prob_14a57e191dcf265f53901c57

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_14a57e191dcf265f53901c57.json](../../datasets/cmm_math/samples/prob_14a57e191dcf265f53901c57.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`19890`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`pass`
- 决策原因码：`meets_cleaning_requirements`
- 开放化改写策略：`blank_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.78
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
若 $x, y$ 满足 $\left\{\begin{array}{l}x \leq 3, \\ x+y \geq 2, \\ y \leq x,\end{array}\right.$ 则 $x+2 y$ 的最大值为
```

**原始答案**

```text
9
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
若 $x, y$ 满足 $\left\{\begin{array}{l}x \leq 3, \\ x+y \geq 2, \\ y \leq x,\end{array}\right.$ 则 $x+2 y$ 的最大值为
```

**规范化答案**

```text
9
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
若 $x, y$ 满足 $\left\{\begin{array}{l}x \leq 3, \\ x+y \geq 2, \\ y \leq x,\end{array}\right.$ 则 $x+2 y$ 的最大值为
```

**改写后（开放题变体）**

```text
若 $x, y$ 满足 $\left\{\begin{array}{l}x \leq 3, \\ x+y \geq 2, \\ y \leq x,\end{array}\right.$ 则 $x+2 y$ 的最大值为
```

- 期望答案类型：`numeric`
- 期望答案：`9`
- 改写 rationale：`Converted multiple choice into blank-style open-ended question.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8462,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "alignment_summary": {
    "alignment_id": "align_9059e48c899c1aa78a71819f",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_14a57e191dcf265f53901c57",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 04. prob_408c338dc6426f67f9b9df88

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_408c338dc6426f67f9b9df88.json](../../datasets/cmm_math/samples/prob_408c338dc6426f67f9b9df88.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`18973`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`pass`
- 决策原因码：`meets_cleaning_requirements`
- 开放化改写策略：`blank_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.78
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
在 $\triangle A B C$ 中, 已知 $B=60^{\circ}, C=45^{\circ}, B C=2$, 且 $A D \perp B C$ 于 $D$, 则 $A D=(\quad)$
```

**原始答案**

```text
$3-\sqrt{3}$
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
在 $\triangle A B C$ 中, 已知 $B=60^{\circ}, C=45^{\circ}, B C=2$, 且 $A D \perp B C$ 于 $D$, 则 $A D=(\quad)$
```

**规范化答案**

```text
$3-\sqrt{3}$
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
在 $\triangle A B C$ 中, 已知 $B=60^{\circ}, C=45^{\circ}, B C=2$, 且 $A D \perp B C$ 于 $D$, 则 $A D=(\quad)$
```

**改写后（开放题变体）**

```text
在 $\triangle A B C$ 中, 已知 $B=60^{\circ}, C=45^{\circ}, B C=2$, 且 $A D \perp B C$ 于 $D$, 则 $A D=(\quad)$
```

- 期望答案类型：`short_text`
- 期望答案：`$3-\sqrt{3}$`
- 改写 rationale：`Converted multiple choice into blank-style open-ended question.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8635,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "alignment_summary": {
    "alignment_id": "align_d81602e06feb996cb6fcb970",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_408c338dc6426f67f9b9df88",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 05. prob_571567bd8a6ebcd43e45b8b8

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_571567bd8a6ebcd43e45b8b8.json](../../datasets/cmm_math/samples/prob_571567bd8a6ebcd43e45b8b8.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`19896`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`pass`
- 决策原因码：`meets_cleaning_requirements`
- 开放化改写策略：`blank_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.78
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
如果实数 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-y+1 \geq 0, \\ y+1 \geq 0, \\ x+y+1 \leq 0,\end{array}\right.$ 则 $2 x-y$ 的最大值为 ( )
```

**原始答案**

```text
1
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
如果实数 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-y+1 \geq 0, \\ y+1 \geq 0, \\ x+y+1 \leq 0,\end{array}\right.$ 则 $2 x-y$ 的最大值为 ( )
```

**规范化答案**

```text
1
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
如果实数 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-y+1 \geq 0, \\ y+1 \geq 0, \\ x+y+1 \leq 0,\end{array}\right.$ 则 $2 x-y$ 的最大值为 ( )
```

**改写后（开放题变体）**

```text
如果实数 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-y+1 \geq 0, \\ y+1 \geq 0, \\ x+y+1 \leq 0,\end{array}\right.$ 则 $2 x-y$ 的最大值为 ( )
```

- 期望答案类型：`numeric`
- 期望答案：`1`
- 改写 rationale：`Converted multiple choice into blank-style open-ended question.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8489,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "alignment_summary": {
    "alignment_id": "align_17ec56dd3797f2464b509a13",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_571567bd8a6ebcd43e45b8b8",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 06. prob_59b86cd9990583e40984ebaf

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_59b86cd9990583e40984ebaf.json](../../datasets/cmm_math/samples/prob_59b86cd9990583e40984ebaf.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`18972`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`pass`
- 决策原因码：`meets_cleaning_requirements`
- 开放化改写策略：`blank_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.78
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
在 $\triangle \mathrm{ABC}$ 中, $B=\frac{\pi}{6}, \mathrm{c}=4, \cos C=\frac{\sqrt{5}}{3}$, 则 $\mathrm{b}=(\quad)$
```

**原始答案**

```text
3 c. $\frac{3}{2}$
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
在 $\triangle \mathrm{ABC}$ 中, $B=\frac{\pi}{6}, \mathrm{c}=4, \cos C=\frac{\sqrt{5}}{3}$, 则 $\mathrm{b}=(\quad)$
```

**规范化答案**

```text
3 c. $\frac{3}{2}$
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
在 $\triangle \mathrm{ABC}$ 中, $B=\frac{\pi}{6}, \mathrm{c}=4, \cos C=\frac{\sqrt{5}}{3}$, 则 $\mathrm{b}=(\quad)$
```

**改写后（开放题变体）**

```text
在 $\triangle \mathrm{ABC}$ 中, $B=\frac{\pi}{6}, \mathrm{c}=4, \cos C=\frac{\sqrt{5}}{3}$, 则 $\mathrm{b}=(\quad)$
```

- 期望答案类型：`short_text`
- 期望答案：`3 c. $\frac{3}{2}$`
- 改写 rationale：`Converted multiple choice into blank-style open-ended question.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8648,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "alignment_summary": {
    "alignment_id": "align_78f58106c65d9e65dc387eb5",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_59b86cd9990583e40984ebaf",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 07. prob_6e6fd12acd827d164b88c477

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_6e6fd12acd827d164b88c477.json](../../datasets/cmm_math/samples/prob_6e6fd12acd827d164b88c477.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`18945`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`pass`
- 决策原因码：`meets_cleaning_requirements`
- 开放化改写策略：`blank_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.78
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
设变量 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x+y-2 \leq 0, \\ x-y+2 \geq 0, \\ x \geqslant-1, \\ y \geqslant-1,\end{array}\right.$, 则目标函数 $z=-4 x+y$ 的最大值为（）
```

**原始答案**

```text
6
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
设变量 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x+y-2 \leq 0, \\ x-y+2 \geq 0, \\ x \geqslant-1, \\ y \geqslant-1,\end{array}\right.$, 则目标函数 $z=-4 x+y$ 的最大值为()
```

**规范化答案**

```text
6
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
设变量 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x+y-2 \leq 0, \\ x-y+2 \geq 0, \\ x \geqslant-1, \\ y \geqslant-1,\end{array}\right.$, 则目标函数 $z=-4 x+y$ 的最大值为()
```

**改写后（开放题变体）**

```text
设变量 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x+y-2 \leq 0, \\ x-y+2 \geq 0, \\ x \geqslant-1, \\ y \geqslant-1,\end{array}\right.$, 则目标函数 $z=-4 x+y$ 的最大值为()
```

- 期望答案类型：`numeric`
- 期望答案：`6`
- 改写 rationale：`Converted multiple choice into blank-style open-ended question.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8527,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "alignment_summary": {
    "alignment_id": "align_339856d108c5f20ef7e6acee",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_6e6fd12acd827d164b88c477",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 08. prob_7dc65d690d408e30adb39da1

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_7dc65d690d408e30adb39da1.json](../../datasets/cmm_math/samples/prob_7dc65d690d408e30adb39da1.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`18971`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`pass`
- 决策原因码：`meets_cleaning_requirements`
- 开放化改写策略：`blank_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.78
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
已知三角形 $\triangle A B C$ 中, $A=30^{\circ}, C=105^{\circ}, b=4$, 则 $a=(\quad)$
```

**原始答案**

```text
$2 \sqrt{2}$ c. $2 \sqrt{3}$
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
已知三角形 $\triangle A B C$ 中, $A=30^{\circ}, C=105^{\circ}, b=4$, 则 $a=(\quad)$
```

**规范化答案**

```text
$2 \sqrt{2}$ c. $2 \sqrt{3}$
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
已知三角形 $\triangle A B C$ 中, $A=30^{\circ}, C=105^{\circ}, b=4$, 则 $a=(\quad)$
```

**改写后（开放题变体）**

```text
已知三角形 $\triangle A B C$ 中, $A=30^{\circ}, C=105^{\circ}, b=4$, 则 $a=(\quad)$
```

- 期望答案类型：`short_text`
- 期望答案：`$2 \sqrt{2}$ c. $2 \sqrt{3}$`
- 改写 rationale：`Converted multiple choice into blank-style open-ended question.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8597,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "alignment_summary": {
    "alignment_id": "align_a76985385d43659cef86db0d",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_7dc65d690d408e30adb39da1",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 09. prob_7e4755a218fcc37692eeeee9

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_7e4755a218fcc37692eeeee9.json](../../datasets/cmm_math/samples/prob_7e4755a218fcc37692eeeee9.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`19876`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`review`
- 决策原因码：`split_variant_needs_review`
- 开放化改写策略：`split_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.62
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
$x$ 的不等式 $a x-b<0$ 的解集是 $(1,+\infty)$, 则关于 $x$ 的不等式 $(a x+b)(x-3)>0$ 的解集是( )
```

**原始答案**

```text
$(-1,3)$
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
$x$ 的不等式 $a x-b<0$ 的解集是 $(1,+\infty)$, 则关于 $x$ 的不等式 $(a x+b)(x-3)>0$ 的解集是( )
```

**规范化答案**

```text
$(-1,3)$
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
$x$ 的不等式 $a x-b<0$ 的解集是 $(1,+\infty)$, 则关于 $x$ 的不等式 $(a x+b)(x-3)>0$ 的解集是( )
```

**改写后（开放题变体）**

```text
$x$ 的不等式 $a x-b<0$ 的解集是 $(1,+\infty)$, 则关于 $x$ 的不等式 $(a x+b)(x-3)>0$ 的解集是( )
请只回答第 1 个目标量。
```

- 期望答案类型：`short_text`
- 期望答案：`$(-1,3)$`
- 改写 rationale：`Compound choice answer was split into multiple open-ended targets.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8417,
  "decision": "review",
  "decision_reason_codes": [
    "split_variant_needs_review"
  ],
  "alignment_summary": {
    "alignment_id": "align_3e396b3f48d0bebf116e958d",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_7e4755a218fcc37692eeeee9",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 10. prob_943c98d97f7a82f001936f4a

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_943c98d97f7a82f001936f4a.json](../../datasets/cmm_math/samples/prob_943c98d97f7a82f001936f4a.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`18902`
- 清洗路径：`multimodal_full`
- 是否文本主导：`False`
- 是否依赖图像：`True`
- 决策：`reject`
- 决策原因码：`missing_core_field, missing_core_image, missing_grounded_visual_path, text_image_misaligned`
- 开放化改写策略：`split_open`
- 对齐状态：`bad`
- 可解性分数：`0.8`
- 可解性提示：`reject`
- 质量风险标记：`missing_core_image`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.9,
    "initial_multi_solution_score": 0.52,
    "initial_verifiability_score": 0.62
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
太极图被称为“中华第一图”. 从孔庙大成殿粱柱, 到楼观台、三茅宫标记物; 从道袍、卦推、中医、气功、武术到南韩国旗…… 太极图无不跃居其上. 这种广为人知的太极图, 其形状如阴阳两鱼互抱在一起, 因而被称为“阴阳鱼太极图”. 在如图所示的阴阳鱼图案中, 阴影部分可表示为

$A=\left\{(x, y) \mid x^{2}+(y-1)^{2} \leq 1\right.$ 或 $\left\{\begin{array}{l}x^{2}+y^{2} \leq 4 \\ x^{2}+(y+1)^{2} \geq 1 \\ x \leq 0\end{array}\right\}$, 设点 $(x, y) \in A$, 则 $z=x+2 y$ 的取值范围是 ( )

<ImageHere>
```

**原始答案**

```text
$[-2 \sqrt{5}, 2+\sqrt{5}]$
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
太极图被称为“中华第一图”. 从孔庙大成殿粱柱, 到楼观台、三茅宫标记物; 从道袍、卦推、中医、气功、武术到南韩国旗...... 太极图无不跃居其上. 这种广为人知的太极图, 其形状如阴阳两鱼互抱在一起, 因而被称为“阴阳鱼太极图”. 在如图所示的阴阳鱼图案中, 阴影部分可表示为

$A=\left\{(x, y) \mid x^{2}+(y-1)^{2} \leq 1\right.$ 或 $\left\{\begin{array}{l}x^{2}+y^{2} \leq 4 \\ x^{2}+(y+1)^{2} \geq 1 \\ x \leq 0\end{array}\right\}$, 设点 $(x, y) \in A$, 则 $z=x+2 y$ 的取值范围是 ( )

<ImageHere>
```

**规范化答案**

```text
$[-2 \sqrt{5}, 2+\sqrt{5}]$
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
太极图被称为“中华第一图”. 从孔庙大成殿粱柱, 到楼观台、三茅宫标记物; 从道袍、卦推、中医、气功、武术到南韩国旗...... 太极图无不跃居其上. 这种广为人知的太极图, 其形状如阴阳两鱼互抱在一起, 因而被称为“阴阳鱼太极图”. 在如图所示的阴阳鱼图案中, 阴影部分可表示为

$A=\left\{(x, y) \mid x^{2}+(y-1)^{2} \leq 1\right.$ 或 $\left\{\begin{array}{l}x^{2}+y^{2} \leq 4 \\ x^{2}+(y+1)^{2} \geq 1 \\ x \leq 0\end{array}\right\}$, 设点 $(x, y) \in A$, 则 $z=x+2 y$ 的取值范围是 ( )

<ImageHere>
```

**改写后（开放题变体）**

```text
太极图被称为“中华第一图”. 从孔庙大成殿粱柱, 到楼观台、三茅宫标记物; 从道袍、卦推、中医、气功、武术到南韩国旗...... 太极图无不跃居其上. 这种广为人知的太极图, 其形状如阴阳两鱼互抱在一起, 因而被称为“阴阳鱼太极图”. 在如图所示的阴阳鱼图案中, 阴影部分可表示为

$A=\left\{(x, y) \mid x^{2}+(y-1)^{2} \leq 1\right.$ 或 $\left\{\begin{array}{l}x^{2}+y^{2} \leq 4 \\ x^{2}+(y+1)^{2} \geq 1 \\ x \leq 0\end{array}\right\}$, 设点 $(x, y) \in A$, 则 $z=x+2 y$ 的取值范围是 ( )

<ImageHere>
请只回答第 1 个目标量。
```

- 期望答案类型：`short_text`
- 期望答案：`$[-2 \sqrt{5}, 2+\sqrt{5}]$`
- 改写 rationale：`Compound choice answer was split into multiple open-ended targets.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.5804,
  "decision": "reject",
  "decision_reason_codes": [
    "missing_core_field",
    "missing_core_image",
    "missing_grounded_visual_path",
    "text_image_misaligned"
  ],
  "alignment_summary": {
    "alignment_id": "align_a01337199003a4937a6e661d",
    "coverage_score": 0.18,
    "consistency_score": 0.0,
    "alignment_status": "bad",
    "conflict_count": 3
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_943c98d97f7a82f001936f4a",
    "solvability_score": 0.8,
    "reasoning_path_exists": false,
    "decision_hint": "reject",
    "failure_codes": [
      "missing_grounded_visual_path",
      "missing_core_field"
    ]
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 1
  },
  "risk_flags": [
    "missing_core_image"
  ],
  "reject_record": {
    "reject_id": "reject_a01337199003a4937a6e661d",
    "problem_id": "prob_943c98d97f7a82f001936f4a",
    "stage": "cleaning",
    "reject_level": "problem",
    "reject_reason_codes": [
      "missing_core_field",
      "missing_core_image",
      "missing_grounded_visual_path",
      "text_image_misaligned"
    ],
    "reject_reason_detail": "Compound choice answer was split into multiple open-ended targets.",
    "blocking_fields": [
      "missing_core_image"
    ],
    "evidence_refs": [
      "align_a01337199003a4937a6e661d",
      "solv_prob_943c98d97f7a82f001936f4a"
    ],
    "recoverable": false,
    "recommended_action": "drop",
    "reviewed_by": null,
    "created_at": "2026-03-25T08:47:22Z"
  }
}
```

---

## 11. prob_a469e8f2eb58a970b588e0d5

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_a469e8f2eb58a970b588e0d5.json](../../datasets/cmm_math/samples/prob_a469e8f2eb58a970b588e0d5.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`19899`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`review`
- 决策原因码：`split_variant_needs_review`
- 开放化改写策略：`split_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.62
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
已知 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-y \geq 0, \\ x+y \leq 2, \\ y \geq 0,\end{array}\right.$围为 ( )
```

**原始答案**

```text
$[-1,1]$
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
已知 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-y \geq 0, \\ x+y \leq 2, \\ y \geq 0,\end{array}\right.$围为 ( )
```

**规范化答案**

```text
$[-1,1]$
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
已知 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-y \geq 0, \\ x+y \leq 2, \\ y \geq 0,\end{array}\right.$围为 ( )
```

**改写后（开放题变体）**

```text
已知 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-y \geq 0, \\ x+y \leq 2, \\ y \geq 0,\end{array}\right.$围为 ( )
请只回答第 1 个目标量。
```

- 期望答案类型：`short_text`
- 期望答案：`$[-1,1]$`
- 改写 rationale：`Compound choice answer was split into multiple open-ended targets.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8458,
  "decision": "review",
  "decision_reason_codes": [
    "split_variant_needs_review"
  ],
  "alignment_summary": {
    "alignment_id": "align_9cf0b5540927db8d55d82373",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_a469e8f2eb58a970b588e0d5",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 12. prob_a7f1f8d9176c160f1c3b4cbc

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_a7f1f8d9176c160f1c3b4cbc.json](../../datasets/cmm_math/samples/prob_a7f1f8d9176c160f1c3b4cbc.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`19894`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`review`
- 决策原因码：`split_variant_needs_review`
- 开放化改写策略：`split_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.62
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )
```

**原始答案**

```text
$(-7,24)$
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )
```

**规范化答案**

```text
$(-7,24)$
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )
```

**改写后（开放题变体）**

```text
已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )
请只回答第 1 个目标量。
```

- 期望答案类型：`short_text`
- 期望答案：`$(-7,24)$`
- 改写 rationale：`Compound choice answer was split into multiple open-ended targets.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8401,
  "decision": "review",
  "decision_reason_codes": [
    "split_variant_needs_review"
  ],
  "alignment_summary": {
    "alignment_id": "align_5c1c178b4ca80bd2efa09244",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_a7f1f8d9176c160f1c3b4cbc",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 13. prob_b1cb15b0aa1053ab2cf788ec

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_b1cb15b0aa1053ab2cf788ec.json](../../datasets/cmm_math/samples/prob_b1cb15b0aa1053ab2cf788ec.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`18925`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`pass`
- 决策原因码：`meets_cleaning_requirements`
- 开放化改写策略：`blank_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.78
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
若实数 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-3 y+4 \geq 0 \\ 3 x-y-4 \leq 0 \\ x+y \geq 0\end{array}\right.$, 则 $z=3 x+2 y$ 的最大值是
```

**原始答案**

```text
10
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
若实数 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-3 y+4 \geq 0 \\ 3 x-y-4 \leq 0 \\ x+y \geq 0\end{array}\right.$, 则 $z=3 x+2 y$ 的最大值是
```

**规范化答案**

```text
10
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
若实数 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-3 y+4 \geq 0 \\ 3 x-y-4 \leq 0 \\ x+y \geq 0\end{array}\right.$, 则 $z=3 x+2 y$ 的最大值是
```

**改写后（开放题变体）**

```text
若实数 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-3 y+4 \geq 0 \\ 3 x-y-4 \leq 0 \\ x+y \geq 0\end{array}\right.$, 则 $z=3 x+2 y$ 的最大值是
```

- 期望答案类型：`numeric`
- 期望答案：`10`
- 改写 rationale：`Converted multiple choice into blank-style open-ended question.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8491,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "alignment_summary": {
    "alignment_id": "align_4fc51a979095fa6816fc5b08",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_b1cb15b0aa1053ab2cf788ec",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 14. prob_be98bd21bcce4a8120a8c823

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_be98bd21bcce4a8120a8c823.json](../../datasets/cmm_math/samples/prob_be98bd21bcce4a8120a8c823.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`19882`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`pass`
- 决策原因码：`meets_cleaning_requirements`
- 开放化改写策略：`blank_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.78
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
实数 $x, y, k$ 满足 $\left\{\begin{array}{l}x+y-3 \geq 0, \\ x-y+1 \geq 0, z=x^{2}+y^{2} \text {, 若 } z \text { 的最大值为 } 13 \text {, 则 } k \text { 的值为 ( ) } \\ x \leq k,\end{array}\right.$
```

**原始答案**

```text
2
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
实数 $x, y, k$ 满足 $\left\{\begin{array}{l}x+y-3 \geq 0, \\ x-y+1 \geq 0, z=x^{2}+y^{2} \text {, 若 } z \text { 的最大值为 } 13 \text {, 则 } k \text { 的值为 ( ) } \\ x \leq k,\end{array}\right.$
```

**规范化答案**

```text
2
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
实数 $x, y, k$ 满足 $\left\{\begin{array}{l}x+y-3 \geq 0, \\ x-y+1 \geq 0, z=x^{2}+y^{2} \text {, 若 } z \text { 的最大值为 } 13 \text {, 则 } k \text { 的值为 ( ) } \\ x \leq k,\end{array}\right.$
```

**改写后（开放题变体）**

```text
实数 $x, y, k$ 满足 $\left\{\begin{array}{l}x+y-3 \geq 0, \\ x-y+1 \geq 0, z=x^{2}+y^{2} \text {, 若 } z \text { 的最大值为 } 13 \text {, 则 } k \text { 的值为 ( ) } \\ x \leq k,\end{array}\right.$
```

- 期望答案类型：`numeric`
- 期望答案：`2`
- 改写 rationale：`Converted multiple choice into blank-style open-ended question.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8569,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "alignment_summary": {
    "alignment_id": "align_e28235255233803d7153c111",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_be98bd21bcce4a8120a8c823",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 15. prob_c33b3ac9e45dad73821aa4fd

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_c33b3ac9e45dad73821aa4fd.json](../../datasets/cmm_math/samples/prob_c33b3ac9e45dad73821aa4fd.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`18947`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`pass`
- 决策原因码：`meets_cleaning_requirements`
- 开放化改写策略：`blank_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.78
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
设 $\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \sin A \sin C=\frac{\sqrt{3}-1}{4}$, 则
角 $C=(\quad)$
```

**原始答案**

```text
$C=15^{\circ}$ 或 $C=45^{\circ}$
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
设 $\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \sin A \sin C=\frac{\sqrt{3}-1}{4}$, 则
角 $C=(\quad)$
```

**规范化答案**

```text
$C=15^{\circ}$ 或 $C=45^{\circ}$
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
设 $\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \sin A \sin C=\frac{\sqrt{3}-1}{4}$, 则
角 $C=(\quad)$
```

**改写后（开放题变体）**

```text
设 $\triangle A B C$ 的内角 $A, B, C$ 的对边分别为 $a, b, c,(a+b+c)(a-b+c)=a c, \sin A \sin C=\frac{\sqrt{3}-1}{4}$, 则
角 $C=(\quad)$
```

- 期望答案类型：`short_text`
- 期望答案：`$C=15^{\circ}$ 或 $C=45^{\circ}$`
- 改写 rationale：`Converted multiple choice into blank-style open-ended question.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8662,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "alignment_summary": {
    "alignment_id": "align_5d94c0bc34d2c8b6c47ed3db",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_c33b3ac9e45dad73821aa4fd",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 16. prob_caae2865377ccd6944f59a21

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_caae2865377ccd6944f59a21.json](../../datasets/cmm_math/samples/prob_caae2865377ccd6944f59a21.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`18905`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`review`
- 决策原因码：`split_variant_needs_review`
- 开放化改写策略：`split_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.62
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
设不等式组 $\left\{\begin{array}{l}x+y-3 \geq 0 \\ x-y+1 \geq 0 \\ 3 x-y-5 \leq 0\end{array}\right.$ 表示的平面区域为 $M$, 若直线 $y=k x$ 经过区域 $M$ 内的点, 则实数 $k$ 的取值范围为
```

**原始答案**

```text
$\left[\frac{1}{2}, 2\right]$
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
设不等式组 $\left\{\begin{array}{l}x+y-3 \geq 0 \\ x-y+1 \geq 0 \\ 3 x-y-5 \leq 0\end{array}\right.$ 表示的平面区域为 $M$, 若直线 $y=k x$ 经过区域 $M$ 内的点, 则实数 $k$ 的取值范围为
```

**规范化答案**

```text
$\left[\frac{1}{2}, 2\right]$
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
设不等式组 $\left\{\begin{array}{l}x+y-3 \geq 0 \\ x-y+1 \geq 0 \\ 3 x-y-5 \leq 0\end{array}\right.$ 表示的平面区域为 $M$, 若直线 $y=k x$ 经过区域 $M$ 内的点, 则实数 $k$ 的取值范围为
```

**改写后（开放题变体）**

```text
设不等式组 $\left\{\begin{array}{l}x+y-3 \geq 0 \\ x-y+1 \geq 0 \\ 3 x-y-5 \leq 0\end{array}\right.$ 表示的平面区域为 $M$, 若直线 $y=k x$ 经过区域 $M$ 内的点, 则实数 $k$ 的取值范围为
请只回答第 1 个目标量。
```

- 期望答案类型：`short_text`
- 期望答案：`$\left[\frac{1}{2}, 2\right]$`
- 改写 rationale：`Compound choice answer was split into multiple open-ended targets.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8702,
  "decision": "review",
  "decision_reason_codes": [
    "split_variant_needs_review"
  ],
  "alignment_summary": {
    "alignment_id": "align_a5bb0b4dd698bf8dadbe55fc",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_caae2865377ccd6944f59a21",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 17. prob_d74f71876f9e0f5717ba47af

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_d74f71876f9e0f5717ba47af.json](../../datasets/cmm_math/samples/prob_d74f71876f9e0f5717ba47af.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`18900`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`pass`
- 决策原因码：`meets_cleaning_requirements`
- 开放化改写策略：`blank_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.78
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
在 $\triangle A B C$ 中, $a, b, c$ 分别为角 $A$, $B, C$ 的对边, 若 $\triangle A B C$ 的面积为 $S$, 且 $4 \sqrt{3} S=(a+b)^{2}-c^{2}$, 则 $\sin \left(C+\frac{\pi}{4}\right)=$
```

**原始答案**

```text
$\frac{\sqrt{6}+\sqrt{2}}{4}$
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
在 $\triangle A B C$ 中, $a, b, c$ 分别为角 $A$, $B, C$ 的对边, 若 $\triangle A B C$ 的面积为 $S$, 且 $4 \sqrt{3} S=(a+b)^{2}-c^{2}$, 则 $\sin \left(C+\frac{\pi}{4}\right)=$
```

**规范化答案**

```text
$\frac{\sqrt{6}+\sqrt{2}}{4}$
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
在 $\triangle A B C$ 中, $a, b, c$ 分别为角 $A$, $B, C$ 的对边, 若 $\triangle A B C$ 的面积为 $S$, 且 $4 \sqrt{3} S=(a+b)^{2}-c^{2}$, 则 $\sin \left(C+\frac{\pi}{4}\right)=$
```

**改写后（开放题变体）**

```text
在 $\triangle A B C$ 中, $a, b, c$ 分别为角 $A$, $B, C$ 的对边, 若 $\triangle A B C$ 的面积为 $S$, 且 $4 \sqrt{3} S=(a+b)^{2}-c^{2}$, 则 $\sin \left(C+\frac{\pi}{4}\right)=$
```

- 期望答案类型：`short_text`
- 期望答案：`$\frac{\sqrt{6}+\sqrt{2}}{4}$`
- 改写 rationale：`Converted multiple choice into blank-style open-ended question.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8712,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "alignment_summary": {
    "alignment_id": "align_a3d0a2a1049f8b563ff9f6fc",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_d74f71876f9e0f5717ba47af",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 18. prob_de810fbe4373a608c3486a6a

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_de810fbe4373a608c3486a6a.json](../../datasets/cmm_math/samples/prob_de810fbe4373a608c3486a6a.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`18927`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`pass`
- 决策原因码：`meets_cleaning_requirements`
- 开放化改写策略：`blank_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.78
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
在 $\triangle A B C$ 中, $a=1, \angle A=\frac{\pi}{6}, \angle B=\frac{\pi}{4}$, 则 $C=(\quad)$
```

**原始答案**

```text
$\frac{\sqrt{6}+\sqrt{2}}{2}$
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
在 $\triangle A B C$ 中, $a=1, \angle A=\frac{\pi}{6}, \angle B=\frac{\pi}{4}$, 则 $C=(\quad)$
```

**规范化答案**

```text
$\frac{\sqrt{6}+\sqrt{2}}{2}$
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
在 $\triangle A B C$ 中, $a=1, \angle A=\frac{\pi}{6}, \angle B=\frac{\pi}{4}$, 则 $C=(\quad)$
```

**改写后（开放题变体）**

```text
在 $\triangle A B C$ 中, $a=1, \angle A=\frac{\pi}{6}, \angle B=\frac{\pi}{4}$, 则 $C=(\quad)$
```

- 期望答案类型：`short_text`
- 期望答案：`$\frac{\sqrt{6}+\sqrt{2}}{2}$`
- 改写 rationale：`Converted multiple choice into blank-style open-ended question.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8618,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "alignment_summary": {
    "alignment_id": "align_87e708fbbba6495c7ccb9dbf",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_de810fbe4373a608c3486a6a",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 19. prob_faf698091f521f348b4f28a2

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_faf698091f521f348b4f28a2.json](../../datasets/cmm_math/samples/prob_faf698091f521f348b4f28a2.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`19897`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`pass`
- 决策原因码：`meets_cleaning_requirements`
- 开放化改写策略：`blank_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.78
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
若 $x, y$ 满足 $\left\{\begin{array}{l}x-y+3 \geq 0, \\ x+y+1 \geq 0, \\ x \leq k,\end{array}\right.$
```

**原始答案**

```text
1
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
若 $x, y$ 满足 $\left\{\begin{array}{l}x-y+3 \geq 0, \\ x+y+1 \geq 0, \\ x \leq k,\end{array}\right.$
```

**规范化答案**

```text
1
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
若 $x, y$ 满足 $\left\{\begin{array}{l}x-y+3 \geq 0, \\ x+y+1 \geq 0, \\ x \leq k,\end{array}\right.$
```

**改写后（开放题变体）**

```text
若 $x, y$ 满足 $\left\{\begin{array}{l}x-y+3 \geq 0, \\ x+y+1 \geq 0, \\ x \leq k,\end{array}\right.$
```

- 期望答案类型：`numeric`
- 期望答案：`1`
- 改写 rationale：`Converted multiple choice into blank-style open-ended question.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8448,
  "decision": "pass",
  "decision_reason_codes": [
    "meets_cleaning_requirements"
  ],
  "alignment_summary": {
    "alignment_id": "align_949cc2d9fd3a80bc53fa61a4",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_faf698091f521f348b4f28a2",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

---

## 20. prob_fef79efed09d0ee1752224e4

- 样本文件：[benchmarkallinone/outputs/report_priority_20/run_f2958f3118292117/datasets/cmm_math/samples/prob_fef79efed09d0ee1752224e4.json](../../datasets/cmm_math/samples/prob_fef79efed09d0ee1752224e4.json)
- 源数据集：`CMM-Math`
- 源 split：`train`
- 源题目 ID：`19873`
- 清洗路径：`text_lightweight`
- 是否文本主导：`True`
- 是否依赖图像：`False`
- 决策：`review`
- 决策原因码：`split_variant_needs_review`
- 开放化改写策略：`split_open`
- 对齐状态：`good`
- 可解性分数：`1.0`
- 可解性提示：`pass`
- 质量风险标记：`无`

### 采集阶段信号

```json
{
  "core_asset_completeness": {
    "has_question_text": true,
    "has_answer_text": true,
    "image_count": 0,
    "has_multiple_images": false
  },
  "initial_scores": {
    "initial_image_dependency_score": 0.28,
    "initial_multi_solution_score": 0.46,
    "initial_verifiability_score": 0.62
  }
}
```

### 1) 处理前：原始题目 / 原始答案

**原始题目**

```text
已知关于 $x$ 的不等式 $a x^{2}-x+b \geq 0$ 的解集为 $[-2,1]$, 则关于 $x$ 的不等式 $b x^{2}-x+a \leq 0$ 的解集为 ( )
```

**原始答案**

```text
$\left[-\frac{1}{2}, 1\right]$
```

### 2) 处理后：规范化题目 / 规范化答案

**规范化题目**

```text
已知关于 $x$ 的不等式 $a x^{2}-x+b \geq 0$ 的解集为 $[-2,1]$, 则关于 $x$ 的不等式 $b x^{2}-x+a \leq 0$ 的解集为 ( )
```

**规范化答案**

```text
$\left[-\frac{1}{2}, 1\right]$
```

### 3) 开放化改写前后

**改写前（使用规范化题目作为输入）**

```text
已知关于 $x$ 的不等式 $a x^{2}-x+b \geq 0$ 的解集为 $[-2,1]$, 则关于 $x$ 的不等式 $b x^{2}-x+a \leq 0$ 的解集为 ( )
```

**改写后（开放题变体）**

```text
已知关于 $x$ 的不等式 $a x^{2}-x+b \geq 0$ 的解集为 $[-2,1]$, 则关于 $x$ 的不等式 $b x^{2}-x+a \leq 0$ 的解集为 ( )
请只回答第 1 个目标量。
```

- 期望答案类型：`short_text`
- 期望答案：`$\left[-\frac{1}{2}, 1\right]$`
- 改写 rationale：`Compound choice answer was split into multiple open-ended targets.`
- 丢弃原因码：`无`

### 4) 图像与可视化产物

- 原始图像来源：无
- 持久化主图：无
- ROI 裁剪图：无

### 5) 清洗判定证据

```json
{
  "clean_score": 0.8439,
  "decision": "review",
  "decision_reason_codes": [
    "split_variant_needs_review"
  ],
  "alignment_summary": {
    "alignment_id": "align_c515da8f7895eca7cc9f652b",
    "coverage_score": 1.0,
    "consistency_score": 1.0,
    "alignment_status": "good",
    "conflict_count": 0
  },
  "solvability_summary": {
    "solvability_id": "solv_prob_fef79efed09d0ee1752224e4",
    "solvability_score": 1.0,
    "reasoning_path_exists": true,
    "decision_hint": "pass",
    "failure_codes": []
  },
  "missing_field_summary": {
    "missing_question_text": false,
    "missing_answer_text": false,
    "missing_image_count": 0
  },
  "risk_flags": [],
  "reject_record": null
}
```

