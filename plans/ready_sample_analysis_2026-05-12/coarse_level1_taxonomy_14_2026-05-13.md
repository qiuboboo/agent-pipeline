# Ready 样本粗粒度一级 Taxonomy（14 类）

记录时间：2026-05-13

本版基于 `plans/ready_sample_analysis_2026-05-12/ready_category_feature_summary.csv` 中的细粒度题型，进一步合并为适合报告/论文表述的粗粒度一级 taxonomy。相较 15 类候选，本版将数学统计类 `statistics_data_analysis` 并入跨学科的“实验、数据与图表解读”，形成 14 个一级类。

## 14 个一级类

1. **几何与空间推理**
   - 覆盖：角度追踪、长度/面积/体积、圆与弦弧、相似全等、三角比例、坐标几何、视觉空间推理、图形变量求解。
   - 典型来源：`mm_math`、`geoqa_plus`、`mathvision`、`geometry3k`。

2. **代数、离散数学与应用数学**
   - 覆盖：代数方程与不等式、线性规划、计数概率组合、数论算术、序列规律、测量单位应用题、数学综合/其他。
   - 典型来源：`scemqa_math`、`cmm_math` 及综合数学集的非几何部分。

3. **实验、数据与图表解读**
   - 覆盖：实验设计、曲线/表格/统计图解释、跨学科数据图表阅读，以及数学统计与数据分析。
   - 说明：这是一个任务形态类，横跨生物、化学、物理、地理、数学。

4. **力学与运动**
   - 覆盖：运动学、动力学、受力分析、能量、碰撞、机械过程。
   - 典型来源：`physreason`、`seephys`、`multi_physics`、`emma_physics`、`phyx`。

5. **电磁、电路与电子系统**
   - 覆盖：物理电磁/电路、直流/交流网络、模拟电子、数字逻辑、信号系统、控制系统、电力电子、电磁场、测量仪器。
   - 典型来源：`eee_bench` 以及物理数据集中的电磁/电路部分。

6. **波动、光学与声学**
   - 覆盖：波、光、声、干涉、折射、成像、声音传播。

7. **热学、流体与气体**
   - 覆盖：热学、流体、气体状态、压强、温度、浮力等。

8. **物理综合与现代物理**
   - 覆盖：物理综合/其他、现代物理、量子、核物理、相对论、天体、引力与轨道。

9. **化学结构与分子表示**
   - 覆盖：分子结构识别、Lewis 结构、成键、SMILES、过渡态结构、异构、命名、有机机理、周期律与化学键。
   - 典型来源：`emma_chemistry`、`scemqa_chemistry`、`sciverse_chemistry`。

10. **化学反应、平衡与计算**
    - 覆盖：反应计量、平衡、动力学、气体、热化学、电化学、酸碱溶液、化学综合/其他。

11. **生命分子、细胞与遗传**
    - 覆盖：细胞结构、遗传、分子生物学、酶、代谢、生化过程。

12. **生态、生理与生命系统**
    - 覆盖：生态、食物网、种群、进化分类、植物、生理、生命周期、生物综合/其他。

13. **地球空间、气候与自然地理**
    - 覆盖：地球-太阳-月球关系、气候天气、水文、地貌地质、地图地形、区域定位、地理综合/其他。

14. **人文地理、资源与环境**
    - 覆盖：人口、城市、经济地理、农业、资源、环境、人地关系。

## 细粒度题型到 14 类映射

- 几何与空间推理：`angle_chasing`, `geometry_angle_chasing`, `geometry_length_area_volume`, `area_perimeter`, `segment_length`, `circle_arc_chord`, `similarity_congruence`, `trigonometric_ratio`, `coordinate_geometry`, `coordinate_geometry_transform`, `visual_spatial_puzzle`, `diagram_variable_solving`
- 代数、离散数学与应用数学：`algebra_equation_inequality`, `linear_programming_constraints`, `counting_probability_combinatorics`, `number_theory_arithmetic`, `sequence_pattern_logic`, `measurement_time_units`, `math_other`
- 实验、数据与图表解读：`chart_graph_interpretation`, `experimental_graph_data`, `graph_data_interpretation`, `lab_graph_data_interpretation`, `statistics_data_analysis`
- 力学与运动：`mechanics_kinematics_dynamics`
- 电磁、电路与电子系统：`electromagnetism_circuits`, `dc_ac_network_analysis`, `analog_electronics_devices`, `digital_logic_boolean`, `sequential_logic_microprocessor`, `signals_systems_filtering`, `control_systems_transfer_function`, `power_machines_transformers`, `power_electronics_converters`, `electromagnetics_fields`, `measurement_instrumentation`, `circuit_other`
- 波动、光学与声学：`waves_optics_sound`
- 热学、流体与气体：`thermo_fluids_gases`
- 物理综合与现代物理：`physics_other`, `modern_quantum_nuclear_relativity`, `astronomy_gravity_orbits`
- 化学结构与分子表示：`molecular_structure_identification`, `molecular_structure_smiles_bonds`, `transition_state_smiles_selection`, `isomer_stereochemistry_nomenclature`, `organic_reaction_mechanism`, `periodic_atomic_bonding`
- 化学反应、平衡与计算：`stoichiometry_reaction_calculation`, `equilibrium_kinetics_gas`, `thermochemistry_calorimetry`, `electrochemistry_redox`, `acid_base_solution`, `chemistry_other`
- 生命分子、细胞与遗传：`cell_molecular_genetics`, `biochemistry_enzymes_metabolism`
- 生态、生理与生命系统：`anatomy_physiology`, `plant_biology`, `life_cycle_development`, `ecology_food_web_population`, `evolution_classification`, `biology_other`
- 地球空间、气候与自然地理：`earth_sun_moon_space`, `climate_weather_seasons`, `hydrology_ocean_rivers`, `geomorphology_geology_hazards`, `map_topography_location`, `geography_other`
- 人文地理、资源与环境：`population_urban_economic`, `agriculture_resources_environment`
