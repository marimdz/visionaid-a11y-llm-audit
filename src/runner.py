"""
Run accessibility audit with an LLM and a prompt template.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from .dataset import Sample, load_benchmark_slices
from .llm import BaseLLM, LLMResponse


def load_prompt_template(name: str, prompts_dir: Path | None = None) -> str:
    """Load a prompt template by name (e.g. audit_binary)."""
    prompts_dir = prompts_dir or (Path(__file__).resolve().parent.parent / "prompts")
    path = prompts_dir / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")
    return path.read_text(encoding="utf-8")


def fill_prompt(template: str, *, file_name: str, language: str, code: str) -> str:
    """Replace {{file_name}}, {{language}}, {{code}} in template."""
    return template.replace("{{file_name}}", file_name).replace(
        "{{language}}", language
    ).replace("{{code}}", code)


def run_sample(
    sample: Sample,
    llm: BaseLLM,
    template: str,
    max_tokens: int = 2048,
) -> tuple[Sample, LLMResponse]:
    """Run the LLM on one sample; return (sample, response)."""
    prompt = fill_prompt(
        template,
        file_name=sample.file_name,
        language=sample.language,
        code=sample.code,
    )
    resp = llm.complete(prompt, max_tokens=max_tokens)
    return sample, resp


def run_benchmark(
    llm: BaseLLM,
    prompt_name: str = "audit_binary",
    prompts_dir: Path | None = None,
    slices: tuple[str, ...] = ("dynamic", "vue", "accessguru"),
    max_tokens: int = 2048,
) -> list[tuple[Sample, LLMResponse]]:
    """Load requested slices, run each sample with the given LLM and prompt; return list of (sample, response)."""
    template = load_prompt_template(prompt_name, prompts_dir=prompts_dir)
    samples = load_benchmark_slices(slices=slices)
    results = []
    for sample in samples:
        _, resp = run_sample(sample, llm, template, max_tokens=max_tokens)
        results.append((sample, resp))
    return results


def parse_verdict(response_text: str) -> bool | None:
    """
    Parse LLM response to a binary verdict: True = has_issues, False = accessible, None = unclear.
    Looks for VERDICT: HAS_ISSUES / VERDICT: ACCESSIBLE, or standalone HAS_ISSUES / ACCESSIBLE.
    """
    text = (response_text or "").strip().upper()
    if not text:
        return None
    # Explicit VERDICT: line
    m = re.search(r"VERDICT:\s*(ACCESSIBLE|HAS_ISSUES)", text)
    if m:
        return m.group(1) == "HAS_ISSUES"
    # Standalone first line
    if re.match(r"^(ACCESSIBLE|HAS_ISSUES)\s*[-.]?", text) or text.startswith("ACCESSIBLE") or text.startswith("HAS_ISSUES"):
        if "HAS_ISSUES" in text[:30]:
            return True
        if "ACCESSIBLE" in text[:30]:
            return False
    # Anywhere in first 200 chars
    head = text[:200]
    if "HAS_ISSUES" in head and "ACCESSIBLE" not in head:
        return True
    if "ACCESSIBLE" in head and "HAS_ISSUES" not in head:
        return False
    return None


def write_benchmark_results(
    results: list[tuple[Sample, LLMResponse]],
    provider: str,
    prompt_name: str,
    model: str | None = None,
    output_dir: Path | None = None,
) -> tuple[int, int]:
    """
    Write model solutions and comparison to a results folder (JSON + TXT).
    Returns (total_input_tokens, total_output_tokens).
    """
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = output_dir or (repo_root / "results")
    output_dir.mkdir(parents=True, exist_ok=True)

    model_name = model or (results[0][1].model if results else "unknown")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = re.sub(r"[^\w\-]", "_", f"{provider}_{model_name}_{prompt_name}")[:80]
    base_name = f"{stamp}_{safe}"

    total_in, total_out = 0, 0
    rows = []
    for sample, resp in results:
        pred = parse_verdict(resp.content)
        gt = sample.has_issues
        if pred is None:
            correct = False
        else:
            correct = pred == gt
        if resp.input_tokens is not None:
            total_in += resp.input_tokens
        if resp.output_tokens is not None:
            total_out += resp.output_tokens
        rows.append({
            "file_name": sample.file_name,
            "slice": sample.slice,
            "has_issues_ground_truth": gt,
            "model_response": resp.content,
            "parsed_verdict": "has_issues" if pred is True else ("accessible" if pred is False else "unclear"),
            "correct": correct,
            "input_tokens": resp.input_tokens,
            "output_tokens": resp.output_tokens,
        })

    correct_count = sum(1 for r in rows if r["correct"])
    total = len(rows)
    accuracy = correct_count / total if total else 0.0

    payload = {
        "run": {
            "provider": provider,
            "model": model_name,
            "prompt_name": prompt_name,
            "timestamp": stamp,
        },
        "summary": {
            "total_samples": total,
            "correct": correct_count,
            "accuracy": accuracy,
            "total_input_tokens": total_in,
            "total_output_tokens": total_out,
        },
        "samples": rows,
    }

    json_path = output_dir / f"{base_name}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    txt_path = output_dir / f"{base_name}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Provider: {provider}  Model: {model_name}  Prompt: {prompt_name}\n")
        f.write(f"Accuracy: {accuracy:.2%}  Correct: {correct_count}/{total}\n")
        f.write(f"Tokens: input={total_in:,}  output={total_out:,}\n\n")
        f.write("-" * 80 + "\n")
        for r in rows:
            f.write(f"File: {r['file_name']}  slice={r['slice']}\n")
            f.write(f"  Ground truth: has_issues={r['has_issues_ground_truth']}\n")
            f.write(f"  Parsed: {r['parsed_verdict']}  correct={r['correct']}\n")
            f.write(f"  Response: {r['model_response'][:500]}{'...' if len(r['model_response']) > 500 else ''}\n")
            f.write(f"  Tokens: in={r['input_tokens']} out={r['output_tokens']}\n\n")

    return total_in, total_out
