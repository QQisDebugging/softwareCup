import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.assessment_item_analysis import AssessmentItemAnalysisAgent
from learning_agent.config import AgentSettings
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.schemas import AssessmentAttemptRecord, AssessmentItemAnalysisRequest
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    request = AssessmentItemAnalysisRequest(
        courseId="course-demo",
        courseTitle="Java Web 应用开发与软件工程实践",
        topic="Spring Boot Controller 与 REST API",
        studentProfileId="profile-demo",
        attempts=[
            AssessmentAttemptRecord(
                questionId="q1",
                knowledgePoint="HTTP 请求响应",
                questionType="选择题",
                score=4,
                maxScore=10,
                correct=False,
                feedback="状态码和请求响应职责理解不稳。",
            ),
            AssessmentAttemptRecord(
                questionId="q2",
                knowledgePoint="Controller 分层职责",
                questionType="简答题",
                score=5,
                maxScore=15,
                correct=False,
                answerSummary="认为 Controller 可以直接访问 Repository。",
                feedback="Controller、Service、Repository 分层职责混淆。",
            ),
            AssessmentAttemptRecord(
                questionId="q3",
                knowledgePoint="REST API 设计",
                questionType="代码纠错题",
                score=13,
                maxScore=15,
                correct=True,
                feedback="能写出 Controller -> Service -> Repository 调用链。",
            ),
        ],
        documentTexts=["题目质量分析需要输出知识点掌握度、高错题、误区聚类和补救计划。"],
    )
    store.add_documents(loader.load_context_documents(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + [
            f"{attempt.knowledgePoint} {attempt.questionType} {attempt.score}/{attempt.maxScore} {attempt.feedback}"
            for attempt in request.attempts
        ],
        source="request.assessment_item_analysis.documentTexts",
        title_prefix="smoke-item-analysis-inline",
        metadata={"studentProfileId": request.studentProfileId or "", "courseId": request.courseId},
    ))
    response = AssessmentItemAnalysisAgent(settings, store).analyze(request)
    print(response.model_dump_json(indent=2))
    assert response.knowledgePointMastery
    assert response.hardItems
    assert response.misconceptionClusters
    assert response.remediationPlan
    assert response.citations


if __name__ == "__main__":
    main()
