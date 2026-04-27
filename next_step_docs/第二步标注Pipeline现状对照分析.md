# 第二步标注 Pipeline 现状对照分析

## 0. 分析范围

本文对照设计文档 [第二步标注Pipeline详细设计.md](./第二步标注Pipeline详细设计.md)，结合当前实现 [pipeline2/pipeline.py](../pipeline2/pipeline.py)、[pipeline2/verified_cot_pipeline.py](../pipeline2/verified_cot_pipeline.py)、[pipeline2/ready_loader.py](../pipeline2/ready_loader.py)、[pipeline2/agents.py](../pipeline2/agents.py)，以及样例输入输出：

- ready 原题： [ready/agent_multidataset_validation_100/run_f7e4c82684a6f704/datasets/geometry3k/samples/prob_016bc73dfd9342abef609367.json](../ready/agent_multidataset_validation_100/run_f7e4c82684a6f704/datasets/geometry3k/samples/prob_016bc73dfd9342abef609367.json)
- verified CoT 样例： [pipeline2/verified_cot_outputs_smoke/problems/prob_016bc73dfd9342abef609367.json](../pipeline2/verified_cot_outputs_smoke/problems/prob_016bc73dfd9342abef609367.json)
- 全量 bundle 样例： [pipeline2/outputs_smoke/problems/prob_016bc73dfd9342abef609367.json](../pipeline2/outputs_smoke/problems/prob_016bc73dfd9342abef609367.json)
- trace eval 样例： [pipeline2/outputs_smoke/trace_eval/mapping_reports/prob_016bc73dfd9342abef609367__trace_smoke_001.json](../pipeline2/outputs_smoke/trace_eval/mapping_reports/prob_016bc73dfd9342abef609367__trace_smoke_001.json)

本文回答两个问题：

1. 现在的实现有什么问题？哪些做到了，哪些没做到？
2. 对照试验例子与 ready 原问题 JSON，现在的实现对哪些部分做了哪些操作？

---

## 1. 结论先行

### 1.1 一句话结论

当前 [pipeline2](../pipeline2) 已经把“`ready -> verified CoT -> claim -> r_nodes -> solution_library -> trace mapping -> novelty/patch`”这条主链路**基本串起来了**，但还没有达到设计文档要求的“严格、稳定、强 grounding 的第二步标注 Pipeline”。

### 1.2 最重要的判断

- **做到的部分**：
  - 从 ready 读取题目；
  - 按多解分数决定方法数；
  - 做方法规划、求解、答案检查、CoT 验证与多轮 polish；
  - 只让“答案正确且最终 CoT 合格”的方法进入 claim/node 阶段；
  - 生成 `problem_record / p_facts / t_facts / k_atoms / r_nodes / solution_library / evidence_bindings / trace_mapping_index`；
  - 做 trace mapping、novelty detect、patch build。

- **没做到或只做到一半的部分**：
  - 没有真正落成设计里要求的“严格 `main.md` 运行态壳 + 单独落盘”；
  - 没有真正做到“直接看图”的强多模态 grounding；
  - `Coverage Hunter` 没实现；
  - `rewrite_report`、`open_ended_problem_variants` 等 ready 信息没有被显式纳入主决策链；
  - patch 回流还是启发式的，离设计里的“二次拆解-重比对-严谨补丁”有明显距离；
  - 仓库中现有 smoke 产物存在版本漂移，说明实现与样例落盘还不完全一致。

---

## 2. 对照设计文档：哪些做到了，哪些没做到

## 2.1 已做到的部分

