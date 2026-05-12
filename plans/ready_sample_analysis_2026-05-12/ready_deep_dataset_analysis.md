# Ready 样本深度特征分析

本报告基于规则初分标签和结构化特征表，目标是判断每个数据集的题型多样性、集中度、长度/复杂度分布和代表样本。

## 数据集多样性排名

| Dataset | Effective Categories | Top1 | Top1 % | Top3 % | Label |
| --- | --- | --- | --- | --- | --- |
| geography\geosqa | 7.84 | climate_weather_seasons | 21.17 | 54.75 | diverse |
| chemistry\sciverse_chemistry | 7.51 | stoichiometry_reaction_calculation | 24.7 | 61.94 | diverse |
| math\scemqa_math | 6.72 | geometry_length_area_volume | 23.28 | 60.85 | diverse |
| chemistry\scemqa_chemistry | 6.54 | stoichiometry_reaction_calculation | 28.83 | 72.07 | diverse |
| circuit\eee_bench | 6.42 | dc_ac_network_analysis | 34.5 | 66.53 | diverse |
| biology\scemqa_biology | 4.77 | cell_molecular_genetics | 43.75 | 81.25 | moderately_concentrated |
| math\mathvision | 4.65 | geometry_angle_chasing | 48.32 | 83.98 | moderately_concentrated |
| physics\phyx | 4.59 | mechanics_kinematics_dynamics | 44.42 | 75.07 | moderately_concentrated |

## 高集中度数据集

| Dataset | Dominant Category | Top1 % | Effective Categories | N |
| --- | --- | --- | --- | --- |
| chemistry\emma_chemistry | transition_state_smiles_selection | 97.92 | 1.12 | 864 |
| physics\physreason | mechanics_kinematics_dynamics | 87.07 | 1.75 | 905 |
| math\mm_math | geometry_angle_chasing | 83.0 | 1.83 | 4229 |
| physics\emma_physics | mechanics_kinematics_dynamics | 62.03 | 3.2 | 266 |
| physics\sciverse_physics | mechanics_kinematics_dynamics | 61.09 | 3.45 | 239 |
| biology\sciverse_biology | cell_molecular_genetics | 57.53 | 4.3 | 219 |
| math\geometry3k | angle_chasing | 56.88 | 4.28 | 879 |
| physics\multi_physics | mechanics_kinematics_dynamics | 54.86 | 3.34 | 525 |

## 长题和复杂题

| Dataset | Question Len Median | Complexity Median | Node Median | Top1 |
| --- | --- | --- | --- | --- |
| physics\physreason | 140.0 | 11.863 | 16.0 | mechanics_kinematics_dynamics |
| physics\multi_physics | 90.0 | 8.272 | 12.0 | mechanics_kinematics_dynamics |
| biology\sciverse_biology | 78.0 | 8.459 | 11.0 | cell_molecular_genetics |
| physics\sciverse_physics | 75.0 | 8.557 | 12.0 | mechanics_kinematics_dynamics |
| physics\seephys | 75.0 | 8.676 | 13.0 | mechanics_kinematics_dynamics |
| physics\emma_physics | 74.0 | 8.459 | 13.0 | mechanics_kinematics_dynamics |
| biology\scemqa_biology | 61.0 | 7.989 | 14.0 | cell_molecular_genetics |
| geography\geosqa | 58.0 | 8.91 | 14.0 | climate_weather_seasons |

## 总体相关性

| X | Y | Pearson r |
| --- | --- | --- |
| question_unit_len | complexity_index | 0.8247 |
| question_unit_len | node_count | 0.3365 |
| condition_count | node_count | 0.5776 |
| visual_entity_count | multimodal_strength_score | 0.7562 |
| multi_step_score | complexity_index | 0.7606 |
| latex_count | answer_unit_len | 0.4349 |

## 每个数据集详情

### biology\ai2d_biology

- N: `1315`
- 多样性：`moderately_concentrated`；有效类别数 `3.91`；Top1 `cell_molecular_genetics` 占 `43.65%`；Top3 占 `88.75%`
- 题长中位数 `9.0`，复杂度中位数 `5.973`，节点数中位数 `11.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| cell_molecular_genetics | 574 | 43.65 | 8.0 | 5.826 | 0.302 | 100.0 |
| ecology_food_web_population | 426 | 32.4 | 13.0 | 6.307 | 0.302 | 100.0 |
| biology_other | 167 | 12.7 | 7.0 | 5.803 | 0.302 | 100.0 |
| plant_biology | 59 | 4.49 | 7.0 | 5.71 | 0.302 | 100.0 |
| anatomy_physiology | 44 | 3.35 | 10.0 | 6.067 | 0.302 | 100.0 |
| life_cycle_development | 43 | 3.27 | 9.0 | 6.006 | 0.302 | 100.0 |
| experimental_graph_data | 1 | 0.08 | 11.0 | 6.113 | 0.302 | 100.0 |
| biochemistry_enzymes_metabolism | 1 | 0.08 | 10.0 | 6.338 | 0.302 | 100.0 |

代表样本：
- `cell_molecular_genetics` / `ai2d_biology00002`: What is the outermost layer of the cell?
- `ecology_food_web_population` / `ai2d_biology00000`: In the above the diagram below, which shows a partial food web. Which animal or bird is on the top of the food chain?
- `biology_other` / `ai2d_biology00015`: Which animal is not an herbivore?
- `plant_biology` / `ai2d_biology00021`: Which represents a branched cluster of flowers in which the branches are racemes?
- `anatomy_physiology` / `ai2d_biology00016`: Which organism in the diagram is important because it returns nutrients back to the soil?
- `life_cycle_development` / `ai2d_biology00035`: What are some ways in which a grasshopper's life cycle differs from that of a mealworm beetle's?

### biology\scemqa_biology

- N: `64`
- 多样性：`moderately_concentrated`；有效类别数 `4.77`；Top1 `cell_molecular_genetics` 占 `43.75%`；Top3 占 `81.25%`
- 题长中位数 `61.0`，复杂度中位数 `7.989`，节点数中位数 `14.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| cell_molecular_genetics | 28 | 43.75 | 92.5 | 8.45 | 0.448 | 67.86 |
| ecology_food_web_population | 17 | 26.56 | 56.0 | 8.0 | 0.374 | 100.0 |
| anatomy_physiology | 7 | 10.94 | 55.0 | 8.059 | 0.302 | 85.71 |
| experimental_graph_data | 4 | 6.25 | 46.0 | 7.696 | 0.392 | 50.0 |
| plant_biology | 2 | 3.12 | 113.5 | 8.66 | 0.462 | 50.0 |
| biochemistry_enzymes_metabolism | 2 | 3.12 | 23.0 | 6.273 | 0.324 | 50.0 |
| biology_other | 2 | 3.12 | 46.0 | 7.427 | 0.372 | 100.0 |
| evolution_classification | 2 | 3.12 | 30.5 | 6.796 | 0.32 | 50.0 |

代表样本：
- `cell_molecular_genetics` / `scemqabiology00000`: The cell cycle is a series of events in the life of a dividing eukaryotic cell. It consists of four stages: G1, S, G2, and M. The duration of the cell cycle varies from one species to another and from one cell type to another. The G1 phase varies the most. For
- `ecology_food_web_population` / `scemqabiology00004`: On the basis of what happens at the end of this chart, what is the most likely explanation for the population decline after point E?
- `anatomy_physiology` / `scemqabiology00007`: A scientist studies the storage and distribution of oxygen in humans and Weddell seals to examine the physiological adaptations that permit seals to descend to great depths and stay submerged for extended periods. The figure depicts the oxygen storage in both 
- `experimental_graph_data` / `scemqabiology00009`: A student sets up a lab experiment to study the behavior of slugs. She uses a 1-square-meter tray filled with soil and divides it into four quadrants with different conditions. She places 20 slugs in the tray, 5 in each quadrant. After 20 minutes, all 20 slugs
- `plant_biology` / `scemqabiology00005`: Two ecologists, Peter and Rosemary Grant, spent thirty years observing, tagging, and measuring finches (a type of bird) in the Galápagos Islands. They made their observations on Daphne Major—one of the most desolate of the Galápagos Islands. It is an uninhabit
- `biochemistry_enzymes_metabolism` / `scemqabiology00010`: Which of the following points on the preceding energy chart represents the activation energy of the reaction involving the enzyme?

