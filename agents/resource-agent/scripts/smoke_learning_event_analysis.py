import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.config import AgentSettings
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.learning_event_analysis import LearningEventAnalysisAgent
from learning_agent.schemas import LearningEventAnalysisRequest
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    request = LearningEventAnalysisRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary="Java 基础较弱，喜欢图解和项目案例。",
        courseTitle="Java Web 应用开发与软件工程实践",
        targetTopic="Spring Boot Controller 与 REST API",
        timeRange="最近 7 天",
        learningEvents=["完成 2 个资源卡。", "错题复盘：同一错误是 Controller 直接访问 Repository。"],
        resourceUsage=["学习 HTTP 请求响应讲解文档。", "完成 MVC 分层职责思维导图。"],
        assessmentSummaries=["入口测评 58/100。", "复测 72/100。"],
        tutoringSummaries=["追问 Controller 为什么不能直接写业务逻辑。"],
        codePracticeSummaries=[],
        documentTexts=["学习事件分析需要识别参与度、掌握趋势、风险信号和下一步 Agent 调用。"],
    )
    store.add_documents(loader.load_context_documents(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + request.learningEvents + request.resourceUsage
        + request.assessmentSummaries + request.tutoringSummaries + request.codePracticeSummaries,
        source="request.learning_event_analysis.documentTexts",
        title_prefix="smoke-events-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    ))
    response = LearningEventAnalysisAgent(settings, store).analyze(request)
    print(response.model_dump_json(indent=2))
    assert response.engagementScore > 0
    assert response.masteryTrend in {"明显提升", "小幅提升", "基本稳定", "下降", "当前较稳", "需要补救", "证据不足"}
    assert response.riskSignals
    assert response.recommendedAgentCalls
    assert response.profileDimensionUpdates
    assert response.citations


if __name__ == "__main__":
    main()
