#!/usr/bin/env python3
"""
Download AccessGuru dataset CSVs (static HTML violations) into data/accessguru/.
Run from repository root: python scripts/download_accessguru.py

Data from: NadeenAhmad/AccessGuruLLM (ASSETS '25).
https://github.com/NadeenAhmad/AccessGuruLLM
"""
from pathlib import Path
import urllib.request
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
ACCESSGURU_DIR = REPO_ROOT / "data" / "accessguru"
ACCESSGURU_DATASET_DIR = ACCESSGURU_DIR / "accessguru_dataset"
BASE = "https://raw.githubusercontent.com/NadeenAhmad/AccessGuruLLM/main/data/accessguru_dataset"

FILES = [
    "accessguru_sampled_syntax_layout_dataset.csv",
    "accessguru_sampled_semantic_violations.csv",
    "Original_full_data.csv",
]


def main() -> None:
    ACCESSGURU_DATASET_DIR.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        path = ACCESSGURU_DATASET_DIR / name
        url = f"{BASE}/{name}"
        if path.exists():
            print(f"Exists: {path}")
            continue
        print(f"Downloading {name}...")
        try:
            urllib.request.urlretrieve(url, path)
            print(f"  -> {path}")
        except Exception as e:
            print(f"  Failed: {e}", file=sys.stderr)
    print("Done. AccessGuru slice will use CSVs in", ACCESSGURU_DATASET_DIR)


if __name__ == "__main__":
    main()
    sys.exit(0)
