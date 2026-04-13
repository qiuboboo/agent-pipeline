# verified CoT 子流水线实现说明

## 1. 目标

[`benchmarkallinone/pipeline2/verified_cot_pipeline.py`](benchmarkallinone/pipeline2/verified_cot_pipeline.py) 只覆盖第二步标注中的前半段：

- 输入来自 [`benchmarkallinone/ready`](benchmarkallinone/ready)
- 根据 [`benchmarkallinone/main.md`](benchmarkallinone/main.md) 的思路构造题目级与方法级运行态
- 自动完成方法规划、求解、答案校验、CoT 验证、CoT 修复
- 最终输出“每题一个主 JSON”，其中保存这道题所有方法分支以及最终经过验证的 `CoT_final`

它**不负责**：
- claim 拆解
- `r_nodes` 构建
- `solution_library` 构建
- `evidence_bindings`
- 命中率评测
- 新解回流 patch

换句话说，这个子流水线的终点是：

- `method[].is_final_CoT_qualified`
- `method[].CoT_final`

---

## 2. 入口与配置

### 2.1 运行入口

- [`benchmarkallinone/run_verified_cot.py`](benchmarkallinone/run_verified_cot.py)
- 内部主入口为 [`main()`](benchmarkallinone/pipeline2/verified_cot_pipeline.py:688)

### 2.2 配置文件

- 默认配置：[`benchmarkallinone/pipeline2/configs/verified_cot_default.yaml`](benchmarkallinone/pipeline2/configs/verified_cot_default.yaml)
- smoke 配置：[`benchmarkallinone/pipeline2/configs/verified_cot_smoke.yaml`](benchmarkallinone/pipeline2/configs/verified_cot_smoke.yaml)

### 2.3 推荐运行命令

```bash
PIPELINE2_API_KEY_PRIMARY="..." PIPELINE2_API_KEY_FALLBACK="..." \
python3 benchmarkallinone/run_verified_cot.py \
  --config benchmarkallinone/pipeline2/configs/verified_cot_smoke.yaml
```

---

## 3. 输入要求

输入必须来自 [`benchmarkallinone/ready`](benchmarkallinone/ready) 下的 `prob_*.json`。

每道题至少要求：

- `clean_pool_entries` 中状态允许进入该阶段
- 有 `problem_id`
- 有规范化题干
- 有规范化标准答案
- 若题目 `requires_image=true`，则必须能解析到至少一张真实图片

上述加载逻辑位于：
- [`load_ready_problem()`](benchmarkallinone/pipeline2/ready_loader.py:146)
- [`discover_ready_problems()`](benchmarkallinone/pipeline2/ready_loader.py:213)

若不满足输入契约，会抛出 [`ReadyDataContractError`](benchmarkallinone/pipeline2/ready_loader.py:10)。

---

## 4. 运行态结构与字段

这个子流水线参考 [`benchmarkallinone/main.md`](benchmarkallinone/main.md) 的 `problem -> method[]` 结构，但做了最小必要扩展。

## 4.1 顶层题目字段

每个题目主 JSON 顶层字段包括：

- `batch_id`
- `problem_id`
- `question_text`
- `standard_answer`
- `images`
- `initial_multi_solution_score`
- `method`
- `input_context`
- `verified_cot_summary`

### 字段解释

#### `batch_id`
表示这道题属于哪次批处理运行。用于断点恢复和区分不同批次结果。

#### `problem_id`
题目唯一标识。来自 ready 样本中的题号。

#### `question_text`
进入标注时使用的规范化题干文本。

#### `standard_answer`
进入标注时使用的标准答案文本。

#### `images`
真实图片路径列表。这里保存的是可读取的图片文件绝对路径或稳定相对路径。

#### `initial_multi_solution_score`
上游清洗阶段给出的多解潜力分数，用来决定这道题要生成几个方法分支。

#### `method`
该题所有方法分支的数组，是本子流水线的核心字段。

