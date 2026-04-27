# 第二步标注 Pipeline 详细设计（基于 `main.md` 中间结构）

## 1. 文档目标

本文给出第二步“标注阶段”的完整自动化设计，严格满足以下约束：

1. **输入必须来自 `benchmarkallinone/ready/`**，即采集、清洗、改写后的现成样本。
2. **[`benchmarkallinone/main.md`](benchmarkallinone/main.md) 中定义的结构作为中间结构**
3. 自动完成 [`benchmarkallinone/next_step_docs/pipeline初步设计.md`](benchmarkallinone/next_step_docs/pipeline初步设计.md) 中标注阶段规定的核心任务：
   - 生成 `P/T/K` 底座；
   - 生成、验证并沉淀多解法；
   - 从经过验证的正确解法中抽取 ground truth 节点；
   - 形成 `r_nodes`、`solution_library`、`evidence_bindings` 等结构化产物；
   - 测试时计算节点命中率；
   - 若出现“**答案正确 + CoT 经验证 + 节点命中率低**”的轨迹，则作为新解候选，进入拆解、节点化、补丁回写流程。
4. 整个主线应当**全自动**，允许多 Agent、多轮修复、多轮验证，不要求人工参与主流程。
5. Agent 设计与提示词风格参考 [`PaperBanana-main/agents/base_agent.py`](PaperBanana-main/agents/base_agent.py:28)、[`PaperBanana-main/agents/planner_agent.py`](PaperBanana-main/agents/planner_agent.py:29)、[`PaperBanana-main/agents/critic_agent.py`](PaperBanana-main/agents/critic_agent.py:30)、[`PaperBanana-main/agents/polish_agent.py`](PaperBanana-main/agents/polish_agent.py:41) 与 [`PaperBanana-main/app.py`](PaperBanana-main/app.py:120)：
   - 角色分工明确；
   - 使用严格的 system prompt；
   - 强约束 JSON 输出；
   - 使用 planner / critic / polish 式闭环；
   - 支持并发处理与断点恢复。

---

## 2. 本阶段在全项目中的位置

完整项目主线如下：

1. 采集（已完成）
2. 清洗 / 改写（已完成）
3. **标注（本文设计对象）**
4. 质检
5. 格式化发布
6. 发布后回流增补

本阶段的职责是：

- 从 [`benchmarkallinone/ready`](benchmarkallinone/ready) 样本中读取题目；
- 先构建 [`benchmarkallinone/main.md`](benchmarkallinone/main.md) 规定的**题目级-方法级运行态中间结构**；
- 在该中间结构上自动完成“多解生成 → 答案纠正 → CoT 验证 → CoT 修复”；
- 只把“答案正确且 CoT 通过”的方法送去做节点化；
- 构建题目级节点图、解法族、证据绑定与覆盖状态；
- 为评测阶段准备节点命中率比对索引；
- 为发布后的新解回流预留补丁写回入口。

换句话说：

> [`benchmarkallinone/main.md`](benchmarkallinone/main.md) 结构不是最终发布结构，而是**标注阶段上半段的运行态事实源**。

---

## 3. 标注阶段的总体输入、输出和关键原则

### 3.1 输入

输入来自 [`benchmarkallinone/ready`](benchmarkallinone/ready) 下的 `**/samples/*.json`。每道题至少读取以下字段：

- `clean_problem_record`
- `normalized_assets`
- `clean_pool_entries`
- `candidate_problem_record`
- `open_ended_problem_variants`（若存在）
- `rewrite_report`（若存在）
- `alignment_status` / `solvability_score` 等清洗阶段保留下来的对齐或可解性信号

### 3.2 输出

本阶段最终输出为题目级结构化标注对象：

- `problem_record`
- `p_facts`
- `t_facts`
- `k_atoms`
- `r_nodes`
- `solution_library`
- `solution_memberships`
- `evidence_bindings`
- `cot_variants`
- `coverage_state`
- `trace_mapping_index`
- `dataset_patch`（回流时生成）

