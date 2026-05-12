#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import re
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ANALYSIS_DIR = PROJECT_ROOT / "plans" / "ready_sample_analysis_2026-05-12"

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
SPACE_RE = re.compile(r"\s+")


CATEGORY_ZH = {
    "acid_base_solution": "酸碱与溶液性质",
    "agriculture_resources_environment": "农业资源与环境",
    "algebra_equation_inequality": "代数方程与不等式",
    "analog_electronics_devices": "模拟电子与器件电路",
    "anatomy_physiology": "解剖与生理结构",
    "angle_chasing": "几何角度追踪",
    "area_perimeter": "面积与周长计算",
    "astronomy_gravity_orbits": "天体引力与轨道",
    "biochemistry_enzymes_metabolism": "生化酶与代谢",
    "biology_other": "生物综合识图",
    "cell_molecular_genetics": "细胞、分子与遗传",
    "chart_graph_interpretation": "图表信息解读",
    "chemistry_other": "化学综合题",
    "circuit_other": "电子电路综合题",
    "circle_arc_chord": "圆、弧、弦与切线",
    "climate_weather_seasons": "气候、天气与季节",
    "control_systems_transfer_function": "控制系统与传递函数",
    "coordinate_geometry": "坐标几何",
    "coordinate_geometry_transform": "坐标几何与变换",
    "counting_probability_combinatorics": "计数、概率与组合",
    "dc_ac_network_analysis": "直流/交流电路网络分析",
    "diagram_variable_solving": "图形变量求解",
    "digital_logic_boolean": "数字逻辑与布尔函数",
    "earth_sun_moon_space": "地球、太阳与月相",
    "ecology_food_web_population": "生态、食物网与种群",
    "electrochemistry_redox": "电化学与氧化还原",
    "electromagnetics_fields": "电磁场与电磁波",
    "electromagnetism_circuits": "电磁学与物理电路",
    "equilibrium_kinetics_gas": "化学平衡、动力学与气体",
    "evolution_classification": "进化与分类",
    "experimental_graph_data": "实验与数据图表",
    "geography_other": "地理综合题",
    "geometry_angle_chasing": "几何角度追踪",
    "geometry_length_area_volume": "几何长度、面积与体积",
    "geomorphology_geology_hazards": "地貌、地质与灾害",
    "graph_data_interpretation": "物理图像与数据解读",
    "hydrology_ocean_rivers": "水文、河流与海洋",
    "isomer_stereochemistry_nomenclature": "异构、立体化学与命名",
    "lab_graph_data_interpretation": "实验图表与数据分析",
    "life_cycle_development": "生命史与发育阶段",
    "linear_programming_constraints": "线性规划与约束最值",
    "map_topography_location": "地图、地形与区位",
    "math_other": "数学综合题",
    "mechanics_kinematics_dynamics": "力学、运动学与动力学",
    "measurement_instrumentation": "测量与仪表",
    "measurement_time_units": "时间、单位与度量",
    "modern_quantum_nuclear_relativity": "近代物理、量子与相对论",
    "molecular_structure_identification": "分子结构识别",
    "molecular_structure_smiles_bonds": "分子结构、键与 SMILES",
    "number_theory_arithmetic": "数论与算术",
    "organic_reaction_mechanism": "有机反应机理",
    "periodic_atomic_bonding": "周期律、原子与成键",
    "physics_other": "物理综合题",
    "plant_biology": "植物结构与功能",
    "population_urban_economic": "人口、城市与经济地理",
    "power_electronics_converters": "电力电子与变换器",
    "power_machines_transformers": "电机、电力系统与变压器",
    "sequential_logic_microprocessor": "时序逻辑与微处理器",
    "sequence_pattern_logic": "序列、规律与逻辑",
    "segment_length": "线段长度求解",
    "signals_systems_filtering": "信号系统与滤波",
    "similarity_congruence": "相似与全等",
    "statistics_data_analysis": "统计与数据分析",
    "stoichiometry_reaction_calculation": "化学计量与反应计算",
    "thermochemistry_calorimetry": "热化学与量热",
    "thermo_fluids_gases": "热学、流体与气体",
    "transition_state_smiles_selection": "过渡态结构与 SMILES 选择",
    "trigonometric_ratio": "三角比计算",
    "visual_spatial_puzzle": "视觉空间与拼图推理",
    "waves_optics_sound": "波动、光学与声学",
}

