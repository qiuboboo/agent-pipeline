# Agent 采集与清洗实现说明与 5 数据集验证报告

## 1. 文档目的

本文档记录基于 [`benchmarkall/pipeline初步设计.md`](benchmarkall/pipeline初步设计.md) 落地的“采集 + 清洗”实现，范围严格限定在以下两段：

1. `Collection`：候选样本接入、资产登记、初步价值打分、候选入池。
2. `Cleaning`：规范化、开放化改写、文本/视觉结构解析、可解性检查、最终门控。

实现时参考了 [`PaperBanana-main/README.md`](PaperBanana-main/README.md) 中的多 agent 编排思想，以及 [`PaperBanana-main/utils/paperviz_processor.py:37`](PaperBanana-main/utils/paperviz_processor.py:37) 所体现的“中心处理器 + 专职 agent + 分阶段串行/局部并发”调度方式，但不复用其图像生成任务逻辑，而是把这种组织方式迁移到 benchmark 数据生产流程中。

本文档同时给出：

- 当前代码实现入口与核心模块
- 全部 agent 的职责、输入、输出与回退策略
- 五个指定数据集的 10 条验证结果
- 当前输出目录、结构化产物与审计记录说明

---

## 2. 本次实际交付内容

### 2.1 代码入口

- 运行入口：[`benchmarkallinone/run_pipeline.py`](benchmarkallinone/run_pipeline.py)
- 主流水线：[`benchmarkallinone/src/benchmarkallinone/pipeline.py`](benchmarkallinone/src/benchmarkallinone/pipeline.py)
- 语义清洗组件：[`benchmarkallinone/src/benchmarkallinone/cleaning_semantics.py`](benchmarkallinone/src/benchmarkallinone/cleaning_semantics.py)
- 10 条验证配置：[`benchmarkallinone/configs/agent_multidataset_validation_10.yaml`](benchmarkallinone/configs/agent_multidataset_validation_10.yaml)
- 验证输出根目录：[`benchmarkallinone/outputs/agent_multidataset_validation_10/run_10fb07acd544b44d`](benchmarkallinone/outputs/agent_multidataset_validation_10/run_10fb07acd544b44d)

### 2.2 已覆盖的数据集

按用户要求接入并验证以下五个数据集：

1. `SCEMQA`：Hugging Face
2. `Geometry3K`：GitHub / InterGPS
3. `CMM-Math`：Hugging Face
4. `MathVision`：Hugging Face
5. `PhysReason`：Hugging Face，且保留 raw zip fallback

对应配置写在 [`benchmarkallinone/configs/agent_multidataset_validation_10.yaml`](benchmarkallinone/configs/agent_multidataset_validation_10.yaml) 中。

### 2.3 模型接入方式

当前实现使用 OpenAI 兼容接口，核心配置位于 [`benchmarkallinone/src/benchmarkallinone/pipeline.py:203`](benchmarkallinone/src/benchmarkallinone/pipeline.py:203) 定义的 [`ModelConfig`](benchmarkallinone/src/benchmarkallinone/pipeline.py:203)：

- `base_url = https://synai996.space/v1`
- `model = gpt-5.4`
- `reasoning_effort = high`

HTTP 请求与多模态 JSON 调用由 [`OpenAICompatibleClient`](benchmarkallinone/src/benchmarkallinone/pipeline.py:419) 统一封装，支持：

