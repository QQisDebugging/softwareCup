import hashlib
import math
import re
from collections.abc import Iterable


class HashingEmbeddingModel:
    """Deterministic local embeddings for offline RAG demos.

    The model uses hashed lexical features instead of external network calls, so the
    competition demo remains runnable without API keys. It can be replaced by a
    cloud embedding provider behind the same `embed` method later.
    """

    def __init__(self, dimensions: int = 384) -> None:
        if dimensions < 64:
            raise ValueError("Embedding dimensions must be >= 64.")
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in self._tokens(text):
            index = self._hash(token) % self.dimensions
            sign = 1.0 if self._hash("sign:" + token) % 2 == 0 else -1.0
            vector[index] += sign
        return self._normalize(vector)

    def embed_many(self, texts: Iterable[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]

    def cosine(self, left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0
        return sum(a * b for a, b in zip(left, right, strict=False))

    def _tokens(self, text: str) -> list[str]:
        lower = text.lower()
        words = re.findall(r"[a-z0-9_+#.-]+", lower)
        chinese = re.findall(r"[\u4e00-\u9fff]", lower)
        bigrams = ["".join(chinese[i : i + 2]) for i in range(max(0, len(chinese) - 1))]
        trigrams = ["".join(chinese[i : i + 3]) for i in range(max(0, len(chinese) - 2))]
        return words + bigrams + trigrams

    def _hash(self, token: str) -> int:
        return int(hashlib.blake2b(token.encode("utf-8"), digest_size=8).hexdigest(), 16)

    def _normalize(self, vector: list[float]) -> list[float]:
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]

