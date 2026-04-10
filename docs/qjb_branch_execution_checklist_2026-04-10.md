# qjb 分支切换执行清单（2026-04-10）

> 目标：把 `agent-pipeline` 切到新的 `qjb` 工作线，明确 **Git 只同步代码/脚本/文档/规则**，而 `outputs/`、`ready/`、`ready_problem_exports/` 改为 **机器本地状态**。本文是执行顺序清单，不在本文里直接做删除或清零。

关联文档：
- `docs/output_to_ready_inventory_2026-04-10.md`
- `docs/qjb_branch_sync_plan_2026-04-10.md`

---

## 0. 先说结论：建议执行顺序

按这个顺序做，风险最低：

1. **冻结口径**：先确认 policy，不碰数据
2. **建分支**：创建并统一切到 `qjb`
3. **改文档**：README / docs 先改到新口径
4. **改脚本边界**：把依赖旧 ready 包的脚本清出来
5. **改 `.gitignore`**：让 outputs/ready 变成默认忽略
6. **清 Git 索引**：只取消追踪，不删本地文件
7. **三机切换**：A/B/笔记本分别同步到 `qjb`
8. **本机重建验证**：验证每台机器都能从本地 outputs 重建 ready

**不要倒过来做。**
尤其不要在 policy 没定、脚本没看清之前，就先 `git rm --cached outputs ready`。

---

## 1. Phase A：冻结 policy（不改数据）

### A1. 固定两份基准文档
确认以下两份文档作为当前基准：

- `docs/output_to_ready_inventory_2026-04-10.md`
- `docs/qjb_branch_sync_plan_2026-04-10.md`

目的：
- 第一份解决“现在仓库里有哪些链路、哪些脚本、哪些文档”
- 第二份解决“将来 qjb 分支三机应该怎么组织”

### A2. 固定新的 repo 口径
正式口径写死为：

- Git 负责：代码 / 脚本 / 文档 / 规则 / 配置
- 本地负责：`outputs/` / `ready/` / `ready_problem_exports/`
- `ready/` 默认通过本机脚本从本机 `outputs/` 重建
- 另一台服务器作为**最全 outputs 主源头**
- 其他机器按需同步 outputs，不通过 Git 分发运行产物

### A3. 本阶段禁止动作
在进入下一阶段前，先不要做这些：

- 不删除任何 `outputs/`
- 不删除任何 `ready/`
- 不做“清零”
- 不直接改 build 口径
- 不直接清 Git 索引

---

## 2. Phase B：创建 `qjb` 分支并固定起点

### B1. 选择基准机器
建议以**当前主开发机**作为建分支起点，但要先确认它的代码是你认可的起点。

### B2. 创建分支
执行目标：

```bash
git checkout -b qjb
```

如果远程已存在同名分支，则改为：

```bash
git fetch origin
git checkout qjb
```

### B3. 推送远程分支
首次推送：

```bash
git push -u origin qjb
```

### B4. 记录起点 commit
在文档或消息里记下：
- `qjb` 是从哪个 commit 切出来的
- 三台机器后续都以这个分支为统一代码源

**验收标准**
- 本地存在 `qjb`
- 远程存在 `origin/qjb`
- 三台机器都能看到这个分支

---

## 3. Phase C：先改文档口径

这个阶段先改“说法”，再改“机制”。

### C1. 更新 README
README 至少要改这几条：

- `outputs/` 不再纳入 Git 跟踪
- `ready/` 不再纳入 Git 跟踪
- `ready_problem_exports/` 不再纳入 Git 跟踪
- `ready` 是本地派生产物
- 跨机器同步 outputs 应通过 `rsync/scp/挂载盘/对象存储` 等方式
- 本机 outputs 覆盖与 ready 生成，依赖哪些脚本

### C2. 给 docs 增加入口
建议在 docs 入口里明确三类文档：

1. **盘点**：`output_to_ready_inventory_2026-04-10.md`
2. **policy**：`qjb_branch_sync_plan_2026-04-10.md`
3. **执行**：`qjb_branch_execution_checklist_2026-04-10.md`（本文）

### C3. 给未来读者一句总规则
建议加一句醒目的总规则：

> 从 `qjb` 分支开始，仓库只同步代码与规则；`outputs/`、`ready/`、`ready_problem_exports/` 是本地状态，不作为 Git 同步对象。

**验收标准**
- README 不再出现“outputs 应纳入 Git 跟踪”这类旧口径
- docs 里能找到 policy + checklist

---

## 4. Phase D：梳理脚本边界，避免切换后脚本失效

这是最容易被忽略、但最容易翻车的一步。

### D1. 固定正式主链
当前正式主链应认定为：

- `scripts/build_ready_from_outputs_content_dedup.py`

要求：
- 未来 canonical ready 以它为主
- 不再让其它历史特例脚本和它并列充当“正式入口”

### D2. 固定 post-ready 边界
明确以下属于 **post-ready**，不是 build ready 本体：

- `scripts/apply_manual_review_release.py`
- `docs/review/review_release_template.md`
- `scripts/build_review_docs.py`
- `scripts/export_ready_to_problem_json.py`

