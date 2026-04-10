# qjb post-index handoff（2026-04-10）

> 目的：记录 `qjb` local-artifact policy 在**本地已经完成到哪一步**，以及从当前状态继续推进到 `origin/qjb` 与三机切换时，应该按什么顺序做。
>
> 本文是 `git rm --cached outputs ready ready_problem_exports` 之后的交接文档。

关联文档：
- `docs/qjb_branch_sync_plan_2026-04-10.md`
- `docs/qjb_branch_execution_checklist_2026-04-10.md`
- `docs/qjb_index_cleanup_preflight_2026-04-10.md`
- `docs/qjb_branch_landing_strategy_2026-04-10.md`
- `docs/qjb_docs_recovery_plan_2026-04-10.md`

---

## 1. 当前已完成状态

截至本次 handoff，以下动作已经在本地完成：

### 1.1 正式承接分支
- 正式承接分支：`qjb`
- 当前可用 worktree：`/tmp/agent-pipeline-qjb-clean`

### 1.2 docs-only 增量已回收到 `qjb`
`temp/run-summary-only` 上形成的 docs-only 增量，已经通过顺序 cherry-pick 回收到 `qjb`。

回收到 `qjb` 的内容包括：
- script boundary audit
- README boundary clarification
- checklist / `.gitignore` state sync
- index cleanup preflight
- landing strategy
- docs recovery plan

### 1.3 本地产物目录已停止被 Git 追踪
已在 `qjb` 上执行：

```bash
git rm -r --cached outputs ready ready_problem_exports
```

并已形成单独 commit：

- `3aa30249 qjb: stop tracking local outputs ready artifacts`

### 1.4 本地文件未被删除
索引清理后已确认：
- `outputs/` 仍在磁盘上
- `ready/` 仍在磁盘上
- `ready_problem_exports/` 仍在磁盘上

也就是说，这次变更是：
- **停止追踪**
- **不是删除本地数据**

---

## 2. 当前尚未完成状态

以下事项在本地尚未继续推进，后续需要按需执行：

### 2.1 远程分支尚未建立
当前检查结果：
- 本地有 `qjb`
- 远程 `origin/qjb` 目前不存在

因此，`qjb` 目前还是**本地完成、未对外发布**的状态。

### 2.2 三机尚未统一切换
三台机器（当前云服务器 / 另一台服务器 / 笔记本）尚未完成：
- 统一获取 `origin/qjb`
- 切换到 `qjb`
- 验证各机本地 `outputs -> ready` 重建能力

### 2.3 主工作树仍保留旧 temp docs 轨迹
当前主工作树仍在：
- branch: `temp/run-summary-only`

它保留的是 docs 形成时的原始 commit 链，不应再视为正式承接面。
正式口径应以 `qjb` 为准。

---

## 3. 从当前状态继续推进的推荐顺序

### Step 1：先确认 `qjb` worktree 状态
在执行任何对外动作前，先确认：

```bash
cd /tmp/agent-pipeline-qjb-clean
git status
git log --oneline -5
```

目标是再次确认：
- 当前分支确实是 `qjb`
- worktree 干净
- `HEAD` 包含 `3aa30249`

---

### Step 2：将本地 `qjb` 发布到远程
如果确认要把这条线作为三机统一基线，应执行：

```bash
cd /tmp/agent-pipeline-qjb-clean
git push -u origin qjb
```

执行后应验证：

```bash
git ls-remote --heads origin qjb
```

验收标准：
- 远程存在 `origin/qjb`
- 后续其他机器可直接 fetch / checkout 这条线

---

### Step 3：其他机器切到 `qjb`
在另外两台机器上，目标动作应是：

```bash
git fetch origin
git checkout qjb
```

如果本地已存在同名旧分支，应先核对其来源，不要盲目覆盖。

这一步的本质是：
- 统一代码 / 脚本 / docs / 规则
- 不试图通过 Git 分发 `outputs/` / `ready/`

---

### Step 4：按机器分别验证本地重建
每台机器都应独立验证：
- 自己本地是否有足够的 `outputs/`
- 是否能从本地 `outputs/` 成功重建本机 `ready/`
- post-ready / export / review 脚本是否仍依赖旧 canonical ready 包路径

重点不是“ready 是否从 Git 拉下来了”，而是：

> **该机器的本地 outputs 是否足以重建它所需要的 ready**

---

### Step 5：确认 temp 分支是否还需要保留
因为 docs 内容已经回收到 `qjb`，后续可以评估：
- `temp/run-summary-only` 是否仍需要保留作审计痕迹
- 或者在确认无用后再清理

这一步应放在：
- `origin/qjb` 已发布
- `qjb` 已成为明确正式线

之后再做，避免过早清理造成歧义。

---

## 4. 当前最重要的操作边界

从这一状态继续往前走时，最重要的是守住这三个边界：

### 4.1 不要回到 temp 上继续做正式变更
`temp/run-summary-only` 现在只应被视为：
- docs 形成期的历史轨迹

不应再继续把正式 policy 变更、索引变更、远程发布动作堆回 temp。

### 4.2 不要把“本地目录还在”误读成“Git 还在追踪”
索引清理后目录留在磁盘上是预期行为。

后续若看到本地目录存在，不应因此怀疑 `3aa30249` 失败；真正的判断标准应是：
- `git ls-files` / `git status`
- 当前分支 HEAD
- 是否能在新 clone / 新机器上不再从 Git 获得这些目录内容

### 4.3 不要把三机切换和数据搬运混成一个动作
三机切换是：
- 统一代码分支

数据搬运是：
- 用 rsync/scp/挂载盘/对象存储等方式处理 `outputs/`

这两件事应拆开，不要试图重新让 Git 承担运行产物同步职责。

---

## 5. 一句话结论

截至本文：

> **`qjb` 的本地 local-artifact policy 已经真正落地完成，下一步不是继续讨论 policy，而是决定是否发布 `origin/qjb`，并开始三机切换与本地重建验证。**
