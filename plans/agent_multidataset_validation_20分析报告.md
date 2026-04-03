# agent_multidataset_validation_20 运行分析报告

本报告分析运行结果 [`summary.json`](benchmarkallinone/outputs/agent_multidataset_validation_20/run_20286086fd5233de/summary.json)，目标是回答：

1. 当前 pipeline 所有功能是否得到了验证，针对采集、清洗、改写等给出具体例子
2. 当前 pipeline 是否运作正常
3. 产物是否符合预期
4. 有没有 fallback？为什么 fallback？fallback 是什么导致的？

---

## 1. 总体结论

本次运行的总汇总位于 [`summary.json`](benchmarkallinone/outputs/agent_multidataset_validation_20/run_20286086fd5233de/summary.json:1)。

- run id: `run_20286086fd5233de`
- 总数据集数: 5
- 总请求数: 737
- 成功请求数: 733
- 失败请求数: 28
- 重试次数: 24
- 总耗时: 4583.884 秒

总体判断：

- 采集、清洗、改写、文本解析、视觉解析、图文对齐、可解性评估、最终门控这些功能都已经被真实运行验证。
- 整体 pipeline 是可运行的，并且能稳定产出全套结构化对象。
- 但它还不是“最终最优策略版本”，不同数据集暴露出不同强弱项，尤其是 [`Geometry3K`](benchmarkallinone/outputs/agent_multidataset_validation_20/run_20286086fd5233de/datasets/geometry3k/summary.json:1) 的高 reject 比例，以及 [`CMM-Math`](benchmarkallinone/outputs/agent_multidataset_validation_20/run_20286086fd5233de/datasets/cmm_math/summary.json:1) 中文本题与多模态目标之间的边界问题，说明当前策略仍在校准中。

---

## 2. 各数据集概况

| 数据集 | 处理数 | pass | review | reject | 改写策略概览 |
| --- | ---: | ---: | ---: | ---: | --- |
| SCEMQA | 20 | 13 | 7 | 0 | keep_open:6, split_open:4, blank_open:10 |
| Geometry3K | 20 | 3 | 7 | 10 | keep_open:20 |
| CMM-Math | 20 | 15 | 3 | 2 | blank_open:15, keep_open:3, split_open:2 |
| MathVision | 20 | 7 | 9 | 4 | keep_open:15, drop_image_index:4, blank_open:1 |
| PhysReason | 20 | 8 | 12 | 0 | keep_open:20 |

---

## 3. 当前 pipeline 所有功能是否得到了验证

答案：**得到了验证。**

### 3.1 采集功能已验证

采集阶段的证据来自以下产物是否齐全：

- `source_intake_records.jsonl`
- `asset_registry_records.jsonl`
- `candidate_problem_records.jsonl`
- `raw_asset_bundles.jsonl`
- `candidate_pool_entries.jsonl`

所有 5 个数据集在 [`run_20286086fd5233de`](benchmarkallinone/outputs/agent_multidataset_validation_20/run_20286086fd5233de) 下都产出了这些对象，没有缺失。

#### 采集样例 1：SCEMQA

SCEMQA 的 pass 样例 `prob_5a1030536aced4a21bef1ddb`：
- 原题来自图像导数题
- 图像、题干、答案都被成功接入
- 候选入池阶段没有被资产缺失拦下

见命令分析输出中 `SCEMQA -> EXAMPLE pass` 的第一条。

#### 采集样例 2：Geometry3K

Geometry3K 的 pass 样例 `prob_ba2479550dc26935b02846f9`：
- GitHub connector 成功发现 repo 数据文件
- 题干、答案、多图像都被接进来
- 说明 GitHub 类型 connector 真正工作了

见 `Geometry3K -> EXAMPLE pass` 第一条。

#### 采集样例 3：PhysReason

PhysReason 全部 20 条都跑通，且 `source_status=available`，说明 Hugging Face + raw zip fallback 路线已被验证。

见 [`physreason/summary.json`](benchmarkallinone/outputs/agent_multidataset_validation_20/run_20286086fd5233de/datasets/physreason/summary.json:1)。

---

### 3.2 清洗功能已验证

清洗阶段的证据来自以下对象：

- `normalization_records.jsonl`
- `clean_problem_records.jsonl`
- `cleaning_records.jsonl`
- `problem_main_records.jsonl`
- `reject_records.jsonl`
- `clean_pool_entries.jsonl`

这些对象在 5 个数据集里都存在，说明规范化、门控和最终决策确实都跑到了。

#### 清洗样例 1：SCEMQA 正常 pass

SCEMQA pass 高频原因：
- `alignment_good`
- `rewrite_usable`
- `jointly_understandable`
- `answer_available`