| 设计模块 | 现状 | 说明 |
| --- | --- | --- |
| Ready Intake Loader | 已做到 | [pipeline2/ready_loader.py](../pipeline2/ready_loader.py) 已实现 ready 扫描、状态过滤、字段提取、图片路径解析。 |
| Method Planner | 已做到 | [pipeline2/agents.py](../pipeline2/agents.py) 中有规划方法的 agent 调用。 |
| Solver | 已做到 | 已能按 method draft 生成 `CoT_raw` 和 `model_answer`。 |
| Answer Match / Repair | 已做到 | 已有确定性比对 + LLM 比对 + answer repair。 |
| CoT Verify / Polish | 已做到 | 已有 0~3 轮验证与 polish 闭环，且 [pipeline2/verified_cot_pipeline.py](../pipeline2/verified_cot_pipeline.py) 专门实现了 verified CoT 子流水线。 |
| PTK Foundation Builder | 已做到 | 已能产出 `problem_record / p_facts / t_facts / k_atoms`。 |
| Claim Extraction | 已做到 | 只对合格方法抽 claim。 |
| Node Induction | 已做到 | 已能生成 `r_nodes` 和 `claim_mappings`。 |
| Solution Grouper / Evidence Binder | 已做到 | 已能生成 `solution_library / solution_memberships / evidence_bindings / coverage_state`。 |
| Trace Mapper / Novelty Detector / Patch Writer | 已做到 | 已能跑通评测轨迹对齐、新颖性判断、补丁构造。 |

## 2.2 部分做到的部分

| 设计要求 | 现状 | 问题 |
| --- | --- | --- |
| 严格经过 `main.md` 中间结构 | 部分做到 | 内存里确实存在 `problem + method[]` 运行态，但当前主流水线最终落盘的是最终 bundle，而不是设计里要求的“只存中间运行态壳”的独立产物。 |
| 全自动主线 | 基本做到 | 主线不依赖人工，但当视觉 grounding 不足时，结果会带着弱支撑继续往后传。 |
| 多解收敛 | 部分做到 | 方法数规则做到了，但“多解是否真实 distinct”仍很依赖 LLM，且 coverage 统计有偏差。 |
| 节点证据绑定 | 部分做到 | 已有 `evidence_bindings`，但弱 grounding 时会出现“节点有了，证据几乎为空”的情况。 |
| 新解回流 | 部分做到 | 已有 trigger、novelty、patch build，但 patch 还很粗糙。 |

## 2.3 没做到的部分

| 设计要求 | 现状 |
| --- | --- |
| `Coverage Hunter` | 当前代码里没有独立实现。 |
| 严格使用图像做多模态 grounding | 当前大多数 agent 实际上吃的是 ready 摘要，而不是直接吃图像。 |
| 显式利用 `rewrite_report`、`open_ended_problem_variants` | 这些字段大多只是被动保留在 `sample_record` 中，没有进入核心逻辑。 |
| 严格的“回流前二次拆解 + 再映射 + 补丁写回” | 当前 patch 更像启发式构造，不是设计中的完整回流闭环。 |
| 与设计完全一致的目录落盘 | 当前代码写的是 [pipeline2/outputs_smoke/problems](../pipeline2/outputs_smoke/problems) 这种 problem bundle 输出；仓库里也同时存在 [pipeline2/outputs_smoke/annotation_outputs](../pipeline2/outputs_smoke/annotation_outputs) 这种旧式目录，版本混杂。 |

---

## 3. 当前实现的关键问题

## 3.1 最大问题：并没有真正“直接看图”

虽然设计文档强调多模态 grounding，但当前 [pipeline2/agents.py](../pipeline2/agents.py) 的主调用方式，本质上更接近“把 ready 中的结构化摘要塞给 LLM，然后走文本推理”。

这带来两个后果：

1. 当 ready 里的视觉结构本身很粗时，后续 agent 无法获得真正足够的图像事实；
2. 即便后续 CoT 写出了具体视觉细节，也可能只是“从答案反推出来的合理故事”，而不是真正可验证的图像证据。

这个问题在样例里非常明显：

- ready 里的 [visual_structure_records](../ready/agent_multidataset_validation_100/run_f7e4c82684a6f704/datasets/geometry3k/samples/prob_016bc73dfd9342abef609367.json) 只提供了 `canvas / roi / subregion` 这类粗粒度对象；
- 但 verified CoT 和 full bundle 里却出现了“`115°`、线性对、相邻角、对顶射线”这类强语义图像事实；
- 这说明当前系统并不是从 ready 中已有的显式视觉事实稳定推出这些内容，而是在弱 grounding 条件下继续生成了细节化推理。

## 3.2 verified CoT 能跑通，但 verifier 仍会“放行弱 grounding”