### biology\sciverse_biology

- N: `219`
- 多样性：`moderately_concentrated`；有效类别数 `4.3`；Top1 `cell_molecular_genetics` 占 `57.53%`；Top3 占 `78.54%`
- 题长中位数 `78.0`，复杂度中位数 `8.459`，节点数中位数 `11.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| cell_molecular_genetics | 126 | 57.53 | 81.0 | 8.468 | 0.311 | 100.0 |
| ecology_food_web_population | 31 | 14.16 | 118.0 | 8.657 | 0.302 | 100.0 |
| biology_other | 15 | 6.85 | 23.0 | 7.027 | 0.302 | 100.0 |
| experimental_graph_data | 13 | 5.94 | 31.0 | 7.458 | 0.347 | 100.0 |
| plant_biology | 11 | 5.02 | 108.0 | 8.438 | 0.302 | 100.0 |
| anatomy_physiology | 10 | 4.57 | 42.0 | 7.7 | 0.333 | 100.0 |
| biochemistry_enzymes_metabolism | 7 | 3.2 | 145.0 | 9.151 | 0.356 | 100.0 |
| evolution_classification | 5 | 2.28 | 80.0 | 8.743 | 0.338 | 100.0 |
| life_cycle_development | 1 | 0.46 | 12.0 | 6.183 | 0.302 | 100.0 |

代表样本：
- `cell_molecular_genetics` / `sciversebiology00004`: 这是四种氨基酸的结构示意图:丝氨酸(A)具有极性侧链,赖氨酸(B)带正电荷,谷氨酸(C)带负电荷,甘氨酸(D)具有非极性侧链。  关于这些氨基酸通过质膜溶解的正确陈述是:  A. 丝氨酸(A)可以很容易地通过质膜溶解。 B. 只有赖氨酸(B)和谷氨酸(C)可以轻松地通过质膜溶解。 C. 丝氨酸(A)、赖氨酸(B)和谷氨酸(C)可以很容易地通过质膜溶解。 D. 只有甘氨酸(D)可以轻松地通过质膜溶解。
- `ecology_food_web_population` / `sciversebiology00000`: 在100代的过程中研究了啮齿动物的种群,以检查牙釉质厚度的变化。适应需要高水平加工的食物资源的物种,其牙釉质比吃柔软、易加工食物的物种更厚。根据这一信息和随后的曲线,回答以下问题:  该物种的饮食发生了何种变化?  A. 它的食物资源变得越来越柔软,更容易加工。 B. 它的食物资源越来越困难加工。 C. 种群数量正在增加。 D. 种群数量正在减少。
- `biology_other` / `sciversebiology00060`: 发现三个小岛的群落是一小部分小鼠的家园。研究发现,小鼠下颌开口的角度存在很大变化。图1显示了在这三个小岛上10个位置采集的小鼠样本中,最大下颌开口角度的平均值。下列哪种解释最合理?  A. 较小的下颌角度有利于小鼠在岛上的生存。 B. 较大的下颌角度不利于小鼠在岛上的生存。 C. 较小的下颌角度不利于小鼠在岛上的生存。 D. 较大的下颌角度有利于小鼠在岛上的生存。
- `experimental_graph_data` / `sciversebiology00019`: 学生设置了一个实验室实验,以研究蚯蚓($sl$)的行为。她设置了一个充满土壤的大托盘,尺寸为1平方米,并分为四个象限,每个象限设置了不同的条件。她在托盘中放置20个蚯蚓,每个象限中有5个。5min后,每个象限中仍有5个蚯蚓。以下哪项不是这一发现的可行解释?  A. 蚯蚓还没有时间迁移。 B. 蚯蚓对温度或盐度条件没有偏好。 C. 蚯蚓无法从托盘的一个区域移动到另一个区域。 D. 蚯蚓不喜欢生活在高温区域。
- `plant_biology` / `sciversebiology00012`: 下图显示了细菌培养物的两条生长曲线 A 和 B。根据生长曲线的特征,哪一项最能解释培养物 A 和培养物 B 之间的差异?  A. 培养物 B 起始细菌数量较多 B. 培养物 A 存在竞争性抑制剂 C. 培养物 B 测量频率较低 D. 培养物 A 尚未耗尽生长所需的空间和营养资源
- `anatomy_physiology` / `sciversebiology00111`: During a dive, a Weddell seal's blood flow to the abdominal organs is shut off and oxygen-rich blood is diverted to the eyes, brain, and spinal cord. Which of the following is the most likely reason for this adaptation?

### chemistry\emma_chemistry

- N: `864`
- 多样性：`single_dominant`；有效类别数 `1.12`；Top1 `transition_state_smiles_selection` 占 `97.92%`；Top3 占 `100.0%`
- 题长中位数 `41.0`，复杂度中位数 `7.734`，节点数中位数 `12.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| transition_state_smiles_selection | 846 | 97.92 | 41.0 | 7.749 | 0.37 | 100.0 |
| chemistry_other | 13 | 1.5 | 14.0 | 6.751 | 0.32 | 100.0 |
| molecular_structure_identification | 5 | 0.58 | 29.0 | 7.671 | 0.347 | 100.0 |

代表样本：
- `transition_state_smiles_selection` / `emmachemistry00000`: Please choose the SMILES expression of the transition-state structure shown in the image, ignoring the arrows.
- `chemistry_other` / `emmachemistry00008`: Isomers of hexane, based on their branching, can be divided into three distinct classes as shown in the figure. What is the correct order of their boiling points?
- `molecular_structure_identification` / `emmachemistry00272`: A compound M_pX_q has cubic close packing (ccp) arrangement of X. Its unit cell structure is shown below. The empirical formula of the compound is <image_1>

### chemistry\scemqa_chemistry

