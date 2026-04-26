# pipeline2 实现说明

## 1. 这套实现解决什么问题

[`benchmarkallinone/pipeline2`](benchmarkallinone/pipeline2) 是第二步标注阶段的完整实现原型。它的目标不是继续做采集和清洗，而是直接接在 [`benchmarkallinone/ready`](benchmarkallinone/ready) 后面，完成以下工作：

1. 从 ready 样本中读取已经清洗、改写、标准化好的题目。
2. 基于题目构造一个题目级运行态对象，并为每道题生成多个方法分支。
3. 对每个方法分支执行：
   - 方法规划；
   - CoT 与答案生成；
   - 答案校验；
   - CoT 验证；
   - CoT 修复；
   - 最终通过判定。
4. 对通过的方法做结构化沉淀：
   - 构建 `P/T/K` 底座；
   - claim 拆解；
   - 节点归纳；
   - 解法族构建；
   - 证据绑定；
   - 覆盖状态维护。
5. 为后续评测准备节点命中率索引。
6. 支持对外部模型轨迹做评测：
   - 节点映射；
   - 命中率计算；
   - 新解候选判定；
   - patch 生成。

这套实现吸收了 [`benchmarkallinone/pipeline_problem_2_CoT-main/src/pipeline_langgraph.py`](benchmarkallinone/pipeline_problem_2_CoT-main/src/pipeline_langgraph.py:1) 的分层 LangGraph 执行方式，但把它扩展到了 [`benchmarkallinone/next_step_docs/第二步标注Pipeline详细设计.md`](benchmarkallinone/next_step_docs/第二步标注Pipeline详细设计.md) 所定义的更完整目标。

---

## 2. 目录结构与每个文件的职责

当前 [`benchmarkallinone/pipeline2`](benchmarkallinone/pipeline2) 的核心文件如下：

- [`benchmarkallinone/pipeline2/__init__.py`](benchmarkallinone/pipeline2/__init__.py)
- [`benchmarkallinone/pipeline2/main.py`](benchmarkallinone/pipeline2/main.py)
- [`benchmarkallinone/pipeline2/config.py`](benchmarkallinone/pipeline2/config.py)
- [`benchmarkallinone/pipeline2/clients.py`](benchmarkallinone/pipeline2/clients.py)
- [`benchmarkallinone/pipeline2/utils.py`](benchmarkallinone/pipeline2/utils.py)
- [`benchmarkallinone/pipeline2/models.py`](benchmarkallinone/pipeline2/models.py)
- [`benchmarkallinone/pipeline2/prompts.py`](benchmarkallinone/pipeline2/prompts.py)
- [`benchmarkallinone/pipeline2/ready_loader.py`](benchmarkallinone/pipeline2/ready_loader.py)
- [`benchmarkallinone/pipeline2/agents.py`](benchmarkallinone/pipeline2/agents.py)
- [`benchmarkallinone/pipeline2/pipeline.py`](benchmarkallinone/pipeline2/pipeline.py)
- [`benchmarkallinone/pipeline2/configs/default_pipeline2.yaml`](benchmarkallinone/pipeline2/configs/default_pipeline2.yaml)
- [`benchmarkallinone/pipeline2/configs/smoke_pipeline2.yaml`](benchmarkallinone/pipeline2/configs/smoke_pipeline2.yaml)
- [`benchmarkallinone/pipeline2/examples/smoke_trace.json`](benchmarkallinone/pipeline2/examples/smoke_trace.json)
- 运行入口 [`benchmarkallinone/run_pipeline2.py`](benchmarkallinone/run_pipeline2.py)

下面按模块逐个解释。

---

## 3. 启动入口模块

## 3.1 [`benchmarkallinone/run_pipeline2.py`](benchmarkallinone/run_pipeline2.py)

这个文件是整个第二步 pipeline 的顶层启动脚本。

### 输入
它不直接读取业务数据，而是负责：
- 定位项目根目录；
- 把 [`benchmarkallinone`](benchmarkallinone) 根目录加入 `sys.path`；
- 导入 [`pipeline2.main`](benchmarkallinone/pipeline2/main.py) 并启动。

### 输出
它本身不产出业务文件，只负责把命令交给 [`pipeline2.main`](benchmarkallinone/pipeline2/main.py)。

### 为什么需要它
因为当前仓库主目录已经有 [`benchmarkallinone/run_pipeline.py`](benchmarkallinone/run_pipeline.py) 用于第一阶段采集清洗，所以第二阶段单独提供一个 [`benchmarkallinone/run_pipeline2.py`](benchmarkallinone/run_pipeline2.py) 更清晰，也便于将两个阶段彻底解耦。

---

## 3.2 [`benchmarkallinone/pipeline2/main.py`](benchmarkallinone/pipeline2/main.py)

这是一个极薄的适配层。

### 输入
- Python 运行时进入该模块时，直接导入 [`pipeline2.pipeline.main()`](benchmarkallinone/pipeline2/pipeline.py:870)。

### 输出
- 不单独产生业务对象。

### 作用
它的作用只是让 `python -m pipeline2.main` 与 `python benchmarkallinone/run_pipeline2.py` 两种方式都能工作。

---

## 4. 配置模块

## 4.1 [`benchmarkallinone/pipeline2/config.py`](benchmarkallinone/pipeline2/config.py)

这个模块定义了整个 pipeline 的配置结构。

### 核心配置类

#### [`ModelEndpointConfig`](benchmarkallinone/pipeline2/config.py:13)
表示一个可调用的 OpenAI-compatible 模型端点。

字段解释：
- `name`：端点名字。不是模型名字，而是路由中的逻辑名字，例如 `primary` 或 `fallback`。
- `base_url`：接口基础地址，用来拼成 `/chat/completions` 请求地址。
- `api_key`：该端点对应的密钥。当前实现推荐用环境变量注入，而不是写死到仓库里。
- `model`：真正发给服务端的模型名，例如 `gpt-5.4`。
- `reasoning_effort`：推理强度参数，当前用于 OpenAI-compatible 请求体中的 `reasoning_effort` 字段。
- `temperature`：采样温度，用来控制输出稳定性。
- `timeout_seconds`：单次请求超时时间。
- `enabled`：这个端点是否启用。禁用时不会发请求。

#### [`PathsConfig`](benchmarkallinone/pipeline2/config.py:25)
表示整个阶段的目录路径配置。

字段解释：
- `ready_root`：ready 样本根目录。第二步标注阶段只从这里读取上游结果。
- `output_root`：第二步所有输出的统一根目录。
- `checkpoint_db_path`：LangGraph checkpoint 所用数据库路径。如果当前环境没有 sqlite checkpointer，就会自动退化到内存版 saver，但路径字段仍保留，方便未来恢复 sqlite。

#### [`RuntimeConfig`](benchmarkallinone/pipeline2/config.py:32)
表示运行时策略。

字段解释：
- `include_manual_review`：是否允许把 `manual_review` 样本也纳入第二步标注。关闭时只处理 `ready_for_annotation`。
- `max_problems`：最多处理多少道题。`0` 表示不限制。
- `max_problem_workers`：题目级最大并发数。
- `max_images_per_problem`：每题最多加载几张图。
- `save_runtime_snapshots`：是否保存运行态快照。
- `save_problem_bundles`：是否把题目级 bundle 完整落盘。
- `enable_trace_patch_writes`：评测时如果判定为可写 patch，是否真的落盘。