### D3. 清理旧 ready 路径依赖
重点检查：

- `scripts/build_review_docs.py`
- 各类 review / analysis / status 文档生成入口

要确认它们是否：
- 仍硬编码旧 `ready/<dataset>/<old_package>` 路径
- 仍假设 ready 是 Git 跟踪目录
- 仍假设所有机器都有同样的 ready 包

### D4. 给“依赖本机 ready”的脚本加前置说明
如果某脚本必须依赖本机已生成的 ready，应在文档或 help 里明确写出：

- 运行前需先本地 build ready
- 如果本机没有该 ready package，会失败
- 这是预期行为，不是 Git 同步问题

**验收标准**
- 主链脚本边界明确
- review/release 不再被误认为 build 阶段
- 至少列出所有仍依赖旧 ready 包的脚本清单

---

## 5. Phase E：核对并冻结 `.gitignore` 口径

### E1. 当前状态
当前仓库里的 `.gitignore` 已经覆盖了 `qjb` policy 需要的核心本地产物规则，包含：

```gitignore
# local runtime artifacts
outputs/
ready/
ready_problem_exports/

# nested runtime caches inside outputs
outputs/repo_cache/
outputs/**/repo_cache/
outputs/**/.git/

# python cache / logs
__pycache__/
*.pyc
*.log
.DS_Store
```

也就是说，这一阶段的重点已经不是“补出第一版 ignore 规则”，而是：
- 确认这套口径与 README / docs 一致
- 不再回退到只忽略 `repo_cache` 的旧说法
- 明确 `.gitignore` **不会自动取消已追踪文件**

### E2. 本阶段结论
当前 `.gitignore` 口径可直接视为 `qjb` policy 的目标状态：

- `outputs/`、`ready/`、`ready_problem_exports/` 默认忽略
- `__pycache__/`、`*.pyc`、`*.log` 默认忽略
- nested cache / nested `.git` 仍显式忽略

如需保留个别小样例，不要放在真实 `outputs/`、`ready/` 里；应迁到：
- `examples/`
- `fixtures/`

### E3. 修改原则
这一阶段只做两件事：
- 核对 `.gitignore` 与 README / docs 口径一致
- 为下一阶段索引清理做好前置条件

仍然**不要**在这一步：
- 删除任何真实文件
- 执行索引清理
- 把“已忽略”误当成“已停止追踪”

**验收标准**
- `.gitignore` 已与当前 policy 对齐
- 文档不再保留“当前只忽略 `outputs/repo_cache/`”这类过时描述
- 团队对“ignore 规则 != 取消追踪”这一点没有歧义

---

## 6. Phase F：清理 Git 索引（只取消追踪，不删本地）

> 这是高影响动作。要在 `qjb` 分支上做，不要在旧分支和脏工作树里乱做。

### F1. 前置检查
执行前必须确认：

- `.gitignore` 已更新
- README / docs 口径已更新
- 当前在 `qjb` 分支
- 确认要保留的本地 `outputs/`、`ready/` 文件都还在磁盘上

### F2. 执行动作
目标动作是：

```bash
git rm -r --cached outputs ready ready_problem_exports
```

注意：
- 这是**取消追踪**，不是删除本地文件
- 但仍然是高风险动作，必须在确认后执行

### F3. 检查结果
执行后应验证：

- 本地 `outputs/` 目录还在
- 本地 `ready/` 目录还在
- `git status` 中显示的是“从索引删除”，不是磁盘消失

### F4. 提交 policy 切换 commit
建议单独一个 commit，提交信息类似：

```text
Stop tracking local outputs and ready artifacts on qjb
```

**验收标准**
- `outputs/ready` 仍在磁盘
- Git 不再追踪这些目录
- 新建/新改 outputs/ready 不再污染 `git status`

---

## 7. Phase G：三台机器切换到 `qjb`

## G1. 云服务器B（最全 outputs 主源头）

目标：
- 切到 `qjb`
- 保留最全 `outputs/`
- 作为其它机器补数据的来源

建议动作：

1. `git fetch origin`
2. `git checkout qjb`
3. `git pull`
4. 检查本地 `outputs/` 是否完整
5. 不要求提交 `ready/`

### G2. 当前云服务器A

目标：
- 切到 `qjb`
- 保留当前机器常用 outputs
- 缺什么再从云服务器B按需同步

建议动作：

1. `git fetch origin`
2. `git checkout qjb`
3. `git pull`
4. 运行 outputs 覆盖盘点脚本
5. 根据缺口从云服务器B同步对应 outputs 子目录
6. 本机构建 ready

### G3. 个人笔记本

目标：
- 切到 `qjb`
- 保留工作需要的局部 outputs
- 做文档、代码、小规模验证

建议动作：

1. `git fetch origin`
2. `git checkout qjb`
3. `git pull`
4. 只按需拉取 outputs 子集
5. 本地构建子集 ready

**验收标准**
- 三台机器都在 `qjb`
- 三台机器都不再依赖 Git 获得 outputs/ready
- 三台机器都知道自己本地 outputs 覆盖范围