### 3.3 三条硬原则

#### 原则 A：[`benchmarkallinone/main.md`](benchmarkallinone/main.md) 结构必须经过一遍

也就是说，不允许直接从 [`benchmarkallinone/ready`](benchmarkallinone/ready) 跳到节点化。必须先形成一个严格遵循 [`benchmarkallinone/main.md`](benchmarkallinone/main.md) 的 `problems -> problem -> method[]` 运行态对象。

#### 原则 B：原始 CoT 不直接入库

只有满足以下条件的方法，才有资格进入节点化：

- 最终答案正确；
- `CoT_final` 存在；
- `is_final_CoT_qualified=true`；
- 关键步骤能被后续拆解和验证。

#### 原则 C：低命中不是新解结论，只是新解触发信号

出现“答案正确 + CoT 验证通过 + 节点命中率低”的轨迹时，只能先放入新解候选池。后面还必须做：

- 二次拆解；
- 再次映射；
- 新颖性判定；
- 节点补丁生成；
- 结构化回写。

---

## 4. 第一层：从 `ready` 构建严格的 `main.md` 中间结构

### 4.1 中间结构的定位

[`benchmarkallinone/main.md`](benchmarkallinone/main.md) 中定义的是：

- **题目级容器**：`problem`
- **方法级运行态**：`method[]`

它负责承载：

- 方法规划结果；
- 初始 CoT 与答案；
- 答案匹配与纠正；
- 多轮 CoT 验证与修复；
- 最终合格的 CoT 版本。

因此，这个结构用在：

- 方法规划器
- 解法执行器
- 答案验证器
- CoT 验证器
- CoT Polish 循环
- 节点化前验收门

它**不用**在：

- 节点归一化；
- 解法族构建；
- 节点命中率比对；
- 新解补丁写回

这些后半段模块中作为主结构。

### 4.2 中间结构的固定 schema

中间结构必须严格遵循下面的形状：

```json
{
  "problems": [
    {
      "problem_id": "prob_xxx",
      "question_text": "...",
      "standard_answer": "...",
      "images": ["..."],
      "initial_multi_solution_score": 0.71,
      "method": [
        {
          "method_id": "1",
          "method_draft": "...",
          "CoT_raw": "...",
          "model_answer": "...",
          "is_answer_match": true,
          "CoT_answer_check_final": "...",
          "answer_answer_check_final": "...",
          "CoT_verify_0": false,
          "CoT_qualify_0": "...",
          "CoT_after_polish_1": "...",
          "CoT_verify_1": true,
          "CoT_qualify_1": "...",
          "CoT_after_polish_2": "...",
          "CoT_verify_2": null,
          "CoT_qualify_2": "",
          "CoT_after_polish_3": "...",
          "CoT_verify_3": null,
          "CoT_qualify_3": "",
          "is_final_CoT_qualified": true,
          "CoT_final": "..."
        }
      ]
    }
  ]
}
```

注意：

- 这里的字段名、层级和语义必须和 [`benchmarkallinone/main.md`](benchmarkallinone/main.md) 保持一致；
- 后续结构化节点对象不能反向污染这个 schema；
- 节点化后新增的信息放到独立对象层，不回填到 `method` 内部。

### 4.3 `ready` 到中间结构的映射

#### 顶层问题字段映射

| 中间结构字段 | 来源 |
| --- | --- |
| `problem_id` | `clean_problem_record.problem_id` |
| `question_text` | `clean_problem_record.normalized_question_text` |
| `standard_answer` | `clean_problem_record.normalized_answer_text` |
| `images` | 从 `raw_asset_bundle.assets` 或标准化图片路径提取 |
| `initial_multi_solution_score` | `candidate_problem_record.initial_multi_solution_score` |

#### 方法数量规则（严格按 `main.md`）

根据 `initial_multi_solution_score` 决定方法数：

