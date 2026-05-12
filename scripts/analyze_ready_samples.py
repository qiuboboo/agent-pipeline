#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Any, Iterable

try:
    from PIL import Image
except Exception:  # pragma: no cover - optional but available in the repo env.
    Image = None  # type: ignore[assignment]


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_READY_ROOT = PROJECT_ROOT / "ready"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "plans" / "ready_sample_analysis_2026-05-12"

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+(?:\.\d+)?")
LATEX_RE = re.compile(r"\\\(|\\\[|\$[^$]+\$|\\[a-zA-Z]+")
NUM_RE = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?:/\d+(?:\.\d+)?)?")
IMAGE_REF_RE = re.compile(r"<image\d*|\\includegraphics|shown in (?:the )?(?:figure|image|diagram)|图|读图|如图", re.I)
CHOICE_MARKER_RE = re.compile(r"(^|\s|\n)(?:[A-D]\.|[A-D]\)|A\.|B\.|C\.|D\.|①|②|③|④)", re.I)


@dataclass(frozen=True)
class PatternRule:
    label: str
    patterns: tuple[str, ...]


SUBJECT_RULES: dict[str, tuple[PatternRule, ...]] = {
    "circuit": (
        PatternRule("digital_logic_boolean", ("boolean", "logic", "truth table", "karnaugh", "k-map", "multiplexer", "decoder", "encoder", "flip-flop", "latch", "xor", "xnor", "ttl", "cmos")),
        PatternRule("sequential_logic_microprocessor", ("counter", "shift register", "register", "8085", "assembly", "accumulator", "clock pulse", "state of", "sequence generator")),
        PatternRule("control_systems_transfer_function", ("transfer function", "bode", "root locus", "nyquist", "closed-loop", "open-loop", "stability", "state-space", "block diagram", "poles", "zeros")),
        PatternRule("signals_systems_filtering", ("signal", "fourier", "laplace", "z-transform", "convolution", "filter", "impulse response", "frequency response", "sampling")),
        PatternRule("analog_electronics_devices", ("op-amp", "operational amplifier", "diode", "transistor", "mosfet", "bjt", "darlington", "amplifier", "rectifier", "bias")),
        PatternRule("dc_ac_network_analysis", ("thevenin", "norton", "equivalent resistance", "resistance", "impedance", "phasor", "rlc", "resistor", "capacitor", "inductor", "node", "mesh", "current", "voltage", "potential", "time constant", "switch", "power factor")),
        PatternRule("power_machines_transformers", ("three-phase", "transformer", "synchronous", "induction motor", "dc motor", "generator", "armature", "winding", "mvar", "kva")),
        PatternRule("power_electronics_converters", ("converter", "inverter", "chopper", "rectifier", "boost", "buck", "duty cycle", "thyristor", "scr")),
        PatternRule("electromagnetics_fields", ("magnetic field", "electric field", "transmission line", "antenna", "waveguide", "maxwell", "flux density")),
        PatternRule("measurement_instrumentation", ("ammeter", "voltmeter", "wattmeter", "oscilloscope", "bridge", "instrument", "measurement")),
    ),
    "physics": (
        PatternRule("mechanics_kinematics_dynamics", ("velocity", "acceleration", "force", "friction", "projectile", "block", "spring", "pendulum", "collision", "momentum", "torque", "rotat", "kinetic", "potential energy", "motion", "mass", "inclined", "work", "energy", "center of mass", "moment of inertia", "angular momentum", "lagrangian", "hamiltonian", "normal mode", "oscillation", "自由落体", "加速度", "速度", "摩擦", "弹簧", "碰撞", "动量", "力矩", "机械能", "小球", "物体", "斜面", "抛", "圆周运动")),
        PatternRule("electromagnetism_circuits", ("charge", "electric field", "magnetic", "current", "voltage", "capacitor", "resistor", "inductor", "flux", "induction", "coulomb", "电场", "磁场", "电流", "电压", "电容", "电阻", "感应", "洛伦兹", "安培")),
        PatternRule("waves_optics_sound", ("lens", "mirror", "refraction", "reflection", "interference", "diffraction", "wave", "sound", "doppler", "光", "透镜", "折射", "反射", "干涉", "衍射", "波")),
        PatternRule("thermo_fluids_gases", ("temperature", "heat", "thermal", "entropy", "pressure", "gas", "fluid", "buoyancy", "density", "温度", "热", "压强", "气体", "流体", "浮力", "密度")),
        PatternRule("modern_quantum_nuclear_relativity", ("quantum", "photon", "electron", "nuclear", "radioactive", "half-life", "relativity", "de broglie", "atom", "量子", "光子", "电子", "核", "相对论", "半衰期")),
        PatternRule("graph_data_interpretation", ("graph", "plot", "curve", "diagram shows", "图像", "曲线", "坐标图", "v-t", "x-t", "y-t")),
        PatternRule("astronomy_gravity_orbits", ("planet", "satellite", "orbit", "gravitational", "kepler", "星球", "卫星", "轨道", "万有引力")),
    ),
    "math": (
        PatternRule("geometry_angle_chasing", ("angle", "\\angle", "∠", "角", "degree", "circ", "parallel", "perpendicular", "垂直", "平行")),
        PatternRule("geometry_length_area_volume", ("area", "perimeter", "volume", "length", "radius", "diameter", "side", "circle", "triangle", "rectangle", "square", "polygon", "cm", "面积", "周长", "体积", "长度", "半径", "直径", "三角形", "矩形", "正方形", "圆")),
        PatternRule("coordinate_geometry_transform", ("coordinate", "cartesian", "slope", "line", "parabola", "rotate", "reflection", "translation", "坐标", "斜率", "直线", "抛物线", "旋转", "平移", "对称")),
        PatternRule("linear_programming_constraints", ("constraint", "constraints", "maximum value", "minimum value", "maximized", "minimized", "约束条件", "最大值", "最小值", "取值范围", "线性规划")),
        PatternRule("algebra_equation_inequality", ("equation", "inequality", "solve", "function", "polynomial", "quadratic", "system", "real number", "不等式", "方程", "函数", "二次", "多项式", "解集")),
        PatternRule("counting_probability_combinatorics", ("probability", "how many ways", "arrange", "combination", "permutation", "count", "dice", "coin", "概率", "组合", "排列", "多少种", "计数")),
        PatternRule("number_theory_arithmetic", ("integer", "prime", "divisible", "remainder", "digit", "factor", "multiple", "整数", "质数", "余数", "因数", "倍数", "数字")),
        PatternRule("statistics_data_analysis", ("mean", "median", "box plot", "regression", "standard deviation", "histogram", "scatterplot", "data", "table", "平均", "中位数", "回归", "标准差", "统计", "表格")),
        PatternRule("sequence_pattern_logic", ("sequence", "pattern", "next", "grid", "magic", "规律", "数列", "图案", "模式")),
        PatternRule("measurement_time_units", ("clock", "time", "calendar", "unit", "rate", "speed", "时间", "时钟", "单位", "速度")),
        PatternRule("visual_spatial_puzzle", ("fold", "cube", "net", "shape", "jigsaw", "mirror", "tile", "piece", "立方体", "折叠", "拼图", "镜子", "瓷砖")),
    ),
    "geography": (
        PatternRule("map_topography_location", ("map", "contour", "latitude", "longitude", "elevation", "slope", "地图", "等高线", "经纬", "海拔", "地形", "方位")),
        PatternRule("climate_weather_seasons", ("climate", "weather", "temperature", "precipitation", "monsoon", "season", "气候", "天气", "气温", "降水", "季风", "季节")),
        PatternRule("earth_sun_moon_space", ("moon", "phase", "earth", "sun", "orbit", "solar", "lunar", "月相", "地球", "太阳", "昼夜", "黄赤交角")),
        PatternRule("hydrology_ocean_rivers", ("river", "ocean", "water cycle", "runoff", "lake", "coast", "河流", "湖", "海洋", "水循环", "径流", "河口")),
        PatternRule("population_urban_economic", ("population", "urban", "city", "industry", "migration", "econom", "人口", "城市", "产业", "迁入", "经济")),
        PatternRule("geomorphology_geology_hazards", ("tectonic", "plate", "earthquake", "volcano", "rock", "landform", "地质", "板块", "地震", "火山", "岩石", "地貌")),
        PatternRule("agriculture_resources_environment", ("agriculture", "soil", "resource", "environment", "pollution", "land use", "农业", "土壤", "资源", "环境", "污染", "土地")),
        PatternRule("chart_graph_interpretation", ("graph", "chart", "table", "diagram", "柱状图", "曲线", "图表", "统计图")),
    ),
    "biology": (
        PatternRule("ecology_food_web_population", ("food web", "food chain", "population", "ecosystem", "predator", "prey", "habitat", "生态", "食物链", "食物网", "种群", "捕食")),
        PatternRule("cell_molecular_genetics", ("cell", "dna", "rna", "gene", "chromosome", "protein", "membrane", "mitosis", "meiosis", "细胞", "基因", "染色体", "蛋白质", "膜", "有丝", "减数")),
        PatternRule("anatomy_physiology", ("organ", "blood", "heart", "lung", "muscle", "nerve", "digest", "respiration", "larynx", "pharynx", "trachea", "anus", "teeth", "canine", "pelvis", "器官", "血液", "心脏", "肌肉", "神经", "消化", "呼吸")),
        PatternRule("life_cycle_development", ("life cycle", "stage", "egg", "larva", "pupa", "adult", "mosquito", "生命周期", "阶段", "幼虫", "蛹", "成虫")),
        PatternRule("evolution_classification", ("evolution", "natural selection", "adapt", "species", "classification", "ancestor", "进化", "自然选择", "物种", "分类", "祖先")),
        PatternRule("plant_biology", ("plant", "leaf", "root", "flower", "photosynthesis", "seed", "植物", "叶", "根", "花", "光合作用", "种子")),
        PatternRule("biochemistry_enzymes_metabolism", ("enzyme", "amino acid", "glucose", "atp", "metabolism", "lipid", "carbohydrate", "酶", "氨基酸", "葡萄糖", "代谢")),
        PatternRule("experimental_graph_data", ("experiment", "graph", "data", "chart", "curve", "实验", "曲线", "数据", "图表")),
    ),
    "chemistry": (
        PatternRule("molecular_structure_smiles_bonds", ("smiles", "structure", "bond", "molecule", "lewis", "geometry", "hybridization", "分子结构", "键", "路易斯", "杂化")),
        PatternRule("isomer_stereochemistry_nomenclature", ("isomer", "stereoisomer", "enantiomer", "cis", "trans", "chir", "nomenclature", "name the following", "boiling point", "异构", "对映", "顺反", "命名", "沸点")),
        PatternRule("stoichiometry_reaction_calculation", ("moles", "mass", "grams", "reaction", "yield", "stoichiometry", "equation", "化学方程", "物质的量", "质量", "产率")),
        PatternRule("thermochemistry_calorimetry", ("enthalpy", "heat", "calor", "specific heat", "temperature", "焓", "热量", "比热", "量热", "温度")),
        PatternRule("equilibrium_kinetics_gas", ("equilibrium", "rate", "kinetic", "pressure", "gas", "container", "平衡", "速率", "压强", "气体")),
        PatternRule("electrochemistry_redox", ("cell", "electrode", "voltage", "oxid", "reduc", "redox", "电池", "电极", "氧化", "还原")),
        PatternRule("acid_base_solution", ("acid", "base", "ph", "titration", "solution", "solubility", "酸", "碱", "滴定", "溶液", "溶解")),
        PatternRule("organic_reaction_mechanism", ("organic", "alkyl", "sn1", "sn2", "reaction mechanism", "benzene", "烃", "卤代", "有机", "机理")),
        PatternRule("periodic_atomic_bonding", ("periodic", "atomic", "ionization", "electronegativity", "intermolecular", "周期", "原子", "电负性", "分子间力")),
        PatternRule("lab_graph_data_interpretation", ("experiment", "graph", "data", "diagram", "实验", "曲线", "数据", "图表")),
    ),
}

