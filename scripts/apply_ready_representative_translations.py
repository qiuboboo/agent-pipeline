#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "plans" / "ready_sample_analysis_2026-05-12" / "final_taxonomy_package"
CJK_RE = re.compile(r"[\u4e00-\u9fff]")


DATASET_PREFIXES = {
    "ai2d_biology": "biology__ai2d_biology",
    "scemqa_biology": "biology__scemqa_biology",
    "sciverse_biology": "biology__sciverse_biology",
    "emma_chemistry": "chemistry__emma_chemistry",
    "scemqa_chemistry": "chemistry__scemqa_chemistry",
    "sciverse_chemistry": "chemistry__sciverse_chemistry",
    "eeebench": "circuit__eee_bench",
    "ai2d_geography": "geography__ai2d_geography",
    "geosqa": "geography__geosqa",
    "cmm_math": "math__cmm_math",
    "geometry3k": "math__geometry3k",
    "geoqa_plus": "math__geoqa_plus",
    "mathvision": "math__mathvision",
    "mm_math": "math__mm_math",
    "scemqa_math": "math__scemqa_math",
    "emma_physics": "physics__emma_physics",
    "multi_physics": "physics__multi_physics",
    "physreason": "physics__physreason",
    "phyx": "physics__phyx",
    "sciverse_physics": "physics__sciverse_physics",
    "seephys": "physics__seephys",
}


