# PPT 加入生产环境数据方案

生成时间：2026-05-13

数据来源：
- `ready/ready_dataset_layout.md`
- `plans/ppt_production_stats_2026-05-13/`
- `plans/ppt_pipeline_outputs_review_ready_plan_2026-05-13.md`
- `plans/ready_sample_analysis_2026-05-12/final_taxonomy_package/`

用途：把全局 ready 资产和 5 月 7 日以来的生产子集一起放进组会 PPT，但必须分开口径。

## 1. 先把口径拆开

1. 全局 ready 资产口径：`29,966` 个去重候选，`21,555` 个最终 pass，覆盖 `21` 个数据集，`6` 个主领域，`14` 类粗粒度 taxonomy。
2. 生产子集口径：`47` 个 canonical production runs，`12,114` 个 processed samples，`88,169` 次 requests，最终 `19,113` 个 final ready。
3. PPT 里不要把这两层数字写到同一个总览页上。

## 2. 可直接引用的关键数字

### 2.1 全局 ready 资产规模

来源：`ready/ready_dataset_layout.md`

- 总候选数：`29,966`
- 最终 pass：`21,555`
- pass rate：`71.93%`
- 覆盖主领域：`6`

PPT 表述：

> 当前完整 ready 资产的口径是 29,966 个去重候选样本，其中 21,555 个最终写入 ready；这才是全局规模，不是 5 月 7 日以来的生产子集。

### 2.2 生产子集 Pipeline1 运行统计

来源：`plans/ppt_production_stats_2026-05-13/01_run_level_usage_summary.md / .csv`

- canonical production runs：`47`
- processed samples：`12,114`
- request count：`88,169`
- successful requests：`77,290`
- text requests：`65,589`
- multimodal requests：`22,580`
- total request seconds：`1,113,875.56` 秒
- 平均 requests / sample：`7.28`
- 平均 request seconds / sample：`91.95` 秒
- 平均 seconds / request：`12.63` 秒

PPT 表述：

> 5 月 7 日以来的生产子集中，Pipeline1 对 12,114 个样本产生 88,169 次模型请求，平均每个样本约 7.28 次请求、累计请求耗时约 92 秒。

### 2.3 生产子集 outputs 到 ready 总体转化

来源：`plans/ppt_production_stats_2026-05-13/02_dataset_level_outputs_to_ready_conversion.md / .csv`

合计口径：

- processed：`32,292`
- pass：`16,495`
- review：`12,744`
- reject：`386`
- released review：`2,618`
- dropped review：`10,126`
- dedup removed：`2,667`
- final ready：`19,113`

计算比例：

- review rate：`39.5%`
- review 中实际 release 比例：`20.5%`
- final ready / processed：`59.2%`

PPT 表述：

> 生产子集里的 ready 不是简单复制 outputs，而是经过 release policy、去重和风险过滤后的结果。

### 2.4 review release 实际执行

来源：`plans/ppt_production_stats_2026-05-13/03_review_release_actual_execution.md / .csv`

主要实际释放：

| 数据集 | bucket | actual released |
| --- | --- | ---: |
| mm_math | A | 1,114 |
| ai2d | A | 751 |
| geoqa_plus | A | 305 |
| multi_physics | A | 257 |
| multi_physics | B1 | 123 |
| physreason | A | 52 |
| multi_physics | B2 | 9 |
| seephys | A1 | 7 |

PPT 表述：

> 实际释放集中在 alignment-only 或 alignment + grounding path 一类非致命风险，而关键条件缺失、答案冲突和图文冲突仍被保留为风险。

### 2.5 全局 ready 域分布

来源：`ready/ready_dataset_layout.md`

- total ready samples：`21,555`
- dataset count：`21`
- domain count：`6`

