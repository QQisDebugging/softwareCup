import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.config import AgentSettings
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.resource_curation import ResourceCurationAgent
from learning_agent.schemas import ResourceCurationRequest
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    request = ResourceCurationRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary="Java 基础较弱，喜欢图解和项目案例，测评暴露 MVC 分层职责薄弱。",
        courseTitle="Java Web 应用开发与软件工程实践",
        topic="Spring Boot Controller 与 REST API",
        weaknesses=["HTTP 请求响应", "MVC 分层职责", "接口调试"],
        timeBudgetMinutes=120,
        candidateResources=[
            "Controller 负责请求响应，Service 负责业务规则，Repository 负责数据访问。",
            "REST API 实训应包含路由设计、DTO、异常响应和 Postman 调试。",
            "错题复盘卡需要记录错误原因、修正后的调用链和下一次检查点。",
        ],
        documentTexts=["个性化资源推送应覆盖讲解文档、图解、练习题、实操案例和复测。"],
    )
    store.add_documents(loader.load_context_documents(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + request.candidateResources,
        source="request.resource_curation.documentTexts",
        title_prefix="smoke-curation-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    ))
    response = ResourceCurationAgent(settings, store).curate(request)
    print(response.model_dump_json(indent=2))
    assert response.curatedResources
    assert len(response.curatedResources) >= 4
    assert response.coverageMap
    assert response.usagePlan
    assert response.citations
    assert response.profileDimensionUpdates


if __name__ == "__main__":
    main()
