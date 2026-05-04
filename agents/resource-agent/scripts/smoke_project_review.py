import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.config import AgentSettings
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.project_review import ProjectReviewAgent
from learning_agent.schemas import ProjectFileInput, ProjectReviewRequest
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    request = ProjectReviewRequest(
        studentProfileId="profile-demo",
        courseId="course-demo",
        studentProfileSummary="Java 基础较弱，容易把 Controller、Service、Repository 职责写混。",
        courseTitle="Java Web 应用开发与软件工程实践",
        projectTitle="REST API 分层练习",
        targetTopic="Spring Boot Controller 与 REST API",
        files=[
            ProjectFileInput(
                path="src/main/java/demo/UserController.java",
                language="Java",
                content="""
@RestController
class UserController {
  private final UserRepository userRepository;
  @PostMapping("/users")
  public User create(@RequestBody User user) {
    if (user.getName() == null) {
      throw new RuntimeException("name");
    }
    return userRepository.save(user);
  }
  public User find(String id) {
    try {
      return userRepository.findById(id).get();
    } catch (Exception e) {
      e.printStackTrace();
    }
    return null;
  }
}
""",
            ),
            ProjectFileInput(
                path="src/main/java/demo/UserRepository.java",
                language="Java",
                content='class UserRepository { String sql = "select * from user where name=" + name; }',
            ),
        ],
        documentTexts=["课程要求 Controller 负责请求响应，Service 负责业务规则，Repository 负责数据访问。"],
    )
    store.add_documents(loader.load_context_documents(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + [f"{file.path}\n{file.content}" for file in request.files],
        source="request.project_review.documentTexts",
        title_prefix="smoke-project-review-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    ))
    response = ProjectReviewAgent(settings, store).review(request)
    print(response.model_dump_json(indent=2))
    assert response.overallScore < 90
    assert response.architectureIssues
    assert response.testGaps
    assert response.securityNotes
    assert response.knowledgeMapping
    assert response.refactorTasks
    assert response.citations
    assert response.profileDimensionUpdates


if __name__ == "__main__":
    main()
