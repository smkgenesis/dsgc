from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DSGCConfig:
    lambda_delta: float = 0.1
    lambda_pi: float = 0.3
    lambda_p: float = 1.0
    lambda_r: float = 0.2
    lambda_u: float = 0.1
    gamma: float = 0.5
    tau_compact_percentile: float = 0.5
    tau_recall: float = 0.5
    l1_budget: int = 256
    embedding_dim: int = 256
    relevance_temperature: float = 0.25
    density_exponent: float = 0.25
    recall_max_hops: int = 8
    encoder_type: str = "frozen"  # "frozen" | "sentence"
    sentence_model: str = "all-MiniLM-L6-v2"
