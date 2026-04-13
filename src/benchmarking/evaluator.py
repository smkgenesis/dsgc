from __future__ import annotations

import re


def prerequisite_retention(retained_ids: set[str], prerequisite_ids: list[str]) -> float:
    if not prerequisite_ids:
        return 0.0
    return len(retained_ids & set(prerequisite_ids)) / len(prerequisite_ids)


def full_chain_retention(retained_ids: set[str], chain_ids: list[str]) -> float:
    return float(set(chain_ids).issubset(retained_ids))


def normalize_answer(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def answer_accuracy(predicted: str, ground_truth: str) -> float:
    return float(normalize_answer(predicted) == normalize_answer(ground_truth))
