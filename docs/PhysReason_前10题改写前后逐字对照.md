# PhysReason 前 10 题改写前后逐字对照

- 数据来源：`outputs/physreason_validation_10_rerun/run_45692c67ba13ca88`
- 说明：以下“原题”尽量取自样本中的原始题面；“改写后”取自 `rewrite_reports.jsonl` 中的 `rewritten_question_text`。
- 本批次结果：`pass=5 / review=5 / reject=0`，且 LLM 调用成功 (`successful_request_count=60`)。

## 本批次改写特征总结

### 总体特征

- 这 10 条样本全部走了 `rewrite_strategy = keep_open`
- 改写整体偏**保守型规范化**，不是大幅重写
- 主要收益在于：
  - 题面表达更线性
  - 数学符号与单位格式更规整
  - 多小问结构更接近标准开放题
- 整体风格是“**尽量保真，不主动重构**”

### 观察到的优点

- 没有明显改坏题意或删掉关键条件
- 多数题目在改写后仍能完整保留原物理场景、约束和求解目标
- 对本身已经较完整的开放题，`keep_open` 路径效果稳定
- 较短或中等长度题目（如波动、油滴实验、篮球回弹等）改写后可读性提升较明显

### 观察到的不足

- 对长题、综合题的压缩能力有限，题面仍然偏长
- 多小问答案常常仍以“连续堆叠公式/结果”的方式呈现，可读性一般
- 对图依赖题，改写后虽然保留了 “As shown in the figure...” 之类描述，但不一定充分把图中必要信息文字化
- 对工程背景较重或条件很多的题目，改写后仍然容易进入 `review`

### 当前判断

- 这批改写结果整体**可用**
- 更适合作为“开放题规范化整理”结果，而不是“高强度重写优化”结果
- 如果后续继续批跑 PhysReason，建议重点关注：
  - 长题压缩
  - 多问答案编号化/结构化
  - 图像关键信息的文本化表达
  - `review` 样本中是否存在系统性模式（如题太长、图依赖过强、答案表达过密）

## 1. cal_problem_00035 / prob_01a437b145f0376c39e3c023

- `decision`: `pass`
- `title`: `PhysReason 开放题`
- `rewrite_strategy`: `keep_open`

### 原题

An L-shaped skateboard A is initially at rest on a rough horizontal surface. A light spring with a spring constant of $k$ is fixed to the right end of the skateboard. The left end of the spring is connected to a small block B, and the spring is initially at its natural length. A small block C slides onto the skateboard from its leftmost end with an initial velocity $v_{0}$. After traveling a distance of $s_{0}$, it undergoes a perfectly inelastic collision with B (the collision time is extremely short), and then they move together to the right. After a certain period, the skateboard A also begins to move. The masses of A, B, and C are all $m$. The coefficient of kinetic friction between the skateboard and the small blocks, and between the skateboard and the ground, are both $\mu$. The magnitude of gravitational acceleration is $g$. The maximum static friction is approximately equal to the sliding friction, and the spring remains within its elastic limit throughout.

1. What is the magnitude of the velocity of C just before the collision?
2. What is the mechanical energy loss during the collision between C and B?
3. How much work is done by C and B against friction from the instant of the collision until A begins to move?

### 原答案

$\sqrt{v_{0}^{2}-2\mu g s_{0}}$
$\frac{1}{4}m(v_{0}^{2}-2\mu g s_{0})$
$\frac{2\mu^{2}m^{2}g^{2}}{k}$

### 改写后题目

An L-shaped skateboard A is initially at rest on a rough horizontal surface. A light spring with a spring constant of $k$ is fixed to the right end of the skateboard. The left end of the spring is connected to a small block B, and the spring is initially at its natural length. A small block C slides onto the skateboard from its leftmost end with an initial velocity $v_{0}$. After traveling a distance of $s_{0}$, it undergoes a perfectly inelastic collision with B (the collision time is extremely short), and then they move together to the right. After a certain period, the skateboard A also begins to move. The masses of A, B, and C are all $m$. The coefficient of kinetic friction between the skateboard and the small blocks, and between the skateboard and the ground, are both $\mu$. The magnitude of gravitational acceleration is $g$. The maximum static friction is approximately equal to the sliding friction, and the spring remains within its elastic limit throughout.

1. What is the magnitude of the velocity of C just before the collision?
2. What is the mechanical energy loss during the collision between C and B?
3. How much work is done by C and B against friction from the instant of the collision until A begins to move?

### 改写后参考答案

$\sqrt{v_{0}^{2}-2\mu g s_{0}}$
$\frac{1}{4}m(v_{0}^{2}-2\mu g s_{0})$
$\frac{2\mu^{2}m^{2}g^{2}}{k}$

---

## 2. cal_problem_00045 / prob_7f8a40f70e2614f26f18c94b