| 领域 | pass | total | pass rate |
| --- | ---: | ---: | ---: |
| 数学 | 10,084 | 14,185 | 71.09% |
| 物理 | 4,573 | 6,981 | 65.51% |
| 化学 | 1,222 | 1,782 | 68.57% |
| 生物 | 1,598 | 1,809 | 88.34% |
| 地理 | 2,055 | 2,298 | 89.43% |
| 电子电路 | 2,023 | 2,911 | 69.50% |

PPT 表述：

> 全局 ready 资产在 6 个主领域里以数学、物理和地理为主；这和 5 月 7 日以来的生产子集不是同一个口径。

### 2.6 14 类粗粒度 taxonomy

来源：
- `plans/ppt_pipeline_outputs_review_ready_plan_2026-05-13.md`
- `plans/ready_sample_analysis_2026-05-12/coarse_level1_taxonomy_14_2026-05-13.md`

- total ready samples：`21,555`
- dataset count：`21`
- taxonomy class count：`14`

| 一级 taxonomy | 代表方向 | 占比 |
| --- | --- | ---: |
| 几何与空间推理 | 视觉数学主干 | 40.9% |
| 电磁、电路与电子系统 | 电路与电子系统 | 12.7% |
| 力学与运动 | 经典力学主干 | 12.3% |
| 地球空间、气候与自然地理 | 地理主干 | 5.9% |
| 代数、离散数学与应用数学 | 数学非几何 | 5.5% |
| 化学结构与分子表示 | 化学结构主干 | 4.4% |
| 生态、生理与生命系统 | 生命科学主干 | 3.9% |
| 生命分子、细胞与遗传 | 细胞与遗传主干 | 3.4% |

PPT 表述：

> 14 类粗粒度 taxonomy 把 ready 资产拆成“几何/力学/电路”三大主轴，并保留化学、生命科学和地理的跨学科覆盖。

### 2.7 review 原因分布

来源：`plans/ppt_production_stats_2026-05-13/06_reason_category_distribution.md / .csv`

注意：这是 reason occurrence，不是 unique sample。

| 原因类别 | 出现次数 | 占比 |
| --- | ---: | ---: |
| alignment / metadata consistency | 22,643 | 32.1% |
| other | 20,285 | 28.7% |
| answer / target solvability | 11,594 | 16.4% |
| visual grounding / image quality | 9,359 | 13.3% |
| rewrite / structure / options | 6,699 | 9.5% |

PPT 表述：

> review 原因主要来自 alignment/metadata、一部分答案可解性、视觉 grounding/image quality 和改写结构问题。

### 2.8 rewrite-resolvability

来源：`plans/ppt_production_stats_2026-05-13/06_rewrite_resolvability_distribution.md / .csv`

- rewritten_and_solvable：`17,575`
- rewritten_but_still_risky：`1,538`

PPT 表述：

> 大部分改写样本最终可解，但仍有 1,538 个 occurrence 被标记为 rewritten but still risky，说明 rewrite 不能替代质量门控。

## 3. 推荐 PPT 页结构

### 第 1 页：全局 ready 资产概览

标题：

> ready 资产全局规模

图形：

三张指标卡：

- 29,966 total candidates
- 21,555 ready pass
- 14 taxonomy classes

讲述句：

> 29,966 是全局去重候选总量，21,555 是最终 ready pass。

### 第 2 页：Ready Pass 数据资产结构图

标题：

> Ready Pass 数据资产结构图

图形：

这一页不要做成文件包结构图，也不要出现 `dataset_summary`、`taxonomy.csv`、`sample_list.csv`、`feature_stats.csv` 等内部文件名。它应该表达“最终 ready pass 资产有哪些覆盖、有哪些分析证据”。

一句话声明：

> 当前 ready pass 资产覆盖 6 个主领域、21 个核心数据集，并已形成可用于论文分析的题型 taxonomy 与数据特征统计。

主图建议：

左侧三张强指标卡：

- 21,555 ready pass
- 21 datasets
- 14 coarse taxonomy classes

