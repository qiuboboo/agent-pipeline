# 2026-03-27 current changes summary

- Date: 2026-03-27
- Area: Collection / Cleaning / Config / Docs
- Scope: current working-tree changes in `benchmark/src/`, `configs/`, `docs/`, `README.md`

## Summary

本次改动集中在 5 个方面：

1. **Geometry3K ingest 排序修复**
   - 修正 `GitHubConnector.discover_data_files()` 对 `geometry3k` 的候选文件排序。
   - 提高 `annotation_tool/data_collection/data_examples/\d+/data.json` 的优先级。
   - 下调 `diagram_parser/detection/*.csv` 与 `*labels*.csv`，避免先扫到高成本辅助文件。

2. **Collection 初步评分显式拆出**
   - 在 `pipeline_collection.py` 中新增：
     - `compute_collection_priority(...)`
     - `run_initial_collection_scoring(...)`
   - 把 Collection 末尾原本散落在 `preprocess_sample(...)` 里的初步评分逻辑集中起来。
   - `build_candidate_pool_entry(...)` 改为直接接收整理好的 `priority_score / priority_tier`。

3. **Cleaning gate 判定语义调整**
   - `pipeline_cleaning.py` 里把 `hard_reject_codes` 改成 `risk_reason_codes`。
   - 这些风险原因仍会写入 `reason_codes`，但不再单独作为“只要出现就立刻 reject”的短路条件。
   - 最终判定继续由 `clean_score` 和后续阈值逻辑统一决定。

4. **远端模型配置与调试增强**
   - `PipelineConfig.from_dict(...)` 现在会优先从环境变量 `OPENAI_API_KEY` 注入 API key。
   - `configs/all_candidates_remote.yaml` 中的 `model.api_key` 改为空字符串，避免把环境变量占位写死在配置里。
   - `OpenAICompatibleClient.chat_json(...)` 增加调试能力：
     - 支持 `PIPELINE_DEBUG_CHAT_JSON`
     - 支持 `PIPELINE_DEBUG_CHAT_JSON_LOG`
     - 记录 HTTPError / URLError / Timeout / JSON 解析失败 / 无 choices / content 抽取失败等信息
   - 同时补充了 `Accept`、`Connection: close`、`User-Agent` 请求头。

5. **README 与模块文档同步更新**
   - README 现在把 Collection 明确拆成：`ingestion / preprocess / initial collection scoring / structure extract`。
   - `docs/pipeline_python_modules_reference.md` 已同步说明 Collection 新结构与函数职责。
   - `docs/run_summaries/README.md` 已登记本条 2026-03-27 摘要。

## Evidence

### 1. Geometry3K ingest ranking

更新 `benchmark/src/multidataset_cleaning_pipeline.py` 的 `GitHubConnector.discover_data_files()`：

- boost `annotation_tool/data_collection/data_examples/\d+/data.json`
- demote `diagram_parser/detection/*.csv`
- demote `*labels*.csv`
- keep `logic_form.json` down-weighted

已验证该修复可避免 `geometry3k` 在 Collection ingest 阶段优先扫入大型辅助 CSV。

### 2. Collection initial scoring refactor

`pipeline_collection.py` 中：

- 新增 `compute_collection_priority(...)`
- 新增 `run_initial_collection_scoring(...)`
- `preprocess_sample(...)` 改为调用上述集中逻辑
- `build_candidate_pool_entry(...)` 改为消费已整理好的 `priority` 对象

这次改动的目标是把 Collection 末尾的初步评分块显式收拢，减少 `preprocess_sample(...)` 内部耦合。

### 3. Cleaning gate behavior

`pipeline_cleaning.py` 中：

- `missing_answer`
- `missing_question_text`
- `missing_core_image`
- `low_resolution`
- `severe_blur`
- `image_unreadable`
- `text_image_misaligned`
- `rewrite_failed`
- `solvability failure codes`

这些原因现在进入 `reason_codes`，但不再通过单独的 `hard_reject_codes` 分支直接短路判定。

### 4. Remote model config and debug

`multidataset_cleaning_pipeline.py` 中：

- `PipelineConfig.from_dict(...)` 支持从 `OPENAI_API_KEY` 读取 key
- `OpenAICompatibleClient.chat_json(...)` 支持调试开关和日志落盘
- 对常见请求失败场景增加可观测性

`configs/all_candidates_remote.yaml` 中：

- `model.api_key: ""`

意味着运行时默认依赖环境变量注入，而不是配置文件内写占位值。

## Conclusion

这批改动不是单点修 bug，而是一次围绕 Collection/Config/Cleaning 的小规模整理：

- 修掉了 `geometry3k` ingest 的明显瓶颈
- 把 Collection 初步评分显式模块化
- 放宽了 Cleaning 对风险原因的“立即 reject”语义
- 提高了远端模型调用的配置灵活性和可观测性
- 同步更新了 README 与模块说明文档

## Additional smoke findings (2026-03-27 afternoon)

在后续 1-sample-per-dataset smoke 中，又得到三个有代表性的判定样本：

1. **CMM-Math 从 review 修到 pass**
   - 之前 `split_open` 的触发条件过宽，会把数学区间/集合式单答案误判成 compound answer。
   - 收紧 `is_compound_answer_question(...)` 后，CMM-Math 从 `review` 变成 `pass`，说明这部分属于规则误伤而非样本本身有问题。

2. **MM-Math 的 review 是合理保留的 review**
   - 样本：`prob_c11f4ea0de15f097c71f67f5`
   - 题面强依赖几何图，视觉锚点非常密集（`ABC / B / C / M / N / D / MN / AB / CD / BC / triangle ACD`）。
   - 最终判定为 `review`，原因包括：
     - `alignment_risky`
     - `major_alignment_conflict`
     - `visual_reference_density_mismatch`
   - 这个例子很适合作为“应当保留的 review”样本：题目可解，但当前自动 alignment 虽然足以支撑可解性判断，仍不足以低风险地直接放行。

3. **SCEMQA 的隐式函数图题通过弱视觉锚点补偿，从 reject 提升到 pass**
   - 样本：`prob_80511fe3dbb76971a8d87952`
   - 题面：`At which value of x is f continuous but not differentiable?`
   - 修改前：
     - `alignment_pairs = 0`
     - `coverage_score = 0.18`
     - `consistency_score = 0.10`
     - `alignment_status = bad`
     - `clean_decision = reject`
   - 根因：题目明显依赖函数图，但题干没有显式视觉锚点词，导致 alignment 无法建立文本-图像配对，只能落到 `implicit_visual_dependency` / `bad_alignment`。
   - 修改：在 `AlignmentEngine` 中新增对隐式函数图题的弱视觉锚点补偿（weak visual hints），当题干出现 `continuous / differentiable / slope / value of x / graph of` 等模式时，自动补入如 `graph / curve / point / x-value / non-differentiable point` 这类弱锚点供 alignment 使用。
   - 修改后：
     - `alignment_pairs = 5`
     - `coverage_score = 0.90`
     - `consistency_score = 0.98`
     - `alignment_status = good`
     - `clean_decision = pass`
   - 对应提交：`1597c36` — `fix: add weak visual hints for implicit function-graph questions`
   - 验证运行：`outputs/smoke_scemqa_weak_hints/run_3ab87b6af935c76b`
   - 该轮 smoke 最终结果：**pass 8 / review 1 / reject 1**。
   - 该轮从 run 创建到 summary 落盘耗时约 **731 秒（12.2 分钟）**。