#### [`ThresholdConfig`](benchmarkallinone/pipeline2/config.py:43)
表示一系列阈值。

字段解释：
- `method_score_thresholds`：多解分数到方法数量的映射阈值。当前是 `0.33 / 0.67`。
- `novelty_total_threshold`：总节点命中率低于该阈值时，才可能进入新解候选。
- `novelty_required_threshold`：必要节点命中率低于该阈值时，才可能进入新解候选。

#### [`ModelRouterConfig`](benchmarkallinone/pipeline2/config.py:51)
表示模型路由。

字段解释：
- `primary`：主模型端点。
- `fallback`：备用模型端点。主端点失败时会自动尝试。

#### [`Pipeline2Config`](benchmarkallinone/pipeline2/config.py:68)
是总配置对象。

### 关键方法

#### [`from_yaml()`](benchmarkallinone/pipeline2/config.py:74)
作用：
- 读取 YAML；
- 展开环境变量；
- 组装成 dataclass 配置对象。

#### [`resolve_path()`](benchmarkallinone/pipeline2/config.py:113)
作用：
- 把相对路径解释成相对于 [`benchmarkallinone`](benchmarkallinone) 根目录的绝对路径；
- 保证整个 pipeline 目录定位一致。

---

## 5. HTTP 客户端与模型路由模块

## 5.1 [`benchmarkallinone/pipeline2/clients.py`](benchmarkallinone/pipeline2/clients.py)

这个模块负责所有 LLM 的 HTTP 调用。

### [`OpenAICompatibleClient`](benchmarkallinone/pipeline2/clients.py:21)
这是第二步 pipeline 自己的 OpenAI-compatible 客户端。

#### 输入
- 一个 [`ModelEndpointConfig`](benchmarkallinone/pipeline2/config.py:13)；
- system prompt；
- user prompt 或多模态 user parts。

#### 输出
- 一个解析后的 JSON 字典；
- 失败时返回 `None`。

#### 内部统计字段 `usage_totals`
这些不是业务字段，而是运行监控字段：
- `request_count`：一共发了多少次请求。
- `successful_request_count`：成功解析出 JSON 的请求数。
- `failed_request_count`：失败请求数。
- `retry_count`：因错误重试的次数。
- `text_request_count`：文本请求数。
- `multimodal_request_count`：多模态请求数。
- `requests_with_usage`：服务端返回 usage 的请求数。
- `prompt_tokens` / `completion_tokens` / `total_tokens`：累计 token。
- `cached_tokens`：缓存命中 token。
- `reasoning_tokens`：推理 token。
- `total_request_seconds`：累计请求耗时。
- `last_error`：最后一次错误信息。

#### 关键方法

##### [`_build_payload()`](benchmarkallinone/pipeline2/clients.py:66)
负责把：
- `model`
- `system prompt`
- `user content`
- `temperature`
- `response_format`
- `reasoning_effort`

组装成最终请求体。

##### [`_post_json()`](benchmarkallinone/pipeline2/clients.py:78)
负责：
- 发 HTTP 请求；
- 重试；
- 解析 usage；
- 从 `choices[0].message.content` 中抽 JSON；
- 把 usage 和耗时附加到返回对象。

##### [`chat_json()`](benchmarkallinone/pipeline2/clients.py:206)
单文本输入的 JSON 调用入口。

##### [`chat_json_with_images()`](benchmarkallinone/pipeline2/clients.py:209)
文本 + 图片的 JSON 调用入口。

### [`ModelRouter`](benchmarkallinone/pipeline2/clients.py:219)

这个类负责主端点和备用端点的路由逻辑。

#### 输入
- 主 [`OpenAICompatibleClient`](benchmarkallinone/pipeline2/clients.py:21)
- 备用 [`OpenAICompatibleClient`](benchmarkallinone/pipeline2/clients.py:21)

#### 输出
- 优先返回主端点的结果；
- 主端点失败则自动切换到备用端点；
- 若主备都无法返回合法 JSON，调用方会通过 [`benchmarkallinone/pipeline2/agents.py`](benchmarkallinone/pipeline2/agents.py) 中的契约检查直接报错。

#### 作用
这样可以避免在每个 agent 函数里手写主备逻辑，统一由 router 负责。当前保留的唯一 fallback 是**端点级主备路由**，不再保留任何内容级启发式回退。

---

## 6. 通用工具模块

## 6.1 [`benchmarkallinone/pipeline2/utils.py`](benchmarkallinone/pipeline2/utils.py)

这个模块放的是和业务无关但会被大量复用的小工具。

### 典型工具函数

#### [`read_json()`](benchmarkallinone/pipeline2/utils.py:31)
读 JSON 文件。

#### [`write_json()`](benchmarkallinone/pipeline2/utils.py:36)
写 JSON 文件。第二步的大部分产物都是通过它落盘。

#### [`write_jsonl()`](benchmarkallinone/pipeline2/utils.py:42)
写 JSONL。评测映射报告、novelty 候选列表、patch 列表等就是用它输出的。

#### [`normalize_whitespace()`](benchmarkallinone/pipeline2/utils.py:58)
做空白和换行规范化。几乎所有文本字段写入前都要过它，保证后续比较稳定。

#### [`canonicalize_answer_text()`](benchmarkallinone/pipeline2/utils.py:72)
把答案文本转换成更适合比较的规范形式，用于答案等价判断。

#### [`extract_json_object()`](benchmarkallinone/pipeline2/utils.py:98)
从模型返回文本中提取 JSON 对象。因为模型偶尔会输出多余文本，所以要做容错提取。

#### [`split_multiline_answer()`](benchmarkallinone/pipeline2/utils.py:132)
把多行答案拆开，用于多子问答案比对。

#### [`split_or_alternatives()`](benchmarkallinone/pipeline2/utils.py:138)
把 `0 or sqrt(3)/2` 这样的多合法答案拆成多个候选，便于判等。

---

## 7. 数据模型模块

## 7.1 [`benchmarkallinone/pipeline2/models.py`](benchmarkallinone/pipeline2/models.py)

这个模块定义了运行过程中的主要状态结构。

### [`BatchState`](benchmarkallinone/pipeline2/models.py:7)
表示 batch graph 的状态。

字段解释：
- `batch_id`：本次运行的批次标识。
- `problems`：当前批次里要处理的题目列表，或已经处理完成的题目 bundle 列表。

### [`ProblemState`](benchmarkallinone/pipeline2/models.py:12)
表示 problem graph 的状态。

