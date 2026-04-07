# ler-reasoning-chain-msearth 分支详细汇报（2026-04-02）

## 一、分支整体定位

这个分支的工作主线，不是单点修一个 bug，也不是只补几份实验输出，而是围绕 **ler 路线下的 reasoning-chain / benchmark 批跑落地** 做了一轮比较完整的推进。

从提交和产物看，这条分支主要完成了四类工作：

1. **打通 MSEarth open-ended 的 reasoning_chain 透传链路**
2. **围绕多个 benchmark 数据集做批跑、补跑、合并与结果沉淀**
3. **对运行中出现的 fallback / 失败批次 / 结果口径问题做修复和替换**
4. **把实验结果沉淀成可复核的文档、summary 和 merged outputs**

如果压成一句话，这个分支的价值可以概括为：

> 它把 ler 路线从“能跑一些样本”进一步推进到“能在多个数据集上批量跑、定位异常、补跑替换、形成正式汇总口径，并对关键数据集做分析说明”的状态。

---

## 二、按时间线看，这个分支主要做了什么

### 1. 前置阶段：补齐 benchmarkallinone 的运行与试跑基础
分支前段先做了一些更偏运行侧的工作，包括：

- 更新 `benchmarkallinone` 相关文件
- 创建一键运行脚本
- 做“每个数据集 20 个样本测试”
- 补充 plans、outputs 等运行产物

对应提交包括：

- `10e095a` 创建一键运行脚本
- `d57f315` 每个数据集 20 个样本测试
- `b556c68` 更新 benchmarkallinone scripts, plans, and outputs

这部分的意义在于：它先把“多数据集统一试跑”和“后续大规模批跑”的操作基础打稳了，后面的 MSEarth / EEE-Bench / MathVision / PhysReason 工作，都是在这个基础上展开的。

---

### 2. MSEarth：打通 reasoning_chain 并确认 supporting context 问题
MSEarth 是这条分支最核心的一条主线。

#### 2.1 接入 reasoning_chain 透传
关键提交：

- `15d19f3` Add reasoning chain passthrough for MSEarth open-ended

从提交统计看，这一步主要改了：

- `configs/msearth_open_ended_validation_5.yaml`
- `src/benchmarkallinone/pipeline.py`

这说明这不是单纯补文档，而是把 **MSEarth open-ended 的 reasoning_chain 真正接入了 pipeline**，使其能够从输入一路透传到产物中。

#### 2.2 做分析与标注文档
关键提交：

- `826e9a2` Add MSEarth analysis and annotation docs
- `c809df2` Add MSEarth Open Ended summary notes
- `684f817` Move MSEarth summary into docs

对应文档包括：

- [MSEarth_Open_Ended_汇总说明.md](docs/MSEarth_Open_Ended_汇总说明.md)

这部分不是简单地记录“跑了多少条”，而是明确分析了 MSEarth 数据本身的结构特点：

- 样本不仅依赖图像，还常常依赖 **caption**
- 有些 gold answer 的依据来自 **caption + image + reasoning_chain 联合信息**
- 当前链路里，题面变短是现象，但真正的问题是 **supporting context 可能被丢失**

文档中最关键的判断有两点：

1. **caption 的消失主要发生在 normalization 阶段，而不是 rewrite 阶段**
2. **reasoning_chain 已经透传，但下游标注/QA/发布是否真正消费，还需要继续确认**

这说明这条分支不只是“做实验”，而是已经开始对数据质量与链路语义完整性做系统性判断。

#### 2.3 跑出 MSEarth 样本和批次结果
关键提交：

- `27ab442` Add MSEarth Open Ended 20-sample lerchain run outputs
- `4cf0d62` Add lerchain MSEarth Open Ended run_749a368c3fdbf798 outputs

从提交统计看，这里加入了：

- 配置文件
- 样本级 JSON
- records JSONL
- 图片与 crop 产物
- summary