- `decision`: `review`
- `title`: `PhysReason 开放题`
- `rewrite_strategy`: `keep_open`

### 原题

In a vertical plane, a block $a$ of mass $m$ is initially at rest at point $A$ directly below the suspension point $O$. A conveyor belt MN, rotating counterclockwise with a velocity $v$, is coplanar with the horizontal tracks AB, CD, and FG. The lengths of AB and FG are both $L$, and the midpoint of FG is $E$. A small object $b$ of mass $m$ is gently placed on the conveyor belt. At a certain moment, a small steel ball enters the horizontal pipe from its left end with a horizontal initial velocity, striking $b$ exactly at point N, after which $b$ starts moving leftward. The collision time is extremely short, and all collisions are elastic. The radius of the steel ball is negligible. The mechanical energy of the system is conserved, and air resistance is ignored. Answer the following:

1. What is the maximum speed of $a$ during its motion?
2. Let the height difference between the position of $a$ and point $A$ be $h$. Find the expression of the support force $F_N$ exerted by the support bar on $a$ as a function of $h$.
3. If after being hit, $b$ moves leftward and eventually comes to rest at point $E$, find the possible range of the initial speed of the steel ball.

### 原答案

5\mathrm{m/s}
F_{N}=0.1h-0.14(N) (h \geq 1.2m, direction of $F_{N}$ is vertically downwards)
when $0.9m<h<1.2m$，$2.6m{<}x{\leq}3m$，When $1.2m \leq h \leq 1.65m$，$3.4m{\leq}x{<}3.8m$

### 改写后题目

In a vertical plane, a block $a$ of mass $m$ is initially at rest at point $A$ directly below the suspension point $O$. A conveyor belt MN, rotating counterclockwise with a velocity $v$, is coplanar with the horizontal tracks AB, CD, and FG. The lengths of AB and FG are both $L$, and the midpoint of FG is $E$. A small object $b$ of mass $m$ is gently placed on the conveyor belt. At a certain moment, a small steel ball enters the horizontal pipe from its left end with a horizontal initial velocity, striking $b$ exactly at point N, after which $b$ starts moving leftward. The collision time is extremely short, and all collisions are elastic. The radius of the steel ball is negligible. The mechanical energy of the system is conserved, and air resistance is ignored. Answer the following:

1. What is the maximum speed of $a$ during its motion?
2. Let the height difference between the position of $a$ and point $A$ be $h$. Find the expression of the support force $F_N$ exerted by the support bar on $a$ as a function of $h$.
3. If after being hit, $b$ moves leftward and eventually comes to rest at point $E$, find the possible range of the initial speed of the steel ball.

### 改写后参考答案

5\mathrm{m/s}
F_{N}=0.1h-0.14(N)\; (h \geq 1.2m,\text{ direction of }F_{N}\text{ is vertically downwards})
when\ 0.9m<h<1.2m,\ 2.6m<x\leq 3m;\ when\ 1.2m \leq h \leq 1.65m,\ 3.4m\leq x<3.8m

---

## 3. cal_problem_00049 / prob_a857581cd681b52185e46c3b

- `decision`: `review`
- `title`: `PhysReason 开放题`
- `rewrite_strategy`: `keep_open`

### 原题

A basketball of mass $m$ is dropped from rest at a height $H$ above the ground. It undergoes an inelastic collision with the ground and rebounds to a maximum height $h$ above the ground. The magnitude of the air resistance experienced by the basketball is constant and equal to $\lambda mg$ during both descent and ascent, where $0<\lambda<1$. The collision time is negligible. Assume the coefficient of restitution between the basketball and the ground is constant.

1. Express the coefficient of restitution $k$ in terms of $H$, $h$, and $\lambda$.
2. Suppose that after the first rebound, the ball reaches a maximum height $h_0$. Determine the average force $F_0$ exerted by the ground on the basketball during the collision.
3. If the ball is repeatedly dropped and rebounds to heights forming a sequence, find the impulse $I$ delivered by the ground after $N$ collisions.

### 原答案

$k=\sqrt{\frac{(1+\lambda)h}{(1-\lambda)H}}$
$F_{0}=\frac{2m g(1-\lambda)(H-h)}{h-h_{0}}$
$I=m\sqrt{\frac{2g(1-\lambda)(H-h)(H^{N+1}-h^{N+1})}{h(H^{N}-h^{N})}}$

### 改写后题目

A basketball of mass $m$ is dropped from rest at a height $H$ above the ground. It undergoes an inelastic collision with the ground and rebounds to a maximum height $h$ above the ground. The magnitude of the air resistance experienced by the basketball is constant and equal to $\lambda mg$ during both descent and ascent, where $0<\lambda<1$. The collision time is negligible. Assume the coefficient of restitution between the basketball and the ground is constant.

