# benchmark/src Python 模块与函数说明

本文面向当前采集/清洗流水线的代码结构，按模块说明其职责、主要函数/类、以及每个步骤属于：

- **纯脚本**：规则、启发式、IO、聚合，不依赖 LLM。
- **可选 LLM/Agent**：默认可走模型，但关闭后不会承担主流程必经逻辑。
- **混合 fallback**：优先尝试 LLM/Agent，但内置脚本回退；或由脚本主控、LLM 仅作可选覆写。

---

## 总览：模块与阶段映射

| 模块 | 主要阶段 | 角色 | 自动化类型 |
| --- | --- | --- | --- |
| `pipeline_setup.py` | Stage 0 Setup | 参数解析、配置覆盖、run 目录初始化 | 纯脚本 |
| `pipeline_collection.py` | Stage 1 Collection | 样本接入、预处理、初步评分、结构提取编排 | 纯脚本 |
| `cleaning_semantics.py` | Stage 1/2 支撑 | 文本结构解析、视觉结构解析、对齐、可解性判断 | 纯脚本 |
| `pipeline_cleaning.py` | Stage 2 Cleaning | 改写产物构建、质量 gate、清洗记录落盘对象生成 | 混合 fallback |
| `pipeline_reporting.py` | Stage 3 Report | records 聚合、dataset/run summary 写出 | 纯脚本 |
| `multidataset_cleaning_pipeline.py` | Orchestrator / Shared runtime | 公共 dataclass、连接器、可选 agent、主流程编排 | 混合 fallback |

---

## 阶段关系图：Setup → Collection → Cleaning → Report

```text
run_pipeline.py
    │
    ▼
multidataset_cleaning_pipeline.py
    │
    ├── Stage 0: Setup
    │       └── pipeline_setup.py
    │           - parse_args()
    │           - merge_cli_overrides()
    │           - build_setup_context()
    │           => 输出 SetupContext、run_dir、dataset_root、pipeline_run_id
    │
    ├── Stage 1: Collection
    │       ├── pipeline_collection.py
    │       │   - connector_for() / ingest_dataset_samples()
    │       │   - preprocess_sample()
    │       │   - run_initial_collection_scoring()
    │       │   - extract_sample_structure()
    │       │   => 输出 candidate / normalized / initial scoring / alignment / solvability 等中间结果
    │       │
    │       └── cleaning_semantics.py
    │           - TextContextParser
    │           - VisualParser
    │           - AlignmentEngine
    │           - SolvabilityChecker
    │           => 为 Collection 提供文本/视觉/对齐/可解性解析能力
    │
    ├── Stage 2: Cleaning
    │       └── pipeline_cleaning.py
    │           - rewrite_sample()
    │           - clean_gate()
    │           - finalize_cleaning_sample()
    │           => 输出 problem_main_record / cleaning_record / reject_record / asset_records 等
    │
    └── Stage 3: Report
            └── pipeline_reporting.py
                - append_sample_result()
                - finalize_dataset_report()
                - write_run_summary()
                => 输出 records/*.jsonl、datasets/<dataset>/summary.json、run_dir/summary.json
```

### 阶段间数据流说明

1. **Setup** 先产出运行上下文
   - 由 `pipeline_setup.py` 生成 `SetupContext`
   - 提供后续阶段共用的 `pipeline_run_id`、输出目录、聚合 summary 容器

2. **Collection** 把原始样本转成结构化中间结果
   - `pipeline_collection.py` 负责接入、预处理、提取编排
   - Collection 末尾还有一小段显式的 **initial collection scoring**，先产出 `initial_scores`，再生成 `priority_score / priority_tier`
   - `cleaning_semantics.py` 提供文本结构解析、视觉结构解析、对齐和可解性判断
   - 这一步的结果主要还是“清洗前中间态”，还没有最终 `pass/review/reject`

3. **Cleaning** 把中间结果转成最终清洗判定与记录
   - `pipeline_cleaning.py` 负责 rewrite、quality gate、记录构建
   - **`pass / review / reject` 在这里决定**，核心位置是 `clean_gate()`

4. **Report** 只负责汇总与写出
   - `pipeline_reporting.py` 不重新做判定
   - 它消费 Cleaning 已经产出的结果，统一写出 dataset/run 级 summary 与 records

### 自动化类型在阶段图里的对应关系