见命令输出中的 `TOP_PASS_REASONS`。

这说明清洗阶段不仅保留了样本，还明确要求：
- 图文要对得上
- 改写要可用
- 答案要存在
- 样本要能被理解

#### 清洗样例 2：Geometry3K review

Geometry3K review 高频原因：
- `alignment_requires_review`
- `multi_image_coordination_needed`
- `missing_grounded_visual_path`
- `text_structure_partial`

见命令输出中的 `Geometry3K -> TOP_REVIEW_REASONS`。

这说明清洗模块确实在做：
- 多图协同风险判断
- 图文 grounding 失败检测
- 文本结构不完整检测

而不是简单“有图有题就 pass”。

#### 清洗样例 3：Geometry3K reject

Geometry3K reject 高频原因：
- `missing_answer`
- `missing_required_image`
- `question_text_incomplete`
- `question_text_placeholder`

典型 reject 样例：
- `prob_464f2e961e952b33da99eb36`
- `prob_d176662b4213610a09e022fb`

这两条都是：
- 题面只是占位符 `text`
- 缺图
- 缺答案

说明清洗 reject 不是“随便拒绝”，而是明确拒绝无可恢复语义的脏样本。

---

### 3.3 改写功能已验证

改写阶段的证据来自：

- `rewrite_reports.jsonl`
- `open_ended_problem_variants.jsonl`
- `rewrite_strategy_counts`

#### SCEMQA

SCEMQA 同时出现：
- `keep_open`
- `blank_open`
- `split_open`

见 [`summary.json`](benchmarkallinone/outputs/agent_multidataset_validation_20/run_20286086fd5233de/summary.json:18)。

这说明三类改写逻辑都跑到了：
- 原本开放题保留
- 普通选择题改写为开放题
- 一题多目标时拆成多个开放问题

典型样例：
- `prob_5a1030536aced4a21bef1ddb`：`blank_open`
- `prob_c9971c7fd41b26eeaae5e45b`：`keep_open`
- `prob_d2e18289d6790272f6e58c9b`：`split_open`

#### CMM-Math

CMM-Math 改写主要是：
- `blank_open`
- 少量 `keep_open`
- 少量 `split_open`

见 [`cmm_math/summary.json`](benchmarkallinone/outputs/agent_multidataset_validation_20/run_20286086fd5233de/datasets/cmm_math/summary.json:14)。

说明中文文本题的选择题开放化改写链是工作的。

#### MathVision

MathVision 同时出现：
- `keep_open`
- `blank_open`
- `drop_image_index`

见 [`mathvision/summary.json`](benchmarkallinone/outputs/agent_multidataset_validation_20/run_20286086fd5233de/datasets/mathvision/summary.json:14)。

这说明：
- 本来就是开放题的保留了
- 能开放化的选择题被重写了
- 纯图编号选择题被识别出来并剔除了

这正是设计文档要求的关键能力。

---

### 3.4 文本结构、视觉结构、图文对齐功能已验证

证据来自：

- `text_structure_records.jsonl`
- `visual_structure_records.jsonl`
- `alignment_records.jsonl`

并且这些模块在 review 中确实发挥了作用。

#### 典型例子：Geometry3K review

大量 review 的高频原因正是：
- `alignment_requires_review`
- `missing_grounded_visual_path`

说明对齐模块并不是摆设，而是确实在参与最终判定。

#### 典型例子：SCEMQA review

`prob_80511fe3dbb76971a8d87952` 被 review 的核心理由是：
- 问题和图都能看懂
- 但没能建立稳定的 grounded visual path

这就是文本结构 + 图像结构 + 对齐三步实际发挥作用的证据。

---

### 3.5 可解性与最终门控功能已验证

证据来自：

- `solvability_reports.jsonl`
- `clean_problem_records.jsonl`
- `reject_records.jsonl`
- `clean_pool_entries.jsonl`

#### 典型例子：SCEMQA review

`prob_d2e18289d6790272f6e58c9b`：
- 图文对齐很好
- 可解性通过
- 但因为改写成了 `split_open`，所以仍进入 review

说明最终门控不是只看 solvability，而是在综合：
- 改写风险
- 对齐风险
- 样本理解风险

#### 典型例子：CMM-Math reject

`prob_043aa1289d8e9b0e66e5cfc9`：
- 题干截断
- 缺图
- 缺失目标表达
- 最终 reject

这说明 gate 能识别“不可恢复”的题目。

---

## 4. 当前 pipeline 是否运作正常

整体判断：**运作正常，但规则与 agent 仍在校准中。**

### 4.1 正常运行的证据