1. Express the coefficient of restitution $k$ in terms of $H$, $h$, and $\lambda$.
2. Suppose that after the first rebound, the ball reaches a maximum height $h_0$. Determine the average force $F_0$ exerted by the ground on the basketball during the collision.
3. If the ball is repeatedly dropped and rebounds to heights forming a sequence, find the impulse $I$ delivered by the ground after $N$ collisions.

### 改写后参考答案

$k=\sqrt{\frac{(1+\lambda)h}{(1-\lambda)H}}$
$F_{0}=\frac{2m g(1-\lambda)(H-h)}{h-h_{0}}$
$I=m\sqrt{\frac{2g(1-\lambda)(H-h)(H^{N+1}-h^{N+1})}{h(H^{N}-h^{N})}}$

---

## 4. cal_problem_00057 / prob_7c5896fc8ee4c3f482175e14

- `decision`: `pass`
- `title`: `PhysReason 开放题`
- `rewrite_strategy`: `keep_open`

### 原题

A simple harmonic transverse wave propagates along the positive direction of the $x$-axis. The equilibrium position of the wave source is at the origin of the coordinate system. The vibration graph of the wave source within $0 \sim 4s$ is shown in the figure. At $t=0$, the wave just begins to propagate from the wave source. The wave speed is constant.

1. Determine the wavelength $\lambda$ of the wave.
2. Find the displacement $s$ of a given particle under the specified condition.

### 原答案

$\lambda=2\mathsf{m}$
$s=16cm$

### 改写后题目

A simple harmonic transverse wave propagates along the positive direction of the $x$-axis. The equilibrium position of the wave source is at the origin of the coordinate system. The vibration graph of the wave source within $0 \sim 4s$ is shown in the figure. At $t=0$, the wave just begins to propagate from the wave source. The wave speed is constant.

1. Determine the wavelength $\lambda$ of the wave.
2. Find the displacement $s$ of a given particle under the specified condition.

### 改写后参考答案

$\lambda=2\mathsf{m}$
$s=16cm$

---

## 5. cal_problem_00066 / prob_c7c80add61e033fda5c0f109

- `decision`: `review`
- `title`: `PhysReason 开放题`
- `rewrite_strategy`: `keep_open`

### 原题

A horizontal platform of height $H=0.4m$ is placed on a level ground, on which a rough straight track $AB$ with an inclination angle of $\theta=37^{\circ}$, a horizontal smooth straight track $BC$, a quarter-circular smooth thin circular pipe $CD$, and a horizontal rough straight track $DE$ are arranged in sequence. A small object starts from point A and moves through these tracks under the influence of gravity and friction.

1. Find the speed of the object at a certain position.
2. Determine the minimum height $h_{min}$ required under the given condition.
3. Find the distance traveled on the final rough track.

### 原答案

$4m/s$
$h_{min} = 0.45m$
$0.8m$

### 改写后题目

A horizontal platform of height $H=0.4m$ is placed on a level ground, on which a rough straight track $AB$ with an inclination angle of $\theta=37^{\circ}$, a horizontal smooth straight track $BC$, a quarter-circular smooth thin circular pipe $CD$, and a horizontal rough straight track $DE$ are arranged in sequence. A small object starts from point A and moves through these tracks under the influence of gravity and friction.

1. Find the speed of the object at a certain position.
2. Determine the minimum height $h_{min}$ required under the given condition.
3. Find the distance traveled on the final rough track.

### 改写后参考答案

$4m/s$
$h_{min} = 0.45m$
$0.8m$

---

## 6. cal_problem_00069 / prob_f52b488facca65c7dc8f009c

- `decision`: `pass`
- `title`: `PhysReason 开放题`
- `rewrite_strategy`: `keep_open`

### 原题

A basketball with a mass of $m = 0.60\mathrm{kg}$ is released from rest at a height of $h_1 = 1.8\mathrm{m}$ above the ground, and it rebounds to a height of $h_2 = 1.2\mathrm{m}$. If the basketball is released from rest at a height of $h_3 = 1.5\mathrm{m}$ instead, determine the required physical quantities under the same collision characteristics.

### 原答案

4.5J
9N

### 改写后题目

A basketball with a mass of $m = 0.60\mathrm{kg}$ is released from rest at a height of $h_1 = 1.8\mathrm{m}$ above the ground, and it rebounds to a height of $h_2 = 1.2\mathrm{m}$. If the basketball is released from rest at a height of $h_3 = 1.5\mathrm{m}$ instead, determine the required physical quantities under the same collision characteristics.

### 改写后参考答案

4.5J
9N

---

## 7. cal_problem_00080 / prob_abee1b6763abe8c5bc46fdce

- `decision`: `pass`
- `title`: `PhysReason 开放题`
- `rewrite_strategy`: `keep_open`