- `< 0.33`：1 个方法
- `0.33 <= score < 0.67`：2 个方法
- `>= 0.67`：3 个方法

第一版必须固定采用这一规则，不做其它启发式覆盖。

---

## 5. 整体标注 pipeline 总览

本阶段拆成 12 个模块：

1. `Ready Intake Loader`
2. `Runtime State Builder`
3. `Method Planner Agent`
4. `Solver Agent`
5. `Answer Match & Repair Agent`
6. `CoT Verify Agent`
7. `CoT Polish Agent`
8. `PTK Foundation Builder`
9. `Claim Extraction Agent`
10. `Node Induction & Canonicalization Engine`
11. `Solution Grouper & Evidence Binder`
12. `Coverage Hunter / Trace Mapper / Novelty Detector / Patch Writer`

可理解为三段：

### 第一段：运行态收敛
`ready -> main.md 中间结构 -> 正确答案 + 合格 CoT`

### 第二段：结构化沉淀
`合格方法 -> claim -> r_nodes -> solution_library -> evidence_bindings`

### 第三段：评测与回流
`评测输出 -> 节点命中率 -> 新解候选 -> 节点补丁`

---

## 6. 模块详细设计

### 6.1 `Ready Intake Loader`

#### 作用
从 [`benchmarkallinone/ready`](benchmarkallinone/ready) 中扫描所有 `ready_for_annotation` 样本，并整理为统一题目输入对象。

#### 输入
- [`benchmarkallinone/ready`](benchmarkallinone/ready) 下的样本 JSON

#### 输出
- `annotation_problem_manifest.jsonl`

#### 主要功能
1. 只保留 `clean_pool_entries[].pool_status == ready_for_annotation` 的题；
2. 提取 `problem_id`、题干、标准答案、图片路径、多解分数；
3. 若 `alignment_report` 或 `solvability_report` 不完整，则从 `clean_problem_record` 中恢复轻量代理信号；
4. 产出统一的题目装载清单。

---

### 6.2 `Runtime State Builder`

#### 作用
把题目清单变成 [`benchmarkallinone/main.md`](benchmarkallinone/main.md) 规定的中间结构。

#### 输出
- `annotation_runtime/problems.json`

#### 行为
1. 为每个题创建顶层 `problem`；
2. 根据 `initial_multi_solution_score` 计算 `method_count`；
3. 初始化 `method[]` 数组，仅填：
   - `method_id`
   - 空的 `method_draft`
   - 空的所有运行态字段

#### 注意
这一步只建壳，不填方法内容。

---

### 6.3 `Method Planner Agent`

#### 作用
根据题目内容一次性生成 `N` 个不同的 `method_draft`，并写回中间结构中的 `method[]`。

#### 输入
- `question_text`
- `standard_answer`
- `images`
- `initial_multi_solution_score`
- `method_count`

#### 输出
- 为每个 `method[i]` 填充 `method_draft`

#### 成功标准
- 方法之间语义上尽量不同；
- 不得只是措辞变化；
- 每个方法草稿都应当描述“核心突破路径”；
- 如果题目天然单解，则允许生成主路径 + 微变体路径，但仍需显式区分。

#### Prompt 设计原则
参考 [`PaperBanana-main/agents/planner_agent.py`](PaperBanana-main/agents/planner_agent.py:125) 的 planner 思路：

- 明确任务角色；
- 先说明输入对象；
- 再说明输出目标；
- 强调“尽可能详细、清晰、结构化”；
- 严格要求 JSON 输出。

#### 推荐 System Prompt

