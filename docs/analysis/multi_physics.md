# multi_physics 改写样例分析

- 生成时间：`2026-04-07T10:10:09Z`
- ready 包：`ready/multi_physics/run_filtered_multi_physics_safe`
- 自动结果分布：`pass=22 / review=0 / reject=0`

## Pass 样本分析

- pass 样本数：`22`
- 改写策略分布：`blank_open=17, keep_open=1, split_open=4`

### Pass 案例 1：`prob_0076c2a440d63c484d11532e`

- source_problem_id：`174`
- rewrite_strategy：`blank_open`
- 图片：![](../ready/multi_physics/run_filtered_multi_physics_safe/datasets/multi_physics/artifacts/crops/prob_0076c2a440d63c484d11532e_primary_roi.png)

**原题**

矩形闭合线圈abcd竖直放置，OO′是它的对称轴，通电直导线AB与OO′平行，且AB、OO′所在平面与线圈平面垂直。若要在线圈中产生abcda方向的感应电流，可行的做法是(　　)

**改写**

矩形闭合线圈abcd竖直放置，OO′是它的对称轴，通电直导线AB与OO′平行，且AB、OO′所在平面与线圈平面垂直。若要在线圈中产生abcda方向的感应电流，线圈应如何绕OO′轴转动？

**分析**

该样本自动结果为 `pass`，改写策略是 `blank_open`。 改写把原始素材整理成开放问答形式，但没有引入新的审查风险信号。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

### Pass 案例 2：`prob_00cb75fb78d6482769d704e2`

- source_problem_id：`172`
- rewrite_strategy：`split_open`
- 图片：![](../ready/multi_physics/run_filtered_multi_physics_safe/datasets/multi_physics/artifacts/crops/prob_00cb75fb78d6482769d704e2_primary_roi.png)

**原题**

两同心圆环A、B置于同一水平面上，其中B为均匀带负电绝缘环，A为导体环。当B绕轴心顺时针转动且转速增大时，下列说法正确的是(　　)

**改写**

两同心圆环A、B置于同一水平面上，其中B为均匀带负电绝缘环，A为导体环。当B绕轴心顺时针转动且转速增大时，A中产生什么方向的感应电流？

**分析**

该样本自动结果为 `pass`，改写策略是 `split_open`。 虽然经过拆分式改写，但仍通过了自动检查，说明题意保持较稳定。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

### Pass 案例 3：`prob_439ce68098464f5d04ecd2ef`

- source_problem_id：`71`
- rewrite_strategy：`keep_open`
- 图片：![](../ready/multi_physics/run_filtered_multi_physics_safe/datasets/multi_physics/artifacts/crops/prob_439ce68098464f5d04ecd2ef_primary_roi.png)

**原题**

如图所示，A、B两物体相距x＝7 m，物体A以$v_A=4\mathrm{~m/s}$的速度向右匀速运动，而物体B此时的速度$v_B=10\mathrm{~m/s}$，只在摩擦力作用下向右做匀减速运动，加速度大小为$a=2\mathrm{~m/s^2}$，那么物体A追上物体B所用的时间为

**改写**

如图所示，A、B两物体相距x=7 m，物体A以$v_A=4\mathrm{~m/s}$的速度向右匀速运动，而物体B此时的速度$v_B=10\mathrm{~m/s}$，只在摩擦力作用下向右做匀减速运动，加速度大小为$a=2\mathrm{~m/s^2}$，那么物体A追上物体B所用的时间为多少？

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

### Pass 案例 4：`prob_09d53951d7f0473547fb3e48`

- source_problem_id：`83`
- rewrite_strategy：`split_open`
- 图片：![](../ready/multi_physics/run_filtered_multi_physics_safe/datasets/multi_physics/artifacts/crops/prob_09d53951d7f0473547fb3e48_primary_roi.png)

**原题**

一圆形金属环与两固定的平行长直导线在同一竖直面内，环的圆心与两导线距离相等，环的直径小于两导线间距。两导线中通有大小相等、方向向下的恒定电流。若(　　)

**改写**

一圆形金属环与两固定的平行长直导线在同一竖直面内，环的圆心与两导线距离相等，环的直径小于两导线间距。两导线中通有大小相等、方向向下的恒定电流。在这种装置中，金属环向哪一侧直导线靠近时，环上的感应电流方向为逆时针方向？

**分析**

该样本自动结果为 `pass`，改写策略是 `split_open`。 虽然经过拆分式改写，但仍通过了自动检查，说明题意保持较稳定。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

### Pass 案例 5：`prob_1dc62324d07fe546d4bb2ff0`

- source_problem_id：`162`
- rewrite_strategy：`blank_open`
- 图片：![](../ready/multi_physics/run_filtered_multi_physics_safe/datasets/multi_physics/artifacts/crops/prob_1dc62324d07fe546d4bb2ff0_primary_roi.png)

**原题**

质量为m的铜质小闭合线圈静置于粗糙水平桌面上。当一个竖直放置的条形磁铁贴近线圈，沿线圈中线由左至右从线圈正上方等高、匀速经过时，线圈始终保持不动。则关于线圈在此过程中受到的支持力FN和摩擦力Ff的情况，以下判断正确的是(　　)

**改写**

质量为m的铜质小闭合线圈静置于粗糙水平桌面上。当一个竖直放置的条形磁铁贴近线圈，沿线圈中线由左至右从线圈正上方等高、匀速经过时，线圈始终保持不动。在线圈运动过程中，线圈所受支持力FN与mg的大小关系如何变化？

**分析**

该样本自动结果为 `pass`，改写策略是 `blank_open`。 改写把原始素材整理成开放问答形式，但没有引入新的审查风险信号。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

## Review 原因分析

当前 ready 包没有可统计的 review reason codes。

当前 ready 包没有 `clean_decision=review` 的样本；该数据集当前只能分析 pass 改写例子。

## 小结

当前 ready 包以 `pass` 为主（pass=22, review=0, reject=0），更适合当作稳定改写样本集来观察。
