from __future__ import annotations

from config import DSGCConfig
from core.encoder import make_encoder
from core.graph import DependencyGraph
from core.math_utils import dot, softmax
from policy import BaseMemoryPolicy
from memory_types import MemoryBlock, MemoryTier, Metadata


class MinimalDSGCPolicy(BaseMemoryPolicy):
    """Minimal paper-facing DSGC path: relevance + optional one-hop propagation."""

    def __init__(self, config: DSGCConfig, use_graph: bool = True) -> None:
        self.cfg = config
        self.use_graph = use_graph
        self.encoder = make_encoder(config)
        self.graph = DependencyGraph()
        self.blocks: list[MemoryBlock] = []
        self.last_step_debug: dict[str, object] = {}

    def ingest(self, text: str, block_id: str, **kwargs) -> None:
        self.blocks.append(
            MemoryBlock(
                block_id=block_id,
                raw_text=text,
                block_type=kwargs.get("block_type", "generic"),
                source_type=kwargs.get("source_type", "user"),
                embedding=self.encoder.encode(text),
                token_count=max(len(text.split()), 1),
                pinned=kwargs.get("pin", False),
                metadata=Metadata(turn_index=len(self.blocks), pin=kwargs.get("pin", False)),
            )
        )
        for dep_id in kwargs.get("dependencies", []) or []:
            self.graph.add_edge(block_id, dep_id)

    def step(self, query: str) -> list[MemoryBlock]:
        if not self.blocks:
            self.last_step_debug = {}
            return []

        goal_embedding = self.encoder.encode(query)
        temperature = max(self.cfg.relevance_temperature, 1e-6)
        alpha = [dot(block.embedding, goal_embedding) for block in self.blocks]
        relevance = softmax([value / temperature for value in alpha])

        propagated = [0.0] * len(self.blocks)
        if self.use_graph:
            id_to_idx = {block.block_id: idx for idx, block in enumerate(self.blocks)}
            for idx, block in enumerate(self.blocks):
                for dependent_id in self.graph.n_in(block.block_id):
                    dependent_idx = id_to_idx.get(dependent_id)
                    if dependent_idx is not None:
                        propagated[idx] += relevance[dependent_idx]

        exponent = self.cfg.density_exponent
        density = []
        for idx, block in enumerate(self.blocks):
            score = relevance[idx] + (self.cfg.lambda_pi * propagated[idx])
            density.append(score / (max(block.token_count, 1) ** exponent))

        order = sorted(range(len(self.blocks)), key=lambda idx: density[idx], reverse=True)
        kept: list[MemoryBlock] = []
        used = 0
        for idx in order:
            block = self.blocks[idx]
            if used + block.token_count <= self.cfg.l1_budget:
                block.tier = MemoryTier.L1
                kept.append(block)
                used += block.token_count
        self.last_step_debug = {
            "query": query,
            "block_ids": [block.block_id for block in self.blocks],
            "relevance": {block.block_id: relevance[idx] for idx, block in enumerate(self.blocks)},
            "propagated": {block.block_id: propagated[idx] for idx, block in enumerate(self.blocks)},
            "scores": {block.block_id: density[idx] for idx, block in enumerate(self.blocks)},
            "rank_order": [self.blocks[idx].block_id for idx in order],
            "selected_ids": [block.block_id for block in kept],
        }
        return kept