- **Setup**：纯脚本
- **Collection**：主流程纯脚本；依赖的解析组件也都是纯脚本
- **Cleaning**：混合 fallback
  - rewrite 可能走 LLM/Agent
  - gate 主体是脚本
  - review 边界可选走 agent override
- **Report**：纯脚本

### `multidataset_cleaning_pipeline.py` 在图里的位置

它本身不是单独一个业务阶段，而是：

- 顶层 orchestrator
- 共享 runtime / helper 容器
- connector / normalizer / analyzer / agent 的装配点

也就是说，它负责把：

- `pipeline_setup.py`
- `pipeline_collection.py`
- `cleaning_semantics.py`
- `pipeline_cleaning.py`
- `pipeline_reporting.py`

串成一条完整流水线。

---

## 1. `pipeline_setup.py`

**模块职责**

负责显式的 Setup 阶段：读取 CLI 参数、把 CLI 覆盖合并进配置、初始化本次 run 的目录与上下文。

**自动化类型**：纯脚本

### 主要数据结构

- `SetupContext`
  - 保存本次运行的上下文：`config`、`pipeline_run_id`、`ingest_batch_id`、`run_dir`、`records_dir`、`dataset_root`、`aggregate_summary`。

### 函数

- `parse_args()`
  - 作用：定义并解析 CLI 参数。
  - 典型参数：`--config`、`--output-dir`、`--sample-per-dataset`、`--disable-llm`、`--model`。
  - 类型：纯脚本

- `merge_cli_overrides(config, args)`
  - 作用：把 CLI 参数覆盖到配置对象上。
  - 重点：`--disable-llm` 会直接把 `config.model.enabled` 设为 `False`。
  - 类型：纯脚本

- `build_setup_context(config, ensure_dir, stable_digest, utc_now)`
  - 作用：生成 `pipeline_run_id`、`ingest_batch_id`，创建 run 目录并返回 `SetupContext`。
  - 类型：纯脚本

---

## 2. `pipeline_reporting.py`

**模块职责**

负责显式的 Report 阶段：把前面阶段产出的结果 bundle 聚合为 records 文件、dataset summary、run summary。

**关键边界**

- **不负责决定** `pass / review / reject`
- 只负责**汇总并写出**已经决定好的结果

**自动化类型**：纯脚本

### 常量

- `RESULT_MAPPING`
  - 作用：定义单样本结果字段到 dataset bundle 键名的映射，例如 `problem_main_record -> problem_main_records`。

### 函数

- `init_dataset_bundle()`
  - 作用：初始化 dataset 级别的空 bundle 容器。
  - 类型：纯脚本

- `append_sample_result(bundle, result)`
  - 作用：把单样本结果并入 dataset bundle。
  - 类型：纯脚本

- `write_sample_bundle_if_needed(config, sample_dir, result, write_json)`
  - 作用：在开启 `save_sample_bundle` 时，把单样本完整结果另存为 `samples/*.json`。
  - 类型：纯脚本

- `build_source_unavailable_summary(spec, config, detail)`
  - 作用：为无法采集的数据集生成 `source_unavailable` summary。
  - 类型：纯脚本

- `finalize_dataset_report(...)`
  - 作用：写出 `records/*.jsonl`，统计 `decision_counts` 和 `rewrite_strategy_counts`，生成 `datasets/<dataset>/summary.json`。
  - 类型：纯脚本

- `write_run_summary(run_dir, aggregate_summary, write_json)`
  - 作用：写出 run 级别的 `summary.json`。
  - 类型：纯脚本

---

## 3. `pipeline_collection.py`

**模块职责**

负责显式的 Collection 阶段编排，把原始样本变成清洗前的结构化中间结果。

可拆成四段理解：

1. **Ingestion**：选择 connector 并取样
2. **Preprocess**：标准化文本、落图片、准备候选输入
3. **Initial Collection Scoring**：计算 `initial_scores`、`priority_score`、`priority_tier`
4. **Extract**：抽取文本结构、视觉结构、对齐、可解性

**自动化类型**：纯脚本

> 这里虽然会调用 orchestrator 中的某些 agent/组件实例，但本模块本身的控制流和主判定逻辑都是脚本式编排。

### 函数

#### Ingestion

- `default_image_quality()`
  - 作用：返回默认空图像质量结构，供缺省场景兜底。
  - 类型：纯脚本