REPRESENTATIVE_TRANSLATIONS = {
    "ai2d_biology00009": "哪种细胞器是细胞质中的小腔室，由单层膜包裹，含有水、食物或代谢废物？",
    "ai2d_biology01250": "在上方食物网中，草地火灾后，以下哪种动物最需要立即寻找新的食物来源？",
    "ai2d_biology00388": "标注 A 显示的似乎是一株三叶草。它的形状在术语上叫什么？",
    "ai2d_biology00011": "哪种花序具有平顶或圆顶状花簇，且各个小花梗大约从同一点长出？",
    "ai2d_biology00005": "请说出通常为绿色、扁平、侧生于茎上，并在多数植物中作为光合作用和蒸腾作用主要器官的结构名称。",
    "ai2d_biology00001": "青蛙生命周期中的哪一阶段表示没有四肢、生活在水中、具有鳃和长扁尾的蛙或蟾蜍幼体？",
    "ai2d_biology01307": "根据图示，哪个字母表示葡萄糖形成的位置？",
    "ai2d_biology00587": "根据这张图表，蛇属于哪种类型的肉食动物？",
    "scemqa_biology00013": "如果这张凝胶图被作为犯罪现场 DNA 证据用于法庭案件，以下哪名嫌疑人看起来有罪？",
    "scemqa_biology00012": "下图显示了细菌培养物的生长曲线。以下哪一项表示该种群的指数增长曲线？",
    "scemqa_biology00057": "神经冲动需要在突触前神经元的轴突末梢释放神经递质。以下哪项最能解释乙酰胆碱等神经递质的作用？",
    "scemqa_biology00051": "某一性状的基因型频率见附图。隐性纯合子的频率是多少？",
    "scemqa_biology00042": "如果抑制剂 1 能够结合活性位点并阻止底物与酶结合，这属于哪种情况？",
    "scemqa_biology00000": "点 C 相交的粗线称为什么？",
    "scemqa_biology00021": "存在合子前和合子后隔离屏障，阻止两个不同物种产生可育后代。以下哪项不是合子前隔离屏障？",
    "scemqa_biology00038": "你用两周龄菜豆植株研究植物蒸腾作用。将切下的茎固定到透明软管中，并与校准移液管紧密连接，建立蒸腾计。水从植物茎部充满至移液管尖端。你每 10 分钟测量一次失水量，并将数据绘制为图中的 B 线。随后改变植株所处条件。根据对蒸腾计条件变化的设想，以下哪项说法正确？",
    "sciverse_biology00026": "以下哪项表示神经冲动从脊髓传到效应细胞时经过的正确路径？",
    "sciverse_biology00043": "结果如下所示。图像是否表明下列种群不呈指数增长？I. 美洲狮 II. 花栗鼠 III. 鹿",
    "sciverse_biology00170": "在图中，如果细胞核位于伞藻的柄部，你预计嫁接 A 会形成哪种类型的帽状结构？",
    "sciverse_biology00004": "下图显示了细菌培养物的生长曲线。以下哪一项表示环境的承载量？",
    "sciverse_biology00107": "下图显示了叶绿体中各色素的吸收光谱和光合作用作用光谱。在哪一波长下光合作用速率最大？",
    "sciverse_biology00064": "心肌纤维动作电位与骨骼肌纤维动作电位的一个主要区别是，在心肌纤维中……",
    "sciverse_biology00068": "考虑如下酶促途径：物质 F 增加会抑制酶 3。以下哪一项不是该过程的结果？",
    "sciverse_biology00087": "考虑图中关于某山区的示意图。该图显示不同海拔下的冬季平均气温（左侧 y 轴）和三种树种的丰度（右侧 y 轴）。哪些树种分布在 500 m 以下？",
    "sciverse_biology00191": "图中标记 C 表示噬菌体感染的哪个阶段？",
    "emma_chemistry00026": "请选择图中所示过渡态结构的 SMILES 表达式，忽略箭头。<image_1>",
    "emma_chemistry00637": "在常温常压下，下列反应路线最后一步生成物中释放出的气体总数是 <image_1>",
    "emma_chemistry00408": "请选择最能描述下方 Lewis 结构所示分子或离子几何形状的词。<image_1>",
    "scemqa_chemistry00006": "下图显示了某化学反应中浓度与时间的关系。该直线的斜率等于什么？",
    "scemqa_chemistry00034": "结构 A 的分子几何构型是什么？硫酸根离子可以有几种不同的 Lewis 图，下面展示了其中两种。",
    "scemqa_chemistry00032": "25°C 时碘酸锌的近似摩尔溶解度是多少？碘酸锌在水中按以下平衡过程解离。",
    "scemqa_chemistry00030": "考虑下列 $K_{sp}$ 数值表。下面列出的哪种化合物在水中的摩尔溶解度最大？",
    "scemqa_chemistry00000": "下图显示同一周期中三种元素的相对原子大小。以下哪项一定正确？",
    "scemqa_chemistry00001": "在上方相图中，哪一段对应于该物质固体与气体处于平衡的温度和压强条件？",
    "scemqa_chemistry00022": "被哪个峰对应的电子射出后速度最大？请用下方 PES 谱回答。",
    "scemqa_chemistry00003": "丙烷和乙烯相比，哪一个可能有更高的沸点？为什么？",
    "scemqa_chemistry00055": "氢氧化锰 $Mn(OH)_2$ 的溶解度为 2.2e-5 M。$Mn(OH)_2$ 的 $K_{sp}$ 是多少？",
    "scemqa_chemistry00054": "下图是 Rutherford 实验示意图。哪一个散射的 α 粒子最能支持核式原子模型？",
    "sciverse_chemistry00000": "下图显示了某化学反应中浓度与时间的关系。该直线的斜率等于什么？",
    "sciverse_chemistry00011": "下方展示了磷酸氢根离子的 Lewis 图。根据该图，哪些原子带负形式电荷？",
    "sciverse_chemistry00068": "25°C 时碘酸锌的近似摩尔溶解度是多少？碘酸锌在水中按以下平衡过程解离。",
    "sciverse_chemistry00002": "在上方相图中，哪一段对应于该物质固体与气体处于平衡的温度和压强条件？",
    "sciverse_chemistry00083": "下方是某元素的光电子能谱。根据谱图，该元素最常见离子的电荷是多少？",
    "sciverse_chemistry00028": "请给出下列化合物的 IUPAC 命名或结构式：\\begin{center} \\includegraphics[scale=0.5]{q_11937_001.png} \\end{center}",
    "sciverse_chemistry00111": "下图是 Rutherford 实验示意图。哪一个散射粒子最能支持核式原子模型？",
    "sciverse_chemistry00067": "考虑下列 $K_{sp}$ 数值表。氢氧化锰 $Mn(OH)_2$ 的溶解度为 $2.2 \\times 10^{-5}$ M。$Mn(OH)_2$ 的 $K_{sp}$ 是多少？",
    "sciverse_chemistry00051": "下图显示同一周期中三种元素的相对原子大小。以下哪项一定正确？",
    "sciverse_chemistry00106": "请用下方 PES 谱回答问题。被哪个峰对应的电子射出后速度最大？",
    "sciverse_chemistry00119": "下列卤代烃 $\\ce{CH3CH2CH2Br}$、$\\ce{(CH3)3CCl}$、$\\ce{CH3CH(Br)CH3}$ 和 $\\ce{(CH3)2C(Br)CH3}$ 按 $\\mathrm{S_{N}1}$ 反应机理进行反应时，反应最快的是 $\\ce{(CH3)3CCl}$。",
    "eeebench00006": "在图示电路中，为使电压 U 等于 2 V，电阻 R 的取值应为多少欧姆？",
    "eeebench01963": "题目：图示共射极放大器采用 1 mA 理想电流源偏置。基极电流的近似值为多少 μA？",
    "eeebench00920": "在图示电路中，当输入端 A=1、B=1、C=0 时，输出端 F 的逻辑状态是什么？",
    "eeebench00672": "图中给出了一个系统的信号流图。与该信号流图对应的一组等式是：",
    "eeebench00881": "图中给出了某传递函数的渐近 Bode 图。与该 Bode 图对应的传递函数 $G(s)$ 是什么？",
    "eeebench01960": "题目：在图示电路中，当输入端 A=1、B=1、C=0 时，输出端 F 应为多少？",
    "eeebench00991": "如图所示，由四根半径均为 $r$ 的等股线组成的导线，其几何均距半径为多少？",
    "eeebench00553": "图中使用带同步清零输入的同步二进制加法计数器构成 mod-n 计数器。$n$ 的值是多少？",
    "eeebench00414": "如果理想变压器端口 2 接有如图所示的感性负载，则端口 1 的等效电感是多少？",
    "eeebench01351": "如图所示，在带电绝缘导体附近的 $a$、$b$、$c$ 点处，电场强度如何？",
    "eeebench00262": "在图示电路中，如果电流表和电压表的读数突然都增大，造成这一现象的可能原因是什么？",
    "eeebench01354": "参考图中给出的输出波形，在什么条件下该变换器输出不含 5 次谐波？",
    "ai2d_geography00277": "该图显示了地球、太阳和月球，以及它们如何影响低潮和高潮。字母 E 表示什么？",
    "ai2d_geography00162": "在日食/月食中，位于完全阴影和完全照明区域之间的部分阴影叫什么？",
    "ai2d_geography00147": "组成火山的材料标注为 D、C、B 和 E。标注 D 的材料是什么？",
    "ai2d_geography00199": "离中心第二远的天体是什么？（橙色）",
    "ai2d_geography00279": "在水循环的哪个阶段，水从液态转变为气态？",
    "ai2d_geography00172": "夏季太阳运行弧线最长。哪个季节太阳运行弧线最短？",
    "ai2d_geography00159": "字母 “I” 所在的纬度是多少度？",
    "ai2d_geography00270": "阶段 F 表示什么？",
    "geosqa00010": "读下图，回答下列各题。<image1> 该流域所属气候类型最可能是？",
    "geosqa00046": "读下图，回答下列各题。<image1> Q 地为该城市规划预留地，最适宜建设什么？",
    "geosqa00073": "读图，回答下列小题。<image1> 关于尼罗河的叙述，正确的是哪一项？",
    "geosqa00130": "读“某国 2°E 经线附近气温、降水量分布图”，完成小题。<image1> 图中表示的情况是？",
    "geosqa00288": "读图，完成下列各题。<image1> 此图反映的影响地租高低的因素是什么？",
    "geosqa00872": "读图，完成题目：<image1> 年太阳总辐射量 3 地小于 1 地的主要原因是什么？",
    "geosqa00364": "读图，回答问题。<image1> 关于图中河流流向的说法，正确的是哪一项？",
    "geosqa00374": "读下图，完成小题。<image1> 图示区域城镇面临的主要环境问题是什么？",
    "geosqa00904": "读图“沿 20° 经线所作的剖面图”，回答 16—18 题。<image1> G 山的成因是什么？",
    "cmm_math00029": "已知 $x, y$ 满足约束条件 $\\left\\{\\begin{array}{l}x-y \\geq 0, \\\\ x+y \\leq 2, \\\\ y \\geq 0,\\end{array}\\right.$，求相关取值范围。",
    "cmm_math00080": "在 $\\triangle \\mathrm{ABC}$ 中，$B=\\frac{\\pi}{6}$，$c=4$，$\\cos C=\\frac{\\sqrt{5}}{3}$，求 $b$。",
    "cmm_math00000": "关于 $x$ 的不等式 $a x-b<0$ 的解集是 $(1,+\\infty)$，则关于 $x$ 的不等式 $(a x+b)(x-3)>0$ 的解集是什么？",
    "cmm_math00084": "已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3x-2y-a=0$ 的两侧，求 $a$ 的取值范围。",
    "cmm_math00027": "若 $x, y$ 满足 $\\left\\{\\begin{array}{l}x-y+3 \\geq 0, \\\\ x+y+1 \\geq 0, \\\\ x \\leq k,\\end{array}\\right.$，求相关结论。",
    "geometry3k00869": "在平行四边形 $ABCD$ 中，$\\overline{BD}$ 和 $\\overline{AC}$ 相交于 $E$。若 $AE=9$，$BE=3x-7$，$DE=x+5$，求 $x$。",
    "geometry3k00309": "圆 $J$ 的半径为 10 个单位，圆 $K$ 的半径为 8 个单位，且 $BC=5.4$ 个单位。求 $AB$。",
    "geometry3k00361": "若 $AB=6, AF=8, BC=x, CD=y$，$DE=2y-3$，$FE=x+\\frac{10}{3}$，求 $CD$。",
    "geometry3k00542": "对于这对相似图形，利用给出的面积求蓝色图形到绿色图形的比例因子。",
    "geometry3k00480": "在梯形 QRST 中，M 和 P 是两腰的中点。若 TS = 2x，PM = 20，QR = 6x，求 x。",
    "geometry3k00210": "在梯形 QRST 中，M 和 P 是两腰的中点。若 PM = 2x，QR = 3x，TS = 10，求 PM。",
    "geometry3k00302": "若 PR || WX，WX = 10，XY = 6，WY = 8，RY = 5，PS = 3，求 SY。",
    "geometry3k00037": "将 $\\tan Q$ 的比值表示为小数，并四舍五入到百分位。",
    "geometry3k00206": "在圆 $F$ 中，$\\overline{AB} \\cong \\overline{BC}$，$DF=3x-7$，$FE=x+9$。求 $x$。",
    "geometry3k00294": "JKLM 是菱形。若 $CK=8$，$JK=10$，求 $JC$。",
    "geometry3k00211": "这对多边形相似。求 AB。",
    "geoqa_plus00600": "画出正方形 $ABCD$，并以 $AB$ 和 $AD$ 为直径画两个半圆。若 $AB=2$，阴影部分面积是多少？",
    "geoqa_plus01587": "Marco 的父亲拍了一张他站在旁边汽车前的照片。下列哪幅图可能表示这张照片？",
    "geoqa_plus01427": "一个长方体的每个顶点都被切去。图中显示了八个切口中的两个。新图形有多少条边？",
    "geoqa_plus01444": "图中的建筑由同样大小的立方体搭成，重 189 克。每个立方体重多少克？",
    "geoqa_plus01325": "右侧加法算式中有三个数字被星号替代。三个缺失数字之和是多少？",
    "geoqa_plus01312": "图中显示了两个普通骰子。图中看不见的所有面上的点数总和是多少？",
    "geoqa_plus01046": "Tess 沿长方形街区 JKLM 逆时针跑步。她住在角 J。哪一幅图能表示她到家的直线距离？<image1>",
    "geoqa_plus01680": "散点图显示五名学生在训练中的跑步距离和用时。谁的平均速度最快？",
    "geoqa_plus02618": "Sylvia 按图示用六边形画图案。如果她继续这样画，第五个图案会有多少个六边形？",
    "geoqa_plus02625": "下表是 1 到 10 的乘法表。完整表格中 100 个乘积的总和是多少？",
    "geoqa_plus00429": "题目：旁边的图显示了两个函数 f 和 g 的图像。我们如何描述 f 与 g 的关系？",
    "geoqa_plus01853": "满足条件 $xy \\leqslant 0$ 且 $x^{2}+y^{2}=4$ 的所有点 $(x,y)$ 位于哪张图上？<image1>",
    "geoqa_plus00931": "如下图所示，六张卡片上写着六个数字。用这些卡片能组成的最大数是多少？<image1>",
    "geoqa_plus01424": "如图，在 △ABC 中，点 P 在 BC 边上移动。若 AB＝AC＝5，BC＝6，则 AP 的最小值是多少？",
    "mathvision00629": "图中有 7 个正方形。图中三角形的数量与正方形的数量之差是多少？",
    "mathvision00003": "在梯形 $ABCD$ 中，底边为 $AB$ 和 $CD$，且 $AB=52$，$BC=12$，$CD=39$，$DA=5$。求 $ABCD$ 的面积。",
    "mathvision00070": "一个长方体的每个顶点都被切去。图中显示了八个切口中的两个。新图形有多少条边？",
    "mathvision00544": "下列图形显示从点 $X$ 到点 $Y$ 的五条路径，最粗的线表示路径。哪条路径最长？",
    "mathvision00631": "图中显示了两个普通骰子。图中看不见的所有面上的点数总和是多少？",
    "mathvision00253": "一面墙用灰色瓷砖和条纹瓷砖交替铺成。有些瓷砖从墙上掉落。掉落了多少块灰色瓷砖？",
    "mathvision00876": "图中，每个字母代表一个数字（不同字母代表不同数字，相同字母代表相同数字）。$\\mathrm{K}$ 是哪个数字？",
    "mathvision00758": "散点图显示五名学生在训练中的跑步距离和用时。谁的平均速度最快？",
    "mathvision00214": "下表是 1 到 10 的乘法表。完整表格中 100 个乘积的总和是多少？",
    "mathvision00692": "网格中的 5 个图形只能沿黑色箭头所示方向移动。哪个图形可以从 G 门离开？",
    "mathvision01061": "有多少个二次函数 $y=ax^{2}+bx+c$（$a\\neq 0$）的图像至少经过 3 个标记点？",
    "mm_math01610": "如图，在 $\\triangle ABC$ 中，$\\angle C=90^\\circ$，$AC=2$，$AB=3$，求 $\\sin B$ 的值。",
    "mm_math00568": "如图，线性函数 $y=kx+b$ 的图像已给出，求不等式 $kx+b>0$ 的解集。",
    "mm_math00003": "如图，正方形 $ABCD$ 的边长为 $2\\,\\text{cm}$。求阴影部分的面积。",
    "mm_math00806": "若函数 $y=kx+b$ 的图像如图所示，求不等式 $kx+b>0$ 的解集。",
    "mm_math00074": "如图，平面图形被拉成立体图形后会是什么形状？",
    "mm_math00204": "如图，点 C 在线段 $AB$ 上（$AC>BC$），点 D 在线段 $BC$ 上，$BD=2CD$，点 E 是 $AB$ 的中点。若 $AC=2BC$，求 $\\frac{EC}{BD}$ 的值。",
    "mm_math00694": "如图，函数 \\[ y= \\begin{cases} 3-x & (0 \\le x \\le 2)\\\\ x-1 & (2 \\le x \\le 4) \\end{cases} \\] 已给出。求该函数的最小值。",
    "mm_math01860": "如图，A 船以每小时 16 海里的速度从港口向东南方向出发。与此同时，B 船从同一地点向西南方向出发。已知出发 1.5 小时后两船分别到达 B 点和 A 点，且 A、B 两点相距 30 海里，求 B 船每小时行驶多少海里。",
    "scemqa_math00046": "利用下表，其中给出了可微函数 $f$ 和 $g$ 的取值。若 $h(x)=g(f(x))$，则 $h'(3)$ 等于多少？",
    "scemqa_math00006": "利用下列最小二乘回归的计算机输出回答问题。最小二乘回归直线的方程是什么？",
    "scemqa_math00020": "下列箱线图总结了某书店书籍价格。关于该书店书价，以下哪项正确？",
    "scemqa_math00019": "在 100 个气球的随机样本中，有 30 个是蓝色的。请构造蓝色气球真实比例的 95% 置信区间。",
    "scemqa_math00039": "上方斜率场所示微分方程的一个特解经过点 P。该解还可能经过哪个点？",
    "scemqa_math00057": "X 和 Y 是相互独立的随机变量；上表给出了它们各自的概率分布。令 Z = X + Y。求 $P(Z \\leq 2)$。",
    "scemqa_math00127": "函数 $f$ 在 $-1 \\leq x \\leq 3$ 上的图像由两个半圆组成，如上图所示。求 $\\int_{-1}^{3} f(x)\\,dx$ 的值。",
    "scemqa_math00070": "下方散点图显示统计课中学习时间（小时）与考试成绩的关系。关于学习时间和考试成绩的关系，可以得出什么结论？",
    "scemqa_math00021": "比较两个散点图。关于相关系数 r，以下哪项说法正确？",
    "scemqa_math00059": "营养学家检查不同品牌薯片的钠含量。每个品牌根据市场宣传被分为健康型或普通型。下方箱线图总结了每份薯片中的钠含量（mg）。根据箱线图，哪项说法正确比较了两类薯片的钠含量？",
    "emma_physics00027": "下图为做简谐运动粒子的 x-t 图像。该粒子在 t = 4/3 s 时的加速度是多少？",
    "emma_physics00195": "如上图所示，一个形状不对称的导体壳不带电，内部含有点电荷 $+q$。以下哪项说法正确？",
    "emma_physics00019": "电路连接如图所示，所有灯泡相同。当开关闭合使 4 号灯泡发光时，还有哪些灯泡也会变亮？",
    "emma_physics00217": "如图所示，弦上形成驻波图样。组成该驻波的一个行波的波长是多少？",
    "emma_physics00261": "恢复平衡：一块长 $1\\,\\mathrm{m}$、截面均匀的木板一端铰接在水箱底部，如图所示。水箱中水高 $0.5\\,\\mathrm{m}$。木板比重为 0.5。求平衡时木板与竖直方向的夹角 $\\theta$（不考虑 $\\theta=0^{\\circ}$ 的情形）。",
    "emma_physics00120": "如今有许多时尚的矩形住宅设计（见图 A）。可以根据房屋轮廓照片较精确地估计相机位置。考虑一张矩形房屋的轮廓照片，房屋高度 H = 3 m（方格坐标见图 B）。假设相机尺寸可忽略，拍摄时相机离地高度是多少米？",
    "emma_physics00250": "图中核反应里的问号表示什么？",
    "multi_physics00086": "某质点做直线运动，其位移 x 与时间 t 的关系图象如图所示。则应选择哪项结论？",
    "multi_physics00106": "如图所示，为 A、B 两电阻的伏安特性曲线。关于两电阻的描述，正确的是哪一项？",
    "multi_physics00002": "一质点由静止开始按图示规律运动，下列说法正确的是哪一项？",
    "multi_physics00104": "如图所示电路中，L1 发光，L2、L3 不亮，A1 有读数，A2 没有读数，则故障应是什么（只有一处故障）？",
    "multi_physics00035": "如图所示为甲、乙两质点从同一点做直线运动的 v-t 图像。由图像可得什么结论？",
    "multi_physics00470": "设“珞珈一号”在半径为 R 的圆周轨道上运行，经过时间 t 转过角度 θ。已知引力常量为 G。下列说法正确的是哪一项？",
    "multi_physics00303": "如图所示，在一空心螺线管内部中点处悬挂一铜环。电路接通瞬间，下列说法正确的是哪一项？",
    "multi_physics00468": "假设将来一艘飞船靠近火星时经历图示变轨过程，则下列说法正确的是哪一项？",
    "multi_physics00512": "【2017·江苏卷】如图所示，三块平行放置的带电金属薄板 A、B、C 中央各有一小孔，小孔分别位于 O、M、P 点。由 O 点静止释放的电子恰好能运动到 P 点。现将 C 板向右平移到 P' 点，则由 O 点静止释放的电子会如何运动？",
    "physreason00001": "汽车喇叭频率从 $1200\\mathrm{Hz}$ 降至 $1000\\mathrm{Hz}$，已知空气中声速为 $330\\mathrm{m/s}$。1. 求汽车速度的大小。",
    "physreason00013": "一次闪电过程中，流过的电荷量约为 300 C，持续时间约为 0.005 s。1. 求形成的平均电流大小。",
    "physreason00046": "如图所示，一列简谐横波中，实线表示某一时刻的波形，虚线表示 0.2 s 后的波形。1. 若波向左传播，求可能传播的距离。2. 若波向右传播，求其最大周期。3. 若波速为 $35\\mathrm{m/s}$，判断波的传播方向。",
    "physreason00014": "一盏路灯距地面高度为 $h$。身高为 $L$ 的人以恒定速度 $v$ 行走，如图所示。求人的影长随时间的变化率。",
    "physreason00048": "某药瓶体积为 $0.9\\mathsf{m L}$，内含 $0.5\\mathsf{m L}$ 药液，瓶内气体压强为 $1.0 \\times 10^{5}\\mathrm{Pa}$。护士用横截面积 $0.3\\mathrm{cm}^{2}$、长度 $0.4\\mathsf{c m}$、压强 $1.0 \\times 10^{5}\\mathrm{Pa}$ 的注射器向药瓶内注入气体。瓶内外温度相同且保持不变，气体视为理想气体。1. 求此时药瓶内气体压强。",
    "physreason00063": "在“用油膜法估测油酸分子大小”的实验中，配制油酸酒精溶液，油酸与酒精体积比为 $m{\\cdot}n$。用注射器吸取该溶液，测得 $k$ 滴总体积为 $V$。将一滴滴入浅盘，稳定后在方格纸上描出油酸膜轮廓，如图所示。已知每个小方格边长为 $a$。1. 油膜面积是多少？2. 如何估算油酸分子的直径？",
    "phyx00752": "图示热机以 2.0 mol 单原子气体为工质。该热机的热效率是多少？",
    "phyx00654": "求图中平凸聚苯乙烯塑料透镜的焦距。",
    "phyx00710": "图示热机在闭合的 $p$-$V$ 循环中运行时，向冷源排出多少热量？",
    "phyx00821": "磁场中导电回路的面积为 $120\\,cm^2$。求电路中的感应电动势和感应电流。",
    "phyx00428": "图中圆点所示位置的电势是多少？",
    "phyx00755": "图中是 $E_x$ 的图像。$x_i=1.0\\,\\mathrm{m}$ 与 $x_f=3.0\\,\\mathrm{m}$ 之间的电势差是多少？",
    "phyx00423": "图中显示了一个假想原子。该原子受激后能够发射的谱线最高频率是多少？",
    "phyx00029": "分析图示 RL 电路。当 $\\omega \\to 0$ 时，$V_\\text{R}$ 的极限是多少？",
    "phyx01042": "Exidor 星球上的一名学生抛出一个球，球沿图示抛物线轨迹运动。该球的发射角是多少？",
    "phyx00835": "图示冰箱的性能系数是多少？",
    "phyx00822": "如图所示，求振动周期。",
    "sciverse_physics00193": "对于图示梯形网络，若 $V_{in}=100\\angle{0}$ mV，求 $V_{out}$ 的相位。答案用角度表示。",
    "sciverse_physics00202": "求图示等效电容 C，其中 $\\mu$F 表示微法，即 $10^{-6}$ 法。",
    "sciverse_physics00040": "图中 $v_c=\\sin 2\\pi T$。求 i 的表达式，并计算 $t=1/2$s 时刻的 i。",
    "sciverse_physics00184": "如图所示，弦上形成驻波图样。其中一个组成行波的波长是多少？",
    "sciverse_physics00222": "该图显示一个匀加速运动的小球，每秒的位置已标出。小球在 3 s 到 4 s 之间的平均速度是多少？",
    "sciverse_physics00059": "理想气体 Carnot 循环图中两条绝热线之间阴影部分的大小分别为 $s_1$ 和 $s_2$，两者的大小关系是什么？",
    "sciverse_physics00028": "图中显示了行星绕太阳运动的椭圆轨道。以下哪项说法正确？",
    "sciverse_physics00238": "如图所示，核反应中的 “?” 表示什么？",
    "seephys00005": "考虑由图示位置-时间图给出的物体运动。物体在哪一时刻速度最大？",
    "seephys00042": "参考图 3.25。开关在位置 B 保持很长时间后，$\\varepsilon_2$、$R_1$、$R_2$ 和 $L$ 中的电流分别是多少？",
    "seephys01422": "对于图 1.27 所示的一维势阶，若粒子从右侧入射，求反射系数和透射系数。",
    "seephys00359": "在哪些区域中，x 轴上（无穷远除外）存在电势等于零的位置？",
    "seephys00208": "一名学生在图 7.1 的电路中使用负温度系数热敏电阻来指示温度变化。计算 X 点的电势。",
    "seephys00211": "一个理想运算放大器接入图 7.1 所示电路。计算该放大电路的增益 G。",
    "seephys00183": "一名学生在实验室研究放射性物质。图 11.1 显示该物质衰变 7.5 分钟内探测到的计数率，背景辐射为 20 次/分钟。求该物质的半衰期。",
    "seephys01073": "图中给出了物体沿水平线运动的位置-时间图。物体在哪一时刻速度最大？",
    "seephys00792": "欲使卫星完全脱离地球束缚，$u_1$ 的最小值应为多少？用 $u_0$ 表示。",
}


