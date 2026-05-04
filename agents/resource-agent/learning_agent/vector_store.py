from dataclasses import dataclass
from pathlib import Path
from threading import RLock

from learning_agent.documents import DocumentLoader, KnowledgeChunk, KnowledgeDocument
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.schemas import KnowledgeMatch


@dataclass
class IndexedChunk:
    chunk: KnowledgeChunk
    embedding: list[float]


class InMemoryVectorStore:
    def __init__(self, embedding_model: HashingEmbeddingModel, project_root: Path | None = None) -> None:
        self.embedding_model = embedding_model
        self._loader = DocumentLoader(project_root=project_root or Path.cwd())
        self._documents: dict[str, KnowledgeDocument] = {}
        self._chunks: list[IndexedChunk] = []
        self._lock = RLock()

    @property
    def document_count(self) -> int:
        with self._lock:
            return len(self._documents)

    @property
    def chunk_count(self) -> int:
        with self._lock:
            return len(self._chunks)

    def add_documents(self, documents: list[KnowledgeDocument]) -> int:
        valid_documents = [document for document in documents if document.text.strip()]
        if not valid_documents:
            return 0
        document_ids = {document.id for document in valid_documents}
        chunks = self._loader.split_documents(valid_documents)
        embeddings = self.embedding_model.embed_many(chunk.text for chunk in chunks)
        indexed_chunks = [
            IndexedChunk(chunk=chunk, embedding=embedding)
            for chunk, embedding in zip(chunks, embeddings, strict=True)
        ]
        with self._lock:
            for document in valid_documents:
                self._documents[document.id] = document
            self._chunks = [
                indexed
                for indexed in self._chunks
                if indexed.chunk.document_id not in document_ids
            ]
            self._chunks.extend(indexed_chunks)
        return len(indexed_chunks)

    def search(self, query: str, top_k: int = 6, filters: dict[str, str] | None = None) -> list[KnowledgeMatch]:
        query_embedding = self.embedding_model.embed(query)
        query_tokens = set(self.embedding_model.tokens(query))
        filters = filters or {}
        scored: list[tuple[float, KnowledgeChunk]] = []
        with self._lock:
            indexed_chunks = list(self._chunks)
        for indexed in indexed_chunks:
            if not self._matches_filters(indexed.chunk, filters):
                continue
            vector_score = self.embedding_model.cosine(query_embedding, indexed.embedding)
            lexical_score = self._lexical_score(query_tokens, indexed.chunk.text)
            request_boost = 0.04 if indexed.chunk.source == "request.documentTexts" else 0.0
            score = min(1.0, vector_score * 0.74 + lexical_score * 0.26 + request_boost)
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

    def _lexical_score(self, query_tokens: set[str], text: str) -> float:
        if not query_tokens:
            return 0.0
        text_tokens = set(self.embedding_model.tokens(text))
        if not text_tokens:
            return 0.0
        overlap = query_tokens & text_tokens
        return min(1.0, len(overlap) / max(3, len(query_tokens)))
