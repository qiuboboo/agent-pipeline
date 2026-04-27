# 第二步标注 Pipeline 补全后实现评估

## 0. 本文目的

本文对照 [`benchmarkallinone/next_step_docs/第二步标注Pipeline详细设计.md`](./第二步标注Pipeline详细设计.md)，说明当前 [`benchmarkallinone/pipeline2`](../pipeline2) 在本轮补全后的实现状态，重点回答：

1. 现在的实现还有什么问题？哪些做到了，哪些没做到？
2. 对照试验样例与 ready 原问题 JSON，现在的实现对哪些部分做了哪些操作？

同时，本文会明确区分：

- **旧的不好的实现**：本轮补全前的 [`benchmarkallinone/pipeline2`](../pipeline2) 主线；
- **新的实现**：本轮补全后，以 [`benchmarkallinone/pipeline2/annotation_modules.py`](../pipeline2/annotation_modules.py) 为核心、已经接入主线的版本。

---

## 1. 旧实现与新实现的边界

## 1.1 旧实现是什么

旧实现并不是“完全没有第二步 pipeline”，而是已经有一条能跑通的主线：

`ready -> method planning -> solver -> answer check/repair -> CoT verify/polish -> PTK -> claim -> r_nodes -> solution_library -> trace eval`

但旧实现在“抽取 groundtruth 节点前一步”的两个关键模块上存在明显不足：

1. **PTK Foundation Builder 只有单次抽取，没有 planner/critic/polish 闭环**；
2. **Claim Extraction 只有单次抽取，没有 claim critic/polish 闭环**；
3. **两者都主要吃 ready 摘要，缺少真正的图像输入链路**；
4. **coverage 统计把规划方法数和合格方法数混淆**；
5. **无 API key 时，live run 会报成“LLM returned no JSON object”，错误定位很差。**

也就是说，旧实现“能跑”，但离设计文档要求的“严格、全自动、多 Agent、多轮修复、多轮验证”还差一截。

## 1.2 新实现是什么

本轮补全后，新实现把“抽取 groundtruth 节点前一步”的两个模块补成了真正的闭环模块：

1. **题目级 `PTK Foundation Builder` 闭环**
   - 初次抽取 `P/T/K`；
   - `PTK Foundation Critic` 审核 grounding / coverage / minimality；
   - `PTK Foundation Polish` 按 critic 指令重写；
   - 最终只允许通过审核的 `P/T/K` 进入 claim 阶段；
   - 把审核轨迹沉淀到 `ptk_foundation_audit`。

2. **方法级 `Claim Extraction Agent` 闭环**
   - 先从 verified CoT 抽 claim；
   - `Claim Verify` 检查 atomicity / dependency / grounding；
   - `Claim Polish` 按 critic 指令修正 claim 序列；
   - 最终只允许通过审核的 claim 序列进入 node induction；
   - 把审核轨迹沉淀到 `claim_audit` / `claim_extraction_audits`。

3. **主线集成点**
   - 在 [`benchmarkallinone/pipeline2/pipeline.py`](../pipeline2/pipeline.py) 中，把旧的单次 `extract_ptk` / `extract_claims` 替换为新的闭环实现；
   - 把审计信息写进最终 problem bundle；
   - 修复 `coverage_state.method_count`，使其反映规划方法总数，而不是仅反映合格方法数；
   - 加入 API key 前置检查，避免无密钥时误报成 JSON 契约错误。

---

## 2. 本轮新增与修改的核心文件

## 2.1 新增文件

### [`benchmarkallinone/pipeline2/annotation_modules.py`](../pipeline2/annotation_modules.py)

这是本轮补全的核心文件，负责实现两个闭环模块：

- `build_ptk_foundation()`
- `extract_claims_bundle()`

它们具备以下特征：

- 严格的 JSON 契约校验；
- 必须图像接入时走图像输入，不再只走纯文本摘要；
- critic / polish 多轮修复；
- 审计轨迹落盘；
- 失败时显式报错，不用内容 fallback 掩盖问题。

## 2.2 修改文件

### [`benchmarkallinone/pipeline2/prompts.py`](../pipeline2/prompts.py)

新增了以下 prompt：

