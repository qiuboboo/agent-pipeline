# from huggingface download M3CoT test set.
# first download the parquet files.
# then load them with datasets and save as jsonl with images saved separately.

from pathlib import Path
import json
import os

# Set up proxy for Hugging Face datasets if needed
os.environ["HTTP_PROXY"] = "http://127.0.0.1:10809"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:10809"

from datasets import load_dataset
from huggingface_hub import HfApi, hf_hub_download

DATASET_NAME = "LightChen2333/M3CoT"
SPLIT = "test"
OUTPUT_DIR = Path("m3cot")
PARQUET_DIR = OUTPUT_DIR / "parquet"
IMAGES_DIR = OUTPUT_DIR / "images"
OUTPUT_FILE = OUTPUT_DIR / "test.jsonl"


def make_json_safe(value):
    if isinstance(value, dict):
        return {k: make_json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [make_json_safe(v) for v in value]
    return value


def save_image(image, index: int) -> str:
    image_path = IMAGES_DIR / f"{index:06d}.png"
    image.save(image_path)
    return image_path.as_posix()


def list_test_parquet_files(hf_token: str) -> list[str]:
    api = HfApi(token=hf_token)
    repo_files = api.list_repo_files(DATASET_NAME, repo_type="dataset")
    parquet_files = [path for path in repo_files if path.endswith(".parquet")]
    test_files = [
        path
        for path in parquet_files
        if Path(path).name.startswith(f"{SPLIT}-") or f"/{SPLIT}-" in path
    ]

    if not test_files:
        available = "\n".join(parquet_files[:50])
        raise RuntimeError(
            f"Could not find parquet files for split={SPLIT!r}. Available parquet files:\n{available}"
        )

    return sorted(test_files)


def download_parquet_files(parquet_files: list[str], hf_token: str) -> list[str]:
    PARQUET_DIR.mkdir(parents=True, exist_ok=True)
    local_files = []
    for parquet_file in parquet_files:
        local_path = hf_hub_download(
            repo_id=DATASET_NAME,
            repo_type="dataset",
            filename=parquet_file,
            token=hf_token,
            local_dir=PARQUET_DIR,
            local_dir_use_symlinks=False,
        )
        local_files.append(local_path)
    return local_files


def main() -> None:
    # unauthenticated API calls have very low rate limits, so we require a token
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise RuntimeError("HF_TOKEN is not set. Please export your Hugging Face token first.")

    parquet_files = list_test_parquet_files(hf_token)
    print(f"Found {len(parquet_files)} parquet file(s) for split={SPLIT!r}.")

    local_parquet_files = download_parquet_files(parquet_files, hf_token)
    print(f"Downloaded parquet files to {PARQUET_DIR.resolve()}")

    dataset = load_dataset("parquet", data_files=local_parquet_files, split="train")

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for row in dataset:
            image = row.get("image")
            if image is not None:
                row["image"] = save_image(image, count)
            f.write(json.dumps(make_json_safe(row), ensure_ascii=False) + "\n")
            count += 1

    print(f"Saved {count} records to {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
