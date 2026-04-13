from __future__ import annotations

from config import DSGCConfig
from core.encoder import make_encoder
from policy import BaseMemoryPolicy
from memory_types import MemoryBlock, MemoryTier, Metadata


class SlidingWindowPolicy(BaseMemoryPolicy):
    def __init__(self, config: DSGCConfig) -> None:
        self.cfg = config
        self.encoder = make_encoder(config)
        self.current_turn = 0
        self.blocks: list[MemoryBlock] = []

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
                metadata=Metadata(turn_index=self.current_turn, pin=kwargs.get("pin", False)),
            )
        )
        self.current_turn += 1

    def step(self, query: str) -> list[MemoryBlock]:
        sorted_blocks = sorted(self.blocks, key=lambda block: block.metadata.turn_index, reverse=True)
        kept: list[MemoryBlock] = []
        used = 0
        for block in sorted_blocks:
            if used + block.token_count <= self.cfg.l1_budget:
                block.tier = MemoryTier.L1
                kept.append(block)
                used += block.token_count
        return kept