也就是说，这不是只验证代码可运行，而是完整产出了 **可审计的 benchmark run artifact**。

#### 2.4 整理输出位置与目录
关键提交：

- `62e385d` Move MSEarth outputs into outputs and drop trash folder

这一步的意义不小。它说明你不是把 MSEarth 结果临时堆在分支里，而是主动做了一次**产物归档与口径整理**：

- 把最终结果统一放到 `outputs/`
- 清理中间 trash / 临时文档位置
- 让 MSEarth 这条线从“临时验证”转成“可保留的正式产物”

#### 2.5 合并 MSEarth `0000:0120` 结果
关键提交：

- `30f3a83` data: merge MSEarth open-ended 0000-0120 outputs

对应说明文档：

- [MSEarth_open_ended_0000_0120_合并说明.md](docs/MSEarth_open_ended_0000_0120_合并说明.md)

这一步是整个 MSEarth 工作从“样本试跑”走向“正式汇总”的关键节点。

文档里已经明确给出：

- merged 输出目录
- 各 batch 的来源与统计
- 目录名 overlap 但 problem_id 无重复的判断
- `from20_to300` 总目录当前不能直接作为正式 merge 来源

最终汇总结果为：

- 合并样本数：`180`
- `pass = 84`
- `review = 84`
- `reject = 12`

这说明你在 MSEarth 这条线上完成的不只是功能接入，而是：

> **从 reasoning_chain 接入 → 样本跑通 → supporting context 风险分析 → 批量结果合并 → 正式 summary 口径沉淀** 的完整闭环。

---

### 3. EEE-Bench：做 rewrite 对比与 300 条合并
这条分支里还有一条比较清晰的 EEE-Bench 线。

关键提交：

- `b15861a` Add EEE-Bench rewrite comparison notes
- `f9d8fe5` Add EEE-Bench head10 evaluation outputs
- `bf53eb9` data: merge EEE-Bench 0000-0300 outputs

从文档和当前目录看，对应产物包括：

- [EEE-Bench_前10题改写前后对照.md](docs/EEE-Bench_前10题改写前后对照.md)
- [EEE-Bench_0000_0300_合并说明.md](docs/EEE-Bench_0000_0300_合并说明.md)
- [EEE-Bench_visual_structure_records_口径不一致问题记录.md](docs/EEE-Bench_visual_structure_records_口径不一致问题记录.md)

这说明你在 EEE-Bench 上做的不是“跑一下看看”，而是至少做了三层工作：

1. **小样本对照验证**：先看改写前后长什么样
2. **批量产物汇总**：推进到 `0:300` 规模
3. **口径问题记录**：开始关注 records 层面的字段一致性问题

另外当前未跟踪文件也表明，这条线后面还在继续往前推；不过当时用于验证 / 批跑的几份 EEE-Bench 专用 YAML 现在已经按仓库清理规则删除，只保留标准主配置与脚本：

- `configs/eee_bench_10_debug.yaml`（已删除，旧验证配置）
- `configs/eee_bench_20_batch.yaml`（已删除，旧批跑配置）
- `configs/eee_bench_300.yaml`（已删除，旧汇总配置）
- [scripts/run_eee_bench_20_batches.sh](scripts/run_eee_bench_20_batches.sh)
- 当前保留标准配置：`configs/eee_bench.yaml`

所以 EEE-Bench 这部分更准确的说法是：

> 你在这条分支里把 EEE-Bench 从“小样本对照验证”推进到了“可批量执行并形成 300 条 merged 输出”的状态，同时已经开始记录字段口径层面的真实问题。

---

### 4. MathVision：从 10 条验证走到 300 条合并修复
MathVision 是这条分支里最完整、最有“修问题”意味的一条线之一。

关键提交：

- `ee10322` Add MathVision 300 merged summary
- `f75a4da` Move MathVision 300 merged summary into outputs
- `b2aafae` Add MathVision 10 validation summary

