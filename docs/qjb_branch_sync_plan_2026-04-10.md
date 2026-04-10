# qjb 分支三环境同步方案（2026-04-10）

> 目标：开一条明确的 `qjb` 分支工作线，把 **云服务器A / 云服务器B / 个人笔记本** 三个环境都同步到统一代码状态；同时把 `outputs/`、`ready/` 从版本控制职责里拿掉，改成 **各机本地持有、各机可自行从本地 outputs 构建 ready**。

---

## 1. 背景与当前诉求

当前状态：

- 有三个工作环境：
  1. **当前这台云服务器**
  2. **另一台云服务器**
  3. **个人笔记本**
- 三处都已经存在一定量的 `outputs` 记录
- **最新、最全的 outputs 在另一台服务器上**
- 后续希望：
  - 三台机器都切到统一的 `qjb` 分支
  - 三台机器都保留各自本地 `outputs/`
  - 仓库层面 **不再追踪 `outputs/` 和 `ready/`**
  - 任意一台机器在有本地 `outputs/` 的前提下，都能通过脚本重新生成本机 `ready/`

这实际上是在把仓库职责从：

> **代码 + 大量运行产物 + ready 结果**

收敛为：

> **代码 + 文档 + 脚本 + 构建规则**

而把运行产物职责下放为：

> **每台机器各自本地保存 outputs / ready，按规则自行重建**

---

## 2. 目标架构

## 2.1 代码仓库应负责什么

`qjb` 分支上，仓库应只负责：

- pipeline 代码
- `outputs -> ready` 构建脚本
- review/release 脚本
- 文档、规则、清单
- 必要的小型 manifest / plans / 配置

也就是：

- `src/`
- `scripts/`
- `docs/`
- `plans/`（若仍需要）
- 配置文件

## 2.2 仓库不应负责什么

`qjb` 分支上，仓库不应继续承担以下大体量产物的同步：

- `outputs/`
- `ready/`
- `ready_problem_exports/`
- 各类 `.log`
- 运行时缓存
- `__pycache__/`
- 临时验证输出 / smoke 输出 / rerun 中间产物

## 2.3 三机职责

### 云服务器B（另一台服务器）
**角色：主 outputs 源头 / 最全数据持有者**

- 保存最新最全的 `outputs/`
- 需要时可跑全量/较大规模流程
- 可作为其它机器补全 outputs 的来源

### 云服务器A（当前机器）
**角色：代码同步 + 可选部分 outputs 持有 + 可重建 ready**

- 跟上 `qjb` 分支最新代码
- 根据需要保留部分或全部 `outputs/`
- 本机可以从本机 `outputs/` 重建 `ready/`

### 个人笔记本
**角色：轻量开发 / 文档 / 局部调试 / 小规模重建**

- 同步 `qjb` 分支代码
- 本地保存自己需要的一部分 `outputs/`
- 可跑子集 ready 构建与验证
- 不要求长期保存最大最全 outputs

---

## 3. 核心原则

## 3.1 `outputs/` 和 `ready/` 改为“本地状态”，不是 Git 状态

这条是整个方案的根。

一旦采用 `qjb` 分支方案，推荐明确以下口径：

- `outputs/` 是 **机器本地运行产物**
- `ready/` 是 **机器本地派生产物**
- Git 不再承担它们的同步职责
- 跨机器同步时，优先同步：
  - **代码**（Git）
  - **需要共享的 outputs 数据**（rsync/手工同步/外部存储）
- `ready/` 默认本地重建，不靠 Git 分发

## 3.2 `ready` 必须可重建，而不是必须被同步

未来的稳定口径应是：

> 只要有正确的 `outputs/` 和正确版本的构建脚本，`ready/` 就应该可重建。

也就是说：

- `ready/` 是 cache-like / derived artifact
- 真正重要的是：
  1. 输入 `outputs/`
  2. 构建脚本版本
  3. 构建规则文档
  4. 必要的计划文件 / policy 文件

## 3.3 `outputs` 允许各机不一致，但必须“知道自己不一致”

三机不一定都持有同样完整的 outputs，这是现实约束。

可以接受：
- 云服务器B 最全
- 云服务器A 次之
- 笔记本最少

但必须让每台机器都能回答：

- 我现在有哪些 `outputs/`？
- 缺哪些？
- 本机当前能构建哪些 `ready`？
- 和主 outputs 源头相比差哪些数据集/哪些 range？

这正是 `build_sample_manifest.py` / `build_output_root_coverage.py` 后续应该承担的价值。

---

## 4. 对仓库策略的影响

## 4.1 `.gitignore` 必须升级

