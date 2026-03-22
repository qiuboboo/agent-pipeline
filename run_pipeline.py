from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
from pathlib import Path

from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = PROJECT_ROOT / "outputs"
SAMPLE_PATH = OUTPUT_ROOT / "samples.jsonl"
PROMPT_PATH = PROJECT_ROOT / "prompts" / "extract_question_answer_image.md"
SCORING_PROMPT_PATH = PROJECT_ROOT / "prompts" / "preliminary_value_scoring.md"

api_key = os.environ.get("OPENAI_API_KEY_AGENT")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY_AGENT is not set")

client = OpenAI(
    api_key=api_key,
    base_url="https://synai996.space/v1",
)


def read_prompt(prompt_path: Path) -> str:
    return prompt_path.read_text(encoding="utf-8").strip()


def strip_code_fence(text: str) -> str:
    text = text.strip()
    if not text.startswith("```"):
        return text

    lines = text.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def parse_json_response(text: str) -> dict:
    cleaned = strip_code_fence(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise


def build_extraction_user_prompt(record: dict) -> str:
    record_json = json.dumps(record, ensure_ascii=False, indent=2)
    return f"""下面是一条原始 JSON 记录。
请按照 system prompt 的规则提取 question_text、answer_text 和 image_paths。
只返回 JSON 对象。

原始 JSON:
{record_json}
"""


def build_scoring_user_prompt(sample: dict) -> str:
    sample_json = json.dumps(sample, ensure_ascii=False, indent=2)
    return f"""下面是一个已经抽取出的候选样本，请你根据 system prompt 中的评分标准进行初步价值评分。
如果附带了图片，请结合图片一起判断；如果图片缺失，则仅根据文本保守评分。
只返回 JSON 对象。

候选样本:
{sample_json}
"""


def encode_image_as_data_url(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(image_path.name)
    mime_type = mime_type or "application/octet-stream"
    data = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{data}"


def build_user_content(user_prompt: str, image_paths: list[str] | None = None, asset_base_dir: Path | None = None):
    if not image_paths:
        return user_prompt

    content_blocks = [{"type": "text", "text": user_prompt}]
    for raw_path in image_paths:
        image_path = Path(raw_path)
        if not image_path.is_absolute() and asset_base_dir is not None:
            image_path = asset_base_dir / image_path
        if not image_path.exists():
            continue
        content_blocks.append(
            {
                "type": "image_url",
                "image_url": {"url": encode_image_as_data_url(image_path)},
            }
        )

    if len(content_blocks) == 1:
        return user_prompt
    return content_blocks


def call_model(
    system_prompt: str,
    user_prompt: str,
    image_paths: list[str] | None = None,
    asset_base_dir: Path | None = None,
) -> str:
    response = client.chat.completions.create(
        model="gpt-5.4",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": build_user_content(user_prompt, image_paths=image_paths, asset_base_dir=asset_base_dir),
            },
        ],
    )
    return response.choices[0].message.content or ""


def iter_records(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        with path.open("r", encoding="utf-8") as fh:
            for index, line in enumerate(fh):
                line = line.strip()
                if not line:
                    continue
                yield index, json.loads(line)
        return

    if suffix == ".json":
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            for index, record in enumerate(data):
                yield index, record
            return
        if isinstance(data, dict):
            yield 0, data
            return
        raise ValueError(f"Unsupported JSON root type: {type(data).__name__}")

    raise ValueError(f"Unsupported input format: {path.suffix}")


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def make_problem_id(prefix: str, record: dict, index: int) -> str:
    source_id = record.get("id") or record.get("image_id") or f"{index:06d}"
    return f"{prefix}_{str(source_id).replace('/', '_')}"


# 默认假设：record 中的图片路径相对于输入 JSON/JSONL 文件所在目录
# 输出阶段先保留为相对路径，不转成绝对路径
# 支持：
# image: "a.png"
# image: ["a.png", "b.png"]
# images: ["a.png", "b.png"]
def resolve_image_paths(record: dict) -> list[str]:
    raw_images = record.get("images")
    if raw_images is None:
        raw_images = record.get("image")
    if not raw_images:
        return []

    if isinstance(raw_images, str):
        raw_images = [raw_images]

    resolved_paths: list[str] = []
    for image_value in raw_images:
        image_path = Path(image_value)
        resolved_paths.append(str(image_path))

    return resolved_paths


def score_sample(sample: dict, scoring_prompt_path: Path, asset_base_dir: Path | None = None) -> dict:
    system_prompt = read_prompt(scoring_prompt_path)
    user_prompt = build_scoring_user_prompt(sample)
    response_text = call_model(
        system_prompt,
        user_prompt,
        image_paths=sample.get("image_paths", []),
        asset_base_dir=asset_base_dir,
    )
    assessment = parse_json_response(response_text)

    return {
        "preliminary_value_score": assessment.get("preliminary_value_score"),
        "preliminary_value_level": assessment.get("value_level", ""),
        "preliminary_value_reason": (assessment.get("short_reason") or "").strip(),
        "preliminary_value_dimensions": assessment.get("dimension_scores") or {},
    }


# 只收集输入 raw record 中的四个核心字段：problem_id / question_text / answer_text / image_paths
# question / answer / image_paths 由大模型从原始 JSON 中抽取，尽量保留原文。
def build_sample(
    record: dict,
    index: int,
    prefix: str,
    asset_base_dir: Path | None = None,
    scoring_prompt_path: Path | None = None,
) -> dict:
    system_prompt = read_prompt(PROMPT_PATH)
    user_prompt = build_extraction_user_prompt(record)
    response_text = call_model(system_prompt, user_prompt)
    extracted = parse_json_response(response_text)

    sample = {
        "problem_id": make_problem_id(prefix, record, index),
        "question_text": (extracted.get("question_text") or "").strip(),
        "answer_text": (extracted.get("answer_text") or "").strip(),
        "image_paths": resolve_image_paths({"images": extracted.get("image_paths", [])}),
    }

    if scoring_prompt_path is not None:
        sample.update(score_sample(sample, scoring_prompt_path, asset_base_dir=asset_base_dir))

    return sample


def main() -> None:
    parser = argparse.ArgumentParser(description="Step 1: collect question, answer, image paths, and preliminary value score")
    parser.add_argument("input", type=Path, help="Path to a JSON or JSONL file that contains raw dataset records")
    parser.add_argument("--prefix", default="m3cot")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--reset-output", action="store_true")
    parser.add_argument(
        "--scoring-prompt",
        type=Path,
        default=SCORING_PROMPT_PATH,
        help="Path to the value-scoring prompt document",
    )
    parser.add_argument("--no-scoring", action="store_true", help="Skip preliminary value scoring")
    args = parser.parse_args()

    if args.reset_output and SAMPLE_PATH.exists():
        SAMPLE_PATH.unlink()

    scoring_prompt_path = None if args.no_scoring else args.scoring_prompt

    processed = 0
    for index, record in iter_records(args.input):
        sample = build_sample(
            record,
            index,
            args.prefix,
            asset_base_dir=args.input.parent,
            scoring_prompt_path=scoring_prompt_path,
        )
        append_jsonl(SAMPLE_PATH, sample)
        print(f"built sample: {sample['problem_id']}")
        processed += 1
        if args.limit and processed >= args.limit:
            break

    print(f"Saved {processed} sample(s) to {SAMPLE_PATH}")


if __name__ == "__main__":
    main()
