import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.code_practice import CodePracticeAgent
from learning_agent.config import AgentSettings
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.schemas import CodePracticeGenerateRequest, CodePracticeGradeRequest
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    agent = CodePracticeAgent(settings, store)
    request = CodePracticeGenerateRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary="Java 基础较弱，容易混淆 Controller 和 Service。",
        courseTitle="Java Web 应用开发与软件工程实践",
        topic="Spring Boot Controller 与 REST API",
        documentTexts=["Controller 负责请求响应，Service 负责业务规则，Repository 负责数据访问。"],
    )
    store.add_documents(loader.load_context_documents(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts,
        source="request.code_practice.documentTexts",
        title_prefix="smoke-code-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    ))
    generated = agent.generate(request)
    graded = agent.grade(CodePracticeGradeRequest(
        studentProfileId=request.studentProfileId,
        courseId=request.courseId,
        studentProfileSummary=request.studentProfileSummary,
        courseTitle=request.courseTitle,
        topic=request.topic,
        exercise=generated.exercise,
        submissionCode=generated.exercise.starterCode,
    ))
    print(generated.model_dump_json(indent=2))
    print(graded.model_dump_json(indent=2))
    assert generated.exercise.starterCode
    assert generated.citations
    assert graded.defects
    assert graded.profileDimensionUpdates
    assert graded.score < graded.maxScore


if __name__ == "__main__":
    main()
