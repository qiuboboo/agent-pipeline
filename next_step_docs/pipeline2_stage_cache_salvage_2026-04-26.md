# Pipeline2 Stage Cache / Salvage 补完后实现说明（2026-04-26）

## 0. 文档目的

本文用于记录 `agent-pipeline` 当前 `qjb` 分支上，对 `pipeline2` 进行 **问题级重试、stage retry、stage cache / salvage、PTK 子阶段进度持久化、problem error 摘要增强** 后的实现状态。

写这份文档的目的有三个：

1. 说明这轮补了什么、为什么补；
2. 说明现在失败 / 中断后哪些内容可以 salvage；
3. 明确还没补的边界，避免后续误以为已经迁完整个上游架构。

本文只描述截至以下提交为止已经落地的内容：

- `b7b3016cb`：`Add pipeline2 stage cache salvage path`
- `3181d162e`：`Improve pipeline2 salvage progress reporting`

本轮没有重新跑数据集；验证方式是代码审查、diff 检查与最小编译检查。

---

## 1. 背景：为什么要补 salvage

此前 `pipeline2` 在长批次运行中暴露了几个恢复性问题：

1. 长任务可能被 `SIGKILL` 或外部生命周期中断；
2. 批次未走到 batch finalization 时，`annotation_runtime/problems.json`、`failed_problems.json`、`usage_summary.json` 等批级摘要可能缺失；
3. `langgraph.checkpoint.sqlite` 在当前环境中并不总是可用，缺失时会 fallback 到 `InMemorySaver()`，不能假定 `--resume-batch-id` 可完整恢复；
4. PTK / claim 的内部 critic-polish 循环成本较高，如果中途失败或中断，全部重跑浪费明显；
5. 原先失败题目主要依赖批级 `failed_problems` 汇总，不够适合单题级 forensic 与后续 salvage。

因此本轮采用“**方案 B：最小迁移上游更稳的恢复能力，不硬搬整套架构**”。

也就是说，本轮重点不是重写模型路由、prompt 策略或上游全部 PTK 质量增强，而是先让中断后的可恢复资产尽量落盘。

---

## 2. 当前已经补上的能力总览

当前 `agent-pipeline/src/benchmarkallinone/pipeline2` 已经具备以下恢复相关能力：

### 2.1 problem 级失败落盘

相关文件：

- `src/benchmarkallinone/pipeline2/pipeline.py`
- `src/benchmarkallinone/pipeline2/models.py`
- `src/benchmarkallinone/pipeline2/config.py`
- `src/benchmarkallinone/pipeline2/configs/default_pipeline2.yaml`

核心行为：

- 单题失败不会只消失在 batch exception 里；
- `_run_problem_with_retries(...)` 会按 `runtime.problem_retry_attempts` 做题目级重试；
- 如果最终仍失败，并且 `runtime.continue_on_problem_error: true`，会写出：

```text
<output_root>/problem_errors/<problem_id>.json
```

该文件记录：

- `problem_id`
- `status = unavailable`
- `current_status = problem_unavailable`
- `attempts_exhausted`
- `error_type`
- `error_message`
- 数据集 / subject / sample_path / question / answer / images 等题目信息

在 `3181d162e` 之后，该 error record 还会带 `stage_cache_summary`，详见第 5 节。

---

### 2.2 problem 结构验证接入

相关文件：

- `src/benchmarkallinone/pipeline2/pipeline.py`
- `src/benchmarkallinone/pipeline2/verification_modules.py`

当前结构验证节点接在：

```text
bind_evidence -> validate_problem_structure -> finalize_problem_bundle
```

这样做的好处是：

- `bind_evidence` 之后已经有足够完整的结构化对象；
- `finalize_problem_bundle` 前还能决定是否 fail / 是否记录 `verification_audit`；
- 最终 bundle 中会保留结构验证审计。

相关配置：

