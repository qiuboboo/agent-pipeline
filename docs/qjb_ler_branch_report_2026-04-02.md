# qjb 与 ler 分支梳理（2026-04-02）

当前我对分支情况做了一个比较系统的梳理，重点看了 `qjb` 分支本身做了什么、它和 `ler` 分支的关系，以及两边在样本输出上的对应情况。

## 一、`qjb` 分支的核心工作是什么

`qjb` 分支的核心不只是“改了几处逻辑”或者“多跑了几轮实验”，而是做了一轮比较完整的工程化推进。它的主线主要有几部分：

### 1. rewrite 流程持续向 `ler` 收敛
这条分支有一条很明显的主线，就是把 rewrite 流程逐步往 `ler` 的实现方式靠拢，包括：
- 返回结构对齐
- 控制流收敛
- rewrite agent 的接口形状靠近 `ler`
- 减少 qjb 自己特有的分支逻辑

这部分的意义不在于立刻带来 benchmark 分数变化，而在于降低后续继续分叉、继续长歪的风险，也给以后向 `ler` 迁移或合并创造条件。

### 2. normalization 相关兼容层被显式整理
围绕 rewrite 过程中引入的一些 normalization 兼容逻辑，`qjb` 并没有简单地继续往 agent 内堆补丁，而是做了层次整理：
- 标出哪些是临时兼容层
- 把不应长期留在 agent 内部的逻辑往外移
- 提高基础层复用性
- 给未来删除过渡层留空间

### 3. pipeline 完成了 staged / modular 拆分
这是 `qjb` 很重要的一点。它不再把逻辑继续堆在一个 all-in-one 文件里，而是拆成了多个模块，比如：
- `pipeline_collection.py`
- `pipeline_extraction.py`
- `pipeline_normalization.py`
- `pipeline_cleaning.py`
- `pipeline_rewrite.py`
- `pipeline_reporting.py`
- `pipeline_setup.py`
- `pipeline_types.py`
- `pipeline_utils.py`
- `pipeline_clients.py`
- `pipeline_logging.py`

这说明它已经不是“在原来代码上修修补补”，而是在把工程结构往更稳定的形态推进。

### 4. 运行稳定性和可观测性增强
`qjb` 还做了很多跟可运行性直接相关的事情，包括：
- 瞬时 API 故障重试
- chat_json 失败时记录更多上下文
- run log 补充
- rewrite 调试信息补充
- remote disconnect 处理
- 环境变量检查与 fail-fast
- 在 rewrite report 里保留模型使用信息

### 5. 数据接入和解析问题修复
这条分支还修了不少真实数据问题，比如：
- 相对图像路径处理
- JSON 编码图片路径列表解析
- Geometry3K 数据加载方式
- 某些答案解析和 ranking 逻辑
- 某些弱视觉提示和函数图题型处理

### 6. 实验和文档沉淀
`qjb` 不是只有代码，还留下了大量：
- run summaries
- rerun analysis
- benchmark 输出
- 文档说明
- config
- 中间 records / samples / summaries

所以它已经不仅是“一个代码分支”，而是一段带有上下文、证据和分析结论的工程历史。

## 二、`qjb` 的拆解思路是什么

这个点很重要，建议在汇报里明确说出来。

`qjb` 的拆法**不是直接按 agent class 去拆**，而是采用了 **staged pipeline** 的思路，也就是按流程阶段和工程职责来拆。

可以把它理解成几层大的 stage：

1. **多源接入 / collection**
2. **字段抽取 / extraction**
3. **规范化 / normalization**
4. **清洗 / rewrite / gate**
5. **汇总输出 / reporting**
6. **公共支撑层**：setup / types / utils / clients / logging

也就是说，`qjb` 更像是在回答这个问题：

> 整条 pipeline 的每一个阶段分别做什么，怎么把它们拆开，让代码更容易维护和演进？

而不是去强调：

> 每一个 agent 各自叫什么名字？

## 三、为什么这种 staged pipeline 拆法有价值

这个拆法的价值，重点不在“结构更整齐”，而在于后续工程推进会更省力。

### 1. 更容易定位问题
出问题时更容易判断到底是：
- collection 出错
- extraction 出错
- normalization 出错
- rewrite 出错
- reporting 出错

### 2. 更容易做局部修改
如果只改某一段，比如：
- 字段抽取
- normalization 规则
- rewrite 逻辑
- report 输出

就可以局部动，不容易影响整条链路。

### 3. 更容易单段测试
拆开以后可以单独测：
- 一条样本的 extraction 结果
- 一组字段的 normalization
- 某个 rewrite 输入输出形状

### 4. 更容易复用公共能力
像：
- `types`
- `utils`
- `clients`
- `logging`
- `setup`

这些抽出来以后，整个 pipeline 共享，避免重复实现。

### 5. 更利于迁移和收敛
因为 `qjb` 本身就承担了一部分“向 `ler` 收敛”的任务。按 stage 拆以后，可以一段一段对齐，而不是一次性整体硬迁移。

### 6. 更利于多人协作
不同人可以分别看：
- collection
- rewrite
- normalization
- reporting

边界更清楚，冲突也更少。

### 7. 更利于文档和代码一一对应
现在这种拆法很适合写成：
- collection stage 做什么
- extraction stage 做什么
- normalization stage 做什么

文档和代码模块之间更容易形成稳定映射。

## 四、`qjb` 和 `ler` 的关系怎么理解

从设计思路上看：

- **`ler`** 更偏 **agent-oriented / all-in-one**
- **`qjb`** 更偏 **pipeline-stage / 工程职责拆分**

