# Benchmark data

This directory holds the **Tabular Accessibility Dataset** used for the LLM audit benchmark.

## Setup

Run from the repository root:

```bash
python scripts/download_benchmark.py
```

This will:

1. Download `LLM-WebAccessibility-v2.1.0.zip` from [Zenodo](https://doi.org/10.5281/zenodo.17062188).
2. Extract it here. The benchmark lives under `manuandru-LLM-WebAccessibility-eae77a6/Dynamic Generated Content/` (code in `data/`, labels and reports in `eval/`).

The zip and the extracted folder are gitignored; re-run the script to fetch the data.

## Citation

Andruccioli, M.; Bassi, B.; Delnevo, G.; Salomoni, P. *The Tabular Accessibility Dataset: A Benchmark for LLM-Based Web Accessibility Auditing.* Data 2025, 10(9), 149. https://doi.org/10.3390/data10090149

Dataset: https://doi.org/10.5281/zenodo.17062188 (CC BY 4.0).