REFINED_ZH = {
    "network_voltage_current": "节点电压、电流与等效网络",
    "logic_output_identification": "组合逻辑输出识别",
    "random_signal_communication": "随机信号与通信信息论",
    "oscillator_frequency": "振荡器与工作频率",
    "control_stability": "控制系统稳定性",
    "two_port_network": "二端口网络参数",
    "geometry_segment_measurement": "几何线段测量",
    "geometry_quadrilateral_polygon": "四边形与多边形性质",
    "geometry_generic_measurement": "图形通用量测",
    "math_puzzle_logic": "数学谜题与逻辑推理",
    "ratio_rate_application": "比例、配方与应用题",
    "data_table_statistics": "数据表与统计推断",
    "physics_conceptual_judgement": "物理概念判断",
    "advanced_mechanics": "高级力学与振动",
    "thermal_engine_refrigeration": "热机、制冷与能效",
    "physical_circuit_application": "物理电路应用",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build final taxonomy package and paper-style plots for ready samples.")
    parser.add_argument("--analysis-dir", type=Path, default=DEFAULT_ANALYSIS_DIR)
    parser.add_argument("--calibration-per-category", type=int, default=20)
    parser.add_argument("--translate-representatives", action="store_true", help="Translate representative questions with MyMemory API.")
    parser.add_argument("--translate-limit", type=int, default=220)
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def clean_text(text: str, max_chars: int | None = None) -> str:
    text = SPACE_RE.sub(" ", text or "").strip()
    if max_chars and len(text) > max_chars:
        return text[: max_chars - 3].rstrip() + "..."
    return text


def has_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text or ""))


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def final_category(row: dict[str, Any]) -> tuple[str, str, str]:
    dataset = row["dataset_path"].replace("/", "\\")
    category = row["solution_category"]
    q = f"{row.get('question','')} {row.get('answer','')}".lower()

    refined = ""
    if dataset == "circuit\\eee_bench" and category == "circuit_other":
        if any(x in q for x in ["autocorrelation", "random process", "power spectral", "binary symmetric", "gaussian", "receiver"]):
            refined = "random_signal_communication"
        elif any(x in q for x in ["output y", "output f", "full subtractor", "logic", "binary", "boolean"]):
            refined = "logic_output_identification"
        elif any(x in q for x in ["oscillator", "operating frequency"]):
            refined = "oscillator_frequency"
        elif any(x in q for x in ["stable", "feedback", "range of k"]):
            refined = "control_stability"
        elif any(x in q for x in ["z-matrix", "two-port"]):
            refined = "two_port_network"
        elif any(x in q for x in ["potential", "voltage", "current", "capacitance", "resistance", "uab", " va", " v_a", "circuit shown"]):
            refined = "network_voltage_current"
    elif dataset == "math\\geometry3k" and category == "math_other":
        if any(x in q for x in ["find $", "find ax", "find bc", "find af", "find sp", "find wt", "find gh", "find yz", "find cd", "find x", "find y"]):
            refined = "geometry_segment_measurement"
        if any(x in q for x in ["kite", "square", "rhombus", "parallelogram", "trapezoid", "polygon"]):
            refined = "geometry_quadrilateral_polygon"
        if any(x in q for x in ["circle", "\\odot", "widehat", "circumference"]):
            refined = "circle_arc_chord"
        if not refined:
            refined = "geometry_generic_measurement"
    elif dataset == "math\\geoqa_plus" and category == "math_other":
        if any(x in q for x in ["route", "ways", "vertices", "die", "numbered", "sum of the numbers"]):
            refined = "math_puzzle_logic"
        elif any(x in q for x in ["recipe", "largest number", "liters", "eggs", "flour", "ratio"]):
            refined = "ratio_rate_application"
        elif any(x in q for x in ["graph", "table", "chart", "data"]):
            refined = "data_table_statistics"
        else:
            refined = "math_puzzle_logic"
    elif dataset == "math\\scemqa_math" and category == "math_other":
        if any(x in q for x in ["box plot", "regression", "data", "table", "scatter"]):
            refined = "data_table_statistics"
        elif any(x in q for x in ["function", "graph", "equation"]):
            refined = "algebra_equation_inequality"
        else:
            refined = "math_puzzle_logic"
    elif dataset == "physics\\multi_physics" and category == "physics_other":
        if any(x in q for x in ["电路", "电流", "电压", "circuit", "saturation", "amplifier"]):
            refined = "physical_circuit_application"
        else:
            refined = "physics_conceptual_judgement"
    elif dataset == "physics\\phyx" and category == "physics_other":
        if any(x in q for x in ["cop", "heat engine", "refrigerator", "efficiency"]):
            refined = "thermal_engine_refrigeration"
        elif any(x in q for x in ["circuit", "mutual inductance", "capacitor", "resistor"]):
            refined = "physical_circuit_application"
        elif any(x in q for x in ["time period", "oscillation", "normal mode"]):
            refined = "advanced_mechanics"
        else:
            refined = "physics_conceptual_judgement"
    elif dataset == "physics\\seephys" and category == "physics_other":
        if any(x in q for x in ["circuit", "bulb", "resistor", "current", "capacitor"]):
            refined = "physical_circuit_application"
        elif any(x in q for x in ["lagrangian", "hamiltonian", "normal mode", "oscillation"]):
            refined = "advanced_mechanics"
        else:
            refined = "physics_conceptual_judgement"

    key = refined or category
    if dataset == "circuit\\eee_bench":
        merge_map = {
            "logic_output_identification": "digital_logic_boolean",
            "random_signal_communication": "signals_systems_filtering",
            "oscillator_frequency": "analog_electronics_devices",
            "control_stability": "control_systems_transfer_function",
            "two_port_network": "dc_ac_network_analysis",
        }
        key = merge_map.get(key, key)
    zh = REFINED_ZH.get(key) or CATEGORY_ZH.get(key) or key
    basis = f"refined:{refined}" if refined else f"mapped:{category}"
    return key, zh, basis


