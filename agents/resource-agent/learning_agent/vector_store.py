from dataclasses import dataclass
from pathlib import Path

from learning_agent.documents import DocumentLoader, KnowledgeChunk, KnowledgeDocument
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.schemas import KnowledgeMatch


@dataclass
class IndexedChunk:
    chunk: KnowledgeChunk
    embedding: list[float]


class InMemoryVectorStore:
    def __init__(self, embedding_model: HashingEmbeddingModel) -> None:
        self.embedding_model = embedding_model
        self._loader = DocumentLoader(project_root=Path.cwd())
        self._documents: dict[str, KnowledgeDocument] = {}
        self._chunks: list[IndexedChunk] = []

    @property
    def document_count(self) -> int:
        return len(self._documents)

    @property
    def chunk_count(self) -> int:
        return len(self._chunks)

    def add_documents(self, documents: list[KnowledgeDocument]) -> int:
        if not documents:
            return 0
        for document in documents:
            if document.text.strip():
                self._documents[document.id] = document
        chunks = self._loader.split_documents([document for document in documents if document.text.strip()])
        embeddings = self.embedding_model.embed_many(chunk.text for chunk in chunks)
        for chunk, embedding in zip(chunks, embeddings, strict=True):
            self._chunks.append(IndexedChunk(chunk=chunk, embedding=embedding))
        return len(chunks)

    def search(self, query: str, top_k: int = 6, filters: dict[str, str] | None = None) -> list[KnowledgeMatch]:
        query_embedding = self.embedding_model.embed(query)
        filters = filters or {}
        scored: list[tuple[float, KnowledgeChunk]] = []
        for indexed in self._chunks:
            if not self._matches_filters(indexed.chunk, filters):
                continue
            score = self.embedding_model.cosine(query_embedding, indexed.embedding)
            scored.append((score, indexed.chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            KnowledgeMatch(
                id=chunk.id,
                score=round(float(score), 4),
                text=chunk.text,
                source=chunk.source,
                title=chunk.title,
                metadata=chunk.metadata,
            )
            for score, chunk in scored[:top_k]
        ]

    def _matches_filters(self, chunk: KnowledgeChunk, filters: dict[str, str]) -> bool:
        for key, expected in filters.items():
            actual = str(chunk.metadata.get(key, ""))
            if actual != expected:
                return False
        return True
