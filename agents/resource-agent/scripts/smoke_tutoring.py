import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.config import AgentSettings
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.schemas import TutoringRequest
from learning_agent.tutoring import TutoringAgent
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    request = TutoringRequest(
        sessionId="smoke-tutoring",
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary="Java 基础较弱，容易混淆 Controller、DTO、Service，喜欢图解。",
        courseTitle="Java Web 应用开发与软件工程实践",
        question="Controller 能不能直接调用 Repository？为什么？",
        conversationHistory=["学生：我写接口时总想直接查数据库。", "系统：先区分 Controller 和 Service 的职责。"],
        documentTexts=["Controller 只处理 HTTP 入参、DTO 校验和响应封装；业务规则和事务应放在 Service。"],
    )
    store.add_documents(loader.load_context_documents(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts,
        source="request.tutoring.documentTexts",
        title_prefix="smoke-tutoring-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    ))
    response = TutoringAgent(settings, store).answer(request)
    print(response.model_dump_json(indent=2))
    assert "智能辅导答复" in response.answer
    assert response.citations
    assert response.followUpQuestions
    assert "```mermaid" in response.mermaidDiagram
    assert "MASTERY_WEAKNESS" in response.profileSignals


if __name__ == "__main__":
    main()