- `connector_for(pipeline, spec)`
  - 作用：根据 `spec.source_kind` 选择 `local_file / huggingface / github / source_unavailable` connector。
  - 类型：纯脚本

- `ingest_dataset_samples(pipeline, spec)`
  - 作用：执行 connector 的 `sample()`，得到 `source_status / samples / detail`。
  - 类型：纯脚本

#### Preprocess / Initial Collection Scoring

- `compute_collection_priority(pipeline, initial_scores)`
  - 作用：根据 `initial_scores` 汇总 `priority_score` 与 `priority_tier`。
  - 类型：纯脚本

- `run_initial_collection_scoring(...)`
  - 作用：把 Collection 结尾那一小段初步评分显式收拢起来。
  - 做的事情包括：
    - 生成 `multi_solution_policy`
    - 计算 `initial_image_dependency_score`
    - 计算 `initial_multi_solution_score`
    - 计算 `initial_verifiability_score`
    - 汇总 `priority_score` / `priority_tier`
  - 类型：纯脚本

- `build_candidate_problem_record(...)`
  - 作用：生成候选题目的基础记录，保存原始题目信息和初始评分。
  - 类型：纯脚本

- `build_raw_asset_bundle(...)`
  - 作用：生成原始资产包，记录 question/answer/image 是否存在及其基本属性。
  - 类型：纯脚本

- `build_candidate_pool_entry(...)`
  - 作用：生成候选池条目，写入已经整理好的 `priority_score` / `priority_tier`，并标记推荐清洗路径。
  - 类型：纯脚本

- `build_normalized_assets(...)`
  - 作用：生成标准化后的文本/图像区域描述，作为后续清洗输入。
  - 类型：纯脚本

- `preprocess_sample(pipeline, spec, sample, image_dir)`
  - 作用：Collection 的核心预处理函数。
  - 做的事情包括：
    - 清洗原始 question/answer 文本
    - 结构化归一化文本
    - 语言识别、answer type 推断
    - choice 提取
    - 生成 `candidate_id` / `problem_id`
    - 持久化图片并计算质量分
    - 推断 `requires_image` / `text_dominant` / `cleaning_path`
    - 计算 `text_completeness`
    - 调用 `run_initial_collection_scoring(...)`
    - 产出候选记录、原始资产、候选池、标准化资产
  - 类型：纯脚本

#### Extract

- `build_alignment_record(...)`
  - 作用：调用 `alignment_engine.align()` 生成对齐记录，并补齐稳定的 `alignment_id`。
  - 类型：纯脚本

- `build_quality_flags(...)`
  - 作用：基于文本缺失、图像质量、对比度、裁切、multi-image variance 等规则打质量 flag。
  - 类型：纯脚本

- `build_text_structure_record(...)`
  - 作用：把文本解析结果整理成 records 可落盘的结构。
  - 类型：纯脚本

- `extract_sample_structure(pipeline, sample, preprocessed, open_variants)`
  - 作用：Collection 的核心结构提取函数。
  - 做的事情包括：
    - 解析 `text_structure`
    - 解析 `visual_structures`
    - 计算 `alignment_record`
    - 生成 `quality_flags`
    - 生成 `solvability_report`
    - 输出 `text_structure_records`
  - 类型：纯脚本

---

## 4. `cleaning_semantics.py`

**模块职责**

提供 Collection / Cleaning 共用的语义解析组件。这里是流水线里最核心的**非 Agent 规则层**之一。

**自动化类型**：纯脚本

### 基础函数

- `utc_now()`
  - 作用：生成 UTC 时间戳。
  - 类型：纯脚本

- `clamp(value, low=0.0, high=1.0)`
  - 作用：分数截断到区间内。
  - 类型：纯脚本

- `normalize_whitespace(text)`
  - 作用：统一空白字符与换行。
  - 类型：纯脚本

- `split_sentences(text)`
  - 作用：按中英文标点和换行切分句段。
  - 类型：纯脚本

- `normalize_units(text)`
  - 作用：把题干/答案里的常见单位归一为统一写法，并记录归一操作。
  - 类型：纯脚本

- `extract_variable_aliases(text)`
  - 作用：从文本中抽取变量符号/标签别名。
  - 类型：纯脚本

- `extract_unit_mentions(text)`
  - 作用：提取文本出现过的单位种类。
  - 类型：纯脚本

