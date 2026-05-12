# Ready Pass Sample Feature Analysis

- Total pass sample files: `21555`
- Dataset count: `21`
- Scope: all `ready/<subject>/<dataset>/samples/*.json` files.
- Class labels are rule-based initial labels for fast diversity analysis; they should be treated as auditable draft tags, not final human taxonomy.

## Overall Distribution

| Subject | Pass Samples | Share |
| --- | --- | --- |
| math | 10084 | 46.78% |
| physics | 4573 | 21.22% |
| geography | 2055 | 9.53% |
| circuit | 2023 | 9.39% |
| biology | 1598 | 7.41% |
| chemistry | 1222 | 5.67% |

## Dataset Overview

| Dataset | N | Top Categories | Q Len Median | Requires Image % | Multi-step Median | Complexity Median |
| --- | --- | --- | --- | --- | --- | --- |
| biology\ai2d_biology | 1315 | cell_molecular_genetics 574, ecology_food_web_population 426, biology_other 167, plant_biology 59 | 9.0 | 100.0 | 0.302 | 5.973 |
| biology\scemqa_biology | 64 | cell_molecular_genetics 28, ecology_food_web_population 17, anatomy_physiology 7, experimental_graph_data 4 | 61.0 | 76.56 | 0.392 | 7.989 |
| biology\sciverse_biology | 219 | cell_molecular_genetics 126, ecology_food_web_population 31, biology_other 15, experimental_graph_data 13 | 78.0 | 100.0 | 0.311 | 8.459 |
| chemistry\emma_chemistry | 864 | transition_state_smiles_selection 846, chemistry_other 13, molecular_structure_identification 5 | 41.0 | 100.0 | 0.37 | 7.734 |
| chemistry\scemqa_chemistry | 111 | stoichiometry_reaction_calculation 32, molecular_structure_smiles_bonds 26, equilibrium_kinetics_gas 22, acid_base_solution 9 | 37.0 | 93.69 | 0.392 | 7.768 |
| chemistry\sciverse_chemistry | 247 | stoichiometry_reaction_calculation 61, molecular_structure_smiles_bonds 49, equilibrium_kinetics_gas 43, thermochemistry_calorimetry 31 | 47.0 | 100.0 | 0.356 | 7.987 |
| circuit\eee_bench | 2023 | dc_ac_network_analysis 698, analog_electronics_devices 368, circuit_other 280, digital_logic_boolean 226 | 33.0 | 98.52 | 0.401 | 7.828 |
| geography\ai2d_geography | 298 | earth_sun_moon_space 118, chart_graph_interpretation 98, geomorphology_geology_hazards 31, geography_other 28 | 8.0 | 100.0 | 0.302 | 5.864 |
| geography\geosqa | 1757 | climate_weather_seasons 372, population_urban_economic 338, chart_graph_interpretation 252, map_topography_location 225 | 58.0 | 100.0 | 0.374 | 8.91 |
| math\cmm_math | 142 | linear_programming_constraints 54, geometry_angle_chasing 42, algebra_equation_inequality 21, coordinate_geometry_transform 18 | 33.0 | 2.82 | 0.374 | 5.812 |
| math\geometry3k | 879 | angle_chasing 500, math_other 117, circle_arc_chord 77, area_perimeter 72 | 11.0 | 97.04 | 0.302 | 6.095 |
| math\geoqa_plus | 2766 | geometry_angle_chasing 1435, geometry_length_area_volume 633, math_other 305, visual_spatial_puzzle 80 | 36.0 | 99.89 | 0.347 | 7.928 |
| math\mathvision | 1879 | geometry_angle_chasing 908, geometry_length_area_volume 496, math_other 174, coordinate_geometry_transform 64 | 41.0 | 82.22 | 0.356 | 7.69 |
| math\mm_math | 4229 | geometry_angle_chasing 3510, coordinate_geometry_transform 407, geometry_length_area_volume 276, algebra_equation_inequality 27 | 44.0 | 96.15 | 0.41 | 7.869 |
| math\scemqa_math | 189 | geometry_length_area_volume 44, statistics_data_analysis 36, math_other 35, algebra_equation_inequality 35 | 29.0 | 86.24 | 0.365 | 7.445 |
| physics\emma_physics | 266 | mechanics_kinematics_dynamics 165, electromagnetism_circuits 53, physics_other 23, waves_optics_sound 10 | 74.0 | 76.32 | 0.428 | 8.459 |
| physics\multi_physics | 525 | mechanics_kinematics_dynamics 288, electromagnetism_circuits 141, physics_other 61, waves_optics_sound 15 | 90.0 | 87.43 | 0.32 | 8.272 |
| physics\physreason | 905 | mechanics_kinematics_dynamics 788, electromagnetism_circuits 40, waves_optics_sound 36, physics_other 27 | 140.0 | 80.11 | 0.649 | 11.863 |
| physics\phyx | 1139 | mechanics_kinematics_dynamics 506, waves_optics_sound 198, thermo_fluids_gases 151, physics_other 132 | 54.0 | 100.0 | 0.428 | 8.452 |
| physics\sciverse_physics | 239 | mechanics_kinematics_dynamics 146, electromagnetism_circuits 34, physics_other 27, waves_optics_sound 21 | 75.0 | 100.0 | 0.392 | 8.557 |
| physics\seephys | 1499 | mechanics_kinematics_dynamics 767, electromagnetism_circuits 323, waves_optics_sound 169, physics_other 156 | 75.0 | 90.86 | 0.374 | 8.676 |

## Per-Dataset Detail

### biology\ai2d_biology

- Samples: `1315`
- Median question units: `9.0`; p25-p75: `7.0`-`13.0`
- Median answer units: `1.0`
- Requires image: `100.0%`; has choice marker: `0.38%`
- Median visual entities: `6.0`; median node count: `11.0`
- Median scores: multimodal `0.958`, multi-step `0.302`, verifiability `0.986`

| Solution Category | Count | Share |
| --- | --- | --- |
| cell_molecular_genetics | 574 | 43.65% |
| ecology_food_web_population | 426 | 32.4% |
| biology_other | 167 | 12.7% |
| plant_biology | 59 | 4.49% |
| anatomy_physiology | 44 | 3.35% |
| life_cycle_development | 43 | 3.27% |
| experimental_graph_data | 1 | 0.08% |
| biochemistry_enzymes_metabolism | 1 | 0.08% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| generic_visual | 806 | 61.29% |
| wide_diagram | 263 | 20.0% |
| dense_diagram | 216 | 16.43% |
| geometry_diagram | 23 | 1.75% |
| chart_like | 7 | 0.53% |

Representative examples:
- `ecology_food_web_population`: `ai2d_biology00000` - In the above the diagram below, which shows a partial food web. Which animal or bird is on the top of the food chain?
- `cell_molecular_genetics`: `ai2d_biology00002` - What is the outermost layer of the cell?
- `biology_other`: `ai2d_biology00015` - Which animal is not an herbivore?
- `anatomy_physiology`: `ai2d_biology00016` - Which organism in the diagram is important because it returns nutrients back to the soil?
- `plant_biology`: `ai2d_biology00021` - Which represents a branched cluster of flowers in which the branches are racemes?

