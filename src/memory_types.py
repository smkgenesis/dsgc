from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MemoryTier(str, Enum):
    L1 = "l1"
    L2 = "l2"
    L3 = "l3"


@dataclass(slots=True)
class Metadata:
    turn_index: int
    pin: bool = False
    access_count: int = 0
    source_type: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Fact:
    fact: str
    kind: str
    confidence: float = 0.0
    derived_from: list[str] = field(default_factory=list)
    anchor: str | None = None
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MemoryBlock:
    block_id: str
    raw_text: str
    block_type: str
    source_type: str
    embedding: tuple[float, ...] = field(default_factory=tuple)
    tier: MemoryTier = MemoryTier.L1
    token_count: int = 0
    pinned: bool = False
    facts: list[Fact] = field(default_factory=list)
    dependency_ids: list[str] = field(default_factory=list)
    usage_count: int = 0
    metadata: Metadata = field(default_factory=lambda: Metadata(turn_index=0))
    fact_pack: str | None = None
    raw_ptr: str | None = None


@dataclass(slots=True)
class GoalState:
    text: str
    constraints: list[str] = field(default_factory=list)
    obligations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BudgetState:
    l1_token_capacity: int
    l2_token_capacity: int
    recall_token_budget: int
    gc_compute_budget_ms: int | None = None
    recall_latency_budget_ms: int | None = None
