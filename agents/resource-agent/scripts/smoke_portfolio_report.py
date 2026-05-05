import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.config import AgentSettings
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.portfolio_report import PortfolioReportAgent
from learning_agent.schemas import PortfolioReportRequest
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    request = PortfolioReportRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentName="张同学",
        studentProfileSummary="Java 基础较弱，喜欢图解和项目案例，最近开始主动复盘错题。",
        courseTitle="Java Web 应用开发与软件工程实践",
        topic="Spring Boot Controller 与 REST API",
        timeRange="最近 7 天",
        completedResources=[
            "完成 HTTP 请求响应基础讲解文档，提交 6 行学习笔记。",
            "完成 MVC 分层职责思维导图，并标注 Controller/Service/Repository 边界。",
            "观看 REST API 短视频脚本并完成 2 道入口诊断题。",
        ],
        assessmentSummaries=["入口测评 58/100，错在 HTTP 状态码和 MVC 分层职责。", "复测 72/100，能说明 Service 下沉业务规则。"],
        tutoringSummaries=["追问 Controller 为什么不能直接访问 Repository，并记录了调用链。"],
        codePracticeSummaries=["完成 REST API 分层改造练习，静态批改 76分，仍需补异常响应。"],
        learningEvents=["错题复盘：把错误原因归类为职责边界不清。", "学习总结：下一步补 DTO 与异常响应。"],
        weaknesses=["HTTP 状态码", "MVC 分层职责", "异常响应"],
        improvements=["能画出 Controller -> Service -> Repository 调用链。"],
        documentTexts=["课程评价需要结合资源完成、测评结果、答疑互动、代码实操和复盘证据。"],
    )
    store.add_documents(loader.load_context_documents(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + request.completedResources + request.assessmentSummaries
        + request.tutoringSummaries + request.codePracticeSummaries + request.learningEvents,
        source="request.portfolio.documentTexts",
        title_prefix="smoke-portfolio-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    ))
    response = PortfolioReportAgent(settings, store).build(request)
    print(response.model_dump_json(indent=2))
    assert response.evidenceItems
    assert response.masteryRadar
    assert response.nextMilestones
    assert response.teacherCommentsDraft
    assert response.citations
    assert response.profileDimensionUpdates


if __name__ == "__main__":
    main()
