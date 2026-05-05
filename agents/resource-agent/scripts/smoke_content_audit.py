import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.config import AgentSettings
from learning_agent.content_audit import ContentAuditAgent
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.schemas import ContentAuditRequest
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    request = ContentAuditRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        courseTitle="Java Web 应用开发与软件工程实践",
        topic="Spring Boot Controller 与 REST API",
        content=(
            "Controller 负责请求响应，Service 负责业务规则。"
            "这个方法保证学生 100% 掌握所有知识点，并且是全国第一的权威结论。"
        ),
        documentTexts=["Controller 负责请求响应，Service 负责业务规则，Repository 负责数据访问。"],
    )
    store.add_documents(loader.load_context_documents(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts,
        source="request.audit.documentTexts",
        title_prefix="smoke-audit-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    ))
    response = ContentAuditAgent(settings, store).audit(request)
    print(response.model_dump_json(indent=2))
    assert response.overallScore < 100
    assert response.citations
    assert response.riskyClaims
    assert response.recommendations
    assert "需要补充依据" in response.revisedContent or "风险修订提示" in response.revisedContent


if __name__ == "__main__":
    main()