- `runtime.enable_problem_structure_validation`
- `runtime.fail_on_problem_structure_validation`

---

### 2.3 stage retry

相关文件：

- `src/benchmarkallinone/pipeline2/pipeline.py`
- `src/benchmarkallinone/pipeline2/config.py`
- `src/benchmarkallinone/pipeline2/configs/default_pipeline2.yaml`

当前新增了 stage retry 层：

- `_invoke_graph_with_stage_retries(...)`
- `_is_transient_stage_error(...)`
- `_extract_stage_name(...)`
- `StageRetryBudgetExhaustedError`

配置项：

```yaml
runtime:
  stage_retry_attempts: 3
  stage_retry_backoff_seconds: 1.0
```

它的作用是：

1. 对看起来像 transient 的错误做同 stage bounded retry；
2. 尽量利用 LangGraph checkpoint 从当前 stage 附近恢复；
3. 如果同一 stage 连续失败超过预算，抛 `StageRetryBudgetExhaustedError`；
4. 再交给 problem-level retry / `problem_errors` 路径处理。

当前 transient marker 包括：

- `timeout`
- `timed out`
- `read operation timed out`
- `connection reset`
- `brokenpipeerror`
- `sslerror`
- `http 408`
- `http 409`
- `http 429`
- `http 500`
- `http 502`
- `http 503`
- `http 504`

注意：stage retry 不是无限 retry，也不是换模型 fallback；它只是给外部抖动一个受控恢复窗口。

---

### 2.4 stage cache / salvage 基础层

相关文件：

- `src/benchmarkallinone/pipeline2/pipeline.py`

新增 helper：

```python
_stage_cache_path(batch_id, problem_id, stage_name, item_key)
_load_stage_cache_record(batch_id, problem_id, stage_name, item_key)
_write_stage_cache_record(batch_id, problem_id, stage_name, item_key, payload)
```

cache 路径规则：

```text
<runtime_dir>/stage_cache/<batch_id>/<problem_id>/<stage_name>/<digest>.json
```

其中 digest 来源于：

```python
stable_digest([batch_id, problem_id, stage_name, item_key], length=16)
```

当前接入的 stage cache 包括：

| stage_name | item_key | 内容 |
| --- | --- | --- |
| `ptk_foundation` | `bundle` | 完整 PTK bundle |
| `ptk_foundation_progress` | `bundle` | PTK 进行中进度 |
| `method_results` | `method_id` | 单个 method graph 运行结果 |
| `claim_bundles` | `method_id` | 单个 method 的完整 claim bundle |
| `claim_bundle_progress` | `method_id` | 单个 method 的 claim 抽取/修复进度 |

这层的目标是：即使 problem graph 不能完全从 checkpoint 恢复，也可以在下一次 problem attempt 中复用已经成功的昂贵阶段结果。

---

## 3. PTK stage salvage 细节

### 3.1 完整 PTK bundle cache

在 `_build_ptk_node(...)` 中，优先读取：

```python
_load_stage_cache_record(batch_id, problem_id, "ptk_foundation", "bundle")
```

只有当 cache record 满足以下结构时才复用：

- `problem_record` 是 dict；
- `p_facts` 是 list；
- `t_facts` 是 list；
- `k_atoms` 是 list；
- `audit` 是 dict。

复用成功后不会重跑 PTK extraction / critic / polish。

---

### 3.2 PTK repair-round progress

如果没有完整 `ptk_foundation`，则读取：

```python
_load_stage_cache_record(batch_id, problem_id, "ptk_foundation_progress", "bundle")
```

并传入：

```python
build_ptk_foundation(
    router,
    problem,
    max_repair_rounds=4,
    progress_state=progress_state,
    save_progress=_save_ptk_progress,
)
```

`build_ptk_foundation(...)` 会保存：

- `foundation`
- `audit_rounds`
- `next_round_index`
- `pending_critique`
- `passed`