- `normalize_structured_text(text)`
  - 作用：综合执行单位归一、变量抽取、句段切分，返回结构化规范文本。
  - 类型：纯脚本

### 类

- `TextContextParser`
  - 作用：把题干解析为：
    - `conditions`
    - `targets`
    - `answer_slots`
    - `entity_mentions`
    - `question_type`
  - 关键意义：决定文本结构是否完整，以及题目需要哪些回答槽位。
  - 类型：纯脚本

- `VisualParser`
  - 作用：对图像做轻量结构化解析，不依赖 OCR。
  - 会生成：
    - `visual_kind`
    - `visual_entities`
    - `visual_relations`
    - `parser_confidence`
  - 类型：纯脚本

- `AlignmentEngine`
  - 作用：把文本中的视觉锚点和视觉结构做对齐，计算：
    - `alignment_pairs`
    - `conflict_pairs`
    - `coverage_score`
    - `consistency_score`
    - `alignment_status`
  - 关键意义：`good / risky / bad` 直接影响后续 Cleaning gate。
  - 类型：纯脚本

- `SolvabilityChecker`
  - 作用：判断题目是否具备最基本的可解性。
  - 核心维度：
    - `answer_verifiable`
    - `target_clear`
    - `rewrite_complete`
    - `text_sufficient`
    - `visual_grounding_available`
  - 输出：`solvability_score` 与 `decision_hint`。
  - 类型：纯脚本

---

## 5. `pipeline_cleaning.py`

**模块职责**

负责显式的 Cleaning 阶段：把 Collection 的中间结果进一步变成清洗后的 records、gate 决策、问题主记录等。

**关键边界**

- `pass / review / reject` 的最终脚本决策发生在这里
- Stage 3 Report 只消费这里的结果，不重新裁决

**自动化类型**：混合 fallback

- 改写部分会调用 `RewriteAgent`
- 决策主体 `clean_gate()` 是规则脚本
- 规则判成 `review` 后，还允许 `DecisionAgent.review_override()` 做可选覆写

### 函数

#### Rewrite / transform

- `build_open_variants(pipeline, problem_id, rewrite_report)`
  - 作用：把 rewrite 结果整理成开放题变体列表。
  - 类型：混合 fallback（输入依赖 rewrite agent，整理动作本身是脚本）

- `build_rewrite_record(...)`
  - 作用：生成 rewrite 记录，写明策略、理由、变体数量。
  - 类型：混合 fallback

- `rewrite_sample(pipeline, spec, sample, preprocessed)`
  - 作用：调用 `pipeline.rewrite_agent.rewrite(...)`，并生成 `open_variants` 和 `rewrite_record`。
  - 类型：混合 fallback

#### Record building

- `build_clean_problem_record(...)`
  - 作用：生成 clean problem 级记录，汇总清洗后的关键状态。
  - 类型：纯脚本

- `create_roi_assets(...)`
  - 作用：根据 `roi_bbox` 从原图裁出 ROI 图片并生成 crop 资产。
  - 类型：纯脚本

- `build_asset_records(...)`
  - 作用：构造 question/answer/image/open-variant 等资产记录。
  - 类型：纯脚本

- `build_node_records(...)`
  - 作用：把条件、目标槽位、答案、视觉实体、质量信号等转成 node records。
  - 类型：纯脚本

- `build_cleaning_record(...)`
  - 作用：生成 cleaning record，总结 normalization、质量检查、alignment、text structure、solvability、rewrite 和最终决策。
  - 类型：混合 fallback

- `build_reject_record(...)`
  - 作用：在 `decision == reject` 时生成 reject record。
  - 类型：纯脚本

- `build_problem_main_record(...)`
  - 作用：生成最核心的 problem 主记录，供 report 统计与下游消费。
  - 类型：纯脚本

- `build_field_audit_records(...)`
  - 作用：记录 question/answer 归一化、rewrite 策略、gate decision 等字段变更审计信息。
  - 类型：混合 fallback

#### Gate / finalization

- `clean_gate(...)`
  - 作用：Cleaning 阶段的核心裁决函数。
  - 主要输入：
    - 文本完整度
    - 图像质量
    - alignment 状态
    - potential scores
    - rewrite 结果
    - text structure
    - solvability
  - 主要输出：
    - `decision`: `pass / review / reject`
    - `decision_reason_codes`
    - `clean_score`
  - 说明：这是**决定 pass / review / reject 的主要位置**。
  - 类型：混合 fallback（主体是脚本，末尾允许 `DecisionAgent` 可选覆写）