#### `input_context`
这道题的输入背景信息摘要，不参与方法执行逻辑本身，但有助于定位样本来源。

它包括：
- `dataset_name`：数据集名字
- `source_problem_id`：原始题号
- `subject`：学科
- `requires_image`：是否必须使用图像
- `text_dominant`：是否文本主导
- `alignment_status`：图文对齐状态
- `solvability_score`：上游可解性分数
- `sample_path`：ready 样本路径
- `clean_pool_status`：清洗池状态
- `clean_decision`：清洗阶段结论

#### `verified_cot_summary`
表示该题在 verified CoT 阶段的总体结果。

它包括：
- `planned_method_count`：一共规划了多少个方法
- `qualified_method_count`：多少个方法最终通过验证
- `verified_cot_ready`：这道题是否至少有一个通过验证的最终 CoT

---

## 4.2 方法级字段

每个 `method[]` 元素字段参考 [`benchmarkallinone/main.md`](benchmarkallinone/main.md) 并保留同名主字段：

- `method_id`
- `method_draft`
- `CoT_raw`
- `model_answer`
- `is_answer_match`
- `answer_match_reason`
- `answer_match_part_results`
- `CoT_answer_check_final`
- `answer_answer_check_final`
- `CoT_verify_0`
- `CoT_qualify_0`
- `CoT_after_polish_1`
- `CoT_verify_1`
- `CoT_qualify_1`
- `CoT_after_polish_2`
- `CoT_verify_2`
- `CoT_qualify_2`
- `CoT_after_polish_3`
- `CoT_verify_3`
- `CoT_qualify_3`
- `is_final_CoT_qualified`
- `CoT_final`
- `planner_metadata`
- `solver_metadata`
- `verify_reports`

### 字段解释

#### `method_id`
方法分支编号，例如 `1`、`2`、`3`。

#### `method_draft`
该方法的高层解题路线描述。由方法规划 agent 生成。

#### `CoT_raw`
该方法第一次求解时直接生成的原始 CoT。

#### `model_answer`
与 `CoT_raw` 同轮产出的原始答案。

#### `is_answer_match`
这条方法当前答案是否和标准答案匹配。

#### `answer_match_reason`
答案判等模块给出的结论说明。

#### `answer_match_part_results`
对于多子问题目，逐部分比对结果的列表。每个元素会说明某一部分答案是否等价。

#### `CoT_answer_check_final`
在答案校验阶段之后保留下来的 CoT 版本。

- 如果原始答案就匹配，这里等于 `CoT_raw`
- 如果原始答案不匹配，这里等于修复后的 CoT

#### `answer_answer_check_final`
与 `CoT_answer_check_final` 对应的最终答案版本。

#### `CoT_verify_0`
对 `CoT_answer_check_final` 的第 0 轮验证是否通过。

#### `CoT_qualify_0`
第 0 轮验证给出的修改建议。

#### `CoT_after_polish_1`
根据第 0 轮建议修复后的第一版 CoT。

#### `CoT_verify_1`
对 `CoT_after_polish_1` 的验证结果。

#### `CoT_qualify_1`
第 1 轮验证给出的修改建议。

#### `CoT_after_polish_2`
根据第 1 轮建议修复后的第二版 CoT。

#### `CoT_verify_2`
对 `CoT_after_polish_2` 的验证结果。

#### `CoT_qualify_2`
第 2 轮验证给出的修改建议。

#### `CoT_after_polish_3`
根据第 2 轮建议修复后的第三版 CoT。

#### `CoT_verify_3`
对 `CoT_after_polish_3` 的验证结果。

#### `CoT_qualify_3`
第 3 轮验证给出的修改意见。通常到这里已经不再继续修复。

#### `is_final_CoT_qualified`
该方法最终是否拥有一个通过验证的 CoT。

#### `CoT_final`
最终保留下来的 CoT：
- 若某一轮通过，则取通过的那个版本
- 若全部失败，则保留最后一版修复结果，但 `is_final_CoT_qualified=false`