当前仓库 `.gitignore` 只忽略了：

```gitignore
outputs/repo_cache/
outputs/**/repo_cache/
outputs/**/.git/
__pycache__/
*.pyc
.DS_Store
```

这和新的 `qjb` 方案是冲突的。

因为当前规则下：
- `outputs/` 大部分内容仍会进入 Git 视野
- `ready/` 根本没被忽略
- 各类 log 也未系统忽略

### 新方案建议
在 `qjb` 分支落地时，把 `.gitignore` 口径改成更明确的一版，例如：

```gitignore
# local runtime artifacts
outputs/
ready/
ready_problem_exports/

# runtime cache / temp
__pycache__/
*.pyc
*.log
.DS_Store
```

如果后续还需要在仓库内保留少量“示例 outputs / 示例 ready”，那应该用：
- 单独的 `examples/`
- 或 `fixtures/`
- 而不是继续混在真实 `outputs/`、`ready/` 目录中

## 4.2 README / 文档口径也必须同步修改

当前 `README.md` 里仍然写着类似：
- 其余需要保留的 `outputs/` 运行结果应直接纳入 Git 跟踪

这和你现在的方向正相反。

所以 `qjb` 分支落地时，README 至少要更新这几条：

1. `outputs/` 不再纳入版本控制
2. `ready/` 不再纳入版本控制
3. `ready` 为本地派生产物，建议本地重建
4. 跨机器同步 outputs 用 Git 之外的方式
5. 用什么脚本检查本机 outputs 覆盖情况

---

## 5. 建议的工作模式

## 5.1 Git 只同步代码与规则

三台机器统一采用：

- 同一个远程仓库
- 同一个 `qjb` 分支
- Git 只同步：代码、脚本、文档、配置、计划文件

不再用 Git 做：
- outputs 分发
- ready 分发
- 运行日志分发

## 5.2 outputs 用“主源头 + 按需拉取”模式

建议把 **另一台服务器** 定义为：

> `outputs` 主源头

之后其他机器不再追求“自动完全一致”，而采用：

- 哪台机器要跑哪个数据集，先确认本机是否有对应 outputs
- 没有就从主源头按需同步
- 同步完后本机自己构建 ready

也就是：

> Git 同步代码，`rsync/scp/手动同步` 同步数据。

## 5.3 ready 一律本机生成

统一口径：

- 不跨机器同步 `ready/`
- 不把 `ready/` 提交到 Git
- 每台机器用统一脚本本地生成

这样有几个好处：

1. `ready/` 不再成为 Git 冲突源
2. 大量文件不会污染仓库状态
3. 只要脚本与 inputs 一致，结果就可复现
4. 每台机器都能独立验证本地环境是否可工作

---

## 6. 推荐落地步骤

下面是我建议的执行顺序。

## 阶段 A：先确定 policy，不马上删东西

### A1. 建立 `qjb` 分支工作说明
需要一份固定文档说明：
- `qjb` 分支的目标
- Git 只追踪什么
- outputs/ready 如何处理
- 三机的角色分工

### A2. 先不要立刻物理删除 `outputs/ready`
在 policy 明确前，不要直接大清理。

原因：
- 当前仓库里还有很多历史 ready / outputs 被脚本或文档引用
- 需要先完成脚本清点和路径改造
- 否则容易“先删后断”

---

## 阶段 B：让主链 ready 真正可重建

### B1. 明确唯一主链脚本
建议以：
- `scripts/build_ready_from_outputs_content_dedup.py`
作为未来唯一正式主链

### B2. review/release 继续独立
- `scripts/apply_manual_review_release.py`
必须保持在 post-ready 层

### B3. 清理对旧 ready 包的硬编码依赖
重点对象：
- `scripts/build_review_docs.py`

因为它还写死了多个旧 package 路径。

如果不先改这层，那么即使不追踪 `ready/`，机器切换后文档脚本也可能还在找旧包。

---

## 阶段 C：切换 Git 策略

### C1. 修改 `.gitignore`
目标是让这些目录默认不进入 Git：
- `outputs/`
- `ready/`
- `ready_problem_exports/`
- `*.log`

### C2. 清理 Git 索引中的历史追踪
如果仓库里这些目录之前已经被 Git 追踪，仅加 `.gitignore` 不够。

还需要一次 index 清理动作（仅取消追踪，不删本地文件）：

```bash
git rm -r --cached outputs ready ready_problem_exports
```

然后再提交一次 policy 变更。

> 注意：这一步是高影响动作，应该在 `qjb` 分支单独执行，不要直接在当前混乱工作树里贸然做。