- `finalize_cleaning_sample(...)`
  - 作用：Cleaning 的总收口函数。
  - 做的事情包括：
    - 计算 potential scores
    - 执行 `clean_gate`
    - 生成 clean problem record
    - 生成 ROI / asset / node / cleaning / reject / problem_main / audit records
    - 打包单样本结果
  - 类型：混合 fallback

---

## 6. `multidataset_cleaning_pipeline.py`

**模块职责**

这是当前总 orchestrator 和共享 runtime 模块：

- 保留公共工具函数
- 定义配置 dataclass
- 定义 sample/connector/client/agent 类
- 初始化 parser / analyzer / agent / connector class
- 串联 Setup → Collection → Cleaning → Report

**自动化类型**：混合 fallback

### 6.1 通用工具函数

- `utc_now()` / `ensure_dir()` / `clamp()`
  - 作用：时间、目录、分数截断工具。
  - 类型：纯脚本

- `json_default()` / `write_json()` / `write_jsonl()`
  - 作用：JSON/JSONL 序列化与落盘。
  - 类型：纯脚本

- `sha256_bytes()` / `stable_digest()`
  - 作用：稳定 ID 与内容 hash 生成。
  - 类型：纯脚本

- `to_plain_text()` / `normalize_whitespace()`
  - 作用：松散输入统一转文本，并归一空白。
  - 类型：纯脚本

- `is_null_like_text()` / `is_missing_value()`
  - 作用：识别空值、伪空值。
  - 类型：纯脚本

- `parse_choice_map()`
  - 作用：把 dict/list/text 等形式的选项统一转成 `A -> 文本` 映射。
  - 类型：纯脚本

- `extract_json_object()`
  - 作用：从模型输出或自由文本里尽量提取 JSON 对象。
  - 类型：纯脚本

### 6.2 配置与数据对象

- `ModelConfig`
  - 作用：模型配置。
  - 类型：纯脚本数据结构

- `ThresholdConfig`
  - 作用：阈值配置。
  - 类型：纯脚本数据结构

- `DatasetSpec`
  - 作用：数据集规格定义。
  - 类型：纯脚本数据结构

- `PipelineConfig`
  - 作用：总配置对象。
  - 重要类方法：
    - `default_dataset_specs()`：内置默认数据集规格
    - `from_yaml(path)`：从 YAML 加载配置
  - 类型：纯脚本

- `UnifiedSample`
  - 作用：统一样本结构，屏蔽不同数据源格式差异。
  - 类型：纯脚本数据结构

### 6.3 模型客户端与基础处理组件

- `OpenAICompatibleClient`
  - 作用：向 OpenAI 兼容接口发起 JSON chat 请求。
  - 说明：模型关闭或缺少 key 时会直接返回 `None`。
  - 类型：可选 LLM/Agent

- `TextNormalizer`
  - 作用：题干/答案标准化、语言识别、answer type 推断、choice 抽取、图像依赖判断、文本完整度打分。
  - 关键点：虽然类名叫 normalizer，但内部全是规则逻辑，不依赖 LLM。
  - 类型：纯脚本

- `ImageQualityAnalyzer`
  - 作用：计算模糊度、对比度、噪声、ROI、可读性、感知 hash。
  - 类型：纯脚本

### 6.4 连接器与抽取辅助

- `BaseConnector`
  - 作用：connector 基类。
  - 类型：纯脚本

- `SourceUnavailableConnector`
  - 作用：对没有稳定公共数据源的数据集返回 `source_unavailable`。
  - 类型：纯脚本

- `read_prompt(path)`
  - 作用：读取 prompt 文件。
  - 类型：纯脚本

- `normalize_image_path_list(value)`
  - 作用：统一 image path 输入格式。
  - 类型：纯脚本

- `resolve_image_candidate_path(path_str, base_dir)`
  - 作用：在多个候选目录里解析实际图片路径。
  - 类型：纯脚本

- `choose_candidate_field(row, candidates, fallback_regex)`
  - 作用：在记录字段中选择 question/answer/image/choice 对应列。
  - 类型：纯脚本

- `heuristic_extract_record_content(row, spec)`
  - 作用：通过字段名启发式抽取 question / answer / image / choice。
  - 类型：纯脚本