#### `planner_metadata`
方法规划阶段生成的附加解释，包括：
- `distinctiveness_rationale`：这条方法为什么与其它方法不同
- `image_role`：图像在这条方法里扮演什么角色
- `text_role`：题干文本在这条方法里扮演什么角色
- `knowledge_role`：关键知识桥梁是什么

#### `solver_metadata`
求解阶段模型原始返回中的额外元数据，例如 `_llm_usage`、`_llm_elapsed_seconds` 等。

#### `verify_reports`
每一轮验证的结构化记录列表。每个元素包括：
- `round_index`：第几轮
- `verify_pass`：该轮是否通过
- `critic_suggestions`：修改建议
- `major_failures`：关键失败项列表
- `extractability_score`：可拆解度分数
- `grounding_score`：图像 grounding 分数
- `method_fidelity_score`：方法忠实度分数

---

## 5. 执行主线

## 5.1 方法级 LangGraph

方法级图由 [`build_method_graph()`](benchmarkallinone/pipeline2/verified_cot_pipeline.py:360) 构建。

执行顺序如下：

1. `generate_cot`
2. `answer_check`
3. `verify_round_0`
4. `polish_round_1`（若第 0 轮失败）
5. `verify_round_1`
6. `polish_round_2`（若第 1 轮失败）
7. `verify_round_2`
8. `polish_round_3`（若第 2 轮失败）
9. `verify_round_3`
10. `finalize_method`

### 各节点作用

#### `generate_cot`
函数：[`_generate_cot_node()`](benchmarkallinone/pipeline2/verified_cot_pipeline.py:191)

输入：
- 题目对象
- 一个空方法对象，但含有 `method_draft`

输出：
- 写入 `CoT_raw`
- 写入 `model_answer`

#### `answer_check`
函数：[`_answer_check_node()`](benchmarkallinone/pipeline2/verified_cot_pipeline.py:208)

输入：
- 当前 CoT
- 当前答案
- 标准答案

输出：
- 填充 `is_answer_match`
- 填充 `answer_match_reason`
- 填充 `answer_match_part_results`
- 更新 `CoT_answer_check_final`
- 更新 `answer_answer_check_final`

#### `verify_round_i`
函数：[`_verify_round()`](benchmarkallinone/pipeline2/verified_cot_pipeline.py:248)

输入：
- 当前版本 CoT
- 方法草稿
- 标准答案

输出：
- `CoT_verify_i`
- `CoT_qualify_i`
- 在 `verify_reports` 中写入结构化验证日志

#### `polish_round_i`
函数：[`_polish_round()`](benchmarkallinone/pipeline2/verified_cot_pipeline.py:286)

输入：
- 当前 CoT
- 上一轮验证建议

输出：
- `CoT_after_polish_i`

#### `finalize_method`
函数：[`_finalize_method_node()`](benchmarkallinone/pipeline2/verified_cot_pipeline.py:331)

作用：
- 选择最终通过的 CoT
- 写入 `CoT_final`
- 写入 `is_final_CoT_qualified`

---

## 5.2 题目级 LangGraph

题目级图由 [`build_problem_graph()`](benchmarkallinone/pipeline2/verified_cot_pipeline.py:526) 构建。

执行顺序：
- `prepare_methods`
- `run_methods`
- `finalize_verified_cot_problem`

### `prepare_methods`
函数：[`_prepare_methods_node()`](benchmarkallinone/pipeline2/verified_cot_pipeline.py:402)

作用：
- 读取 `initial_multi_solution_score`
- 根据阈值决定方法数
- 调用方法规划 agent
- 初始化每个方法对象

### `run_methods`
函数：[`_run_methods_node()`](benchmarkallinone/pipeline2/verified_cot_pipeline.py:436)

作用：
- 逐个方法跑 method graph
- 收集每个方法的最终状态