因此，如果失败发生在 PTK critic / polish 多轮修复之间，下一次可以从已完成的 round 附近继续，而不是从头抽取 PTK。

---

### 3.3 PTK 初始三子阶段 progress（3181d162e 新增）

在 `3181d162e` 之前，`build_ptk_foundation(...)` 只有在 `_extract_ptk_once(...)` 完整成功返回之后才会有 `foundation` 可持久化。

但 `_extract_ptk_once(...)` 内部实际是三步连续调用：

```text
PerceptionExtraction -> TextCondition -> KnowledgeLibrarian
```

如果进程在中间被 kill，例如：

- `p_facts` 已生成，但 `TextCondition` 卡住；
- `p_facts` / `t_facts` 已生成，但 `KnowledgeLibrarian` 卡住；

旧逻辑无法复用已完成子结果。

现在 `_extract_ptk_once(...)` 本身也支持：

```python
progress_state: Optional[Dict[str, Any]]
save_progress: Optional[Callable[[Dict[str, Any]], None]]
```

它会在子阶段边界写出：

- `problem_record`
- `p_facts`
- `t_facts`
- `k_atoms`
- `next_ptk_substage`
- `ptk_substage_status`

典型状态包括：

```json
{
  "problem_record": {...},
  "p_facts": [...],
  "t_facts": [],
  "k_atoms": [],
  "next_ptk_substage": "text_condition",
  "ptk_substage_status": "in_progress"
}
```

或：

```json
{
  "problem_record": {...},
  "p_facts": [...],
  "t_facts": [...],
  "k_atoms": [],
  "next_ptk_substage": "knowledge_librarian",
  "ptk_substage_status": "in_progress"
}
```

当 `k_atoms` 也完成后，会写入：

```json
{
  "foundation": {...},
  "next_ptk_substage": "complete",
  "ptk_substage_status": "complete"
}
```

这样 kill 在 PTK 初始三连调用中间时，下一次 attempt 可以跳过已经持久化的 P/T/K 子结果。

---

## 4. method stage salvage 细节

相关函数：

- `_run_methods_node(...)`
- `_run_single_method(...)`

每个 method 单独缓存：

```python
_write_stage_cache_record(batch_id, problem_id, "method_results", method_id, {"method": processed})
```

读取时要求：

- cache record 是 dict；
- `record["method"]` 是 dict；
- `method_id` 与当前 method 一致。

这样如果一个 problem 有多个 method，已经跑完的 method 不会因为后续 method 或 claim 阶段失败而全部重跑。

同时 `_write_method_snapshot(...)` 仍保留，用于 method 级别快照观察。

---

## 5. claim stage salvage 细节

### 5.1 完整 claim bundle cache

在 `_extract_claims_node(...)` 中，针对每个 qualified method 优先读取：

```python
_load_stage_cache_record(batch_id, problem_id, "claim_bundles", method_id)
```

复用要求：

- `method_id` 一致；
- `claims` 是 list；
- `audit` 是 dict。

复用成功后不会重跑 claim extraction / verify / polish。

---

### 5.2 claim repair-round progress

如果没有完整 `claim_bundles`，则读取：

```python
_load_stage_cache_record(batch_id, problem_id, "claim_bundle_progress", method_id)
```

并传给：

```python
extract_claims_bundle(
    router,
    problem,
    method,
    cot_text,
    p_facts,
    t_facts,
    k_atoms,
    max_repair_rounds=4,
    progress_state=progress_state,
    save_progress=_save_claim_progress,
)
```

`extract_claims_bundle(...)` 会保存：

- `claims`
- `audit_rounds`
- `next_round_index`
- `pending_critique`
- `passed`

这保证 claim 初次抽取成功后，即使 critique/polish 后续失败，也可以复用初始 claims 和已经完成的 audit rounds。

---

### 5.3 claim failure audit trail

如果 claim extraction 抛 `PipelineDataContractError`，当前逻辑会：