- N: `111`
- 多样性：`diverse`；有效类别数 `6.54`；Top1 `stoichiometry_reaction_calculation` 占 `28.83%`；Top3 占 `72.07%`
- 题长中位数 `37.0`，复杂度中位数 `7.768`，节点数中位数 `14.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| stoichiometry_reaction_calculation | 32 | 28.83 | 38.5 | 8.052 | 0.392 | 96.88 |
| molecular_structure_smiles_bonds | 26 | 23.42 | 33.0 | 7.61 | 0.347 | 96.15 |
| equilibrium_kinetics_gas | 22 | 19.82 | 46.5 | 8.454 | 0.423 | 100.0 |
| acid_base_solution | 9 | 8.11 | 32.0 | 7.424 | 0.347 | 88.89 |
| periodic_atomic_bonding | 6 | 5.41 | 17.5 | 6.308 | 0.302 | 100.0 |
| thermochemistry_calorimetry | 6 | 5.41 | 48.0 | 8.64 | 0.392 | 100.0 |
| isomer_stereochemistry_nomenclature | 3 | 2.7 | 60.0 | 9.263 | 0.509 | 66.67 |
| chemistry_other | 3 | 2.7 | 15.0 | 5.074 | 0.302 | 33.33 |
| lab_graph_data_interpretation | 2 | 1.8 | 16.0 | 6.441 | 0.329 | 100.0 |
| electrochemistry_redox | 2 | 1.8 | 41.5 | 7.037 | 0.378 | 50.0 |

代表样本：
- `stoichiometry_reaction_calculation` / `scemqachemistry00003`: Two half-cells are set up as follows:  Half-Cell A: Strip of Cu(s) in $CuNO_3(aq)$  Half-Cell B: Strip of Zn(s) in $Zn(NO_3)_2(aq)$  When the cells are connected according to the following diagram, the following reaction occurs. What will happen in the salt br
- `molecular_structure_smiles_bonds` / `scemqachemistry00000`: The graph below shows the amount of potential energy between two hydrogen atoms as the distance between them changes. At which point in the graph would a molecule of H2 be the most stable?
- `equilibrium_kinetics_gas` / `scemqachemistry00007`: A solution of carbonic acid, $H_2CO_3$, is titrated with sodium hydroxide, NaOH. The following graph is produced. In addition to $OH^-$, what species are present in the solution during section III of the graph?
- `acid_base_solution` / `scemqachemistry00015`: Consider the following table of $K_{sp}$ values. Which compound listed below has the greatest molar solubility in water?
- `periodic_atomic_bonding` / `scemqachemistry00001`: Which of the labeled arrows in the diagram above represents the strongest intermolecular force?
- `thermochemistry_calorimetry` / `scemqachemistry00052`: On the phase diagram above, segment __________ corresponds to the conditions of temperature and pressure under which the solid and the gas of the substance are in equilibrium.

### chemistry\sciverse_chemistry

- N: `247`
- 多样性：`diverse`；有效类别数 `7.51`；Top1 `stoichiometry_reaction_calculation` 占 `24.7%`；Top3 占 `61.94%`
- 题长中位数 `47.0`，复杂度中位数 `7.987`，节点数中位数 `12.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| stoichiometry_reaction_calculation | 61 | 24.7 | 52.0 | 7.823 | 0.356 | 100.0 |
| molecular_structure_smiles_bonds | 49 | 19.84 | 35.0 | 7.518 | 0.347 | 100.0 |
| equilibrium_kinetics_gas | 43 | 17.41 | 60.0 | 8.708 | 0.437 | 100.0 |
| thermochemistry_calorimetry | 31 | 12.55 | 74.0 | 8.504 | 0.383 | 100.0 |
| acid_base_solution | 22 | 8.91 | 38.0 | 7.476 | 0.333 | 100.0 |
| isomer_stereochemistry_nomenclature | 11 | 4.45 | 17.0 | 6.47 | 0.302 | 100.0 |
| lab_graph_data_interpretation | 11 | 4.45 | 57.0 | 8.189 | 0.401 | 100.0 |
| electrochemistry_redox | 7 | 2.83 | 62.0 | 8.144 | 0.347 | 100.0 |
| periodic_atomic_bonding | 6 | 2.43 | 17.5 | 6.198 | 0.302 | 100.0 |
| chemistry_other | 5 | 2.02 | 20.0 | 6.201 | 0.257 | 100.0 |
| organic_reaction_mechanism | 1 | 0.4 | 59.0 | 8.01 | 0.392 | 100.0 |

代表样本：
- `stoichiometry_reaction_calculation` / `sciversechemistry00002`: 一名学生设计了一个实验,以确定铝的比热容。该实验过程如下:将质量为 $5.86\ \mathrm{g}$ 的铝块加热至不同温度,然后将其滴入装有 $25.0\ \mathrm{mL}$ 水的量热计中。下图显示了其中一次试验过程中收集的数据。已知水的比热容为 $4.18\ \mathrm{J/(g\cdot^\circ C)}$,密度为 $1.00\ \mathrm{g/mL}$,请计算该次试验中水吸收的热量(单位:J)。
- `molecular_structure_smiles_bonds` / `sciversechemistry00013`: 乙酰离子的化学式为C$_2$H$_3$O$^-$,并给出了两种可能的Lewis电子点式结构。请使用形式电荷理论,判断左边还是右边的结构更加合理。(答案为单词)
- `equilibrium_kinetics_gas` / `sciversechemistry00007`: 已知反应 $\mathrm{A + 2B \rightarrow 2C}$ 的动力学数据,请根据给定信息计算该反应的速率常数 $k$ 的值,单位为 $\mathrm{m^{-1}s^{-1}}$。
- `thermochemistry_calorimetry` / `sciversechemistry00001`: 已知一个体积为 2 升的密闭容器中,装有氦气和氩气。图中显示了该容器内压强 $p$ 与温度 $T$ 的关系曲线。问该容器中氦气分子的数目是多少?
- `acid_base_solution` / `sciversechemistry00000`: 下列各图常用来说明甲烷分子的结构。哪一种与甲烷分子的真实结构相差较大?  \begin{center} \includegraphics[scale=0.5]{q_11896_001.png} \end{center}
- `isomer_stereochemistry_nomenclature` / `sciversechemistry00006`: 请给出下列化合物的 IUPAC 命名或结构式:  \begin{center} \includegraphics[scale=0.5]{q_11937_001.png} \end{center}

### circuit\eee_bench

- N: `2023`
- 多样性：`diverse`；有效类别数 `6.42`；Top1 `dc_ac_network_analysis` 占 `34.5%`；Top3 占 `66.53%`
- 题长中位数 `33.0`，复杂度中位数 `7.828`，节点数中位数 `13.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| dc_ac_network_analysis | 698 | 34.5 | 35.0 | 7.868 | 0.401 | 98.71 |
| analog_electronics_devices | 368 | 18.19 | 37.0 | 7.948 | 0.401 | 99.46 |
| circuit_other | 280 | 13.84 | 23.0 | 7.332 | 0.365 | 98.93 |
| digital_logic_boolean | 226 | 11.17 | 25.5 | 7.391 | 0.354 | 98.23 |
| signals_systems_filtering | 191 | 9.44 | 44.0 | 8.382 | 0.428 | 96.86 |
| control_systems_transfer_function | 143 | 7.07 | 33.0 | 7.785 | 0.401 | 100.0 |
| sequential_logic_microprocessor | 35 | 1.73 | 31.0 | 7.741 | 0.383 | 100.0 |
| power_machines_transformers | 30 | 1.48 | 36.0 | 7.794 | 0.351 | 100.0 |
| electromagnetics_fields | 24 | 1.19 | 57.0 | 8.181 | 0.441 | 75.0 |
| measurement_instrumentation | 17 | 0.84 | 29.0 | 7.762 | 0.365 | 100.0 |
| power_electronics_converters | 11 | 0.54 | 30.0 | 8.069 | 0.428 | 100.0 |

代表样本：
- `dc_ac_network_analysis` / `eeebench00005`: In the circuit shown in figure, the voltage at point A is ( )
- `analog_electronics_devices` / `eeebench00002`: Calculate current I\(_2\) in this Darlington pair circuit, assuming a typical forward base-emitter junction voltage drop of 0.7 volts for each transistor. The current I\(_2\) is ______ mA.
- `circuit_other` / `eeebench00025`: Answer with a floating-point number to one decimal place. The autocorrelation function \(R_X(\tau)\) of a wide-sense stationary random process \(X(t)\) is shown in the image. The average power of \(X(t)\) is ____________.
- `digital_logic_boolean` / `eeebench00000`: The Boolean function \( f \) implemented in the figure using two-input multiplexers is
- `signals_systems_filtering` / `eeebench00018`: The output voltage of a boost converter circuit is a function of the input voltage and the duty cycle of the switching signal, represented by the variable D (ranging from 0% to 100%), where \(D = \frac{t_{on}}{t_{on} + t_{off}}\). Based on this mathematical re
- `control_systems_transfer_function` / `eeebench00001`: The asymptotic approximation of the log-magnitude versus frequency plot of a minimum phase system with real poles and one zero is shown in the figure. Its transfer function is ______.

### geography\ai2d_geography

- N: `298`
- 多样性：`diverse`；有效类别数 `4.4`；Top1 `earth_sun_moon_space` 占 `39.6%`；Top3 占 `82.89%`
- 题长中位数 `8.0`，复杂度中位数 `5.864`，节点数中位数 `12.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| earth_sun_moon_space | 118 | 39.6 | 9.0 | 5.983 | 0.302 | 100.0 |
| chart_graph_interpretation | 98 | 32.89 | 7.0 | 5.869 | 0.302 | 100.0 |
| geomorphology_geology_hazards | 31 | 10.4 | 7.0 | 5.754 | 0.302 | 100.0 |
| geography_other | 28 | 9.4 | 6.5 | 5.654 | 0.302 | 100.0 |
| hydrology_ocean_rivers | 10 | 3.36 | 8.5 | 5.921 | 0.302 | 100.0 |
| climate_weather_seasons | 8 | 2.68 | 8.5 | 5.869 | 0.302 | 100.0 |
| map_topography_location | 3 | 1.01 | 5.0 | 5.475 | 0.302 | 100.0 |
| agriculture_resources_environment | 2 | 0.67 | 4.5 | 5.516 | 0.302 | 100.0 |