字段解释：
- `batch_id`：当前所属批次。
- `problem`：题目级运行态对象。这里会保存 `problem_id`、题干、答案、图片、method 列表等。
- `problem_record`：题目正式记录，是进入节点化后的主对象。
- `p_facts`：感知事实集合，每条表示一个视觉层的客观事实。
- `t_facts`：题干条件集合，每条表示一个文本条件、目标或子问。
- `k_atoms`：知识原子集合，每条表示一个潜在可用的知识规则。
- `cot_variants`：保存题目下所有方法的 CoT 变体和状态摘要。
- `claim_sequences`：每条合格方法拆出的 claim 序列。
- `r_nodes`：归一化后的推理节点。
- `claim_mappings`：claim 到 `r_node` 的归并映射关系。
- `solution_library`：题目下的解法族列表。
- `solution_memberships`：节点属于哪个解法族、是 required 还是 optional。
- `evidence_bindings`：节点绑定到了哪些证据。
- `coverage_state`：当前解法覆盖程度。
- `trace_mapping_index`：评测映射所需的索引摘要。
- `problem_bundle`：最终汇总对象，把上述题目级产物打包在一起。

### [`MethodState`](benchmarkallinone/pipeline2/models.py:31)
表示 method graph 的状态。

字段解释：
- `batch_id`：当前批次。
- `problem`：所属题目。
- `method`：当前方法对象。
- `current_cot_text`：当前轮正在验证或修复的 CoT 文本。
- `current_cot_key`：当前 CoT 对应哪个字段，例如 `CoT_raw` 或 `CoT_after_polish_1`。
- `current_answer`：当前版本对应的答案文本。

### [`LoadedReadyProblem`](benchmarkallinone/pipeline2/models.py:40)
表示从 ready 成功装载出来的一道题。

字段解释：
- `problem_id`：题目唯一 ID。
- `question_text`：清洗后的题干。
- `standard_answer`：清洗后的标准答案。
- `images`：解析出来的图片文件路径列表。
- `initial_multi_solution_score`：来自清洗阶段的多解潜力分数，用来决定方法数量。
- `dataset_name`：数据集名。
- `source_problem_id`：上游数据集中原始题号。
- `subject`：学科，例如数学、物理。
- `requires_image`：是否必须看图。
- `text_dominant`：是否以文本为主。
- `alignment_status`：图文对齐状态，例如 `good`、`risky`。
- `solvability_score`：可解性分数。
- `clean_pool_status`：样本目前在清洗池中的状态，如 `ready_for_annotation`。
- `clean_decision`：清洗阶段的最终结论，比如 `pass`、`review`。
- `sample_path`：该样本 JSON 文件的路径。
- `sample_record`：原始样本 JSON 全对象。
- `metadata`：额外辅助信息，比如 question_type、多解策略、风险标记等。

#### [`to_runtime_problem()`](benchmarkallinone/pipeline2/models.py:60)
作用是把 `LoadedReadyProblem` 转换成运行态题目对象，作为 problem graph 的直接输入。

### [`ClaimRecord`](benchmarkallinone/pipeline2/models.py:81)
表示一条原子 claim。

字段解释：
- `claim_id`：claim 自己的唯一标识。
- `problem_id`：这条 claim 属于哪道题。
- `method_id`：这条 claim 属于哪种方法分支。
- `claim_text`：这一步推理的文本内容。
- `claim_type`：claim 的类型，比如 perception、derivation、knowledge_call。
- `depends_on`：这一步依赖哪些前面的 claim。
- `evidence_hint`：粗粒度证据提示，比如 visual/text/knowledge。

### [`NodeRecord`](benchmarkallinone/pipeline2/models.py:103)
表示归一化后的 `r_node`。

字段解释：
- `r_id`：节点唯一 ID。
- `problem_id`：所属题目。
- `node_type`：节点类型。
- `canonical_claim`：规范化后的标准表述。
- `surface_forms`：该节点的所有表面表达变体。
- `equivalence_group_id`：等价分组 ID。
- `support_level`：当前节点的支撑强度，例如 HIGH / MEDIUM / LOW。
- `source_claim_ids`：这个节点由哪些 claim 合并而来。

### [`SolutionRecord`](benchmarkallinone/pipeline2/models.py:127)
表示一条解法族。

字段解释：
- `solution_id`：解法族 ID。
- `problem_id`：所属题目。
- `method_signature`：对该解法族主路径的摘要描述。
- `required_r_ids`：这条解法族一定会经过的关键节点。
- `optional_r_ids`：可能出现但不是必需的节点。
- `ordered_core_path`：主干节点顺序。
- `supported_answer`：该解法族导向的答案。
- `member_method_ids`：哪些方法实例归属于这条解法族。

---

## 8. Prompt 模块

## 8.1 [`benchmarkallinone/pipeline2/prompts.py`](benchmarkallinone/pipeline2/prompts.py)

这个模块集中管理所有 agent 的 system prompt 和 user prompt builder。

### 为什么单独拆出来
因为当前第二步不是一个单一的“调用模型返回答案”脚本，而是一套多 agent 系统。把 prompt 全放在一个文件里，有两个好处：

1. 更容易迭代 prompt，而不会污染业务逻辑。
2. 可以直接模仿 [`PaperBanana-main/agents/planner_agent.py`](PaperBanana-main/agents/planner_agent.py:125) 与 [`PaperBanana-main/agents/critic_agent.py`](PaperBanana-main/agents/critic_agent.py:152) 这种“角色 + 任务 + 规则 + JSON 输出”风格。

### 已实现的 agent prompt
当前已经实现：
- `METHOD_PLANNER_SYSTEM_PROMPT`
- `SOLVER_SYSTEM_PROMPT`
- `ANSWER_EQUIVALENCE_SYSTEM_PROMPT`
- `ANSWER_REPAIR_SYSTEM_PROMPT`
- `COT_VERIFY_SYSTEM_PROMPT`
- `COT_POLISH_SYSTEM_PROMPT`
- `PERCEPTION_EXTRACTION_SYSTEM_PROMPT`
- `TEXT_CONDITION_SYSTEM_PROMPT`
- `KNOWLEDGE_LIBRARIAN_SYSTEM_PROMPT`
- `CLAIM_EXTRACTION_SYSTEM_PROMPT`
- `NODE_INDUCTION_SYSTEM_PROMPT`
- `SOLUTION_GROUPER_SYSTEM_PROMPT`
- `EVIDENCE_BINDER_SYSTEM_PROMPT`
- `TRACE_MAPPER_SYSTEM_PROMPT`
- `NOVELTY_DETECTOR_SYSTEM_PROMPT`

### user prompt builder 的作用
例如：
- [`build_method_planner_user_prompt()`](benchmarkallinone/pipeline2/prompts.py)
- [`build_solver_user_prompt()`](benchmarkallinone/pipeline2/prompts.py)
- [`build_cot_verify_user_prompt()`](benchmarkallinone/pipeline2/prompts.py)

它们的作用是把：
- 题目内容；
- 标准答案；
- 方法草稿；
- 图像信息；
- 已有节点库；
- 评测轨迹

拼成适合对应 agent 的输入。

也就是说：
**system prompt 负责定义角色，user prompt builder 负责组织上下文。**

