# Pipeline2 PTK Repair On Cache 与环境变量修复说明

日期：2026-04-28

## 1. 背景

本轮 `ready` 五样本验证中，`tmp_ready_5samples_20260428_w5_rerun` 的主要问题分为两类：

1. `PhysReason` 在 `PTKFoundationGate` 连续 5 轮未过。
2. `EEE-Bench` 在 `PTKFoundationGate` 连续 5 轮未过。

此外，在后续修复验证时，又暴露出一类运行层问题：

3. 临时配置文件仍使用 `${OPENAI_API_KEY}`，而当前本地标注链路实际约定的是 `ANNOTATION_API_BASE_URL` / `ANNOTATION_API_KEY`。

这导致 repair 或 rerun 时，即使加载了 `pipeline2.local.env`，如果配置文件没有引用 `ANNOTATION_*` 变量，仍可能打到错误的认证路径，出现 `401 INVALID_API_KEY`。


## 2. 本次已完成修复

### 2.1 PTK T 层结构修复

已在 [src/benchmarkallinone/pipeline2/annotation_modules.py](/d:/Hallucination/workspace/agent-pipeline/src/benchmarkallinone/pipeline2/annotation_modules.py:247) 增加以下修复：

- 支持把 `Find: 1. ... 2. ... 3. ...` 解析成稳定的 `goal + subquestion` 结构。
- 过滤 `2`、`3`、`Find: 1` 这类编号碎片和坏 goal 片段。
- 避免同一 ask 同时以 `constraint` 和 `subquestion` 重复保留。
- 对 `In the circuit shown in the figure, the circuit is a` 这类截断分类题干，自动重建为可用的 `given + goal`。

### 2.2 针对性测试

已在 [src/benchmarkallinone/pipeline2/tests/test_annotation_modules.py](/d:/Hallucination/workspace/agent-pipeline/src/benchmarkallinone/pipeline2/tests/test_annotation_modules.py:266) 增加两条测试：

- 编号子问重建测试
- 截断分类题干修复测试

这两条新增测试已通过。

### 2.3 直接基于已有 cache 做 PTK repair 的入口

新增脚本：

- [run_pipeline2_repair_ptk_from_cache.py](/d:/Hallucination/workspace/agent-pipeline/run_pipeline2_repair_ptk_from_cache.py:1)

用途：

- 不重新经过 `MethodPlanner`
- 直接读取已有 `ptk_foundation_progress`
- 在旧 foundation 基础上继续做 PTK critic/polish repair

这个入口适合修 `PTKFoundationGate` 卡住的样本。


## 3. 已确认的 repair 机制行为

### 3.1 `resume-batch-id` 不是本次最合适的方式

`resume_annotation_pipeline()` 依赖 langgraph checkpoint。

如果某个 batch thread 已经结束，再调用 `--resume-batch-id`，更偏向“读取已有终态”，而不是“重新执行 repair”。

因此，对已经跑完但 PTK 没过的样本，不推荐把 `resume-batch-id` 当作 repair 入口。

### 3.2 正确的 cache repair 思路

对于已经存在的：

- `annotation_runtime/stage_cache/<batch_id>/<problem_id>/ptk_foundation_progress/*.json`

应优先采用两种方式之一：

1. 用 `run_pipeline2_repair_ptk_from_cache.py` 直接修单题。
2. 或者同 `batch_id` + 同 `output_root` + 新 `checkpoint_db_path` 全批重跑。

其中第一种更推荐，因为不会重新走 `MethodPlanner`。

### 3.3 5 轮失败后仍可继续 repair

`build_ptk_foundation()` 在读取旧 progress 时，如果发现：

- `passed = false`
- `pending_critique = null`
- `next_round_index > max_repair_rounds`

会自动把 repair 状态重置为新一轮继续修，而不是直接放弃。

因此旧的 `ptk_foundation_progress` 是可复用的，不需要手工删掉。


## 4. 环境变量约定

本地 pipeline2 标注链路应明确统一使用以下变量：

- `ANNOTATION_API_BASE_URL`
- `ANNOTATION_API_KEY`

当前本地环境文件位置：

- [src/benchmarkallinone/pipeline2/configs/pipeline2.local.env](/d:/Hallucination/workspace/agent-pipeline/src/benchmarkallinone/pipeline2/configs/pipeline2.local.env:1)

### 4.1 本次明确调整

以下临时配置文件已改为引用 `ANNOTATION_*` 变量，而不是 `${OPENAI_API_KEY}`：

- [pipeline2/configs/tmp_ready_5samples_20260428.yaml](/d:/Hallucination/workspace/agent-pipeline/pipeline2/configs/tmp_ready_5samples_20260428.yaml:1)
- [pipeline2/configs/tmp_ready_5samples_20260428_w5_fix1.yaml](/d:/Hallucination/workspace/agent-pipeline/pipeline2/configs/tmp_ready_5samples_20260428_w5_fix1.yaml:1)
- [pipeline2/configs/tmp_ready_5samples_20260428_w5_repair_on_cache.yaml](/d:/Hallucination/workspace/agent-pipeline/pipeline2/configs/tmp_ready_5samples_20260428_w5_repair_on_cache.yaml:1)

修复后，这些配置明确使用：

- `base_url: ${ANNOTATION_API_BASE_URL}`
- `api_key: ${ANNOTATION_API_KEY}`

### 4.2 当前 401 的解释

当前 repair 失败不是因为 repair 逻辑不生效，而是因为运行时对 endpoint 的认证返回：

- `HTTP 401`
- `INVALID_API_KEY`

也就是说，现在阻塞在外部认证，不阻塞在本地 repair 代码路径。


## 5. 推荐执行方式

### 5.1 直接修单题 PTK cache

示例：

```bash
python run_pipeline2_repair_ptk_from_cache.py \
  --config pipeline2/configs/tmp_ready_5samples_20260428_w5_repair_on_cache.yaml \
  --batch-id tmp_ready_5samples_20260428_w5_rerun \
  --problem-id prob_00b3397a2b9eb04954f73ecb \
  --max-repair-rounds 4
```

适合：

- `PhysReason`
- `EEE-Bench`

### 5.2 在已有 output_root 上全批 repair 重跑

注意：

- 保留原 `output_root`
- 保留原 `batch_id`
- 更换新的 `checkpoint_db_path`

这样 graph 会重新执行，但 `stage_cache` 会复用旧的 `ptk_foundation_progress`。


## 6. 本轮结论

### 6.1 逻辑层

本轮 PTK 失败的两个已知问题都已有针对性修复：

- `PhysReason`：多子问 T 层结构损坏
- `EEE-Bench`：截断题干导致 given/goal 不完整

### 6.2 运行层

当前需要明确统一：

- 使用 `ANNOTATION_API_BASE_URL`
- 使用 `ANNOTATION_API_KEY`

不要再把临时 pipeline2 配置写成 `${OPENAI_API_KEY}`，否则会再次出现 repair/rerun 与本地 env 约定不一致的问题。

### 6.3 下一步

在 API 认证恢复后，优先执行：

1. 先用 `run_pipeline2_repair_ptk_from_cache.py` 修 `PhysReason`
2. 再修 `EEE-Bench`
3. 如果两者通过，再考虑是否需要对整批做一次 cache-based repair rerun
