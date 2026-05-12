# math\mm_math final taxonomy package

- 样本数：4229
- 最终类别数：8

## Taxonomy

| 类别 | 中文名 | 数量 | 占比 | 定义 |
| --- | --- | --- | --- | --- |
| geometry_angle_chasing | 几何角度追踪 | 3510 | 83.0% | 需要运用“几何角度追踪”相关知识或解法的题目。 |
| coordinate_geometry_transform | 坐标几何与变换 | 407 | 9.62% | 需要运用“坐标几何与变换”相关知识或解法的题目。 |
| geometry_length_area_volume | 几何长度、面积与体积 | 276 | 6.53% | 需要运用“几何长度、面积与体积”相关知识或解法的题目。 |
| algebra_equation_inequality | 代数方程与不等式 | 27 | 0.64% | 需要运用“代数方程与不等式”相关知识或解法的题目。 |
| visual_spatial_puzzle | 视觉空间与拼图推理 | 5 | 0.12% | 需要运用“视觉空间与拼图推理”相关知识或解法的题目。 |
| math_other | 数学综合题 | 2 | 0.05% | 需要运用“数学综合题”相关知识或解法的题目。 |
| linear_programming_constraints | 线性规划与约束最值 | 1 | 0.02% | 需要运用“线性规划与约束最值”相关知识或解法的题目。 |
| measurement_time_units | 时间、单位与度量 | 1 | 0.02% | 需要运用“时间、单位与度量”相关知识或解法的题目。 |

## 代表例题

| 中文类别 | 样本ID | 题目 | 中文题意 | 答案 |
| --- | --- | --- | --- | --- |
| 几何角度追踪 | mmmath00361 | As shown in the figure, in $\triangle ABC$, $\angle C=90^\circ$, $AC=2$, and $AB=3$, what is the value of $\sin B$? | 如图，在 $\triangle ABC$ 中，$\angle C=90^\circ$，$AC=2$，$AB=3$，求 $\sin B$ 的值。 | $\frac{2}{3}$ |
| 坐标几何与变换 | mmmath00109 | As shown in the graph of the linear function $y=kx+b$, what is the solution set of the linear inequality $kx+b>0$? | 如图，线性函数 $y=kx+b$ 的图像已给出，求不等式 $kx+b>0$ 的解集。 | \textbf{Solution:} From the graph, it is known that $y$ decreases as $x$ increases, and when $x<2$, the line is above the x-axis,\\ therefore, the solution set for $kx+b>0$ is $\boxed{x<2}$. |
| 几何长度、面积与体积 | mmmath00398 | As shown in the figure, the side length of the square $ABCD$ is $2\, \text{cm}$. What is the area of the shaded region? | 如图，正方形 $ABCD$ 的边长为 $2\,\text{cm}$。求阴影部分的面积。 | \textbf{Solution:} It is known from symmetry that $S_{\text{shaded area}} = \frac{1}{2}S_{\text{square} ABCD} = \frac{1}{2} \times 2 \times 2 = \boxed{2}\text{cm}^2$ |
| 代数方程与不等式 | mmmath02519 | If the graph of the function $y=kx+b$ is shown in the figure, what is the solution set of the inequality $kx+b>0$? | 若函数 $y=kx+b$ 的图像如图所示，求不等式 $kx+b>0$ 的解集。 | $x<2$ |
| 视觉空间与拼图推理 | mmmath03709 | As shown in the figure, what will be the shape after the planar figure is pulled into a three-dimensional form? | 如图，平面图形被拉成立体图形后会是什么形状？ | pentagonal prism |
| 数学综合题 | mmmath03879 | As shown in the figure, point C is a point on segment $AB$ ($AC>BC$), D is on segment $BC$, $BD=2CD$, and point E is the midpoint of $AB$. If $AC=2BC$, find the value of $\frac{EC}{BD}$. | 如图，点 C 在线段 $AB$ 上（$AC>BC$），点 D 在线段 $BC$ 上，$BD=2CD$，点 E 是 $AB$ 的中点。若 $AC=2BC$，求 $\frac{EC}{BD}$ 的值。 | \textbf{Solution:} From the given information, we have $BC=CD+BD=3x$, $AC=2BC=6x$, \[\therefore AB=3x+6x=9x,\] \[\because \text{E is the midpoint of } AB,\] \[\therefore EB=\frac{1}{2}AB=4.5x,\] \[\therefore EC=EB-BC=1.5x,\] \[\therefore \frac{EC}{BD}=\frac... |
| 线性规划与约束最值 | mmmath01183 | As shown in the graph, the function \[ y= \begin{cases} 3-x & (0 \le x \le 2)\\ x-1 & (2 \le x \le 4) \end{cases} \] is illustrated. What is the minimum value of this function? | 如图，函数 \[ y= \begin{cases} 3-x & (0 \le x \le 2)\\ x-1 & (2 \le x \le 4) \end{cases} \] 已给出。求该函数的最小值。 | 1 |
| 时间、单位与度量 | mmmath00731 | As shown in the figure, ship A leaves the port at a speed of 16 nautical miles per hour, heading southeast. At the same time and from the same location, ship B heads southwest. It is known that one and a half hours after leaving the port, they reach points B and A respectively. Given that the distance between points A and B is 30 nautical miles, how many nautical miles does ship B travel per hour? | 如图，A 船以每小时 16 海里的速度从港口向东南方向出发。与此同时，B 船从同一地点向西南方向出发。已知出发 1.5 小时后两船分别到达 B 点和 A 点，且 A、B 两点相距 30 海里，求 B 船每小时行驶多少海里。 | \textbf{Solution:} As shown in the diagram: $OA = 16 \times 1.5 = 24$ (nautical miles),\\ $AB = 30$ (nautical miles),\\ By the Pythagorean theorem, we have: $OB = \sqrt{30^2 - 24^2} = 18$ (nautical miles),\\ $18 \div 1.5 = \boxed{12}$ (nautical miles/hour),... |

## 特征统计

| 中文类别 | N | 题长中位数 | 复杂度中位数 | multi-step中位数 | 需图像% |
| --- | --- | --- | --- | --- | --- |
| 几何角度追踪 | 3510 | 44.0 | 7.895 | 0.41 | 96.95 |
| 坐标几何与变换 | 407 | 50.0 | 7.906 | 0.437 | 91.15 |
| 几何长度、面积与体积 | 276 | 42.0 | 7.387 | 0.401 | 93.12 |
| 代数方程与不等式 | 27 | 39.0 | 7.563 | 0.41 | 96.3 |
| 视觉空间与拼图推理 | 5 | 19.0 | 6.796 | 0.311 | 100.0 |
| 数学综合题 | 2 | 61.5 | 8.392 | 0.439 | 100.0 |
| 线性规划与约束最值 | 1 | 36.0 | 9.011 | 0.545 | 100.0 |
| 时间、单位与度量 | 1 | 77.0 | 8.744 | 0.347 | 100.0 |
