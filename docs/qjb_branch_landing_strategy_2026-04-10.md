# qjb 分支落点策略（2026-04-10）

> 目的：明确当前 `qjb` local-artifact policy / 索引清理相关 commit，**最终应该落在哪个分支**，以及当前 `temp/run-summary-only` 与本地 `qjb` 之间的关系。
>
> 本文只做分支落点决策说明，不执行分支切换，不执行 cherry-pick，不执行 `git rm --cached`。

关联文档：
- `docs/qjb_branch_sync_plan_2026-04-10.md`
- `docs/qjb_branch_execution_checklist_2026-04-10.md`
- `docs/qjb_index_cleanup_preflight_2026-04-10.md`

---

## 1. 当前已核实的 Git 事实

截至本次检查，仓库里的相关分支 / worktree 状态是：

### 当前活跃工作树
- worktree：`/root/.openclaw/workspace/agent-pipeline`
- 当前分支：`temp/run-summary-only`
- 当前 `HEAD`：`3e6c7711`

### 当前 `qjb` 分支
- 本地分支：`qjb`
- `qjb` 当前指向：`a1d7d197`
- `qjb` 当前绑定的 worktree：`/tmp/agent-pipeline-qjb-clean`

### 远程情况
- 当前远程分支列表中**没有** `origin/qjb`
- 也就是说，`qjb` 目前仍是**本地分支引用**，尚未形成统一远程工作线

---

## 2. 当前 temp 分支与 qjb 的真实关系

本次检查的 merge-base / 独有提交关系是：

- `merge-base(qjb, temp/run-summary-only) = a1d7d197`
- `qjb` 相对于 `temp/run-summary-only`：**没有额外提交**
- `temp/run-summary-only` 相对于 `qjb`：有以下纯增量 docs commit
  - `72471dc3 docs: add qjb script boundary audit`
  - `c2b5de41 docs: clarify qjb README boundaries`
  - `36ca0b8e docs: sync qjb checklist with gitignore state`
  - `3e6c7711 docs: add qjb index cleanup preflight`
  - `de738f6b docs: define qjb landing branch strategy`

这说明：

> 当前 `temp/run-summary-only` 不是另一条和 `qjb` 并行分叉很远的工作线；它本质上是**从 `qjb` 当前头部 `a1d7d197` 往前累积了 5 个 docs-only 增量 commit 的承载分支**。

换句话说：

- `qjb` = 当前正式候选分支名，但头部还停在旧位置
- `temp/run-summary-only` = 暂时承载了最新 docs 进展的工作分支

---

## 3. 这意味着什么

## 3.1 最终正式落点应是 `qjb`

因为整个 policy、三机同步、索引清理、后续重建验证，都是围绕：

- `qjb` 作为正式工作线
- 三机最终统一切到 `qjb`

来设计的。

所以从命名语义和后续协作成本看，最终承接这些 commit 的分支应该是：

- **`qjb`**

而不是：

- `temp/run-summary-only`

---

## 3.2 `temp/run-summary-only` 应被视为过渡承载分支

当前 `temp/run-summary-only` 的价值是：

- 在不强行切换当前大脏工作树的前提下，先把文档与 policy 整理工作推进完
- 让最新 docs 进展先安全落成 commit

但它不适合作为最终长期承接分支，原因有三：

1. **名字是临时语义**
   - 它看起来像一次阶段性执行 / 汇总分支，不像长期 policy 工作线

2. **与三机同步方案不匹配**
   - 三机方案写的是统一切到 `qjb`
   - 不是统一切到 `temp/run-summary-only`

3. **后续远程落点会混乱**
   - 如果继续在 temp 分支上做真正的索引清理与 policy 切换，后面还得再解释：
     - temp 是不是正式线
     - qjb 还要不要
     - 远程到底推哪个

---

## 4. 因此，对“索引清理 commit 落点”的建议结论

### 建议结论

> **索引清理 commit 的正式落点应是 `qjb`，不是 `temp/run-summary-only`。**

当前更合理的顺序应是：

1. 先把 `temp/run-summary-only` 上这 5 个 docs-only 增量回收到 `qjb`
2. 让 `qjb` 变成“已吸收最新 policy 文档状态”的正式承接分支
3. 再在 `qjb` 上执行：
   ```bash
   git rm -r --cached outputs ready ready_problem_exports
   ```
4. 之后如需远程统一，再把 `qjb` 推到远程

---

## 5. 为什么不建议直接在 temp 分支上继续做索引清理

虽然技术上当然可以在 `temp/run-summary-only` 上执行 `git rm --cached`，但不建议这样做，原因是：

### 5.1 会把“文档过渡分支”和“正式 policy 分支”混为一体

这样会让后续读历史的人很难理解：
- 到底哪个分支才是三机统一工作线
- temp 分支和 qjb 分支谁才是主线

### 5.2 后续还得再做一次“把 temp 收回 qjb”的动作

如果索引清理 commit 也先落在 temp 上，之后还是要解决：
- qjb 如何跟上
- 远程最终推哪个
- 其它机器该切哪个

相当于把必须解决的问题往后拖，而不是消除它。

### 5.3 `qjb` 本地分支目前并没有分叉出额外非文档提交

这点很关键。

因为当前关系非常干净：
- `qjb` 停在 `a1d7d197`
- `temp/run-summary-only` 只是多了 5 个 docs-only 提交

所以现在处理分支落点，成本是最低的。

---

## 6. 当前最稳的分支策略

基于当前状态，建议采用下面这条策略：

### Phase 1：把 docs 增量收归 `qjb`
目标：
- 让 `qjb` 成为最新 policy 文档状态的正式承接分支

### Phase 2：只在 `qjb` 上做索引清理
目标：
- 把本地产物停止追踪这一步，直接落在正式工作线上

### Phase 3：以 `qjb` 为中心做后续三机切换
目标：
- 云服务器 A / B / 笔记本都围绕同一个正式分支名工作

---

## 7. 本文给出的最终判断

基于当前已核实的 Git 状态，可以下这个明确判断：

1. `qjb` 当前真实存在，且绑定在 `/tmp/agent-pipeline-qjb-clean` worktree 上
2. `temp/run-summary-only` 当前只是比 `qjb` 多 4 个 docs-only 增量 commit
3. 因此，**最终正式落点应是 `qjb`**
4. `temp/run-summary-only` 应视为阶段性承载分支，而不是最终 policy 主线
5. 后续真正高影响的索引清理动作，不建议先落在 temp 分支

---

## 8. 建议的下一步

完成本文后，下一步建议直接进入：

1. 设计“如何把当前 temp 上 4 个 docs-only 提交安全回收到 `qjb`”
2. 明确该回收动作是在现有 `/tmp/agent-pipeline-qjb-clean` worktree 上做，还是用更稳的只读/低风险方式做
3. 回收完成后，再进入索引清理执行