### 原题

As shown in the figure, an elastic bumper is installed at the bottom of a fixed inclined plane with an inclination angle of $\theta$. The masses of two blocks, P and Q, are $m$ and $4m$, respectively. Q is initially at rest at point A on the inclined plane. Under the given initial condition, analyze the subsequent motion and related physical quantities.

### 原答案

The speed of P is $\frac{3}{5}v_{0}$, the speed of Q is $\frac{2}{5}v_{0}$.
$h_{n}=(\frac{7}{25})^{n-1}\cdot\frac{v_{0}^{2}}{25g}$
$H=...$

### 改写后题目

As shown in the figure, an elastic bumper is installed at the bottom of a fixed inclined plane with an inclination angle of $\theta$. The masses of two blocks, P and Q, are $m$ and $4m$, respectively. Q is initially at rest at point A on the inclined plane. Under the given initial condition, analyze the subsequent motion and related physical quantities.

### 改写后参考答案

The speed of P is $\frac{3}{5}v_{0}$, the speed of Q is $\frac{2}{5}v_{0}$.
$h_{n} = \left(\frac{7}{25}\right)^{n-1} \cdot \frac{v_{0}^{2}}{25g}$, $(n=1,2,3,\ldots)$
$H = ...$

---

## 8. cal_problem_00121 / prob_1de3cadd4760801be164f51b

- `decision`: `review`
- `title`: `PhysReason 开放题`
- `rewrite_strategy`: `keep_open`

### 原题

Electromagnetic aircraft launch is the most advanced catapult technology for aircraft carriers, and China has reached the world's advanced level in this field. An interest group is conducting research on the design of an electromagnetic launch system. As shown in the relevant figure/model, answer the related questions.

### 原答案

80A
0.5Ω
$t_3 = \frac{\sqrt{5}+3}{2}s$

### 改写后题目

Electromagnetic aircraft launch is the most advanced catapult technology for aircraft carriers, and China has reached the world's advanced level in this field. An interest group is conducting research on the design of an electromagnetic launch system. As shown in the relevant figure/model, answer the related questions.

### 改写后参考答案

80A
0.5Ω
$t_3 = \frac{\sqrt{5}+3}{2}s$

---

## 9. cal_problem_00122 / prob_8ff2691d45cdfe92a6e73a5d

- `decision`: `pass`
- `title`: `PhysReason 开放题`
- `rewrite_strategy`: `keep_open`

### 原题

Millikan proved the quantization of electric charge by observing the motion of oil droplets, for which he was awarded the Nobel Prize in Physics in 1923. The figure illustrates the principle of the Millikan oil-drop experiment, where two sufficiently large parallel metal plates are placed horizontally and charged, creating a uniform electric field between them. Answer the related questions.

### 原答案

k = \frac{m_{0}^{\frac{2}{3}} g t}{h_{1}}
Oil droplet A is uncharged, and oil droplet B carries a negative charge.
q = \frac{m_{0} g d (h_{1}+h_{2})}{h_{1} U}
$\Delta E_{p}=...$

### 改写后题目

Millikan proved the quantization of electric charge by observing the motion of oil droplets, for which he was awarded the Nobel Prize in Physics in 1923. The figure illustrates the principle of the Millikan oil-drop experiment, where two sufficiently large parallel metal plates are placed horizontally and charged, creating a uniform electric field between them. Answer the related questions.

### 改写后参考答案

k = \frac{m_{0}^{\frac{2}{3}} g t}{h_{1}}
Oil droplet A is uncharged, and oil droplet B carries a negative charge.
And q = \frac{m_{0} g d (h_{1}+h_{2})}{h_{1} U}
$\Delta E_{p} = ...$

---

## 10. cal_problem_00128 / prob_3b609192383fdf1b3340f3bd

- `decision`: `review`
- `title`: `PhysReason 开放题`
- `rewrite_strategy`: `keep_open`

### 原题

A horizontal metal ring with a radius of $r=0.2\mathsf{m}$ is fixed. Two metal rods, each with a length of $r$ and a resistance of $R_{0}$, are placed along the diameter of the ring. One end of each rod is in good contact with the ring, and the other end is connected to the corresponding plate/part of the device. Under the given magnetic/electric conditions, determine the related physical quantities.

### 原答案

0.54C, plate M becomes positively charged
0.16C
0.14m

### 改写后题目

A horizontal metal ring with a radius of $r=0.2\mathsf{m}$ is fixed. Two metal rods, each with a length of $r$ and a resistance of $R_{0}$, are placed along the diameter of the ring. One end of each rod is in good contact with the ring, and the other end is connected to the corresponding plate/part of the device. Under the given magnetic/electric conditions, determine the related physical quantities.

### 改写后参考答案

0.54C, plate M becomes positively charged
0.16C
0.14m

---