### biology\scemqa_biology

- Samples: `64`
- Median question units: `61.0`; p25-p75: `28.75`-`93.0`
- Median answer units: `5.5`
- Requires image: `76.56%`; has choice marker: `4.69%`
- Median visual entities: `6.0`; median node count: `14.0`
- Median scores: multimodal `0.962`, multi-step `0.392`, verifiability `0.997`

| Solution Category | Count | Share |
| --- | --- | --- |
| cell_molecular_genetics | 28 | 43.75% |
| ecology_food_web_population | 17 | 26.56% |
| anatomy_physiology | 7 | 10.94% |
| experimental_graph_data | 4 | 6.25% |
| plant_biology | 2 | 3.12% |
| biochemistry_enzymes_metabolism | 2 | 3.12% |
| biology_other | 2 | 3.12% |
| evolution_classification | 2 | 3.12% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| chart_like | 24 | 37.5% |
| generic_visual | 12 | 18.75% |
| wide_diagram | 7 | 10.94% |
| geometry_diagram | 4 | 6.25% |
| dense_diagram | 2 | 3.12% |

Representative examples:
- `cell_molecular_genetics`: `scemqabiology00000` - The cell cycle is a series of events in the life of a dividing eukaryotic cell. It consists of four stages: G1, S, G2, and M. The duration of the cell cycle varies from one species to another and from one cell type to an
- `ecology_food_web_population`: `scemqabiology00004` - On the basis of what happens at the end of this chart, what is the most likely explanation for the population decline after point E?
- `plant_biology`: `scemqabiology00005` - Two ecologists, Peter and Rosemary Grant, spent thirty years observing, tagging, and measuring finches (a type of bird) in the Galápagos Islands. They made their observations on Daphne Major—one of the most desolate of t
- `anatomy_physiology`: `scemqabiology00007` - A scientist studies the storage and distribution of oxygen in humans and Weddell seals to examine the physiological adaptations that permit seals to descend to great depths and stay submerged for extended periods. The fi
- `experimental_graph_data`: `scemqabiology00009` - A student sets up a lab experiment to study the behavior of slugs. She uses a 1-square-meter tray filled with soil and divides it into four quadrants with different conditions. She places 20 slugs in the tray, 5 in each 

### biology\sciverse_biology

- Samples: `219`
- Median question units: `78.0`; p25-p75: `32.5`-`141.0`
- Median answer units: `3.0`
- Requires image: `100.0%`; has choice marker: `40.18%`
- Median visual entities: `6.0`; median node count: `11.0`
- Median scores: multimodal `0.969`, multi-step `0.311`, verifiability `0.986`

| Solution Category | Count | Share |
| --- | --- | --- |
| cell_molecular_genetics | 126 | 57.53% |
| ecology_food_web_population | 31 | 14.16% |
| biology_other | 15 | 6.85% |
| experimental_graph_data | 13 | 5.94% |
| plant_biology | 11 | 5.02% |
| anatomy_physiology | 10 | 4.57% |
| biochemistry_enzymes_metabolism | 7 | 3.2% |
| evolution_classification | 5 | 2.28% |
| life_cycle_development | 1 | 0.46% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| generic_visual | 79 | 36.07% |
| wide_diagram | 69 | 31.51% |
| chart_like | 36 | 16.44% |
| dense_diagram | 22 | 10.05% |
| geometry_diagram | 12 | 5.48% |
| circuit_diagram | 1 | 0.46% |

Representative examples:
- `ecology_food_web_population`: `sciversebiology00000` - 在100代的过程中研究了啮齿动物的种群,以检查牙釉质厚度的变化。适应需要高水平加工的食物资源的物种,其牙釉质比吃柔软、易加工食物的物种更厚。根据这一信息和随后的曲线,回答以下问题:  该物种的饮食发生了何种变化?  A. 它的食物资源变得越来越柔软,更容易加工。 B. 它的食物资源越来越困难加工。 C. 种群数量正在增加。 D. 种群数量正在减少。
- `evolution_classification`: `sciversebiology00001` - 如图<img="q_07905_001.png">所示,M、N、O三个分类单元共有白圆形这一特征,该特征不仅存在于它们的最近共同祖先中,而且还存在于更早的祖先($*$)中。因此,白圆形是这三个分类单元的共有的一个祖先性状。
- `cell_molecular_genetics`: `sciversebiology00004` - 这是四种氨基酸的结构示意图:丝氨酸(A)具有极性侧链,赖氨酸(B)带正电荷,谷氨酸(C)带负电荷,甘氨酸(D)具有非极性侧链。  关于这些氨基酸通过质膜溶解的正确陈述是:  A. 丝氨酸(A)可以很容易地通过质膜溶解。 B. 只有赖氨酸(B)和谷氨酸(C)可以轻松地通过质膜溶解。 C. 丝氨酸(A)、赖氨酸(B)和谷氨酸(C)可以很容易地通过质膜溶解。 D. 只有甘氨酸(D)可以轻松地通过质膜溶解。
- `biochemistry_enzymes_metabolism`: `sciversebiology00010` - 如果抑制剂能够与酶的活性位点结合并阻止底物在该位点上结合,这是一种竞争性抑制的例子。  A. 非竞争性抑制 B. 竞争性抑制 C. 辅助因子 D. 辅酶
- `plant_biology`: `sciversebiology00012` - 下图显示了细菌培养物的两条生长曲线 A 和 B。根据生长曲线的特征,哪一项最能解释培养物 A 和培养物 B 之间的差异?  A. 培养物 B 起始细菌数量较多 B. 培养物 A 存在竞争性抑制剂 C. 培养物 B 测量频率较低 D. 培养物 A 尚未耗尽生长所需的空间和营养资源

### chemistry\emma_chemistry

- Samples: `864`
- Median question units: `41.0`; p25-p75: `17.0`-`45.0`
- Median answer units: `5.0`
- Requires image: `100.0%`; has choice marker: `0.0%`
- Median visual entities: `6.0`; median node count: `12.0`
- Median scores: multimodal `0.977`, multi-step `0.37`, verifiability `0.997`

| Solution Category | Count | Share |
| --- | --- | --- |
| transition_state_smiles_selection | 846 | 97.92% |
| chemistry_other | 13 | 1.5% |
| molecular_structure_identification | 5 | 0.58% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| generic_visual | 734 | 84.95% |
| wide_diagram | 126 | 14.58% |
| geometry_diagram | 2 | 0.23% |
| chart_like | 2 | 0.23% |

Representative examples:
- `transition_state_smiles_selection`: `emmachemistry00000` - Please choose the SMILES expression of the transition-state structure shown in the image, ignoring the arrows.
- `chemistry_other`: `emmachemistry00008` - Isomers of hexane, based on their branching, can be divided into three distinct classes as shown in the figure. What is the correct order of their boiling points?
- `molecular_structure_identification`: `emmachemistry00272` - A compound M_pX_q has cubic close packing (ccp) arrangement of X. Its unit cell structure is shown below. The empirical formula of the compound is <image_1>

