import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.config import AgentSettings
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.knowledge_graph import KnowledgeGraphAgent
from learning_agent.schemas import KnowledgeGraphRequest
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    request = KnowledgeGraphRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        courseTitle="Java Web 应用开发与软件工程实践",
        topic="Spring Boot Controller 与 REST API",
        weaknessSignals=["分层职责", "REST API 边界"],
        documentTexts=["Controller 负责请求响应，Service 负责业务规则，Repository 负责数据访问。"],
    )
    store.add_documents(loader.load_context_documents(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts,
        source="request.graph.documentTexts",
        title_prefix="smoke-graph-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    ))
    response = KnowledgeGraphAgent(settings, store).build(request)
    print(response.model_dump_json(indent=2))
    assert len(response.nodes) >= 6
    assert response.edges
    assert response.citations
    assert "flowchart" in response.mermaidDiagram
    assert response.weakPointHighlights


if __name__ == "__main__":
    main()
