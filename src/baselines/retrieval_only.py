from __future__ import annotations

from config import DSGCConfig
from core.encoder import make_encoder
from core.math_utils import dot
from policy import BaseMemoryPolicy
from memory_types import MemoryBlock, MemoryTier, Metadata


class RetrievalOnlyPolicy(BaseMemoryPolicy):
    def __init__(self, config: DSGCConfig) -> None:
        self.cfg = config
        self.encoder = make_encoder(config)
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

    def step(self, query: str) -> list[MemoryBlock]:
        if not self.blocks:
            self.last_step_debug = {}
            return []
        goal_embedding = self.encoder.encode(query)
        scores = {block.block_id: dot(block.embedding, goal_embedding) for block in self.blocks}
        order = sorted(self.blocks, key=lambda block: scores[block.block_id], reverse=True)
        kept: list[MemoryBlock] = []
        used = 0
        for block in order:
            if used + block.token_count <= self.cfg.l1_budget:
                block.tier = MemoryTier.L1
                kept.append(block)
                used += block.token_count
        self.last_step_debug = {
            "query": query,
            "block_ids": [block.block_id for block in self.blocks],
            "relevance": {block.block_id: scores[block.block_id] for block in self.blocks},
            "propagated": {block.block_id: 0.0 for block in self.blocks},
            "scores": {block.block_id: scores[block.block_id] for block in self.blocks},
            "rank_order": [block.block_id for block in order],
            "selected_ids": [block.block_id for block in kept],
        }
        return kept
