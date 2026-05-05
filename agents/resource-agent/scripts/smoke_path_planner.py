import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.config import AgentSettings
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.path_planner import PathPlannerAgent
from learning_agent.schemas import LearningPathPlanRequest
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    request = LearningPathPlanRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary="Java 基础较弱，容易混淆 Controller、Service、Repository，喜欢图解和项目案例。",
        courseTitle="Java Web 应用开发与软件工程实践",
        topic="Spring Boot Controller 与 REST API",
        goal="一周内能完成一个 REST API 分层小案例",
        timeframeDays=7,
        dailyMinutes=45,
        weaknessSignals=["分层职责", "Controller 直接访问 Repository", "REST API 边界"],
        recentScores=[42, 58],
        documentTexts=["Controller 负责请求响应，Service 负责业务规则，Repository 负责数据访问。"],
    )
    store.add_documents(loader.load_context_documents(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts,
        source="request.path.documentTexts",
        title_prefix="smoke-path-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    ))
    response = PathPlannerAgent(settings, store).plan(request)
    print(response.model_dump_json(indent=2))
    assert response.stages
    assert len(response.stages) >= 3
    assert response.resourceRecommendations
    assert response.reviewCheckpoints
    assert response.citations
    assert "mermaid" in response.mermaidRoadmap
    assert response.profileDimensionUpdates


if __name__ == "__main__":
    main()
