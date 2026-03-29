# 200 样本候选数据集远程基准测试报告（新主线复跑）

_日期：2026-03-26_

## 运行信息

- 配置：`configs/candidate_200_remote.yaml`
- 输出：`outputs/candidate_200_remote/run_1dbbbab6d8b51fd6/summary.json`
- 规模：10 个数据集 × 每个 20 个样本 = 200 个请求样本
- 运行说明：本轮在切换到 `benchmarkallinone` 主线实现后复跑，并显式带上本地代理访问 Hugging Face

## 总体结果

- Pass：**63**
- Review：**49**
- Reject：**88**

### 可用性口径

- **严格可用（只算 pass）**：63 / 200 = **31.5%**
- **宽松可用（pass + review）**：112 / 200 = **56.0%**

---

## 按数据集统计

| 数据集 | 学科 | Requested | Processed | Pass | Review | Reject | 严格可用 | 宽松可用 | 主要 rewrite 分布 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| SCEMQA | science | 20 | 20 | 2 | 0 | 18 | 10.0% | 10.0% | `blank_open:11`, `split_open:9` |
| Geometry3K | math | 20 | 20 | 2 | 1 | 17 | 10.0% | 15.0% | `blank_open:10`, `keep_open:10` |
| CMM-Math | math | 20 | 20 | 13 | 6 | 1 | 65.0% | 95.0% | `split_open:7`, `blank_open:13` |
| MathVision | math | 20 | 20 | 11 | 3 | 6 | 55.0% | 70.0% | `keep_open:13`, `blank_open:6`, `split_open:1` |
| MM-Math | math | 20 | 20 | 0 | 10 | 10 | 0.0% | 50.0% | `keep_open:20` |
| SeePhys | physics | 20 | 20 | 3 | 1 | 16 | 15.0% | 20.0% | `keep_open:20` |
| Multi-Physics | physics | 20 | 20 | 10 | 0 | 10 | 50.0% | 50.0% | `keep_open:20` |
| PhysReason | physics | 20 | 20 | 4 | 11 | 5 | 20.0% | 75.0% | `keep_open:20` |
| EEE-Bench | engineering | 20 | 20 | 12 | 6 | 2 | 60.0% | 90.0% | `blank_open:8`, `keep_open:8`, `split_open:3`, `drop_image_index:1` |
| EMMA-Physics | physics | 20 | 20 | 6 | 11 | 3 | 30.0% | 85.0% | `blank_open:11`, `split_open:9` |

---

## 按学科聚合

| 学科 | 数据集数 | Processed | Pass | Review | Reject | 严格可用 | 宽松可用 |
|---|---:|---:|---:|---:|---:|---:|---:|
| science | 1 | 20 | 2 | 0 | 18 | 10.0% | 10.0% |
| math | 4 | 80 | 26 | 20 | 34 | 32.5% | 57.5% |
| physics | 4 | 80 | 23 | 23 | 34 | 28.75% | 57.5% |
| engineering | 1 | 20 | 12 | 6 | 2 | 60.0% | 90.0% |

---

## 快速结论

### 当前表现最强的数据集（按严格可用率）
- **CMM-Math**：65.0%
- **EEE-Bench**：60.0%
- **MathVision**：55.0%
- **Multi-Physics**：50.0%

### 当前最有潜力的数据集（按宽松可用率）
- **CMM-Math**：95.0%
- **EEE-Bench**：90.0%
- **EMMA-Physics**：85.0%
- **PhysReason**：75.0%
- **MathVision**：70.0%

### 当前高 reject / 需要重点检查的数据集
- **SCEMQA**：10.0% strict / 10.0% lenient
- **Geometry3K**：10.0% strict / 15.0% lenient
- **SeePhys**：15.0% strict / 20.0% lenient
- **MM-Math**：0.0% strict / 50.0% lenient

---

## 与 README 中旧 200 样本 benchmark 的差异分析

README 中记录的旧 200 样本 benchmark（`run_6be16173d2403a7e`）结果为：

- Pass：**90**
- Review：**26**
- Reject：**84**
- **严格可用**：45.0%
- **宽松可用**：58.0%

本轮新主线复跑结果为：