样例 [pipeline2/verified_cot_outputs_smoke/problems/prob_016bc73dfd9342abef609367.json](../pipeline2/verified_cot_outputs_smoke/problems/prob_016bc73dfd9342abef609367.json) 表明：

- 方法 1 经过多轮 polish，最终被标记为 `is_final_CoT_qualified=true`；
- 但它前几轮 verifier 自己也承认“`115°` 与 straight line 关系并没有被权威 grounding context 支撑”；
- 最后一轮却把它放过了。

这意味着：**当前 verifier 更像“风格-一致性 critic”，还不是一个真正严格的证据审查器。**

## 3.3 full pipeline 已实现，但节点层会继承上游 hallucination

样例 [pipeline2/outputs_smoke/problems/prob_016bc73dfd9342abef609367.json](../pipeline2/outputs_smoke/problems/prob_016bc73dfd9342abef609367.json) 中：

- `claim_sequences` 已经把“`115°`、linear pair、180-115=65”拆成了 7 个 claim；
- `r_nodes` 也把这些 claim 节点化了；
- 但 `evidence_bindings` 里多个节点的 `p_fact_ids / t_fact_ids / k_atom_ids` 基本是空的，支撑强度还是 `LOW`。

这说明当前实现已经具备“节点化能力”，但还没有具备“只沉淀高可信节点”的约束能力。

## 3.4 `coverage_state.method_count` 统计有问题

从设计看，`method_count` 应该反映题目的规划方法数；但当前样例里：

- verified CoT summary 显示 `planned_method_count=2`；
- full bundle 的 `coverage_state.method_count=1`。

这说明当前 coverage 统计实际上在用“合格方法数”，而不是“规划方法数”，会让 coverage 指标失真。

## 3.5 trace 评测指标会被“只命中 final answer”高估

在 trace 样例 [pipeline2/outputs_smoke/trace_eval/mapping_reports/prob_016bc73dfd9342abef609367__trace_smoke_001.json](../pipeline2/outputs_smoke/trace_eval/mapping_reports/prob_016bc73dfd9342abef609367__trace_smoke_001.json) 里：

- 只匹配到了最终答案节点；
- `node_hit_rate_total=0.25`、`node_hit_rate_required=0.25`，说明覆盖很低；
- 但 `topology_consistency_score=1.0`、`evidence_grounding_score=1.0`。

这两个高分看上去不太合理，因为它们是建立在“命中节点很少”的前提下算出来的。当前指标更像“命中的那几个节点质量还行”，不是真正意义上的“整条推理链结构质量很高”。

## 3.6 patch writer 还是启发式，不够严格

当前 trace 样例里最后没有写 patch，因为 novelty detector 给的是 `old_family_branch_extension`。这一点本身没问题；问题在于：如果未来被判成 `new_solution_family`，当前 patch 机制也是直接把 unmatched claims 生成为新节点，再给出空证据的默认 binding。它离设计里要求的“二次拆解、再映射、严谨新颖性判断、结构化补丁”还差一大截。

## 3.7 仓库里的试验产物存在版本漂移

仓库同时存在两类输出：

- [pipeline2/outputs_smoke/problems](../pipeline2/outputs_smoke/problems)：更像当前完整实现的 canonical bundle；
- [pipeline2/outputs_smoke/annotation_outputs](../pipeline2/outputs_smoke/annotation_outputs)：内容风格与当前代码、当前 full bundle 明显不一致，更像旧实验产物。

这会带来一个现实问题：**现在看 repo，很难一眼判断哪份样例才是“当前实现”的标准输出。**

---

## 4. 对照 ready 原问题 JSON：当前实现到底做了哪些操作

下面以样例题 `prob_016bc73dfd9342abef609367` 为例。

## 4.1 第一步：筛题与装载

当前实现会先从 ready 里做这几件事：

