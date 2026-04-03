# PhysReason 批跑中 fallback 批次异常说明

## 背景

在 `PhysReason` 的 `0:300`、每批 20 条批跑过程中，发现部分批次并未正常使用 LLM 完成判定，而是在上游模型服务异常时退回到了 fallback 路径。

相关总任务：
- launcher: `scripts/physreason_batch_launcher.py`
- 输出根目录：`outputs/physreason_batched_eval`

---

## 异常批次范围

目前明确识别为 fallback 异常批次的范围：

- `0180_0200`
- `0200_0220`
- `0220_0240`
- `0240_0260`

建议后续作为一个连续区间统一处理：

- **重跑范围：`0180:0260`**

---

## 识别依据

这些批次的 `datasets/physreason/summary.json` 显示出非常一致的异常模式：

### 共同特征

- `successful_request_count = 0`
- `failed_request_count = 360`
- `retry_count = 240`
- `last_error = HTTP 502 Bad Gateway`

这说明：

- 该批次中所有 LLM 请求都没有成功
- pipeline 发起了大量重试
- 但上游服务持续不可用

---

## 样本级证据

在这些异常批次中抽查样本，`problem_main_record` 中出现：

- `agent_decision_source = fallback`

同时常伴随：

- `agent_completeness_status = complete`
- `agent_image_support_status = clear_enough`
- `agent_joint_understanding_status = understandable`

这表示：

- 样本不是空结果
- 系统在 LLM 不可用时，改由 fallback/启发式规则继续给出判定

---

## fallback 的实际含义

这里的 fallback 更接近：

> 当 LLM 推理链不可用时，系统基于题面完整性、图像支持情况、对齐状态、可解性等已有信号进行保守决策。

因此这些批次仍然会产生：

- `pass`
- `review`
- `reject`

但其可信度不应等同于正常使用 LLM 完成的批次。

---

## 影响评估

### 不影响

- 批任务继续推进
- 样本文件、summary、records 的落盘完整性
- 后续定位异常区间

### 会影响

- 该区间样本的质量置信度
- 与正常 LLM 批次的可比性
- 最终合并结果的可靠性

因此，`0180:0260` 不建议直接混入正式最终结果，而应优先重跑。

---

## 当前判断

这不是数据源本身坏掉，也不是样本天然不可用。

更准确地说，这是：

> 上游模型服务在该时间窗口内出现 502，导致整批请求失败，pipeline 被迫退回 fallback 路径。

所以这是一次**推理服务异常导致的批次级质量风险**，而不是样本级脏数据问题。

---

## 处理建议

### 建议方案

在 `0:300` 全部跑完后：

1. 保留当前批跑产物，作为异常证据
2. 单独重跑以下区间：
   - `0180:0200`
   - `0200:0220`
   - `0220:0240`
   - `0240:0260`
3. 用重跑结果替换 fallback 批次
4. 再进行最终合并与上传

### 推荐操作口径

- 将 `0180:0260` 标记为 **fallback 异常区间**
- 在最终汇总文档中注明该区间曾发生 502 / fallback
- 最终 merge 时优先使用重跑结果，而不是当前 fallback 结果

---

## 备注

当前已观察到的典型 fallback 样本并不意味着题目本身错误。例如有些样本仍表现为：

- `solvability_score = 1.0`
- `alignment_status = good/risky`
- `rewrite_strategy = keep_open`

这说明 fallback 可以产出“看起来合理”的结果，但由于缺失正常 LLM 推理支持，仍应视为异常批次并重跑。
