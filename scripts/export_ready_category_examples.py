#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ANALYSIS_DIR = PROJECT_ROOT / "plans" / "ready_sample_analysis_2026-05-12"


@dataclass(frozen=True)
class CategoryHint:
    category: str
    hints: tuple[str, ...]


CATEGORY_HINTS = [
    CategoryHint("geometry_angle_chasing", ("angle", "\\angle", "∠", "角", "degree", "parallel")),
    CategoryHint("angle_chasing", ("angle", "\\angle", "∠", "角", "degree")),
    CategoryHint("geometry_length_area_volume", ("area", "perimeter", "volume", "length", "radius", "side", "面积", "周长")),
    CategoryHint("mechanics_kinematics_dynamics", ("velocity", "acceleration", "force", "friction", "spring", "motion", "速度", "加速度", "力")),
    CategoryHint("electromagnetism_circuits", ("electric", "magnetic", "current", "voltage", "charge", "电场", "磁场", "电流")),
    CategoryHint("dc_ac_network_analysis", ("current", "voltage", "resistance", "impedance", "thevenin", "norton", "circuit")),
    CategoryHint("cell_molecular_genetics", ("cell", "dna", "gene", "chromosome", "protein", "细胞", "基因")),
    CategoryHint("ecology_food_web_population", ("food web", "food chain", "population", "predator", "producer", "生态", "种群")),
    CategoryHint("transition_state_smiles_selection", ("smiles", "transition-state", "transition state")),
    CategoryHint("stoichiometry_reaction_calculation", ("moles", "reaction", "mass", "grams", "化学方程", "物质的量")),
    CategoryHint("molecular_structure_smiles_bonds", ("structure", "bond", "molecule", "smiles", "分子", "键")),
    CategoryHint("climate_weather_seasons", ("climate", "weather", "temperature", "precipitation", "气候", "降水", "气温")),
    CategoryHint("chart_graph_interpretation", ("graph", "chart", "table", "图", "图表", "曲线")),
    CategoryHint("population_urban_economic", ("population", "urban", "city", "econom", "人口", "城市", "经济")),
]

HINT_LOOKUP = {item.category: item.hints for item in CATEGORY_HINTS}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export one short example for every ready solution category.")
    parser.add_argument("--analysis-dir", type=Path, default=DEFAULT_ANALYSIS_DIR)
    parser.add_argument("--max-question-units", type=int, default=80)
    parser.add_argument("--max-answer-units", type=int, default=30)
    return parser.parse_args()


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def clean_text(text: str, max_chars: int = 260) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def load_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def score_row(row: dict[str, Any], max_question_units: int, max_answer_units: int) -> tuple[int, int, float, str]:
    q_len = as_int(row.get("question_unit_len"))
    a_len = as_int(row.get("answer_unit_len"))
    over_penalty = 0
    if q_len > max_question_units:
        over_penalty += q_len - max_question_units
    if a_len > max_answer_units:
        over_penalty += a_len - max_answer_units
    # Prefer concise, non-empty answers. Slightly prefer examples that still have
    # enough content to be understandable.
    empty_answer_penalty = 500 if not (row.get("answer") or "").strip() else 0
    return (over_penalty + empty_answer_penalty, q_len + a_len, as_float(row.get("complexity_index")), row.get("canonical_sample_id", ""))


def recommendation_score(row: dict[str, Any], max_question_units: int, max_answer_units: int) -> tuple[int, int, int, float, str]:
    q_len = as_int(row.get("question_unit_len"))
    a_len = as_int(row.get("answer_unit_len"))
    question = (row.get("question") or "").lower()
    category = row.get("solution_category") or ""
    hints = HINT_LOOKUP.get(category, ())
    has_hint = any(hint.lower() in question for hint in hints)
    fallback = "fallback" in (row.get("category_basis") or "")
    other = category.endswith("_other") or category == "math_other"
    too_short = q_len < 8
    too_long = q_len > max_question_units
    answer_too_long = a_len > max_answer_units
    empty_answer = not (row.get("answer") or "").strip()
    penalty = 0
    penalty += 0 if has_hint else 80
    penalty += 50 if fallback and not other else 0
    penalty += 35 if too_short else 0
    penalty += max(0, q_len - max_question_units) * 2 if too_long else 0
    penalty += max(0, a_len - max_answer_units) * 2 if answer_too_long else 0
    penalty += 500 if empty_answer else 0
    # Prefer concise examples after representativeness penalties are settled.
    target_distance = abs(q_len - 16)
    return (penalty, target_distance, q_len + a_len, as_float(row.get("complexity_index")), row.get("canonical_sample_id", ""))


def pick_examples(rows: list[dict[str, Any]], group_keys: tuple[str, ...], max_question_units: int, max_answer_units: int) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row[key] for key in group_keys)].append(row)

    examples = []
    for key, group_rows in sorted(grouped.items()):
        best = sorted(group_rows, key=lambda row: score_row(row, max_question_units, max_answer_units))[0]
        payload = {name: value for name, value in zip(group_keys, key)}
        payload.update(
            {
                "count": len(group_rows),
                "dataset_path": best["dataset_path"],
                "dataset_key": best["dataset_key"],
                "canonical_sample_id": best["canonical_sample_id"],
                "sample_file": best["sample_file"],
                "source_problem_id": best["source_problem_id"],
                "question_units": as_int(best.get("question_unit_len")),
                "answer_units": as_int(best.get("answer_unit_len")),
                "question_type": best["question_type"],
                "answer_shape": best["answer_shape"],
                "requires_image": best["requires_image"],
                "complexity_index": best["complexity_index"],
                "question": clean_text(best["question"], 320),
                "answer": clean_text(best["answer"], 180),
            }
        )
        examples.append(payload)
    return examples


