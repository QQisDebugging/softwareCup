import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.config import AgentSettings
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.graph import ResourceGenerationWorkflow
from learning_agent.schemas import ResourceAgentRequest
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions))
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    workflow = ResourceGenerationWorkflow(settings=settings, vector_store=store)
    response = workflow.generate(
        ResourceAgentRequest(
            taskId="smoke-task",
            studentProfileId="profile-demo",
            courseId="course-demo",
            studentProfileSummary="大二软件工程学生，Java 基础较弱，喜欢图解、案例驱动和短视频脚本，每天可学习 45 分钟。",
            courseTitle="Java Web 应用开发与软件工程实践",
            topic="Spring Boot Controller 与 REST API",
            resourceType="微课讲义",
            modality="文本+图解脚本+练习题",
            prompt="面向 Java 基础较弱的大二学生，用项目案例讲解 Controller、DTO 和 Service 分层。",
        )
    )
    print(response.model_dump_json(indent=2))
    assert response.estimatedMinutes >= 1
    assert "资料来源" in response.content
    assert "多智能体" in response.content
    assert "```mermaid" in response.content


if __name__ == "__main__":
    main()