### chemistry\scemqa_chemistry

- Samples: `111`
- Median question units: `37.0`; p25-p75: `24.0`-`58.5`
- Median answer units: `3.0`
- Requires image: `93.69%`; has choice marker: `0.9%`
- Median visual entities: `5.0`; median node count: `14.0`
- Median scores: multimodal `0.961`, multi-step `0.392`, verifiability `0.997`

| Solution Category | Count | Share |
| --- | --- | --- |
| stoichiometry_reaction_calculation | 32 | 28.83% |
| molecular_structure_smiles_bonds | 26 | 23.42% |
| equilibrium_kinetics_gas | 22 | 19.82% |
| acid_base_solution | 9 | 8.11% |
| periodic_atomic_bonding | 6 | 5.41% |
| thermochemistry_calorimetry | 6 | 5.41% |
| isomer_stereochemistry_nomenclature | 3 | 2.7% |
| chemistry_other | 3 | 2.7% |
| lab_graph_data_interpretation | 2 | 1.8% |
| electrochemistry_redox | 2 | 1.8% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| wide_diagram | 38 | 34.23% |
| chart_like | 36 | 32.43% |
| generic_visual | 17 | 15.32% |
| geometry_diagram | 11 | 9.91% |
| circuit_diagram | 2 | 1.8% |

Representative examples:
- `molecular_structure_smiles_bonds`: `scemqachemistry00000` - The graph below shows the amount of potential energy between two hydrogen atoms as the distance between them changes. At which point in the graph would a molecule of H2 be the most stable?
- `periodic_atomic_bonding`: `scemqachemistry00001` - Which of the labeled arrows in the diagram above represents the strongest intermolecular force?
- `stoichiometry_reaction_calculation`: `scemqachemistry00003` - Two half-cells are set up as follows:  Half-Cell A: Strip of Cu(s) in $CuNO_3(aq)$  Half-Cell B: Strip of Zn(s) in $Zn(NO_3)_2(aq)$  When the cells are connected according to the following diagram, the following reaction
- `equilibrium_kinetics_gas`: `scemqachemistry00007` - A solution of carbonic acid, $H_2CO_3$, is titrated with sodium hydroxide, NaOH. The following graph is produced. In addition to $OH^-$, what species are present in the solution during section III of the graph?
- `isomer_stereochemistry_nomenclature`: `scemqachemistry00012` - Two half-cells are set up as follows:  Half-Cell A: Strip of Cu(s) in $CuNO_3(aq)$  Half-Cell B: Strip of Zn(s) in $Zn(NO_3)_2(aq)$  When the cells are connected according to the following diagram, the following reaction

### chemistry\sciverse_chemistry

- Samples: `247`
- Median question units: `47.0`; p25-p75: `27.0`-`74.5`
- Median answer units: `2.0`
- Requires image: `100.0%`; has choice marker: `3.24%`
- Median visual entities: `6.0`; median node count: `12.0`
- Median scores: multimodal `0.969`, multi-step `0.356`, verifiability `0.997`

| Solution Category | Count | Share |
| --- | --- | --- |
| stoichiometry_reaction_calculation | 61 | 24.7% |
| molecular_structure_smiles_bonds | 49 | 19.84% |
| equilibrium_kinetics_gas | 43 | 17.41% |
| thermochemistry_calorimetry | 31 | 12.55% |
| acid_base_solution | 22 | 8.91% |
| isomer_stereochemistry_nomenclature | 11 | 4.45% |
| lab_graph_data_interpretation | 11 | 4.45% |
| electrochemistry_redox | 7 | 2.83% |
| periodic_atomic_bonding | 6 | 2.43% |
| chemistry_other | 5 | 2.02% |
| organic_reaction_mechanism | 1 | 0.4% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| wide_diagram | 111 | 44.94% |
| generic_visual | 68 | 27.53% |
| chart_like | 47 | 19.03% |
| geometry_diagram | 17 | 6.88% |
| circuit_diagram | 2 | 0.81% |
| dense_diagram | 2 | 0.81% |

Representative examples:
- `acid_base_solution`: `sciversechemistry00000` - 下列各图常用来说明甲烷分子的结构。哪一种与甲烷分子的真实结构相差较大?  \begin{center} \includegraphics[scale=0.5]{q_11896_001.png} \end{center}
- `thermochemistry_calorimetry`: `sciversechemistry00001` - 已知一个体积为 2 升的密闭容器中,装有氦气和氩气。图中显示了该容器内压强 $p$ 与温度 $T$ 的关系曲线。问该容器中氦气分子的数目是多少?
- `stoichiometry_reaction_calculation`: `sciversechemistry00002` - 一名学生设计了一个实验,以确定铝的比热容。该实验过程如下:将质量为 $5.86\ \mathrm{g}$ 的铝块加热至不同温度,然后将其滴入装有 $25.0\ \mathrm{mL}$ 水的量热计中。下图显示了其中一次试验过程中收集的数据。已知水的比热容为 $4.18\ \mathrm{J/(g\cdot^\circ C)}$,密度为 $1.00\ \mathrm{g/mL}$,请计算该次试验中水吸收的热量(单位:J)。
- `organic_reaction_mechanism`: `sciversechemistry00003` - 下列卤代烃 $\ce{CH3CH2CH2Br}$、$\ce{(CH3)3CCl}$、$\ce{CH3CH(Br)CH3}$ 和 $\ce{(CH3)2C(Br)CH3}$ 按 $\mathrm{S_{N}1}$ 反应机理进行反应时,反应最快的是 $\ce{(CH3)3CCl}$。
- `isomer_stereochemistry_nomenclature`: `sciversechemistry00006` - 请给出下列化合物的 IUPAC 命名或结构式:  \begin{center} \includegraphics[scale=0.5]{q_11937_001.png} \end{center}

### circuit\eee_bench

- Samples: `2023`
- Median question units: `33.0`; p25-p75: `21.0`-`49.0`
- Median answer units: `2.0`
- Requires image: `98.52%`; has choice marker: `6.08%`
- Median visual entities: `6.0`; median node count: `13.0`
- Median scores: multimodal `0.975`, multi-step `0.401`, verifiability `0.997`

| Solution Category | Count | Share |
| --- | --- | --- |
| dc_ac_network_analysis | 698 | 34.5% |
| analog_electronics_devices | 368 | 18.19% |
| circuit_other | 280 | 13.84% |
| digital_logic_boolean | 226 | 11.17% |
| signals_systems_filtering | 191 | 9.44% |
| control_systems_transfer_function | 143 | 7.07% |
| sequential_logic_microprocessor | 35 | 1.73% |
| power_machines_transformers | 30 | 1.48% |
| electromagnetics_fields | 24 | 1.19% |
| measurement_instrumentation | 17 | 0.84% |
| power_electronics_converters | 11 | 0.54% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| circuit_diagram | 1415 | 69.95% |
| generic_visual | 401 | 19.82% |
| chart_like | 100 | 4.94% |
| geometry_diagram | 53 | 2.62% |
| dense_diagram | 24 | 1.19% |