- 文本 JSON 调用：[`OpenAICompatibleClient.chat_json()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:624)
- 图文 JSON 调用：[`OpenAICompatibleClient.chat_json_with_images()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:627)
- token / 请求耗时 / 重试统计：[`OpenAICompatibleClient._post_json()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:494)

---

## 3. 设计约束：严格以初步设计为准

本次实现遵循 [`benchmarkall/pipeline初步设计.md`](benchmarkall/pipeline初步设计.md) 的三个核心约束：

### 3.1 采集阶段要完成四件事

对应 [`benchmarkall/pipeline初步设计.md:88`](benchmarkall/pipeline初步设计.md:88) 到 [`benchmarkall/pipeline初步设计.md:136`](benchmarkall/pipeline初步设计.md:136) 的要求，代码中落成以下四步：

1. 样本接入
2. 资产登记
3. 初步价值打分
4. 候选入池

### 3.2 清洗阶段要完成规范化与开放化改写

对应 [`benchmarkall/pipeline初步设计.md:195`](benchmarkall/pipeline初步设计.md:195) 到 [`benchmarkall/pipeline初步设计.md:233`](benchmarkall/pipeline初步设计.md:233)，当前实现覆盖：

- 题面与答案规范化
- 文本主导 / 多模态清洗路径分流
- 选择题开放化改写
- 纯图编号选择题剔除
- 图文结构解析
- 可解性检查
- 保留 / review / reject 门控

### 3.3 只实现采集与清洗，不扩展到标注/QA/发布

虽然输出已经为后续标注预留了 `problem_main_record / node_record / alignment_record / solvability_report` 等底座对象，但本次交付范围仍然只覆盖采集与清洗，不实现 [`benchmarkall/pipeline初步设计.md`](benchmarkall/pipeline初步设计.md) 后续的 Annotation、QA 与 Format 主链。

---

## 4. 参考 PaperBanana 的组织方式

### 4.1 参考了什么

参考点主要有两部分：

1. **Agent 分工方式**：见 [`PaperBanana-main/README.md:39`](PaperBanana-main/README.md:39) 到 [`PaperBanana-main/README.md:45`](PaperBanana-main/README.md:45)
2. **中心处理器调度方式**：见 [`PaperBanana-main/utils/paperviz_processor.py:37`](PaperBanana-main/utils/paperviz_processor.py:37) 到 [`PaperBanana-main/utils/paperviz_processor.py:240`](PaperBanana-main/utils/paperviz_processor.py:240)

PaperBanana 的核心思想不是“一个万能 prompt 做完全部事情”，而是：

- 每个 agent 只负责一个窄职责
- 上游 agent 产出的结构化结果作为下游证据
- 用中心 orchestrator 控制调用顺序、迭代和并发

### 4.2 迁移到本项目后的形式

在本项目中，这一组织方式落地为：

- 中心流水线类：[`MultiDatasetCleaningPipeline`](benchmarkallinone/src/benchmarkallinone/pipeline.py:2731)
- 中间调度器：[`AgenticCleaningOrchestrator`](benchmarkallinone/src/benchmarkallinone/pipeline.py:2673)
- 通用 agent 基类：[`BaseStructuredAgent`](benchmarkallinone/src/benchmarkallinone/pipeline.py:1744)

每个 agent 独立拥有：

- 专属 prompt 文件
- 专属输入 payload
- JSON 结构化输出
- fallback 规则回退逻辑

这和 PaperBanana 中“Retriever / Planner / Stylist / Visualizer / Critic”按工种拆分的思想是一致的，只是本项目的 agent 工种替换成了数据生产链路。

---

## 5. 当前流水线总览

### 5.1 总体执行顺序

单样本实际执行顺序见 [`MultiDatasetCleaningPipeline.process_sample()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:3982)：

1. `Source Intake`
2. `Asset Registry`
3. `Potential Scorer`
4. `Candidate Registrar`
5. `Normalization`
6. `Rewrite`
7. `TextContextParser`
8. `VisualParser`
9. `AlignmentEngine`
10. `Sample Understanding`
11. `SolvabilityChecker`
12. `Decision Agent`
13. 结构化结果落盘

### 5.2 多数据集调度

多数据集执行入口是 [`MultiDatasetCleaningPipeline.run()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:2782)，其行为是：

- 遍历配置中的数据集列表
- 为每个数据集选择 connector
- 执行数据抽样与单样本清洗
- 在每个数据集目录写出独立 `summary.json`
- 最终在 run 根目录聚合总 `summary.json`

### 5.3 样本并发

单数据集内部支持样本级并发，逻辑位于 [`MultiDatasetCleaningPipeline.run_single_dataset()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:2797)。

本次验证配置 [`benchmarkallinone/configs/agent_multidataset_validation_10.yaml`](benchmarkallinone/configs/agent_multidataset_validation_10.yaml) 使用：

- `sample_per_dataset: 10`
- `sample_concurrency: 2`

