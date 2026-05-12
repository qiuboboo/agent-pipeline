#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_ROOT = PROJECT_ROOT / "plans" / "ready_sample_analysis_2026-05-12" / "final_taxonomy_package"
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
SPACE_RE = re.compile(r"\s+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Translate representative questions in final taxonomy package.")
    parser.add_argument("--package-root", type=Path, default=DEFAULT_PACKAGE_ROOT)
    parser.add_argument("--limit", type=int, default=260)
    parser.add_argument("--sleep", type=float, default=0.25)
    return parser.parse_args()


def clean(text: str) -> str:
    return SPACE_RE.sub(" ", text or "").strip()


def has_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text or ""))


def read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


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


def translate(text: str, cache: dict[str, str], limit: int, sleep_s: float) -> tuple[str, str]:
    text = clean(text)
    if not text:
        return "", "empty"
    if has_cjk(text):
        return text, "original_zh"
    source = text[:limit]
    if source in cache:
        return cache[source], "machine_cached"
    url = "https://api.mymemory.translated.net/get?q=" + urllib.parse.quote(source) + "&langpair=en%7Czh-CN"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=25) as response:
            payload = json.loads(response.read().decode("utf-8"))
        translated = clean((payload.get("responseData") or {}).get("translatedText") or "")
        if translated:
            cache[source] = translated
            time.sleep(sleep_s)
            return translated, "machine_mymemory"
    except Exception as exc:
        return "", f"translation_failed:{type(exc).__name__}"
    return "", "translation_empty"


def md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(item).replace("\n", " ").replace("|", "\\|") for item in row) + " |")
    return lines


def rebuild_readme(ds_dir: Path, rep_rows: list[dict[str, Any]]) -> None:
    taxonomy = read_csv(ds_dir / "taxonomy.csv")
    stats = read_csv(ds_dir / "feature_stats.csv")
    dataset = taxonomy[0]["dataset"] if taxonomy else ds_dir.name
    lines: list[str] = []
    lines.append(f"# {dataset} final taxonomy package")
    lines.append("")
    lines.append(f"- 样本数：{sum(int(row['count']) for row in taxonomy) if taxonomy else ''}")
    lines.append(f"- 最终类别数：{len(taxonomy)}")
    lines.append("")
    lines.append("## Taxonomy")
    lines.append("")
    lines.extend(md_table(["类别", "中文名", "数量", "占比", "定义"], [[r["final_category"], r["final_category_zh"], r["count"], f"{r['share_pct']}%", r["definition_zh"]] for r in taxonomy]))
    lines.append("")
    lines.append("## 代表例题")
    lines.append("")
    lines.extend(md_table(["中文类别", "样本ID", "题目", "中文题意", "答案"], [[r["final_category_zh"], r["canonical_sample_id"], r["question"], r.get("question_zh", ""), r["answer"]] for r in rep_rows]))
    lines.append("")
    lines.append("## 特征统计")
    lines.append("")
    lines.extend(md_table(["中文类别", "N", "题长中位数", "复杂度中位数", "multi-step中位数", "需图像%"], [[r["final_category_zh"], r["count"], r["question_len_median"], r["complexity_median"], r["multi_step_median"], r["requires_image_pct"]] for r in stats]))
    (ds_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    package_root = args.package_root.resolve()
    cache_path = package_root / "translation_cache.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    translated = 0
    failed = 0
    for rep_path in sorted(package_root.glob("*/representative_examples.csv")):
        rows = read_csv(rep_path)
        for row in rows:
            zh, status = translate(row.get("question", ""), cache, args.limit, args.sleep)
            row["question_zh"] = zh
            row["translation_status"] = status
            if status.startswith("machine"):
                translated += 1
            elif status.startswith("translation_failed"):
                failed += 1
        write_csv(rep_path, rows)
        rebuild_readme(rep_path.parent, rows)
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"translated_or_cached": translated, "failed": failed, "cache_size": len(cache)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