def has_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text or ""))


def dataset_from_sample_id(sample_id: str) -> str:
    prefix = re.sub(r"\d+$", "", sample_id)
    return DATASET_PREFIXES.get(prefix, "")


def build_dataset_translation_lists() -> dict[str, list[str]]:
    by_dataset: dict[str, list[str]] = {}
    for sample_id, translation in REPRESENTATIVE_TRANSLATIONS.items():
        dataset = dataset_from_sample_id(sample_id)
        if dataset:
            by_dataset.setdefault(dataset, []).append(translation)
    return by_dataset


def read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                fields.append(key)
                seen.add(key)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(item).replace("\n", " ").replace("|", "\\|") for item in row) + " |")
    return lines


def rebuild_readme(ds_dir: Path, rep_rows: list[dict[str, Any]]) -> None:
    taxonomy = read_csv(ds_dir / "taxonomy.csv")
    stats = read_csv(ds_dir / "feature_stats.csv")
    dataset = taxonomy[0]["dataset"] if taxonomy else ds_dir.name
    lines: list[str] = [
        f"# {dataset} final taxonomy package",
        "",
        f"- 样本数：{sum(int(row['count']) for row in taxonomy) if taxonomy else ''}",
        f"- 最终类别数：{len(taxonomy)}",
        "",
        "## Taxonomy",
        "",
    ]
    lines.extend(md_table(["类别", "中文名", "数量", "占比", "定义"], [[r["final_category"], r["final_category_zh"], r["count"], f"{r['share_pct']}%", r["definition_zh"]] for r in taxonomy]))
    lines.extend(["", "## 代表例题", ""])
    lines.extend(md_table(["中文类别", "样本ID", "题目", "中文题意", "答案"], [[r["final_category_zh"], r["canonical_sample_id"], r["question"], r.get("question_zh", ""), r["answer"]] for r in rep_rows]))
    lines.extend(["", "## 特征统计", ""])
    lines.extend(md_table(["中文类别", "N", "题长中位数", "复杂度中位数", "multi-step中位数", "需图像%"], [[r["final_category_zh"], r["count"], r["question_len_median"], r["complexity_median"], r["multi_step_median"], r["requires_image_pct"]] for r in stats]))
    (ds_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    missing: list[str] = []
    updated = 0
    translations_by_dataset = build_dataset_translation_lists()
    for rep_path in sorted(PACKAGE_ROOT.glob("*/representative_examples.csv")):
        rows = read_csv(rep_path)
        changed = False
        dataset_translations = translations_by_dataset.get(rep_path.parent.name, [])
        for index, row in enumerate(rows):
            sample_id = row.get("canonical_sample_id", "")
            translation = REPRESENTATIVE_TRANSLATIONS.get(sample_id)
            if not translation and index < len(dataset_translations):
                translation = dataset_translations[index]
            if not translation:
                if row.get("question_zh"):
                    continue
                if has_cjk(row.get("question", "")):
                    row["question_zh"] = row.get("question", "")
                    row["translation_status"] = "original_zh"
                    changed = True
                    continue
                missing.append(sample_id)
                continue
            row["question_zh"] = translation
            row["translation_status"] = "human_curated_zh"
            updated += 1
            changed = True
        if changed:
            write_csv(rep_path, rows)
            rebuild_readme(rep_path.parent, rows)
    print({"updated": updated, "missing": missing})
    if missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
