"""
Score LLM audit results against ground-truth labels (binary: has_issues or not).
"""
from __future__ import annotations

from dataclasses import dataclass

from src.dataset import Sample
from src.llm import LLMResponse
from src.runner import parse_verdict


@dataclass
class BinaryMetrics:
    """Binary classification metrics (accessible vs has_issues)."""
    accuracy: float
    tp: int
    tn: int
    fp: int
    fn: int
    total: int
    unclear: int  # responses that could not be parsed


def score_binary(
    results: list[tuple[Sample, LLMResponse]],
    parse_fn: callable = parse_verdict,
) -> BinaryMetrics:
    """
    Compare LLM verdicts to ground truth. Treats unclear parses as wrong for accuracy.
    """
    tp = tn = fp = fn = unclear = 0
    for sample, resp in results:
        pred = parse_fn(resp.content)
        gt = sample.has_issues
        if pred is None:
            unclear += 1
            # Count as wrong
            if gt:
                fn += 1
            else:
                fp += 1
        elif pred and gt:
            tp += 1
        elif not pred and not gt:
            tn += 1
        elif pred and not gt:
            fp += 1
        else:
            fn += 1
    total = len(results)
    correct = tp + tn
    accuracy = correct / total if total else 0.0
    return BinaryMetrics(
        accuracy=accuracy,
        tp=tp, tn=tn, fp=fp, fn=fn,
        total=total,
        unclear=unclear,
    )


def f1_binary(metrics: BinaryMetrics) -> float:
    """F1 for the positive class (has_issues)."""
    p = metrics.tp / (metrics.tp + metrics.fp) if (metrics.tp + metrics.fp) > 0 else 0.0
    r = metrics.tp / (metrics.tp + metrics.fn) if (metrics.tp + metrics.fn) > 0 else 0.0
    return 2 * p * r / (p + r) if (p + r) > 0 else 0.0
