# 200 样本候选数据集远程基准测试报告

_日期：2026-03-24_

## 运行信息

- 配置：`configs/candidate_200_remote.yaml`
- 输出：`outputs/candidate_200_remote/run_6be16173d2403a7e/summary.json`
- 规模：10 个数据集 × 每个 20 个样本 = 200 个请求样本

## 耗时

- 总耗时：**195 秒**
- Requested samples：**200**
- Processed samples：**200**
- 平均每个 processed sample 的 wall-clock 时间：**0.975 秒 / 样本**

## 总体结果

- Pass：**90**
- Review：**26**
- Reject：**84**

### 可用性口径

- **严格可用（只算 pass）**：90 / 200 = **45.0%**
- **宽松可用（pass + review）**：116 / 200 = **58.0%**

---

## 按数据集统计

| 数据集 | 学科 | Requested | Processed | Pass | Review | Reject | 严格可用 | 宽松可用 | 主要 rewrite 分布 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| SCEMQA | science | 20 | 20 | 3 | 0 | 17 | 15.0% | 15.0% | `blank_open:11`, `split_open:9` |
| Geometry3K | math | 20 | 20 | 0 | 4 | 16 | 0.0% | 20.0% | `blank_open:10`, `candidate_reject:10` |
| CMM-Math | math | 20 | 20 | 13 | 6 | 1 | 65.0% | 95.0% | `blank_open:13`, `split_open:7` |
| MathVision | math | 20 | 20 | 11 | 3 | 6 | 55.0% | 70.0% | `keep_open:13`, `blank_open:6`, `split_open:1` |
| MM-Math | math | 20 | 20 | 10 | 0 | 10 | 50.0% | 50.0% | `keep_open:20` |
| SeePhys | physics | 20 | 20 | 4 | 0 | 16 | 20.0% | 20.0% | `keep_open:20` |
| Multi-Physics | physics | 20 | 20 | 11 | 0 | 9 | 55.0% | 55.0% | `keep_open:20` |
| PhysReason | physics | 20 | 20 | 15 | 0 | 5 | 75.0% | 75.0% | `keep_open:20` |
| EEE-Bench | engineering | 20 | 20 | 15 | 4 | 1 | 75.0% | 95.0% | `blank_open:8`, `keep_open:8`, `split_open:3`, `drop_image_index:1` |
| EMMA-Physics | physics | 20 | 20 | 8 | 9 | 3 | 40.0% | 85.0% | `blank_open:11`, `split_open:9` |

---

## 按学科聚合

| 学科 | 数据集数 | Processed | Pass | Review | Reject | 严格可用 | 宽松可用 |
|---|---:|---:|---:|---:|---:|---:|---:|
| science | 1 | 20 | 3 | 0 | 17 | 15.0% | 15.0% |
| math | 4 | 80 | 34 | 13 | 33 | 42.5% | 58.75% |
| physics | 4 | 80 | 38 | 9 | 33 | 47.5% | 58.75% |
| engineering | 1 | 20 | 15 | 4 | 1 | 75.0% | 95.0% |

---

## 快速结论

### 当前表现最强的数据集（按严格可用率）
- **PhysReason**：75.0%
- **EEE-Bench**：75.0%
- **CMM-Math**：65.0%
- **MathVision**：55.0%
- **Multi-Physics**：55.0%
- **MM-Math**：50.0%

### 当前最有潜力的数据集（按宽松可用率）
- **EEE-Bench**：95.0%
- **CMM-Math**：95.0%
- **EMMA-Physics**：85.0%
- **PhysReason**：75.0%
- **MathVision**：70.0%

### 当前默认阈值下最弱的几个数据集
- **SCEMQA**：15.0% strict / 15.0% lenient
- **Geometry3K**：0.0% strict / 20.0% lenient
- **SeePhys**：20.0% strict / 20.0% lenient

---

## 本轮运行中的 rewrite 分布观察

### 以 `keep_open` 为主
- `MM-Math`
- `SeePhys`
- `Multi-Physics`
- `PhysReason`
- `MathVision` 的大部分样本

这类数据集更像天然开放题、多步推理题，而不是标准单目标视觉选择题。

### 以 `blank_open` 为主
- `EEE-Bench`（但不是完全单一）
- `SCEMQA` 的一部分
- `Geometry3K` 的一部分
- `MathVision` 的一部分

这类题更接近“标准视觉选择题 -> 开放题”的改写路径。

