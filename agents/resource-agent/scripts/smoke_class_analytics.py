import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.class_analytics import ClassAnalyticsAgent
from learning_agent.config import AgentSettings
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.schemas import ClassAnalyticsRequest, StudentLearningSnapshot
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    request = ClassAnalyticsRequest(
        courseId="course-demo",
        courseTitle="Java Web 应用开发与软件工程实践",
        topic="Spring Boot Controller 与 REST API",
        snapshots=[
            StudentLearningSnapshot(
                studentProfileId="s1",
                studentName="张同学",
                profileSummary="Java 基础较弱，喜欢图解。",
                recentScores=[48, 55],
                completedResources=1,
                tutoringCount=0,
                codePracticeCount=0,
                weaknessSignals=["HTTP 请求响应", "MVC 分层职责"],
                learningEvents=["只完成入口讲解。"],
            ),
            StudentLearningSnapshot(
                studentProfileId="s2",
                studentName="李同学",
                profileSummary="能理解概念，实操不足。",
                recentScores=[62, 70],
                completedResources=3,
                tutoringCount=1,
                codePracticeCount=0,
                weaknessSignals=["MVC 分层职责", "REST API 边界"],
                learningEvents=["错题复盘：Controller 直接访问 Repository。"],
            ),
            StudentLearningSnapshot(
                studentProfileId="s3",
                studentName="王同学",
                profileSummary="项目能力较好。",
                recentScores=[82, 88],
                completedResources=4,
                tutoringCount=2,
                codePracticeCount=2,
                weaknessSignals=["异常响应"],
                learningEvents=["完成代码实操和复盘。"],
            ),
        ],
        documentTexts=["教师端需要按照班级学情识别共性薄弱点、干预分组和资源缺口。"],
    )
    store.add_documents(loader.load_context_documents(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + [
            f"{snapshot.studentName} {snapshot.profileSummary} {' '.join(snapshot.weaknessSignals)}"
            for snapshot in request.snapshots
        ],
        source="request.class_analytics.documentTexts",
        title_prefix="smoke-class-analytics-inline",
        metadata={"courseId": request.courseId},
    ))
    response = ClassAnalyticsAgent(settings, store).analyze(request)
    print(response.model_dump_json(indent=2))
    assert response.classMasteryAverage > 0
    assert response.engagementAverage > 0
    assert response.topWeaknesses
    assert response.interventionGroups
    assert response.resourceGaps
    assert response.teacherActions
    assert response.citations


if __name__ == "__main__":
    main()
