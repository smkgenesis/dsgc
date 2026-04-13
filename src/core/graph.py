from __future__ import annotations

from collections import defaultdict


class DependencyGraph:
    """Edge convention: (i, j) means block i depends on block j."""

    def __init__(self) -> None:
        self._out: dict[str, set[str]] = defaultdict(set)
        self._in: dict[str, set[str]] = defaultdict(set)

    def add_edge(self, dependent: str, prerequisite: str) -> None:
        self._out[dependent].add(prerequisite)
        self._in[prerequisite].add(dependent)

    def n_in(self, block_id: str) -> set[str]:
        return set(self._in.get(block_id, set()))

    def n_out(self, block_id: str) -> set[str]:
        return set(self._out.get(block_id, set()))

    @property
    def num_nodes(self) -> int:
        return len(set(self._in) | set(self._out))
