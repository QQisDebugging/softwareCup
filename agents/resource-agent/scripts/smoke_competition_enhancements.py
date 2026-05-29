import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.competition_enhancements import (
    AgentRunStore,
    CourseCoverageAgent,
    DefensePackAgent,
    ErrorBookAgent,
    GraphRagQueryAgent,
    HumanReviewAgent,
    OcrQuestionAgent,
    RagEvaluationAgent,
    VoicePackageAgent,
)
from learning_agent.config import AgentSettings
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.schemas import (
    AgentRunRecordRequest,
    AgentRunStepRecord,
    AssessmentAttemptRecord,
    CourseAssessmentInventoryItem,
    CourseCoverageRequest,
    CourseResourceInventoryItem,
    DefensePackRequest,
    ErrorBookRequest,
    GraphRagQueryRequest,
    HumanReviewRequest,
    OcrQuestionRequest,
    RagEvaluationRequest,
    VoicePackageRequest,
)
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    context = [
        "RAG 需要检索课程资料并在回答中展示引用证据，避免无依据生成。",
        "Spring Boot REST API 课程要求 Controller、Service、Repository 分层清晰。",
        "教师端需要查看课程覆盖率、班级风险和资源缺口。",
    ]
    store.add_documents(loader.load_context_documents(
        paths=[],
        texts=context,
        source="smoke.competition_enhancements",
        title_prefix="smoke-enhancement",
        metadata={"courseId": "course-demo"},
    ))

    rag_eval = RagEvaluationAgent(settings, store).evaluate(RagEvaluationRequest(
        courseId="course-demo",
        courseTitle="Java Web 应用开发",
        question="为什么 RAG 资源生成需要展示引用？",
        answer="RAG 资源生成需要展示引用，因为这样可以让教师和学生核对依据，降低幻觉风险。",
        expectedAnswer="回答应说明引用证据、防幻觉和教师审核。",
        contexts=context,
    ))
    assert rag_eval.overallScore > 30
    assert rag_eval.metricBreakdown

    run = AgentRunStore(settings).record(AgentRunRecordRequest(
        taskName="RAG 质量评测演示",
        endpoint="/agents/evaluation/rag-quality",
        provider="offline",
        requestPayload={"question": "为什么需要引用？"},
        responsePayload={"overallScore": rag_eval.overallScore},
        steps=[
            AgentRunStepRecord(order=1, agentName="rag_evaluation_agent", inputSummary="question+answer", outputSummary=rag_eval.summary)
        ],
    ))
    assert run.runId
    assert AgentRunStore(settings).get(run.runId) is not None

    human = HumanReviewAgent(settings, store).review(HumanReviewRequest(
        courseId="course-demo",
        courseTitle="Java Web 应用开发",
        resourceTitle="REST API 分层讲解",
        content="REST API 分层讲解需要结合 Controller、Service、Repository 职责边界，并展示引用证据。",
        rubric=["必须有引用证据", "必须说明分层职责"],
    ))
    assert human.publishChecklist
    assert human.decision.riskLevel

    voice = VoicePackageAgent(settings, store).build(VoicePackageRequest(
        courseId="course-demo",
        courseTitle="Java Web 应用开发",
        topic="REST API 分层",
        script="第一步介绍 Controller 只负责请求响应。第二步说明 Service 承载业务规则。第三步说明 Repository 负责数据访问。",
        targetDurationMinutes=3,
    ))
    assert voice.segments
    assert voice.subtitleSrt

    ocr = OcrQuestionAgent(settings, store).extract(OcrQuestionRequest(
        courseId="course-demo",
        courseTitle="Java Web 应用开发",
        imageName="rest-api-question.png",
        ocrText="1. Spring Boot 中 Controller 的主要职责是什么？A. 数据访问 B. 请求响应 C. 物理存储 D. 编译代码",
    ))
    assert ocr.questions
    assert ocr.nextAgentCalls

    graph = GraphRagQueryAgent(settings, store).query(GraphRagQueryRequest(
        courseId="course-demo",
        courseTitle="Java Web 应用开发",
        query="Controller 直接访问 Repository 为什么不好？",
        weaknessSignals=["MVC 分层职责"],
    ))
    assert graph.expandedConcepts
    assert graph.retrievalPath

    attempts = [
        AssessmentAttemptRecord(questionId="q1", knowledgePoint="MVC 分层职责", questionType="选择题", score=3, maxScore=10, correct=False, answerSummary="混淆 Controller 和 Repository", feedback="分层职责错误"),
        AssessmentAttemptRecord(questionId="q2", knowledgePoint="REST API 边界", questionType="简答题", score=6, maxScore=10, correct=False, answerSummary="接口边界描述不完整", feedback="缺少状态码"),
        AssessmentAttemptRecord(questionId="q3", knowledgePoint="MVC 分层职责", questionType="代码题", score=8, maxScore=10, correct=True, answerSummary="基本正确", feedback="仍需补异常处理"),
    ]
    error_book = ErrorBookAgent(settings, store).analyze(ErrorBookRequest(
        studentProfileId="stu-demo",
        courseId="course-demo",
        courseTitle="Java Web 应用开发",
        attempts=attempts,
        recentWeaknesses=["MVC 分层职责"],
    ))
    assert error_book.errorClusters
    assert error_book.reviewSchedule

    coverage = CourseCoverageAgent(settings, store).analyze(CourseCoverageRequest(
        courseId="course-demo",
        courseTitle="Java Web 应用开发",
        chapters=["MVC 分层职责", "REST API 边界", "异常响应"],
        resourceInventory=[
            CourseResourceInventoryItem(title="MVC 图解", resourceType="思维导图", knowledgePoints=["MVC 分层职责"]),
            CourseResourceInventoryItem(title="REST API 案例", resourceType="实操案例", knowledgePoints=["REST API 边界"]),
        ],
        assessmentInventory=[
            CourseAssessmentInventoryItem(title="MVC 选择题", questionType="选择题", knowledgePoints=["MVC 分层职责"]),
        ],
    ))
    assert coverage.coverageRadar
    assert coverage.gaps

    defense = DefensePackAgent(settings, store).build(DefensePackRequest(
        projectName="个性化学习多智能体系统",
        implementedFeatures=["对话式画像", "RAG 资源生成", "防幻觉评测", "错题本", "班级分析"],
        techStack=["FastAPI", "LangGraph", "LangChain", "RAG", "Embedding"],
        riskConcerns=["讯飞 API 不可用", "评委追问防幻觉"],
        apiStatus={"activeProvider": "offline", "fallbackProvider": "offline"},
    ))
    assert defense.qaPairs
    assert defense.featureMatrix
    assert defense.apiChecklist

    print({
        "ragScore": rag_eval.overallScore,
        "runId": run.runId,
        "reviewRisk": human.decision.riskLevel,
        "voiceSegments": len(voice.segments),
        "ocrQuestions": len(ocr.questions),
        "graphConcepts": len(graph.expandedConcepts),
        "errorClusters": len(error_book.errorClusters),
        "coverageGaps": len(coverage.gaps),
        "defenseQA": len(defense.qaPairs),
    })


if __name__ == "__main__":
    main()