### claim 链路 prompt 瘦身（最新）
当前已先做一轮低风险 claim prompt 瘦身，目标是在**不改变最终 JSON schema / 输出契约**的前提下，先降低 `ClaimExtraction` / `ClaimVerify` / `ClaimPolish` 的单次请求体积：
- 把三者 user prompt 中超长的自然语言规则段改写成更短的 numbered rules，保留核心约束（原子性、局部 bridge、depends_on 只能指向 earlier claim IDs、wrap-around 支撑、synthesis 靠后、minimum/optimal 的最短局部支撑、变量消元路径保持等）；
- 在 `annotation_modules.py` 中为 claim 侧新增 `_select_claim_context(...)`，对传入 prompt 的 `p_facts / t_facts / k_atoms` 做窄化；
- `ClaimExtraction` 现在只拼接 compact PTK foundation（默认 `p/t/k` 各截到 8/8/8）；
- `ClaimVerify` / `ClaimPolish` 当前默认只携带较窄的 PTK 子集（默认 `8/8/6`），避免把整份 PTK 无差别塞入 claim 审核/修补请求。

在此基础上，`ClaimVerify` 已进一步拆成**三段窄审计**，但仍复用原有的 `CLAIM_VERIFY_SYSTEM_PROMPT` 输出契约：
- `ClaimVerifyStructure`：只看 claim 原子性、顺序、depends_on 合法性、bridge 局部性；
- `ClaimVerifyGrounding`：只看 PTK / CoT grounding、wrap-around 支撑、minimum/optimal 的最短支撑链；
- `ClaimVerifyGlobal`：只看轻量的全局顺序与 synthesis/answer 位置关系；
- 三段结果会在代码里 merge，最终仍回收到原先 `pass / critical_issues / revision_instructions / atomicity_score / dependency_score / grounding_score` 这套字段上。

这轮改动的定位是**先缩 payload、先降 429 风险**，同时把最肥的 claim verify 从“一坨全审计”改成“多段窄审计”；但还没有把 claim 主链路彻底改造成新的多 agent 协议。也就是说：
- `extract -> verify -> polish` 仍然是同一闭环；
- 只是 `verify` 内部已经被拆成多次更窄的调用；
- 后续如果需要，还可以继续把 `ClaimPolish` 对应拆成更细的 repair phases。

### p_facts 符号保真约束（最新）
针对近期暴露出的 `p_facts` 符号污染 / 标签漂移问题，当前已在 PTK 的 perception 链路上补充低风险约束，仍**不改变 JSON schema / 输出契约**：
- `PerceptionExtraction` 明确要求对 labels、legends、axis text、circuit/component markings、geometry point names、subscripts、superscripts、Greek letters、operators、units 等**尽量逐视觉保真**，不要擅自 paraphrase、normalize、translate、或“修正”为猜测的标准写法；
- 若关键符号看不清，优先显式写成视觉不清 / ambiguous，而不是猜一个看起来合理的 canonical string；
- `PTKFoundationCritic` 现在会把 guessed symbol normalization、mojibake-like corruption、以及把 text-explicit givens 泄漏到 `p_facts` 里的情况视为明确问题；对关键 `p_facts` 中可见字符串被破坏的情况允许直接 `pass=false`；
- `PTK_P_FACTS_POLISH` 在修补时被明确要求：优先保留可见字符串、删除猜测性正规化、删除解释性含义扩写、删除误混入 `p_facts` 的 text-only givens。

这轮改动的目标不是让模型具备真正 OCR 级确定性，而是先把 `p_facts` 的默认偏好从“可读性整理”拉回到“视觉字符串保真优先”，减少同题重跑时的符号漂移与污染扩散。


---

## 9. Ready 装载模块

## 9.1 [`benchmarkallinone/pipeline2/ready_loader.py`](benchmarkallinone/pipeline2/ready_loader.py)

这个模块负责从 ready 样本中挑题并转成第二步 pipeline 可用的 `LoadedReadyProblem`。

### 关键函数

#### [`_iter_sample_paths()`](benchmarkallinone/pipeline2/ready_loader.py:14)
递归扫描 ready 根目录下所有 `prob_*.json`。

#### [`_extract_status()`](benchmarkallinone/pipeline2/ready_loader.py:101)
读取 `clean_pool_entries`，判断这道题是否可以进入第二步。当前规则：
- 默认只接受 `ready_for_annotation`
- 如果配置允许，也接受 `manual_review`

#### [`_resolve_candidate_path()`](benchmarkallinone/pipeline2/ready_loader.py:33)
这是图像路径修复的核心函数。

它的作用是：
- 把 `raw_asset_bundle`、`asset_registry_record`、`asset_records`、`normalized_assets.image_regions` 里出现的图片路径转成当前磁盘上真实存在的文件路径；
- 兼容不同样本里出现的：
  - 相对路径；
  - artifacts 路径；
  - crop 路径；
  - ready 内部 run 目录路径。

#### [`_collect_image_paths()`](benchmarkallinone/pipeline2/ready_loader.py:49)
负责从样本 JSON 中尽可能多地收集图片路径候选源，然后交给 `_resolve_candidate_path()` 去找真实文件。

它会尝试读取：
- 顶层 `image_paths`
- `asset_registry_record.image_manifest[].path`
- `raw_asset_bundle.assets[].storage_uri`
- `normalized_assets.image_regions[].source_uri/storage_uri`
- `asset_records[].source_uri/storage_uri`

如果这些都找不到，还会 fallback 到类似：
- `artifacts/images/<problem_id>_primary.png`
- `artifacts/crops/<problem_id>_primary_roi.png`

#### [`load_ready_problem()`](benchmarkallinone/pipeline2/ready_loader.py:115)
这是装载单题的主入口。

##### 输入
- `sample_path`：样本 JSON 文件路径。
- `workspace_root`：当前工作根目录。
- `include_manual_review`：是否允许 review 样本进入。
- `max_images`：最多装几张图。

##### 输出
- 一个 [`LoadedReadyProblem`](benchmarkallinone/pipeline2/models.py:40)
- 如果该题不满足入场条件，则返回 `None`

##### 做的事情
- 判状态；
- 抽 `problem_id`；
- 抽规范化题干与答案；
- 抽图片路径；
- 抽多解分数、学科、对齐状态、可解性分数等；
- 打包成统一题目对象。

#### [`discover_ready_problems()`](benchmarkallinone/pipeline2/ready_loader.py:177)
遍历整个 ready 根目录，批量加载题目。

##### 输入
- ready 根目录
- include_manual_review
- max_problems
- max_images

##### 输出
- `List[LoadedReadyProblem]`

---

## 10. Agent 业务模块

## 10.1 [`benchmarkallone/pipeline2/agents.py`](benchmarkallinone/pipeline2/agents.py)

这个模块是真正的业务逻辑核心。它把 prompt、router 和严格契约检查结合起来，提供“一个个可调用的业务原子”。当前版本已经移除内容级 fallback：如果 LLM 没有返回满足 schema 的 JSON，就直接失败，不再自动补模板结果。

### 当前的上下文裁剪策略
`agents.py` 里的 `_augment_prompt_with_ready_context(...)` 不再总是附加同一份完整 ready 摘要，而是根据 agent 名称选择不同 profile：
- 只保留该 agent 真正常用的结构块；
- 限制 `text_segments / targets / entities / visual_entities / visual_relations / upstream_nodes` 数量；
- 对长字符串做截断；
- 把 ready summary 明确降级为“compact trusted upstream summary”，避免它在语义上压过原题、原 CoT、图像本身。