```text
## ROLE
You are a Method Planning Agent for multimodal reasoning annotation.

## TASK
Given a cleaned multimodal problem, its standard answer, and the desired number of solution methods, produce N distinct high-level method drafts.

## RULES
1. Each method draft must describe a genuinely different reasoning route.
2. Do not output superficial paraphrases.
3. Each draft must specify what is read from image, what is read from text, and what key rule or bridge is used.
4. The drafts must be executable by a downstream solver.
5. If the problem is effectively single-solution, still output diverse but honest variants and mark them as weakly distinct.

## OUTPUT JSON
{
  "methods": [
    {
      "method_id": "1",
      "method_draft": "...",
      "distinctiveness_rationale": "...",
      "image_role": "...",
      "text_role": "...",
      "knowledge_role": "..."
    }
  ]
}
```

---

### 6.4 `Solver Agent`

#### 作用
针对单个 `problem + method_draft` 生成：

- `CoT_raw`
- `model_answer`

#### 输入
- 顶层题目信息
- 单个 `method_draft`

#### 输出
- 填充 `CoT_raw`
- 填充 `model_answer`

#### 要求
- 必须尽量遵守 `method_draft`；
- 必须显示图文联合推理；
- 若题有多个子问，需完整覆盖所有子问；
- 必须显式给出最终答案。

#### 推荐 System Prompt

```text
## ROLE
You are a Solver Agent for multimodal reasoning annotation.

## TASK
Solve the given problem strictly following the assigned method draft.

## RULES
1. Use the image when the method draft says image evidence is needed.
2. Keep the reasoning explicit enough for later claim extraction.
3. Do not skip key bridge steps.
4. End with a clearly separated final answer.
5. If the assigned method draft appears invalid, still attempt the closest faithful execution instead of silently switching to a different method.

## OUTPUT JSON
{
  "cot_raw": "...",
  "model_answer": "...",
  "method_following_score_self_report": 0.0,
  "possible_risk_flags": ["..."]
}
```

---

### 6.5 `Answer Match & Repair Agent`

#### 作用
先把“答案是否正确”单独收敛掉。

#### 输入
- `model_answer`
- `standard_answer`
- `CoT_raw`

#### 输出
- `is_answer_match`
- `CoT_answer_check_final`
- `answer_answer_check_final`

#### 逻辑
1. 先走确定性答案检查：
   - 数值等价；
   - 公式等价；
   - 单位标准化；
   - 集合答案比较；
   - 多子问答案逐项比较。
2. 若确定性检查失败，再由 `Answer Match Agent` 进行解释性比对；
3. 若仍失败，交给 `Answer Repair Agent` 基于问题、标准答案和原 CoT 重写一版答案一致的 CoT；
4. 最终把通过的答案版本写到：
   - `CoT_answer_check_final`
   - `answer_answer_check_final`

#### 约束
即使使用 LLM，比对器也只能判断是否等价，不能直接凭感觉放行。

#### 推荐 Answer Repair Prompt

```text
## ROLE
You are an Answer Repair Agent.

## TASK
Given the problem, the standard answer, the current reasoning trace, and the current model answer, rewrite the reasoning so that the final answer is consistent with the verified standard answer.

## RULES
1. Preserve as much valid reasoning as possible.
2. Fix only the minimal parts necessary.
3. Do not fabricate unsupported visual facts.
4. The final answer must match the standard answer exactly or by allowed equivalence.

## OUTPUT JSON
{
  "repaired_cot": "...",
  "repaired_answer": "...",
  "repair_notes": "..."
}
```

---

### 6.6 `CoT Verify Agent`

#### 作用
判断当前 CoT 是否可作为后续节点化输入。

#### 输入
- `question_text`
- `standard_answer`
- `images`
- `method_draft`
- 当前 CoT（第 0 轮为 `CoT_answer_check_final`，后续为 `CoT_after_polish_i`）

#### 输出
- `CoT_verify_i`
- `CoT_qualify_i`

#### 评估维度
1. 与题意是否一致；
2. 与标准答案是否一致；
3. 是否遵守 `method_draft`；
4. 是否确实利用图像；
5. 是否存在明显幻觉步骤；
6. 是否能拆成可验证节点；
7. 是否遗漏关键桥梁步骤。