def pick_recommended_examples(rows: list[dict[str, Any]], group_keys: tuple[str, ...], max_question_units: int, max_answer_units: int) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row[key] for key in group_keys)].append(row)

    examples = []
    for key, group_rows in sorted(grouped.items()):
        best = sorted(group_rows, key=lambda row: recommendation_score(row, max_question_units, max_answer_units))[0]
        payload = {name: value for name, value in zip(group_keys, key)}
        payload.update(
            {
                "count": len(group_rows),
                "dataset_path": best["dataset_path"],
                "dataset_key": best["dataset_key"],
                "canonical_sample_id": best["canonical_sample_id"],
                "sample_file": best["sample_file"],
                "source_problem_id": best["source_problem_id"],
                "question_units": as_int(best.get("question_unit_len")),
                "answer_units": as_int(best.get("answer_unit_len")),
                "question_type": best["question_type"],
                "answer_shape": best["answer_shape"],
                "requires_image": best["requires_image"],
                "complexity_index": best["complexity_index"],
                "category_basis": best.get("category_basis", ""),
                "question": clean_text(best["question"], 360),
                "answer": clean_text(best["answer"], 200),
            }
        )
        examples.append(payload)
    return examples


def md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        escaped = [str(item).replace("\n", " ").replace("|", "\\|") for item in row]
        lines.append("| " + " | ".join(escaped) + " |")
    return lines


def write_global_md(path: Path, examples: list[dict[str, Any]]) -> None:
    lines: list[str] = []
    lines.append("# 每个题型类别的一道简短例题")
    lines.append("")
    lines.append("选择规则：每个 `solution_category` 内优先选题干和答案最短、答案非空的样本。类别是当前规则初分标签。")
    lines.append("")
    table_rows = []
    for ex in sorted(examples, key=lambda item: (-item["count"], item["solution_category"])):
        table_rows.append(
            [
                ex["solution_category"],
                ex["count"],
                ex["dataset_path"],
                ex["canonical_sample_id"],
                ex["question"],
                ex["answer"],
            ]
        )
    lines.extend(md_table(["类别", "样本数", "数据集", "样本ID", "简短例题", "答案"], table_rows))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_recommended_global_md(path: Path, examples: list[dict[str, Any]]) -> None:
    lines: list[str] = []
    lines.append("# 每个题型类别的一道推荐简短例题")
    lines.append("")
    lines.append("选择规则：在简短的基础上，优先选择题干中出现该类别关键词、非 fallback、题干长度适中的样本；适合放在正文展示。")
    lines.append("")
    table_rows = []
    for ex in sorted(examples, key=lambda item: (-item["count"], item["solution_category"])):
        table_rows.append(
            [
                ex["solution_category"],
                ex["count"],
                ex["dataset_path"],
                ex["canonical_sample_id"],
                ex["question"],
                ex["answer"],
            ]
        )
    lines.extend(md_table(["类别", "样本数", "数据集", "样本ID", "推荐例题", "答案"], table_rows))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_dataset_md(path: Path, examples: list[dict[str, Any]]) -> None:
    lines: list[str] = []
    lines.append("# 每个数据集-题型类别的一道简短例题")
    lines.append("")
    lines.append("选择规则同全局版；这里按数据集展开，适合做附录或人工复核。")
    current_dataset = None
    table_rows: list[list[Any]] = []
    for ex in sorted(examples, key=lambda item: (item["dataset_path"], -item["count"], item["solution_category"])):
        if current_dataset is None:
            current_dataset = ex["dataset_path"]
        if ex["dataset_path"] != current_dataset:
            lines.append("")
            lines.append(f"## {current_dataset}")
            lines.append("")
            lines.extend(md_table(["类别", "样本数", "样本ID", "简短例题", "答案"], table_rows))
            table_rows = []
            current_dataset = ex["dataset_path"]
        table_rows.append([ex["solution_category"], ex["count"], ex["canonical_sample_id"], ex["question"], ex["answer"]])
    if current_dataset is not None:
        lines.append("")
        lines.append(f"## {current_dataset}")
        lines.append("")
        lines.extend(md_table(["类别", "样本数", "样本ID", "简短例题", "答案"], table_rows))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(path: Path, examples: list[dict[str, Any]]) -> None:
    if not examples:
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in examples:
        for key in row:
            if key not in seen:
                fieldnames.append(key)
                seen.add(key)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(examples)


def main() -> None:
    args = parse_args()
    analysis_dir = args.analysis_dir.resolve()
    rows = load_rows(analysis_dir / "ready_sample_features_with_text.csv")

    global_examples = pick_examples(rows, ("solution_category",), args.max_question_units, args.max_answer_units)
    dataset_examples = pick_examples(rows, ("dataset_path", "solution_category"), args.max_question_units, args.max_answer_units)
    recommended_global_examples = pick_recommended_examples(rows, ("solution_category",), args.max_question_units, args.max_answer_units)

    write_global_md(analysis_dir / "每个题型类别简短例题.md", global_examples)
    write_recommended_global_md(analysis_dir / "每个题型类别推荐简短例题.md", recommended_global_examples)
    write_dataset_md(analysis_dir / "每个数据集题型类别简短例题.md", dataset_examples)
    write_csv(analysis_dir / "global_category_short_examples.csv", global_examples)
    write_csv(analysis_dir / "global_category_recommended_examples.csv", recommended_global_examples)
    write_csv(analysis_dir / "dataset_category_short_examples.csv", dataset_examples)
    (analysis_dir / "category_short_examples.json").write_text(
        json.dumps({"global": global_examples, "global_recommended": recommended_global_examples, "by_dataset": dataset_examples}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({"global_categories": len(global_examples), "dataset_category_pairs": len(dataset_examples)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