代表样本：
- `earth_sun_moon_space` / `ai2d_geography00001`: Choose the option which is the phase of the moon occurring when it passes between the earth and the sun and is invisible or visible only as a narrow crescent at sunset?
- `chart_graph_interpretation` / `ai2d_geography00000`: What comes after the 1st quarter?
- `geomorphology_geology_hazards` / `ai2d_geography00006`: What cycle is depicted in the given diagram?
- `geography_other` / `ai2d_geography00005`: Which layer does D represent?
- `hydrology_ocean_rivers` / `ai2d_geography00003`: What is the runoff stage?
- `climate_weather_seasons` / `ai2d_geography00038`: What process is labeled B in the diagram?

### geography\geosqa

- N: `1757`
- 多样性：`diverse`；有效类别数 `7.84`；Top1 `climate_weather_seasons` 占 `21.17%`；Top3 占 `54.75%`
- 题长中位数 `58.0`，复杂度中位数 `8.91`，节点数中位数 `14.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| climate_weather_seasons | 372 | 21.17 | 57.5 | 8.892 | 0.373 | 100.0 |
| population_urban_economic | 338 | 19.24 | 64.0 | 9.063 | 0.383 | 100.0 |
| chart_graph_interpretation | 252 | 14.34 | 57.0 | 8.857 | 0.373 | 100.0 |
| map_topography_location | 225 | 12.81 | 55.0 | 8.919 | 0.382 | 100.0 |
| geography_other | 165 | 9.39 | 49.0 | 8.624 | 0.365 | 100.0 |
| earth_sun_moon_space | 135 | 7.68 | 61.0 | 8.953 | 0.374 | 100.0 |
| hydrology_ocean_rivers | 106 | 6.03 | 56.5 | 8.956 | 0.391 | 100.0 |
| agriculture_resources_environment | 101 | 5.75 | 67.0 | 9.102 | 0.391 | 100.0 |
| geomorphology_geology_hazards | 63 | 3.59 | 55.0 | 9.014 | 0.392 | 100.0 |

代表样本：
- `climate_weather_seasons` / `geosqa00002`: 某地理学习小组为了深入了解各种气候类型的分布与成因,做了各种模拟演示。图为某理想区域分布图,结合所学知识回答题。  <image1>  在模拟演示中,当黄赤交角变为0°,如果甲地气候类型在地球上无法再找到.试分析甲地实际所在的半球及其气候类型分别是 ( )
- `population_urban_economic` / `geosqa00000`: 亦庄经济技术开发区是北京市重点发展的三个新卫星城之一,其定位是京津城际发展走廊上的高新技术产业和先进制造业基地。近年来人口数量不断增加。下图为“亦庄城镇人口构成比例图”。读图,回答下列各题。  <image1>  影响亦庄人口迁入的主要因素是
- `chart_graph_interpretation` / `geosqa00005`: 凡是温度在0°C或0°C以下,并含有冰的各种岩(土)称为冻土。读下图“北半球多年冻土分布剖面图”,回答下列问题。  <image1>  图中所示的冻土分布特点是
- `map_topography_location` / `geosqa00003`: 一群旅游爱好者到祖国的大好河山去旅游,右图为他们到达30°N附近一个地区的等高线地形图,图中等高距为100m。读图回答题。  <image1>  山峰5的最大海拔可能为
- `geography_other` / `geosqa00027`: 下图示意我国某山峰植被分布状况。读图完成下列各题。  <image1>  当地马铃薯的栽培高度上限比玉米高的原因主要是马铃薯
- `earth_sun_moon_space` / `geosqa00012`: 下图为某地连续三个月的正午太阳高度角随时间变化示意图(I、II、III各表示一个月),已知该地水平移动的物体向左偏转。读下图,回答下列题。  <image1>  下列说法正确的是

### math\cmm_math

- N: `142`
- 多样性：`diverse`；有效类别数 `4.14`；Top1 `linear_programming_constraints` 占 `38.03%`；Top3 占 `82.39%`
- 题长中位数 `33.0`，复杂度中位数 `5.812`，节点数中位数 `6.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| linear_programming_constraints | 54 | 38.03 | 42.0 | 6.004 | 0.365 | 1.85 |
| geometry_angle_chasing | 42 | 29.58 | 22.0 | 5.476 | 0.374 | 7.14 |
| algebra_equation_inequality | 21 | 14.79 | 41.0 | 5.991 | 0.383 | 0.0 |
| coordinate_geometry_transform | 18 | 12.68 | 29.0 | 5.687 | 0.41 | 0.0 |
| math_other | 7 | 4.93 | 25.0 | 5.457 | 0.338 | 0.0 |

