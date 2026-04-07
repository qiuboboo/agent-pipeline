# PhysReason split_open note

PhysReason 不建议全量改成 `split_open`。

随机看了几道多问题后，子问之间经常存在依赖：
- 有些是**弱依赖**：共享同一物理建模，但后问可基本独立重做。
- 也有不少是**强依赖**：后问直接建立在前问求出的碰撞系数、做功结果或中间关系上。

例子：
- **弱依赖**：[prob_dc5fbe6551994389c2d1c06c.json](ready/physreason/run_merged_physreason_0000_0300/datasets/physreason/samples/prob_dc5fbe6551994389c2d1c06c.json)
  - 第 1 问求灭火弹击中高楼时的高度 `H`
  - 第 2 问求电容工作电压 `U`
  - 两问共用背景，但第 2 问基本不依赖第 1 问结果，单独重写后仍可成立
- **强依赖**：[prob_0387e56f0a96baa08c2a14a8.json](ready/physreason/run_merged_physreason_0000_0300/datasets/physreason/samples/prob_0387e56f0a96baa08c2a14a8.json)
  - 背景：先用一次自由下落-反弹建立固定碰撞损失规律，再分析运动员下拍后篮球为何还能反弹回目标高度
  - 第 1 问求运动员对篮球做功 `w`
  - 第 2 问求拍球时施加力的大小
  - 第 2 问通常建立在第 1 问的做功结果上，拆开后容易丢失关键中间量

当前更适合：
1. 只对明显可独立回答的多问题尝试 `split_open`
2. 对“第 2 问/第 3 问依赖第 1 问结果”的题继续 `keep_open`
3. 先做小样本 A/B，而不是全量切换