中间按领域列出数据集标签：

| 领域 | 数据集 |
| --- | --- |
| 数学 | mm_math、geoqa_plus、mathvision、geometry3k、scemqa_math、cmm_math |
| 物理 | seephys、phyx、physreason、multi_physics、emma_physics、sciverse_physics |
| 化学 | emma_chemistry、sciverse_chemistry、scemqa_chemistry |
| 生物 | ai2d_biology、sciverse_biology、scemqa_biology |
| 地理 | geosqa、ai2d_geography |
| 电子电路 | eee_bench |

右侧或下方必须放真实统计图，不要只写“统计图”三个字，也不要把图片文件名显示在 PPT 页面上：

- 用 `paper_subject_pie.png` 作为领域分布图素材，页面图题写“领域分布”
- 用 `paper_final_category_bar.png` 作为 taxonomy 类别柱状图素材，页面图题写“题型结构”
- 用 `paper_complexity_scatter.png` 或 `paper_question_length_boxplot.png` 作为复杂度/题长图素材，页面图题写“复杂度与题长”

底部结论条：

> 资产已经从“样本集合”整理为“领域覆盖 + 题型 taxonomy + 特征统计”的分析对象。

### 第 3 页：生产子集成本与请求

标题：

> 5 月 7 日以来的生产子集

图形：

横向流程图。这个图不要做成“流程线 + 底部大指标条”，而要做成“中间流程线 + 每个节点一个上下交错的对话框/标注气泡”：

```text
原始样本 → 规范化 → Prompt 构造 → 模型改写 → 图像资产 → 清洗验证 → outputs
```

节点气泡建议：

| 节点 | 气泡位置 | 气泡短说明 | 指标 |
| --- | --- | --- | --- |
| 原始样本 | 上 | 生产窗口子集，不等于全局 ready | 12,114 processed |
| 规范化 | 下 | 统一字段和元数据 | 47 runs |
| Prompt 构造 | 上 | 每个样本触发多轮请求 | 7.28 requests/sample |
| 模型改写 | 下 | 覆盖文本与多模态请求 | 88,169 requests |
| 图像资产 | 上 | 保留视觉 grounding 资产 | 22,580 multimodal requests |
| 清洗验证 | 下 | 通过质量门控进入 outputs | 77,290 successful requests |
| outputs | 上 | 后续进入 ready 转化漏斗 | 91.95 sec/sample |

版式要求：

- 流程线居中横向贯穿页面，节点间距均匀。
- 对话框用白底、细绿色描边、轻微阴影或无阴影。
- 每个气泡只放一句短说明和一个数字，不要写成段落。
- 页面底部最多放一句口径提醒，不要再放大面积指标卡。

讲述句：

> 这部分统计只覆盖生产窗口中的一个子集，不等于全局 ready 资产。

### 第 4 页：生产子集 outputs → ready 漏斗

标题：

> outputs → ready：选择、去重与质量门控

图形：

```text
processed 32,292
→ pass 16,495
→ review 12,744
→ released review 2,618
→ dedup removed 2,667
→ final ready 19,113
```

旁边标注：

- review rate：39.5%
- review release rate：20.5%
- final ready rate：59.2%

讲述句：

> 生产子集里的 ready 不是简单复制 outputs，而是经过 release policy、去重和风险过滤后的结果。

### 第 5 页：Review release 实际放行

标题：

> Review release：释放非致命工程风险，保留语义风险

图形：

左侧规则框：

```text
pass → ready
review → only if matched policy
reject → dropped
```

右侧 Top release bar：

- mm_math A：1,114
- ai2d A：751
- geoqa_plus A：305
- multi_physics A/B：389
- physreason A：52
- seephys A1：7

讲述句：

> 实际释放集中在 alignment-only 或 alignment + grounding path 一类非致命风险。

### 第 6 页：全局 Ready 域分布

标题：

> 全局 ready：6 个主领域