这与 PaperBanana 的“批量处理 + 可控并发”思路一致，但这里的并发对象是样本而不是候选图像生成任务。

---

## 6. 数据源接入层设计

### 6.1 Connector 抽象

统一抽象基类是 [`BaseConnector`](benchmarkallinone/src/benchmarkallinone/pipeline.py:849)。

已实现四类 connector：

- [`SourceUnavailableConnector`](benchmarkallinone/src/benchmarkallinone/pipeline.py:865)
- [`LocalFileConnector`](benchmarkallinone/src/benchmarkallinone/pipeline.py:1027)
- [`HuggingFaceConnector`](benchmarkallinone/src/benchmarkallinone/pipeline.py:1193)
- [`GitHubConnector`](benchmarkallinone/src/benchmarkallinone/pipeline.py:1495)

### 6.2 Hugging Face 数据集

五个目标数据集中，`SCEMQA / CMM-Math / MathVision / PhysReason` 都支持 HF 接入：

- split 自动探测：[`HuggingFaceConnector.load_dataset_any()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:1198)
- 图片解析：[`HuggingFaceConnector.load_images()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:1220)

### 6.3 PhysReason raw zip fallback

按用户要求保留 Hugging Face 启用方式，同时保留原始 zip 回退路径：[`HuggingFaceConnector.sample_from_physreason_zip()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:1337)

当标准 [`load_dataset()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:1202) 失败时，[`HuggingFaceConnector.sample()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:1421) 会自动切到 raw zip 解析路径。

### 6.4 Geometry3K GitHub 接入

`Geometry3K` 使用 InterGPS GitHub 仓库，仓库拉取由 [`GitHubConnector.ensure_repo()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:1496) 执行，结构发现与样本解析由 [`GitHubConnector.sample()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:1642) 完成。

对于 Geometry3K，还显式兜底查找：

- `img_diagram.png`
- `img_problem.png`
- `img_diagram_point.png`

对应代码在 [`GitHubConnector.sample()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:1691)。

---

## 7. Agent 体系设计

## 7.1 Agent 基类

所有 LLM agent 共享基类 [`BaseStructuredAgent`](benchmarkallinone/src/benchmarkallinone/pipeline.py:1744)，统一负责：

- 加载 prompt
- 把 payload 转成 JSON 用户消息
- 必要时附带图片
- 调用 OpenAI 兼容接口
- 返回结构化 JSON

这保证了所有 agent 具备统一接口和统一失败回退逻辑。

---

## 7.2 Source Intake Agent

### 作用

从原始记录里尽量抽出：

- `raw_question_text`
- `raw_answer_text`
- `choice_map`
- `image_paths`
- `force_requires_image`

### 代码位置

- 类定义：[`SourceIntakeAgent`](benchmarkallinone/src/benchmarkallinone/pipeline.py:1762)
- prompt：[`benchmarkallinone/prompts/extract_unified_sample.md`](benchmarkallinone/prompts/extract_unified_sample.md)
- 启发式回退：[`heuristic_extract_record_content()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:936)

### 设计特点

1. 先跑启发式字段猜测，再让 agent 修正。
2. agent 不能编造事实，只能从原始记录抽取。
3. 记录 `question_field / answer_field / image_field / choice_field / extraction_notes`，供后续审计。

---

## 7.3 Asset Registry Agent

### 作用

实现初步设计中的“资产登记”步骤，检查图像、题干、答案是否齐全。

### 代码位置

- 类定义：[`AssetRegistryAgent`](benchmarkallinone/src/benchmarkallinone/pipeline.py:1811)
- prompt：[`benchmarkallinone/prompts/collection/asset_registry.md`](benchmarkallinone/prompts/collection/asset_registry.md)

### 输出内容

- `image_manifest`
- `text_manifest`
- `answer_manifest`
- `issues`
- `registry_passed`

### 设计特点

1. 即使 agent 失败，也有 [`AssetRegistryAgent.fallback_process()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:1820) 保底。
2. 资产检查只做“可证实的问题”，不会脑补图片内容。
3. 为后续候选入池和初始评分提供最基础的完整性证据。

---

## 7.4 Potential Scorer Agent