这样做的目标不是改变任务定义，而是减少单次请求的 prompt 体积，尤其是 PTK / claim / validation 这类容易叠上下文的阶段。

### 10.1.1 方法规划

#### [`plan_methods()`](benchmarkallinone/pipeline2/agents.py)
##### 输入
- `router`
- `problem`
- `method_count`

##### 输出
- `List[Dict]`，每个元素是一条方法草稿

##### 字段解释
每个返回的方法对象包含：
- `method_id`：方法编号。
- `method_draft`：该方法要走的核心路径。
- `distinctiveness_rationale`：为什么它和其他方法不同。
- `image_role`：这条方法如何使用图像。
- `text_role`：这条方法如何使用题干文本。
- `knowledge_role`：这条方法的知识桥梁是什么。

##### 当前实现特征
- 必须由 LLM 返回合法且数量足够的方法草稿。
- 如果主备模型都无法返回符合契约的 JSON，则直接失败。

### 10.1.2 方法求解

#### [`solve_method()`](benchmarkallinone/pipeline2/agents.py)
##### 输入
- `router`
- `problem`
- `method`

##### 输出
- `cot`：生成的 CoT
- `answer`：生成的答案
- `meta`：本次生成的原始元信息

##### 当前实现特征
- 有图时仍会优先使用多模态调用。
- 如果模型不可用、被拦截、或返回的 JSON 不含必需字段，系统会直接失败，不再生成兜底 CoT。

### 10.1.3 答案判等

#### [`deterministic_answer_match()`](benchmarkallinone/pipeline2/agents.py)
这是不依赖模型的确定性答案比对器。

##### 输入
- `problem`
- `predicted_answer`

##### 输出
- `is_equivalent`：整体是否等价。
- `reason`：判定原因，例如 `deterministic_match`、`part_count_mismatch`。
- `part_results`：逐子答案比较结果。

##### 字段解释
`part_results` 中每一项包含：
- `standard_part`：标准答案中的这一部分。
- `predicted_part`：预测答案对应部分。
- `is_equivalent`：该部分是否通过。
- `reason`：该部分通过或失败的原因。

#### [`judge_answer_equivalence()`](benchmarkallinone/pipeline2/agents.py)
这是更高一层的判等函数。

##### 工作方式
- 先走 [`deterministic_answer_match()`](benchmarkallinone/pipeline2/agents.py)
- 如果失败，再调用 `ANSWER_EQUIVALENCE_SYSTEM_PROMPT` 对模糊情况做 LLM judge

### 10.1.9 结构校验的分批调用
在 [`benchmarkallinone/pipeline2/verification_modules.py`](benchmarkallinone/pipeline2/verification_modules.py) 里，`ClaimSetValidation` 和 `NodeSetValidation` 已经支持按 batch 拆分：
- claim set 默认按较小批次分批审查；
- node set 也按较小批次拆开；
- 每批仍然要求返回原有 JSON schema；
- 代码侧会把多批结果重新合并回一个总报告，并保持原有字段结构（`pass`、`*_judgments`、`global_failures`、`summary` 等）。

这样做的主要目的，是避免把整份 claims / nodes / mappings 一口气塞进单次请求，降低 prompt 臃肿和超长上下文失稳风险，同时尽量不改上游下游的数据契约。


#### [`repair_answer()`](benchmarkallinone/pipeline2/agents.py)
##### 输入
- 问题对象
- 方法对象
- 原 CoT
- 原预测答案

##### 输出
- `cot`：修复后的 CoT
- `answer`：修复后的答案
- `notes`：修复说明

### 10.1.5 CoT 验证与修复

#### [`verify_cot()`](benchmarkallinone/pipeline2/agents.py)
##### 输出字段
- `verify_pass`：这条 CoT 是否通过。
- `critic_suggestions`：如果不通过，应如何修改。
- `major_failures`：主要失败项列表。
- `extractability_score`：是否容易拆成 claim。
- `grounding_score`：图像 grounding 程度。
- `method_fidelity_score`：对方法草稿的忠实度。

#### [`polish_cot()`](benchmarkallinone/pipeline2/agents.py)
##### 输出字段
- `polished_cot`：修复后的 CoT。
- `polish_summary`：本次修复摘要。
- `preserved_method_identity`：是否保持住原方法身份。

### 10.1.6 PTK 底座

#### [`extract_ptk()`](benchmarkallinone/pipeline2/agents.py)
##### 输出字段
- `problem_record`：题目级主记录。
- `p_facts`：视觉事实。
- `t_facts`：文本条件。
- `k_atoms`：知识原子。

##### 当前 repair 策略
PTK foundation 现在不是再让 `PTKFoundationPolish` 每轮“整份重写整个 PTK”，而是优先走**分阶段修补**：
- critic 先给出 revision instructions；
- 代码会根据指令判断优先需要修的是 `p_facts`、`t_facts` 还是 `k_atoms`；
- 对应 section 用单独 patch agent 做局部重写；
- 其他 section 只作为 reference context 保留，不在该轮一起重写；
- 多个 section 需要修改时，再按 section 逐个 patch 并回填。

这样做的主要目的，是降低一次 polish 把本来好的 section 也一起改坏的概率，尤其是避免 `p_facts` 在整份重写时被误修空。

##### `problem_record` 字段解释
- `problem_id`：题目标识。
- `question_text`：题干。
- `standard_answer`：标准答案。
- `images`：图片路径。
- `dataset_name`：数据集。
- `source_problem_id`：原始题号。
- `subject`：学科。
- `requires_image`：是否必须看图。
- `text_dominant`：是否文本主导。
- `alignment_status`：图文对齐状态。
- `solvability_score`：可解性分数。
- `sample_path`：ready 样本路径。

##### `p_facts` 字段解释
每条视觉事实包含：
- `p_id`：视觉事实 ID。
- `fact_text`：这个视觉事实到底说了什么。
- `confidence`：抽取可信度。
- `visual_anchor`：它锚定的视觉来源，例如 `ready_visual_structure`。

##### `t_facts` 字段解释
每条文本条件包含：
- `t_id`：文本事实 ID。
- `fact_text`：题干中抽出的条件文本。
- `fact_role`：这条文本事实是什么角色，例如 `given`、`goal`、`constraint`、`subquestion`。

##### `k_atoms` 字段解释
每条知识原子包含：
- `k_id`：知识原子 ID。
- `knowledge_text`：具体规则内容。
- `knowledge_type`：规则类型，例如 `theorem`、`formula`、`principle`。
- `applicability_note`：适用范围说明。

### 10.1.7 claim 提取

#### [`extract_claims()`](benchmarkallinone/pipeline2/agents.py)
##### 输入
- 合格 CoT
- 问题对象
- 方法对象

##### 输出
- `List[ClaimRecord]`

##### 每条 claim 的字段含义
- `claim_id`：claim 编号。
- `problem_id`：属于哪道题。
- `method_id`：属于哪种方法。
- `claim_text`：原子化后的步骤文本。
- `claim_type`：步骤类型。
- `depends_on`：依赖的上一层 claim。
- `evidence_hint`：提示后续应该去绑定哪类证据。

