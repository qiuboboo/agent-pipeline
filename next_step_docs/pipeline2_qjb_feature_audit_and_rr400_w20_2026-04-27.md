# Pipeline2 qjb 功能对照与 rr400_w20 分析记录（2026-04-27）

## 1. 背景

本记录汇总两件事：

1. 将 `pipeline2/next_step_docs` 的 9 个历史文档同步到 `agent-pipeline/qjb` 后，对照 qjb 当前 pipeline2 实现逐项检查哪些优化已存在、哪些缺失。
2. 记录 `rr400_w20`（400 样本、20 并发）运行的统计口径、结果和多模态请求比例异常偏高的代码级原因。

同步提交：

```text
fe9782f82 Sync historical pipeline2 next step docs
```

## 2. qjb 功能对照结论

### 2.1 已实现或基本实现

- ready 输入契约与图片检查：`ready_loader.py` 中 `load_ready_problem()` 会加载 `ready_for_annotation`，并在 `requires_image=true` 但图片缺失时硬失败。
- method planning：按 `initial_multi_solution_score` 决定目标方法数，低/中/高分别对应 1/2/3 个方法。
- Solver / AnswerEquivalence / AnswerRepair：主线已接入。
- CoTVerify / CoTPolish 多轮闭环：method graph 包含 verify/polish round 0-3。
- PTK foundation：包含 `build_ptk_foundation()`、`critique_ptk_foundation()`、`polish_ptk_foundation()`，有 structure critic、visual grounding critic 和 heuristic sanity check。
- Claim extraction：包含 extraction、structure/grounding/global critique、polish 多轮闭环。
- Claim -> r_nodes、solution_library、evidence_bindings、trace_mapping_index：主线已存在。
- stage cache / progress salvage：PTK、method、claim bundle 等阶段有 cache/progress 文件。
- stage retry / problem retry：配置里有 `stage_retry_attempts`、`problem_retry_attempts`，失败会进入 `problem_errors` 并记录 `[problem-marked-unavailable]`。
- usage summary：`clients.py` 统计 request_count、successful_request_count、failed_request_count、retry_count、multimodal_request_count、text_request_count、total_tokens 等。
- fail-fast API key 检查：`ensure_available(...)` 已用于 annotate/evaluate/output verifier 等入口。
- Responses API 支持：`clients.py` 中有 responses payload 和 response text 提取逻辑。
- 图题 multimodal 硬约束：`_call_router(...)` 会在图片成功加载后走 `chat_json_with_images(...)`，并在 `require_images=True` 时检查实际 request mode。

### 2.2 缺失或不完整

- Coverage Hunter 没有独立实现；当前只有 coverage_state 统计，没有主动发现覆盖缺口并补方法的 agent。
- `rewrite_report` / `open_ended_problem_variants` 仍未进入主决策链，只在 backup 示例 JSON 中可见。
- trace patch 回流仍偏启发式，不是完整严格的二次拆解、审核、回写链路。
- Problem structure validation 已接入，但当前是 LLM-based claim/node validation，不是早期文档中更低成本的纯 heuristic structural 秒批。
- `extract_claims_bundle()` 会返回 `claim_gate_status="soft_failed"`，但主 pipeline 最好再显式拦截 `claim_gate_passed == false`，防止 soft-failed claims 进入后续 node induction。

## 3. rr400_w20 统计记录

用户指定统计截止点：

```text
2026-04-27 02:35:05
```

统计口径：

- 截止点前 `[problem-done]` 记为通过。
- 截止点前 `[problem-marked-unavailable]` 记为已处理但未通过。
- 截止点前出现过但未结束的题不计入通过率分母。
- token 只统计截止点前日志中 `[llm-request-success] total_tokens=...`。
- 截止点之后失败不看。

结果：

```text
已结束处理题数：264
通过题数：30
通过率：11.36%
成功请求：7509
tokens：55,119,956
估算成本：约 $50.97
```

对比 `incremental100_20260425_v1`：

```text
incremental100：56/100，通过率 56.00%
rr400_w20 全量近似：30/400，通过率约 7.5%
rr400_w20 截止口径：30/264，通过率 11.36%
```

低通过率主要不是余额不足之后才造成的；在截止点前已经大量出现：

- `Non-JSON HTTP response`
- HTTP 错误
- `MethodPlanner` 等中间阶段失败
- 高并发下请求链路不稳定
- 后段 multimodal 调用过多导致 token、延迟、失败面放大

## 4. 多模态比例差异的代码级原因

### 4.1 `_call_router(...)` 的真实触发规则

核心逻辑在 `agents.py`：

```python
images = _load_images(image_paths)
response = (
    router.chat_json_with_images(system_prompt, user_prompt, images)
    if images
    else router.chat_json(system_prompt, user_prompt)
)
```

因此：

- 真正决定是否 multimodal 的不是 `require_images` 本身，而是 `image_paths` 是否传入且能成功加载。
- `require_images=True` 的作用是硬性要求图必须存在，并检查返回 `_llm_request_mode == "multimodal"`。
- 只要某个阶段给 `_call_router(...)` 传了 `_problem_image_paths(problem)`，图题就会变成 multimodal 请求。

### 4.2 当前 qjb 为什么 multimodal 比例偏高

当前 qjb 的代码在许多阶段都传图，包含：

- MethodPlanner / Solver 相关阶段
- AnswerEquivalenceJudge
- AnswerRepair
- CoTVerify
- CoTPolish
- PTKVisualGroundingCritic
- ClaimExtraction
- ClaimVerifyStructure
- ClaimVerifyGrounding
- ClaimVerifyGlobal
- ClaimPolish
- FinalCoTValidation
- ClaimSetValidation
- NodeSetValidation

这导致一个图题不是只在少数必要阶段带图，而是全链路大量后段 agent 也带图。

### 4.3 为什么另一个 pipeline2 / backup 的多模态比例更低

与当前 qjb 相比，早期/backup pipeline2 更保守：

- 很多结构化、验证、修复类阶段使用 `require_images=False`。
- 很多阶段不传 `_problem_image_paths(problem)`，即使题目本身是图题，也只用 compact ready context 或文本化结构。
- 只有真正视觉 grounding 必要的阶段才附图。

所以如果看到“pipeline2 的 multimodal 比例比 qjb/rr400_w20 低”，原因不是数据集本身一定图题少，而是代码路由策略不同：旧/低比例 pipeline2 的后段多为 text-only；当前 qjb 的后段大量 multimodal。

## 5. 建议修改方向

优先将后段结构化/验证/修复类 agent 改回 text-only 或按需升级：

- 保留 multimodal：Solver、PTKVisualGroundingCritic、必要的 CoTVerify。
- 默认 text-only：AnswerEquivalenceJudge、AnswerRepair、CoTPolish、ClaimVerifyStructure、ClaimVerifyGlobal、ClaimPolish、ClaimSetValidation、NodeSetValidation。
- 对 `ClaimVerifyGrounding` 可以保留图题 multimodal，但要评估成本；也可以先用 ready visual context，失败时再升级 multimodal。
- 在 `_extract_claims_node()` 显式拦截 `claim_gate_passed == false`。
- 遇到余额不足 / HTTP 403 / `INSUFFICIENT_BALANCE` 应全局停止 batch。
- 对 `Non-JSON HTTP response` 加短 retry。