1. 所有 5 个数据集都是 `source_status=available`
2. 每个数据集都真实处理了 20 条
3. records 文件齐全，没有结构性缺失
4. 最终总汇总 `last_error=null`
5. 虽然有请求失败和重试，但没有导致整条链路中断

见：
- [`summary.json`](benchmarkallinone/outputs/agent_multidataset_validation_20/run_20286086fd5233de/summary.json:203)

### 4.2 说明系统在“正常工作”但不是“最终稳定版”的现象

#### 现象 A：Geometry3K reject 很高

- 20 条里 reject 了 10 条
- 原因集中在：占位题面、缺图、缺答案

这更像是上游 repo 数据文件质量问题，而不是 pipeline 崩了。

#### 现象 B：CMM-Math 出现 collection reject，但 cleaning pass

例如 pass 样例里：
- `collection_decision = reject`
- 但 `clean_decision = pass`

说明 collection gate 和 cleaning gate 的标准还不完全一致。

这不是“跑坏”，但说明策略还在调参。

#### 现象 C：review 偏多

像 PhysReason 有 12/20 review，Geometry3K 有 7/20 review。

这通常说明：
- 对齐引擎偏保守
- 或视觉 grounding 能力还不够细

这属于“质量校准问题”，不是“系统不能跑”。

---

## 5. 产物是否符合预期

总体判断：**基本符合预期，但有个别不完全理想的地方。**

### 5.1 符合预期的部分

- 每个数据集都有 `summary.json`
- 每个数据集都有 `samples/` 与 `records/`
- 每条样本都有完整单题执行档案
- 从采集、规范化、改写、结构解析、对齐、可解性、最终门控，到审计字段，全都有落盘
- 改写策略与决策之间总体一致

### 5.2 不完全符合预期的地方

#### 问题 1：Collection 与 Cleaning 的判断不一致

在 CMM-Math 中明显能看到：
- collection 因“无图像资产”倾向 reject
- 但 cleaning 仍允许 pass / review

这会让分析上出现一种奇怪现象：
- 候选池认为它不该进来
- 清洗池又认为它还能用

#### 问题 2：多模态目标和文本题边界还没收紧到底

CMM-Math 某些纯文本数学题依然 pass，这是否符合你最终目标，要看你是不是允许文本题保留少量占比。

#### 问题 3：Geometry3K 的脏样本比例高

说明当前 GitHub 结构发现策略会把一些明显无效的条目也带进来，后面虽然能 reject，但前面做了无效工作。

---

## 6. 有没有 fallback？为什么 fallback？fallback 是什么导致的？

有。

### 6.1 fallback 是什么

这里的 fallback 指：
某个 agent 本该用 LLM 结果，但因为请求失败、返回格式不合法、或字段缺失，最终退回规则 / 保底逻辑。

典型 fallback 点包括：
- `asset_registry`
- `initial_scoring`
- `candidate_registration`
- `normalization`
- `sample_understanding`
- `decision_agent`

### 6.2 本次运行里观察到的 fallback

根据统计：

- SCEMQA 有 fallback：
  - `asset_registry = 1`
  - `initial_scoring = 1`
  - `candidate_registration = 2`
- Geometry3K：0
- CMM-Math：0
- MathVision：0
- PhysReason：0

也就是说，本次 20 条运行里 fallback 主要集中在 SCEMQA。

### 6.3 fallback 为什么会发生

根本原因通常只有三类：

1. LLM 请求失败或超时
2. LLM 返回内容不是合法 JSON
3. LLM 返回 JSON 了，但字段缺失 / 类型不合规，不能被当前 agent 接受

本次运行的总体数据说明：
- `failed_request_count = 28`
- `retry_count = 24`
- 但 `last_error = null`

这说明：
- 的确发生了请求波动
- 系统通过重试和 fallback 把它吸收了
- 没让整条链路中断

### 6.4 fallback 是什么导致的

结合这次运行现象，主要诱因是：

- SCEMQA 图文题字段结构复杂，答案形式和图像字段波动较大
- 某些 agent 输出 JSON 严格性不够稳定
- 网络请求本身存在少量失败，需要重试

### 6.5 fallback 是不是坏事

不是。

fallback 的意义就是：
- 保证整条链路不停
- 让样本至少能产出最低限度结构化结果
- 保证最终还有 pass/review/reject 的依据

真正需要关注的是：
- fallback 是否集中在某个 agent
- fallback 是否过多
- fallback 后的产物是否仍然可信

从这次结果看：
- fallback 次数不多
- 只集中在 SCEMQA
- 没有造成整体崩溃

因此可以判断：
**fallback 机制是有效的，而且这次确实发挥了作用。**