- `PTK_FOUNDATION_CRITIC_SYSTEM_PROMPT`
- `PTK_FOUNDATION_POLISH_SYSTEM_PROMPT`
- `CLAIM_VERIFY_SYSTEM_PROMPT`
- `CLAIM_POLISH_SYSTEM_PROMPT`

以及对应的 user prompt 构造函数。

### [`benchmarkallinone/pipeline2/pipeline.py`](../pipeline2/pipeline.py)

主线改动包括：

- `build_ptk_foundation()` 接管旧的 `extract_ptk()` 直接调用；
- `extract_claims_bundle()` 接管旧的单次 `extract_claims()`；
- 最终输出新增：
  - `annotation_pipeline_version`
  - `ptk_foundation_audit`
  - `claim_extraction_audits`
- `coverage_state.method_count` 修复为规划方法总数。

### [`benchmarkallinone/pipeline2/agents.py`](../pipeline2/agents.py)

`group_solutions()` 新增 `planned_method_count` 参数，用于修复 coverage 统计口径。

### [`benchmarkallinone/pipeline2/clients.py`](../pipeline2/clients.py)

新增：

- `has_available_endpoint()`
- `ensure_available()`

作用是：

- 在 live pipeline 启动前检查是否存在可用 API key；
- 没有 key 时直接给出明确错误；
- 避免旧实现里的误导性错误信息。

### [`benchmarkallinone/pipeline2/verified_cot_pipeline.py`](../pipeline2/verified_cot_pipeline.py)

新增同样的 API key 前置检查，使 verified CoT 子流水线也能 fail fast。

### [`benchmarkallinone/pipeline2/tests/test_annotation_modules.py`](../pipeline2/tests/test_annotation_modules.py)
### [`benchmarkallinone/pipeline2/tests/test_clients.py`](../pipeline2/tests/test_clients.py)

补了单元测试，覆盖：

- PTK repair loop；
- claim repair loop；
- claim 无法修复时显式失败；
- coverage 统计修复；
- router API key 可用性检查。

---

## 3. 现在的实现：哪些做到了，哪些没做到

## 3.1 已经做到的

### A. 主线仍然是全自动的

当前主线不要求人工参与：

- 自动读 ready；
- 自动决定方法数；
- 自动 planner / solver / answer repair / CoT verify / CoT polish；
- 自动 PTK foundation critic / polish；
- 自动 claim verify / polish；
- 自动 node induction / solution grouping / evidence binding；
- 自动 trace mapping / novelty detect / patch build。

### B. 新增了必要的多 Agent 闭环

对照设计文档，本轮真正补上的就是“抽取 groundtruth 节点前一步”的两个闭环模块：

1. **PTK Foundation Builder** 现在不是单次抽取，而是：
   - extractor -> critic -> polish -> re-critic
2. **Claim Extraction Agent** 现在不是单次 claim 切分，而是：
   - extractor -> critic -> polish -> re-critic

这符合设计里要求的：

- 角色分工明确；
- 严格 system prompt；
- JSON 强约束；
- critic / polish 闭环；
- 不允许用 fallback 隐藏问题。

### C. 审计信息已经进入最终产物

这点很重要。现在最终 bundle 不再只是“结果对象”，而是同时带有：

- `ptk_foundation_audit`
- `claim_extraction_audits`

因此后面可以精确回答：

- 题目级底座是否经过修复；
- 哪个方法的 claim 序列修过几轮；
- 最终为什么放行。

### D. coverage 统计口径已修复

旧实现里 `coverage_state.method_count` 会退化成“合格方法数”；
本轮修复后，它变回“规划方法总数”，而 `qualified_method_count` 单独保留。

### E. 无密钥时会明确失败，不再假装是 JSON 问题

当前环境里没有：

- `PIPELINE2_API_KEY_PRIMARY`
- `PIPELINE2_API_KEY_FALLBACK`

所以 live annotate 无法真正调用模型。

旧实现会把这个问题表现成：

- `LLM returned no JSON object`

这很误导。

新实现会直接报：

- `No enabled model endpoint has an API key`

这才是正确的 fail-fast 行为。

---

## 3.2 还没做到的

### A. `Coverage Hunter` 仍未实现

这部分在设计文档里存在，但当前代码仍没有独立模块落地。