### 10.1.8 节点归纳

#### [`induce_nodes()`](benchmarkallinone/pipeline2/agents.py)
##### 输出
- `r_nodes`
- `claim_mappings`

##### `r_nodes` 字段解释
- `r_id`：节点 ID。
- `problem_id`：所属题目。
- `node_type`：节点类型。
- `canonical_claim`：规范节点文本。
- `surface_forms`：所有表面表达。
- `equivalence_group_id`：等价归组编号。
- `support_level`：支撑强度。
- `source_claim_ids`：源 claim 列表。

##### `claim_mappings` 字段解释
每条映射包含：
- `claim_id`：原始 claim。
- `r_id`：被归并到哪个节点。
- `equivalence_group_id`：它属于哪个等价组。

### 10.1.9 解法聚类与证据绑定

#### [`group_solutions()`](benchmarkallinone/pipeline2/agents.py)
##### 输出
- `solution_library`
- `solution_memberships`
- `coverage_state`

##### `solution_library` 字段解释
- `solution_id`：解法族 ID。
- `problem_id`：所属题目。
- `method_signature`：该解法族的主干方法签名。
- `required_r_ids`：必要节点列表。
- `optional_r_ids`：可选节点列表。
- `ordered_core_path`：核心节点顺序。
- `supported_answer`：这条解法支持的答案。
- `member_method_ids`：归属到该解法族的方法实例。

##### `solution_memberships` 字段解释
每条 membership 记录说明：
- `solution_id`：属于哪条解法族。
- `r_id`：对应哪个节点。
- `membership_role`：是 `required` 还是 `optional`。
- `order_index`：在该解法中的顺序位置。

##### `coverage_state` 字段解释
- `problem_id`：对应题目。
- `method_count`：这道题一共尝试了多少方法。
- `qualified_method_count`：多少方法通过验证。
- `solution_count`：当前归纳出多少解法族。
- `node_count`：当前题目已有多少节点。
- `used_k_atom_ids`：已经被解法用到的知识原子。
- `unused_k_atom_ids`：还没有被用到的知识原子。
- `coverage_near_saturated`：是否接近覆盖饱和。

#### [`bind_evidence()`](benchmarkallinone/pipeline2/agents.py)
##### 输出
- `evidence_bindings`

##### 每条 evidence binding 的字段解释
- `r_id`：该证据绑定属于哪个节点。
- `p_fact_ids`：它依赖哪些视觉事实。
- `t_fact_ids`：它依赖哪些文本事实。
- `k_atom_ids`：它依赖哪些知识原子。
- `predecessor_r_ids`：它依赖哪些前驱节点。
- `support_strength`：整体支撑强度。
- `binding_rationale`：为什么这样绑定。

### 10.1.10 命中率评测与新解回流

#### [`build_trace_mapping_index()`](benchmarkallinone/pipeline2/agents.py)
用于构建评测阶段的加速索引。

##### 字段解释
- `problem_id`：这份索引服务于哪道题。
- `node_catalog`：节点目录，每个节点包含 `r_id`、canonical claim、surface forms、node type。
- `solutions`：解法目录，每条解法包含 `solution_id`、required/optional 节点和主路径顺序。

#### [`map_trace()`](benchmarkallinone/pipeline2/agents.py)
##### 输入
- 题目 bundle
- 一条评测轨迹
- novelty 阈值
- lexical match 阈值

##### 输出字段解释
- `problem_id`：对应题目。
- `model_name`：产生这条轨迹的模型。
- `run_id`：这次运行 ID。
- `answer_correct`：答案是否正确。
- `pred_cot_verified`：这条 CoT 是否通过验证。
- `best_solution_id`：最相近的已知解法族。
- `matched_r_ids`：命中的所有节点。
- `matched_required_r_ids`：命中的必要节点。
- `unmatched_claim_ids`：没能匹配到现有节点的 claim。
- `claim_matches`：每条 claim 匹配到了哪个节点以及分数。
- `node_hit_rate_total`：总节点命中率。
- `node_hit_rate_required`：必要节点命中率。
- `topology_consistency_score`：主路径顺序是否一致。
- `evidence_grounding_score`：命中的节点是否有足够证据。
- `novelty_candidate`：是否达到新解候选触发条件。
- `pred_claims`：把预测 CoT 拆出来的 claim。
- `answer_judgment`：答案判等详情。
- `verify_result`：CoT 验证详情。

#### [`detect_novelty()`](benchmarkallinone/pipeline2/agents.py)
##### 输出字段解释
- `novelty_label`：分类结果。可能是：
  - `old_family_rephrase`
  - `old_family_branch_extension`
  - `new_solution_family`
  - `uncertain_manual_queue`
- `reason`：判定原因。
- `new_required_claim_ids`：如果有新方法，哪些 claim 被认为是新的必要步骤。
- `new_signature`：候选新方法的主干签名。

#### [`build_patch()`](benchmarkallinone/pipeline2/agents.py)
##### 输出字段解释
- `problem_id`：该 patch 属于哪道题。
- `patch_applied`：这次是否真的生成 patch。
- `novelty_label`：为什么生成 patch。
- `reason`：补丁生成原因。
- `trace_record`：原始评测轨迹。
- `mapping_report`：命中率映射报告。
- `new_r_nodes`：新增节点。
- `new_solution`：新增解法族对象。
- `new_solution_memberships`：新增 membership 记录。
- `new_evidence_bindings`：新增证据绑定记录。

---

## 11. 主流程编排模块

## 11.1 [`benchmarkallinone/pipeline2/pipeline.py`](benchmarkallinone/pipeline2/pipeline.py)

这是整个系统的调度中心。

### 11.1.1 RuntimeContext

[`RuntimeContext`](benchmarkallinone/pipeline2/pipeline.py:40) 保存本次运行的全部上下文。

字段解释：
- `project_root`：项目根目录。
- `config`：当前加载的配置对象。
- `router`：主备模型路由器。
- `ready_root`：ready 样本目录。
- `output_root`：全部输出的根目录。
- `checkpoint_db_path`：checkpoint 路径。
- `runtime_dir`：运行态目录。
- `runtime_state_path`：题目级运行态总表路径。
- `method_runs_dir`：单方法运行快照目录。
- `problem_bundles_dir`：题目 bundle 输出目录。
- `problem_records_dir`：题目主记录输出目录。
- `p_facts_dir` / `t_facts_dir` / `k_atoms_dir`：PTK 输出目录。
- `r_nodes_dir`：节点目录。
- `solution_library_dir`：解法族目录。
- `solution_memberships_dir`：解法成员关系目录。
- `evidence_bindings_dir`：证据绑定目录。
- `coverage_state_dir`：覆盖状态目录。
- `trace_mapping_index_dir`：trace mapping 索引目录。
- `cot_variants_dir`：方法 CoT 变体目录。
- `trace_eval_dir`：评测目录。
- `incoming_traces_dir`：原始评测轨迹目录。
- `mapping_reports_dir`：映射报告目录。
- `novelty_candidates_dir`：新解候选目录。
- `patches_dir`：patch 总目录。
- `dataset_patches_dir`：最终 patch 输出目录。