- Pass：**63**
- Review：**49**
- Reject：**88**
- **严格可用**：31.5%
- **宽松可用**：56.0%

### 1) 总体变化

| 指标 | 旧结果 | 新结果 | 变化 |
|---|---:|---:|---:|
| Pass | 90 | 63 | **-27** |
| Review | 26 | 49 | **+23** |
| Reject | 84 | 88 | **+4** |
| 严格可用率 | 45.0% | 31.5% | **-13.5pt** |
| 宽松可用率 | 58.0% | 56.0% | **-2.0pt** |

### 2) 解读

这次最明显的变化不是“整体不可用”，而是：

- **Pass 明显下降**
- **Review 明显上升**
- **Reject 只小幅上升**

这意味着新主线更像是：

- 对不少原本会直接判为 `pass` 的样本，改成了更保守的 `review`
- 不是大面积把样本直接打废
- 因此**宽松可用率只从 58.0% 降到 56.0%**，变化不大

换句话说，新主线当前更保守，主要影响的是严格可用口径，而不是整体保留率。

### 3) 数据集层面的主要变化

#### 基本仍然稳定较强
- **CMM-Math**：仍然很强，说明其结构化改写与清洗链路比较稳
- **EEE-Bench**：依然是强正对照数据集
- **MathVision**：仍然处于“可用且值得继续优化”的区间

#### review 增多、值得细查的
- **PhysReason**：从之前更高的 strict 表现转成了 `review` 偏多，说明门控可能更谨慎了
- **EMMA-Physics**：宽松可用依旧高，但 `review` 多，适合继续调 threshold / prompt
- **MM-Math**：从旧结果里的 10 pass / 10 reject，变成 0 pass / 10 review / 10 reject，说明新主线对这类样本的判定明显保守了

#### 仍然偏弱或高 reject 的
- **SCEMQA**
- **Geometry3K**
- **SeePhys**

这几类数据集在旧结果里就不算强，这次仍然高 reject，说明问题并不是偶然波动，而是稳定存在。

### 4) 当前阶段判断

这次复跑说明：

1. **新主线已经能稳定复现完整 200 样本 benchmark**，替换后的主线具备继续迭代价值。
2. **宽松可用率基本稳定**，说明主线替换没有把整体样本保留能力打崩。
3. **严格可用率下降明显**，当前优先问题不是“接入失败”，而是：
   - gate / clean score 是否更保守
   - prompt 输出是否更倾向 `review`
   - 哪些 source-specific prompt 或判定规则需要放宽或重写

---

## 当前阶段意味着什么

1. 现阶段主问题已经不是“主线能不能跑通”，而是：
   - 高 reject 数据集为什么持续偏弱
   - review 偏多的数据集是否被过度保守处理
2. 新主线已经可以作为 `main` 版本继续推进，但下一步应集中在：
   - 高 reject 数据集检查
   - prompt 调整
   - source-specific 阈值与 rewrite-policy 优化

---

## 下次计划

### 1) 检查高 reject 数据集
优先抽查以下数据集的 `reject_records` / `problem_main_records`：
- `SCEMQA`
- `Geometry3K`
- `SeePhys`
- `MM-Math`

重点看：
- 是否存在明显误杀
- 是图像质量、文本完整性、图文对齐还是 rewrite/gate 导致 reject
- 哪些 reject 模式是 source-specific 的稳定问题

### 2) 修改 prompt
优先检查和调整：
- `prompts/extract_unified_sample.md`
- `prompts/collection/asset_registry.md`
- `prompts/collection/potential_scorer.md`
- `prompts/collection/candidate_registrar.md`

重点目标：
- 减少本应 `pass` 的样本被推到 `review`
- 降低高 reject 数据集上的保守偏差
- 让 source-specific 的题型判断与 rewrite-policy 更贴合真实分布

### 3) 继续做小规模人工抽样校准
针对：
- `SCEMQA`
- `Geometry3K`
- `MM-Math`
- `PhysReason`
- `EMMA-Physics`

按题型与 rewrite 策略分层抽样，检查：
- `pass/review/reject` 是否符合人工判断
- prompt 调整后是否能提升 strict usable
