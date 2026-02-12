# visionaid-a11y-llm-audit

**Accessibility report generator and LLM benchmark** for web accessibility auditing. This repo uses the [Tabular Accessibility Dataset](https://www.mdpi.com/2306-5729/10/9/149) as a labeled benchmark to compare how different LLMs and prompts perform at detecting accessibility issues in source code.

## Benchmark and citation

The benchmark is from:

- **Article:** Andruccioli, M.; Bassi, B.; Delnevo, G.; Salomoni, P. **The Tabular Accessibility Dataset: A Benchmark for LLM-Based Web Accessibility Auditing.** *Data* **2025**, 10(9), 149. [https://doi.org/10.3390/data10090149](https://doi.org/10.3390/data10090149)
- **Dataset (Zenodo):** [https://doi.org/10.5281/zenodo.17062188](https://doi.org/10.5281/zenodo.17062188) (CC BY 4.0)

The benchmark has **three slices**:

- **dynamic (Dynamic Generated Content):** Angular, React, Vue, and PHP code — **9 samples**. Ground truth in `eval/labels.csv`.
- **vue (Vue Table Components):** 25 delivery projects × component variants (minimal/accessible, options/composition API) — **many samples**. Ground truth in `eval/labels.csv` (Project; Component; …).
- **accessguru (AccessGuru):** Static HTML snippets with real-world violations — **hundreds of samples**. Data from [AccessGuruLLM](https://github.com/NadeenAhmad/AccessGuruLLM) (ASSETS '25). All rows are violations (has_issues=True).

**Labels:** Zenodo `labels.csv` files list **per-issue** rows (Success Criterion, Problem Found, …). We derive a **binary** has_issues per sample and score the LLM’s ACCESSIBLE vs HAS_ISSUES. AccessGuru rows are all violations. Full labels are on each `Sample` as `reference_issues`.

## Setup

1. **Clone and install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Download benchmark data**

   - **Zenodo (dynamic + vue slices):**
     ```bash
     python scripts/download_benchmark.py
     ```
   - **AccessGuru (accessguru slice, static HTML):**
     ```bash
     python scripts/download_accessguru.py
     ```
   Use `--slices dynamic` to run only the 9 Dynamic samples; use `--slices all` (default) to run all slices for which data exists.

3. **Set API keys** (for running LLMs; default providers are cost-effective)

   - **Gemini:** `export GEMINI_API_KEY=...` or `GOOGLE_API_KEY=...`
   - **DeepSeek:** `export DEEPSEEK_API_KEY=...`
   - **Kimi (Moonshot):** `export MOONSHOT_API_KEY=...` or `KIMI_API_KEY=...`
   - Optional: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` for `--provider openai` / `--provider anthropic`

## Usage

- **Single run** (default provider: gemini):

  ```bash
  python run_audit.py --provider gemini --prompt audit_binary
  python run_audit.py --provider deepseek
  python run_audit.py --provider kimi
  python run_audit.py --slices dynamic,vue   # Tabular Accessibility Dataset only
  ```

- **Compare** all provider × model × prompt combinations (prints accuracy/F1 and **token usage** per model):

  ```bash
  python run_audit.py --compare
  ```
  Uses: Gemini (gemini-2.0-flash, gemini-1.5-flash, gemini-1.5-pro), DeepSeek (deepseek-chat, deepseek-reasoner), Kimi (moonshot-v1-8k, kimi-k2-0905-preview, kimi-k2-turbo-preview).

- **List samples (no API calls):**

  ```bash
  python run_audit.py --list-samples
  python run_audit.py --list-samples --slices dynamic,vue
  ```

### Prompts

Defined in `prompts/`:

- **audit_binary** – Strict one-line verdict: ACCESSIBLE or HAS_ISSUES.
- **audit_with_reason** – Verdict plus optional short explanation.
- **audit_wcag_focused** – Verdict plus WCAG criterion (e.g. 1.3.1) when HAS_ISSUES.

You can add new `.txt` templates using placeholders: `{{file_name}}`, `{{language}}`, `{{code}}`.

### Scoring

- **Binary:** Ground truth is derived from the benchmark’s `labels.csv` (files listed there are “has_issues”; others are “accessible”). The runner parses the LLM output for ACCESSIBLE / HAS_ISSUES and computes **accuracy** and **F1 (has_issues)**.

## Project layout

- `data/` – Benchmark data. Zenodo extract and `data/accessguru/` are gitignored; run the download scripts to populate.
- `prompts/` – Prompt templates for the audit task.
- `scoring/` – Binary metrics and scoring logic.
- `src/` – Dataset loaders (dynamic, vue, accessguru), LLM clients, runner.
- `run_audit.py` – CLI: default providers **gemini**, **deepseek**, **kimi**; `--compare` runs all provider×model×prompt and prints **token usage**; `--slices`, `--list-samples`.
- `PRICING.md` – Links to each provider’s pricing; use reported token counts to estimate cost.
- `scripts/download_benchmark.py` – Download Zenodo (dynamic + vue slices).
- `scripts/download_accessguru.py` – Download AccessGuru CSVs (accessguru slice).

## License

See [LICENSE](LICENSE). The benchmark dataset is CC BY 4.0 (see Zenodo page).
