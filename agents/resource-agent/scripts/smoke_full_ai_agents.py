import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.agent_trace import AgentTraceAgent
from learning_agent.assessment import AssessmentAgent
from learning_agent.assessment_item_analysis import AssessmentItemAnalysisAgent
from learning_agent.class_analytics import ClassAnalyticsAgent
from learning_agent.code_practice import CodePracticeAgent
from learning_agent.config import AgentSettings
from learning_agent.content_audit import ContentAuditAgent
from learning_agent.course_diagnosis import CourseDiagnosisAgent
from learning_agent.demo_planner import DemoScenarioPlannerAgent
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.graph import ResourceGenerationWorkflow
from learning_agent.knowledge_graph import KnowledgeGraphAgent
from learning_agent.learning_event_analysis import LearningEventAnalysisAgent
from learning_agent.path_planner import PathPlannerAgent
from learning_agent.portfolio_report import PortfolioReportAgent
from learning_agent.prerequisite import PrerequisiteDiagnosisAgent
from learning_agent.profile_infer import ProfileInferenceAgent
from learning_agent.project_review import ProjectReviewAgent
from learning_agent.resource_curation import ResourceCurationAgent
from learning_agent.schemas import (
    AgentTraceRequest,
    AssessmentAnswer,
    AssessmentGenerateRequest,
    AssessmentGradeRequest,
    AssessmentAttemptRecord,
    AssessmentItemAnalysisRequest,
    ClassAnalyticsRequest,
    CodePracticeGenerateRequest,
    CodePracticeGradeRequest,
    ContentAuditRequest,
    CourseDiagnosisRequest,
    DemoScenarioRequest,
    KnowledgeGraphRequest,
    LearningEventAnalysisRequest,
    LearningPathPlanRequest,
    PortfolioReportRequest,
    ProfileInferRequest,
    PrerequisiteDiagnosisRequest,
    ProjectFileInput,
    ProjectReviewRequest,
    ResourceAgentRequest,
    ResourceCurationRequest,
    StoryboardRequest,
    StudentLearningSnapshot,
    TutoringRequest,
)
from learning_agent.storyboard import StoryboardAgent
from learning_agent.tutoring import TutoringAgent
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    inline_doc = "Controller 负责请求响应，Service 负责业务规则，Repository 负责数据访问。"
    store.add_documents(loader.load_context_documents(
        paths=[],
        texts=[inline_doc],
        source="smoke.full.documentTexts",
        title_prefix="smoke-full-inline",
        metadata={"courseId": "course-demo", "studentProfileId": "profile-demo"},
    ))

    profile = "Java 基础较弱，容易混淆 Controller、Service、Repository，喜欢图解和项目案例。"
    course = "Java Web 应用开发与软件工程实践"
    topic = "Spring Boot Controller 与 REST API"

    resource = ResourceGenerationWorkflow(settings, store).generate(ResourceAgentRequest(
        taskId="task-full",
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary=profile,
        courseTitle=course,
        topic=topic,
        resourceType="微课讲义",
        modality="文本+图解脚本",
        prompt="用项目案例讲解 Controller、Service、Repository 分层。",
        documentTexts=[inline_doc],
    ))
    tutoring = TutoringAgent(settings, store).answer(TutoringRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary=profile,
        courseTitle=course,
        question="Controller 为什么不应该直接写复杂业务逻辑？",
        documentTexts=[inline_doc],
    ))
    assessment_agent = AssessmentAgent(settings, store)
    assessment = assessment_agent.generate(AssessmentGenerateRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary=profile,
        courseTitle=course,
        topic=topic,
        count=4,
        documentTexts=[inline_doc],
    ))
    grade = assessment_agent.grade(AssessmentGradeRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary=profile,
        courseTitle=course,
        topic=topic,
        questions=assessment.questions,
        answers=[
            AssessmentAnswer(questionId=assessment.questions[0].id, answer=assessment.questions[0].answer),
            AssessmentAnswer(questionId=assessment.questions[1].id, answer="错误"),
        ],
    ))
    path = PathPlannerAgent(settings, store).plan(LearningPathPlanRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary=profile,
        courseTitle=course,
        topic=topic,
        weaknessSignals=["分层职责", "REST API 边界"],
        documentTexts=[inline_doc],
    ))
    graph = KnowledgeGraphAgent(settings, store).build(KnowledgeGraphRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        courseTitle=course,
        topic=topic,
        weaknessSignals=["分层职责", "REST API 边界"],
        documentTexts=[inline_doc],
    ))
    audit = ContentAuditAgent(settings, store).audit(ContentAuditRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        courseTitle=course,
        topic=topic,
        content=resource.content + "\n这个方法保证学生 100% 掌握所有知识点。",
        documentTexts=[inline_doc],
    ))
    diagnosis = CourseDiagnosisAgent(settings, store).diagnose(CourseDiagnosisRequest(
        courseId="course-demo",
        courseTitle=course,
        courseDescription="覆盖 Spring Boot、REST API、数据库、学习画像和智能体服务调用。",
        syllabusText="第1周 HTTP 基础；第2周 REST API；第3周 学习画像；第4周 智能辅导。",
        targetStudentProfile=profile,
        documentTexts=[inline_doc],
    ))
    code_agent = CodePracticeAgent(settings, store)
    code = code_agent.generate(CodePracticeGenerateRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary=profile,
        courseTitle=course,
        topic=topic,
        documentTexts=[inline_doc],
    ))
    code_grade = code_agent.grade(CodePracticeGradeRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary=profile,
        courseTitle=course,
        topic=topic,
        exercise=code.exercise,
        submissionCode=code.exercise.starterCode,
    ))
    storyboard = StoryboardAgent(settings, store).create(StoryboardRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary=profile,
        courseTitle=course,
        topic=topic,
        documentTexts=[inline_doc],
    ))
    prerequisite = PrerequisiteDiagnosisAgent(settings, store).diagnose(PrerequisiteDiagnosisRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary=profile,
        courseTitle=course,
        targetTopic=topic,
        completedTopics=["Java 面向对象基础"],
        assessmentWeaknesses=grade.weaknessSignals,
        documentTexts=[inline_doc],
    ))
    curation = ResourceCurationAgent(settings, store).curate(ResourceCurationRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary=profile,
        courseTitle=course,
        topic=topic,
        weaknesses=grade.weaknessSignals + ["REST API 边界"],
        candidateResources=[
            resource.summary,
            path.summary,
            storyboard.summary,
        ],
        documentTexts=[inline_doc],
    ))
    portfolio = PortfolioReportAgent(settings, store).build(PortfolioReportRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentName="演示学生",
        studentProfileSummary=profile,
        courseTitle=course,
        topic=topic,
        completedResources=[resource.summary, path.summary, storyboard.summary],
        assessmentSummaries=[grade.feedback],
        tutoringSummaries=[tutoring.answer[:160]],
        codePracticeSummaries=[code_grade.feedback],
        learningEvents=["错题复盘：Controller 直接承载业务逻辑导致职责边界不清。"],
        weaknesses=grade.weaknessSignals,
        improvements=["能说出 Controller -> Service -> Repository 调用链。"],
        documentTexts=[inline_doc],
    ))
    trace = AgentTraceAgent(settings).explain(AgentTraceRequest(
        taskName="全链路智能学习闭环",
        userIntent="演示资源生成、答疑、测评、路径、图谱、审计、代码实操、多模态、先修诊断、资源策展和档案报告。",
        studentProfileId="profile-demo",
        courseId="course-demo",
        involvedAgents=[
            "profile_agent",
            "rag_retrieval_agent",
            "resource_generator_agent",
            "assessment_agent",
            "portfolio_report_agent",
            "content_audit_agent",
        ],
        responseSummary=portfolio.summary,
        citations=graph.citations[:3],
        fallbackEvents=["offline provider 可保证无密钥演示链路不中断。"],
    ))
    inferred_profile = ProfileInferenceAgent(settings, store).infer(ProfileInferRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        courseTitle=course,
        declaredMajor="软件工程",
        currentLevel="Java 基础较弱",
        learningGoal=f"掌握 {topic}",
        preferences="喜欢图解和项目案例",
        constraintsText="每天 45 分钟",
        dialogueTurns=[
            "学生：我想学 Spring Boot，但是 Controller、Service、Repository 分不清。",
            "学生：我喜欢先看图，再做一个能跑的小项目。",
        ],
        learningRecords=["错题复盘：Controller 直接访问 Repository。"],
        assessmentSummaries=[grade.feedback],
        documentTexts=[inline_doc],
    ))
    event_analysis = LearningEventAnalysisAgent(settings, store).analyze(LearningEventAnalysisRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary=profile,
        courseTitle=course,
        targetTopic=topic,
        learningEvents=["完成资源生成和错题复盘。", "同一错误：Controller 直接访问 Repository。"],
        resourceUsage=[resource.summary, curation.summary],
        assessmentSummaries=[grade.feedback],
        tutoringSummaries=[tutoring.answer[:140]],
        codePracticeSummaries=[code_grade.feedback],
        documentTexts=[inline_doc],
    ))
    item_analysis = AssessmentItemAnalysisAgent(settings, store).analyze(AssessmentItemAnalysisRequest(
        courseId="course-demo",
        courseTitle=course,
        topic=topic,
        studentProfileId="profile-demo",
        attempts=[
            AssessmentAttemptRecord(
                questionId=result.questionId,
                knowledgePoint=result.knowledgePoint,
                questionType="自动测评题",
                score=result.score,
                maxScore=result.maxScore,
                correct=result.correct,
                feedback=result.feedback,
            )
            for result in grade.questionResults
        ],
        documentTexts=[inline_doc],
    ))
    project_review = ProjectReviewAgent(settings, store).review(ProjectReviewRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary=profile,
        courseTitle=course,
        projectTitle="REST API 分层练习",
        targetTopic=topic,
        files=[
            ProjectFileInput(
                path="src/main/java/demo/UserController.java",
                content="@RestController class UserController { UserRepository repo; @PostMapping(\"/u\") User save(@RequestBody User u){ return repo.save(u); } }",
            )
        ],
        documentTexts=[inline_doc],
    ))
    class_analytics = ClassAnalyticsAgent(settings, store).analyze(ClassAnalyticsRequest(
        courseId="course-demo",
        courseTitle=course,
        topic=topic,
        snapshots=[
            StudentLearningSnapshot(
                studentProfileId="profile-demo",
                studentName="演示学生",
                profileSummary=profile,
                recentScores=[grade.score],
                completedResources=3,
                tutoringCount=1,
                codePracticeCount=0,
                weaknessSignals=grade.weaknessSignals + ["REST API 边界"],
                learningEvents=["错题复盘：Controller 直接访问 Repository。"],
            ),
            StudentLearningSnapshot(
                studentProfileId="profile-peer",
                studentName="同伴学生",
                profileSummary="能理解概念但实操不足。",
                recentScores=[68, 72],
                completedResources=2,
                tutoringCount=1,
                codePracticeCount=0,
                weaknessSignals=["REST API 边界", "MVC 分层职责"],
                learningEvents=["完成资源学习。"],
            ),
        ],
        documentTexts=[inline_doc],
    ))
    demo_plan = DemoScenarioPlannerAgent(settings, store).plan(DemoScenarioRequest(
        scenarioTitle="软件杯 A3 个性化学习多智能体演示",
        audience="评委",
        courseTitle=course,
        studentProfileSummary=profile,
        timeLimitMinutes=7,
        coreEndpoints=[
            "/agents/profile/infer",
            "/agents/prerequisite/diagnose",
            "/agents/resources/curate",
            "/agents/resource-generation",
            "/agents/assessment/grade",
            "/agents/report/portfolio",
            "/agents/trace/explain",
        ],
        availableArtifacts=["smoke_full_ai_agents.py 输出", "Java/Vue3 对接文档"],
        riskConcerns=["网络不稳定时使用 offline provider"],
        documentTexts=[inline_doc],
    ))

    summary = {
        "resourceMinutes": resource.estimatedMinutes,
        "tutoringCitations": len(tutoring.citations),
        "assessmentQuestions": len(assessment.questions),
        "assessmentScore": grade.score,
        "pathStages": len(path.stages),
        "graphNodes": len(graph.nodes),
        "auditScore": audit.overallScore,
        "diagnosisTasks": len(diagnosis.recommendedTasks),
        "codeDefects": len(code_grade.defects),
        "storyboardScenes": len(storyboard.videoStoryboard),
        "prerequisiteReadiness": prerequisite.readinessScore,
        "curatedResources": len(curation.curatedResources),
        "portfolioEvidence": len(portfolio.evidenceItems),
        "traceSteps": len(trace.traceSteps),
        "profileDimensions": len(inferred_profile.dimensions),
        "eventRisks": len(event_analysis.riskSignals),
        "itemMasteryPoints": len(item_analysis.knowledgePointMastery),
        "projectIssues": len(project_review.architectureIssues),
        "classGroups": len(class_analytics.interventionGroups),
        "demoScenes": len(demo_plan.scenes),
    }
    print(summary)
    assert resource.content
    assert tutoring.citations
    assert len(assessment.questions) == 4
    assert grade.profileDimensionUpdates
    assert len(path.stages) >= 3
    assert len(graph.nodes) >= 6
    assert audit.riskyClaims
    assert diagnosis.recommendedTasks
    assert code_grade.defects
    assert len(storyboard.videoStoryboard) >= 4
    assert prerequisite.prerequisites
    assert len(curation.curatedResources) >= 4
    assert portfolio.masteryRadar
    assert len(trace.traceSteps) >= 5
    assert len(inferred_profile.dimensions) >= 8
    assert event_analysis.recommendedAgentCalls
    assert item_analysis.remediationPlan
    assert project_review.refactorTasks
    assert project_review.qualityGates
    assert project_review.fileMetrics
    assert class_analytics.teacherActions
    assert class_analytics.studentRiskProfiles
    assert class_analytics.interventionPriority
    assert len(demo_plan.scenes) >= 6
    assert demo_plan.totalEstimatedMinutes * 60 >= demo_plan.scenes[-1].endSecond
    assert demo_plan.timelineMarkdown
    assert demo_plan.riskPlaybook


if __name__ == "__main__":
    main()