| ready 字段 | 当前实现的操作 | 样例结果 |
| --- | --- | --- |
| `clean_pool_entries[].pool_status` | 过滤，只接受 `ready_for_annotation` | 该题被放行 |
| `clean_problem_record.problem_id` | 取为运行态 `problem_id` | `prob_016bc73dfd9342abef609367` |
| `clean_problem_record.normalized_question_text` | 取为 `question_text` | `Find $m\angle VXW$.` |
| `clean_problem_record.normalized_answer_text` | 取为 `standard_answer` | `65` |
| `candidate_problem_record.initial_multi_solution_score` | 决定方法数 | `0.56 -> 2 个方法` |
| `asset_registry_record / raw_asset_bundle / normalized_assets / asset_records` 中的图像路径 | 解析为可用本地图片路径 | 解析出 1 张图 |
| `alignment_status / solvability_score` | 作为题目级辅助信号带入运行态 | `good / 1.0` |
| 整个样本 JSON | 在 full bundle 中被保留到 `runtime_problem.sample_record` | 原样保留，便于追溯 |

这里要注意：当前 loader 真正“显式消费”的核心字段比较少，主要就是 `problem_id / question / answer / image / method score / alignment / solvability / metadata` 这些；其余很多字段虽然保留了，但没有进入强逻辑分支。

## 4.2 第二步：把 ready 问题改造成运行态问题对象

这个阶段，ready 原题不再被当成“直接做节点化的对象”，而是会被改造成一个更简化的运行态题目对象，核心字段大致变成：

- `problem_id`
- `question_text`
- `standard_answer`
- `images`
- `initial_multi_solution_score`
- `dataset_name`
- `source_problem_id`
- `subject`
- `requires_image`
- `text_dominant`
- `alignment_status`
- `solvability_score`
- `clean_pool_status`
- `clean_decision`
- `sample_path`
- `metadata`

也就是说，**当前实现做了明显的“字段压缩 + 运行态重组”**。

## 4.3 第三步：方法规划

样例中，`initial_multi_solution_score=0.56`，因此当前实现为这道题规划了 2 个方法：

1. **方法 1**：局部角追 / 线性对路线；
2. **方法 2**：较大图形 / 平行线或三角形路线。

这一步已经体现出设计里“按多解分数决定方法数”的规则，说明**多方法规划机制已经落地**。

## 4.4 第四步：求解、答案比对、CoT 验证与 polish

### 方法 1 的操作

当前实现对方法 1 做了这些事：

- 生成 `CoT_raw`；
- 生成 `model_answer=65`；
- 与标准答案比对，判定 `is_answer_match=true`；
- 多轮 CoT verify / polish；
- 最终得到 `is_final_CoT_qualified=true` 和 `CoT_final`。

也就是说，这条方法被认定为“可进入后续节点化”的合格方法。

### 方法 2 的操作

方法 2 同样：

- 给出了 `model_answer=65`；
- 答案也判对了；
- 但 4 轮 verifier 都没有真正放行；
- 最终 `is_final_CoT_qualified=false`。

这说明当前实现已经区分了两层门：

1. **答案对不对**；
2. **推理能不能作为标注事实沉淀**。

这是当前实现里做得比较对的一点。

## 4.5 第五步：构建 `PTK` 底座

对照 ready 原 JSON，可以看出当前实现对 ready 做了“重新抽取底座”的操作，而不是直接复用 ready 现成节点：

### `problem_record`

从 ready 中复制/重组出：

- 题号；
- 规范化题干；
- 规范化答案；
- 图片路径；
- 数据集信息；
- 对齐状态与可解性分数。

### `p_facts`

当前实现尝试从视觉上下文中重新提 perception facts。

但在这个例子上，ready 自带的视觉结构太粗，所以最终产出的 perception facts 要么非常泛，要么在 full bundle 中干脆转而依赖 CoT 里的视觉叙述。

### `t_facts`

当前实现把 ready 里的题面核心目标重写成文本条件，比如：

- `Find m∠VXW.`

### `k_atoms`

当前实现不是直接使用 ready 里的 `node_records` 中已有知识节点，而是重新让 agent 生成适用知识库，比如：

- linear pair rule；
- triangle angle sum；
- vertical angles；
- angles around a point 等。

这说明：**当前实现对 ready 不是“直接搬运”，而是“把 ready 当条件，再重新生成标注期知识底座”。**

## 4.6 第六步：只对合格方法做 claim 抽取

样例 full bundle 里，只能看到方法 1 进入了 `claim_sequences`。这说明当前实现做了如下过滤：