DATASET_RULES: dict[str, tuple[PatternRule, ...]] = {
    "geometry3k": (
        PatternRule("angle_chasing", ("angle", "\\angle", "m angle", "measure of", "parallel", "perpendicular")),
        PatternRule("diagram_variable_solving", ("find x", "find y", "value of the variable", "in the figure")),
        PatternRule("segment_length", ("find dx", "find sp", "find af", "length", "side", "segment", "midpoint")),
        PatternRule("area_perimeter", ("area", "perimeter")),
        PatternRule("circle_arc_chord", ("circle", "arc", "chord", "tangent", "diameter", "radius", "circumference", "widehat")),
        PatternRule("trigonometric_ratio", ("tan", "sin", "cos")),
        PatternRule("similarity_congruence", ("similar", "congruent", "proportional", "scale")),
        PatternRule("right_triangle_pythagorean", ("right triangle", "hypotenuse", "pythagorean")),
        PatternRule("coordinate_geometry", ("coordinate", "slope", "line")),
    ),
    "emma_chemistry": (
        PatternRule("transition_state_smiles_selection", ("smiles", "transition-state", "transition state")),
        PatternRule("bond_counting", ("total number of bonds", "number of bonds", "single, double, and triple bonds")),
        PatternRule("molecular_structure_identification", ("structure", "molecule", "arrows")),
    ),
    "eee_bench": SUBJECT_RULES["circuit"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze pass samples under the ready dataset tree.")
    parser.add_argument("--ready-root", type=Path, default=DEFAULT_READY_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max-examples-per-class", type=int, default=5)
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def first_dict(items: Any) -> dict[str, Any]:
    if isinstance(items, list) and items and isinstance(items[0], dict):
        return items[0]
    return {}


def get_question(sample: dict[str, Any]) -> str:
    for path in (
        ("problem_main_record", "normalized_question_text"),
        ("clean_problem_record", "normalized_question_text"),
        ("normalized_assets", "normalized_question_text"),
        ("candidate_problem_record", "raw_question_text"),
        ("problem_main_record", "raw_question_text"),
    ):
        obj: Any = sample
        for key in path:
            obj = obj.get(key) if isinstance(obj, dict) else None
        text = as_text(obj).strip()
        if text:
            return text
    return ""


def get_answer(sample: dict[str, Any]) -> str:
    for path in (
        ("problem_main_record", "normalized_answer_text"),
        ("clean_problem_record", "normalized_answer_text"),
        ("normalized_assets", "normalized_answer_text"),
        ("candidate_problem_record", "raw_answer_text"),
        ("problem_main_record", "raw_answer_text"),
    ):
        obj: Any = sample
        for key in path:
            obj = obj.get(key) if isinstance(obj, dict) else None
        text = as_text(obj).strip()
        if text:
            return text
    return ""


def detect_language(text: str) -> str:
    cjk = len(CJK_RE.findall(text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if cjk and latin:
        return "mixed_zh_en" if cjk >= 8 and latin >= 8 else ("zh" if cjk > latin else "en")
    if cjk:
        return "zh"
    if latin:
        return "en"
    return "other"


def text_units(text: str) -> int:
    return len(CJK_RE.findall(text)) + len(WORD_RE.findall(text))


def sentence_count(text: str) -> int:
    parts = [p for p in re.split(r"[。！？.!?\n]+", text) if p.strip()]
    return len(parts)


def count_choice_map(sample: dict[str, Any]) -> int:
    for key in ("source_intake_record", "normalization_record"):
        obj = sample.get(key) or {}
        choice_map = obj.get("choice_map") or obj.get("normalized_choice_map") or {}
        if isinstance(choice_map, dict):
            return len(choice_map)
    return 0


def flatten_domain_tags(value: Any) -> list[str]:
    if isinstance(value, list):
        return [as_text(item) for item in value if as_text(item)]
    if isinstance(value, str) and value:
        return [value]
    return []


def image_paths(sample: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for key in ("image_path", "crop_path"):
        value = sample.get(key)
        if isinstance(value, str) and value:
            paths.append(value)
    for key in ("images", "crops", "image_paths", "crop_paths"):
        value = sample.get(key)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str) and item:
                    paths.append(item)
    return sorted(set(paths))


def image_stats(dataset_root: Path, rel_paths: list[str]) -> dict[str, Any]:
    widths: list[int] = []
    heights: list[int] = []
    sizes: list[int] = []
    missing = 0
    for rel in rel_paths:
        path = dataset_root / rel
        if not path.exists():
            missing += 1
            continue
        sizes.append(path.stat().st_size)
        if Image is not None:
            try:
                with Image.open(path) as img:
                    widths.append(img.width)
                    heights.append(img.height)
            except Exception:
                pass
    if not widths or not heights:
        return {"image_width_max": "", "image_height_max": "", "image_area_max": "", "image_file_size_max": max(sizes) if sizes else "", "missing_media_count": missing}
    return {
        "image_width_max": max(widths),
        "image_height_max": max(heights),
        "image_area_max": max(w * h for w, h in zip(widths, heights)),
        "image_file_size_max": max(sizes) if sizes else "",
        "missing_media_count": missing,
    }


def classify_sample(subject: str, dataset_key: str, question: str, answer: str, visual_kinds: list[str]) -> tuple[str, str]:
    text = f"{question}\n{answer}\n{' '.join(visual_kinds)}".lower()
    rules = DATASET_RULES.get(dataset_key) or SUBJECT_RULES.get(subject, ())
    hits: list[str] = []
    for rule in rules:
        if any(pattern.lower() in text for pattern in rule.patterns):
            hits.append(rule.label)
    if not hits:
        if "geometry" in visual_kinds:
            return "visual_diagram_reasoning", "visual_kind"
        return f"{subject}_other", "fallback"
    return hits[0], "keyword:" + hits[0]


def answer_shape(answer: str) -> str:
    stripped = answer.strip()
    if not stripped:
        return "empty"
    if len(stripped) <= 3 and re.fullmatch(r"[A-Da-d①②③④1-4]", stripped):
        return "choice_label"
    if re.fullmatch(r"[-+]?\d+(?:\.\d+)?(?:\s*(?:°|%|[A-Za-z/]+|Ω|次|N|V|mA|kg|cm|m|s))?", stripped):
        return "numeric_or_unit"
    if "$" in stripped or "\\" in stripped:
        return "formula_latex"
    if "\n" in stripped or ";" in stripped or "," in stripped:
        return "multi_part_text"
    if text_units(stripped) <= 5:
        return "short_text"
    return "long_text"


def extract_features(sample_path: Path, ready_root: Path) -> dict[str, Any]:
    sample = read_json(sample_path)
    dataset_root = sample_path.parents[1]
    subject = sample_path.parents[2].name
    dataset_key = sample_path.parents[1].name
    problem_main = sample.get("problem_main_record") or {}
    clean_problem = sample.get("clean_problem_record") or {}
    candidate = sample.get("candidate_problem_record") or {}
    text_structure = first_dict(sample.get("text_structure_records"))
    solvability = first_dict(sample.get("solvability_reports"))
    rewrite_report = first_dict(sample.get("rewrite_reports"))
    visual_records = sample.get("visual_structure_records") or []
    visual_kinds: list[str] = []
    visual_entity_count = 0
    visual_relation_count = 0
    visual_readability_scores: list[float] = []
    dark_pixel_ratios: list[float] = []
    for record in visual_records:
        if not isinstance(record, dict):
            continue
        attrs = record.get("global_attributes") or {}
        kind = as_text(attrs.get("visual_kind"))
        if kind:
            visual_kinds.append(kind)
        visual_entity_count += len(record.get("visual_entities") or [])
        visual_relation_count += len(record.get("visual_relations") or [])
        for source, bucket in ((attrs.get("readability_score"), visual_readability_scores), (attrs.get("dark_pixel_ratio"), dark_pixel_ratios)):
            try:
                bucket.append(float(source))
            except (TypeError, ValueError):
                pass

    node_records = sample.get("node_records") or []
    node_types = Counter(as_text(node.get("node_type")) for node in node_records if isinstance(node, dict))
    origin_kinds = Counter(as_text(node.get("origin_kind")) for node in node_records if isinstance(node, dict))

    question = get_question(sample)
    answer = get_answer(sample)
    rel_images = image_paths(sample)
    media = image_stats(dataset_root, rel_images)
    category, basis = classify_sample(subject, dataset_key, question, answer, visual_kinds)

    q_units = text_units(question)
    condition_count = len(text_structure.get("conditions") or [])
    target_count = len(text_structure.get("targets") or [])
    answer_slot_count = len(text_structure.get("answer_slots") or [])
    entity_count = len(text_structure.get("entity_mentions") or [])
    sentence_segments = len(text_structure.get("sentence_segments") or [])
    node_count = len(node_records)
    image_count = int(problem_main.get("image_count") or candidate.get("image_count") or len(rel_images) or 0)
    multi_step_score = float(problem_main.get("multi_step_score") or candidate.get("initial_multi_solution_score") or 0)
    multimodal_score = float(problem_main.get("multimodal_strength_score") or candidate.get("initial_image_dependency_score") or 0)
    complexity_index = (
        math.log1p(q_units)
        + 0.35 * condition_count
        + 0.45 * target_count
        + 0.25 * answer_slot_count
        + 0.08 * node_count
        + 0.15 * visual_entity_count
        + 1.2 * multi_step_score
        + 0.8 * multimodal_score
    )

    return {
        "subject": subject,
        "dataset_key": dataset_key,
        "dataset_path": str(dataset_root.relative_to(ready_root)),
        "sample_file": sample_path.name,
        "canonical_sample_id": as_text(sample.get("canonical_sample_id") or sample_path.stem),
        "canonical_sample_index": sample.get("canonical_sample_index", ""),
        "problem_id": as_text(problem_main.get("problem_id") or clean_problem.get("problem_id") or candidate.get("candidate_id")),
        "source_dataset": as_text(candidate.get("source_dataset") or problem_main.get("source_dataset")),
        "source_problem_id": as_text(candidate.get("source_problem_id") or problem_main.get("source_problem_id")),
        "question": question,
        "answer": answer,
        "solution_category": category,
        "category_basis": basis,
        "language": detect_language(question),
        "question_type": as_text(clean_problem.get("question_type") or text_structure.get("question_type") or problem_main.get("problem_type")),
        "answer_type": as_text(problem_main.get("answer_type") or first_dict(text_structure.get("answer_slots")).get("expected_answer_type")),
        "answer_shape": answer_shape(answer),
        "domain_tags": "|".join(flatten_domain_tags(problem_main.get("domain_tags"))),
        "question_char_len": len(question),
        "question_unit_len": q_units,
        "question_sentence_count": sentence_count(question),
        "question_line_count": len(question.splitlines()) if question else 0,
        "answer_char_len": len(answer),
        "answer_unit_len": text_units(answer),
        "latex_count": len(LATEX_RE.findall(question)),
        "numeric_token_count": len(NUM_RE.findall(question)),
        "has_choice_marker": bool(CHOICE_MARKER_RE.search(question)),
        "choice_count": count_choice_map(sample),
        "has_image_reference": bool(IMAGE_REF_RE.search(question)),
        "has_image": bool(problem_main.get("image_count") or candidate.get("has_image") or rel_images),
        "image_count": image_count,
        "media_path_count": len(rel_images),
        "requires_image": bool(problem_main.get("requires_image") or candidate.get("requires_image")),
        "text_dominant": bool(problem_main.get("text_dominant") or candidate.get("text_dominant")),
        "has_multiple_images": bool(problem_main.get("has_multiple_images")),
        "visual_record_count": len(visual_records),
        "visual_kinds": "|".join(sorted(set(visual_kinds))),
        "visual_entity_count": visual_entity_count,
        "visual_relation_count": visual_relation_count,
        "visual_readability_mean": round(mean(visual_readability_scores), 4) if visual_readability_scores else "",
        "dark_pixel_ratio_mean": round(mean(dark_pixel_ratios), 4) if dark_pixel_ratios else "",
        "condition_count": condition_count,
        "target_count": target_count,
        "answer_slot_count": answer_slot_count,
        "entity_mention_count": entity_count,
        "sentence_segment_count": sentence_segments,
        "node_count": node_count,
        "node_types": "|".join(f"{key}:{value}" for key, value in sorted(node_types.items()) if key),
        "origin_kinds": "|".join(f"{key}:{value}" for key, value in sorted(origin_kinds.items()) if key),
        "rewrite_strategy": as_text(rewrite_report.get("strategy") or problem_main.get("rewrite_strategy")),
        "path_mode": as_text(solvability.get("path_mode")),
        "solvability_score": solvability.get("solvability_score", ""),
        "multimodal_strength_score": problem_main.get("multimodal_strength_score", ""),
        "multi_step_score": problem_main.get("multi_step_score", ""),
        "verifiability_score": problem_main.get("verifiability_score", ""),
        "complexity_index": round(complexity_index, 4),
        **media,
    }


def quantiles(values: list[float]) -> dict[str, float | int | str]:
    if not values:
        return {"count": 0, "mean": "", "median": "", "p25": "", "p75": "", "min": "", "max": ""}
    values = sorted(values)

    def pct(p: float) -> float:
        if len(values) == 1:
            return values[0]
        idx = (len(values) - 1) * p
        lo = math.floor(idx)
        hi = math.ceil(idx)
        if lo == hi:
            return values[lo]
        return values[lo] * (hi - idx) + values[hi] * (idx - lo)

    return {
        "count": len(values),
        "mean": round(mean(values), 3),
        "median": round(median(values), 3),
        "p25": round(pct(0.25), 3),
        "p75": round(pct(0.75), 3),
        "min": round(values[0], 3),
        "max": round(values[-1], 3),
    }


def counter_top(rows: list[dict[str, Any]], key: str, n: int = 12) -> list[dict[str, Any]]:
    counter = Counter(as_text(row.get(key)) for row in rows)
    counter.pop("", None)
    return [{"value": value, "count": count, "pct": round(count / len(rows) * 100, 2)} for value, count in counter.most_common(n)]


def split_counter_top(rows: list[dict[str, Any]], key: str, sep: str = "|", n: int = 12) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for row in rows:
        for item in as_text(row.get(key)).split(sep):
            item = item.strip()
            if item:
                counter[item] += 1
    return [{"value": value, "count": count, "pct": round(count / len(rows) * 100, 2)} for value, count in counter.most_common(n)]


def numeric_column(rows: list[dict[str, Any]], key: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        value = row.get(key)
        if value == "" or value is None:
            continue
        try:
            values.append(float(value))
        except (TypeError, ValueError):
            pass
    return values


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sample_count": len(rows),
        "language": counter_top(rows, "language"),
        "question_type": counter_top(rows, "question_type"),
        "answer_shape": counter_top(rows, "answer_shape"),
        "solution_category": counter_top(rows, "solution_category", n=20),
        "visual_kinds": split_counter_top(rows, "visual_kinds", n=20),
        "path_mode": counter_top(rows, "path_mode"),
        "rewrite_strategy": counter_top(rows, "rewrite_strategy"),
        "domain_tags": split_counter_top(rows, "domain_tags", n=20),
        "question_unit_len": quantiles(numeric_column(rows, "question_unit_len")),
        "answer_unit_len": quantiles(numeric_column(rows, "answer_unit_len")),
        "latex_count": quantiles(numeric_column(rows, "latex_count")),
        "numeric_token_count": quantiles(numeric_column(rows, "numeric_token_count")),
        "image_count": quantiles(numeric_column(rows, "image_count")),
        "visual_entity_count": quantiles(numeric_column(rows, "visual_entity_count")),
        "condition_count": quantiles(numeric_column(rows, "condition_count")),
        "target_count": quantiles(numeric_column(rows, "target_count")),
        "answer_slot_count": quantiles(numeric_column(rows, "answer_slot_count")),
        "node_count": quantiles(numeric_column(rows, "node_count")),
        "complexity_index": quantiles(numeric_column(rows, "complexity_index")),
        "multimodal_strength_score": quantiles(numeric_column(rows, "multimodal_strength_score")),
        "multi_step_score": quantiles(numeric_column(rows, "multi_step_score")),
        "verifiability_score": quantiles(numeric_column(rows, "verifiability_score")),
        "has_image_pct": round(sum(1 for row in rows if row.get("has_image")) / len(rows) * 100, 2) if rows else 0,
        "requires_image_pct": round(sum(1 for row in rows if row.get("requires_image")) / len(rows) * 100, 2) if rows else 0,
        "has_choice_marker_pct": round(sum(1 for row in rows if row.get("has_choice_marker")) / len(rows) * 100, 2) if rows else 0,
    }


def build_examples(rows: list[dict[str, Any]], max_examples: int) -> dict[str, list[dict[str, Any]]]:
    examples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        category = as_text(row.get("solution_category"))
        if len(examples[category]) >= max_examples:
            continue
        examples[category].append(
            {
                "canonical_sample_id": row["canonical_sample_id"],
                "sample_file": row["sample_file"],
                "source_problem_id": row["source_problem_id"],
                "question_excerpt": as_text(row["question"])[:220].replace("\n", " "),
                "answer_excerpt": as_text(row["answer"])[:120].replace("\n", " "),
            }
        )
    return dict(examples)


def iter_sample_files(ready_root: Path) -> Iterable[Path]:
    yield from sorted(ready_root.glob("*/*/samples/*.json"))


def write_csv(path: Path, rows: list[dict[str, Any]], include_text: bool) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    if not include_text:
        fieldnames = [name for name in fieldnames if name not in {"question", "answer"}]
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(as_text(item).replace("\n", " ") for item in row) + " |")
    return lines


def write_markdown(output_dir: Path, rows: list[dict[str, Any]], summary: dict[str, Any], examples: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# Ready Pass Sample Feature Analysis")
    lines.append("")
    lines.append(f"- Total pass sample files: `{len(rows)}`")
    lines.append(f"- Dataset count: `{len(summary['datasets'])}`")
    lines.append("- Scope: all `ready/<subject>/<dataset>/samples/*.json` files.")
    lines.append("- Class labels are rule-based initial labels for fast diversity analysis; they should be treated as auditable draft tags, not final human taxonomy.")
    lines.append("")
    lines.append("## Overall Distribution")
    lines.append("")
    subject_counter = Counter(row["subject"] for row in rows)
    total = len(rows) or 1
    lines.extend(md_table(["Subject", "Pass Samples", "Share"], [[key, value, f"{value / total * 100:.2f}%"] for key, value in subject_counter.most_common()]))
    lines.append("")
    lines.append("## Dataset Overview")
    lines.append("")
    dataset_rows: list[list[Any]] = []
    for dataset_path, item in sorted(summary["datasets"].items()):
        dataset_rows.append(
            [
                dataset_path,
                item["sample_count"],
                ", ".join(f"{x['value']} {x['count']}" for x in item["solution_category"][:4]),
                item["question_unit_len"]["median"],
                item["requires_image_pct"],
                item["multi_step_score"]["median"],
                item["complexity_index"]["median"],
            ]
        )
    lines.extend(md_table(["Dataset", "N", "Top Categories", "Q Len Median", "Requires Image %", "Multi-step Median", "Complexity Median"], dataset_rows))
    lines.append("")
    lines.append("## Per-Dataset Detail")
    for dataset_path, item in sorted(summary["datasets"].items()):
        lines.append("")
        lines.append(f"### {dataset_path}")
        lines.append("")
        lines.append(f"- Samples: `{item['sample_count']}`")
        lines.append(f"- Median question units: `{item['question_unit_len']['median']}`; p25-p75: `{item['question_unit_len']['p25']}`-`{item['question_unit_len']['p75']}`")
        lines.append(f"- Median answer units: `{item['answer_unit_len']['median']}`")
        lines.append(f"- Requires image: `{item['requires_image_pct']}%`; has choice marker: `{item['has_choice_marker_pct']}%`")
        lines.append(f"- Median visual entities: `{item['visual_entity_count']['median']}`; median node count: `{item['node_count']['median']}`")
        lines.append(f"- Median scores: multimodal `{item['multimodal_strength_score']['median']}`, multi-step `{item['multi_step_score']['median']}`, verifiability `{item['verifiability_score']['median']}`")
        lines.append("")
        lines.extend(md_table(["Solution Category", "Count", "Share"], [[x["value"], x["count"], f"{x['pct']}%"] for x in item["solution_category"][:12]]))
        if item["visual_kinds"]:
            lines.append("")
            lines.extend(md_table(["Visual Kind", "Count", "Share"], [[x["value"], x["count"], f"{x['pct']}%"] for x in item["visual_kinds"][:8]]))
        dataset_examples = examples.get(dataset_path, {})
        if dataset_examples:
            lines.append("")
            lines.append("Representative examples:")
            for category, category_examples in list(dataset_examples.items())[:5]:
                if not category_examples:
                    continue
                ex = category_examples[0]
                lines.append(f"- `{category}`: `{ex['canonical_sample_id']}` - {ex['question_excerpt']}")
    lines.append("")
    lines.append("## Extracted Feature Families")
    lines.append("")
    feature_rows = [
        ["Text", "language, question length, answer length, sentence/line count, LaTeX count, numeric token count"],
        ["Task form", "question_type, answer_type, answer_shape, choice markers, answer slots"],
        ["Multimodal", "has_image, image_count, media size/dimensions, requires_image, visual kind, visual entity/relation counts"],
        ["Reasoning structure", "condition/target/entity counts, node count/types, path_mode, rewrite_strategy"],
        ["Scores", "multimodal_strength_score, multi_step_score, verifiability_score, solvability_score, derived complexity_index"],
        ["Taxonomy", "subject/domain tags plus rule-based solution_category per sample"],
    ]
    lines.extend(md_table(["Family", "Features"], feature_rows))
    (output_dir / "ready_sample_analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    ready_root = args.ready_root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = [extract_features(path, ready_root) for path in iter_sample_files(ready_root)]
    by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_dataset[row["dataset_path"]].append(row)
        by_subject[row["subject"]].append(row)

    summary = {
        "ready_root": str(ready_root),
        "sample_count": len(rows),
        "dataset_count": len(by_dataset),
        "overall": summarize_rows(rows),
        "subjects": {key: summarize_rows(value) for key, value in sorted(by_subject.items())},
        "datasets": {key: summarize_rows(value) for key, value in sorted(by_dataset.items())},
    }
    examples = {key: build_examples(value, args.max_examples_per_class) for key, value in sorted(by_dataset.items())}

    write_csv(output_dir / "ready_sample_features.csv", rows, include_text=False)
    write_csv(output_dir / "ready_sample_features_with_text.csv", rows, include_text=True)
    with (output_dir / "ready_sample_features.jsonl").open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")
    (output_dir / "ready_sample_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "ready_sample_category_examples.json").write_text(json.dumps(examples, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(output_dir, rows, summary, examples)

    print(json.dumps({"sample_count": len(rows), "dataset_count": len(by_dataset), "output_dir": str(output_dir)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
