"""
Load benchmark slices: Dynamic Generated Content, Vue Table Components, AccessGuru.

- Dynamic: Andruccioli et al., Data 2025, 10(9), 149. https://doi.org/10.3390/data10090149
- Vue: same Zenodo dataset, 25 delivery projects.
- AccessGuru: Fathallah et al., ASSETS '25. https://github.com/NadeenAhmad/AccessGuruLLM
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .config import (
    BENCHMARK_DATA_DIR,
    LABELS_CSV,
    VUE_TABLE_DATA_DIR,
    VUE_LABELS_CSV,
    ACCESSGURU_DATASET_DIR,
)


@dataclass
class Sample:
    """A single code sample with ground-truth accessibility labels."""
    file_name: str
    code: str
    has_issues: bool  # Binary: True = has at least one issue (derived from labels)
    language: str  # js, php, vue, html
    reference_issues: list[dict]  # Full labels (structure depends on slice)
    slice: str = "dynamic"  # "dynamic" | "vue" | "accessguru"


def _detect_language(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".vue":
        return "vue"
    if ext == ".php":
        return "php"
    if ext in (".js", ".jsx", ".ts", ".tsx"):
        return "js"
    return ext.lstrip(".") or "unknown"


def load_labels(labels_path: Path) -> dict[str, list[dict]]:
    """Load labels.csv (semicolon-separated). Returns dict: file_name -> list of issue rows."""
    by_file: dict[str, list[dict]] = {}
    if not labels_path.exists():
        return by_file
    with open(labels_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            name = row.get("File", "").strip()
            if not name:
                continue
            by_file.setdefault(name, []).append(row)
    return by_file


def load_dynamic_content_benchmark(
    data_dir: Path | None = None,
    labels_path: Path | None = None,
) -> list[Sample]:
    """
    Load all code samples from Dynamic Generated Content with ground-truth labels.

    - Code files live in data_dir (default: benchmark data directory). Only .js, .php, .vue
      are loaded (e.g. songs.json is excluded), so this returns 9 samples.
    - labels.csv has one row per issue (File; Row; Analyzed Code; Success Criterion; Problem Found).
      Files with any row are has_issues=True; files with no rows are accessible.
    """
    data_dir = data_dir or BENCHMARK_DATA_DIR
    labels_path = labels_path or LABELS_CSV
    labels_by_file = load_labels(labels_path)

    samples: list[Sample] = []
    # Only load code files (exclude songs.json etc.)
    code_extensions = {".js", ".php", ".vue"}
    for path in sorted(data_dir.iterdir()):
        if not path.is_file() or path.suffix.lower() not in code_extensions:
            continue
        name = path.name
        code = path.read_text(encoding="utf-8", errors="replace")
        issue_rows = labels_by_file.get(name, [])
        has_issues = len(issue_rows) > 0
        samples.append(
            Sample(
                file_name=name,
                code=code,
                has_issues=has_issues,
                language=_detect_language(path),
                reference_issues=issue_rows,
                slice="dynamic",
            )
        )
    return samples


def _load_vue_labels(labels_path: Path | None = None) -> set[tuple[str, str]]:
    """Load Vue labels.csv; return set of (Project, Component) that have at least one issue."""
    labels_path = labels_path or VUE_LABELS_CSV
    out: set[tuple[str, str]] = set()
    if not labels_path.exists():
        return out
    with open(labels_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            proj = (row.get("Project") or "").strip()
            comp = (row.get("Component") or "").strip()
            if proj and comp:
                out.add((proj, comp))
    return out


def load_vue_table_benchmark(
    data_dir: Path | None = None,
    labels_path: Path | None = None,
) -> list[Sample]:
    """
    Load Vue Table Components: one sample per (delivery, component).
    Each sample = concatenated .vue files in that component folder.
    has_issues = (Project, Component) appears in labels.csv.
    """
    data_dir = data_dir or VUE_TABLE_DATA_DIR
    labels_path = labels_path or VUE_LABELS_CSV
    has_issues_set = _load_vue_labels(labels_path)
    labels_by_key: dict[tuple[str, str], list[dict]] = {}
    if labels_path.exists():
        with open(labels_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                proj = (row.get("Project") or "").strip()
                comp = (row.get("Component") or "").strip()
                if proj and comp:
                    labels_by_key.setdefault((proj, comp), []).append(row)

    samples: list[Sample] = []
    if not data_dir.exists():
        return samples

    for delivery_dir in sorted(data_dir.iterdir()):
        if not delivery_dir.is_dir() or not delivery_dir.name.startswith("delivery-"):
            continue
        src_dir = delivery_dir / "src"
        if not src_dir.is_dir():
            continue
        project = delivery_dir.name
        for comp_dir in sorted(src_dir.iterdir()):
            if not comp_dir.is_dir():
                continue
            # Skip App.vue, assets, style, etc.; keep minimal-*, accessible-*
            name = comp_dir.name
            if name in ("assets", "style", "components") or name.endswith(".vue"):
                continue
            vue_files = sorted(comp_dir.rglob("*.vue"))
            if not vue_files:
                continue
            parts = []
            for vf in vue_files:
                try:
                    parts.append(f"// --- {vf.name} ---\n{vf.read_text(encoding='utf-8', errors='replace')}")
                except OSError:
                    continue
            if not parts:
                continue
            code = "\n\n".join(parts)
            key = (project, name)
            has_issues = key in has_issues_set
            ref_issues = labels_by_key.get(key, [])
            samples.append(
                Sample(
                    file_name=f"{project}_{name}",
                    code=code,
                    has_issues=has_issues,
                    language="vue",
                    reference_issues=ref_issues,
                    slice="vue",
                )
            )
    return samples


def load_accessguru_benchmark(
    dataset_dir: Path | None = None,
    max_samples: int | None = 500,
) -> list[Sample]:
    """
    Load AccessGuru static HTML snippets (violations). Each CSV row = one sample.
    All rows have has_issues=True. Code = affected_html_elements (strip backticks).
    """
    dataset_dir = dataset_dir or ACCESSGURU_DATASET_DIR
    samples: list[Sample] = []
    if not dataset_dir.exists():
        return samples

    csv_files = [
        dataset_dir / "accessguru_sampled_syntax_layout_dataset.csv",
        dataset_dir / "accessguru_sampled_semantic_violations.csv",
        dataset_dir / "Original_full_data.csv",
    ]
    seen_ids: set[str] = set()
    for csv_path in csv_files:
        if not csv_path.exists():
            continue
        if max_samples and len(samples) >= max_samples:
            break
        with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if max_samples and len(samples) >= max_samples:
                    break
                # Column name varies by CSV: affected_html_elements, affectedHTMLElement(s), Affected HTML, etc.
                code = (
                    row.get("affected_html_elements")
                    or row.get("affected_html_element")
                    or row.get("affectedHTMLElement(s)")
                    or row.get("Affected HTML")
                    or row.get("html", "")
                )
                if not code or not str(code).strip():
                    continue
                code = str(code).strip().strip("`").strip()
                if not code:
                    continue
                uid = row.get("id", str(len(samples)))
                if uid in seen_ids:
                    continue
                seen_ids.add(uid)
                ref = {k: v for k, v in row.items() if v}
                samples.append(
                    Sample(
                        file_name=row.get("html_file_name", uid),
                        code=code,
                        has_issues=True,
                        language="html",
                        reference_issues=[ref],
                        slice="accessguru",
                    )
                )
    return samples


def load_benchmark_slices(
    slices: tuple[str, ...] = ("dynamic", "vue", "accessguru"),
) -> list[Sample]:
    """Load and concatenate samples from the requested slices."""
    out: list[Sample] = []
    if "dynamic" in slices:
        out.extend(load_dynamic_content_benchmark())
    if "vue" in slices:
        out.extend(load_vue_table_benchmark())
    if "accessguru" in slices:
        out.extend(load_accessguru_benchmark())
    return out


def get_benchmark_available(slices: tuple[str, ...] = ("dynamic",)) -> bool:
    """Return True if the requested slice(s) have data available."""
    if "dynamic" in slices and (not BENCHMARK_DATA_DIR.exists() or not LABELS_CSV.exists()):
        return False
    if "vue" in slices and (not VUE_TABLE_DATA_DIR.exists() or not VUE_LABELS_CSV.exists()):
        return False
    if "accessguru" in slices:
        if not ACCESSGURU_DATASET_DIR.exists():
            return False
        any_csv = next(ACCESSGURU_DATASET_DIR.glob("*.csv"), None)
        if not any_csv:
            return False
    return True
