import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.assessment import AssessmentAgent
from learning_agent.config import AgentSettings
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.schemas import AssessmentAnswer, AssessmentGenerateRequest, AssessmentGradeRequest
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    agent = AssessmentAgent(settings, store)
    generate_request = AssessmentGenerateRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary="Java 基础较弱，容易混淆 Controller、Service、Repository。",
        courseTitle="Java Web 应用开发与软件工程实践",
        topic="Spring Boot Controller 与 REST API",
        count=4,
        documentTexts=["Controller 负责请求响应，Service 负责业务规则，Repository 负责数据访问。"],
    )
    store.add_documents(loader.load_context_documents(
        paths=generate_request.knowledgeBasePaths,
        texts=generate_request.documentTexts,
        source="request.assessment.documentTexts",
        title_prefix="smoke-assessment-inline",
        metadata={"studentProfileId": generate_request.studentProfileId, "courseId": generate_request.courseId},
    ))
    generated = agent.generate(generate_request)
    answers = [
        AssessmentAnswer(questionId=generated.questions[0].id, answer=generated.questions[0].answer),
        AssessmentAnswer(questionId=generated.questions[1].id, answer="正确"),
        AssessmentAnswer(questionId=generated.questions[2].id, answer="Controller -> Service -> Repository -> DB"),
        AssessmentAnswer(questionId=generated.questions[3].id, answer="它负责请求响应，误区是把业务都写进 Controller。"),
    ]
    graded = agent.grade(AssessmentGradeRequest(
        studentProfileId=generate_request.studentProfileId,
        courseId=generate_request.courseId,
        studentProfileSummary=generate_request.studentProfileSummary,
        courseTitle=generate_request.courseTitle,
        topic=generate_request.topic,
        questions=generated.questions,
        answers=answers,
    ))
    print(generated.model_dump_json(indent=2))
    print(graded.model_dump_json(indent=2))
    assert len(generated.questions) == 4
    assert generated.citations
    assert graded.maxScore > 0
    assert graded.profileDimensionUpdates
    assert "MASTERY_WEAKNESS" in {item.dimensionKey for item in graded.profileDimensionUpdates}


if __name__ == "__main__":
    main()

