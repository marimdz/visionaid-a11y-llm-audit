# Project: P5 – Automating Digital Accessibility

## What This Project Does

This project builds LLM-powered tools that analyze websites for WCAG accessibility issues and generate structured remediation reports. It is a Computing for Good course project at Georgia Tech (OMSCS) partnered with the Vision Aid Digital Accessibility Testing Team.

The system has three planned stages:
1. Automated webpage accessibility analysis → structured CSV reports
2. Code remediation suggestions based on those reports
3. (Stretch) Chrome extension for on-the-fly accessibility fixes

## Architecture Overview

```
project-root/
├── prompts/                  # Modular prompt components
│   ├── task_instructions.py  # 6 task instruction variations (simple → chain-of-thought)
│   ├── guideline_variations.py  # 3 WCAG guideline levels (zero-shot, principle, full)
│   └── report_formatting.py  # CSV report format specification
├── scripts/
│   ├── generate_prompt.py    # Assembles prompts from modular components (18 combinations)
│   └── run_factorial_test.py # Runs all prompt combinations against HTML input via API
├── test_files/               # HTML files to analyze (may be very large, 500K+ tokens)
└── [preprocessing pipeline]  # HTML parsing/preprocessing (Annika & Andrew's work)
```

## Tech Stack

- Python 3.x (use virtual environment: `source venv/bin/activate`)
- Anthropic API (Claude Sonnet 4.5 preferred for testing — `claude-sonnet-4-20250514`)
- HTML preprocessing: BeautifulSoup / custom parsers (check imports in preprocessing files)
- Accessibility tools context: axe-core, Lighthouse, WAVE (hybrid approach)
- Output format: CSV with columns — ID, element_name, browser_combination, page_title, issue_title, steps_to_reproduce, actual_result, expected_result, recommendation, wcag_sc, category, log_date, reported_by

## Current Task: Codebase Analysis for Prompt Modularization

### Context

The existing prompt system (`prompts/` + `scripts/generate_prompt.py`) builds monolithic prompts that analyze an entire HTML file at once. The team's preprocessing pipeline now parses HTML into smaller structural units (headings, forms, tables, ARIA regions, etc.). The next step is to **modularize the prompt system so that specific, targeted prompts can be generated for individual HTML elements or element types** identified by the preprocessor.

For example: if the preprocessor identifies a `<table>` element, a table-specific prompt should be generated that includes only the relevant WCAG criteria for data tables (header associations, scope attributes, captions, etc.) and asks the LLM to evaluate just that element.

### Your Task

**Phase 1: Discover and Document**

1. Read every file in the repo. Start with `prompts/`, `scripts/`, and any preprocessing directories.
2. Identify the preprocessing pipeline entry points and understand:
   - What HTML elements/sections does it extract?
   - What data structures does it output? (dicts, lists, DOM fragments, plain strings?)
   - How does it chunk or categorize elements?
3. Understand the existing prompt assembly system:
   - How does `generate_prompt.py` combine components from `prompts/`?
   - What is the interface between prompt generation and the API test runner?
   - Where are the WCAG guidelines stored and how are they referenced?
4. Map the connection points (or gaps) between preprocessing output and prompt input.

**Phase 2: Produce an Architectural Plan**

Write a file called `docs/modular-prompts-plan.md` containing:

1. **Current State Summary** — What exists, how it works, key file paths and functions.
2. **Proposed Element-Specific Prompt Architecture** — How to create targeted prompts for different element types (headings, tables, forms, images, links, ARIA landmarks, iframes, lists, etc.). Consider:
   - A registry/mapping of element types → relevant WCAG criteria subsets
   - A prompt template system that accepts a single element or element group plus its surrounding context
   - How the CSV report format stays consistent across element-specific analyses
   - How results from multiple element-specific prompts get aggregated into one report
3. **Integration Points** — Exactly where and how the preprocessing output feeds into the new prompt system. Name specific functions, classes, or files that need to change.
4. **Cost/Token Analysis** — Compare estimated token usage of the element-specific approach vs. the current monolithic approach. The monolithic approach uses ~487K input tokens per request for the test HTML file.
5. **Recommended Implementation Order** — Which element types to modularize first (prioritize those with the clearest WCAG criteria mappings and highest impact).
6. **Open Questions** — Anything unclear from the codebase that the team needs to resolve.

## Code Patterns

- Prompt components are Python files with module-level string variables (not classes)
- `generate_prompt.py` uses dicts to map variation names to prompt strings
- The factorial test runner iterates over all combinations and calls the Anthropic API
- File encoding: use `encoding='utf-8', errors='replace'` when reading HTML files

## Style Rules

- Python code: standard PEP 8
- Docstrings for all new functions
- Use `pathlib.Path` for file paths (consistent with existing scripts)
- Commit messages: descriptive, prefixed with area (e.g., "prompts: add element-specific template system")

## Do NOT

- Do not call the Anthropic API or spend any money — this task is analysis only
- Do not delete or overwrite existing prompt files — propose additions alongside them
- Do not refactor the preprocessing pipeline — document it as-is and propose integration points
- Do not create placeholder/stub implementations yet — this phase is strictly planning
- Do not install new dependencies
- Do not modify test_files/ or any HTML input files

## Common Issues

- HTML test files can be enormous (500K+ tokens) — do not try to read them fully into context
- Some files may have non-UTF-8 encoding; always use `errors='replace'`
- The `prompts/` directory uses bare string variables, not functions — note this when proposing the new architecture (functions or classes may be more appropriate for parameterized element-specific prompts)

## When You're Done

Output the completed `docs/modular-prompts-plan.md` and print a summary of:
- Number of files examined
- Key preprocessing functions/classes found
- Top 3 recommended element types to modularize first
- Any blockers or questions for the team
