import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.config import AgentSettings
from learning_agent.course_diagnosis import CourseDiagnosisAgent
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.schemas import CourseDiagnosisRequest
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    request = CourseDiagnosisRequest(
        courseId="course-demo",
        courseTitle="Java Web 应用开发与软件工程实践",
        courseDescription="覆盖 Spring Boot、REST API、数据库、学习画像和智能体服务调用。",
        syllabusText="第1周 HTTP 基础；第2周 REST API；第3周 学习画像；第4周 智能辅导。",
        targetStudentProfile="Java 基础较弱，喜欢图解和项目案例。",
        documentTexts=["课程已有讲解文档和练习题，但短视频脚本、实操案例、知识图谱还不完整。"],
    )
    store.add_documents(loader.load_context_documents(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + [request.syllabusText],
        source="request.course_diagnosis.documentTexts",
        title_prefix="smoke-diagnosis-inline",
        metadata={"courseId": request.courseId},
    ))
    response = CourseDiagnosisAgent(settings, store).diagnose(request)
    print(response.model_dump_json(indent=2))
    assert response.coverageScore > 0
    assert response.coveredKnowledgePoints
    assert response.assessmentBlueprint
    assert response.recommendedTasks
    assert response.citations


if __name__ == "__main__":
    main()
