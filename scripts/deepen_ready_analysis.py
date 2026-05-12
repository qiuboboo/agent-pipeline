#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ANALYSIS_DIR = PROJECT_ROOT / "plans" / "ready_sample_analysis_2026-05-12"


NUMERIC_COLUMNS = [
    "question_unit_len",
    "answer_unit_len",
    "latex_count",
    "numeric_token_count",
    "image_count",
    "visual_entity_count",
    "condition_count",
    "target_count",
    "answer_slot_count",
    "node_count",
    "complexity_index",
    "multimodal_strength_score",
    "multi_step_score",
    "verifiability_score",
]

LENGTH_BUCKETS = [
    (0, 10, "short_0_10"),
    (11, 25, "medium_short_11_25"),
    (26, 50, "medium_26_50"),
    (51, 100, "long_51_100"),
    (101, 10**9, "very_long_101_plus"),
]

COMPLEXITY_BUCKETS = [
    (0, 6, "low_under_6"),
    (6, 8, "medium_6_8"),
    (8, 10, "high_8_10"),
    (10, 10**9, "very_high_10_plus"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build deeper dataset-level summaries from ready_sample_features_with_text.csv.")
    parser.add_argument("--analysis-dir", type=Path, default=DEFAULT_ANALYSIS_DIR)
    parser.add_argument("--max-categories", type=int, default=15)
    parser.add_argument("--examples-per-category", type=int, default=3)
    return parser.parse_args()


def as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def as_float(value: Any) -> float | None:
    if value in ("", None):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_rows(analysis_dir: Path) -> list[dict[str, Any]]:
    path = analysis_dir / "ready_sample_features_with_text.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


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


def numeric_values(rows: list[dict[str, Any]], key: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        value = as_float(row.get(key))
        if value is not None:
            values.append(value)
    return values


def bucket(value: float, buckets: list[tuple[int, int, str]]) -> str:
    for lo, hi, label in buckets:
        if lo <= value <= hi:
            return label
    return buckets[-1][2]


def top_counter(rows: list[dict[str, Any]], key: str, limit: int = 10) -> list[dict[str, Any]]:
    counter = Counter(as_text(row.get(key)) for row in rows)
    counter.pop("", None)
    total = len(rows) or 1
    return [{"value": value, "count": count, "pct": round(count / total * 100, 2)} for value, count in counter.most_common(limit)]


def shannon_entropy(counter: Counter[str]) -> float:
    total = sum(counter.values())
    if total == 0:
        return 0.0
    return -sum((count / total) * math.log(count / total, 2) for count in counter.values() if count)


def hhi(counter: Counter[str]) -> float:
    total = sum(counter.values())
    if total == 0:
        return 0.0
    return sum((count / total) ** 2 for count in counter.values())


def concentration_label(top1_share: float) -> str:
    if top1_share >= 0.8:
        return "single_dominant"
    if top1_share >= 0.6:
        return "strongly_concentrated"
    if top1_share >= 0.4:
        return "moderately_concentrated"
    return "diverse"


def summarize_category(rows: list[dict[str, Any]], examples_per_category: int) -> dict[str, Any]:
    examples = []
    for row in rows[:examples_per_category]:
        examples.append(
            {
                "canonical_sample_id": row["canonical_sample_id"],
                "sample_file": row["sample_file"],
                "source_problem_id": row["source_problem_id"],
                "question_excerpt": as_text(row["question"])[:260].replace("\n", " "),
                "answer_excerpt": as_text(row["answer"])[:140].replace("\n", " "),
            }
        )
    return {
        "count": len(rows),
        "question_len": quantiles(numeric_values(rows, "question_unit_len")),
        "complexity": quantiles(numeric_values(rows, "complexity_index")),
        "multi_step": quantiles(numeric_values(rows, "multi_step_score")),
        "requires_image_pct": round(sum(row.get("requires_image") == "True" for row in rows) / len(rows) * 100, 2) if rows else 0,
        "question_type": top_counter(rows, "question_type", 5),
        "answer_shape": top_counter(rows, "answer_shape", 5),
        "visual_kinds": top_counter(rows, "visual_kinds", 5),
        "examples": examples,
    }


def summarize_dataset(rows: list[dict[str, Any]], max_categories: int, examples_per_category: int) -> dict[str, Any]:
    category_counter = Counter(row["solution_category"] for row in rows)
    top_counts = category_counter.most_common()
    total = len(rows) or 1
    top1_share = top_counts[0][1] / total if top_counts else 0.0
    top3_share = sum(count for _, count in top_counts[:3]) / total
    entropy = shannon_entropy(category_counter)
    effective_categories = 2**entropy if entropy else 0.0
    length_counter = Counter(bucket(as_float(row.get("question_unit_len")) or 0, LENGTH_BUCKETS) for row in rows)
    complexity_counter = Counter(bucket(as_float(row.get("complexity_index")) or 0, COMPLEXITY_BUCKETS) for row in rows)

    category_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        category_groups[row["solution_category"]].append(row)

    category_summaries: dict[str, Any] = {}
    for category, count in top_counts[:max_categories]:
        category_summaries[category] = {
            "share_pct": round(count / total * 100, 2),
            **summarize_category(category_groups[category], examples_per_category),
        }

    return {
        "sample_count": len(rows),
        "category_count": len(category_counter),
        "top1_category": top_counts[0][0] if top_counts else "",
        "top1_share_pct": round(top1_share * 100, 2),
        "top3_share_pct": round(top3_share * 100, 2),
        "entropy_bits": round(entropy, 3),
        "effective_category_count": round(effective_categories, 2),
        "hhi": round(hhi(category_counter), 4),
        "concentration_label": concentration_label(top1_share),
        "length_buckets": [{"bucket": key, "count": value, "pct": round(value / total * 100, 2)} for key, value in length_counter.most_common()],
        "complexity_buckets": [{"bucket": key, "count": value, "pct": round(value / total * 100, 2)} for key, value in complexity_counter.most_common()],
        "question_len": quantiles(numeric_values(rows, "question_unit_len")),
        "answer_len": quantiles(numeric_values(rows, "answer_unit_len")),
        "complexity": quantiles(numeric_values(rows, "complexity_index")),
        "node_count": quantiles(numeric_values(rows, "node_count")),
        "visual_entity_count": quantiles(numeric_values(rows, "visual_entity_count")),
        "multi_step": quantiles(numeric_values(rows, "multi_step_score")),
        "multimodal": quantiles(numeric_values(rows, "multimodal_strength_score")),
        "verifiability": quantiles(numeric_values(rows, "verifiability_score")),
        "language": top_counter(rows, "language", 5),
        "question_type": top_counter(rows, "question_type", 5),
        "answer_shape": top_counter(rows, "answer_shape", 6),
        "path_mode": top_counter(rows, "path_mode", 3),
        "rewrite_strategy": top_counter(rows, "rewrite_strategy", 5),
        "categories": category_summaries,
    }


def pearson(rows: list[dict[str, Any]], x_key: str, y_key: str) -> float | None:
    pairs: list[tuple[float, float]] = []
    for row in rows:
        x = as_float(row.get(x_key))
        y = as_float(row.get(y_key))
        if x is not None and y is not None:
            pairs.append((x, y))
    if len(pairs) < 2:
        return None
    xs = [x for x, _ in pairs]
    ys = [y for _, y in pairs]
    mx = mean(xs)
    my = mean(ys)
    num = sum((x - mx) * (y - my) for x, y in pairs)
    den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return round(num / (den_x * den_y), 4)


def build_rankings(dataset_summary: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    def rank(key_path: tuple[str, ...], reverse: bool = True, limit: int = 8) -> list[dict[str, Any]]:
        items = []
        for dataset, item in dataset_summary.items():
            value: Any = item
            for key in key_path:
                value = value.get(key, {}) if isinstance(value, dict) else {}
            if isinstance(value, (int, float)):
                items.append({"dataset": dataset, "value": value})
        return sorted(items, key=lambda x: x["value"], reverse=reverse)[:limit]

    return {
        "longest_question_median": rank(("question_len", "median")),
        "highest_complexity_median": rank(("complexity", "median")),
        "highest_effective_category_count": rank(("effective_category_count",)),
        "highest_top1_concentration": rank(("top1_share_pct",)),
        "lowest_top1_concentration": rank(("top1_share_pct",), reverse=False),
        "highest_multistep_median": rank(("multi_step", "median")),
    }


def build_outliers(rows: list[dict[str, Any]], limit: int = 30) -> dict[str, list[dict[str, Any]]]:
    def take(key: str) -> list[dict[str, Any]]:
        ranked = sorted(rows, key=lambda row: as_float(row.get(key)) or -1, reverse=True)[:limit]
        return [
            {
                "dataset_path": row["dataset_path"],
                "canonical_sample_id": row["canonical_sample_id"],
                "sample_file": row["sample_file"],
                "solution_category": row["solution_category"],
                key: row.get(key),
                "question_excerpt": as_text(row["question"])[:220].replace("\n", " "),
            }
            for row in ranked
        ]

    return {
        "longest_questions": take("question_unit_len"),
        "highest_complexity": take("complexity_index"),
        "most_nodes": take("node_count"),
        "most_visual_entities": take("visual_entity_count"),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                fieldnames.append(key)
                seen.add(key)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(as_text(item).replace("\n", " ") for item in row) + " |")
    return lines


def write_markdown(path: Path, deep: dict[str, Any]) -> None:
    datasets = deep["datasets"]
    lines: list[str] = []
    lines.append("# Ready 样本深度特征分析")
    lines.append("")
    lines.append("本报告基于规则初分标签和结构化特征表，目标是判断每个数据集的题型多样性、集中度、长度/复杂度分布和代表样本。")
    lines.append("")
    lines.append("## 数据集多样性排名")
    lines.append("")
    rank_rows = []
    for item in deep["rankings"]["highest_effective_category_count"]:
        ds = item["dataset"]
        rank_rows.append([ds, item["value"], datasets[ds]["top1_category"], datasets[ds]["top1_share_pct"], datasets[ds]["top3_share_pct"], datasets[ds]["concentration_label"]])
    lines.extend(md_table(["Dataset", "Effective Categories", "Top1", "Top1 %", "Top3 %", "Label"], rank_rows))
    lines.append("")
    lines.append("## 高集中度数据集")
    lines.append("")
    concentrated_rows = []
    for item in deep["rankings"]["highest_top1_concentration"]:
        ds = item["dataset"]
        concentrated_rows.append([ds, datasets[ds]["top1_category"], item["value"], datasets[ds]["effective_category_count"], datasets[ds]["sample_count"]])
    lines.extend(md_table(["Dataset", "Dominant Category", "Top1 %", "Effective Categories", "N"], concentrated_rows))
    lines.append("")
    lines.append("## 长题和复杂题")
    lines.append("")
    long_rows = []
    for item in deep["rankings"]["longest_question_median"]:
        ds = item["dataset"]
        long_rows.append([ds, item["value"], datasets[ds]["complexity"]["median"], datasets[ds]["node_count"]["median"], datasets[ds]["top1_category"]])
    lines.extend(md_table(["Dataset", "Question Len Median", "Complexity Median", "Node Median", "Top1"], long_rows))
    lines.append("")
    lines.append("## 总体相关性")
    lines.append("")
    corr_rows = [[item["x"], item["y"], item["pearson"]] for item in deep["correlations"]]
    lines.extend(md_table(["X", "Y", "Pearson r"], corr_rows))
    lines.append("")
    lines.append("## 每个数据集详情")
    for dataset, item in datasets.items():
        lines.append("")
        lines.append(f"### {dataset}")
        lines.append("")
        lines.append(f"- N: `{item['sample_count']}`")
        lines.append(f"- 多样性：`{item['concentration_label']}`；有效类别数 `{item['effective_category_count']}`；Top1 `{item['top1_category']}` 占 `{item['top1_share_pct']}%`；Top3 占 `{item['top3_share_pct']}%`")
        lines.append(f"- 题长中位数 `{item['question_len']['median']}`，复杂度中位数 `{item['complexity']['median']}`，节点数中位数 `{item['node_count']['median']}`")
        lines.append("")
        cat_rows = []
        for category, cat in item["categories"].items():
            cat_rows.append([category, cat["count"], cat["share_pct"], cat["question_len"]["median"], cat["complexity"]["median"], cat["multi_step"]["median"], cat["requires_image_pct"]])
        lines.extend(md_table(["Category", "N", "%", "Q Len Med", "Complexity Med", "Multi-step Med", "Req Image %"], cat_rows))
        lines.append("")
        lines.append("代表样本：")
        shown = 0
        for category, cat in item["categories"].items():
            if shown >= 6:
                break
            if not cat["examples"]:
                continue
            ex = cat["examples"][0]
            lines.append(f"- `{category}` / `{ex['canonical_sample_id']}`: {ex['question_excerpt']}")
            shown += 1
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    analysis_dir = args.analysis_dir.resolve()
    rows = load_rows(analysis_dir)
    by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_dataset[row["dataset_path"]].append(row)

    dataset_summary = {
        dataset: summarize_dataset(dataset_rows, args.max_categories, args.examples_per_category)
        for dataset, dataset_rows in sorted(by_dataset.items())
    }
    correlations = []
    for x_key, y_key in [
        ("question_unit_len", "complexity_index"),
        ("question_unit_len", "node_count"),
        ("condition_count", "node_count"),
        ("visual_entity_count", "multimodal_strength_score"),
        ("multi_step_score", "complexity_index"),
        ("latex_count", "answer_unit_len"),
    ]:
        correlations.append({"x": x_key, "y": y_key, "pearson": pearson(rows, x_key, y_key)})

    deep = {
        "sample_count": len(rows),
        "dataset_count": len(dataset_summary),
        "datasets": dataset_summary,
        "rankings": build_rankings(dataset_summary),
        "correlations": correlations,
        "outliers": build_outliers(rows),
    }

    (analysis_dir / "ready_deep_dataset_analysis.json").write_text(json.dumps(deep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(analysis_dir / "ready_deep_dataset_analysis.md", deep)

    diversity_rows = []
    category_rows = []
    for dataset, item in dataset_summary.items():
        diversity_rows.append(
            {
                "dataset": dataset,
                "sample_count": item["sample_count"],
                "category_count": item["category_count"],
                "effective_category_count": item["effective_category_count"],
                "entropy_bits": item["entropy_bits"],
                "hhi": item["hhi"],
                "concentration_label": item["concentration_label"],
                "top1_category": item["top1_category"],
                "top1_share_pct": item["top1_share_pct"],
                "top3_share_pct": item["top3_share_pct"],
                "question_len_median": item["question_len"]["median"],
                "complexity_median": item["complexity"]["median"],
                "node_count_median": item["node_count"]["median"],
                "multi_step_median": item["multi_step"]["median"],
            }
        )
        for category, cat in item["categories"].items():
            category_rows.append(
                {
                    "dataset": dataset,
                    "category": category,
                    "count": cat["count"],
                    "share_pct": cat["share_pct"],
                    "question_len_median": cat["question_len"]["median"],
                    "complexity_median": cat["complexity"]["median"],
                    "multi_step_median": cat["multi_step"]["median"],
                    "requires_image_pct": cat["requires_image_pct"],
                    "top_question_type": cat["question_type"][0]["value"] if cat["question_type"] else "",
                    "top_answer_shape": cat["answer_shape"][0]["value"] if cat["answer_shape"] else "",
                }
            )
    write_csv(analysis_dir / "ready_dataset_diversity.csv", diversity_rows)
    write_csv(analysis_dir / "ready_category_feature_summary.csv", category_rows)

    outlier_rows = []
    for group, group_rows in deep["outliers"].items():
        for row in group_rows:
            outlier_rows.append({"group": group, **row})
    write_csv(analysis_dir / "ready_outlier_samples.csv", outlier_rows)

    print(json.dumps({"datasets": len(dataset_summary), "output_dir": str(analysis_dir)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