### 11.1.2 Checkpointer 与 LangGraph 兼容性

你特别提到要尽可能融合 [`benchmarkallinone/pipeline_problem_2_CoT-main/src/pipeline_langgraph.py`](benchmarkallinone/pipeline_problem_2_CoT-main/src/pipeline_langgraph.py:1) 的实现。当前 [`benchmarkallinone/pipeline2/pipeline.py`](benchmarkallinone/pipeline2/pipeline.py:1) 已保留了它的核心思路：

- batch / problem / method 三层 graph
- checkpoint 恢复
- thread_id 分层

但为了兼容当前机器上的 langgraph 版本，做了两点适配：

1. 优先尝试 `SqliteSaver`，如果当前安装的 langgraph 没有 `langgraph.checkpoint.sqlite`，则自动退化到 `InMemorySaver`。
2. 当前版本的 `graph.invoke()` 不接受 `durability="sync"`，因此去掉了该参数，改为直接调用 `graph.invoke(initial_state, config)`。

### 11.1.3 method graph

[`build_method_graph()`](benchmarkallinone/pipeline2/pipeline.py:290) 负责单方法闭环。

执行顺序是：
- `generate_cot`
- `answer_check`
- `verify_round_0`
- `polish_round_1`
- `verify_round_1`
- `polish_round_2`
- `verify_round_2`
- `polish_round_3`
- `verify_round_3`
- `finalize_method`

它保留了 [`benchmarkallinone/pipeline_problem_2_CoT-main/src/pipeline_langgraph.py`](benchmarkallinone/pipeline_problem_2_CoT-main/src/pipeline_langgraph.py:457) 里最核心的 method 流程思想，只是把里面的 stub 函数替换成了 [`benchmarkallinone/pipeline2/agents.py`](benchmarkallinone/pipeline2/agents.py) 的完整实现。

### 11.1.4 problem graph

[`build_problem_graph()`](benchmarkallinone/pipeline2/pipeline.py:425) 负责单题闭环。

执行顺序是：
- `prepare_methods`
- `build_ptk`
- `run_methods`
- `extract_claims`
- `induce_nodes`
- `group_solutions`
- `bind_evidence`
- `finalize_problem_bundle`

### 11.1.5 batch graph

[`build_batch_graph()`](benchmarkallinone/pipeline2/pipeline.py:537) 负责题目级并发。

### 11.1.6 注释式说明关键节点函数

#### [`_prepare_methods_node()`](benchmarkallinone/pipeline2/pipeline.py:328)
作用：
- 根据题目的 `initial_multi_solution_score` 决定方法数；
- 调用 `plan_methods()`；
- 把方法草稿写进运行态 problem。

#### [`_run_methods_node()`](benchmarkallinone/pipeline2/pipeline.py:363)
作用：
- 对每个方法独立跑 method graph；
- 将运行结果写回 `problem["method"]`；
- 同时保存 method 级快照。

#### [`_extract_claims_node()`](benchmarkallinone/pipeline2/pipeline.py:380)
作用：
- 只挑 `is_answer_match=true` 且 `is_final_CoT_qualified=true` 的方法；
- 为这些方法生成 `claim_sequences`；
- 同时汇总 `cot_variants`。

#### [`_induce_nodes_node()`](benchmarkallinone/pipeline2/pipeline.py:415)
作用：
- 把所有合格方法的 claim 汇总；
- 统一归纳成节点。

#### [`_group_solutions_node()`](benchmarkallinone/pipeline2/pipeline.py:438)
作用：
- 基于合格方法和节点，抽解法族。

#### [`_bind_evidence_node()`](benchmarkallinone/pipeline2/pipeline.py:460)
作用：
- 为节点绑定证据；
- 构建题目 bundle；
- 生成 trace mapping index。

#### [`_finalize_problem_bundle_node()`](benchmarkallinone/pipeline2/pipeline.py:491)
作用：
- 把题目级所有产物分别写入不同目录。

### 11.1.7 顶层 API

#### [`run_annotation_pipeline()`](benchmarkallinone/pipeline2/pipeline.py:566)
从 ready 样本启动第二步标注。

#### [`resume_annotation_pipeline()`](benchmarkallinone/pipeline2/pipeline.py:590)
恢复既有 batch。

#### [`evaluate_traces()`](benchmarkallinone/pipeline2/pipeline.py:625)
对外部评测轨迹做命中率计算与新解判定。

#### [`parse_args()`](benchmarkallinone/pipeline2/pipeline.py:853)
当前支持两个子命令：
- `annotate`
- `evaluate-traces`

---

## 12. 配置文件说明

## 12.1 [`benchmarkallinone/pipeline2/configs/default_pipeline2.yaml`](benchmarkallinone/pipeline2/configs/default_pipeline2.yaml)

这是正常运行的默认配置。

### 结构
- `paths`
- `runtime`
- `thresholds`
- `models`

### `models.primary` 和 `models.fallback`
当前实现没有把真实 API key 写入仓库，而是使用环境变量：
- `PIPELINE2_API_KEY_PRIMARY`
- `PIPELINE2_API_KEY_FALLBACK`

这样既能支持你给的主备接口，也不会把敏感信息硬编码在文件里。

## 12.2 [`benchmarkallinone/pipeline2/configs/smoke_pipeline2.yaml`](benchmarkallinone/pipeline2/configs/smoke_pipeline2.yaml)

这是最小运行验证配置。

特点：
- `max_problems: 1`
- `max_problem_workers: 1`
- 输出目录单独落到 `outputs_smoke`

用途：
- 快速检查 pipeline 是否能从 ready 装载、跑通 method graph、构造 bundle、做 trace evaluate。

---

## 13. 示例输入

## 13.1 [`benchmarkallinone/pipeline2/examples/smoke_trace.json`](benchmarkallinone/pipeline2/examples/smoke_trace.json)

这是一个最小评测轨迹例子。

### 字段解释
- `problem_id`：评测对应哪道题。
- `pred_answer`：模型预测答案。
- `pred_cot`：模型输出的推理文本。
- `model_name`：模型名。
- `run_id`：这条轨迹的唯一运行标识。
- `method_hint`：如果外部轨迹本身有方法提示，可以放这里；没有也不影响。
- `created_at`：时间戳。

---

## 14. 输出目录说明

你最新要求是：**每道题最终只保留一个主 JSON 文件**，避免多文件依赖复杂不可控。

因此当前实现的推荐输出口径是：

### `annotate` 主输出
- `pipeline2/outputs_smoke/problems/<problem_id>.json`

这个文件就是该题的**唯一主文件**，内部已经完整包含：
- `problem_record`
- `p_facts`
- `t_facts`
- `k_atoms`
- `claim_sequences`
- `claim_mappings`
- `r_nodes`
- `solution_library`
- `solution_memberships`
- `evidence_bindings`
- `cot_variants`
- `coverage_state`
- `trace_mapping_index`
- `runtime_problem`

### 辅助运行态输出
如果配置 `save_runtime_snapshots=true`，还会额外写：
- `pipeline2/outputs_smoke/annotation_runtime/problems.json`
- `pipeline2/outputs_smoke/annotation_runtime/method_runs/...`

