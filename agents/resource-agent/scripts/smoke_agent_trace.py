import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.agent_trace import AgentTraceAgent
from learning_agent.config import AgentSettings
from learning_agent.schemas import AgentTraceRequest, KnowledgeMatch


def main() -> None:
    settings = AgentSettings.from_env()
    request = AgentTraceRequest(
        taskName="个性化资源生成",
        userIntent="为 Java 基础较弱的学生生成 REST API 分层讲解资源",
        studentProfileId="profile-demo",
        courseId="course-demo",
        involvedAgents=[
            "profile_agent",
            "rag_retrieval_agent",
            "resource_planner_agent",
            "resource_generator_agent",
            "content_audit_agent",
        ],
        requestPayload={
            "topic": "Spring Boot Controller 与 REST API",
            "resourceType": "讲解文档+思维导图",
            "weaknesses": ["MVC 分层职责", "HTTP 请求响应"],
        },
        responseSummary="已生成讲解文档、Mermaid 思维导图、练习题和引用依据。",
        citations=[
            KnowledgeMatch(
                id="demo-citation-1",
                score=0.82,
                text="Controller 负责请求响应，Service 负责业务规则，Repository 负责数据访问。",
                source="smoke",
                title="Java Web 课程讲义",
                metadata={"courseId": "course-demo"},
            )
        ],
        fallbackEvents=["讯飞星火未配置时使用 offline provider 生成结构化演示结果。"],
    )
    response = AgentTraceAgent(settings).explain(request)
    print(response.model_dump_json(indent=2))
    assert response.traceId
    assert len(response.traceSteps) == 5
    assert response.qualityGates
    assert response.fallbackEvents
    assert response.reproducibilityNotes


if __name__ == "__main__":
    main()