### B. 还没有达到“生产级强 grounding”

虽然 PTK/claim 两个模块已经开始接图像，但系统整体仍然强依赖：

- ready 中的结构化摘要；
- 上游可解析出的视觉对象；
- LLM 对这些摘要的理解能力。

也就是说，新实现**比旧实现更严格了**，但还不能说已经完全解决“几何级细粒度视觉 grounding”问题。

### C. `rewrite_report`、`open_ended_problem_variants` 仍未真正进入主决策链

它们目前仍主要是：

- 被动保留；
- 作为样本上下文的一部分；
- 尚未成为方法规划、PTK 审核、claim 审核的硬约束输入。

### D. Patch 回流仍是 Phase 3 的旧启发式

这次补全聚焦的是“抽取 groundtruth 节点前一步”的两个模块。

因此：

- `build_patch()` 仍然还是旧的启发式 patch 逻辑；
- 还没升级成设计文档里的“二次拆解 -> 再映射 -> 严格新颖性判断 -> 严格补丁写回”。

### E. 当前环境无法完成 live smoke 成功运行

原因不是代码逻辑，而是运行环境缺失 API key。

所以本轮验证里，live 命令的正确结果不是“成功产出 bundle”，而是：

- **在真正调用模型前明确失败**。

这已经验证了本轮新增的 fail-fast 保护，但还不能代替真实有 key 环境下的端到端 smoke run。

---

## 4. 针对用户问题 1：现在的实现有什么问题？哪些做到了，哪些没做到？

## 4.1 做到的

1. 第二步 pipeline 主线已经存在且可维护；
2. verified CoT 阶段已经比较完整；
3. 只让“答案正确 + CoT 合格”的方法进入节点化，这条门是对的；
4. 本轮新增了 **PTK 闭环** 与 **claim 闭环**；
5. 主线现在能沉淀这两个闭环的审计结果；
6. `coverage_state.method_count` 口径已修正；
7. 无 API key 时会明确 fail fast；
8. 单元测试已覆盖本轮新增逻辑。

## 4.2 没做到或仍有问题的

1. `Coverage Hunter` 没做；
2. 强多模态 grounding 仍然不够硬；
3. `rewrite_report` / `open_ended_problem_variants` 还没有真正成为主决策输入；
4. Phase 3 的 patch 回流仍是旧逻辑；
5. 当前环境无 API key，无法完成 live 端到端成功跑通；
6. 仓库中旧样例产物和新样例产物仍有版本漂移，需要后续统一。

---

## 5. 针对用户问题 2：对照试验例子与 ready 原问题 JSON，现在的实现对哪些部分做了哪些操作？

下面用样例题：

- ready 原题：[`benchmarkallinone/ready/agent_multidataset_validation_100/run_f7e4c82684a6f704/datasets/geometry3k/samples/prob_016bc73dfd9342abef609367.json`](../ready/agent_multidataset_validation_100/run_f7e4c82684a6f704/datasets/geometry3k/samples/prob_016bc73dfd9342abef609367.json)
- 旧 full bundle 样例：[`benchmarkallinone/pipeline2/outputs_smoke/problems/prob_016bc73dfd9342abef609367.json`](../pipeline2/outputs_smoke/problems/prob_016bc73dfd9342abef609367.json)

来说明“当前实现”对 ready 做了什么。

## 5.1 题目装载阶段

当前实现会真正使用这些 ready 信息：

- `clean_pool_entries[].pool_status`
- `clean_problem_record.problem_id`
- `clean_problem_record.normalized_question_text`
- `clean_problem_record.normalized_answer_text`
- `candidate_problem_record.initial_multi_solution_score`
- 图片路径相关信息
- `alignment_status`
- `solvability_score`
- `requires_image`
- `text_dominant`
- `sample_record` 整体上下文

也就是说，当前系统先做一次提取，提取出好的字段

## 5.2 方法规划阶段

例如样例题里：

- `initial_multi_solution_score = 0.56`

因此会被规划成 **2 个方法**。

当前实现对 ready 在这里做的操作是：

- 读取多解潜力分数；
- 决定分支数；
- 生成 `method[]` 壳；
- 再把问题送给 planner 生成方法草稿。

## 5.3 求解与 verified CoT 阶段

这一步是：