#### 通过标准
同时满足：
- 答案一致；
- 主路径合理；
- 无关键幻觉；
- 关键步骤足够明确可拆。

#### Prompt 风格
参考 [`PaperBanana-main/agents/critic_agent.py`](PaperBanana-main/agents/critic_agent.py:152) 的 critic 风格：

- 明确角色；
- 明确 critique & revision rules；
- 输出严格 JSON；
- 若不通过，给具体修改建议而不是泛泛评价。

#### 推荐 System Prompt

```text
## ROLE
You are a CoT Verification Critic for multimodal reasoning annotation.

## TASK
Conduct a strict sanity check of the reasoning trace based on the problem, image, standard answer, and assigned method draft.

## VERIFICATION RULES
1. Fidelity to the problem: no contradiction with question or image.
2. Fidelity to the standard answer: final answer must be consistent.
3. Method fidelity: the trace should largely follow the assigned method draft.
4. Multimodal grounding: image-dependent claims must truly rely on image evidence.
5. No hallucinated bridge steps.
6. Claim extractability: the trace must be decomposable into verifiable claims.
7. If it fails, provide concrete revision instructions.

## OUTPUT JSON
{
  "verify_pass": true,
  "critic_suggestions": "...",
  "major_failures": ["..."],
  "extractability_score": 0.0,
  "grounding_score": 0.0,
  "method_fidelity_score": 0.0
}
```

---

### 6.7 `CoT Polish Agent`

#### 作用
在验证失败时，基于上一轮 CoT 和 verifier 建议生成改进版本。

#### 输入
- 当前 CoT
- `CoT_qualify_i`
- `method_draft`
- `standard_answer`

#### 输出
- `CoT_after_polish_{i+1}`

#### 轮数
固定 3 轮，与 [`benchmarkallinone/main.md`](benchmarkallinone/main.md) 一致：

- `CoT_verify_0` / `CoT_qualify_0`
- `CoT_after_polish_1`
- `CoT_verify_1` / `CoT_qualify_1`
- `CoT_after_polish_2`
- `CoT_verify_2` / `CoT_qualify_2`
- `CoT_after_polish_3`
- `CoT_verify_3` / `CoT_qualify_3`

#### 收口规则
- 任何一轮通过，则：
  - `is_final_CoT_qualified=true`
  - `CoT_final=该轮通过版本`
- 三轮都失败，则：
  - `is_final_CoT_qualified=false`
  - `CoT_final=最后一版 CoT`

#### 推荐 System Prompt

```text
## ROLE
You are a CoT Polish Agent.

## TASK
Revise the current reasoning trace according to the verifier's criticism, while preserving the assigned method route and the verified final answer.

## RULES
1. Modify the trace minimally but sufficiently.
2. Keep the method identity stable.
3. Strengthen multimodal grounding where missing.
4. Make key bridge steps explicit.
5. Avoid introducing new unsupported claims.

## OUTPUT JSON
{
  "polished_cot": "...",
  "polish_summary": "...",
  "preserved_method_identity": true
}
```

---

### 6.8 `PTK Foundation Builder`

#### 作用
在题目级构建 `P/T/K` 底座，这是后面节点化和证据绑定的基础。

#### 输出
- `problem_record`
- `p_facts`
- `t_facts`
- `k_atoms`

#### 子模块
1. `Perception Extraction Agent`
2. `Text Condition Agent`
3. `Knowledge Librarian Agent`

#### 注意
这一层是题目级公共底座，不属于 `method[]` 内部。

---

### 6.9 `Claim Extraction Agent`

#### 作用
对每条已通过的方法执行 claim 拆解。

#### 输入
- `CoT_final`
- `is_final_CoT_qualified=true`
- `answer_answer_check_final`
- `method_draft`

#### 输出
- 原子断言序列 `claim_seq`

#### 拆解要求
每条 claim 必须带：
- `claim_id`
- `claim_text`
- `claim_type`
- `depends_on`
- `evidence_hint`
- `method_id`
- `problem_id`