### C3. 更新 README / docs
把旧的“outputs 应纳入 Git”口径一起改掉。

---

## 阶段 D：三机切分工落地

### D1. 另一台服务器
- 切到 `qjb`
- 保留最全 `outputs/`
- 作为主数据源

### D2. 当前云服务器
- 切到 `qjb`
- 保留自己常用的数据集 outputs
- 缺的按需从主服务器同步
- 本机生成本机 ready

### D3. 个人笔记本
- 切到 `qjb`
- 只保留工作所需子集 outputs
- 做文档、脚本、小规模验证
- 如需全量 ready，先拉对应 outputs 再生成

---

## 7. 我建议保留的“最小同步单元”

为了让三机都能从本地 outputs 重建 ready，至少需要同步这些东西：

### 代码层
- `src/`
- `scripts/`

### 规则 / 文档层
- `docs/`
- `plans/`（如果 ready 构建仍依赖其中某些选择文件）

### 配置层
- 配置文件
- requirements / 环境说明

### 不必通过 Git 同步的大文件层
- `outputs/`
- `ready/`
- `ready_problem_exports/`
- 各类运行日志

---

## 8. 建议新增的“本机状态检查”工作流

一旦 outputs/ready 不再追踪，仓库里最好固定保留两个检查动作：

## 8.1 检查本机 outputs 覆盖情况
建议依赖：
- `scripts/build_sample_manifest.py`
- `scripts/build_output_root_coverage.py`

目的：回答
- 本机有哪些 outputs
- 哪些 output root 未覆盖
- 哪些 ready package 由哪些 source run 构成

## 8.2 检查本机 ready 是否可重建
建议保留一个简单流程：

1. 清空某个 dataset 的本机 `ready/<dataset>/<package>`
2. 重新运行主链 build ready
3. 检查：
   - `selection_validation.ok`
   - `write_validation.ok`
   - `ready/summary.json`

未来如果要稳定化，建议补一个专门的“rebuild smoke test”脚本。

---

## 9. 风险点

## 9.1 旧脚本/文档仍引用历史 ready 包
这是当前最大风险之一。

例如：
- 文档生成脚本还硬编码旧 `run_merged_*` / `run_filtered_*`
- 某些说明文档默认把旧 ready 包视作正式口径

如果不先梳理这层，切到 `outputs/ready 不追踪` 后，会出现：
- 代码已同步
- 但本机没有旧 ready 包
- 文档脚本直接报错或产出错口径

## 9.2 三机 outputs 不一致导致结果不一致
这是允许的，但必须可见。

解决方式不是强行 Git 同步 outputs，而是：
- 明确主 outputs 源头
- 提供覆盖清单/manifest
- 本机构建前先知道自己缺什么

## 9.3 当前工作树已经很脏
从当前 git 状态看，仓库里存在大量：
- `ready/` 变更
- `outputs/` 未跟踪内容
- log 文件
- pyc / runtime 文件

这意味着：
- **不适合直接在当前状态上粗暴切策略**
- 应该先把 `qjb` 方案做成单独分支政策切换
- 再按步骤清理 Git 跟踪边界

---

## 10. 建议的最终口径

如果要把这套方案压缩成一句正式规则，我建议就是：

> `qjb` 分支只同步代码、脚本、文档和构建规则；`outputs/` 与 `ready/` 一律视为机器本地数据，不纳入版本控制。三台机器各自保留本地 outputs，并使用统一脚本在本机重建 ready；另一台服务器作为最新最全 outputs 的主源头，其他机器按需同步数据而不是通过 Git 传输运行产物。

---

## 11. 我建议的下一步动作

按优先级，我建议后续这样做：

1. **先出一版 `qjb` 分支 policy 变更清单**
   - 哪些文件要改
   - `.gitignore` 怎么改
   - README 怎么改
   - 哪些脚本会受影响

2. **再做一版“切换步骤 runbook”**
   - 三台机器分别怎么切到 `qjb`
   - 哪台保留全量 outputs
   - 其他机器怎么拉子集 outputs

3. **最后才做真实代码改动**
   - 改 `.gitignore`
   - 改 README
   - 清理 Git 索引里的 outputs/ready
   - 修文档生成脚本对旧 ready 包的依赖

---

## 12. 本文与现有盘点文档的关系

这份文档是建立在以下盘点基础上的：
- `docs/output_to_ready_inventory_2026-04-10.md`

两者关系：
- `output_to_ready_inventory_2026-04-10.md`：盘点“现在有哪些脚本和文档”
- `qjb_branch_sync_plan_2026-04-10.md`：定义“接下来三机和 qjb 分支应该怎么组织”