1. 读取最新 `claim_bundle_progress`；
2. 从中提取 `audit_rounds` 和 partial `claims` count；
3. 写入 `claim_extraction_failures`；
4. 标记对应 method：
   - `claim_extraction_status = failed`
   - `claim_extraction_error = ...`
5. 后续如果存在失败 method，会通过 `ClaimExtractionGate` 显式失败。

这意味着：

- 成功 method 的 `claim_bundles` 不会丢；
- 失败 method 的 partial audit 也会尽量进入 failure-side trail；
- 但当前策略仍是 strict：任一 qualified method claim 失败会导致 problem 失败。

这是质量策略选择，不是 salvage 数据丢失。

---

## 6. problem_errors 中的 stage_cache_summary（3181d162e 新增）

此前 `problem_errors/<problem_id>.json` 只记录题目元信息和异常信息，不能直接告诉后续恢复者“哪些 stage cache 已经存在”。

现在 `_build_problem_error_record(...)` 接收 `batch_id`，并附加：

```json
{
  "batch_id": "...",
  "stage_cache_summary": {
    "stage_cache_root": "...",
    "ptk_foundation": {...},
    "ptk_foundation_progress": {...},
    "method_results": [...],
    "claim_bundles": [...],
    "claim_bundle_progress": [...]
  }
}
```

每个 summary item 包含：

- `stage_name`
- `item_key`
- `path`
- `present`
- `readable`
- `keys`
- 对 list 字段的轻量 count，例如：
  - `p_facts_count`
  - `t_facts_count`
  - `k_atoms_count`
  - `audit_rounds_count`
  - `claims_count`
  - `claim_count`
- 对 method cache 的 `method_id`

这样后续只看 `problem_errors/<problem_id>.json`，也能知道：

1. 是否已有 PTK progress；
2. 是否已有完整 PTK；
3. 哪些 method 已经跑完；
4. 哪些 claim bundle 已经可复用；
5. 哪些 claim progress 可用于 forensic。

---

## 7. 当前运行时输出关系

当前关键输出位置如下：

```text
<output_root>/
  problems/
    ... 完整 problem bundle ...
  problem_errors/
    <problem_id>.json
  annotation_runtime/
    pipeline2.log
    problems.json
    failed_problems.json
    usage_summary.json
    method_runs/
    stage_cache/
      <batch_id>/
        <problem_id>/
          ptk_foundation/
          ptk_foundation_progress/
          method_results/
          claim_bundles/
          claim_bundle_progress/
```

注意：`stage_cache` 当前位于 `runtime_dir`，而 `runtime_dir = output_root / "annotation_runtime"`。

这比早先“runtime_dir 与 output_root 分离时可能搬丢 cache”的设计风险更好，因为当前初始化逻辑中：

```python
runtime_dir = output_root / "annotation_runtime"
```

所以只要完整归档 `output_root`，stage cache 会一起被带走。

---

## 8. 和上游 pipeline2 的关系

本轮对比的是：

- 上游本地副本：`/root/.openclaw/workspace/pipeline2`
- 当前工作仓库：`/root/.openclaw/workspace/agent-pipeline`
- 当前分支：`qjb`

审查结论是：

- `_build_ptk_node`
- `_run_methods_node`
- `_extract_claims_node`

这三段核心 stage-cache wiring 已基本对齐。

但当前 `agent-pipeline` 没有迁上游更大的 PTK 质量架构，例如：

- `_sanitize_ptk_foundation(...)`
- `_infer_ptk_issue_categories(...)`
- `_ptk_issue_matches_prefix(...)`
- 分类型 `_polish_p_facts(...)` / `_polish_t_facts(...)` / `_polish_k_atoms(...)` 路径

这是刻意不迁，不是遗漏。

原因是本轮目标是 **salvage durability**，不是重写 PTK prompt / polish 架构。

---

## 9. 已做验证