对应文档：

- [MathVision_10_验证总结.md](docs/MathVision_10_验证总结.md)
- [MathVision_300_汇总.md](docs/MathVision_300_汇总.md)

#### 4.1 先做 10 条验证
10 条验证的价值不只是“证明能跑”，而是帮你识别出链路里的一个关键现象：

- 大部分样本正常走了 LLM normalization
- 少数样本 `llm_used: false`
- 回退到 rule-based normalization 后，`<image1>` 会残留在改写结果里

这一步非常关键，因为它把问题从“结果看上去不太对”收敛成了一个更明确的工程判断：

> **不是整个 MathVision 配置失效，而是部分样本在 normalization 阶段没有拿到可用 LLM 结构化结果，因此回退到了 fallback 路径。**

#### 4.2 再做 300 条汇总与异常 batch 替换
在 300 条汇总里，你已经把这个问题进一步推进成了批量修复。

文档里明确写到：

- 总共 15 个 batch
- 其中 4 个异常 batch 用 rerun 替换
- 原本有 `51` 条 `llm_used: false`
- rerun 之后这 `51` 条已经全部清零

最终结果：

- 总样本数：`300`
- `pass = 178`
- `review = 120`
- `reject = 2`

这说明在 MathVision 上，你不是只做“统计汇总”，而是真正做了：

1. 问题发现（fallback / llm_used false）
2. 范围定位（哪些 batch、多少条样本）
3. rerun 修复
4. merged 结果替换
5. 最终文档化沉淀

所以 MathVision 这条线非常适合在汇报里写成：

> 通过 10 条验证先识别 normalization fallback 问题，再在 300 条批跑中对异常 batch 进行 rerun 替换，最终把 51 条 `llm_used: false` 清零，并形成正式 merged 结果与结论文档。

---

### 5. PhysReason：识别 502/fallback 风险并做异常区间替换
PhysReason 也是很完整的一条线。

关键提交：

- `750f5d7` add merged PhysReason 0:300 outputs
- `0535f0d` add PhysReason 0:300 merge summary doc
- `5e0d4ee` add full PhysReason merged package and validation report

对应文档：

- [PhysReason_0000_0300_合并说明.md](docs/PhysReason_0000_0300_合并说明.md)

这条线最重要的价值在于：你把“批跑异常”明确界定成了**可定位、可替换、可给出口径**的问题，而不是仅仅说“有些 batch 不太稳定”。

文档中已经清楚记录：

- 主跑覆盖 `0:300`
- `0180:0260` 历史批次出现 `HTTP 502 Bad Gateway`
- 这些批次伴随 `successful_request_count = 0`、`fallback 风险`
- 最终不采用历史异常批次，而是采用 rerun 成功结果替换

最终 merged 结果摘要为：

- `processed_samples = 300`
- `pass = 118`
- `review = 182`
- `reject = 0`

所以 PhysReason 这条线可以总结为：

> 你不仅完成了 `0:300` 的 PhysReason 批跑，还把历史失败区间识别出来，明确排除了存在 502/fallback 风险的旧批次，并用 rerun 成功结果形成正式 merged 口径。

---

## 三、这条分支体现出的几个共性特征

从 MSEarth、EEE-Bench、MathVision、PhysReason 这几条线一起看，这个分支有几个很清楚的共性。

### 1. 不只是“跑实验”，而是在做结果工程化
你做的不是单纯多跑几轮 benchmark，而是把实验结果逐步变成：

- 可追溯的 run outputs
- 可检查的 records / sample 级产物
- 可对外描述的 summary 文档
- 可统一引用的 merged 目录

这意味着分支价值不只在实验本身，还在于把实验**组织成可复核资产**。

### 2. 不回避异常，而是显式处理异常批次
MathVision 和 PhysReason 都体现出一个共同点：