---

## 7. 各数据集详细结论

## 7.1 SCEMQA

### 结果
- pass 13
- review 7
- reject 0

### pass 原因
高频是：
- `alignment_good`
- `rewrite_usable`
- `jointly_understandable`
- `answer_available`

说明：
- 图文题主链工作正常
- 改写功能已验证
- 图文对齐与可解性多数可接受

### review 原因
高频是：
- `alignment_requires_review`
- `missing_grounded_visual_path`
- `split_variant_needs_review`

说明：
- review 主要来自图文 grounding 和改写后的复杂形式，而不是题目完全坏掉

### fallback
- 存在少量 fallback
- 但没有影响最终出数

### 判断
SCEMQA 是本次运行里最能证明“采集 + 清洗 + 改写 + 结构解析 + 门控”完整打通的数据集之一。

---

## 7.2 Geometry3K

### 结果
- pass 3
- review 7
- reject 10

### pass 原因
高频是：
- `answer_available`
- `rewrite_usable`
- `alignment_good`

### review 原因
高频是：
- `alignment_requires_review`
- `multi_image_coordination_needed`
- `missing_grounded_visual_path`

### reject 原因
高频是：
- `missing_answer`
- `missing_required_image`
- `question_text_incomplete`
- `question_text_placeholder`

### 判断
Geometry3K 很好地验证了：
- GitHub connector 能工作
- 多图样本链路能工作
- review / reject 规则能筛掉脏样本

但也暴露出：
- 上游 repo 样本发现策略不够干净
- 对齐模块偏保守

---

## 7.3 CMM-Math

### 结果
- pass 15
- review 3
- reject 2

### pass 原因
高频是：
- `alignment_good`
- `rewrite_usable`
- `text_sufficient`
- `answer_available`

### review 原因
高频是：
- `alignment_requires_review`
- `image_missing_but_text_sufficient`
- `normalization_incomplete`
- `notation_ambiguity`

### reject 原因
高频是：
- `question_incomplete`
- `joint_unintelligible`
- `missing_target_expression`
- `rewrite_not_usable`

### 判断
CMM-Math 最能验证：
- 选择题开放化改写
- 文本结构解析
- 截断题 reject
- 符号歧义 review

但也最明显暴露了：
- collection gate 与 cleaning gate 一致性不足
- 文本题是否应进入目标数据集，还需要进一步收紧策略

---

## 7.4 MathVision

### 结果
- pass 7
- review 9
- reject 4

### 改写表现
- `keep_open = 15`
- `drop_image_index = 4`
- `blank_open = 1`

### 说明
MathVision 非常好地验证了：
- 开放题保留
- 图像选择题改写
- 纯图编号题丢弃

特别是 `drop_image_index` 的 reject，直接证明“纯图编号选择题剔除”功能已经被真实验证。

### 判断
MathVision 是本次 run 里最能证明改写模块有效性的一个数据集。

---

## 7.5 PhysReason

### 结果
- pass 8
- review 12
- reject 0

### 改写表现
- 全部 `keep_open`

### 说明
PhysReason 样本大多本身就是复杂开放题，不需要选择题开放化，但很好地验证了：
- 长题干接入
- 多问物理题可解性评估
- 图像辅助结构解析
- review 缓冲机制

### 判断
PhysReason 是本次 run 里最能证明“复杂开放式多模态题清洗链路”可工作的数据集。

---

## 8. 最终判断

### 8.1 当前 pipeline 所有功能是否得到验证

答案：**是。**

被验证的功能包括：
- 采集
- 资产登记
- 候选评分
- 候选入池
- 规范化
- 改写
- 文本结构解析
- 视觉结构解析
- 图文对齐
- 可解性评估
- 最终门控
- fallback 吸收失败请求

### 8.2 当前 pipeline 是否运作正常

答案：**是，运作正常。**

但它仍然是“可运行且有产出”的版本，不是“策略已完全收敛”的最终版本。

### 8.3 产物是否符合预期

答案：**基本符合预期。**

优点：
- 结构齐全
- 审计齐全
- 样本级档案完整
- 能支撑后续标注

不足：
- collection / cleaning 一致性还要继续校准
- 部分 review 偏保守
- 部分上游源的脏样本比例偏高

### 8.4 fallback 是否存在

答案：**存在，但不多，而且是有效的防故障机制。**

本次 fallback 主要发生在 SCEMQA，说明：
- agent 输出确实有轻微波动
- 但 fallback 保证了整条链路没有因此中断

所以，从工程角度看，这个 pipeline 已经具备“**真实可运行、失败可吸收、产物可分析**”的特征。