def translate_question(text: str, cache: dict[str, str], enabled: bool, limit: int) -> tuple[str, str]:
    text = clean_text(text)
    if not text:
        return "", "empty"
    if has_cjk(text):
        return text, "original_zh"
    if not enabled:
        return "", "pending_translation"
    source = text[:limit]
    digest = hashlib.sha1(source.encode("utf-8")).hexdigest()
    if digest in cache:
        return cache[digest], "machine_cached"
    url = "https://api.mymemory.translated.net/get?q=" + urllib.parse.quote(source) + "&langpair=en%7Czh-CN"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        translated = clean_text((payload.get("responseData") or {}).get("translatedText") or "")
        if translated:
            cache[digest] = translated
            time.sleep(0.25)
            return translated, "machine_mymemory"
    except Exception:
        return "", "translation_failed"
    return "", "translation_empty"


def quantiles(values: list[float]) -> dict[str, Any]:
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


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
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


def row_score(row: dict[str, Any]) -> tuple[int, int, float, str]:
    q_len = as_int(row.get("question_unit_len"))
    a_len = as_int(row.get("answer_unit_len"))
    return (abs(q_len - 24), q_len + a_len, as_float(row.get("complexity_index")), row["canonical_sample_id"])


def category_stats(rows: list[dict[str, Any]], total: int) -> dict[str, Any]:
    values = lambda key: [as_float(row.get(key)) for row in rows if row.get(key) not in ("", None)]
    return {
        "count": len(rows),
        "share_pct": round(len(rows) / total * 100, 2) if total else 0,
        "question_len": quantiles(values("question_unit_len")),
        "answer_len": quantiles(values("answer_unit_len")),
        "complexity": quantiles(values("complexity_index")),
        "multi_step": quantiles(values("multi_step_score")),
        "visual_entity_count": quantiles(values("visual_entity_count")),
        "requires_image_pct": round(sum(str(row.get("requires_image")) == "True" for row in rows) / len(rows) * 100, 2) if rows else 0,
        "question_type": Counter(row.get("question_type", "") for row in rows).most_common(5),
        "answer_shape": Counter(row.get("answer_shape", "") for row in rows).most_common(5),
        "visual_kinds": Counter(row.get("visual_kinds", "") for row in rows).most_common(5),
    }


