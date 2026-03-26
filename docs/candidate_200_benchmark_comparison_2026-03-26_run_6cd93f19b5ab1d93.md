# 200 样本候选数据集远程基准测试对比记录（再次复跑）

_日期：2026-03-26_

## 运行信息

- 配置：`configs/candidate_200_remote.yaml`
- 本轮输出：`outputs/candidate_200_remote/run_6cd93f19b5ab1d93/summary.json`
- 对比基线：`docs/candidate_200_benchmark_report_rerun_2026-03-26.md`
- 规模：10 个数据集 × 每个 20 个样本 = 200 个请求样本
- 备注：本轮后台日志未记录完整结束时间，因此这里不写精确 wall-clock 总耗时

## 本轮总体结果

- Pass：**61**
- Review：**48**
- Reject：**91**

### 可用性口径

- **严格可用（只算 pass）**：61 / 200 = **30.5%**
- **宽松可用（pass + review）**：109 / 200 = **54.5%**

---

## 与上一轮 2026-03-26 复跑结果对比

上一轮基线（`run_1dbbbab6d8b51fd6`）：

- Pass：**63**
- Review：**49**
- Reject：**88**
- **严格可用**：**31.5%**
- **宽松可用**：**56.0%**

本轮结果（`run_6cd93f19b5ab1d93`）：

- Pass：**61**
- Review：**48**
- Reject：**91**
- **严格可用**：**30.5%**
- **宽松可用**：**54.5%**

### 差值

| 指标 | 上一轮 | 本轮 | 变化 |
|---|---:|---:|---:|
| Pass | 63 | 61 | **-2** |
| Review | 49 | 48 | **-1** |
| Reject | 88 | 91 | **+3** |
| 严格可用率 | 31.5% | 30.5% | **-1.0pt** |
| 宽松可用率 | 56.0% | 54.5% | **-1.5pt** |

### 解读

- 本轮结果与上一轮非常接近，整体属于**小幅回落**，不是数量级变化。
- 主要变化是：
  - `pass` 小降
  - `review` 小降
  - `reject` 小升
- 因此严格和宽松可用率都比上一轮低一点，但总体仍处于同一性能区间。

---

## 本轮按数据集统计

| 数据集 | 学科 | Requested | Processed | Pass | Review | Reject | 严格可用 | 宽松可用 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| SCEMQA | science | 20 | 20 | 2 | 0 | 18 | 10.0% | 10.0% |
| Geometry3K | math | 20 | 20 | 0 | 0 | 20 | 0.0% | 0.0% |
| CMM-Math | math | 20 | 20 | 13 | 6 | 1 | 65.0% | 95.0% |
| MathVision | math | 20 | 20 | 11 | 3 | 6 | 55.0% | 70.0% |
| MM-Math | math | 20 | 20 | 0 | 10 | 10 | 0.0% | 50.0% |
| SeePhys | physics | 20 | 20 | 3 | 1 | 16 | 15.0% | 20.0% |
| Multi-Physics | physics | 20 | 20 | 10 | 0 | 10 | 50.0% | 50.0% |
| PhysReason | physics | 20 | 20 | 4 | 11 | 5 | 20.0% | 75.0% |
| EEE-Bench | engineering | 20 | 20 | 12 | 6 | 2 | 60.0% | 90.0% |
| EMMA-Physics | physics | 20 | 20 | 6 | 11 | 3 | 30.0% | 85.0% |

---

## 本轮快速结论

### 表现较强的数据集

- **CMM-Math**：65.0% strict / 95.0% lenient
- **EEE-Bench**：60.0% strict / 90.0% lenient
- **MathVision**：55.0% strict / 70.0% lenient
- **Multi-Physics**：50.0% strict / 50.0% lenient

### 高潜力但 review 偏多的数据集

- **EMMA-Physics**：30.0% strict / 85.0% lenient
- **PhysReason**：20.0% strict / 75.0% lenient
- **MM-Math**：0.0% strict / 50.0% lenient

### 当前最弱的数据集

- **Geometry3K**：0.0% strict / 0.0% lenient
- **SCEMQA**：10.0% strict / 10.0% lenient
- **SeePhys**：15.0% strict / 20.0% lenient

---

## 结论

这次再次复跑没有显示出明显改善，相比同日上一轮复跑结果略差一些，但差距不大。当前 200 样本基线可以暂时视为稳定落在：

- **严格可用率约 30%–31%**
- **宽松可用率约 54%–56%**

后续如果要继续优化，优先值得盯的数据集仍然是：

- `Geometry3K`
- `SCEMQA`
- `SeePhys`
- `MM-Math`（主要是 strict 过低）
