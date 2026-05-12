#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ANALYSIS_DIR = PROJECT_ROOT / "plans" / "ready_sample_analysis_2026-05-12"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate plots for ready sample analysis.")
    parser.add_argument("--analysis-dir", type=Path, default=DEFAULT_ANALYSIS_DIR)
    return parser.parse_args()


def load_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def maybe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def save_barh(path: Path, labels: list[str], values: list[float], title: str, xlabel: str, color: str = "#4C78A8") -> None:
    import matplotlib.pyplot as plt

    fig_height = max(4.0, 0.36 * len(labels) + 1.2)
    fig, ax = plt.subplots(figsize=(10, fig_height))
    y = list(range(len(labels)))
    ax.barh(y, values, color=color)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.25)
    for i, value in enumerate(values):
        ax.text(value, i, f" {value:g}", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def save_pie(path: Path, labels: list[str], values: list[float], title: str) -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90, textprops={"fontsize": 9})
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def save_scatter(path: Path, xs: list[float], ys: list[float], labels: list[str], title: str, xlabel: str, ylabel: str) -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(xs, ys, color="#F58518", alpha=0.8)
    for x, y, label in zip(xs, ys, labels):
        ax.annotate(label.split("\\")[-1], (x, y), fontsize=7, xytext=(4, 3), textcoords="offset points")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    analysis_dir = args.analysis_dir.resolve()
    plot_dir = analysis_dir / "figures"
    plot_dir.mkdir(parents=True, exist_ok=True)

    rows = load_csv(analysis_dir / "ready_sample_features.csv")
    diversity = load_csv(analysis_dir / "ready_dataset_diversity.csv")
    deep = json.loads((analysis_dir / "ready_deep_dataset_analysis.json").read_text(encoding="utf-8"))

    subject_counter = Counter(row["subject"] for row in rows)
    save_pie(
        plot_dir / "subject_distribution.png",
        list(subject_counter.keys()),
        list(subject_counter.values()),
        "Ready Pass Samples by Subject",
    )

    dataset_counts = sorted(((row["dataset"], maybe_float(row["sample_count"])) for row in diversity), key=lambda x: x[1], reverse=True)
    save_barh(
        plot_dir / "dataset_sample_counts.png",
        [item[0] for item in dataset_counts],
        [item[1] for item in dataset_counts],
        "Pass Sample Count by Dataset",
        "samples",
        "#4C78A8",
    )

    top1 = sorted(((row["dataset"], maybe_float(row["top1_share_pct"])) for row in diversity), key=lambda x: x[1], reverse=True)
    save_barh(
        plot_dir / "dataset_top1_concentration.png",
        [item[0] for item in top1],
        [item[1] for item in top1],
        "Dominant Category Share by Dataset",
        "top-1 category share (%)",
        "#E45756",
    )

    effective = sorted(((row["dataset"], maybe_float(row["effective_category_count"])) for row in diversity), key=lambda x: x[1], reverse=True)
    save_barh(
        plot_dir / "dataset_effective_categories.png",
        [item[0] for item in effective],
        [item[1] for item in effective],
        "Effective Category Count by Dataset",
        "effective categories",
        "#54A24B",
    )

    qlen = sorted(((row["dataset"], maybe_float(row["question_len_median"])) for row in diversity), key=lambda x: x[1], reverse=True)
    save_barh(
        plot_dir / "dataset_question_length_median.png",
        [item[0] for item in qlen],
        [item[1] for item in qlen],
        "Median Question Length by Dataset",
        "word/CJK units",
        "#B279A2",
    )

    complexity = sorted(((row["dataset"], maybe_float(row["complexity_median"])) for row in diversity), key=lambda x: x[1], reverse=True)
    save_barh(
        plot_dir / "dataset_complexity_median.png",
        [item[0] for item in complexity],
        [item[1] for item in complexity],
        "Median Complexity Index by Dataset",
        "complexity index",
        "#F58518",
    )

    qtype = Counter(row["question_type"] for row in rows)
    save_barh(
        plot_dir / "question_type_distribution.png",
        [key for key, _ in qtype.most_common()],
        [value for _, value in qtype.most_common()],
        "Question Type Distribution",
        "samples",
        "#72B7B2",
    )

    answer_shape = Counter(row["answer_shape"] for row in rows)
    save_barh(
        plot_dir / "answer_shape_distribution.png",
        [key for key, _ in answer_shape.most_common()],
        [value for _, value in answer_shape.most_common()],
        "Answer Shape Distribution",
        "samples",
        "#9D755D",
    )

    save_scatter(
        plot_dir / "dataset_diversity_vs_complexity.png",
        [maybe_float(row["effective_category_count"]) for row in diversity],
        [maybe_float(row["complexity_median"]) for row in diversity],
        [row["dataset"] for row in diversity],
        "Diversity vs. Complexity",
        "effective category count",
        "median complexity index",
    )

    index_lines = ["# Ready Analysis Figures", ""]
    for png in sorted(plot_dir.glob("*.png")):
        index_lines.append(f"- [{png.name}](figures/{png.name})")
    (analysis_dir / "ready_analysis_figures.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    print(json.dumps({"figure_count": len(list(plot_dir.glob('*.png'))), "figure_dir": str(plot_dir)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
