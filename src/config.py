"""Paths and configuration for the benchmark."""
from pathlib import Path

# Repository root (parent of src/)
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
# Zenodo extract folder name (version-dependent)
BENCHMARK_DIR_NAME = "manuandru-LLM-WebAccessibility-eae77a6"
DYNAMIC_CONTENT_DIR = DATA_DIR / BENCHMARK_DIR_NAME / "Dynamic Generated Content"
BENCHMARK_DATA_DIR = DYNAMIC_CONTENT_DIR / "data"
BENCHMARK_EVAL_DIR = DYNAMIC_CONTENT_DIR / "eval"
LABELS_CSV = BENCHMARK_EVAL_DIR / "labels.csv"
ACCESSIBILITY_REPORTS_DIR = BENCHMARK_EVAL_DIR / "accessibility-reports"

# Zenodo dataset
ZENODO_URL = "https://zenodo.org/records/17062188/files/manuandru/LLM-WebAccessibility-v2.1.0.zip?download=1"
ZIP_NAME = "LLM-WebAccessibility-v2.1.0.zip"

# Vue Table Components (25 deliveries)
VUE_TABLE_DIR = DATA_DIR / BENCHMARK_DIR_NAME / "Vue Table Components"
VUE_TABLE_DATA_DIR = VUE_TABLE_DIR / "data"
VUE_LABELS_CSV = VUE_TABLE_DIR / "eval" / "labels.csv"

# AccessGuru (static HTML violations)
ACCESSGURU_DIR = DATA_DIR / "accessguru"
ACCESSGURU_DATASET_DIR = ACCESSGURU_DIR / "accessguru_dataset"
ACCESSGURU_REPO_RAW = "https://raw.githubusercontent.com/NadeenAhmad/AccessGuruLLM/main/data"
