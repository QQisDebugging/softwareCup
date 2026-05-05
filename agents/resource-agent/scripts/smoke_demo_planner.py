import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from learning_agent.config import AgentSettings
from learning_agent.demo_planner import DemoScenarioPlannerAgent
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.schemas import DemoScenarioRequest
from learning_agent.vector_store import InMemoryVectorStore


def main() -> None:
    settings = AgentSettings.from_env()
    loader = DocumentLoader(settings.project_root)
    store = InMemoryVectorStore(HashingEmbeddingModel(settings.embedding_dimensions), settings.project_root)
    store.add_documents(loader.load_seed_documents(settings.seed_knowledge_paths))
    request = DemoScenarioRequest(
        scenarioTitle="软件杯 A3 个性化学习多智能体 7 分钟演示",
        audience="初赛评委",
        courseTitle="Java Web 应用开发与软件工程实践",
        studentProfileSummary="Java 基础较弱，喜欢图解和项目案例。",
        timeLimitMinutes=7,
        coreEndpoints=[
            "/agents/profile/infer",
            "/agents/prerequisite/diagnose",
            "/agents/resources/curate",
            "/agents/resource-generation",
            "/agents/assessment/grade",
            "/agents/report/portfolio",
            "/agents/trace/explain",
            "/agents/class/analytics",
        ],
        availableArtifacts=["smoke_full_ai_agents.py 输出", "Java/Vue3 对接文档", "课程知识库 JSON"],
        riskConcerns=["网络不稳定时要能离线演示", "评委可能追问防幻觉和引用来源"],
        documentTexts=["演示视频应清晰展示操作流程、核心功能、多模态资源生成效果及前沿 AI 技术应用成果。"],
    )
    store.add_documents(loader.load_context_documents(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + request.coreEndpoints + request.availableArtifacts + request.riskConcerns,
        source="request.demo_scenario.documentTexts",
        title_prefix="smoke-demo-scenario-inline",
        metadata={"courseTitle": request.courseTitle},
    ))
    response = DemoScenarioPlannerAgent(settings, store).plan(request)
    print(response.model_dump_json(indent=2))
    assert response.scenes
    assert len(response.scenes) >= 6
    assert response.scenes[0].startSecond == 0
    assert response.scenes[-1].endSecond <= request.timeLimitMinutes * 60
    assert response.totalEstimatedMinutes * 60 >= response.scenes[-1].endSecond
    assert response.timelineMarkdown
    assert response.judgeHighlights
    assert response.prepChecklist
    assert response.riskPlaybook
    assert response.successMetrics
    assert response.citations


if __name__ == "__main__":
    main()
