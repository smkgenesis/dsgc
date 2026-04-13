from __future__ import annotations

import math


def dot(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    return sum(x * y for x, y in zip(a, b))


def softmax(values: list[float]) -> list[float]:
    if not values:
        return []
    shifted = [v - max(values) for v in values]
    exp_values = [math.exp(v) for v in shifted]
    total = sum(exp_values)
    if total == 0.0:
        return [0.0 for _ in values]
    return [v / total for v in exp_values]