- 方法 1：答案正确 + CoT 合格 -> 进入 claim extraction；
- 方法 2：答案正确但 CoT 不合格 -> 不进入 claim extraction。

这是与设计一致的。

在这道题上，方法 1 被拆成了 7 个 claim，大意分别是：

1. `XV` 在 `X` 处落在一条直线上；
2. 因此存在 `XV` 的对向射线；
3. `115°` 角位于 `XW` 与该对向射线之间；
4. `115°` 角与 `∠VXW` 构成线性对；
5. 线性对和为 `180°`；
6. `180 - 115 = 65`；
7. 最终答案 `65°`。

## 4.7 第七步：claim -> r_nodes

当前实现没有直接复用 ready 中已有的 `node_records` 作为最终 `r_nodes`，而是做了两层处理：

1. ready 里的 `node_records` 只作为上游结构化上下文的一部分，被摘要后喂给 agent；
2. 最终 `r_nodes` 是从“合格 CoT 拆出来的 claims”重新归纳出来的。

所以在这个例子上，当前实现对 ready `node_records` 的操作是：

- **不是直接采用**；
- **而是降级为辅助上下文**；
- **然后重新生成本阶段自己的 `r_nodes`**。

这也是为什么 ready 里明明已经有一些 `target_slot / answer_claim / perception_fact / quality_signal` 节点，但 full bundle 里最后的 `r_nodes` 仍然是另一套新节点体系。

## 4.8 第八步：从节点组织出 `solution_library`

样例中，当前实现把方法 1 的节点整理成了 1 个解法族：

- `solution_id=s1`
- `required_r_ids`：核心必要节点
- `optional_r_ids`：可选节点
- `ordered_core_path`：主路径顺序
- `supported_answer=65`

这意味着当前实现已经在做“方法级结果 -> 题目级解法族”的抽象。

## 4.9 第九步：做证据绑定，但绑定质量还不稳

样例里可以看到：

- 对“线性对规则”这种知识节点，系统能绑定到 `k_atom`；
- 但对“图里存在 115°、图里有对向射线、图里角相邻”这类感知/桥接节点，证据常常绑不上；
- 因此出现大量 `LOW` 支撑和空的 `p_fact_ids`。

所以当前实现对 ready 的这部分操作，准确说是：

- **试图从 ready 构建证据绑定**；
- **但当 ready 视觉事实不够细时，绑定会退化成弱绑定甚至空绑定**。

## 4.10 第十步：构建 trace mapping index

当前实现还会把最终节点库再压一层，形成评测期可用的索引：

- 节点目录；
- 解法族所需节点；
- 核心路径顺序。

这说明系统已经开始为“后续模型输出与标准节点库对齐”做准备。

---

## 5. 这个样例里，哪些 ready 内容被真正使用了，哪些没有被真正使用

## 5.1 被真正使用的内容

| ready 内容 | 使用方式 |
| --- | --- |
| `clean_pool_entries.pool_status` | 用于筛选是否进入标注阶段 |
| `clean_problem_record.normalized_question_text` | 变成 `question_text` |
| `clean_problem_record.normalized_answer_text` | 变成 `standard_answer` |
| `candidate_problem_record.initial_multi_solution_score` | 决定方法数 |
| `requires_image / text_dominant` | 进入运行态与 prompt 上下文 |
| `alignment_status / solvability_score` | 进入运行态与 prompt 上下文 |
| `asset_registry_record / raw_asset_bundle / normalized_assets` 中的图片路径信息 | 解析图片路径 |
| `text_structure_records / visual_structure_records / node_records` | 被摘要后作为 prompt 的结构化上下文 |
| 整个 `sample_record` | 在 full bundle 中原样保留，便于追溯 |

## 5.2 没有被真正强利用的内容

| ready 内容 | 现状 |
| --- | --- |
| `rewrite_report` | 设计上应当有价值，但当前主逻辑里没有显式使用痕迹 |
| `open_ended_problem_variants` | 只体现在计数或被动保留，没有进入关键推理链 |
| ready 内已有的细粒度 `node_records` | 没直接转成最终 `r_nodes` |
| ready 的视觉信息 | 实际过于粗，无法稳定支撑几何级细粒度推理 |

