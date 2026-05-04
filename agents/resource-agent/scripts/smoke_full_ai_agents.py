import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.assessment import AssessmentAgent
from learning_agent.code_practice import CodePracticeAgent
from learning_agent.config import AgentSettings
from learning_agent.content_audit import ContentAuditAgent
from learning_agent.course_diagnosis import CourseDiagnosisAgent
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.graph import ResourceGenerationWorkflow
from learning_agent.knowledge_graph import KnowledgeGraphAgent
from learning_agent.path_planner import PathPlannerAgent
from learning_agent.schemas import (
    AssessmentAnswer,
    AssessmentGenerateRequest,
    AssessmentGradeRequest,
    CodePracticeGenerateRequest,
    CodePracticeGradeRequest,
    ContentAuditRequest,
    CourseDiagnosisRequest,
    KnowledgeGraphRequest,
    LearningPathPlanRequest,
    ResourceAgentRequest,
    StoryboardRequest,
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


if __name__ == "__main__":
    main()