### 作用

实现初步设计中的三种初始分数：

- `image_dependency_score`
- `multi_step_score`
- `verifiability_score`

### 代码位置

- 类定义：[`PotentialScorerAgent`](benchmarkallinone/src/benchmarkallinone/pipeline.py:1943)
- prompt：[`benchmarkallinone/prompts/collection/potential_scorer.md`](benchmarkallinone/prompts/collection/potential_scorer.md)

### 设计特点

1. 输入中显式带上 `multi_solution_policy`，使不同数据集的多解挖掘强度可控。
2. 如果资产登记失败，打分会自动保守。
3. 产出 `score_evidence`，保证评分可审计。

---

## 7.5 Candidate Registrar Agent

### 作用

实现初步设计中的“候选入池”：

- `keep`
- `low_priority`
- `reject`

### 代码位置

- 类定义：[`CandidateRegistrarAgent`](benchmarkallinone/src/benchmarkallinone/pipeline.py:2074)
- prompt：[`benchmarkallinone/prompts/collection/candidate_registrar.md`](benchmarkallinone/prompts/collection/candidate_registrar.md)

### 设计特点

1. 资产失败优先 reject。
2. 分数高且无风险时 keep。
3. 中间区域不直接丢弃，而是 low priority。

这一步对应初步设计里“高召回候选池”的理念。

---

## 7.6 Normalization Agent

### 作用

负责清洗阶段的基础规范化：

- 去题源噪声
- 统一答案表达
- 清洗选项结构
- 判断 `requires_image`
- 判断 `text_dominant`
- 选择 `cleaning_path`

### 代码位置

- 类定义：[`NormalizationAgent`](benchmarkallinone/src/benchmarkallinone/pipeline.py:2146)
- prompt：[`benchmarkallinone/prompts/cleaning/normalization_agent.md`](benchmarkallinone/prompts/cleaning/normalization_agent.md)
- 文本标准化工具：[`TextNormalizer`](benchmarkallinone/src/benchmarkallinone/pipeline.py:635)

### 关键实现细节

1. [`TextNormalizer.strip_exam_boilerplate()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:652) 去除考试头、分值头、题源噪声。
2. [`TextNormalizer.normalize_answer()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:680) 统一数字与字母答案。
3. [`TextNormalizer.infer_requires_image()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:740) 现在不再“只要有图就强制 requires_image=true”，而是：
   - 先检查显式视觉锚点
   - 再检查 `<image>` 占位符
   - 有图但无视觉依赖时允许进入文本主导分支
4. `requires_image=false` 时会在质量标记里打出 `text_only_without_visual_need`，并在最终门控中拒绝文本独立可解、但不满足多模态要求的样本。

这条修改是为了更贴合 [`benchmarkall/pipeline初步设计.md:204`](benchmarkall/pipeline初步设计.md:204) 中“完全只需要文字即可作答则去掉这道题”的要求。

---

## 7.7 Sample Understanding Agent

### 作用

不是做死板阈值过滤，而是判断一个样本在语义上是否仍然适合后续标注。

### 代码位置

- 类定义：[`SampleUnderstandingAgent`](benchmarkallinone/src/benchmarkallinone/pipeline.py:2243)
- prompt：[`benchmarkallinone/prompts/cleaning/sample_understanding_agent.md`](benchmarkallinone/prompts/cleaning/sample_understanding_agent.md)

### 输出状态

- `completeness_status`
- `image_support_status`
- `joint_understanding_status`
- `reason_codes`
- `risk_flags`
- `confidence`

### 设计特点

这部分最接近 PaperBanana 的“Critic / 审稿人式”角色：

- 不因低分辨率直接一票否决
- 更偏向给出 `partial` / `review`
- 只在语义真的坏掉时才打 `broken`

---

## 7.8 Rewrite Agent

### 作用

实现清洗阶段最关键的“选择题开放化改写”。

### 代码位置

- 类定义：[`RewriteAgent`](benchmarkallinone/src/benchmarkallinone/pipeline.py:2391)
- prompt：[`benchmarkallinone/prompts/cleaning/rewrite_agent.md`](benchmarkallinone/prompts/cleaning/rewrite_agent.md)

### 支持的策略

- `keep_open`
- `blank_open`
- `split_open`
- `drop_image_index`

### 关键实现点

1. 已经是开放题时直接 `keep_open`。
2. 一般选择题改成开放问答时使用 `blank_open`。
3. 复合答案选择题用 `split_open`。
4. 纯图片索引题使用 `drop_image_index`，对应初步设计中“纯图编号选择题直接淘汰”。

### 已修正的一点

[`RewriteAgent.fallback_rewrite()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:2400) 中，`blank_open` 现在会基于“解析后的真实答案文本”重新推断 `expected_answer_type`，而不是把原 `option` 类型错误地硬改成 `numeric`。这保证例如“答案是 A / B / C 对应的实体标签”时，开放题期待答案类型会变成 `short_text`。