- 不把异常批次和正常批次混在一起直接汇总
- 先识别异常
- 再 rerun
- 最后替换并形成 merged 口径

这比只给最终数字更重要，因为它说明这条分支开始建立一套更可靠的“结果可信性”处理方式。

### 3. 已经开始关注结果背后的语义完整性问题
MSEarth 那条线尤其明显。

你关心的不只是：

- 题有没有改写成功
- summary 里 pass/review/reject 各有多少

你还在看：

- supporting context 有没有丢
- caption 在哪一层消失
- reasoning_chain 虽然透传了，但下游是否真正消费

这表明你已经从“跑通 benchmark”开始转向“判断链路输出是否真正可用于后续标注/QA/发布”。

### 4. 分支里沉淀了大量文档，不只是结果文件
这个分支非常明显地做了文档化沉淀，包括：

- 汇总说明
- merge 说明
- 10 条验证总结
- 前后对照说明
- 口径问题记录
- 分支对比报告

这意味着它已经不再是“只有代码和输出”的分支，而是一段**有判断、有解释、有证据链的工作记录**。

---

## 四、如果单独评价这个分支，它的核心价值是什么

如果不跟 `qjb` 放在一起，只单看这条 `ler-reasoning-chain-msearth` 分支，我会这样评价它：

### 1. 它把 ler 路线向真实 benchmark 落地推进了一大步
这条分支做的不是算法层面的重新设计，而是把现有 ler 路线推进到多个真实数据集上，通过样本、批次、补跑、merge 和文档，把它变成一套更可执行的实验链路。

### 2. 它开始显式建立“正式结果口径”
这点在 MathVision / PhysReason / MSEarth merge 上都非常明显。

你不是简单把所有结果堆在仓库里，而是开始回答：

- 哪个 run 才是最终采用版本？
- 哪些 batch 不应该纳入正式 merge？
- rerun 结果是否足以替换历史异常结果？
- 哪个目录应该作为后续汇总、上传、复核时的统一口径？

这是非常典型的“把实验变成工程资产”的动作。

### 3. 它为后续大规模扩样提供了现实依据
通过 10 条验证、20 条试跑、180/300 条 merged 汇总，你已经积累出一些比较实际的经验：

- 哪些问题是 normalization fallback
- 哪些问题是 502 / API 级异常
- 哪些数据集 review 偏高的原因是什么
- 哪些批次可以直接纳入结果，哪些需要 rerun

所以这条分支不只是产出当前结果，也为后续继续扩样、继续跑更大规模数据提供了现实判断基础。

---

## 五、和 qjb / ler 分支对比报告合并后的总汇报

下面把当前分支工作，与已有的 [qjb_ler_branch_report_2026-04-02.md](docs/qjb_ler_branch_report_2026-04-02.md) 合并起来，形成一份更完整的总汇报。

### 5.1 两份工作的关注重点不一样
已有的 qjb vs ler 报告，核心在回答：

- `qjb` 分支做了什么工程化推进
- `qjb` 和 `ler` 在结构设计上的差异是什么
- 两边的样本输出在多大程度上相似

而当前这个分支的工作，核心在回答：

- `ler` 这条线在真实 benchmark 上推进到了什么程度
- reasoning_chain / merge / rerun / summary 这些结果工程化动作具体做到了哪里
- 多个数据集的正式口径和异常替换方案是什么

换句话说：

- **qjb_ler_branch_report** 更偏“架构梳理 + 分支关系分析”
- **当前分支汇报** 更偏“实验落地 + 结果工程化推进”

这两份内容是互补的，不是重复的。

### 5.2 如果把 qjb 和当前分支一起看，可以得到什么结论

#### 结论一：`qjb` 更偏结构工程化，当前分支更偏结果工程化
根据已有报告：

- `qjb` 的主线是 staged pipeline 拆分、rewrite 向 `ler` 收敛、稳定性增强、代码结构工程化

