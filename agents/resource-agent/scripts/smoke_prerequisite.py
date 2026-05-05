import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.config import AgentSettings
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.prerequisite import PrerequisiteDiagnosisAgent
from learning_agent.schemas import PrerequisiteDiagnosisRequest
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    request = PrerequisiteDiagnosisRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary="Java 基础较弱，不熟 HTTP 请求响应，容易混淆 Controller、Service、Repository。",
        courseTitle="Java Web 应用开发与软件工程实践",
        targetTopic="Spring Boot Controller 与 REST API",
        completedTopics=["Java 面向对象基础"],
        assessmentWeaknesses=["HTTP 请求响应", "MVC 分层职责"],
        documentTexts=["学习 Spring Boot Controller 前，需要理解 HTTP、JSON、MVC 分层和接口调试。"],
    )
    store.add_documents(loader.load_context_documents(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts,
        source="request.prerequisite.documentTexts",
        title_prefix="smoke-prerequisite-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    ))
    response = PrerequisiteDiagnosisAgent(settings, store).diagnose(request)
    print(response.model_dump_json(indent=2))
    assert response.readinessScore < 85
    assert response.prerequisites
    assert response.diagnosticQuestions
    assert response.recommendedWarmups
    assert response.citations
    assert response.profileDimensionUpdates


if __name__ == "__main__":
    main()