def build_dataset_package(dataset: str, rows: list[dict[str, Any]], output_root: Path, cache: dict[str, str], translate: bool, translate_limit: int, calibration_n: int) -> dict[str, Any]:
    safe_name = dataset.replace("\\", "__").replace("/", "__")
    ds_dir = output_root / safe_name
    ds_dir.mkdir(parents=True, exist_ok=True)

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["final_category"]].append(row)

    taxonomy_rows = []
    stat_rows = []
    rep_rows = []
    sample_rows = []
    calibration_rows = []
    rng = random.Random(20260512)

    for category, group in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        stats = category_stats(group, len(rows))
        category_zh = group[0]["final_category_zh"]
        taxonomy_rows.append(
            {
                "dataset": dataset,
                "final_category": category,
                "final_category_zh": category_zh,
                "count": stats["count"],
                "share_pct": stats["share_pct"],
                "definition_zh": f"需要运用“{category_zh}”相关知识或解法的题目。",
                "source_rule": group[0]["final_category_basis"],
            }
        )
        stat_rows.append(
            {
                "dataset": dataset,
                "final_category": category,
                "final_category_zh": category_zh,
                "count": stats["count"],
                "share_pct": stats["share_pct"],
                "question_len_median": stats["question_len"]["median"],
                "question_len_p25": stats["question_len"]["p25"],
                "question_len_p75": stats["question_len"]["p75"],
                "answer_len_median": stats["answer_len"]["median"],
                "complexity_median": stats["complexity"]["median"],
                "multi_step_median": stats["multi_step"]["median"],
                "visual_entity_median": stats["visual_entity_count"]["median"],
                "requires_image_pct": stats["requires_image_pct"],
                "top_question_type": stats["question_type"][0][0] if stats["question_type"] else "",
                "top_answer_shape": stats["answer_shape"][0][0] if stats["answer_shape"] else "",
                "top_visual_kind": stats["visual_kinds"][0][0] if stats["visual_kinds"] else "",
            }
        )
        representative = sorted(group, key=row_score)[0]
        q_zh, trans_status = translate_question(representative["question"], cache, translate, translate_limit)
        rep_rows.append(
            {
                "dataset": dataset,
                "final_category": category,
                "final_category_zh": category_zh,
                "canonical_sample_id": representative["canonical_sample_id"],
                "sample_file": representative["sample_file"],
                "source_problem_id": representative["source_problem_id"],
                "question": clean_text(representative["question"], 650),
                "question_zh": q_zh,
                "translation_status": trans_status,
                "answer": clean_text(representative["answer"], 260),
                "question_units": representative["question_unit_len"],
                "complexity_index": representative["complexity_index"],
            }
        )
        sorted_group = sorted(group, key=lambda item: (as_int(item.get("question_unit_len")), item["canonical_sample_id"]))
        if len(sorted_group) <= calibration_n:
            selected = sorted_group
        else:
            selected = sorted_group[: min(5, calibration_n)]
            rest = [item for item in group if item not in selected]
            selected.extend(rng.sample(rest, min(calibration_n - len(selected), len(rest))))
        for item in selected:
            q_zh, trans_status = translate_question(item["question"], cache, False, translate_limit)
            calibration_rows.append(
                {
                    "dataset": dataset,
                    "final_category": category,
                    "final_category_zh": category_zh,
                    "canonical_sample_id": item["canonical_sample_id"],
                    "sample_file": item["sample_file"],
                    "question": clean_text(item["question"], 500),
                    "question_zh": q_zh,
                    "translation_status": trans_status,
                    "answer": clean_text(item["answer"], 220),
                    "question_units": item["question_unit_len"],
                    "complexity_index": item["complexity_index"],
                }
            )

    for row in sorted(rows, key=lambda item: as_int(item.get("canonical_sample_index"))):
        sample_rows.append(
            {
                "dataset": dataset,
                "canonical_sample_id": row["canonical_sample_id"],
                "sample_file": row["sample_file"],
                "source_problem_id": row["source_problem_id"],
                "final_category": row["final_category"],
                "final_category_zh": row["final_category_zh"],
                "question": clean_text(row["question"], 500),
                "question_zh": row["question"] if has_cjk(row["question"]) else "",
                "translation_status": "original_zh" if has_cjk(row["question"]) else "not_translated_in_full_list",
                "answer": clean_text(row["answer"], 220),
                "question_units": row["question_unit_len"],
                "complexity_index": row["complexity_index"],
                "multi_step_score": row["multi_step_score"],
                "visual_kinds": row["visual_kinds"],
            }
        )

    write_csv(ds_dir / "taxonomy.csv", taxonomy_rows)
    write_csv(ds_dir / "sample_list.csv", sample_rows)
    write_csv(ds_dir / "representative_examples.csv", rep_rows)
    write_csv(ds_dir / "feature_stats.csv", stat_rows)
    write_csv(ds_dir / "calibration_samples.csv", calibration_rows)

    md_lines: list[str] = []
    md_lines.append(f"# {dataset} final taxonomy package")
    md_lines.append("")
    md_lines.append(f"- 样本数：{len(rows)}")
    md_lines.append(f"- 最终类别数：{len(grouped)}")
    md_lines.append("")
    md_lines.append("## Taxonomy")
    md_lines.append("")
    md_lines.extend(md_table(["类别", "中文名", "数量", "占比", "定义"], [[r["final_category"], r["final_category_zh"], r["count"], f"{r['share_pct']}%", r["definition_zh"]] for r in taxonomy_rows]))
    md_lines.append("")
    md_lines.append("## 代表例题")
    md_lines.append("")
    md_lines.extend(md_table(["中文类别", "样本ID", "题目", "中文题意", "答案"], [[r["final_category_zh"], r["canonical_sample_id"], r["question"], r["question_zh"], r["answer"]] for r in rep_rows]))
    md_lines.append("")
    md_lines.append("## 特征统计")
    md_lines.append("")
    md_lines.extend(md_table(["中文类别", "N", "题长中位数", "复杂度中位数", "multi-step中位数", "需图像%"], [[r["final_category_zh"], r["count"], r["question_len_median"], r["complexity_median"], r["multi_step_median"], r["requires_image_pct"]] for r in stat_rows]))
    (ds_dir / "README.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    return {
        "dataset": dataset,
        "sample_count": len(rows),
        "category_count": len(grouped),
        "top_category": taxonomy_rows[0]["final_category"] if taxonomy_rows else "",
        "top_category_zh": taxonomy_rows[0]["final_category_zh"] if taxonomy_rows else "",
        "top_category_share_pct": taxonomy_rows[0]["share_pct"] if taxonomy_rows else 0,
        "directory": str(ds_dir.relative_to(output_root.parent)),
    }


