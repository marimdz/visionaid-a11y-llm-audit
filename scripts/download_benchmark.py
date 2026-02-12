#!/usr/bin/env python3
"""
Download and extract the Tabular Accessibility Dataset (Zenodo) into data/.
Run from repository root: python scripts/download_benchmark.py
"""
from pathlib import Path
import zipfile
import urllib.request
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
ZENODO_URL = "https://zenodo.org/records/17062188/files/manuandru/LLM-WebAccessibility-v2.1.0.zip?download=1"
ZIP_PATH = DATA_DIR / "LLM-WebAccessibility-v2.1.0.zip"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if ZIP_PATH.exists():
        print(f"Zip already exists: {ZIP_PATH}")
    else:
        print("Downloading dataset from Zenodo...")
        urllib.request.urlretrieve(ZENODO_URL, ZIP_PATH)
        print(f"Saved to {ZIP_PATH}")
    print("Extracting...")
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        # Extract into data/; zip has one top-level dir (e.g. manuandru-LLM-WebAccessibility-eae77a6)
        zf.extractall(DATA_DIR)
    print("Done. Benchmark path:", DATA_DIR / "manuandru-LLM-WebAccessibility-eae77a6" / "Dynamic Generated Content")


if __name__ == "__main__":
    main()
    sys.exit(0)