本轮没有跑 dataset pipeline，也没有超过 20 samples 的运行。

做过的检查：

```bash
python3 -m py_compile \
  src/benchmarkallinone/pipeline2/annotation_modules.py \
  src/benchmarkallinone/pipeline2/pipeline.py
```

以及：

```bash
git diff --check -- \
  src/benchmarkallinone/pipeline2/annotation_modules.py \
  src/benchmarkallinone/pipeline2/pipeline.py \
  docs/note.md
```

结果：无输出，表示通过。

---

## 10. 当前仍未解决的边界

### 10.1 cache fingerprint 还没做

当前 stage cache key 仍主要由：

```text
batch_id + problem_id + stage_name + item_key
```

决定。

如果复用同一个 `batch_id/problem_id`，但 prompt、模型、代码、problem 输入发生变化，理论上可能误复用旧 cache。

建议后续加：

- problem fingerprint；
- prompt/config/schema version；
- git commit short hash；
- cache schema version。

读取时不匹配就忽略旧 cache。

---

### 10.2 PTK 子阶段只保存“阶段完成后”的结果

当前 `p_facts`、`t_facts`、`k_atoms` 是在对应模型调用返回并通过 normalize 后保存。

如果 kill 发生在单个模型请求内部，比如 SSE 正在 stream，当前仍不能保存 partial raw response。

这是合理边界：当前不做 streaming partial capture。

---

### 10.3 claim 初始抽取子阶段没有更细粒度拆分

claim 当前保存粒度是：

1. 初始 claims 完整生成后；
2. 每轮 critique / polish 前后。

如果 kill 发生在 `_extract_claims_once(...)` 的模型调用内部，仍需重跑该 method 的 claim extraction。

这比 PTK 三连调用的浪费小，因为 claim 初始阶段不是 P/T/K 三个连续 agent，因此暂时没有继续细拆。

---

### 10.4 strict claim failure 策略仍保留

当前只要有 qualified method 的 claim extraction 最终失败，problem 仍可能通过 `ClaimExtractionGate` hard fail。

这保证节点库质量，但意味着不能产出 partial problem bundle。

后续如果想更偏“尽量产出”，可以加配置：

```yaml
runtime.fail_on_partial_claim_extraction: true/false
```

但这属于质量策略，不属于本轮 salvage patch。

---

## 11. 后续建议

优先级从高到低：

1. **加 cache fingerprint / schema version**
   - 防止 prompt / 模型 / 输入变更后误复用旧 cache。

2. **补一个轻量 cache inspection 脚本**
   - 输入 `output_root + problem_id`；
   - 打印 PTK/method/claim cache 可复用状态；
   - 辅助人工 salvage / integrate。

3. **按小样本验证 PTK 子阶段恢复**
   - 不跑大数据集；
   - 可用 mock router 或单题受控中断方式验证 progress record shape。

4. **再决定是否迁上游 PTK 质量增强**
   - 如果后续 PTK gate failure 仍集中在 `p_facts` / `t_facts` / `k_atoms` 质量问题，再考虑迁 `_sanitize_ptk_foundation` 或分类 polish；
   - 不建议和 salvage patch 混在一起。

---

## 12. 简短结论

当前 `pipeline2` 的恢复能力已经从“只有外层 retry / 失败汇总”推进到：

```text
problem-level retry
+ stage-level transient retry
+ PTK/method/claim stage cache
+ PTK 初始 P/T/K 子阶段 progress
+ claim repair progress
+ problem_errors stage_cache_summary
```

这已经覆盖了当前最关键的中断恢复场景：

- PTK 抽取后中断；
- PTK repair 中断；
- 部分 method 已完成后中断；
- claim extraction / repair 中断；
- 单题最终失败但仍需要知道有哪些可 salvage 资产。

还没做的是 cache fingerprint、partial streaming capture、以及上游更完整的 PTK 质量架构迁移。
