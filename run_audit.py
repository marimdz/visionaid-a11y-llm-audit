#!/usr/bin/env python3
"""
Run accessibility audit benchmark: run one or more LLMs with one or more prompts,
then score against the Tabular Accessibility Dataset and print metrics.

Usage (from repo root):
  pip install -r requirements.txt
  export GEMINI_API_KEY=...   # or DEEPSEEK_API_KEY, MOONSHOT_API_KEY
  python run_audit.py [--provider gemini|deepseek|kimi] [--prompt audit_binary|...]
  python run_audit.py --compare   # run all provider×model×prompt combos and print table + token usage
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

# Ensure repo root on path
REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.dataset import get_benchmark_available, load_benchmark_slices
from src.llm import get_llm, LLMResponse
from src.runner import run_benchmark
from scoring.score import score_binary, f1_binary, BinaryMetrics

# Default providers (cost-effective); optional: openai, anthropic
PROVIDERS = ["gemini", "deepseek", "kimi"]
# Multiple models per provider for --compare
MODELS_BY_PROVIDER = {
    "gemini": ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
    "deepseek": ["deepseek-chat", "deepseek-reasoner"],
    "kimi": ["moonshot-v1-8k", "kimi-k2-0905-preview", "kimi-k2-turbo-preview"],
    "openai": ["gpt-4o-mini", "gpt-4o"],
    "anthropic": ["claude-3-5-haiku-20241022"],
}
PROMPTS = ["audit_binary", "audit_with_reason", "audit_wcag_focused"]
SLICES = ("dynamic", "vue", "accessguru")


def token_totals(results: list) -> tuple[int, int]:
    """Sum input_tokens and output_tokens from (sample, LLMResponse) results."""
    total_in, total_out = 0, 0
    for _, resp in results:
        if isinstance(resp, LLMResponse):
            if resp.input_tokens is not None:
                total_in += resp.input_tokens
            if resp.output_tokens is not None:
                total_out += resp.output_tokens
    return total_in, total_out


def run_one(
    provider: str,
    prompt: str,
    model: str | None = None,
    slices: tuple[str, ...] = SLICES,
):
    llm = get_llm(provider, model=model)
    results = run_benchmark(llm, prompt_name=prompt, slices=slices)
    return score_binary(results), results


def _parse_slices(s: str) -> tuple[str, ...]:
    if s.strip().lower() == "all":
        return SLICES
    return tuple(x.strip().lower() for x in s.split(",") if x.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Run LLM accessibility audit benchmark")
    parser.add_argument("--provider", choices=PROVIDERS + ["openai", "anthropic"], default="gemini")
    parser.add_argument("--model", type=str, default=None, help="Model name (default per provider)")
    parser.add_argument("--prompt", type=str, default="audit_binary", choices=PROMPTS)
    parser.add_argument("--slices", type=str, default="all",
                        help="Comma-separated: dynamic,vue,accessguru or 'all' (default)")
    parser.add_argument("--compare", action="store_true",
                        help="Run all provider×prompt combinations and print comparison table")
    parser.add_argument("--list-samples", action="store_true", help="List benchmark samples and exit")
    parser.add_argument("--no-run", action="store_true", help="Only load benchmark, don't call LLM")
    args = parser.parse_args()

    slices = _parse_slices(args.slices)
    if not get_benchmark_available(slices=slices):
        print("Benchmark data missing for requested slices.", file=sys.stderr)
        print("  dynamic:  python scripts/download_benchmark.py", file=sys.stderr)
        print("  accessguru:  python scripts/download_accessguru.py", file=sys.stderr)
        return 1

    if args.list_samples:
        samples = load_benchmark_slices(slices=slices)
        by_slice = {}
        for s in samples:
            by_slice.setdefault(s.slice, []).append(s)
        for sl in slices:
            n = len(by_slice.get(sl, []))
            print(f"  [{sl}] {n} samples")
        for s in samples:
            print(f"  {s.slice}  {s.file_name}  has_issues={s.has_issues}  lang={s.language}")
        return 0

    if args.no_run:
        samples = load_benchmark_slices(slices=slices)
        by_slice = {}
        for s in samples:
            by_slice.setdefault(s.slice, []).append(s)
        for sl in slices:
            print(f"  {sl}: {len(by_slice.get(sl, []))} samples")
        print(f"Total: {len(samples)} samples.")
        return 0

    if args.compare:
        print("Running all provider × model × prompt combinations...\n")
        rows = []
        for provider in PROVIDERS:
            models = MODELS_BY_PROVIDER.get(provider, [])
            if not models:
                models = [None]  # use default
            for model in models:
                for prompt in PROMPTS:
                    try:
                        m, res = run_one(provider, prompt, model=model, slices=slices)
                        f1 = f1_binary(m)
                        mod = model or get_llm(provider).default_model
                        rows.append((provider, mod, prompt, m.accuracy, f1, m.unclear, res))
                    except Exception as e:
                        mod = model or "?"
                        rows.append((provider, mod, prompt, float("nan"), float("nan"), str(e), None))
        print(f"{'Provider':<10} {'Model':<28} {'Prompt':<22} {'Accuracy':>10} {'F1':>8} {'Unclear':>8}")
        print("-" * 90)
        for r in rows:
            provider, mod, prompt, acc, f1, unclear, _ = r
            acc_s = f"{acc:.2%}" if isinstance(acc, float) and acc == acc else "N/A"
            f1_s = f"{f1:.2%}" if isinstance(f1, float) and f1 == f1 else "N/A"
            u_s = str(unclear) if isinstance(unclear, int) else (str(unclear)[:12] if unclear else "0")
            print(f"{provider:<10} {mod[:27]:<28} {prompt:<22} {acc_s:>10} {f1_s:>8} {u_s:>12}")
        # Token usage per (provider, model) summed over all prompts
        print("\nToken usage (input / output) per provider×model (summed over prompts):")
        tok_by_key = defaultdict(lambda: [0, 0])
        for provider, mod, _prompt, _acc, _f1, _unclear, res in rows:
            if res is None:
                continue
            ti, to = token_totals(res)
            tok_by_key[(provider, mod)][0] += ti
            tok_by_key[(provider, mod)][1] += to
        for (provider, mod), (ti, to) in sorted(tok_by_key.items()):
            print(f"  {provider} / {mod}:  input={ti:,}  output={to:,}")
        return 0

    llm = get_llm(args.provider, model=args.model)
    print(f"Running benchmark: provider={llm.provider}, model={llm.default_model}, prompt={args.prompt}, slices={slices}")
    results = run_benchmark(llm, prompt_name=args.prompt, slices=slices)
    metrics = score_binary(results)
    f1 = f1_binary(metrics)
    ti, to = token_totals(results)
    print()
    print("Overall (binary: accessible vs has_issues)")
    print(f"  Accuracy: {metrics.accuracy:.2%}")
    print(f"  F1 (has_issues): {f1:.2%}")
    print(f"  TP={metrics.tp} TN={metrics.tn} FP={metrics.fp} FN={metrics.fn}  unclear={metrics.unclear}")
    print(f"  Tokens: input={ti:,}  output={to:,}")
    # Per-slice
    by_slice = {}
    for sample, resp in results:
        by_slice.setdefault(sample.slice, []).append((sample, resp))
    if len(by_slice) > 1:
        print("\nPer-slice:")
        for sl in sorted(by_slice.keys()):
            m = score_binary(by_slice[sl])
            f1_sl = f1_binary(m)
            print(f"  {sl}: accuracy={m.accuracy:.2%}  F1={f1_sl:.2%}  n={m.total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