- 按方法草稿重新求解；
- 判断答案是否与标准答案等价；
- 不等价时做 answer repair；
- 再做多轮 CoT verify / polish。

因此，当前实现对 ready 做的不是“拿来即用”，而是：

- **把 ready 当输入条件；**
- **重新生成可验证的运行态解法。**

## 5.4 新的 PTK Foundation Builder 做了什么

旧实现里：

- `problem_record / p_facts / t_facts / k_atoms` 是单次抽取产物。

新实现里：

1. 先抽取 `P/T/K`；
2. 再审核：
   - `p_facts` 是否真的只是客观视觉事实；
   - `t_facts` 是否覆盖显式目标/条件；
   - `k_atoms` 是否是可复用知识，而不是解法步骤；
3. 如果不合格，就自动重写；
4. 直到通过，才允许进入 claim 阶段。

因此，对 ready 原题来说，系统现在会对题目级底座执行：

- **重建**；
- **审计**；
- **修复**；
- **再审计**。

## 5.5 新的 Claim Extraction Agent 做了什么

旧实现里：

- 只要方法合格，就直接从 `CoT_final` 抽 claims。

新实现里：

1. 先做 claim 抽取；
2. 再检查：
   - claim 是否足够原子；
   - 顺序是否与 verified CoT 对齐；
   - `depends_on` 是否只依赖前序 claim；
   - 有没有缺桥梁 claim；
   - 有没有不受 PTK 支撑的视觉 claim；
3. 若不合格，自动 polish claim 序列；
4. 通过后才进入 node induction。

因此，对 ready 原题和其最终合格 CoT 来说，系统现在做的是：

- **不是直接 claim 化**；
- **而是 claim 抽取 + claim 质检 + claim 修复 + 再放行。**

## 5.6 `node_records` 的处理方式

ready 里本来可能就有上游 `node_records`。

当前实现对它们的处理仍然是：

- **只作为辅助上下文；**
- **不会直接复用成最终 `r_nodes`。**

最终 `r_nodes` 仍然来自“本阶段合格 CoT -> claims -> canonical nodes”的链路。

## 5.7 证据绑定与解法族阶段

当前实现会继续对新的 claim/r_node 体系做：

- `solution_library`
- `solution_memberships`
- `evidence_bindings`
- `trace_mapping_index`

但这里依然存在老问题：

- 如果上游视觉 grounding 不够细，`evidence_bindings` 的质量仍会偏弱。

---

## 6. 本轮验证情况

## 6.1 已完成的本地验证

已完成：

1. `py_compile` 语法编译；
2. 单元测试运行通过；
3. live CLI smoke 在无 API key 环境下正确 fail fast。

## 6.2 已通过的测试内容

本轮测试覆盖了：

- PTK critic/polish 闭环；
- claim critic/polish 闭环；
- claim 无法修复时显式失败；
- `coverage_state.method_count` 口径修复；
- `ModelRouter.ensure_available()` 的 fail-fast 行为。

## 6.3 live smoke 的当前结论

当前环境缺少：

- `PIPELINE2_API_KEY_PRIMARY`
- `PIPELINE2_API_KEY_FALLBACK`

所以 live smoke **不能真正调模型成功跑完**。

但新实现已经验证：

- 不会再把这个问题误报成“LLM 没有返回 JSON”；
- 而是会在入口处明确指出“没有可用 API key”。

这说明本轮 debug 已经把“错误暴露方式”修正到正确状态。

---

## 7. 最终结论

如果用一句话概括本轮结果：

> 旧实现已经有第二步 pipeline 原型，但在 PTK 与 claim 两个关键模块上还是“单次抽取、弱审计、弱 fail-fast”；新实现已经把这两个模块补成了真正的多 Agent 闭环，并且接入了主线、测试和错误前置检查，因此第二步标注 pipeline 在“抽取 groundtruth 节点前一步”的实现上已经明显向设计文档收敛。

但要达到完全的生产级目标，后续还需要继续补：

1. `Coverage Hunter`；
2. 更强的图像 grounding；
3. `rewrite_report` / `open_ended_problem_variants` 的主决策接入；
4. 严格的 Phase 3 patch 回流闭环；
5. 有 API key 环境下的端到端 smoke 复验。