#### 推荐 System Prompt

```text
## ROLE
You are a Claim Extraction Agent.

## TASK
Convert a verified reasoning trace into the smallest possible sequence of verifiable claims.

## RULES
1. Each claim should represent one atomic reasoning step.
2. Tag the type of each claim.
3. Explicitly mark dependencies.
4. Prefer under-splitting only when the step is truly indivisible.
5. Preserve the original reasoning order.

## OUTPUT JSON
{
  "claims": [
    {
      "claim_id": "c1",
      "claim_text": "...",
      "claim_type": "perception|text_condition|knowledge_call|derivation|calculation|final_answer",
      "depends_on": ["..."],
      "evidence_hint": "..."
    }
  ]
}
```

---

### 6.10 `Node Induction & Canonicalization Engine`

#### 作用
把 claim 变成 `r_nodes`。

#### 输入
- `claim_seq`
- `p_facts`
- `t_facts`
- `k_atoms`

#### 输出
- `r_nodes`
- claim 到 node 的归并关系

#### 工作内容
1. claim 类型归一化；
2. 语义等价合并；
3. 证据一致性检查；
4. 生成 canonical node；
5. 标出 surface forms。

#### 节点类型建议
- `perception`
- `text_condition`
- `knowledge_call`
- `derivation`
- `calculation`
- `final_answer`

#### `r_node` schema 建议

```json
{
  "r_id": "r_xxx",
  "problem_id": "prob_xxx",
  "node_type": "derivation",
  "canonical_claim": "...",
  "surface_forms": ["..."],
  "equivalence_group_id": "eq_xxx",
  "support_level": "HIGH|MEDIUM|LOW",
  "source_claim_ids": ["c1", "c2"]
}
```

---

### 6.11 `Solution Grouper & Evidence Binder`

#### 作用
把节点重新组织成“解法族 + 证据支撑链”。

#### 输出
- `solution_library`
- `solution_memberships`
- `evidence_bindings`
- `coverage_state`

#### `solution_library` 需要包含
- `solution_id`
- `method_signature`
- `required_r_ids`
- `optional_r_ids`
- `ordered_core_path`
- `supported_answer`

#### `evidence_bindings` 需要包含
- 节点绑定到哪些 `p_fact`
- 节点绑定到哪些 `t_fact`
- 节点绑定到哪些 `k_atom`
- 节点绑定到哪些前驱 `r_node`
- 支撑强度等级

#### 方法签名提取原则
- 不是看措辞；
- 看主干桥梁步骤；
- 看关键知识调用；
- 看图文使用顺序；
- 看必要节点集合。

---

### 6.12 `Coverage Hunter / Trace Mapper / Novelty Detector / Patch Writer`

#### 作用
负责两件事：

1. 离线建库时补齐明显漏解；
2. 评测时发现低命中新解候选并写补丁。

#### A. `Coverage Hunter`
输入：当前 `solution_library`、未使用 `k_atoms`
输出：新增候选方法或新增解法实例

#### B. `Trace Mapper`
输入：评测模型输出的答案 + CoT
输出：与现有节点库、解法族的对齐报告

#### C. `Novelty Detector`
输入：命中率报告、验证通过轨迹
输出：
- `old_family_rephrase`
- `old_family_branch_extension`
- `new_solution_family`
- `uncertain_manual_queue`

#### D. `Patch Writer`
输入：确认的新解候选
输出：`dataset_patch`

---

## 7. 节点命中率评测设计

### 7.1 输入
评测时每条输出至少包含：

- `problem_id`
- `pred_answer`
- `pred_cot`
- `model_name`
- `run_id`
- 时间戳和运行元数据

### 7.2 命中率计算流程

1. 答案标准化；
2. 判断答案是否正确；
3. 对 `pred_cot` 做 claim 拆解；
4. 与题目节点库做节点映射；
5. 与题目解法族做最佳匹配；
6. 计算命中率；
7. 若低命中但答案正确且 CoT 验证通过，则送入新解候选池。