而当前分支体现出来的是：

- 围绕 ler 路线，把多个 benchmark 数据集真正跑起来
- 对异常结果做补跑替换
- 对 merged 目录和最终口径做明确沉淀
- 对关键数据集做 supporting context / fallback 风险分析

所以两边可以比较准确地概括成：

> `qjb` 更像是在做 **代码结构和 pipeline 组织方式的工程化推进**；当前这个 ler 分支更像是在做 **benchmark 结果、实验口径和数据产物的工程化推进**。

#### 结论二：两边不是对立，而是互补
已有报告已经指出：

- `ler` 更偏 agent-oriented / all-in-one
- `qjb` 更偏 pipeline-stage / 工程职责拆分

如果把当前分支纳入一起看，可以补充一句：

- 当前这个 `ler-reasoning-chain-msearth` 分支，则在 **ler 路线现有结构不大改动的前提下，把它推向了更真实、更大规模、更可复核的 benchmark 执行与汇总场景**。

也就是说：

- `qjb` 在回答“结构怎么拆更稳”
- 当前分支在回答“现有 ler 路线如何变成可交付的实验资产”

#### 结论三：样本层面对齐支持“主链能力接近”的判断
已有的 qjb vs ler 报告已经给出了一个比较稳的结论：

- 在 `cmm_math`、`mathvision`、`scemqa`、`geometry3k`、`physreason` 等数据集代表样本上，两边的改写结果和 expected answer 整体是一致的
- 差异主要在题面风格、格式细节、图像占位符保留方式，而不是核心答案

当前分支进一步补强了这个判断，因为你已经在 MathVision、PhysReason、MSEarth 等数据集上产出了更完整的 merged outputs 和总结文档。

这意味着：

> `qjb` 和 `ler` 的差异，更多体现在工程组织形态和一些表达风格上，而不是在 benchmark 主链结果上出现根本分叉。

### 5.3 合并后的总评价
如果把两份材料合成一段最终汇报，我会建议用下面这个总口径：

> 当前可以把 `qjb` 与 `ler-reasoning-chain-msearth` 两条线理解为两种互补推进：
> 
> - `qjb` 侧重把清洗链路按 staged pipeline 做结构化拆分，并持续把 rewrite / normalization 等核心流程向 `ler` 路线收敛；
> - `ler-reasoning-chain-msearth` 分支则侧重把现有 ler 路线落到真实 benchmark 上，完成 MSEarth reasoning_chain 接入、EEE-Bench / MathVision / PhysReason 等多数据集批跑、异常 rerun 替换、merged 输出与总结文档沉淀。
> 
> 从样本对齐结果看，两边在代表性数据集上的核心改写结果与 expected answer 总体一致，差异主要体现在题面风格、格式清理程度和图像占位标记保留方式，而不是核心答案本身。
> 
> 因此，这两条线不是互相竞争的两套完全不同方案，而更像是：`qjb` 在做结构工程化，当前 ler 分支在做结果工程化；两者共同把整条 benchmark 清洗链路往更稳定、更可复核、更接近正式交付的方向推进了一步。

---

## 六、最适合对外汇报的简化版结论

如果你后面要给导师、同学或者组里做口头汇报，最短可以压成下面这版：

> 这条分支主要做了两类事：
> 
> 1. 以 MSEarth 为核心，把 ler 路线下的 reasoning_chain 链路接通，并分析了 caption / supporting context 在 normalization 中丢失的问题；
> 2. 围绕 EEE-Bench、MathVision、PhysReason 等数据集做了批跑、补跑、merge 和总结，开始形成一套更明确的正式结果口径。
> 
> 如果和 qjb 分支一起看，可以把两边理解为互补推进：qjb 更偏结构工程化，当前分支更偏结果工程化；样本层面对齐结果也说明两边主链能力总体一致，差异主要是工程组织和题面风格，而不是核心答案。