---

## 7.9 Decision Agent

### 作用

对所有上游结构化证据做最终门控，输出：

- `pass`
- `review`
- `reject`

### 代码位置

- 类定义：[`DecisionAgent`](benchmarkallinone/src/benchmarkallinone/pipeline.py:2509)
- prompt：[`benchmarkallinone/prompts/cleaning/gate_decision_agent.md`](benchmarkallinone/prompts/cleaning/gate_decision_agent.md)

### 设计特点

1. 和 [`benchmarkallinone/prompts/cleaning/gate_decision_agent.md`](benchmarkallinone/prompts/cleaning/gate_decision_agent.md) 一致，采用“优先 review，不轻易 reject”的偏置。
2. 但仍对两类情况做硬拒绝：
   - `drop_image_index`
   - `text_only_without_visual_need`
3. 这保证最终清洗池不会混入不满足多模态约束的文本题或纯图编号题。

---

## 8. 非 agent 但关键的结构化模块

虽然用户要求采集与清洗全部用 agent 做，但这里的含义更合理地落成了：

- **判断与决策核心由 agent 主导**
- **可验证、可复现、低歧义的结构计算由规则模块完成**

这是必要的，因为以下对象更适合规则化稳定生成。

### 8.1 TextContextParser

- 类定义：[`TextContextParser`](benchmarkallinone/src/benchmarkallinone/cleaning_semantics.py:169)
- 作用：抽取条件、目标、回答槽位、文本实体

### 8.2 VisualParser

- 类定义：[`VisualParser`](benchmarkallinone/src/benchmarkallinone/cleaning_semantics.py:325)
- 作用：对图像做轻量视觉结构解析，不做 OCR 修复

### 8.3 AlignmentEngine

- 类定义：[`AlignmentEngine`](benchmarkallinone/src/benchmarkallinone/cleaning_semantics.py:447)
- 作用：建立图文对齐对、冲突对、覆盖分和一致性分

### 8.4 SolvabilityChecker

- 类定义：[`SolvabilityChecker`](benchmarkallinone/src/benchmarkallinone/cleaning_semantics.py:586)
- 作用：检查是否存在进入标注的最小可解路径

这些模块对应初步设计中的“图文对齐 / 可解性检查 / 结构化底座”，由规则实现能保持一致性和可审计性。

---

## 9. 结构化输出对象

当前单样本会输出下列对象，组装逻辑位于 [`MultiDatasetCleaningPipeline.process_sample()`](benchmarkallinone/src/benchmarkallinone/pipeline.py:3982)：

- `source_intake_record`
- `asset_registry_record`
- `initial_scoring_record`
- `candidate_registration_record`
- `normalization_record`
- `candidate_problem_record`
- `raw_asset_bundle`
- `candidate_pool_entry`
- `clean_pool_entries`
- `clean_problem_record`
- `normalized_assets`
- `problem_main_record`
- `asset_records`
- `text_structure_records`
- `visual_structure_records`
- `solvability_reports`
- `node_records`
- `cleaning_records`
- `reject_records`
- `alignment_records`
- `field_audit_records`
- `rewrite_reports`
- `open_ended_problem_variants`

每个数据集的这些 JSONL 记录文件都落在类似目录：[`benchmarkallinone/outputs/agent_multidataset_validation_10/run_10fb07acd544b44d/datasets/scemqa/records`](benchmarkallinone/outputs/agent_multidataset_validation_10/run_10fb07acd544b44d/datasets/scemqa/records)

