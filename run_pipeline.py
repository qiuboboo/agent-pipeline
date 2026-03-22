from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from openai import OpenAI

OUTPUT_ROOT = Path(__file__).resolve().parent / "outputs"
SAMPLE_PATH = OUTPUT_ROOT / "samples.jsonl"
PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "extract_question_answer_image.md"

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY_AGENT", "你的API密钥"),
    base_url="https://synai996.space/v1",
)


def read_prompt(prompt_path: Path) -> str:
    return prompt_path.read_text(encoding="utf-8").strip()


def build_extraction_user_prompt(record: dict) -> str:
    record_json = json.dumps(record, ensure_ascii=False, indent=2)
    return f"""下面是一条原始 JSON 记录。
请按照 system prompt 的规则提取 question_text、answer_text 和 image_paths。
只返回 JSON 对象。

原始 JSON:
{record_json}
"""


def call_model(system_prompt: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-5.4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


def iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        for index, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            yield index, json.loads(line)


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def make_problem_id(prefix: str, record: dict, index: int) -> str:
    source_id = record.get("id") or record.get("image_id") or f"{index:06d}"
    return f"{prefix}_{str(source_id).replace('/', '_')}"

# 支持json中
# image: "a.png"
# image: ["a.png", "b.png"]
# images: ["a.png", "b.png"]
def resolve_image_paths(base_dir: Path, record: dict) -> list[str]:
    raw_images = record.get("images")
    if raw_images is None:
        raw_images = record.get("image")
    if not raw_images:
        return []

    if isinstance(raw_images, str):
        raw_images = [raw_images]

    resolved_paths: list[str] = []
    script_dir = Path(__file__).resolve().parent
    for image_value in raw_images:
        image_path = Path(image_value)
        if image_path.is_absolute():
            resolved_paths.append(str(image_path))
            continue

        candidates = [
            (base_dir / image_path).resolve(),
            (script_dir / image_path).resolve(),
        ]
        for candidate in candidates:
            if candidate.exists():
                resolved_paths.append(str(candidate))
                break
        else:
            resolved_paths.append(str(candidates[0]))

    return resolved_paths


# 现在只收集 json(Path) 中的某个问题的dict中的question, answer, image。
# 目前 question / answer / image_paths 由大模型从原始 JSON 中抽取，尽量保留原文。
def build_sample(input_path: Path, record: dict, index: int, prefix: str) -> dict:
    system_prompt = read_prompt(PROMPT_PATH)
    user_prompt = build_extraction_user_prompt(record)
    response_text = call_model(system_prompt, user_prompt)
    extracted = json.loads(response_text)

    return {
        "problem_id": make_problem_id(prefix, record, index),
        "question_text": (extracted.get("question_text") or "").strip(),
        "answer_text": (extracted.get("answer_text") or "").strip(),
        "image_paths": resolve_image_paths(input_path.parent, {"images": extracted.get("image_paths", [])}),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Step 1: collect question, answer, and image paths")
    parser.add_argument("input", type=Path, help="Path to a JSONL file such as m3cot/test.jsonl")
    parser.add_argument("--prefix", default="m3cot")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--reset-output", action="store_true")
    args = parser.parse_args()

    if args.reset_output and SAMPLE_PATH.exists():
        SAMPLE_PATH.unlink()

    processed = 0
    for index, record in iter_jsonl(args.input):
        sample = build_sample(args.input, record, index, args.prefix)
        append_jsonl(SAMPLE_PATH, sample)
        print(f"built sample: {sample['problem_id']}")
        processed += 1
        if args.limit and processed >= args.limit:
            break

    print(f"Saved {processed} sample(s) to {SAMPLE_PATH}")


if __name__ == "__main__":
    main()
