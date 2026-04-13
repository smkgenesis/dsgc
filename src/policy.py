from __future__ import annotations

from abc import ABC, abstractmethod

from memory_types import MemoryBlock


class BaseMemoryPolicy(ABC):
    @abstractmethod
    def ingest(self, text: str, block_id: str, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def step(self, query: str) -> list[MemoryBlock]:
        raise NotImplementedError