---

## 10. 10 条验证配置与执行命令

### 10.1 配置文件

本次验证配置为 [`benchmarkallinone/configs/agent_multidataset_validation_10.yaml`](benchmarkallinone/configs/agent_multidataset_validation_10.yaml)。

特点：

- 五个目标数据集都开启
- 每个数据集抽 10 条
- 并发数设为 2
- 输出目录单独隔离

### 10.2 运行命令

通过 [`benchmarkallinone/run_pipeline.py`](benchmarkallinone/run_pipeline.py) 启动：

```bash
python3 ./benchmarkallinone/run_pipeline.py \
  --config ./benchmarkallinone/configs/agent_multidataset_validation_10.yaml \
  --api-key '***' \
  --base-url 'https://synai996.space/v1' \
  --model 'gpt-5.4' \
  --reasoning-effort 'high'
```

---

## 11. 本次验证结果

总运行摘要位于 [`benchmarkallinone/outputs/agent_multidataset_validation_10/run_10fb07acd544b44d/summary.json`](benchmarkallinone/outputs/agent_multidataset_validation_10/run_10fb07acd544b44d/summary.json)。

### 11.1 总体结果

- run id：`run_10fb07acd544b44d`
- 总耗时：2677.108 秒
- 总请求数：374
- 成功请求数：374
- 失败请求数：1
- 总 token：635,505
- reasoning token：109,868

### 11.2 各数据集结果

| 数据集 | 处理条数 | pass | review | reject | 备注 |
| --- | ---: | ---: | ---: | ---: | --- |
| SCEMQA | 10 | 3 | 7 | 0 | 开放题与普通选择题混合，改写以 `keep_open / blank_open` 为主 |
| Geometry3K | 10 | 2 | 8 | 0 | 全部保留为开放题，review 较多主要来自几何图约束复杂度 |
| CMM-Math | 10 | 7 | 1 | 2 | 两条因题干截断、目标缺失被 reject |
| MathVision | 10 | 2 | 7 | 1 | 两条被识别为纯图编号类，其中一条进入 reject |
| PhysReason | 10 | 5 | 5 | 0 | 全部成功进入处理链，部分样本因风险进入 review |

### 11.3 “每个数据集 10 条”核验结果

命令行二次核验结果表明，五个数据集都满足：

- `processed_samples = 10`
- `samples/*.json = 10`

验证输出中的 `sample_files=10` 已经说明每个数据集都真实落盘了 10 个样本 bundle，而不仅是 summary 计数。

---

## 12. 典型结果解读

### 12.1 MathVision 正常多模态开放题样本

可参考样本：[`benchmarkallinone/outputs/agent_multidataset_validation_10/run_10fb07acd544b44d/datasets/mathvision/samples/prob_f732438f47fa7b38775bb162.json`](benchmarkallinone/outputs/agent_multidataset_validation_10/run_10fb07acd544b44d/datasets/mathvision/samples/prob_f732438f47fa7b38775bb162.json)

该样本体现了完整链路：

- `Source Intake` 抽出题干、答案、图像路径
- `Asset Registry` 确认图像存在且可读
- `Potential Scorer` 给出较高图像依赖分
- `Normalization` 保留 `multimodal_full`
- `Rewrite` 识别为已开放题，使用 `keep_open`
- 最终形成完整结构化样本

### 12.2 CMM-Math 的 reject 原因

可见 [`benchmarkallinone/outputs/agent_multidataset_validation_10/run_10fb07acd544b44d/datasets/cmm_math/records/reject_records.jsonl`](benchmarkallinone/outputs/agent_multidataset_validation_10/run_10fb07acd544b44d/datasets/cmm_math/records/reject_records.jsonl) 中的两条记录。

被 reject 的核心原因不是“分辨率低”，而是：

- 题干明显截断
- 无法确定题目真正要求什么
- 即使进行 `blank_open` 改写，也无法恢复明确目标

这符合初步设计强调的“目标不明确、答案不可校验则淘汰”。

### 12.3 MathVision 纯图编号题剔除