`ler` 的代码里，主要 agent 基本都挂在同一个 `BaseStructuredAgent` 下面，比如：
- `SourceIntakeAgent`
- `AssetRegistryAgent`
- `PotentialScorerAgent`
- `CandidateRegistrarAgent`
- `NormalizationAgent`
- `SampleUnderstandingAgent`
- `RewriteAgent`
- `DecisionAgent`

再由 `AgenticCleaningOrchestrator` 串起来，外层是 `MultiDatasetCleaningPipeline`。

`qjb` 并不是否掉 `ler` 的思路，而是把相近的主链路能力翻译成更偏工程模块化的组织方式。

所以更准确的说法是：

> `ler` 像一套更显式的 agent 化设计，`qjb` 像把这套主链按 pipeline stages 重新组织成更利于维护、测试、调试和后续迁移的工程结构。

## 五、两边的相似度怎么判断

### 1. 代码文本相似度不高
如果直接拿代码文本比，`qjb` 和 `ler` 的 all-in-one 文件相似度不算高，说明它不是简单拷贝。

### 2. 功能相似度比较高
但如果按流程节点和功能职责来看，两边的核心链路其实是比较接近的。也就是说，`qjb` 更像是在参考 `ler` 主链路的基础上，做了模块化拆分和工程化重组，而不是另起一套完全不同的东西。

## 六、样本层面的对比情况

为了避免只停留在结构层面，我还按**最新版本输出**对两个分支做了样本对比。

### 第一类：可以直接按共同样本对齐的
目前纳入了三个数据集：
- `cmm_math`
- `mathvision`
- `scemqa`

### 第二类：`problem_id` 不同，但内容能对齐的
又补充看了两个数据集：
- `geometry3k`
- `physreason`

这里不是简单说“两边结果一样”，而是具体看了题面、改写方式和答案口径。

#### 1. `cmm_math`
同一题上，两边 expected answer 一致，但题面风格有细微差别。

- `ler` 的改写更像开放式提问：
  - “已知关于 x 的不等式 ... 的解集为 [-2,1]，求关于 x 的不等式 ... 的解集。”
- `qjb` 的改写更像保留填空题形式：
  - “已知关于 x 的不等式 ... 的解集为 [-2,1]，则关于 x 的不等式 ... 的解集为______。”
- 两边答案都是：
  - `[-1/2, 1]`

这个例子说明：
> 两边核心结果一致，但 `ler` 更倾向于把题面改成标准开放问法，`qjb` 更倾向于保留原题型风格。

#### 2. `mathvision`
这类题上，两边语义和答案都一致，但是否保留图像占位有差别。

- 原题：
  - `Which number should be written in place of the question mark? <image1>`
- `ler` 改写：
  - `Which number should be written in place of the question mark?`
- `qjb` 改写：
  - `Which number should be written in place of the question mark? <image1>`
- 两边答案都是：
  - `60`

这个例子说明：
> 两边在改写结果上基本等价，差异主要是 `qjb` 更保留图像引用痕迹，`ler` 更偏向做纯净题面整理。

#### 3. `scemqa`
当前最新可直接对齐的样本上，两边几乎完全一致。

- 原题：
  - `At which value of x is f continuous but not differentiable?`
- `ler` 改写：
  - 题面保持一致
- `qjb` 改写：
  - 题面保持一致
- 两边答案都是：
  - `3`

这个例子说明：
> 至少在当前这类样本上，两边不仅答案一致，连改写策略也基本一致。

#### 4. `geometry3k`
这个数据集的关键点是：虽然 `problem_id` 不同，但内容完全能对上。

- `ler` 题面：
  - `In ⊙X, AB = 30, CD = 30, and m(arc CZ) = 40. Find m(arc AB).`
- `qjb` 题面：
  - 同一题，只是 LaTeX spacing 稍有区别
- `ler` 改写：
  - 对公式做了更紧凑的书写整理
- `qjb` 改写：
  - 基本保持原题样式
- 两边答案都是：
  - `80`

这个例子说明：
> `geometry3k` 这边两条分支处理的是同一题，只是 ID 生成口径不同，改写差异主要是格式整理程度不同，不是语义差异。

#### 5. `physreason`
这个数据集也能找到题面高度一致、答案一致的样本，只是 `problem_id` 不同。

- 题目都是那道：
  - `An L-shaped skateboard A is initially at rest on a rough horizontal surface ...`
- 两边原题高度一致
- 两边改写也基本保持一致
- expected answer 都是同样的三段式结果：
  - `sqrt(v0^2 - 2μgs0)`
  - `1/4 m(v0^2 - 2μgs0)`
  - `2μ^2 m^2 g^2 / k`

这个例子说明：
> `physreason` 上也能确认两边在实质题目和结果上是一致的，只是最新输出里的 ID 没有直接对齐。

## 七、样本对比的总体结论

综合来看，可以比较稳地说：

> 当前已经纳入了 `cmm_math`、`mathvision`、`scemqa` 三个直接对齐样本，以及 `geometry3k`、`physreason` 两个内容对齐样本。  
> 从这 5 个数据集的代表性样本看，`ler` 和 `qjb` 的改写结果与预期答案整体保持一致；差异不是出在核心答案上，而主要体现在题面风格、格式细节、以及图像占位标记保留方式上。

## 八、整体评价

如果把这次梳理压成一句总结，我会这样说：

> `qjb` 分支的价值，不只是做了几处功能修改，而是完成了一轮以 **staged pipeline 拆解、rewrite 向 `ler` 收敛、运行稳定性增强、以及实验/文档沉淀** 为核心的工程化推进。  
> 它和 `ler` 的关系，不是对立的两套方案，而更像是：`ler` 提供了更显式的 agent 化设计参考，`qjb` 则在保留相近主链路能力的前提下，把这套思路翻译成更适合维护、测试、调试和后续迁移的 pipeline-stage 结构。