图形：

| 领域 | pass | total | pass rate |
| --- | ---: | ---: | ---: |
| 数学 | 10,084 | 14,185 | 71.09% |
| 物理 | 4,573 | 6,981 | 65.51% |
| 化学 | 1,222 | 1,782 | 68.57% |
| 生物 | 1,598 | 1,809 | 88.34% |
| 地理 | 2,055 | 2,298 | 89.43% |
| 电子电路 | 2,023 | 2,911 | 69.50% |

讲述句：

> 全局 ready 资产在数学、物理和地理上最集中。

### 第 7 页：14 类粗粒度 taxonomy

标题：

> ready taxonomy：14 类粗粒度题型

图形：

- 几何与空间推理：40.9%
- 电磁、电路与电子系统：12.7%
- 力学与运动：12.3%
- 地球空间、气候与自然地理：5.9%
- 代数、离散数学与应用数学：5.5%
- 化学结构与分子表示：4.4%
- 生态、生理与生命系统：3.9%
- 生命分子、细胞与遗传：3.4%

讲述句：

> 14 类 taxonomy 把 ready 资产拆成几何、力学、电路三大主轴，并保留跨学科覆盖。

### 第 8 页：Review 原因诊断

标题：

> Review 原因：不只是视觉问题

图形：

- alignment / metadata consistency：32.1%
- other：28.7%
- answer / target solvability：16.4%
- visual grounding / image quality：13.3%
- rewrite / structure / options：9.5%

讲述句：

> review 原因是混合信号，因此 release policy 必须细分风险类型。

## 4. 给 Gemini 的总提示词

```text
你现在要直接生成一份组会 PPT。

请严格只使用我上传的文档作为事实来源，不要补充任何没有出现的数据、比例、结论或数据集名。

最重要的口径规则：
- 全局 ready 资产 = 29,966 candidates / 21,555 pass / 14 taxonomy classes / 21 datasets / 6 domains
- 5 月 7 日以来的生产子集 = 47 runs / 12,114 processed / 88,169 requests / 19,113 final ready
- 这两层数字不能写到同一张总览卡里

PPT 主题：
Pipeline1 / outputs / review release / ready pass 数据生产与分析

风格要求：
- 参考我上传的 PPT 模板风格总结
- 白底
- 深绿色 #005825 为主强调色
- 学术组会风格
- 简洁、克制、扁平化
- 每页只讲一个核心结论
- 不要卡通人物，不要 3D，不要大面积渐变，不要科技大屏风

内容要求：
1. 先根据上传文档生成 8 页以内大纲。
2. 每页只放一个主图或一个主流程图。
3. 第 1 页写全局 ready 资产，第 2 页写 ready pass 数据资产结构，第 3-5 页写生产子集，第 6-7 页写全局分布和 taxonomy，第 8 页写 review 原因。
4. 每页只使用文档中明确给出的数字。
5. 不要把 CSV 表格整页铺满。
6. 第 2 页必须列出 6 个领域下的 21 个数据集，并嵌入真实统计图；页面上不要出现 CSV 文件名、目录名或内部字段名。
7. 第 3 页的流程图必须采用“节点 + 上下交错对话框”的结构，每个对话框只放一句短说明和一个数字。
8. 如果信息不足，请先停下来问我，不要自己猜。

必须出现的事实：
- 全局 ready = 29,966 candidates
- 全局 ready pass = 21,555
- 生产子集 processed samples = 12,114
- 生产子集 requests = 88,169
- 生产子集 final ready = 19,113
- review rate = 39.5%
- 数学 = 10,084 / 14,185
- 物理 = 4,573 / 6,981
```

## 5. 如果 Gemini 还是乱

把流程改成两步：

1. 先让它只输出 PPT 目录和每页一句话结论。
2. 再让它按页生成，不要一次性全包生成。

这样通常比“直接生成完整 PPT”稳很多。