代表样本：
- `linear_programming_constraints` / `cmmmath00000`: 如果实数 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-y+1 \geq 0, \\ y+1 \geq 0, \\ x+y+1 \leq 0,\end{array}\right.$ 则 $2 x-y$ 的最大值为 ( )
- `geometry_angle_chasing` / `cmmmath00003`: 在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\left\{\begin{array}{l}2 x-y-2 \geq 0, \\ x+2 y-1 \geq 0, \\ 3 x+y-8 \leq 0\end{array}\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )
- `algebra_equation_inequality` / `cmmmath00001`: $x$ 的不等式 $a x-b<0$ 的解集是 $(1,+\infty)$, 则关于 $x$ 的不等式 $(a x+b)(x-3)>0$ 的解集是( )
- `coordinate_geometry_transform` / `cmmmath00002`: 已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )
- `math_other` / `cmmmath00005`: 若 $x, y$ 满足 $\left\{\begin{array}{l}x-y+3 \geq 0, \\ x+y+1 \geq 0, \\ x \leq k,\end{array}\right.$

### math\geometry3k

- N: `879`
- 多样性：`moderately_concentrated`；有效类别数 `4.28`；Top1 `angle_chasing` 占 `56.88%`；Top3 占 `78.95%`
- 题长中位数 `11.0`，复杂度中位数 `6.095`，节点数中位数 `12.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| angle_chasing | 500 | 56.88 | 12.0 | 6.093 | 0.302 | 97.0 |
| math_other | 117 | 13.31 | 6.0 | 5.42 | 0.302 | 100.0 |
| circle_arc_chord | 77 | 8.76 | 13.0 | 6.256 | 0.302 | 100.0 |
| area_perimeter | 72 | 8.19 | 13.0 | 6.339 | 0.302 | 94.44 |
| diagram_variable_solving | 41 | 4.66 | 9.0 | 5.788 | 0.302 | 95.12 |
| segment_length | 34 | 3.87 | 14.5 | 6.327 | 0.302 | 91.18 |
| trigonometric_ratio | 21 | 2.39 | 13.0 | 6.044 | 0.257 | 95.24 |
| coordinate_geometry | 12 | 1.37 | 16.5 | 6.605 | 0.369 | 91.67 |
| similarity_congruence | 5 | 0.57 | 8.0 | 5.655 | 0.302 | 100.0 |

代表样本：
- `angle_chasing` / `geometry3k00001`: Find the measure of $\angle 1$.
- `math_other` / `geometry3k00021`: Find $SP$.
- `circle_arc_chord` / `geometry3k00019`: Find $m \widehat{AC}$.
- `area_perimeter` / `geometry3k00005`: For the pair of similar figures, use the given areas to find $x$.
- `diagram_variable_solving` / `geometry3k00003`: Find x in the figure.
- `segment_length` / `geometry3k00000`: Find DX if $EX=24$ and $DE=7$.

### math\geoqa_plus

- N: `2766`
- 多样性：`moderately_concentrated`；有效类别数 `4.41`；Top1 `geometry_angle_chasing` 占 `51.88%`；Top3 占 `85.79%`
- 题长中位数 `36.0`，复杂度中位数 `7.928`，节点数中位数 `14.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| geometry_angle_chasing | 1435 | 51.88 | 34.0 | 7.899 | 0.338 | 99.79 |
| geometry_length_area_volume | 633 | 22.89 | 40.0 | 8.008 | 0.347 | 100.0 |
| math_other | 305 | 11.03 | 34.0 | 7.787 | 0.347 | 100.0 |
| visual_spatial_puzzle | 80 | 2.89 | 32.0 | 7.807 | 0.347 | 100.0 |
| number_theory_arithmetic | 63 | 2.28 | 38.0 | 7.984 | 0.383 | 100.0 |
| counting_probability_combinatorics | 60 | 2.17 | 45.0 | 8.281 | 0.365 | 100.0 |
| coordinate_geometry_transform | 59 | 2.13 | 37.0 | 7.861 | 0.347 | 100.0 |
| measurement_time_units | 48 | 1.74 | 44.0 | 8.445 | 0.369 | 100.0 |
| sequence_pattern_logic | 36 | 1.3 | 44.5 | 8.119 | 0.372 | 100.0 |
| statistics_data_analysis | 33 | 1.19 | 44.0 | 8.471 | 0.392 | 100.0 |
| algebra_equation_inequality | 12 | 0.43 | 26.0 | 7.333 | 0.392 | 100.0 |
| linear_programming_constraints | 2 | 0.07 | 38.0 | 7.427 | 0.324 | 100.0 |

代表样本：
- `geometry_angle_chasing` / `geoqaplus00004`: A rectangle is divided into 7 squares. The sides of the grey squares are all 8. What is the side of the great white square? <image1>
- `geometry_length_area_volume` / `geoqaplus00000`: The shaded area is equal to $2 \pi$. What is the length of $PQ$? <image1>
- `math_other` / `geoqaplus00012`: Werner wants to write a number at each vertex and on each edge of the rhombus. The sum of the numbers at the two vertices at the ends of each edge is equal to the number written on that edge. In the diagram, three edges are labeled 8, 9, and 13, and one edge i
- `visual_spatial_puzzle` / `geoqaplus00002`: Alice has four jigsaw pieces. <image1> Which two can be fitted together to form a hexagon?
- `number_theory_arithmetic` / `geoqaplus00001`: A student correctly added the two two-digit numbers on the left of the board and got the answer 137. What answer will she obtain if she adds the two four-digit numbers on the right of the board?
- `counting_probability_combinatorics` / `geoqaplus00008`: Seven identical dice (each with 1, 2, 3, 4, 5 and 6 points on their faces) are glued together to form the solid shown. Faces that are glued together each have the same number of points. How many points can be seen on the surface of the solid?

### math\mathvision

- N: `1879`
- 多样性：`moderately_concentrated`；有效类别数 `4.65`；Top1 `geometry_angle_chasing` 占 `48.32%`；Top3 占 `83.98%`
- 题长中位数 `41.0`，复杂度中位数 `7.69`，节点数中位数 `12.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| geometry_angle_chasing | 908 | 48.32 | 40.0 | 7.675 | 0.356 | 80.95 |
| geometry_length_area_volume | 496 | 26.4 | 42.0 | 7.761 | 0.356 | 83.87 |
| math_other | 174 | 9.26 | 39.0 | 7.652 | 0.347 | 78.16 |
| coordinate_geometry_transform | 64 | 3.41 | 35.5 | 7.397 | 0.347 | 92.19 |
| counting_probability_combinatorics | 49 | 2.61 | 48.0 | 7.956 | 0.347 | 83.67 |
| visual_spatial_puzzle | 43 | 2.29 | 36.0 | 7.486 | 0.347 | 81.4 |
| number_theory_arithmetic | 42 | 2.24 | 32.5 | 7.71 | 0.369 | 83.33 |
| measurement_time_units | 36 | 1.92 | 44.0 | 7.963 | 0.349 | 86.11 |
| statistics_data_analysis | 32 | 1.7 | 45.5 | 7.969 | 0.374 | 78.12 |
| sequence_pattern_logic | 24 | 1.28 | 49.0 | 8.105 | 0.347 | 91.67 |
| algebra_equation_inequality | 11 | 0.59 | 25.0 | 7.004 | 0.356 | 90.91 |

代表样本：
- `geometry_angle_chasing` / `mathvision00001`: A $3 \times 3 \times 3$ cube weighs 810 grams. If we drill three holes through it as shown, each of which is a $1 \times 1 \times 3$ rectangular parallelepiped, the weight of the remaining solid is:
- `geometry_length_area_volume` / `mathvision00000`: A rectangular piece of paper $ABCD$ is $5\mathrm{~cm}$ wide and $50\mathrm{~cm}$ long. The paper is white on one side and grey on the other. Christina folds the strip as shown so that the vertex $B$ coincides with $M$, the midpoint of the edge $CD$. Then she f
- `math_other` / `mathvision00005`: Which point in the labyrinth can we get to, starting at point $O$?
- `coordinate_geometry_transform` / `mathvision00029`: We take three points from the grid so that they were collinear. How many possibilities do we have?
- `counting_probability_combinatorics` / `mathvision00022`: Maia the bee can only walk on colorful houses. How many ways can you color exactly three white houses with the same color so that Maia can walk from A to B?
- `visual_spatial_puzzle` / `mathvision00018`: Each figure is made up of 4 equally big cubes and coloured in. Which figure needs the least amount of colour?

### math\mm_math

- N: `4229`
- 多样性：`single_dominant`；有效类别数 `1.83`；Top1 `geometry_angle_chasing` 占 `83.0%`；Top3 占 `99.15%`
- 题长中位数 `44.0`，复杂度中位数 `7.869`，节点数中位数 `12.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| geometry_angle_chasing | 3510 | 83.0 | 44.0 | 7.895 | 0.41 | 96.95 |
| coordinate_geometry_transform | 407 | 9.62 | 50.0 | 7.906 | 0.437 | 91.15 |
| geometry_length_area_volume | 276 | 6.53 | 42.0 | 7.387 | 0.401 | 93.12 |
| algebra_equation_inequality | 27 | 0.64 | 39.0 | 7.563 | 0.41 | 96.3 |
| visual_spatial_puzzle | 5 | 0.12 | 19.0 | 6.796 | 0.311 | 100.0 |
| math_other | 2 | 0.05 | 61.5 | 8.392 | 0.439 | 100.0 |
| measurement_time_units | 1 | 0.02 | 77.0 | 8.744 | 0.347 | 100.0 |
| linear_programming_constraints | 1 | 0.02 | 36.0 | 9.011 | 0.545 | 100.0 |

代表样本：
- `geometry_angle_chasing` / `mmmath00000`: As shown in the figure, the quadrilateral $ABCD$ is inscribed in the circle $\odot O$. If one of its exterior angles $\angle DCE = 68^\circ$, what is the degree measure of $\angle BOD$?
- `coordinate_geometry_transform` / `mmmath00006`: As shown in the figure, in the Cartesian coordinate system, the line $y = 2x + 6$ intersects the x-axis at point A and intersects the y-axis at point C. The parabola $y = -2x^2 + bx + c$ passes through points A and C, and intersects the x-axis at another point
- `geometry_length_area_volume` / `mmmath00010`: As shown in the figure, point C is on segment $AB$, and point D is the midpoint of $BC$, with $AB=30\,cm$ and $AC=4CD$. What is the length of $AC$ in $cm$?
- `algebra_equation_inequality` / `mmmath00086`: As shown in the figure, the graph of the function $y=kx+b$ ($k\neq 0$) passes through point $B(2,0)$ and intersects the graph of the function $y=2x$ at point $A$. What is the solution set of the inequality $0<kx+b<2x$?
- `visual_spatial_puzzle` / `mmmath00606`: As shown in the figure is the scene of drumming at the moment of a festive gathering and the three-dimensional shape of the drum. What is the shape of the drum when viewed from the front?
- `math_other` / `mmmath01041`: As shown in the figure, points A and B are located at the two ends of a pond. Xiao Cong wants to measure the distance between A and B with a rope, but the rope is not long enough. A classmate suggests: find a point C on the ground that can be directly reached 

### math\scemqa_math

- N: `189`
- 多样性：`diverse`；有效类别数 `6.72`；Top1 `geometry_length_area_volume` 占 `23.28%`；Top3 占 `60.85%`
- 题长中位数 `29.0`，复杂度中位数 `7.445`，节点数中位数 `13.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| geometry_length_area_volume | 44 | 23.28 | 44.5 | 7.523 | 0.365 | 77.27 |
| statistics_data_analysis | 36 | 19.05 | 25.5 | 7.238 | 0.347 | 97.22 |
| math_other | 35 | 18.52 | 29.0 | 7.444 | 0.392 | 71.43 |
| algebra_equation_inequality | 35 | 18.52 | 25.0 | 7.562 | 0.365 | 100.0 |
| coordinate_geometry_transform | 12 | 6.35 | 19.0 | 7.143 | 0.347 | 100.0 |
| counting_probability_combinatorics | 11 | 5.82 | 66.0 | 8.629 | 0.415 | 81.82 |
| geometry_angle_chasing | 10 | 5.29 | 38.5 | 7.336 | 0.392 | 70.0 |
| measurement_time_units | 4 | 2.12 | 43.0 | 8.531 | 0.405 | 100.0 |
| visual_spatial_puzzle | 2 | 1.06 | 66.5 | 8.814 | 0.41 | 100.0 |

代表样本：
- `geometry_length_area_volume` / `scemqamath00000`: Use the following computer output for a least-squares regression for Questions below. What is the equation of the least-squares regression line?
- `statistics_data_analysis` / `scemqamath00001`: As part of a study on the relationship between the use of tanning booths and the occurrence of skin cancer, researchers reviewed the medical records of 1,436 people. The table below summarizes tanning booth use for people in the study who did and did not have 
- `math_other` / `scemqamath00004`: Breakfast cereals have a wide range of sugar content. Some cereals contain High Fructose Corn Syrup (HFCS) as a source of sugar and some do not. The boxplots above show the total sugar content of different types of cereal for those containing HFCS and for thos
- `algebra_equation_inequality` / `scemqamath00006`: The table shows some of the values of differentiable functions $f$ and $g$ and their derivatives. If $h(x) = f(g(x))$, then $h'(2)$ equals
- `coordinate_geometry_transform` / `scemqamath00033`: Which equation has the slope field shown below?
- `counting_probability_combinatorics` / `scemqamath00008`: Suppose a cell phone company manufactures cell phones and tablets in the following four states: Arizona, California, Washington, and Minnesota. The table below shows the percentage of total output by state, and within each state, the percentage output of each 

### physics\emma_physics

- N: `266`
- 多样性：`strongly_concentrated`；有效类别数 `3.2`；Top1 `mechanics_kinematics_dynamics` 占 `62.03%`；Top3 占 `90.6%`
- 题长中位数 `74.0`，复杂度中位数 `8.459`，节点数中位数 `13.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| mechanics_kinematics_dynamics | 165 | 62.03 | 96.0 | 8.648 | 0.464 | 72.73 |
| electromagnetism_circuits | 53 | 19.92 | 45.0 | 8.072 | 0.392 | 77.36 |
| physics_other | 23 | 8.65 | 32.0 | 7.562 | 0.365 | 86.96 |
| waves_optics_sound | 10 | 3.76 | 96.0 | 9.375 | 0.446 | 100.0 |
| thermo_fluids_gases | 8 | 3.01 | 123.0 | 9.537 | 0.5 | 62.5 |
| graph_data_interpretation | 6 | 2.26 | 85.0 | 9.422 | 0.457 | 100.0 |
| modern_quantum_nuclear_relativity | 1 | 0.38 | 12.0 | 5.935 | 0.352 | 100.0 |

代表样本：
- `mechanics_kinematics_dynamics` / `emmaphysics00000`: A block (B) is attached to two unstretched springs S1 and S2 with spring constants $k$ and $4k$, respectively (see figure I). The other ends are attached to identical supports M1 and M2 not attached to the walls. The springs and supports have negligible mass. 
- `electromagnetism_circuits` / `emmaphysics00007`: A positive charge, $Q$, is located at the origin. We can introduce a new positive charge, $q$ (where $q \neq Q$), anywhere in the region. Let's consider the strength of the electric field, $|\mathbf{E}|$, at $(2, 0)$. Choose the correct statement about $|\math
- `physics_other` / `emmaphysics00003`: In an aluminum (Al) bar of square cross section, a square hole is drilled and is filled with iron (Fe) as shown in the figure. The electrical resistivities of Al and Fe are $2.7 \times 10^{-8}$ $\Omega$ m and $1.0 \times 10^{-7}$ $\Omega$ m, respectively. The 
- `waves_optics_sound` / `emmaphysics00029`: Consider an optical system made of many identical ideal (negligible-thickness) halflenses with focal length $f>0$, organized so that they share the same center and are angular-separated equally at density $n$ (number of lenses per unit-radian). Define the leng
- `thermo_fluids_gases` / `emmaphysics00013`: Anyone who's had an apple may know that pieces of an apple stick together: when picking up one piece, a second piece may also come with the first piece. The same idea is tried on a golden apple. Consider two uniform hemispheres with radius $r=4\ \mathrm{cm}$ m
- `graph_data_interpretation` / `emmaphysics00024`: These days, there are so many stylish rectangular home-designs (see figure A). It is possible from the outline of those houses in their picture to estimate with good precision where the camera was. Consider an outline in one photograph of a rectangular house w

### physics\multi_physics

- N: `525`
- 多样性：`moderately_concentrated`；有效类别数 `3.34`；Top1 `mechanics_kinematics_dynamics` 占 `54.86%`；Top3 占 `93.33%`
- 题长中位数 `90.0`，复杂度中位数 `8.272`，节点数中位数 `12.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| mechanics_kinematics_dynamics | 288 | 54.86 | 97.0 | 8.346 | 0.32 | 89.58 |
| electromagnetism_circuits | 141 | 26.86 | 83.0 | 8.266 | 0.311 | 89.36 |
| physics_other | 61 | 11.62 | 82.0 | 8.129 | 0.32 | 77.05 |
| waves_optics_sound | 15 | 2.86 | 82.0 | 8.358 | 0.302 | 86.67 |
| graph_data_interpretation | 8 | 1.52 | 59.0 | 7.813 | 0.324 | 100.0 |
| astronomy_gravity_orbits | 7 | 1.33 | 92.0 | 7.443 | 0.32 | 28.57 |
| thermo_fluids_gases | 4 | 0.76 | 46.0 | 7.827 | 0.302 | 100.0 |
| modern_quantum_nuclear_relativity | 1 | 0.19 | 81.0 | 8.524 | 0.302 | 100.0 |

代表样本：
- `mechanics_kinematics_dynamics` / `multiphysics00000`: 如图所示，质量为4kg的物体A静止在竖直的轻弹簧上面。质量为1kg的物体B用细线悬挂起来，A、B紧挨在一起，但A、B之间无压力。某时刻将细线剪断，则细线剪断瞬间，B对A的压力大小为（取g=10$\mathrm{m/s^{2}}$）（）
- `electromagnetism_circuits` / `multiphysics00001`: 矩形闭合线圈abcd竖直放置，OO′是它的对称轴，通电直导线AB与OO′平行，且AB、OO′所在平面与线圈平面垂直。若要在线圈中产生abcda方向的感应电流，可行的做法是（ ）
- `physics_other` / `multiphysics00007`: 某质点沿直线运动，其位移—时间图象如图所示。关于该质点的运动，下列说法中正确的是：
- `waves_optics_sound` / `multiphysics00009`: 将一光滑轻杆固定在地面上，杆与地面间夹角为$\theta$，一光滑轻环套在杆上。一个大小和质量都不计的滑轮用轻绳OP悬挂在天花板上，用另一轻绳通过滑轮系在轻环上，用手拉住轻绳另一端并使OP恰好在竖直方向，如图所示。现水平向右拉绳，当轻环重新静止不动时，OP绳与天花板之间的夹角为（ ）
- `graph_data_interpretation` / `multiphysics00026`: 货车和客车在公路上同一车道行驶，客车在前，货车在后。突然出现紧急情况，两车同时刹车。刚开始刹车时两车相距30 m，刹车过程中两车的 v-t 图像如图所示，则下列判断正确的是：
- `astronomy_gravity_orbits` / `multiphysics00020`: 金星和地球在同一平面内绕太阳公转，且公转轨道均视为圆形，如图所示，在地球上观测，发现金星与太阳可呈现的视角（太阳与金星均视为质点，它们与眼睛连线的夹角）有最大值，最大视角的正弦值为n，则金星的公转周期为( )

### physics\physreason

- N: `905`
- 多样性：`single_dominant`；有效类别数 `1.75`；Top1 `mechanics_kinematics_dynamics` 占 `87.07%`；Top3 占 `95.47%`
- 题长中位数 `140.0`，复杂度中位数 `11.863`，节点数中位数 `16.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| mechanics_kinematics_dynamics | 788 | 87.07 | 147.0 | 11.989 | 0.658 | 80.46 |
| electromagnetism_circuits | 40 | 4.42 | 95.5 | 10.66 | 0.622 | 70.0 |
| waves_optics_sound | 36 | 3.98 | 99.0 | 10.944 | 0.615 | 88.89 |
| physics_other | 27 | 2.98 | 84.0 | 9.394 | 0.518 | 74.07 |
| thermo_fluids_gases | 13 | 1.44 | 154.0 | 10.71 | 0.622 | 76.92 |
| graph_data_interpretation | 1 | 0.11 | 124.0 | 10.912 | 0.541 | 100.0 |

代表样本：
- `mechanics_kinematics_dynamics` / `physreason00000`: A thin string of length L is fixed at its upper end, and a small ball of mass m and charge q is attached to the lower end. The ball is placed in a uniform electric field pointing horizontally to the right. Initially, the string and the ball are held horizontal
- `electromagnetism_circuits` / `physreason00007`: As shown in Figure (1), a device for detecting gas discharge processes has two electrodes connected to a long straight wire in an ionization chamber filled with neon gas (Ne). These electrodes are then connected to a high-voltage power supply via two horizonta
- `waves_optics_sound` / `physreason00027`: A simple harmonic transverse wave propagates along the positive direction of the $x$-axis. The equilibrium position of the wave source is at the origin of the coordinate system. The vibration graph of the wave source within $0 \sim 4s$ is shown in the figure. 
- `physics_other` / `physreason00062`: A small ball is released from rest at a height of $500\mathrm{m}$ above the ground and falls freely under gravity, with $g=10\mathrm{m}/\mathrm{s}^{2}$.  1. How long does it take for the small ball to fall to the ground? 2. From the moment it begins to fall, t
- `thermo_fluids_gases` / `physreason00021`: Hot isostatic pressing (HIP) equipment is used for material processing. During operation, an inert gas is first compressed into a pre-evacuated furnace chamber at room temperature. The furnace chamber is then heated to utilize the high-temperature and high-pre
- `graph_data_interpretation` / `physreason00196`: In the experiment "Estimating the Size of Oleic Acid Molecules Using the Oil Film Method," an oleic acid-alcohol solution is prepared with a volume ratio of oleic acid to alcohol as $m{\cdot}n$. A syringe is used to draw droplets of this solution, and the tota

### physics\phyx

- N: `1139`
- 多样性：`moderately_concentrated`；有效类别数 `4.59`；Top1 `mechanics_kinematics_dynamics` 占 `44.42%`；Top3 占 `75.07%`
- 题长中位数 `54.0`，复杂度中位数 `8.452`，节点数中位数 `12.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| mechanics_kinematics_dynamics | 506 | 44.42 | 57.0 | 8.601 | 0.437 | 100.0 |
| waves_optics_sound | 198 | 17.38 | 56.0 | 8.441 | 0.437 | 100.0 |
| thermo_fluids_gases | 151 | 13.26 | 60.0 | 8.646 | 0.428 | 100.0 |
| physics_other | 132 | 11.59 | 45.5 | 8.108 | 0.397 | 100.0 |
| electromagnetism_circuits | 130 | 11.41 | 42.5 | 8.109 | 0.423 | 100.0 |
| modern_quantum_nuclear_relativity | 10 | 0.88 | 38.5 | 7.883 | 0.387 | 100.0 |
| graph_data_interpretation | 10 | 0.88 | 28.0 | 7.303 | 0.378 | 100.0 |
| astronomy_gravity_orbits | 2 | 0.18 | 86.5 | 8.259 | 0.392 | 100.0 |

代表样本：
- `mechanics_kinematics_dynamics` / `phyx00000`: A therapist tells a \(74\,\text{kg}\) patient with a broken leg that he must have his leg in a cast suspended horizontally. For minimum discomfort, the leg should be supported by a vertical strap attached at the center of mass of the leg-cast system. To comply
- `waves_optics_sound` / `phyx00003`: The index of refraction for violet light in silica flint glass is 1.66, and that for red light is 1.62. What is the angular spread of visible light passing through a prism of apex angle \(60.0^\circ\) if the angle of incidence is \(50.0^\circ\)? See figure.
- `thermo_fluids_gases` / `phyx00198`: Two pipes are separated by a distance d, entering perpendicularly and passing through a large wall of thickness t, as shown in the figure. The thermal conductivity of the wall is K, and the temperature far from the pipes is T0. At x = +d/2, hot water flows in 
- `physics_other` / `phyx00002`: A spaceship flies past Earth. A crew member on board the spaceship measures its length, obtaining the value as shown in the figure. What length do observers measure on Earth?
- `electromagnetism_circuits` / `phyx00048`: In the circuit shown in Figure, the switch is initially at point A. At time $t = 0$, the switch is moved to point B. After a long time, If there is voltage remaining on the capacitor, what are the voltages $V_1$
- `modern_quantum_nuclear_relativity` / `phyx00045`: Nuclei of a radioactive element $A$ are being produced at a constant rate $\alpha$. The element has a decay constant $\lambda$. At time $t = 0$, there are $N_0$ nuclei of the element as shown in figure. Calculate the number $N$ of nuclei of $A$ at time $t$

### physics\sciverse_physics

- N: `239`
- 多样性：`strongly_concentrated`；有效类别数 `3.45`；Top1 `mechanics_kinematics_dynamics` 占 `61.09%`；Top3 占 `86.61%`
- 题长中位数 `75.0`，复杂度中位数 `8.557`，节点数中位数 `12.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| mechanics_kinematics_dynamics | 146 | 61.09 | 83.5 | 8.79 | 0.401 | 100.0 |
| electromagnetism_circuits | 34 | 14.23 | 51.0 | 8.322 | 0.392 | 100.0 |
| physics_other | 27 | 11.3 | 30.0 | 7.335 | 0.365 | 100.0 |
| waves_optics_sound | 21 | 8.79 | 78.0 | 8.521 | 0.365 | 100.0 |
| graph_data_interpretation | 5 | 2.09 | 69.0 | 9.761 | 0.446 | 100.0 |
| thermo_fluids_gases | 3 | 1.26 | 39.0 | 7.549 | 0.338 | 100.0 |
| astronomy_gravity_orbits | 2 | 0.84 | 72.0 | 7.744 | 0.302 | 100.0 |
| modern_quantum_nuclear_relativity | 1 | 0.42 | 13.0 | 5.339 | 0.302 | 100.0 |

代表样本：
- `mechanics_kinematics_dynamics` / `sciversephysics00001`: 一根直径为 $D$ 的管道分裂为两根相同直径 $d$ 的小管道。若小管道中水流速度为 $v$,则大管道中水流速度为多少?  A. $\frac{dv}{d}$ B. $\frac{2dv}{d}$ C. $\frac{d^2v}{d^2}$ D. $\frac{2d^2v}{D^2}$
- `electromagnetism_circuits` / `sciversephysics00000`: 已构建如图所示的电路,电压源为12 V的理想电池。假设电池在完全放电前能持续供电15min,在此期间电池电压保持恒定为12V,放电后电压瞬间降为0V。求该电路的等效电阻。
- `physics_other` / `sciversephysics00004`: 如图所示,四根相同的杆受力。请对作用在左端铰链处的扭矩大小进行排序。  \begin{align*} \mathrm{A.}\quad& \mathrm{III} > \mathrm{I} = \mathrm{IV} > \mathrm{II}\\ \mathrm{B.}\quad& \mathrm{II} > \mathrm{IV} > \mathrm{III} > \mathrm{I}\\ \mathrm{C.}\quad& \mathrm{I} = \mathrm{III} = \mathrm{IV} > \
- `waves_optics_sound` / `sciversephysics00027`: 测量飞机空速的仪器称为皮托管。如图所示,面向传入空气流的开口(带有小孔径)用于静止捕获空气。垂直于空气流的开口(带有较大光圈)旨在以流速捕获空气。设水管计内液体为水,液面高度差$H = 1\\ \mathrm{m}$,空气密度$\rho_\mathrm{air} = 1.2\\ \mathrm{kg/m^3}$,则飞机的空速为:  A. $27\\ \mathrm{m/s}$ B. $68\\ \mathrm{m/s}$ C. $95\\ \mathrm{m/s}$ D. $128\\ \mathrm{m/s}$
- `graph_data_interpretation` / `sciversephysics00028`: 已知安装了旋转惯性的自行车轮,使其顺时针围绕垂直轴旋转。连接到车轮边缘的是火箭发动机,该发动机在燃烧时在车轮上施加顺时针扭矩 $\tau$。给出了车轮的角位置 $\theta$ 作为时间 $t$ 的函数的图。  除了车轮的旋转惯性和发动机燃烧的时间持续时间之外,该图中哪一项信息可以测定火箭在车轮上施加的净扭矩?  A. $t = 0$ s 和 $t = 3$ s 之间的图形面积 B. $t = 2$ s 之前和之后图形斜率的变化 C. 图在 $t = 3$ s 的垂直轴读数 D. 图在 $t = 2$ s 的垂直轴
- `thermo_fluids_gases` / `sciversephysics00050`: 一根水平管道中充满水。在某一时刻,管道发生扩张,如图所示。管道中的三个点标记为A、B和C,其中A点处管道直径最大,B点处管道直径最小。已知管道中液体处于静止状态,则这三点处的压强$P_A$、$P_B$、$P_C$的大小关系为:  A. $P_A > P_C > P_B$ B. $P_A = P_B = P_C$ C. $P_B = P_C > P_A$ D. $P_B > P_C > P_A$

### physics\seephys

- N: `1499`
- 多样性：`moderately_concentrated`；有效类别数 `3.96`；Top1 `mechanics_kinematics_dynamics` 占 `51.17%`；Top3 占 `83.99%`
- 题长中位数 `75.0`，复杂度中位数 `8.676`，节点数中位数 `13.0`

| Category | N | % | Q Len Med | Complexity Med | Multi-step Med | Req Image % |
| --- | --- | --- | --- | --- | --- | --- |
| mechanics_kinematics_dynamics | 767 | 51.17 | 87.0 | 8.75 | 0.383 | 89.44 |
| electromagnetism_circuits | 323 | 21.55 | 64.0 | 8.607 | 0.383 | 93.81 |
| waves_optics_sound | 169 | 11.27 | 70.0 | 8.698 | 0.392 | 94.08 |
| physics_other | 156 | 10.41 | 63.0 | 8.22 | 0.347 | 91.03 |
| thermo_fluids_gases | 52 | 3.47 | 81.5 | 8.768 | 0.356 | 84.62 |
| modern_quantum_nuclear_relativity | 14 | 0.93 | 81.5 | 8.954 | 0.439 | 78.57 |
| graph_data_interpretation | 12 | 0.8 | 36.5 | 7.644 | 0.338 | 100.0 |
| astronomy_gravity_orbits | 6 | 0.4 | 51.5 | 8.812 | 0.329 | 83.33 |

代表样本：
- `mechanics_kinematics_dynamics` / `seephys00000`: A disk of mass $M$ and radius $R$ slides without friction on a horizontal surface. Another disk of mass $m$ and radius $r$ is pinned through its center to a point off the center of the first disk by a distance $b$, so that it can rotate without friction on the
- `electromagnetism_circuits` / `seephys00001`: Name the lowest electric multipole in the radiation field emitted by the following time-varying charge distributions. A uniform charged spherical shell whose radius varies as $R=R_{0}+R_{1}\cos(\omega t)$.
- `waves_optics_sound` / `seephys00010`: A plane monochromatic wave (wavelength $\lambda$) is incident on a set of 5 slits spaced at a distance $d$ (Fig. 2.55). Assume that the width of the individual slits is much less than $d$. For the resulting interference pattern focused on a screen, compute the
- `physics_other` / `seephys00015`: Refer to Fig. 3.67. When this monostable circuit is triggered, how long will $Q_2$ be off?
- `thermo_fluids_gases` / `seephys00006`: A simple molecular beam apparatus is shown in Fig. 2.40. The oven contains $\mathrm{H}_{2}$ molecules at 300 K and at a pressure of 1 mm of mercury. The hole on the oven has a diameter of $100 \mu \mathrm{m}$, which is much smaller than the molecular mean free
- `modern_quantum_nuclear_relativity` / `seephys00048`: The potential curves for the ground electronic state (A) and an excited electronic state (B) of a diatomic molecule are shown in Fig. 8.2. Each electronic state has a series of vibrational levels labeled by the quantum number $\nu$. Some molecules were initial