### `finalize_verified_cot_problem`
函数：[`_finalize_verified_cot_problem_node()`](benchmarkallinone/pipeline2/verified_cot_pipeline.py:519)

作用：
- 组装每题最终 JSON
- 检查至少有一个方法通过验证
- 落盘到每题单文件输出目录

---

## 5.3 batch 级 LangGraph

batch 级图由 [`build_batch_graph()`](benchmarkallinone/pipeline2/verified_cot_pipeline.py:577) 构建。

作用：
- 让多道题并发执行题目级图
- 保持每题互相隔离
- 支持 checkpoint / resume

---

## 6. 输入到 verified CoT 的必要模块

在这个子流水线里，真正必要而且已经保留的模块只有：

1. ready 样本装载
2. 方法规划 agent
3. 求解 agent
4. 答案判等模块
5. 答案修复 agent
6. CoT 验证 agent
7. CoT 修复 agent
8. 方法级与题目级调度器

没有保留任何“为了未来节点化而提前执行”的多余步骤。

也就是说，这个子流水线是**最小必要闭环**：

`ready -> problem -> methods -> raw CoT/answer -> answer repair -> CoT verify/polish -> verified CoT final`

---

## 7. 输出目录

该子流水线只要求每题一个主文件。

默认输出目录来自配置，例如：
- [`benchmarkallinone/pipeline2/configs/verified_cot_default.yaml`](benchmarkallinone/pipeline2/configs/verified_cot_default.yaml)
- [`benchmarkallinone/pipeline2/configs/verified_cot_smoke.yaml`](benchmarkallinone/pipeline2/configs/verified_cot_smoke.yaml)

每题主文件路径形式：

- `pipeline2/verified_cot_outputs/problems/<problem_id>.json`
- 或 smoke 下的 `pipeline2/verified_cot_outputs_smoke/problems/<problem_id>.json`

可选调试产物：
- `annotation_runtime/problems.json`
- `annotation_runtime/method_runs/...`

但这些只是运行时快照，不是正式依赖输出。

---

## 8. 与 [`benchmarkallinone/main.md`](benchmarkallinone/main.md) 的关系

这个子流水线严格参考 [`benchmarkallinone/main.md`](benchmarkallinone/main.md) 的核心设计：

- 顶层是题目对象
- 题目下有 `method[]`
- 每个方法都有：
  - `method_draft`
  - `CoT_raw`
  - `model_answer`
  - `is_answer_match`
  - `CoT_answer_check_final`
  - `answer_answer_check_final`
  - `CoT_verify_0..3`
  - `CoT_qualify_0..3`
  - `CoT_after_polish_1..3`
  - `is_final_CoT_qualified`
  - `CoT_final`

区别是：
- 实现里增加了 `answer_match_reason`、`answer_match_part_results`、`planner_metadata`、`solver_metadata`、`verify_reports`
- 这些新增字段不是偏离，而是为了让验证过程可追踪、可调试、可复现

---

## 9. 当前运行边界

这个子流水线已经实现为**严格模式**：

- 如果方法规划 agent 没有返回合法 JSON，直接失败
- 如果 solver 没有返回 `cot_raw` 或 `model_answer`，直接失败
- 如果 CoT verify 没有返回合法字段，直接失败
- 如果题目要求看图却没有图片，直接失败
- 不再用模板内容兜底

唯一保留的 fallback 是：
- 主备模型端点切换

这属于基础设施高可用，不属于内容级 fallback。

---

## 10. 后续衔接

当这个 verified CoT 子流水线跑完后，后续节点化阶段只需要读取每题主 JSON 中：

- `problem_id`
- `question_text`
- `standard_answer`
- `images`
- `method[]`

然后只挑：
- `is_answer_match=true`
- `is_final_CoT_qualified=true`

的方法进入 claim 拆解与节点构建即可。

因此，它可以自然作为更完整第二步 pipeline 的前半段输入层。