def plot_outputs(all_rows: list[dict[str, Any]], output_root: Path) -> None:
    import matplotlib.pyplot as plt

    fig_dir = output_root / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    def save_bar(path: Path, labels: list[str], values: list[float], title: str, xlabel: str) -> None:
        fig, ax = plt.subplots(figsize=(10, max(4, 0.35 * len(labels) + 1)))
        y = range(len(labels))
        ax.barh(list(y), values, color="#4C78A8")
        ax.set_yticks(list(y))
        ax.set_yticklabels(labels, fontsize=8)
        ax.invert_yaxis()
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.grid(axis="x", alpha=0.25)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)

    subject = Counter(row["subject"] for row in all_rows)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(list(subject.values()), labels=list(subject.keys()), autopct="%1.1f%%", startangle=90)
    ax.set_title("Subject Distribution")
    fig.tight_layout()
    fig.savefig(fig_dir / "paper_subject_pie.png", dpi=200)
    plt.close(fig)

    by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in all_rows:
        by_dataset[row["dataset_path"]].append(row)

    # Question length boxplot.
    labels = list(sorted(by_dataset))
    data = [[as_float(row["question_unit_len"]) for row in by_dataset[label]] for label in labels]
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.boxplot(data, labels=[label.split("\\")[-1] for label in labels], showfliers=False)
    ax.set_title("Question Length Distribution by Dataset")
    ax.set_ylabel("word/CJK units")
    ax.tick_params(axis="x", labelrotation=60, labelsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "paper_question_length_boxplot.png", dpi=200)
    plt.close(fig)

    category = Counter(row["final_category"] for row in all_rows)
    top = category.most_common(25)
    save_bar(fig_dir / "paper_final_category_bar.png", [x[0] for x in top], [x[1] for x in top], "Top Final Taxonomy Categories", "samples")

    # Multi-step distribution.
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist([as_float(row["multi_step_score"]) for row in all_rows], bins=30, color="#54A24B", alpha=0.85)
    ax.set_title("Multi-step Score Distribution")
    ax.set_xlabel("multi_step_score")
    ax.set_ylabel("samples")
    fig.tight_layout()
    fig.savefig(fig_dir / "paper_multistep_histogram.png", dpi=200)
    plt.close(fig)

    visual_counter: Counter[str] = Counter()
    for row in all_rows:
        for part in (row.get("visual_kinds") or "").split("|"):
            if part:
                visual_counter[part] += 1
    top_visual = visual_counter.most_common(15)
    save_bar(fig_dir / "paper_visual_type_bar.png", [x[0] for x in top_visual], [x[1] for x in top_visual], "Visual Type Distribution", "samples")

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter([as_float(row["question_unit_len"]) for row in all_rows], [as_float(row["complexity_index"]) for row in all_rows], s=4, alpha=0.2, color="#F58518")
    ax.set_title("Complexity vs. Question Length")
    ax.set_xlabel("question length")
    ax.set_ylabel("complexity index")
    fig.tight_layout()
    fig.savefig(fig_dir / "paper_complexity_scatter.png", dpi=200)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    analysis_dir = args.analysis_dir.resolve()
    output_root = analysis_dir / "final_taxonomy_package"
    output_root.mkdir(parents=True, exist_ok=True)
    cache_path = output_root / "translation_cache.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}

    rows = read_rows(analysis_dir / "ready_sample_features_with_text.csv")
    enriched_rows = []
    for row in rows:
        key, zh, basis = final_category(row)
        row = dict(row)
        row["final_category"] = key
        row["final_category_zh"] = zh
        row["final_category_basis"] = basis
        enriched_rows.append(row)

    by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in enriched_rows:
        by_dataset[row["dataset_path"].replace("/", "\\")].append(row)

    summaries = []
    for dataset, dataset_rows in sorted(by_dataset.items()):
        summaries.append(build_dataset_package(dataset, dataset_rows, output_root, cache, args.translate_representatives, args.translate_limit, args.calibration_per_category))

    write_csv(output_root / "all_samples_with_final_taxonomy.csv", [
        {
            "dataset": row["dataset_path"].replace("/", "\\"),
            "canonical_sample_id": row["canonical_sample_id"],
            "final_category": row["final_category"],
            "final_category_zh": row["final_category_zh"],
            "question": clean_text(row["question"], 500),
            "question_zh": row["question"] if has_cjk(row["question"]) else "",
            "answer": clean_text(row["answer"], 220),
            "question_units": row["question_unit_len"],
            "complexity_index": row["complexity_index"],
        }
        for row in enriched_rows
    ])
    write_csv(output_root / "dataset_summary.csv", summaries)
    plot_outputs(enriched_rows, output_root)
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md = ["# Final Taxonomy Package", "", "每个数据集均包含 taxonomy、sample_list、representative_examples、feature_stats、calibration_samples 五个文件。", ""]
    md.extend(md_table(["数据集", "样本数", "类别数", "最大类", "最大类占比", "目录"], [[s["dataset"], s["sample_count"], s["category_count"], s["top_category_zh"], f"{s['top_category_share_pct']}%", s["directory"]] for s in summaries]))
    (output_root / "README.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"datasets": len(summaries), "output_root": str(output_root), "translate": args.translate_representatives}, ensure_ascii=False))


if __name__ == "__main__":
    main()
