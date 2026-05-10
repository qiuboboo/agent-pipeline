# GeoQA-Plus 改写题放行决策记录（2026-05-10）

## 适用范围

本记录适用于：

- `outputs/geoqa_plus_3040_4040/run_37eb9c7ed2c09962`

本次判断的核心问题是：很多样本因为原始选择题记录有噪声被标为 `review`，但如果只看改写后的开放题，题干、答案和数学逻辑是可用的。这类样本是否可以作为 review-release 候选进入 ready。

## 本次发现的问题

这批 GeoQA-Plus 样本的主要问题不是简单的“图片全错”，而是几个问题叠加：

- 原题通常是选择题，题干末尾有 `（）`，但具体选项文本缺失。
- 答案文本常常是完整解析，并在末尾写 `故选 X`，但原始 gold answer、选项映射或改写 expected answer 被记录为不一致。
- Hugging Face 原始图片字段在 metadata 中表现为 PIL 对象字符串，例如 `<PIL.Image ...>`，不是稳定图片路径。不过 pipeline 已经保存了可用的 artifact 图片。
- 很多图片是一张图里拼了多个小图，或包含一个额外无关图。这个会带来视觉噪声，但不一定破坏改写后的开放题。

因此，这批样本不能简单按原始 choice/gold answer 判断是否可用。对于部分样本，原始选择题标准答案确实不可靠，但开放题改写后的题干和 expected answer 是自洽的。

## 放行策略

本次新增一个显式候选桶，而不是按 reason code 一刀切：

- 候选文件：`docs/review/geoqa_plus_rewrite_release_candidates_2026-05-10.json`
- 候选 key：`rewrite_usable_no_key_condition_gap_candidates`
- policy bucket：`geoqa_plus.release_buckets.rewrite_release`

候选样本必须满足：

- 存在 open-ended variants。
- 每个 variant 都有 `rewritten_question_text` 和 `expected_answer`。
- `solvability_reports` 中 `answer_verifiable=true`、`target_clear=true`、`rewrite_complete=true`。
- 最新 cleaning agent assessment 判断为 `complete` 且 `understandable`。
- rewrite report 没有 discard reason codes。
- 不包含明确的核心语义坏信号，例如题目目标缺失、题干不完整、题图/题文冲突、答案明显不一致、rewrite consistency failed 等。
- 排除“题干关键条件缺失，必须靠图片、答案解析或隐含上下文补出来”的样本。

以下问题不作为本候选桶的硬拒绝条件：

- 原始选择题 gold answer 或选项映射不一致。
- 原始选项文本缺失。
- 图片中多了一个额外无关图，只要相关图和改写题仍能支持理解。
- metadata 中图片路径是 PIL 对象字符串，只要 artifact 图片实际存在。

## 数量统计

对于 `geoqa_plus_3040_4040`：

- 扫描/去重后样本数：`1000`
- 原始 pass：`1`
- 原始 review：`999`
- 原始 reject：`0`
- 候选桶行数：`813`
- 通过 `rewrite_release` 实际释放的 review：`812`
- 最终可进入 ready：`813`
- 仍丢弃的 review：`187`

候选桶中有 1 个样本本来就是原始 pass，所以候选桶行数是 `813`，实际 `released_review` 是 `812`。

候选桶内 rewrite strategy 分布：

- `blank_open`：`806`
- `split_open`：`5`
- `keep_open`：`2`

本候选规则排除项统计：

- `semantic_core_bad`：`80`
- `agent_understandable` 未通过：`106`
- `agent_complete` 未通过：`29`
- `key_condition_requires_image_or_recovery`：`1`

当前本地所有 `geoqa_plus` outputs 按 `source_problem_id` 去重后：

- release 前选中：`3001`
- 原始 pass：`1153`
- 原始 review：`1846`
- 原始 reject：`2`
- release review 总数：`979`
- 旧 A 桶释放：`167`
- 本次 `rewrite_release` 桶释放：`812`
- release 后可进入 ready：`2132`

## 抽样例子

### source_problem_id `3729`

- problem：`prob_15c79251a29a513903983335`
- 原题：正六边形外接圆，点 `P` 在圆上，求 `∠CPD`。
- 原始问题：答案解析给出 `30°或150°`，但末尾写 `故选：B`，且选项文本缺失。
- 图片问题：相关圆图存在，但右侧还有一个无关平行四边形图。
- 改写结果：
  - 情形 1：`P` 在弧 `CAD` 上，答案 `30°`。
  - 情形 2：`P` 在小弧 `CD` 上，答案 `150°`。
- 判断：原始选择题选项映射不可靠，但 split-open 改写后的两个开放题数学上成立。

### source_problem_id `3222`

- problem：`prob_52835eadb011dc2cbf6a00a0`
- 改写题：平行四边形 `ABCD` 对角线交于 `O`，两条对角线长度和为 `36`，`△OCD` 周长为 `23`，求 `AB`。
- expected answer：`5`
- 判断：`OC + OD = 18`，`OC + OD + CD = 23`，所以 `CD=5`，平行四边形对边相等，`AB=5`。改写题可用。

### source_problem_id `3157`

- problem：`prob_bae75a4f510a3f191ad6bb0a`
- 改写题：正方形变为菱形，`∠D′AB=60°`，求菱形面积与原正方形面积之比。
- expected answer：`sqrt(3)/2`
- 判断：改写题和答案逻辑一致，额外/弱视觉内容不影响核心数学关系。

### source_problem_id `3294`

- problem：`prob_7e0090b258028aef580ef231`
- 改写题：一副三角板摆放，`DE ∥ BC`，求 `∠BFC`。
- expected answer：`105°`
- 判断：题干、图示关系和答案一致。

### source_problem_id `3204`

- problem：`prob_c8d7033b8bc059ae6b100174`
- 改写题：圆与切线关系，`∠P=40°`，求 `∠B`。
- expected answer：`25°`
- 判断：题干完整，图示可支持，答案逻辑一致。

### source_problem_id `3291`（已排除）

- problem：`prob_4a58fe26f9b966be075861a2`
- 原题/改写题只写“在 `ABCD` 中”，但没有明确说明 `ABCD` 是平行四边形。
- 解答使用了平行四边形性质：`AB=DC`、`AD ∥ BC`。
- 判断：该题关键条件需要从图片或上下文补出，因此不进入本次候选桶。

## 剩余风险

这次放行是基于规则和抽样确认的 review-release，不是对全部 813 个样本逐题人工证明。主要剩余风险是：少数 expected answer 可能继承了源解析中的细微错误。

不过，本规则已经排除了显式语义冲突、题干关键条件缺失、答案明显不一致和 rewrite 失败等硬风险。抽样结果也支持本次判断：大量 review 是由原始选择题 gold/选项映射噪声导致，而不是改写后的开放题本身不可用。