可见 [`benchmarkallinone/outputs/agent_multidataset_validation_10/run_10fb07acd544b44d/datasets/mathvision/records/rewrite_reports.jsonl`](benchmarkallinone/outputs/agent_multidataset_validation_10/run_10fb07acd544b44d/datasets/mathvision/records/rewrite_reports.jsonl) 中：

- `prob_2ade924e60e14f2fc742fbe0`
- `prob_3d78becf15a57caf11f3ca84`

都被标记为 `drop_image_index`。

其中至少一条进入了 [`reject_records.jsonl`](benchmarkallinone/outputs/agent_multidataset_validation_10/run_10fb07acd544b44d/datasets/mathvision/records/reject_records.jsonl)，原因明确是：

- 任务本质上只是从 A-E 图里选一个图
- 无法转成有语义的开放问答目标

这正是 [`benchmarkall/pipeline初步设计.md:173`](benchmarkall/pipeline初步设计.md:173) 定义的“纯图编号选择题直接淘汰”。

---

## 13. 本次实现相对初步设计的对齐情况

### 13.1 已完成部分

#### 采集阶段

- 样本接入
- 资产登记
- 初步价值打分
- 候选入池

#### 清洗阶段

- 文本规范化
- 答案规范化
- 文本主导题识别
- 选择题开放化改写
- 纯图编号题剔除
- 图像质量分析
- 文本结构解析
- 视觉结构解析
- 图文对齐
- 可解性检查
- pass/review/reject 门控
- 全量 JSONL 审计落盘

### 13.2 尚未扩展的部分

- 标注阶段的 `P/T/K/R/S/A/B` 全量生成
- QA 审核闭环
- 格式化发布
- 发布后回流补丁

这部分没有纳入本次交付范围。

---

## 14. 当前实现的工程优势

### 14.1 agent-first，但不是 agent-only 幻觉化

当前实现采取“agent 主导决策 + 规则保证稳定”的平衡方式：

- 要理解语义、判断题型、决定门控时，交给 agent
- 要计算 bbox、readability、hash、对齐 coverage 时，交给规则

这样既满足了“采集和清洗要全部用 agent 做”的主旨，又避免让 agent 去生成本应稳定计算的字段，减少漂移。

### 14.2 全链路可审计

所有关键阶段都有独立记录文件，能回溯：

- 样本是如何抽取字段的
- 为什么被判定为需要图片 / 不需要图片
- 为什么被改写成开放题
- 为什么被 review 或 reject

### 14.3 多源接入已经统一

目前同一套主链已经覆盖：

- Hugging Face
- GitHub 仓库
- 本地文件
- Hugging Face raw zip fallback

这为之后继续接更多数据集提供了直接扩展点。

---

## 15. 后续建议

### 15.1 若要继续提升通过率

优先建议三件事：

1. 为 `CMM-Math` 增加“截断题干检测 + 上下文补救策略”
2. 为 `MathVision` 增加“可开放化的标签型选择题”更细粒度重写规则
3. 将 `Decision Agent` 的 reason code 进一步标准化，便于后续统计分析

### 15.2 若要进入下一阶段

建议直接以本次 run 的结构化输出为底座，在下一阶段新增：

- 标注代理
- 多解路径挖掘代理
- QA 审核代理
- 发布格式化模块

无需重做采集和清洗层。

---

## 16. 结论

本次已经完整落地并跑通一套基于 agent 的多数据集采集与清洗流水线，严格围绕 [`benchmarkall/pipeline初步设计.md`](benchmarkall/pipeline初步设计.md) 的 Collection 与 Cleaning 范围实现，并参考 [`PaperBanana-main/utils/paperviz_processor.py:37`](PaperBanana-main/utils/paperviz_processor.py:37) 的多 agent 编排思想完成了工程化组织。

最终结果是：

- 五个指定数据集全部接入完成
- 每个数据集都完成 10 条真实运行
- 输出了完整的结构化记录、样本 bundle 与 run summary
- 纯图编号题已按要求剔除
- 文本独立可解但不满足多模态约束的样本已按要求过滤
- 结果可直接作为后续标注阶段的输入底座
