#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

from review_release_policy import format_rule_summary, get_dataset_policy, iter_dataset_roots, normalize_bucket_rule, load_review_release_policy_config

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = PROJECT_ROOT / "docs"
MANIFESTS_DOCS_ROOT = DOCS_ROOT / "manifests"
REVIEW_DOCS_ROOT = DOCS_ROOT / "review"
ANALYSIS_DOCS_ROOT = DOCS_ROOT / "analysis"


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def escape_cell(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("|", "\\|")
    text = text.replace("\n", "<br>")
    return text


def make_table(headers: List[str], rows: List[List[Any]]) -> str:
    parts = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        parts.append("| " + " | ".join(escape_cell(cell) for cell in row) + " |")
    return "\n".join(parts)


def iter_ready_packages() -> Iterable[Path]:
    for dataset_root in iter_dataset_roots():
        if (dataset_root / "summary.json").exists():
            yield dataset_root


def pick_first_nonempty(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            if value.strip():
                return value
            continue
        return str(value)
    return ""


def pick_variant_text(sample: Dict[str, Any]) -> str:
    variants = sample.get("open_ended_problem_variants") or []
    for variant in variants:
        if not isinstance(variant, dict):
            continue
        rewritten = pick_first_nonempty(variant.get("rewritten_question_text"))
        if rewritten:
            return rewritten
    problem_main = sample.get("problem_main_record") or {}
    clean_problem = sample.get("clean_problem_record") or {}
    normalized_assets = sample.get("normalized_assets") or {}
    normalization = sample.get("normalization_record") or {}
    return pick_first_nonempty(
        problem_main.get("normalized_question_text"),
        clean_problem.get("normalized_question_text"),
        normalized_assets.get("normalized_question_text"),
        normalization.get("normalized_question_text"),
    )


def pick_raw_question(sample: Dict[str, Any]) -> str:
    problem_main = sample.get("problem_main_record") or {}
    source = sample.get("source_intake_record") or {}
    candidate = sample.get("candidate_problem_record") or {}
    return pick_first_nonempty(
        problem_main.get("raw_question_text"),
        source.get("raw_question_text"),
        candidate.get("raw_question_text"),
    )


def pick_source_problem_id(sample: Dict[str, Any]) -> str:
    problem_main = sample.get("problem_main_record") or {}
    clean_problem = sample.get("clean_problem_record") or {}
    candidate = sample.get("candidate_problem_record") or {}
    source = sample.get("source_intake_record") or {}
    return pick_first_nonempty(
        problem_main.get("source_problem_id"),
        clean_problem.get("source_problem_id"),
        candidate.get("source_problem_id"),
        source.get("source_problem_id"),
    )


def pick_clean_decision(sample: Dict[str, Any]) -> str:
    problem_main = sample.get("problem_main_record") or {}
    clean_problem = sample.get("clean_problem_record") or {}
    clean_pool = sample.get("clean_pool_entries") or []
    first_clean_pool = clean_pool[0] if clean_pool and isinstance(clean_pool[0], dict) else {}
    return pick_first_nonempty(
        problem_main.get("clean_decision"),
        clean_problem.get("clean_decision"),
        first_clean_pool.get("clean_decision"),
        "unknown",
    )


def pick_rewrite_strategy(sample: Dict[str, Any]) -> str:
    problem_main = sample.get("problem_main_record") or {}
    rewrite_reports = sample.get("rewrite_reports") or []
    first_report = rewrite_reports[0] if rewrite_reports and isinstance(rewrite_reports[0], dict) else {}
    return pick_first_nonempty(
        problem_main.get("rewrite_strategy"),
        first_report.get("strategy"),
        "unknown",
    )


def pick_review_reason(sample: Dict[str, Any]) -> str:
    clean_problem = sample.get("clean_problem_record") or {}
    clean_pool = sample.get("clean_pool_entries") or []
    first_clean_pool = clean_pool[0] if clean_pool and isinstance(clean_pool[0], dict) else {}
    reason_codes = clean_problem.get("decision_reason_codes") or first_clean_pool.get("decision_reason_codes") or []
    if isinstance(reason_codes, list):
        return ", ".join(str(code) for code in reason_codes if code)
    return pick_first_nonempty(reason_codes)


def pick_review_reason_codes(sample: Dict[str, Any]) -> List[str]:
    clean_problem = sample.get("clean_problem_record") or {}
    clean_pool = sample.get("clean_pool_entries") or []
    first_clean_pool = clean_pool[0] if clean_pool and isinstance(clean_pool[0], dict) else {}
    reason_codes = clean_problem.get("decision_reason_codes") or first_clean_pool.get("decision_reason_codes") or []
    if isinstance(reason_codes, list):
        return [str(code) for code in reason_codes if code]
    reason = pick_first_nonempty(reason_codes)
    return [reason] if reason else []


def pick_image_markdown(dataset_root: Path, problem_id: str) -> str:
    crop_dir = dataset_root / "artifacts" / "crops"
    image_dir = dataset_root / "artifacts" / "images"
    for folder in [crop_dir, image_dir]:
        if not folder.exists():
            continue
        matches = sorted(folder.glob(f"{problem_id}*"))
        if matches:
            return f"![]({(Path('..') / matches[0].relative_to(PROJECT_ROOT)).as_posix()})"
    return ""


def collect_samples(dataset_root: Path) -> List[Dict[str, Any]]:
    samples_dir = dataset_root / "samples"
    rows: List[Dict[str, Any]] = []
    for sample_path in sorted(samples_dir.glob("*.json")):
        sample = read_json(sample_path)
        problem_main = sample.get("problem_main_record") or {}
        rewrite_reports = sample.get("rewrite_reports") or []
        first_report = rewrite_reports[0] if rewrite_reports and isinstance(rewrite_reports[0], dict) else {}
        problem_id = pick_first_nonempty(problem_main.get("problem_id"), sample_path.stem)
        rows.append(
            {
                "problem_id": problem_id,
                "source_problem_id": pick_source_problem_id(sample),
                "decision": pick_clean_decision(sample),
                "raw_question": pick_raw_question(sample),
                "rewritten_question": pick_variant_text(sample),
                "image_markdown": pick_image_markdown(dataset_root, problem_id),
                "review_reason": pick_review_reason(sample),
                "review_reason_codes": pick_review_reason_codes(sample),
                "rewrite_strategy": pick_rewrite_strategy(sample),
                "consistency_check_passed": first_report.get("consistency_check_passed"),
                "question_check_passed": first_report.get("question_check_passed"),
            }
        )
    return rows


def top_counter_rows(counter: Counter[str], limit: int = 8) -> List[List[Any]]:
    return [[key, count] for key, count in counter.most_common(limit)]


def pick_pass_examples(samples: List[Dict[str, Any]], max_examples: int = 5) -> List[Dict[str, Any]]:
    pass_samples = [sample for sample in samples if sample["decision"] == "pass"]
    selected: List[Dict[str, Any]] = []
    seen_ids = set()
    for strategy, _ in Counter(sample["rewrite_strategy"] for sample in pass_samples).most_common():
        for sample in pass_samples:
            if sample["problem_id"] in seen_ids:
                continue
            if sample["rewrite_strategy"] != strategy:
                continue
            if not sample["raw_question"] or not sample["rewritten_question"]:
                continue
            selected.append(sample)
            seen_ids.add(sample["problem_id"])
            if len(selected) >= max_examples:
                return selected
            break
    for sample in pass_samples:
        if len(selected) >= max_examples:
            break
        if sample["problem_id"] in seen_ids:
            continue
        if not sample["raw_question"] or not sample["rewritten_question"]:
            continue
        selected.append(sample)
        seen_ids.add(sample["problem_id"])
    return selected


def pick_review_examples(samples: List[Dict[str, Any]], max_examples: int = 5) -> List[Dict[str, Any]]:
    review_samples = [sample for sample in samples if sample["decision"] == "review"]
    reason_counter = Counter(code for sample in review_samples for code in sample["review_reason_codes"])
    selected: List[Dict[str, Any]] = []
    seen_ids = set()
    covered_reasons = set()
    for reason, _ in reason_counter.most_common():
        for sample in review_samples:
            if sample["problem_id"] in seen_ids:
                continue
            if reason not in sample["review_reason_codes"]:
                continue
            selected.append(sample)
            seen_ids.add(sample["problem_id"])
            covered_reasons.update(sample["review_reason_codes"])
            if len(selected) >= max_examples:
                return selected
            break
    for sample in review_samples:
        if len(selected) >= max_examples:
            break
        if sample["problem_id"] in seen_ids:
            continue
        if not sample["review_reason_codes"] and covered_reasons:
            continue
        selected.append(sample)
        seen_ids.add(sample["problem_id"])
    return selected


def describe_pass_example(dataset_summary: Dict[str, Any], sample: Dict[str, Any]) -> str:
    strategy = sample["rewrite_strategy"]
    detail = dataset_summary.get("detail") or ""
    notes = [f"该样本自动结果为 `pass`，改写策略是 `{strategy}`。"]
    if strategy == "keep_open":
        notes.append("改写基本保持开放题结构，主要做措辞与格式规范化。")
    elif strategy == "blank_open":
        notes.append("改写把原始素材整理成开放问答形式，但没有引入新的审查风险信号。")
    elif strategy == "split_open":
        notes.append("虽然经过拆分式改写，但仍通过了自动检查，说明题意保持较稳定。")
    else:
        notes.append("改写后的题干与原题保持主问题一致，自动检查未触发 review。")
    if sample["consistency_check_passed"] is True:
        notes.append("rewrite consistency check 也通过。")
    if sample["question_check_passed"] is True:
        notes.append("question check 也通过。")
    if "filtered safe subset" in detail.lower() or "selection_rule" in json.dumps(dataset_summary.get("filtered_from") or {}, ensure_ascii=False).lower():
        notes.append("该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。")
    return " ".join(notes)


def describe_review_example(sample: Dict[str, Any]) -> str:
    reasons = sample["review_reason_codes"]
    if not reasons:
        return "该样本进入 `review`，但当前样本元数据里没有明确的 `decision_reason_codes`，适合作为需要进一步人工补充判断依据的案例。"
    if len(reasons) == 1:
        return f"该样本进入 `review` 的主因是 `{reasons[0]}`，说明自动链路在这个风险点上无法直接放行。"
    return f"该样本同时触发了多个 review 原因：`{', '.join(reasons)}`，属于复合风险案例，不适合直接自动放行。"


def pick_decision_counts(dataset_summary: Dict[str, Any]) -> Dict[str, Any]:
    return dataset_summary.get("decision_counts") or dataset_summary.get("status_counts") or {}


def summarize_dataset(dataset_summary: Dict[str, Any], review_reason_counter: Counter[str]) -> str:
    counts = pick_decision_counts(dataset_summary)
    pass_count = counts.get("pass", 0)
    review_count = counts.get("review", 0)
    reject_count = counts.get("reject", 0)
    if review_count == 0:
        return f"当前 ready 包以 `pass` 为主（pass={pass_count}, review={review_count}, reject={reject_count}），更适合当作稳定改写样本集来观察。"
    if review_count > pass_count:
        top_reason = review_reason_counter.most_common(1)[0][0] if review_reason_counter else "review_reason_missing"
        return f"当前数据集 `review` 数量高于 `pass`（pass={pass_count}, review={review_count}, reject={reject_count}），更像是审核偏严或对齐风险较高；高频原因集中在 `{top_reason}`。"
    top_reason = review_reason_counter.most_common(1)[0][0] if review_reason_counter else "review_reason_missing"
    return f"当前数据集同时存在稳定通过样本与需人工复核样本（pass={pass_count}, review={review_count}, reject={reject_count}）；review 主要集中在 `{top_reason}` 一类问题。"


def build_analysis_doc(dataset_root: Path) -> str:
    dataset_key = dataset_root.name
    package_root = dataset_root.parent.parent
    dataset_summary = read_json(dataset_root / "summary.json")
    counts = pick_decision_counts(dataset_summary)
    strategy_counts = dataset_summary.get("rewrite_strategy_counts") or {}
    samples = collect_samples(dataset_root)
    pass_examples = pick_pass_examples(samples)
    review_examples = pick_review_examples(samples)
    review_reason_counter = Counter(code for sample in samples if sample["decision"] == "review" for code in sample["review_reason_codes"])

    lines = [
        f"# {dataset_key} 改写样例分析",
        "",
        f"- 生成时间：`{utc_now()}`",
        f"- ready 包：`{package_root.relative_to(PROJECT_ROOT).as_posix()}`",
        f"- 自动结果分布：`pass={counts.get('pass', 0)} / review={counts.get('review', 0)} / reject={counts.get('reject', 0)}`",
        "",
        "## Pass 样本分析",
        "",
        f"- pass 样本数：`{counts.get('pass', 0)}`",
        f"- 改写策略分布：`{', '.join(f'{key}={value}' for key, value in strategy_counts.items()) or '无'}`",
        "",
    ]

    if pass_examples:
        for index, sample in enumerate(pass_examples, start=1):
            lines.extend(
                [
                    f"### Pass 案例 {index}：`{sample['problem_id']}`",
                    "",
                    f"- source_problem_id：`{sample['source_problem_id']}`",
                    f"- rewrite_strategy：`{sample['rewrite_strategy']}`",
                    f"- 图片：{sample['image_markdown'] or '无' }",
                    "",
                    "**原题**",
                    "",
                    sample["raw_question"] or "无",
                    "",
                    "**改写**",
                    "",
                    sample["rewritten_question"] or "无",
                    "",
                    "**分析**",
                    "",
                    describe_pass_example(dataset_summary, sample),
                    "",
                ]
            )
    else:
        lines.extend(["当前 ready 包没有 `clean_decision=pass` 的样本。", ""])

    lines.extend(["## Review 原因分析", ""])
    if review_reason_counter:
        lines.extend(
            [
                make_table(["review reason", "count"], top_counter_rows(review_reason_counter, limit=8)),
                "",
            ]
        )
    else:
        lines.extend(["当前 ready 包没有可统计的 review reason codes。", ""])

    if review_examples:
        for index, sample in enumerate(review_examples, start=1):
            lines.extend(
                [
                    f"### Review 案例 {index}：`{sample['problem_id']}`",
                    "",
                    f"- source_problem_id：`{sample['source_problem_id']}`",
                    f"- review reasons：`{sample['review_reason'] or '无'}`",
                    f"- 图片：{sample['image_markdown'] or '无' }",
                    "",
                    "**原题**",
                    "",
                    sample["raw_question"] or "无",
                    "",
                    "**改写**",
                    "",
                    sample["rewritten_question"] or "无",
                    "",
                    "**分析**",
                    "",
                    describe_review_example(sample),
                    "",
                ]
            )
    else:
        lines.extend(["当前 ready 包没有 `clean_decision=review` 的样本；该数据集当前只能分析 pass 改写例子。", ""])

    lines.extend(["## 小结", "", summarize_dataset(dataset_summary, review_reason_counter), ""])
    return "\n".join(lines)


def build_manifest_doc(dataset_root: Path) -> str:
    dataset_key = dataset_root.name
    package_root = dataset_root.parent.parent
    dataset_summary = read_json(dataset_root / "summary.json")
    dedupe = dataset_summary.get("dedupe") or {}
    duplicate_manifest_path = PROJECT_ROOT / dedupe.get("duplicate_manifest_file", "")
    suspected_duplicates_path = PROJECT_ROOT / dedupe.get("suspected_duplicates_file", "")
    duplicate_manifest = read_json(duplicate_manifest_path) if duplicate_manifest_path.exists() else {}
    suspected_duplicates = read_json(suspected_duplicates_path) if suspected_duplicates_path.exists() else []

    lines = [
        f"# {dataset_key} 重复与疑似重复清单",
        "",
        f"- 生成时间：`{utc_now()}`",
        f"- ready 包：`{package_root.relative_to(PROJECT_ROOT).as_posix()}`",
        f"- dataset summary：`{(dataset_root / 'summary.json').relative_to(PROJECT_ROOT).as_posix()}`",
        "",
        "## 去重规则",
        "",
        "- 不依赖 `source id`。",
        "- 不直接用 `parent_problem_id` 判重。",
        "- 先按 `problem_id` 去掉跨 run 重复。",
        "- 再按标准化后的 `question + answer` 做严格内容去重。",
        "- 高相似题只标记为疑似重复，不自动删除。",
        "",
        "## 汇总",
        "",
    ]

    lines.append(
        make_table(
            ["指标", "值"],
            [
                ["输入样本数", dedupe.get("input_samples", 0)],
                ["problem_id 去重后", dedupe.get("after_problem_id_dedup", 0)],
                ["严格内容去重后", dedupe.get("after_content_dedup", 0)],
                ["problem_id 删除数", dedupe.get("dropped_problem_id_duplicates", 0)],
                ["严格内容重复删除数", dedupe.get("dropped_content_duplicates", 0)],
                ["疑似重复对数", dedupe.get("suspected_duplicate_pairs", 0)],
            ],
        )
    )

    problem_id_duplicates = duplicate_manifest.get("problem_id_duplicates") or []
    content_duplicates = duplicate_manifest.get("content_duplicates") or []

    lines.extend(["", "## 严格重复：problem_id", ""])
    if problem_id_duplicates:
        rows = []
        for item in problem_id_duplicates:
            for dropped in item.get("dropped", []):
                rows.append(
                    [
                        item.get("kept", {}).get("problem_id", ""),
                        item.get("kept", {}).get("sample_path", ""),
                        dropped.get("problem_id", ""),
                        dropped.get("sample_path", ""),
                    ]
                )
        lines.append(make_table(["保留 problem_id", "保留样本", "删除 problem_id", "删除样本"], rows))
    else:
        lines.append("无。")

    lines.extend(["", "## 严格重复：标准化 question + answer", ""])
    if content_duplicates:
        rows = []
        for item in content_duplicates:
            for dropped in item.get("dropped", []):
                rows.append(
                    [
                        item.get("kept", {}).get("problem_id", ""),
                        item.get("kept", {}).get("sample_path", ""),
                        dropped.get("problem_id", ""),
                        dropped.get("sample_path", ""),
                    ]
                )
        lines.append(make_table(["保留 problem_id", "保留样本", "删除 problem_id", "删除样本"], rows))
    else:
        lines.append("无。")

    lines.extend(["", "## 疑似重复", ""])
    if suspected_duplicates:
        rows = [
            [
                item.get("left_problem_id", ""),
                item.get("right_problem_id", ""),
                item.get("question_similarity", ""),
                item.get("left_sample_path", ""),
                item.get("right_sample_path", ""),
            ]
            for item in suspected_duplicates
        ]
        lines.append(make_table(["左 problem_id", "右 problem_id", "问题相似度", "左样本", "右样本"], rows))
    else:
        lines.append("无。")

    return "\n".join(lines) + "\n"


def build_policy_summary(dataset_key: str) -> List[str]:
    policy_root = load_review_release_policy_config()
    review_release = policy_root.get("review_release") or {}
    defaults = review_release.get("defaults") or {}
    dataset_policy = (review_release.get("datasets") or {}).get(dataset_key) or {}
    if not dataset_policy:
        return []
    release_buckets = dataset_policy.get("release_buckets") or {}
    if not release_buckets:
        return []

    lines = ["## 已配置的 review-release policy", ""]
    for bucket_key in sorted(release_buckets.keys()):
        rule = normalize_bucket_rule(dataset_policy, bucket_key, defaults=defaults)
        if not rule:
            continue
        lines.append(
            f"- `{bucket_key}` 桶：{format_rule_summary(rule.get('rule_type', 'structured_selection'), rule.get('selection'), rule.get('selection_notes', ''))}"
        )
        release_basis = rule.get("release_basis")
        if release_basis:
            lines.append(f"  - release_basis: `{release_basis}`")
        adjacent_key = rule.get("adjacent_key") or ""
        if adjacent_key:
            adjacent_label = rule.get("adjacent_label") or "adjacent bucket"
            adjacent_rule = format_rule_summary(
                rule.get("adjacent_rule_type", "structured_selection"),
                rule.get("adjacent_selection"),
                rule.get("adjacent_selection_notes", ""),
            )
            lines.append(f"  - adjacent: `{adjacent_label}` -> {adjacent_rule}")
    lines.append("")
    return lines


def build_review_doc(dataset_root: Path) -> str:
    dataset_key = dataset_root.name
    package_root = dataset_root.parent.parent
    dataset_summary = read_json(dataset_root / "summary.json")
    samples = collect_samples(dataset_root)
    sample_rows = [
        [
            sample["problem_id"],
            sample["source_problem_id"],
            sample["decision"],
            "",
            sample["raw_question"],
            sample["rewritten_question"],
            sample["image_markdown"],
            sample["review_reason"],
        ]
        for sample in samples
        if sample["decision"] == "review"
    ]

    counts = pick_decision_counts(dataset_summary)
    lines = [
        f"# {dataset_key} review 台账",
        "",
        f"- 生成时间：`{utc_now()}`",
        f"- ready 包：`{package_root.relative_to(PROJECT_ROOT).as_posix()}`",
        f"- review 样本数：`{len(sample_rows)}`",
        f"- 自动结果分布：`pass={counts.get('pass', 0)} / review={counts.get('review', 0)} / reject={counts.get('reject', 0)}`",
        "",
        "人工接受状态说明：`1=pass`，`0=reject`，空白表示未看。",
        "",
    ]
    lines.extend(build_policy_summary(dataset_key))
    if sample_rows:
        lines.extend(
            [
                make_table(
                    ["problem_id", "source_problem_id", "自动结果", "人工接受状态", "原题原文", "改写内容", "图片简略图", "备注"],
                    sample_rows,
                ),
                "",
            ]
        )
    else:
        lines.extend(["当前 ready 包没有 `clean_decision=review` 的样本。", ""])
    return "\n".join(lines)


def main() -> None:
    generated = []
    for dataset_root in iter_ready_packages():
        dataset_key = dataset_root.name
        dataset_summary = read_json(dataset_root / "summary.json")
        dedupe = dataset_summary.get("dedupe") or {}

        review_doc = build_review_doc(dataset_root)
        review_path = REVIEW_DOCS_ROOT / f"{dataset_key}.md"
        write_text(review_path, review_doc)

        analysis_doc = build_analysis_doc(dataset_root)
        analysis_path = ANALYSIS_DOCS_ROOT / f"{dataset_key}.md"
        write_text(analysis_path, analysis_doc)

        generated_item = {
            "dataset_key": dataset_key,
            "review_doc": review_path.relative_to(PROJECT_ROOT).as_posix(),
            "analysis_doc": analysis_path.relative_to(PROJECT_ROOT).as_posix(),
        }
        if dedupe:
            manifest_doc = build_manifest_doc(dataset_root)
            manifest_path = MANIFESTS_DOCS_ROOT / f"{dataset_key}.md"
            write_text(manifest_path, manifest_doc)
            generated_item["manifest_doc"] = manifest_path.relative_to(PROJECT_ROOT).as_posix()
        generated.append(generated_item)
    print(json.dumps(generated, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
