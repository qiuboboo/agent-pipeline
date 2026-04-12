#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_ROOT = PROJECT_ROOT / "outputs"
ALLOWED_SUBJECTS = ["Math", "Physics", "Biology", "Chemistry"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Use an LLM to guess SCEMQA subject labels and export a mapping file.")
    parser.add_argument("--outputs-root", default=str(OUTPUTS_ROOT), help="Outputs root to scan.")
    parser.add_argument("--dataset", default="scemqa", help="Dataset key to scan. Default: scemqa")
    parser.add_argument("--out", default="scemqa_subject_mapping.csv", help="Output CSV path.")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-5.4"), help="LLM model name.")
    parser.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL", ""), help="Optional OpenAI-compatible base URL.")
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", ""), help="API key. Defaults to OPENAI_API_KEY.")
    parser.add_argument("--limit", type=int, default=0, help="Optional max sample count.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output file.")
    return parser.parse_args()


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def pick_first_nonempty(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            if value.strip():
                return value.strip()
            continue
        return str(value)
    return ""


def sample_problem_id(sample: Dict[str, Any], sample_path: Path) -> str:
    for block_name in ["problem_main_record", "clean_problem_record", "normalization_record", "candidate_problem_record", "source_intake_record"]:
        block = sample.get(block_name) or {}
        value = block.get("problem_id")
        if value:
            return str(value)
    return sample_path.stem


def sample_source_problem_id(sample: Dict[str, Any], sample_path: Path) -> str:
    for block_name in ["problem_main_record", "clean_problem_record", "normalization_record", "candidate_problem_record", "source_intake_record"]:
        block = sample.get(block_name) or {}
        value = block.get("source_problem_id")
        if value:
            return str(value)
    return sample_problem_id(sample, sample_path)


def sample_question(sample: Dict[str, Any]) -> str:
    for block_name, field_names in [
        ("source_intake_record", ["raw_question_text"]),
        ("candidate_problem_record", ["raw_question_text"]),
        ("problem_main_record", ["raw_question_text", "normalized_question_text"]),
        ("normalization_record", ["normalized_question_text"]),
    ]:
        block = sample.get(block_name) or {}
        for field_name in field_names:
            value = block.get(field_name)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def sample_choices(sample: Dict[str, Any]) -> Dict[str, Any]:
    source = sample.get("source_intake_record") or {}
    choice_map = source.get("choice_map")
    if isinstance(choice_map, dict):
        return choice_map
    return {}


def iter_sample_paths(outputs_root: Path, dataset: str) -> Iterable[Path]:
    yield from sorted(outputs_root.glob(f"**/datasets/{dataset}/samples/*.json"))


def build_client(base_url: str, api_key: str):
    if OpenAI is None:
        raise RuntimeError("openai package is not installed. Install it before running this script.")
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def llm_guess_subject(client, model: str, question: str, choices: Dict[str, Any]) -> Dict[str, Any]:
    prompt = (
        "You are labeling a science QA sample into exactly one subject from this closed set: "
        "Math, Physics, Biology, Chemistry.\n"
        "Return JSON only with keys: subject, confidence, rationale.\n"
        "confidence must be a float between 0 and 1.\n"
        "Do not output any extra text.\n\n"
        f"Question:\n{question}\n\n"
        f"Choices:\n{json.dumps(choices, ensure_ascii=False)}\n"
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You classify exam questions by subject and respond with strict JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    content = resp.choices[0].message.content or "{}"
    start = content.find("{")
    end = content.rfind("}")
    if start >= 0 and end >= start:
        content = content[start : end + 1]
    data = json.loads(content)
    subject = str(data.get("subject") or "").strip()
    if subject not in ALLOWED_SUBJECTS:
        raise RuntimeError(f"Unexpected subject: {subject!r}")
    confidence = data.get("confidence")
    try:
        confidence = float(confidence)
    except Exception:
        confidence = 0.0
    rationale = str(data.get("rationale") or "").strip()
    return {"subject": subject, "confidence": confidence, "rationale": rationale}


def main() -> None:
    args = parse_args()
    out_path = Path(args.out)
    if out_path.exists() and not args.overwrite:
        raise SystemExit(f"Output file already exists: {out_path}. Use --overwrite to replace it.")
    if not args.api_key:
        raise SystemExit("Missing API key. Set OPENAI_API_KEY or pass --api-key.")

    outputs_root = Path(args.outputs_root)
    sample_paths = list(iter_sample_paths(outputs_root, args.dataset))
    if args.limit > 0:
        sample_paths = sample_paths[: args.limit]

    client = build_client(args.base_url, args.api_key)
    rows: List[Dict[str, Any]] = []

    for idx, sample_path in enumerate(sample_paths, start=1):
        sample = read_json(sample_path)
        question = sample_question(sample)
        choices = sample_choices(sample)
        if not question:
            rows.append(
                {
                    "sample_path": sample_path.as_posix(),
                    "source_problem_id": sample_source_problem_id(sample, sample_path),
                    "problem_id": sample_problem_id(sample, sample_path),
                    "subject": "",
                    "confidence": "",
                    "rationale": "missing_question",
                }
            )
            continue
        result = llm_guess_subject(client, args.model, question, choices)
        rows.append(
            {
                "sample_path": sample_path.as_posix(),
                "source_problem_id": sample_source_problem_id(sample, sample_path),
                "problem_id": sample_problem_id(sample, sample_path),
                "subject": result["subject"],
                "confidence": result["confidence"],
                "rationale": result["rationale"],
            }
        )
        print(f"[{idx}/{len(sample_paths)}] {sample_path.name} -> {result['subject']} ({result['confidence']:.2f})", file=sys.stderr)
        time.sleep(0.1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["sample_path", "source_problem_id", "problem_id", "subject", "confidence", "rationale"])
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "output": out_path.as_posix(),
        "rows": len(rows),
        "subject_counts": {subject: sum(1 for row in rows if row.get("subject") == subject) for subject in ALLOWED_SUBJECTS},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