---

## 8. Phase H：建立新的数据同步方式（非 Git）

### H1. 固定主数据源
明确：
- **另一台服务器 = 最新最全 outputs 主源头**

### H2. 固定同步策略
推荐原则：
- 代码：Git 同步
- outputs：`rsync/scp/外部存储` 同步
- ready：不跨机器同步，默认本机重建

### H3. 固定最小同步粒度
建议按以下粒度同步 outputs：

- 数据集级
- range 级
- 必要时 run 级

不要一上来全量复制全部 outputs，除非确实需要。

### H4. 给同步动作留出 manifest 支撑
切换后应经常用：
- `scripts/build_sample_manifest.py`
- `scripts/build_output_root_coverage.py`

来回答：
- 本机缺哪些 outputs
- 哪些 ready 是由哪些 source run 组成

**验收标准**
- 至少有一条可重复的数据同步路径
- 不用 Git 也能把需要的 outputs 从云服务器B拉到别的机器

---

## 9. Phase I：本机 ready 重建验证

这个阶段才真正证明新方案站得住。

### I1. 选一个数据集做 smoke test
优先选一个中等规模的数据集，例如：
- `mm_math`
- `seephys`
- `emma_physics`

不要一开始就拿最重的数据集做验证。

### I2. 在某一台机器上验证“本机 outputs -> 本机 ready”
验证流程：

1. 确认本机有该数据集所需 outputs
2. 如有旧 ready，先只针对该目标包做可控清理/备份
3. 运行主链脚本重建 ready
4. 检查：
   - `selection_validation.ok = true`
   - `write_validation.ok = true`
   - `summary.json` 正常
   - 样本数与预期一致

### I3. 在第二台机器上复现
用同一代码版本、同一 outputs 子集，在另一台机器复现同一数据集。

重点检查：
- 结果是否一致
- summary 是否一致
- provenance / selection manifest 是否一致

### I4. 再扩大到重点数据集
验证顺序建议：
1. `mm_math`
2. `seephys`
3. `emma_physics`
4. `mathvision`
5. `eee_bench`
6. `physreason`

**验收标准**
- 至少两个机器能对同一数据集生成一致 ready
- selection/write validation 都通过

---

## 10. Phase J：历史链归档与后续清理

这个阶段不是现在立刻做，但后面一定要做。

### J1. 历史特例脚本归档候选
后续优先归档：

- `scripts/build_ready_from_outputs_content_dedup.fdefb72.py`
- `scripts/export_special_outputs_to_ready.py`
- `scripts/build_physreason_merged_full.js`
- `scripts/build_physreason_merged_summary.js`

### J2. 历史说明文档归档候选
后续把强历史口径的说明文档标注为：
- 历史记录
- 非当前 canonical build 入口

### J3. 保留必要 provenance
归档不等于抹掉历史。

需要保留：
- 为什么某些数据集曾有特例
- 为什么 `physreason` 是特殊 case
- 为什么 `eee_bench_merged_*` 要排除

**验收标准**
- 新人不再误把历史特例脚本当正式入口
- 当前 canonical path 只有一条主线

---

## 11. 实操时的风险提示

### 风险 1：在旧分支直接清索引
不要这样做。先切 `qjb`，再动索引。

### 风险 2：把 `.gitignore` 当成“自动取消追踪”
不是。`.gitignore` 只能阻止新文件进入视野，不能把已追踪文件自动拿掉。

### 风险 3：以为 ready 不追踪 = ready 不重要
不是。ready 仍然重要，只是它变成**本地可重建产物**。

### 风险 4：三机 outputs 不一致导致误判
这是预期现象，不是 bug。关键是要能盘点出差异，而不是假设它们一致。

### 风险 5：脚本仍硬编码旧 ready 包
这是切换后最容易炸的地方，优先检查 `build_review_docs.py` 一类脚本。

---

## 12. 最终验收清单

全部做完后，至少应满足以下条件：

- [ ] `origin/qjb` 已存在
- [ ] 三台机器都已切到 `qjb`
- [ ] README 已改成“outputs/ready 本地化”口径
- [ ] `.gitignore` 已忽略 `outputs/`、`ready/`、`ready_problem_exports/`
- [ ] Git 已停止追踪这些目录
- [ ] 云服务器B被明确为最全 outputs 主源头
- [ ] 其它机器可按需同步 outputs，而不是靠 Git
- [ ] 至少两个机器成功从本地 outputs 重建同一 ready 包
- [ ] `selection_validation.ok = true`
- [ ] `write_validation.ok = true`
- [ ] 历史特例脚本已被标注为历史链，而不是正式主入口

---

## 13. 我建议的下一步动作

如果按这个 checklist 往下走，下一步最合理的是：

1. **先改 README + `.gitignore` 草案**
2. **列出所有依赖旧 ready 路径的脚本/文档**
3. **确认后再真正执行 `git rm --cached`**
4. **最后再开始三机切换**

也就是说，下一轮最适合做的是：

> 产出一版 `qjb` policy 落地 patch（README / `.gitignore` / docs 入口），但先不做索引清理。