### 以 `split_open` 为主或占比较高
- `CMM-Math`
- `EMMA-Physics`
- `SCEMQA` 的一部分

这类题通常更像结构化目标、可拆分目标，或者本身就包含复合子目标。

---

## 当前阶段意味着什么

1. **连接器覆盖已经不是当前最主要的问题**，至少对当前可达的候选集来说是这样。
2. 现在更明显的瓶颈已经变成：**source-specific 质量阈值** 与 **rewrite-policy 分流**。
3. 单一 rewrite 路径不足以覆盖所有数据集。
4. 当前最适合作为正对照继续迭代的数据集是：
   - `EEE-Bench`
   - `PhysReason`
   - `CMM-Math`
5. 当前最可能需要做 source-specific 处理的数据集是：
   - `Geometry3K`
   - `SCEMQA`
   - `SeePhys`
   - `MathVision` 的部分样本

---

## 建议的下一步

优先做一轮 source-specific 的质量分析，重点看：
- `low_resolution`
- `low_text_completeness`
- candidate-intake reject 模式
- `Geometry3K`、`SCEMQA`、`SeePhys` 是否需要 threshold override

---

## 与之前 benchmark 的对比

这轮 200 样本 benchmark 最值得对比的两个历史参考是：

1. 更早的 **4 数据集 remote benchmark**（`geometry3k`、`cmm_math`、`mathvision`、`eee_bench`，每个 10 条）
2. 更早的 **all-candidate remote smoke**（每个数据集 2 条）

### A. 与更早的 4 数据集 remote benchmark 对比

更早的 4 数据集 benchmark 总计：
- processed：40
- pass：12
- review：12
- reject：16
- strict usable：**30.0%**
- lenient usable：**60.0%**

当前 200 样本 benchmark 总计：
- processed：200
- pass：90
- review：26
- reject：84
- strict usable：**45.0%**
- lenient usable：**58.0%**

#### 主要变化
- strict usable 从 **30.0% -> 45.0%**
- lenient usable 基本持平：**60.0% -> 58.0%**

#### 解读
这不应被看作退步。新的 benchmark 更大、覆盖更多数据集，而且包含连接器修复后的状态。它更接近真实分布：review 比例相对下降，但真正的 pass 和真正的 reject 更清晰了。

#### 对共享的 4 个数据集逐个看

- **Geometry3K**
  - 之前：`0 / 4 / 6`
  - 现在：`0 / 4 / 16`
  - 结论：偏弱不是小样本偶然，而是当前阈值下的稳定问题

- **CMM-Math**
  - 之前：`5 / 5 / 0`
  - 现在：`13 / 6 / 1`
  - 结论：依然非常强，而且比之前更像一个稳定的数学 benchmark 源

- **MathVision**
  - 之前：`0 / 0 / 10`
  - 现在：`11 / 3 / 6`
  - 结论：这是改进最大的一个；图像 materialization 修复后，它已经从“几乎不可用”变成“真实可用”

- **EEE-Bench**
  - 之前：`7 / 3 / 0`
  - 现在：`15 / 4 / 1`
  - 结论：依然是非常稳的正对照，样本放大后表现仍然稳定

### B. 与更早的 all-candidate smoke 对比

更早的 all-candidate smoke 总计：
- processed：22
- pass：8
- review：4
- reject：10
- strict usable：**36.4%**
- lenient usable：**54.5%**

当前 200 样本 benchmark 总计：
- processed：200
- pass：90
- review：26
- reject：84
- strict usable：**45.0%**
- lenient usable：**58.0%**

#### 主要变化
- strict usable 从 **36.4% -> 45.0%**
- lenient usable 从 **54.5% -> 58.0%**

#### 解读
更早的 smoke 更偏“连通性测试”；当前这轮 200 样本结果明显更能代表真实情况，因此更适合作为后续 rewrite 策略和 threshold 调整的参考基线。

### C. 经过 200 样本之后，哪些判断变得更确定了

这轮更大规模的 benchmark 强化了以下判断：

- `EEE-Bench` 仍然是很强的 engineering 正对照源
- `CMM-Math` 不是小样本偶然好，而是真的较强
- `MathVision` 在连接器修复后，已经真正进入“可用数据集”行列
- `PhysReason` 比最早的小样本 smoke 暗示的还要强
- `Geometry3K` 在当前阈值下确实偏弱
- `SeePhys` 比最早 2 样本 smoke 暗示的更弱
- `MM-Math` 虽然可用，但没有最早小样本看起来那么稳定
