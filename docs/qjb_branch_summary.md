# qjb 分支成果总结

## 一句话总结

`qjb` 分支完成了一轮以 **rewrite 流程收敛、pipeline 模块化拆分、运行稳定性增强、实验与文档沉淀** 为核心的工程化推进。它的主要价值不在于单次 benchmark 数字的即时跃升，而在于为后续迁移、合并、调试和持续迭代显著降低了复杂度与成本。

---

## 1. rewrite 流程持续向 `ler` 对齐

`qjb` 分支的一条主线，是把 rewrite 流程从分支特化实现逐步收敛到更接近 `ler` 的结构与接口约定，相关提交包括：

- `603e9e0` align rewrite flow with ler behavior
- `ce5985b` move rewrite agent closer to ler structure
- `4c507c3` separate rewrite variant normalization layer
- `90c9a8d` thin rewrite fallback and keep ler-shaped return path
- `69dacfc` reduce qjb-specific rewrite control flow
- `8c3aa6d` match ler rewrite signature

这部分工作的意义在于：

- 降低 qjb 分支自身的特化程度
- 为后续向 `ler` 迁移或合并铺路
- 减少 rewrite 逻辑继续分叉、继续长歪的风险
- 让返回形状、控制流和兼容层更清晰可控

这是一类典型的“结构收敛”工作，短期不一定直接转化为分数提升，但对后续维护和演进非常关键。

---

## 2. 显式梳理 normalization 临时层，避免补丁继续堆进 agent

围绕 rewrite 过程中出现的 normalization 兼容逻辑，`qjb` 分支做了明显的层次整理：

- `687467d` introduce base structured agent for rewrite
- `077202c` mark rewrite variant normalization as temporary
- `bdd6355` move temporary rewrite normalization out of agent
- `b9d0f76` lift list-field normalization into base agent
- `abc453b` Add qjb normalization agent plan and MSEarth probe config

这表明分支不只是“让它先跑起来”，而是在主动：

- 标注哪些兼容层是临时方案
- 把不应长期留在 agent 内部的逻辑外移
- 提升基础层复用性
- 为后续删除过渡层、回归更干净结构留下空间

这类工作的重要价值在于防止临时代码固化为永久债务。

---

## 3. 将 pipeline 从大流程推进为 staged / modular 结构

`qjb` 分支完成了一轮比较明确的 pipeline 模块化拆分，典型结果包括：

- `pipeline_collection.py`
- `pipeline_extraction.py`
- `pipeline_normalization.py`
- `pipeline_rewrite.py`
- `pipeline_reporting.py`
- `pipeline_setup.py`
- `pipeline_types.py`
- `pipeline_utils.py`
- `pipeline_clients.py`
- `pipeline_logging.py`

相关提交包括：

- `d73d6dc` refactor pipeline into staged modules and add agent-only extraction mode
- `3a60ed9` add staged pipeline design plan document
- `fd1193b` add initial pipeline refactor architecture docs
- `868922c` docs: add pipeline architecture and module contracts

配套文档也同步补齐了架构、模块、契约与中间产物说明。

这部分工作的直接收益是：

- 各阶段职责更明确
- 局部修改更容易控制影响面
- 更利于测试与调试
- 更利于后续多人协作与分支合并
- 文档和代码之间开始形成稳定映射关系

这是很典型的“把项目从能跑推进到能维护”的成果。

---

## 4. 运行稳定性与可观测性显著增强

`qjb` 分支投入了不少工作在运行稳定性、错误定位和实验可追踪性上，相关提交包括：

- `3083129` feat: retry transient chat_json API failures
- `667d3d4` debug: include retry attempt counts in chat_json errors
- `51ce6b1` debug: surface chat_json failure details in run log
- `490ee4b` feat: add run log for rewrite debugging
- `5c650c6` feat: add run logs and verify rewrite llm recovery
- `62a3a92` fix: handle remote disconnects in chat client
- `49de646` fix: expand env api keys and fail fast on placeholders
- `6850ea7` fix: persist llm_used in rewrite reports

这些改动共同完成了几件很重要的事：