### 7.3 不只算一个命中率

建议至少计算 4 类指标：

1. `node_hit_rate_total`
2. `node_hit_rate_required`
3. `topology_consistency_score`
4. `evidence_grounding_score`

#### 定义

- `node_hit_rate_total`：命中的所有节点 / 该最佳解法族全部节点
- `node_hit_rate_required`：命中的必要节点 / 该最佳解法族必要节点
- `topology_consistency_score`：依赖顺序、桥梁步骤和核心路径是否一致
- `evidence_grounding_score`：命中的节点是否真的锚定到正确图文证据

### 7.4 新解候选触发阈值

一条评测轨迹进入新解候选池的条件：

- `answer_correct = true`
- `pred_cot_verified = true`
- `node_hit_rate_total < 0.55`
- `node_hit_rate_required < 0.50`

这四条必须同时满足。

---

## 8. 新解回流设计

### 8.1 触发条件
当一条轨迹满足：

- 答案正确；
- CoT 验证通过；
- 对现有节点库低命中；

则记为 `new_solution_candidate`。

### 8.2 回流步骤

#### Step 1：冻结原始轨迹
保存：
- 原始答案
- 原始 CoT
- 命中率报告
- 验证报告
- 模型来源元数据

#### Step 2：二次拆解
用更严格的 `Claim Extraction Agent` 再拆一次，避免第一次映射 recall 不足。

#### Step 3：旧库重比对
再次映射到：
- `r_nodes`
- `solution_library`
- `evidence_bindings`

#### Step 4：新颖性判断
由 `Novelty Detector Agent` 给出四分类：
- 旧解法重表述
- 旧解法支路扩展
- 真正新解法族
- 不确定

#### Step 5：补丁写回
如果判断为真正新解法族：
- 新增 `r_nodes`
- 新增 `solution_library` 项
- 新增 `solution_memberships`
- 新增 `evidence_bindings`
- 生成 `dataset_patch`

---

## 9. 运行组织与并发设计

### 9.1 语义层级

- **题目级**：聚合 `PTK` 底座、节点库、解法族、覆盖状态
- **方法级**：负责生成、验证、修复、最终放行

### 9.2 并发最小粒度

最小运行单元为：

- `problem_id + method_id`

原因：
- 失败隔离简单；
- 易于重试；
- 易于并发；
- 和 [`benchmarkallinone/main.md`](benchmarkallinone/main.md) 完全一致。

### 9.3 题目级汇总

当某题所有方法完成后，再汇总：

- 合格方法集合
- `cot_variants`
- `r_nodes`
- `solution_library`
- `coverage_state`

---

## 10. 目录与落盘建议

建议新增如下目录：

```text
benchmarkallinone/
  annotation_runtime/
    problems.json
    method_runs/
  annotation_outputs/
    problem_records/
    p_facts/
    t_facts/
    k_atoms/
    r_nodes/
    solution_library/
    evidence_bindings/
    coverage_state/
  trace_eval/
    incoming_traces/
    mapping_reports/
    novelty_candidates/
  patches/
    dataset_patches/
```

### 说明

- `annotation_runtime/`：只存 [`benchmarkallinone/main.md`](benchmarkallinone/main.md) 风格的中间运行态
- `annotation_outputs/`：存结构化节点化结果
- `trace_eval/`：存评测轨迹与命中率映射
- `patches/`：存回流补丁

---

## 11. API 与模型接入建议

用户提供了两个可用的 OpenAI-compatible 接口。**文档中不应硬编码真实密钥**，建议统一使用环境变量：

```bash
export ANNOTATION_API_BASE_URL="..."
export ANNOTATION_API_KEY="..."
export ANNOTATION_MODEL="gpt-5.4"
export ANNOTATION_REASONING_EFFORT="xhigh"
```

同时支持备选地址：