Representative examples:
- `digital_logic_boolean`: `eeebench00000` - The Boolean function \( f \) implemented in the figure using two-input multiplexers is
- `control_systems_transfer_function`: `eeebench00001` - The asymptotic approximation of the log-magnitude versus frequency plot of a minimum phase system with real poles and one zero is shown in the figure. Its transfer function is ______.
- `analog_electronics_devices`: `eeebench00002` - Calculate current I\(_2\) in this Darlington pair circuit, assuming a typical forward base-emitter junction voltage drop of 0.7 volts for each transistor. The current I\(_2\) is ______ mA.
- `dc_ac_network_analysis`: `eeebench00005` - In the circuit shown in figure, the voltage at point A is ( )
- `measurement_instrumentation`: `eeebench00009` - In the sinusoidal AC circuit shown in the figure, an inductance with reactance of \(10\,\Omega\) and a load \(Z\) are connected in series. If the voltmeters \((V1)\), \((V2)\), and \((V)\) all show the same value, then t

### geography\ai2d_geography

- Samples: `298`
- Median question units: `8.0`; p25-p75: `6.0`-`10.0`
- Median answer units: `1.0`
- Requires image: `100.0%`; has choice marker: `0.34%`
- Median visual entities: `6.0`; median node count: `12.0`
- Median scores: multimodal `0.962`, multi-step `0.302`, verifiability `0.986`

| Solution Category | Count | Share |
| --- | --- | --- |
| earth_sun_moon_space | 118 | 39.6% |
| chart_graph_interpretation | 98 | 32.89% |
| geomorphology_geology_hazards | 31 | 10.4% |
| geography_other | 28 | 9.4% |
| hydrology_ocean_rivers | 10 | 3.36% |
| climate_weather_seasons | 8 | 2.68% |
| map_topography_location | 3 | 1.01% |
| agriculture_resources_environment | 2 | 0.67% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| generic_visual | 101 | 33.89% |
| dense_diagram | 96 | 32.21% |
| wide_diagram | 90 | 30.2% |
| geometry_diagram | 9 | 3.02% |
| chart_like | 2 | 0.67% |

Representative examples:
- `chart_graph_interpretation`: `ai2d_geography00000` - What comes after the 1st quarter?
- `earth_sun_moon_space`: `ai2d_geography00001` - Choose the option which is the phase of the moon occurring when it passes between the earth and the sun and is invisible or visible only as a narrow crescent at sunset?
- `hydrology_ocean_rivers`: `ai2d_geography00003` - What is the runoff stage?
- `geography_other`: `ai2d_geography00005` - Which layer does D represent?
- `geomorphology_geology_hazards`: `ai2d_geography00006` - What cycle is depicted in the given diagram?

### geography\geosqa

- Samples: `1757`
- Median question units: `58.0`; p25-p75: `44.0`-`85.0`
- Median answer units: `6.0`
- Requires image: `100.0%`; has choice marker: `0.17%`
- Median visual entities: `6.0`; median node count: `14.0`
- Median scores: multimodal `0.979`, multi-step `0.374`, verifiability `0.997`

| Solution Category | Count | Share |
| --- | --- | --- |
| climate_weather_seasons | 372 | 21.17% |
| population_urban_economic | 338 | 19.24% |
| chart_graph_interpretation | 252 | 14.34% |
| map_topography_location | 225 | 12.81% |
| geography_other | 165 | 9.39% |
| earth_sun_moon_space | 135 | 7.68% |
| hydrology_ocean_rivers | 106 | 6.03% |
| agriculture_resources_environment | 101 | 5.75% |
| geomorphology_geology_hazards | 63 | 3.59% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| wide_diagram | 960 | 54.64% |
| generic_visual | 622 | 35.4% |
| dense_diagram | 175 | 9.96% |

Representative examples:
- `population_urban_economic`: `geosqa00000` - 亦庄经济技术开发区是北京市重点发展的三个新卫星城之一,其定位是京津城际发展走廊上的高新技术产业和先进制造业基地。近年来人口数量不断增加。下图为“亦庄城镇人口构成比例图”。读图,回答下列各题。  <image1>  影响亦庄人口迁入的主要因素是
- `hydrology_ocean_rivers`: `geosqa00001` - 下面两幅图分别是两条大河的河口图,图中小岛因泥沙不断堆积而扩展,最终将与河的哪岸相连接。  <image1>  1与甲岸相连2与乙岸相连3与丙岸相连4与丁岸相连
- `climate_weather_seasons`: `geosqa00002` - 某地理学习小组为了深入了解各种气候类型的分布与成因,做了各种模拟演示。图为某理想区域分布图,结合所学知识回答题。  <image1>  在模拟演示中,当黄赤交角变为0°,如果甲地气候类型在地球上无法再找到.试分析甲地实际所在的半球及其气候类型分别是 ( )
- `map_topography_location`: `geosqa00003` - 一群旅游爱好者到祖国的大好河山去旅游,右图为他们到达30°N附近一个地区的等高线地形图,图中等高距为100m。读图回答题。  <image1>  山峰5的最大海拔可能为
- `chart_graph_interpretation`: `geosqa00005` - 凡是温度在0°C或0°C以下,并含有冰的各种岩(土)称为冻土。读下图“北半球多年冻土分布剖面图”,回答下列问题。  <image1>  图中所示的冻土分布特点是

### math\cmm_math

- Samples: `142`
- Median question units: `33.0`; p25-p75: `29.0`-`45.0`
- Median answer units: `2.0`
- Requires image: `2.82%`; has choice marker: `0.0%`
- Median visual entities: `0.0`; median node count: `6.0`
- Median scores: multimodal `0.33`, multi-step `0.374`, verifiability `1.0`

| Solution Category | Count | Share |
| --- | --- | --- |
| linear_programming_constraints | 54 | 38.03% |
| geometry_angle_chasing | 42 | 29.58% |
| algebra_equation_inequality | 21 | 14.79% |
| coordinate_geometry_transform | 18 | 12.68% |
| math_other | 7 | 4.93% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| generic_visual | 4 | 2.82% |