- 对瞬时 API 故障增加恢复能力
- 让失败原因从“黑箱”变成“可定位”
- 保留更完整的 run log 和重试信息
- 在报告中保留模型使用信息，便于回溯
- 提前暴露环境变量配置问题，减少假跑与空跑

这类成果常常不会直接体现在 benchmark 表格里，但它们决定了实验结果是否可靠、问题是否可复现、系统是否可维护。

---

## 5. 修复了多项真实数据接入与解析问题

`qjb` 分支并不只是做结构清理，也解决了多处真实影响结果的数据问题：

- `07b3f01` fix: resolve relative HF image paths in connector
- `9cb20f0` fix: parse JSON-encoded image path lists
- `82bad4d` fix: load Geometry3K samples from official zip splits
- `a5e9a6d` refactor collection scoring and fix geometry3k ingest ranking
- `621f5d9` fix: tighten split-open detection for math-style answers
- `1597c36` fix: add weak visual hints for implicit function-graph questions

这部分工作的价值很直接：

- 避免数据入口错误污染后续分析
- 提升样本解析和图像路径处理的健壮性
- 修复特定 benchmark / dataset 上的错误行为
- 为后续对比实验提供更可信的输入基础

如果没有这些工作，后面的很多 benchmark 结论都可能建立在有问题的数据流之上。

---

## 6. 积累了大量实验资产与分析文档

`qjb` 分支不是只改代码，也留下了大量实验与分析沉淀，包括：

- candidate 200 long-run artifacts / summaries / analysis
- 200-sample rerun findings
- SCEMQA weak visual hint improvement notes
- MM-Math review example and smoke findings
- rewrite LLM recovery verification
- MSEarth probe config 与后续输出
- 多个数据集的 records / samples / summary / outputs

相关提交包括：

- `cdc5e7f` docs: summarize candidate 200 long-run analysis
- `825d20d` data: add candidate 200 long-run summaries and sample records
- `b3a3065` data: add candidate 200 long-run artifacts
- `46b1dd9` docs: add runtime summary for candidate 200 long run
- `2062bd9` docs: record rewrite llm recovery verification
- `486ff22` docs: record 2026-03-28 candidate_200 rerun analysis
- `248d3b7` docs: record SCEMQA weak visual hint improvement
- `a798b2b` docs: record MM-Math review example and smoke findings
- `3887e42` docs: summarize 200-sample rerun findings and rewrite issues

这意味着 `qjb` 已经不仅是一个代码分支，也是一段带有上下文、证据和结论的实验历史。它为后续决策提供了重要依据，避免重复试错。

---

## 7. 文档体系同步推进，降低未来理解与交接成本

`qjb` 分支在重构期间并没有放弃文档，反而持续把结构变化、迁移状态和问题背景写下来：

- `4a8d47e` docs: rewrite README around staged pipeline and current issues
- `8b0577d` docs: append prompt references to structure docs
- `056bfa2` docs: mark cleaning stage as agent-heavy in structure docs
- `f13ae8e` docs: align rewrite policy and README status notes
- `abac353` chore: sync pipeline refactor and docs reorg (2026-03-29)

这类工作避免了常见的“代码变了、文档全废”的问题，使分支成果更容易被吸收和复用。

---

## 总结评价

从仓库历史看，`qjb` 分支的主要成果不是单点功能，而是一次高密度的结构性推进：

1. rewrite 流程向 `ler` 收敛
2. normalization 兼容层显式化并开始外移
3. pipeline 完成 staged / modular 拆分
4. 日志、重试、恢复、报错与追踪能力增强
5. 多项数据接入与解析问题得到修复
6. benchmark 与 rerun 结果形成系统化沉淀
7. 文档与代码同步演化，降低未来迁移和交接成本

如果只用“分数有没有立刻大涨”来评价，`qjb` 很容易被低估；但如果从工程演进角度看，它显然已经产出了大量可复用、可迁移、可沉淀的资产。

更准确地说，`qjb` 的价值在于：

> 它把项目从“能继续堆功能”往“能持续演化、能定位问题、能与其他分支收敛”推进了一大步。
