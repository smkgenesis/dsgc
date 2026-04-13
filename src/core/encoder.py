from __future__ import annotations

import hashlib
import math
import re


TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


class FrozenEncoder:
    """Deterministic feature-hashing encoder for reproducible local experiments."""

    def __init__(self, embedding_dim: int = 256) -> None:
        self.dim = embedding_dim

    def _tokenize(self, text: str) -> list[str]:
        return TOKEN_RE.findall(text.lower())

    def encode(self, text: str) -> tuple[float, ...]:
        vec = [0.0] * self.dim
        for token in self._tokenize(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dim
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vec[bucket] += sign
        norm = math.sqrt(sum(v * v for v in vec))
        if norm == 0.0:
            return tuple(vec)
        return tuple(v / norm for v in vec)

    def encode_batch(self, texts: list[str]) -> list[tuple[float, ...]]:
        return [self.encode(text) for text in texts]


class SentenceEncoder:
    """Semantic encoder backed by sentence-transformers (optional dependency)."""

    _cache: dict[str, object] = {}

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is required for SentenceEncoder. "
                "Install it with: pip install sentence-transformers"
            ) from exc
        if model_name not in SentenceEncoder._cache:
            SentenceEncoder._cache[model_name] = SentenceTransformer(model_name)
        self._model = SentenceEncoder._cache[model_name]
        self.dim: int = self._model.get_sentence_embedding_dimension()

    def encode(self, text: str) -> tuple[float, ...]:
        vec = self._model.encode(text, normalize_embeddings=True)
        return tuple(float(v) for v in vec)

    def encode_batch(self, texts: list[str]) -> list[tuple[float, ...]]:
        vecs = self._model.encode(texts, normalize_embeddings=True)
        return [tuple(float(v) for v in vec) for vec in vecs]


def make_encoder(config) -> FrozenEncoder | SentenceEncoder:
    """Return the encoder specified by config.encoder_type."""
    if config.encoder_type == "sentence":
        return SentenceEncoder(config.sentence_model)
    return FrozenEncoder(config.embedding_dim)