- `prompt_extract_record_content(row, spec, client)`
  - 作用：尝试用 prompt + LLM 抽取结构化内容，失败时回退到 `heuristic_extract_record_content()`。
  - 类型：混合 fallback

- `resolve_multiple_choice_answer_text(answer_text, choice_map)`
  - 作用：把 `A` 这类选项答案映射成对应选项文本。
  - 类型：纯脚本

### 6.5 具体 connector 类

- `LocalFileConnector`
  - 作用：从本地 `json/jsonl/csv/tsv/parquet` 读取记录，转成 `UnifiedSample`。
  - 类型：混合 fallback
  - 原因：主流程是脚本；但单条记录抽取时会走 `prompt_extract_record_content()`，可选调用 LLM。

- `HuggingFaceConnector`
  - 作用：从 Hugging Face dataset 取样并转成 `UnifiedSample`。
  - 类型：混合 fallback
  - 原因同上。

- `GitHubConnector`
  - 作用：clone/open repo、自动发现数据文件、解析记录与图片，并转成 `UnifiedSample`。
  - 类型：混合 fallback
  - 原因同上；仓库发现和解析是脚本，记录字段抽取可走 LLM fallback。

### 6.6 Agent / decision 类

- `RewriteAgent`
  - 作用：把题目改写成开放式或更适合清洗/标注的形式。
  - 行为：
    - 若模型可用，尝试走模型
    - 否则走规则策略（如 `keep_open`、`split_open`、`drop_image_index` 等）
  - 类型：混合 fallback

- `DecisionAgent`
  - 作用：对 `review` 边界样本做可选 override。
  - 说明：不是主决策器；主决策仍是 `clean_gate()`。
  - 类型：可选 LLM/Agent

### 6.7 主编排类

- `MultiDatasetCleaningPipeline`
  - 作用：主 orchestrator。
  - 典型职责：
    - 初始化共享组件：normalizer、image analyzer、text parser、visual parser、alignment engine、solvability checker、rewrite/decision agent
    - 暴露通用 helper 给 stage 模块使用
    - 遍历 datasets
    - 调用 Collection → Cleaning → Report
  - 类型：混合 fallback

- `main()`
  - 作用：整体 CLI 入口，串联 config、setup context、pipeline 实例和 run 执行。
  - 类型：混合 fallback

---

## 7. 按处理步骤看：哪些是纯脚本，哪些依赖 Agent

### 7.1 纯脚本步骤

这些步骤即使 `--disable-llm` 也照常运行：

1. Setup 参数解析与 run 目录初始化
2. 连接器选择
3. 本地/HF/GitHub 数据读取与样本抽样主流程
4. 文本归一化、choice 解析、answer type 推断
5. 图片保存、图像质量分析、ROI 计算
6. 文本结构解析
7. 视觉结构解析
8. text-image alignment
9. solvability 判定
10. `clean_gate()` 主裁决
11. records / summary 聚合与写出

### 7.2 可选 LLM/Agent 步骤

这些步骤是增强项，不是 disable-llm 下的主依赖：

1. `OpenAICompatibleClient.chat_json()`
2. `DecisionAgent.review_override()`

### 7.3 混合 fallback 步骤

这些步骤会优先尝试模型，但脚本能回退：

1. 记录字段抽取：`prompt_extract_record_content()` → fallback 到启发式抽取
2. 题目改写：`RewriteAgent` 模型改写 → fallback 到规则改写
3. review 边界决策：`clean_gate()` 先脚本给结果 → `DecisionAgent` 仅作可选覆写

---

## 8. 当前最重要的架构结论

### `pass / review / reject` 在哪里决定？

在 **Stage 2 Cleaning**，核心函数是：

- `pipeline_cleaning.clean_gate()`
- `pipeline_cleaning.finalize_cleaning_sample()`

Stage 3 `pipeline_reporting.py` 只负责：

- 汇总 `problem_main_record.clean_decision`
- 统计 `decision_counts`
- 写出 summary 和 records

### 这条流水线是不是“全 Agent 化”？

不是。

当前实现是：

- **主干大部分是脚本/启发式**
- **少数点位接入可选 LLM/Agent**
- **关闭 LLM 后仍可完成一条可运行的 deterministic pipeline**

也就是说，这更像是：

- **脚本主导的采集/清洗流水线**
- 外挂了 **可选的 LLM 增强模块**

而不是纯 agent black-box 流水线。