Representative examples:
- `linear_programming_constraints`: `cmmmath00000` - 如果实数 $x, y$ 满足约束条件 $\left\{\begin{array}{l}x-y+1 \geq 0, \\ y+1 \geq 0, \\ x+y+1 \leq 0,\end{array}\right.$ 则 $2 x-y$ 的最大值为 ( )
- `algebra_equation_inequality`: `cmmmath00001` - $x$ 的不等式 $a x-b<0$ 的解集是 $(1,+\infty)$, 则关于 $x$ 的不等式 $(a x+b)(x-3)>0$ 的解集是( )
- `coordinate_geometry_transform`: `cmmmath00002` - 已知点 $(-3,-1)$ 和点 $(4,-6)$ 在直线 $3 x-2 y-a=0$ 的两侧, 则 $a$ 的取值范围为 ( )
- `geometry_angle_chasing`: `cmmmath00003` - 在平面直角坐标系 $x O y$ 中, $M$ 为不等式组 $\left\{\begin{array}{l}2 x-y-2 \geq 0, \\ x+2 y-1 \geq 0, \\ 3 x+y-8 \leq 0\end{array}\right.$ 所表示的区域上一动点,则直线 OM 斜率的最小值为 ( )
- `math_other`: `cmmmath00005` - 若 $x, y$ 满足 $\left\{\begin{array}{l}x-y+3 \geq 0, \\ x+y+1 \geq 0, \\ x \leq k,\end{array}\right.$

### math\geometry3k

- Samples: `879`
- Median question units: `11.0`; p25-p75: `6.0`-`16.0`
- Median answer units: `1.0`
- Requires image: `97.04%`; has choice marker: `0.11%`
- Median visual entities: `6.0`; median node count: `12.0`
- Median scores: multimodal `0.961`, multi-step `0.302`, verifiability `1.0`

| Solution Category | Count | Share |
| --- | --- | --- |
| angle_chasing | 500 | 56.88% |
| math_other | 117 | 13.31% |
| circle_arc_chord | 77 | 8.76% |
| area_perimeter | 72 | 8.19% |
| diagram_variable_solving | 41 | 4.66% |
| segment_length | 34 | 3.87% |
| trigonometric_ratio | 21 | 2.39% |
| coordinate_geometry | 12 | 1.37% |
| similarity_congruence | 5 | 0.57% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| geometry_diagram | 495 | 56.31% |
| generic_visual | 235 | 26.73% |
| wide_diagram | 87 | 9.9% |
| dense_diagram | 36 | 4.1% |

Representative examples:
- `segment_length`: `geometry3k00000` - Find DX if $EX=24$ and $DE=7$.
- `angle_chasing`: `geometry3k00001` - Find the measure of $\angle 1$.
- `diagram_variable_solving`: `geometry3k00003` - Find x in the figure.
- `area_perimeter`: `geometry3k00005` - For the pair of similar figures, use the given areas to find $x$.
- `circle_arc_chord`: `geometry3k00019` - Find $m \widehat{AC}$.

### math\geoqa_plus

- Samples: `2766`
- Median question units: `36.0`; p25-p75: `26.0`-`49.0`
- Median answer units: `2.0`
- Requires image: `99.89%`; has choice marker: `0.76%`
- Median visual entities: `6.0`; median node count: `14.0`
- Median scores: multimodal `0.966`, multi-step `0.347`, verifiability `0.986`

| Solution Category | Count | Share |
| --- | --- | --- |
| geometry_angle_chasing | 1435 | 51.88% |
| geometry_length_area_volume | 633 | 22.89% |
| math_other | 305 | 11.03% |
| visual_spatial_puzzle | 80 | 2.89% |
| number_theory_arithmetic | 63 | 2.28% |
| counting_probability_combinatorics | 60 | 2.17% |
| coordinate_geometry_transform | 59 | 2.13% |
| measurement_time_units | 48 | 1.74% |
| sequence_pattern_logic | 36 | 1.3% |
| statistics_data_analysis | 33 | 1.19% |
| algebra_equation_inequality | 12 | 0.43% |
| linear_programming_constraints | 2 | 0.07% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| generic_visual | 965 | 34.89% |
| geometry_diagram | 816 | 29.5% |
| wide_diagram | 763 | 27.58% |
| dense_diagram | 146 | 5.28% |
| chart_like | 64 | 2.31% |
| circuit_diagram | 9 | 0.33% |

Representative examples:
- `geometry_length_area_volume`: `geoqaplus00000` - The shaded area is equal to $2 \pi$. What is the length of $PQ$? <image1>
- `number_theory_arithmetic`: `geoqaplus00001` - A student correctly added the two two-digit numbers on the left of the board and got the answer 137. What answer will she obtain if she adds the two four-digit numbers on the right of the board?
- `visual_spatial_puzzle`: `geoqaplus00002` - Alice has four jigsaw pieces. <image1> Which two can be fitted together to form a hexagon?
- `geometry_angle_chasing`: `geoqaplus00004` - A rectangle is divided into 7 squares. The sides of the grey squares are all 8. What is the side of the great white square? <image1>
- `sequence_pattern_logic`: `geoqaplus00006` - Peter rides his bike along a cycle path in a park. He starts at point $S$ and rides in the direction of the arrow. At the first crossing he turns right, then at the next left, and then again to the right and then again t

### math\mathvision

- Samples: `1879`
- Median question units: `41.0`; p25-p75: `30.0`-`54.0`
- Median answer units: `1.0`
- Requires image: `82.22%`; has choice marker: `0.85%`
- Median visual entities: `6.0`; median node count: `12.0`
- Median scores: multimodal `0.974`, multi-step `0.356`, verifiability `1.0`

| Solution Category | Count | Share |
| --- | --- | --- |
| geometry_angle_chasing | 908 | 48.32% |
| geometry_length_area_volume | 496 | 26.4% |
| math_other | 174 | 9.26% |
| coordinate_geometry_transform | 64 | 3.41% |
| counting_probability_combinatorics | 49 | 2.61% |
| visual_spatial_puzzle | 43 | 2.29% |
| number_theory_arithmetic | 42 | 2.24% |
| measurement_time_units | 36 | 1.92% |
| statistics_data_analysis | 32 | 1.7% |
| sequence_pattern_logic | 24 | 1.28% |
| algebra_equation_inequality | 11 | 0.59% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| geometry_diagram | 789 | 41.99% |
| generic_visual | 363 | 19.32% |
| wide_diagram | 238 | 12.67% |
| dense_diagram | 84 | 4.47% |
| chart_like | 62 | 3.3% |
| circuit_diagram | 9 | 0.48% |

Representative examples:
- `geometry_length_area_volume`: `mathvision00000` - A rectangular piece of paper $ABCD$ is $5\mathrm{~cm}$ wide and $50\mathrm{~cm}$ long. The paper is white on one side and grey on the other. Christina folds the strip as shown so that the vertex $B$ coincides with $M$, t
- `geometry_angle_chasing`: `mathvision00001` - A $3 \times 3 \times 3$ cube weighs 810 grams. If we drill three holes through it as shown, each of which is a $1 \times 1 \times 3$ rectangular parallelepiped, the weight of the remaining solid is:
- `measurement_time_units`: `mathvision00002` - What time is it now, if after 6 hours and 30 minutes the clock will show 4:00?
- `math_other`: `mathvision00005` - Which point in the labyrinth can we get to, starting at point $O$?
- `number_theory_arithmetic`: `mathvision00009` - The digits of the sequence $123451234512345 \ldots$ fill the cells on a sheet of paper in a spiral-like manner beginning with the marked cell (see the figure). Which digit is written in the cell being 100 cells above the

### math\mm_math

- Samples: `4229`
- Median question units: `44.0`; p25-p75: `35.0`-`57.0`
- Median answer units: `68.0`
- Requires image: `96.15%`; has choice marker: `4.73%`
- Median visual entities: `5.0`; median node count: `12.0`
- Median scores: multimodal `0.95`, multi-step `0.41`, verifiability `0.975`

| Solution Category | Count | Share |
| --- | --- | --- |
| geometry_angle_chasing | 3510 | 83.0% |
| coordinate_geometry_transform | 407 | 9.62% |
| geometry_length_area_volume | 276 | 6.53% |
| algebra_equation_inequality | 27 | 0.64% |
| visual_spatial_puzzle | 5 | 0.12% |
| math_other | 2 | 0.05% |
| measurement_time_units | 1 | 0.02% |
| linear_programming_constraints | 1 | 0.02% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| geometry_diagram | 3196 | 75.57% |
| chart_like | 722 | 17.07% |
| generic_visual | 104 | 2.46% |
| wide_diagram | 35 | 0.83% |
| dense_diagram | 9 | 0.21% |

Representative examples:
- `geometry_angle_chasing`: `mmmath00000` - As shown in the figure, the quadrilateral $ABCD$ is inscribed in the circle $\odot O$. If one of its exterior angles $\angle DCE = 68^\circ$, what is the degree measure of $\angle BOD$?
- `coordinate_geometry_transform`: `mmmath00006` - As shown in the figure, in the Cartesian coordinate system, the line $y = 2x + 6$ intersects the x-axis at point A and intersects the y-axis at point C. The parabola $y = -2x^2 + bx + c$ passes through points A and C, an
- `geometry_length_area_volume`: `mmmath00010` - As shown in the figure, point C is on segment $AB$, and point D is the midpoint of $BC$, with $AB=30\,cm$ and $AC=4CD$. What is the length of $AC$ in $cm$?
- `algebra_equation_inequality`: `mmmath00086` - As shown in the figure, the graph of the function $y=kx+b$ ($k\neq 0$) passes through point $B(2,0)$ and intersects the graph of the function $y=2x$ at point $A$. What is the solution set of the inequality $0<kx+b<2x$?
- `visual_spatial_puzzle`: `mmmath00606` - As shown in the figure is the scene of drumming at the moment of a festive gathering and the three-dimensional shape of the drum. What is the shape of the drum when viewed from the front?

### math\scemqa_math

- Samples: `189`
- Median question units: `29.0`; p25-p75: `21.0`-`45.0`
- Median answer units: `3.0`
- Requires image: `86.24%`; has choice marker: `0.53%`
- Median visual entities: `6.0`; median node count: `13.0`
- Median scores: multimodal `0.962`, multi-step `0.365`, verifiability `0.997`

| Solution Category | Count | Share |
| --- | --- | --- |
| geometry_length_area_volume | 44 | 23.28% |
| statistics_data_analysis | 36 | 19.05% |
| math_other | 35 | 18.52% |
| algebra_equation_inequality | 35 | 18.52% |
| coordinate_geometry_transform | 12 | 6.35% |
| counting_probability_combinatorics | 11 | 5.82% |
| geometry_angle_chasing | 10 | 5.29% |
| measurement_time_units | 4 | 2.12% |
| visual_spatial_puzzle | 2 | 1.06% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| chart_like | 94 | 49.74% |
| wide_diagram | 47 | 24.87% |
| geometry_diagram | 11 | 5.82% |
| generic_visual | 8 | 4.23% |
| dense_diagram | 3 | 1.59% |

Representative examples:
- `geometry_length_area_volume`: `scemqamath00000` - Use the following computer output for a least-squares regression for Questions below. What is the equation of the least-squares regression line?
- `statistics_data_analysis`: `scemqamath00001` - As part of a study on the relationship between the use of tanning booths and the occurrence of skin cancer, researchers reviewed the medical records of 1,436 people. The table below summarizes tanning booth use for peopl
- `measurement_time_units`: `scemqamath00002` - As part of a community service program, students in three middle school grades (grade 6, grade 7, grade 8) each chose to participate in one of three school-sponsored volunteer activities. The graph below shows the distri
- `math_other`: `scemqamath00004` - Breakfast cereals have a wide range of sugar content. Some cereals contain High Fructose Corn Syrup (HFCS) as a source of sugar and some do not. The boxplots above show the total sugar content of different types of cerea
- `algebra_equation_inequality`: `scemqamath00006` - The table shows some of the values of differentiable functions $f$ and $g$ and their derivatives. If $h(x) = f(g(x))$, then $h'(2)$ equals

### physics\emma_physics

- Samples: `266`
- Median question units: `74.0`; p25-p75: `43.25`-`115.75`
- Median answer units: `3.0`
- Requires image: `76.32%`; has choice marker: `7.14%`
- Median visual entities: `5.0`; median node count: `13.0`
- Median scores: multimodal `0.969`, multi-step `0.428`, verifiability `0.997`

| Solution Category | Count | Share |
| --- | --- | --- |
| mechanics_kinematics_dynamics | 165 | 62.03% |
| electromagnetism_circuits | 53 | 19.92% |
| physics_other | 23 | 8.65% |
| waves_optics_sound | 10 | 3.76% |
| thermo_fluids_gases | 8 | 3.01% |
| graph_data_interpretation | 6 | 2.26% |
| modern_quantum_nuclear_relativity | 1 | 0.38% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| geometry_diagram | 66 | 24.81% |
| circuit_diagram | 41 | 15.41% |
| wide_diagram | 40 | 15.04% |
| chart_like | 35 | 13.16% |
| generic_visual | 19 | 7.14% |
| dense_diagram | 2 | 0.75% |

Representative examples:
- `mechanics_kinematics_dynamics`: `emmaphysics00000` - A block (B) is attached to two unstretched springs S1 and S2 with spring constants $k$ and $4k$, respectively (see figure I). The other ends are attached to identical supports M1 and M2 not attached to the walls. The spr
- `physics_other`: `emmaphysics00003` - In an aluminum (Al) bar of square cross section, a square hole is drilled and is filled with iron (Fe) as shown in the figure. The electrical resistivities of Al and Fe are $2.7 \times 10^{-8}$ $\Omega$ m and $1.0 \times
- `electromagnetism_circuits`: `emmaphysics00007` - A positive charge, $Q$, is located at the origin. We can introduce a new positive charge, $q$ (where $q \neq Q$), anywhere in the region. Let's consider the strength of the electric field, $|\mathbf{E}|$, at $(2, 0)$. Ch
- `thermo_fluids_gases`: `emmaphysics00013` - Anyone who's had an apple may know that pieces of an apple stick together: when picking up one piece, a second piece may also come with the first piece. The same idea is tried on a golden apple. Consider two uniform hemi
- `graph_data_interpretation`: `emmaphysics00024` - These days, there are so many stylish rectangular home-designs (see figure A). It is possible from the outline of those houses in their picture to estimate with good precision where the camera was. Consider an outline in

### physics\multi_physics

- Samples: `525`
- Median question units: `90.0`; p25-p75: `65.0`-`114.0`
- Median answer units: `8.0`
- Requires image: `87.43%`; has choice marker: `1.52%`
- Median visual entities: `5.0`; median node count: `12.0`
- Median scores: multimodal `0.855`, multi-step `0.32`, verifiability `0.874`

| Solution Category | Count | Share |
| --- | --- | --- |
| mechanics_kinematics_dynamics | 288 | 54.86% |
| electromagnetism_circuits | 141 | 26.86% |
| physics_other | 61 | 11.62% |
| waves_optics_sound | 15 | 2.86% |
| graph_data_interpretation | 8 | 1.52% |
| astronomy_gravity_orbits | 7 | 1.33% |
| thermo_fluids_gases | 4 | 0.76% |
| modern_quantum_nuclear_relativity | 1 | 0.19% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| generic_visual | 262 | 49.9% |
| wide_diagram | 180 | 34.29% |
| dense_diagram | 17 | 3.24% |
| geometry_diagram | 1 | 0.19% |

Representative examples:
- `mechanics_kinematics_dynamics`: `multiphysics00000` - 如图所示，质量为4kg的物体A静止在竖直的轻弹簧上面。质量为1kg的物体B用细线悬挂起来，A、B紧挨在一起，但A、B之间无压力。某时刻将细线剪断，则细线剪断瞬间，B对A的压力大小为（取g=10$\mathrm{m/s^{2}}$）（）
- `electromagnetism_circuits`: `multiphysics00001` - 矩形闭合线圈abcd竖直放置，OO′是它的对称轴，通电直导线AB与OO′平行，且AB、OO′所在平面与线圈平面垂直。若要在线圈中产生abcda方向的感应电流，可行的做法是（ ）
- `physics_other`: `multiphysics00007` - 某质点沿直线运动，其位移—时间图象如图所示。关于该质点的运动，下列说法中正确的是：
- `waves_optics_sound`: `multiphysics00009` - 将一光滑轻杆固定在地面上，杆与地面间夹角为$\theta$，一光滑轻环套在杆上。一个大小和质量都不计的滑轮用轻绳OP悬挂在天花板上，用另一轻绳通过滑轮系在轻环上，用手拉住轻绳另一端并使OP恰好在竖直方向，如图所示。现水平向右拉绳，当轻环重新静止不动时，OP绳与天花板之间的夹角为（ ）
- `astronomy_gravity_orbits`: `multiphysics00020` - 金星和地球在同一平面内绕太阳公转，且公转轨道均视为圆形，如图所示，在地球上观测，发现金星与太阳可呈现的视角（太阳与金星均视为质点，它们与眼睛连线的夹角）有最大值，最大视角的正弦值为n，则金星的公转周期为( )

### physics\physreason

- Samples: `905`
- Median question units: `140.0`; p25-p75: `104.0`-`192.0`
- Median answer units: `11.0`
- Requires image: `80.11%`; has choice marker: `12.27%`
- Median visual entities: `6.0`; median node count: `16.0`
- Median scores: multimodal `0.962`, multi-step `0.649`, verifiability `0.997`

| Solution Category | Count | Share |
| --- | --- | --- |
| mechanics_kinematics_dynamics | 788 | 87.07% |
| electromagnetism_circuits | 40 | 4.42% |
| waves_optics_sound | 36 | 3.98% |
| physics_other | 27 | 2.98% |
| thermo_fluids_gases | 13 | 1.44% |
| graph_data_interpretation | 1 | 0.11% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| geometry_diagram | 309 | 34.14% |
| circuit_diagram | 154 | 17.02% |
| chart_like | 119 | 13.15% |
| wide_diagram | 71 | 7.85% |
| generic_visual | 58 | 6.41% |
| dense_diagram | 15 | 1.66% |

Representative examples:
- `mechanics_kinematics_dynamics`: `physreason00000` - A thin string of length L is fixed at its upper end, and a small ball of mass m and charge q is attached to the lower end. The ball is placed in a uniform electric field pointing horizontally to the right. Initially, the
- `electromagnetism_circuits`: `physreason00007` - As shown in Figure (1), a device for detecting gas discharge processes has two electrodes connected to a long straight wire in an ionization chamber filled with neon gas (Ne). These electrodes are then connected to a hig
- `thermo_fluids_gases`: `physreason00021` - Hot isostatic pressing (HIP) equipment is used for material processing. During operation, an inert gas is first compressed into a pre-evacuated furnace chamber at room temperature. The furnace chamber is then heated to u
- `waves_optics_sound`: `physreason00027` - A simple harmonic transverse wave propagates along the positive direction of the $x$-axis. The equilibrium position of the wave source is at the origin of the coordinate system. The vibration graph of the wave source wit
- `physics_other`: `physreason00062` - A small ball is released from rest at a height of $500\mathrm{m}$ above the ground and falls freely under gravity, with $g=10\mathrm{m}/\mathrm{s}^{2}$.  1. How long does it take for the small ball to fall to the ground?

### physics\phyx

- Samples: `1139`
- Median question units: `54.0`; p25-p75: `38.0`-`73.0`
- Median answer units: `2.0`
- Requires image: `100.0%`; has choice marker: `2.37%`
- Median visual entities: `6.0`; median node count: `12.0`
- Median scores: multimodal `0.972`, multi-step `0.428`, verifiability `0.997`

| Solution Category | Count | Share |
| --- | --- | --- |
| mechanics_kinematics_dynamics | 506 | 44.42% |
| waves_optics_sound | 198 | 17.38% |
| thermo_fluids_gases | 151 | 13.26% |
| physics_other | 132 | 11.59% |
| electromagnetism_circuits | 130 | 11.41% |
| modern_quantum_nuclear_relativity | 10 | 0.88% |
| graph_data_interpretation | 10 | 0.88% |
| astronomy_gravity_orbits | 2 | 0.18% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| wide_diagram | 304 | 26.69% |
| generic_visual | 281 | 24.67% |
| geometry_diagram | 202 | 17.73% |
| chart_like | 157 | 13.78% |
| circuit_diagram | 98 | 8.6% |
| dense_diagram | 97 | 8.52% |

Representative examples:
- `mechanics_kinematics_dynamics`: `phyx00000` - A therapist tells a \(74\,\text{kg}\) patient with a broken leg that he must have his leg in a cast suspended horizontally. For minimum discomfort, the leg should be supported by a vertical strap attached at the center o
- `physics_other`: `phyx00002` - A spaceship flies past Earth. A crew member on board the spaceship measures its length, obtaining the value as shown in the figure. What length do observers measure on Earth?
- `waves_optics_sound`: `phyx00003` - The index of refraction for violet light in silica flint glass is 1.66, and that for red light is 1.62. What is the angular spread of visible light passing through a prism of apex angle \(60.0^\circ\) if the angle of inc
- `modern_quantum_nuclear_relativity`: `phyx00045` - Nuclei of a radioactive element $A$ are being produced at a constant rate $\alpha$. The element has a decay constant $\lambda$. At time $t = 0$, there are $N_0$ nuclei of the element as shown in figure. Calculate the num
- `electromagnetism_circuits`: `phyx00048` - In the circuit shown in Figure, the switch is initially at point A. At time $t = 0$, the switch is moved to point B. After a long time, If there is voltage remaining on the capacitor, what are the voltages $V_1$

### physics\sciverse_physics

- Samples: `239`
- Median question units: `75.0`; p25-p75: `45.5`-`102.0`
- Median answer units: `3.0`
- Requires image: `100.0%`; has choice marker: `47.7%`
- Median visual entities: `6.0`; median node count: `12.0`
- Median scores: multimodal `0.967`, multi-step `0.392`, verifiability `0.986`

| Solution Category | Count | Share |
| --- | --- | --- |
| mechanics_kinematics_dynamics | 146 | 61.09% |
| electromagnetism_circuits | 34 | 14.23% |
| physics_other | 27 | 11.3% |
| waves_optics_sound | 21 | 8.79% |
| graph_data_interpretation | 5 | 2.09% |
| thermo_fluids_gases | 3 | 1.26% |
| astronomy_gravity_orbits | 2 | 0.84% |
| modern_quantum_nuclear_relativity | 1 | 0.42% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| wide_diagram | 110 | 46.03% |
| generic_visual | 66 | 27.62% |
| circuit_diagram | 30 | 12.55% |
| chart_like | 22 | 9.21% |
| geometry_diagram | 9 | 3.77% |
| dense_diagram | 2 | 0.84% |

Representative examples:
- `electromagnetism_circuits`: `sciversephysics00000` - 已构建如图所示的电路,电压源为12 V的理想电池。假设电池在完全放电前能持续供电15min,在此期间电池电压保持恒定为12V,放电后电压瞬间降为0V。求该电路的等效电阻。
- `mechanics_kinematics_dynamics`: `sciversephysics00001` - 一根直径为 $D$ 的管道分裂为两根相同直径 $d$ 的小管道。若小管道中水流速度为 $v$,则大管道中水流速度为多少?  A. $\frac{dv}{d}$ B. $\frac{2dv}{d}$ C. $\frac{d^2v}{d^2}$ D. $\frac{2d^2v}{D^2}$
- `physics_other`: `sciversephysics00004` - 如图所示,四根相同的杆受力。请对作用在左端铰链处的扭矩大小进行排序。  \begin{align*} \mathrm{A.}\quad& \mathrm{III} > \mathrm{I} = \mathrm{IV} > \mathrm{II}\\ \mathrm{B.}\quad& \mathrm{II} > \mathrm{IV} > \mathrm{III} > \mathrm{I}\\ \mathrm{C.}\quad& \ma
- `waves_optics_sound`: `sciversephysics00027` - 测量飞机空速的仪器称为皮托管。如图所示,面向传入空气流的开口(带有小孔径)用于静止捕获空气。垂直于空气流的开口(带有较大光圈)旨在以流速捕获空气。设水管计内液体为水,液面高度差$H = 1\\ \mathrm{m}$,空气密度$\rho_\mathrm{air} = 1.2\\ \mathrm{kg/m^3}$,则飞机的空速为:  A. $27\\ \mathrm{m/s}$ B. $68\\ \mathrm{m/s}$ C. $95\
- `graph_data_interpretation`: `sciversephysics00028` - 已知安装了旋转惯性的自行车轮,使其顺时针围绕垂直轴旋转。连接到车轮边缘的是火箭发动机,该发动机在燃烧时在车轮上施加顺时针扭矩 $\tau$。给出了车轮的角位置 $\theta$ 作为时间 $t$ 的函数的图。  除了车轮的旋转惯性和发动机燃烧的时间持续时间之外,该图中哪一项信息可以测定火箭在车轮上施加的净扭矩?  A. $t = 0$ s 和 $t = 3$ s 之间的图形面积 B. $t = 2$ s 之前和之后图形斜率的变化 C. 

### physics\seephys

- Samples: `1499`
- Median question units: `75.0`; p25-p75: `52.5`-`107.0`
- Median answer units: `7.0`
- Requires image: `90.86%`; has choice marker: `2.27%`
- Median visual entities: `6.0`; median node count: `13.0`
- Median scores: multimodal `0.965`, multi-step `0.374`, verifiability `0.986`

| Solution Category | Count | Share |
| --- | --- | --- |
| mechanics_kinematics_dynamics | 767 | 51.17% |
| electromagnetism_circuits | 323 | 21.55% |
| waves_optics_sound | 169 | 11.27% |
| physics_other | 156 | 10.41% |
| thermo_fluids_gases | 52 | 3.47% |
| modern_quantum_nuclear_relativity | 14 | 0.93% |
| graph_data_interpretation | 12 | 0.8% |
| astronomy_gravity_orbits | 6 | 0.4% |

| Visual Kind | Count | Share |
| --- | --- | --- |
| generic_visual | 622 | 41.49% |
| wide_diagram | 309 | 20.61% |
| circuit_diagram | 187 | 12.47% |
| geometry_diagram | 156 | 10.41% |
| chart_like | 97 | 6.47% |
| dense_diagram | 6 | 0.4% |

Representative examples:
- `mechanics_kinematics_dynamics`: `seephys00000` - A disk of mass $M$ and radius $R$ slides without friction on a horizontal surface. Another disk of mass $m$ and radius $r$ is pinned through its center to a point off the center of the first disk by a distance $b$, so th
- `electromagnetism_circuits`: `seephys00001` - Name the lowest electric multipole in the radiation field emitted by the following time-varying charge distributions. A uniform charged spherical shell whose radius varies as $R=R_{0}+R_{1}\cos(\omega t)$.
- `thermo_fluids_gases`: `seephys00006` - A simple molecular beam apparatus is shown in Fig. 2.40. The oven contains $\mathrm{H}_{2}$ molecules at 300 K and at a pressure of 1 mm of mercury. The hole on the oven has a diameter of $100 \mu \mathrm{m}$, which is m
- `waves_optics_sound`: `seephys00010` - A plane monochromatic wave (wavelength $\lambda$) is incident on a set of 5 slits spaced at a distance $d$ (Fig. 2.55). Assume that the width of the individual slits is much less than $d$. For the resulting interference 
- `physics_other`: `seephys00015` - Refer to Fig. 3.67. When this monostable circuit is triggered, how long will $Q_2$ be off?

## Extracted Feature Families

| Family | Features |
| --- | --- |
| Text | language, question length, answer length, sentence/line count, LaTeX count, numeric token count |
| Task form | question_type, answer_type, answer_shape, choice markers, answer slots |
| Multimodal | has_image, image_count, media size/dimensions, requires_image, visual kind, visual entity/relation counts |
| Reasoning structure | condition/target/entity counts, node count/types, path_mode, rewrite_strategy |
| Scores | multimodal_strength_score, multi_step_score, verifiability_score, solvability_score, derived complexity_index |
| Taxonomy | subject/domain tags plus rule-based solution_category per sample |