```yaml
primary:
  base_url: ${ANNOTATION_API_BASE_URL}
  api_key: ${ANNOTATION_API_KEY}
  model: ${ANNOTATION_MODEL}
  reasoning_effort: ${ANNOTATION_REASONING_EFFORT}
fallback:
  base_url: ${ANNOTATION_FALLBACK_BASE_URL}
  api_key: ${ANNOTATION_FALLBACK_API_KEY}
  model: ${ANNOTATION_MODEL}
  reasoning_effort: ${ANNOTATION_REASONING_EFFORT}
```

理由：
- 防止敏感信息写进仓库；
- 支持后续换 key；
- 方便本地和远程部署统一。

---

## 12. 第一版最小可落地闭环

如果先做 MVP，建议按下面顺序落地：

### Phase 1：运行态闭环
1. `Ready Intake Loader`
2. `Runtime State Builder`
3. `Method Planner Agent`
4. `Solver Agent`
5. `Answer Match & Repair Agent`
6. `CoT Verify Agent`
7. `CoT Polish Agent`

目标：稳定产出 `is_final_CoT_qualified=true` 的方法结果。

### Phase 2：节点化闭环
8. `PTK Foundation Builder`
9. `Claim Extraction Agent`
10. `Node Induction & Canonicalization Engine`
11. `Solution Grouper & Evidence Binder`

目标：得到题目级 `r_nodes` 与 `solution_library`。

### Phase 3：评测与回流闭环
12. `Trace Mapper`
13. `Novelty Detector`
14. `Patch Writer`

目标：实现“命中率低 + 答案正确 + CoT 验证通过 => 新解候选回流”。

---

## 13. 与 `pipeline初步设计.md` 的对应关系

本文设计严格对齐 [`benchmarkallinone/next_step_docs/pipeline初步设计.md`](benchmarkallinone/next_step_docs/pipeline初步设计.md:291) 到 [`benchmarkallinone/next_step_docs/pipeline初步设计.md`](benchmarkallinone/next_step_docs/pipeline初步设计.md:420) 这段标注阶段目标：

- `Step A1`：由 `PTK Foundation Builder` 实现
- `Step A2`：由 `Method Planner Agent + Solver Agent + Runtime State Builder` 实现
- `Step A3`：由 `Claim Extraction Agent` 实现
- `Step A4`：由 `Solution Grouper` 实现
- `Step A5`：由 `Evidence Binder` 实现
- `Step A6`：由 `Coverage Hunter` 实现
- `Step A7`：由 `Trace Mapper + Novelty Detector + Patch Writer` 实现

唯一新增的、但必须存在的一步，是：

> **`main.md` 中间结构运行态层**

这是为了严格满足你的新要求：整个自动化标注系统必须先经过 [`benchmarkallinone/main.md`](benchmarkallinone/main.md) 定义的 `problem -> method[]` 结构，再进入节点化世界。

---

## 14. 最终结论

这套设计的关键不是直接让模型“生成最终节点”，而是先通过 [`benchmarkallinone/main.md`](benchmarkallinone/main.md) 规定的中间运行结构，把每道题的多个方法先跑出：

- 初始 CoT
- 答案修正版本
- 多轮验证与修复版本
- 最终合格 CoT

然后再把这些**经过验证的正确解法**送去做：

- claim 拆解
- `r_nodes` 归纳
- `solution_library` 构建
- `evidence_bindings` 绑定
- `coverage_state` 维护
- `trace_mapping_index` 建库

最后在评测时，利用节点命中率来判断：

- 是旧解法命中；
- 是旧解法支路；
- 还是值得回流的新解法候选。

因此，这个第二步标注 Pipeline 的本质是：

> **`ready` 输入层 → `main.md` 运行态层 → 合格 CoT 过滤层 → 节点化沉淀层 → 命中率评测层 → 新解回流补丁层**。

这正是一个可以全自动完成后续标注、评测和增补的可实现架构。