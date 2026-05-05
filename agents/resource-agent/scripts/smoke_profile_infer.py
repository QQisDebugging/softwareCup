import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.config import AgentSettings
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.profile_infer import ProfileInferenceAgent
from learning_agent.schemas import ProfileInferRequest
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    request = ProfileInferRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        courseTitle="Java Web 应用开发与软件工程实践",
        declaredMajor="软件工程",
        currentLevel="大二，Java 基础较弱",
        learningGoal="两周内掌握 Spring Boot REST API 分层开发",
        preferences="喜欢图解、项目案例和短视频脚本",
        constraintsText="每天可学习 45 分钟",
        dialogueTurns=[
            "系统：你希望提升哪门课？学生：Java Web 和 Spring Boot。",
            "系统：最近最容易错什么？学生：Controller、Service、Repository 分层总混。",
            "学生：我喜欢先看图解，再做一个能跑的小项目。",
        ],
        learningRecords=["错题复盘：Controller 直接访问 Repository。"],
        assessmentSummaries=["入口测评 58/100，薄弱点是 HTTP 请求响应和 MVC 分层。"],
        documentTexts=["画像应包含知识基础、认知风格、学习目标、兴趣方向、易错点、时间约束、资源偏好和掌握度。"],
    )
    store.add_documents(loader.load_context_documents(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + request.dialogueTurns + request.learningRecords + request.assessmentSummaries,
        source="request.profile_infer.documentTexts",
        title_prefix="smoke-profile-inline",
        metadata={"studentProfileId": request.studentProfileId or "", "courseId": request.courseId or ""},
    ))
    response = ProfileInferenceAgent(settings, store).infer(request)
    print(response.model_dump_json(indent=2))
    assert len(response.dimensions) >= 8
    assert response.extractedSignals
    assert response.followUpQuestions
    assert response.citations


if __name__ == "__main__":
    main()