这些仅用于调试和中途恢复，不再是正式依赖文件。

### `evaluate-traces` 输出
评测阶段仍会写 trace 级结果：
- `pipeline2/outputs_smoke/trace_eval/mapping_reports.jsonl`
- `pipeline2/outputs_smoke/trace_eval/novelty_candidates.jsonl`
- `pipeline2/outputs_smoke/trace_eval/dataset_patches.jsonl`
- `pipeline2/outputs_smoke/trace_eval/mapping_reports/*.json`
- `pipeline2/outputs_smoke/trace_eval/novelty_candidates/*.json`
- `pipeline2/outputs_smoke/patches/dataset_patches/*.json`（若真的生成 patch）

但这些都是评测与补丁记录，不是题目 GT 的主存储结构。

---

## 15. 当前验证状态

已经完成的最小验证包括：

1. [`benchmarkallinone/pipeline2`](benchmarkallinone/pipeline2) 下所有 `.py` 文件通过 `py_compile`。
2. 运行：
   - [`python3 benchmarkallinone/run_pipeline2.py annotate --config benchmarkallinone/pipeline2/configs/smoke_pipeline2.yaml`](benchmarkallinone/run_pipeline2.py)
   成功产出题目 bundle。
3. 运行：
   - [`python3 benchmarkallinone/run_pipeline2.py evaluate-traces --config benchmarkallinone/pipeline2/configs/smoke_pipeline2.yaml --trace-file benchmarkallinone/pipeline2/examples/smoke_trace.json`](benchmarkallinone/run_pipeline2.py)
   成功产出 mapping / novelty / patch 三类结果文件。
4. 已修复两个关键兼容性问题：
   - 当前 langgraph 环境缺少 `langgraph.checkpoint.sqlite` 时，自动回退 `InMemorySaver`；
   - 当前 langgraph 版本的 `invoke()` 不接受 `durability="sync"`，已适配。
5. 已修复 ready 图像路径解析问题，当前可以正确解析出诸如 [`benchmarkallinone/ready/agent_multidataset_validation_100/run_f7e4c82684a6f704/datasets/geometry3k/artifacts/images/prob_016bc73dfd9342abef609367_primary.png`](benchmarkallinone/ready/agent_multidataset_validation_100/run_f7e4c82684a6f704/datasets/geometry3k/artifacts/images/prob_016bc73dfd9342abef609367_primary.png) 这样的真实图像文件。

---

## 16. 当前实现边界与严格模式说明

这部分必须讲清楚：当前 [`benchmarkallinone/pipeline2`](benchmarkallinone/pipeline2) 已经切换到**严格无内容 fallback 模式**。

### 已经做到的
- 能从 ready 自动装载题目；
- 能走完整 method graph；
- 能沉淀 `problem_record / p_facts / t_facts / k_atoms / r_nodes / solution_library / evidence_bindings / coverage_state / trace_mapping_index`；
- 能对外部 trace 做映射、命中率计算、novelty 分类与 patch 生成；
- 有主备模型路由；
- 有 LangGraph 分层与恢复机制；
- 题目正式 GT 以“每题一个主 JSON”方式保存；
- 当任何关键 agent 输出缺失、字段为空或格式不符时，会直接抛出契约错误并停止该题流程。

### 当前唯一保留的 fallback
当前只保留一种 fallback：
- **模型端点级主备切换**。也就是 `primary` 失败时，允许尝试 `fallback` 端点。
- 如果 `primary` 和 `fallback` 实际上指向同一个 `base_url + api_key + api_mode` 资源池，router 会自动禁用这个重复 fallback，避免在同一路限流池上重复放大 429。

这不属于内容 fallback，而属于基础设施层的高可用策略。

### 已移除的内容级 fallback
下面这些内容级 fallback 已经移除：
- 方法规划失败时用模板方法代替；
- 求解失败时用标准答案伪造 CoT；
- PTK 抽取失败时从 ready 结构直接拼启发式 PTK；
- claim 提取失败时按句子切分兜底；
- node 归纳失败时按 claim 文本直接生成节点；
- solution family 聚类失败时用节点列表直接拼签名；
- evidence binding 失败时按词面重叠启发式绑定；
- trace mapping 失败时用 lexical 匹配代替；
- novelty detection 失败时用阈值规则强行分类。

### 这意味着什么
这套实现现在的语义是：

- **没有合法 JSON，就失败**；
- **没有必要字段，就失败**；
- **没有关键结构输出，就失败**；
- **没有题目主 JSON，就不允许做 trace evaluate**。

这正符合你“去掉所有 fallback，给出完整实现”的要求。

### 当前仍然存在的现实问题
虽然内容级 fallback 已移除，但实际运行结果仍然受外部模型端点约束：
- 主端点可能返回 Cloudflare 403；
- 主端点或备端点可能返回 429，此时客户端会按端点配置做指数退避，并在有 `Retry-After` 时优先遵守服务端节流提示；
- 备端点可能返回 `choices[0].message.role` 但没有 `content`；
- 某些 agent 虽然得到 JSON，但字段可能为空，例如 `p_facts=[]`；

在严格模式下，这些都会被视为**真正错误**，而不会被系统悄悄修补。

---

## 17. 推荐的实际使用方式

### 17.1 设置环境变量
建议不要把真实 key 写进 YAML，而是设置：

```bash
export PIPELINE2_API_KEY_PRIMARY="你的主 API Key"
export PIPELINE2_API_KEY_FALLBACK="你的备 API Key"
```

### 17.2 跑 smoke

```bash
python3 benchmarkallinone/run_pipeline2.py annotate --config benchmarkallinone/pipeline2/configs/smoke_pipeline2.yaml
python3 benchmarkallinone/run_pipeline2.py evaluate-traces --config benchmarkallinone/pipeline2/configs/smoke_pipeline2.yaml --trace-file benchmarkallinone/pipeline2/examples/smoke_trace.json
```

### 17.3 跑全量或半全量
把 [`benchmarkallinone/pipeline2/configs/default_pipeline2.yaml`](benchmarkallinone/pipeline2/configs/default_pipeline2.yaml) 里的：
- `max_problems`
- `max_problem_workers`
- `include_manual_review`
- 阈值
- 主备模型参数

调到合适值，再运行 `annotate` 即可。

---

## 18. 一句话总结

[`benchmarkallinone/pipeline2`](benchmarkallinone/pipeline2) 当前已经实现了一个完整的第二步标注系统框架：

- 它能从 ready 数据开始；
- 能沿着 `problem -> method -> verified CoT -> claims -> nodes -> solution families -> evidence bindings -> trace mapping -> novelty patch` 这条链闭环运行；
- 并且已经验证了 annotate 和 evaluate-traces 两个主命令都能在 smoke 配置下成功运行。

因此，它现在可以被视为：

> **融合了 [`benchmarkallinone/pipeline_problem_2_CoT-main`](benchmarkallinone/pipeline_problem_2_CoT-main) LangGraph 思路、并对齐 [`benchmarkallinone/next_step_docs/第二步标注Pipeline详细设计.md`](benchmarkallinone/next_step_docs/第二步标注Pipeline详细设计.md) 的第二步标注完整实现原型。**
