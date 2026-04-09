#!/usr/bin/env python3
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "benchmark" / "src"))

from multidataset_cleaning_pipeline import main

if __name__ == "__main__":
    raise SystemExit(main())