---

## 6. trace eval 例子说明了什么

trace 样例 [pipeline2/examples/smoke_trace.json](../pipeline2/examples/smoke_trace.json) 的 `pred_cot` 很短，只说了“图中角关系 + consistent angle chase -> 答案 65”。

当前实现对它做了这些操作：

1. 判断答案是否正确：结果正确；
2. 对 `pred_cot` 再拆 claim：拆成 3 个 claim；
3. 与现有节点库映射：只命中了最终答案节点；
4. 计算命中率：总命中率和必要命中率都只有 `0.25`；
5. 因为答案正确、CoT 验证通过、命中率低，所以触发 `novelty_candidate=true`；
6. 但 novelty detector 最终给的是 `old_family_branch_extension`；
7. 所以最终没有写入 patch，见 [pipeline2/outputs_smoke/trace_eval/dataset_patches.jsonl](../pipeline2/outputs_smoke/trace_eval/dataset_patches.jsonl)。

这说明当前 Phase 3 已经有了“触发、判断、不写 patch”的完整分支，但它还没有强到足以稳定地区分“真正新解”和“只是写法不同”。

---

## 7. 最终回答

## 7.1 现在的实现有什么问题？哪些做到了，哪些没做到？

### 做到的

- 主链路已经存在，不是空设计；
- `ready -> 方法规划 -> 求解 -> 答案检查 -> CoT 验证/修复 -> claim -> r_nodes -> solution_library -> trace eval` 已经能跑；
- verified CoT 子流水线已经比较完整；
- “只让合格 CoT 进入节点化”这一门做对了；
- trace novelty / patch 的外壳也已经具备。

### 没做到或问题很大的

- 没有真正做到强多模态 grounding；
- verifier 还会放行弱支撑 CoT；
- 节点化会继承上游 hallucination；
- evidence binding 形式上有了，实质上常常很弱；
- `Coverage Hunter` 没做；
- patch 回流仍是启发式；
- 一些 ready 关键信息没有真正利用；
- coverage 与评测指标存在失真；
- 仓库里的试验产物存在版本漂移。

## 7.2 对照试验样例与 ready 原问题 JSON，现在的实现对哪些部分做了哪些操作？

### 已做的操作

- **筛选**：从 ready 中筛出 `ready_for_annotation` 的题；
- **字段压缩**：把 ready 大 JSON 压成运行态问题对象；
- **图片解析**：从多处候选路径里解析出本地图片；
- **多解规划**：根据 `initial_multi_solution_score=0.56` 规划 2 个方法；
- **求解与过滤**：两个方法都求解，但只保留“答案对且 CoT 合格”的方法 1；
- **底座重建**：重新生成 `problem_record / p_facts / t_facts / k_atoms`；
- **节点化**：把方法 1 的 CoT 拆成 claims，再归纳为 `r_nodes`；
- **解法聚合**：把节点组织成 1 个 `solution_library` 项；
- **评测建索引**：生成 `trace_mapping_index`；
- **轨迹评测**：把预测 trace 再拆 claims、做匹配、做 novelty 判断。

### 没做或没做好

- 没有把 ready 里的 `rewrite_report`、`open_ended_problem_variants` 真正纳入核心决策；
- 没有直接复用 ready 已有的 `node_records` 作为最终标注节点；
- 没有从 ready 的视觉结构中稳定恢复足够细的几何事实；
- 没有形成设计里那种严格可信的“证据先行，再节点化”的闭环。

---

## 8. 建议的判断方式

如果要给当前实现一个更准确的定位，我会这样描述：

> 当前 [pipeline2](../pipeline2) 不是“还没开始做”，而是“Phase 1 已经比较成型，Phase 2/3 也已经有代码和样例，但整体还处在 **能跑通原型**、尚未达到 **严格标注生产级** 的阶段”。

其中最优先要补的不是更多模块，而是三件事：

1. 把视觉 grounding 做实；
2. 把运行态与最终产物的标准输出收敛到一套；
3. 把 evidence binding / trace metric / patch 回流从启发式升级为严格约束。
