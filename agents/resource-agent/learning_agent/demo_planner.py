from learning_agent.config import AgentSettings
from learning_agent.resource_templates import compact
from learning_agent.schemas import (
    DemoRiskPlan,
    DemoScenarioRequest,
    DemoScenarioResponse,
    DemoScene,
    KnowledgeMatch,
)
from learning_agent.vector_store import InMemoryVectorStore


class DemoScenarioPlannerAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def plan(self, request: DemoScenarioRequest) -> DemoScenarioResponse:
        citations = self.vector_store.search(self._query(request), top_k=self.settings.retrieval_top_k)
        endpoints = request.coreEndpoints or self._default_endpoints()
        scenes = self._scenes(request, endpoints)
        total_seconds = sum(scene.estimatedSeconds for scene in scenes)
        total_minutes = max(1, (total_seconds + 59) // 60)
        summary = (
            f"`{request.scenarioTitle}` 演示规划完成：{len(scenes)} 个场景，预计 {total_minutes} 分钟，"
            f"覆盖画像、诊断、生成、评估、报告和可解释追踪。"
        )
        return DemoScenarioResponse(
            demoTitle=request.scenarioTitle,
            totalEstimatedMinutes=total_minutes,
            scenes=scenes,
            timelineMarkdown=self._timeline_markdown(scenes),
            judgeHighlights=self._highlights(request),
            prepChecklist=self._checklist(request, scenes),
            riskPlaybook=self._risk_playbook(request),
            successMetrics=self._success_metrics(),
            citations=citations,
            summary=summary,
        )

    def _query(self, request: DemoScenarioRequest) -> str:
        return "\n".join([
            request.scenarioTitle,
            request.audience,
            request.courseTitle,
            request.studentProfileSummary,
            " ".join(request.coreEndpoints),
            " ".join(request.availableArtifacts),
            " ".join(request.riskConcerns),
            "演示 视频 答辩 多智能体 RAG 防幻觉 画像",
        ])

    def _default_endpoints(self) -> list[str]:
        return [
            "/agents/profile/infer",
            "/agents/prerequisite/diagnose",
            "/agents/resources/curate",
            "/agents/resource-generation",
            "/agents/assessment/grade",
            "/agents/report/portfolio",
            "/agents/trace/explain",
        ]

    def _scenes(self, request: DemoScenarioRequest, endpoints: list[str]) -> list[DemoScene]:
        seconds_budget = max(180, request.timeLimitMinutes * 60)
        selected_endpoints = endpoints[:min(10, max(1, seconds_budget // 10))]
        per_scene = max(35, min(65, round(seconds_budget / max(1, len(selected_endpoints)))))
        scenes = [
            self._scene(index, endpoint, request, per_scene)
            for index, endpoint in enumerate(selected_endpoints, start=1)
        ]
        total = sum(scene.estimatedSeconds for scene in scenes)
        if total > seconds_budget:
            base_seconds = max(10, seconds_budget // len(scenes))
            remainder = max(0, seconds_budget - (base_seconds * len(scenes)))
            scenes = [
                scene.model_copy(update={"estimatedSeconds": base_seconds + (1 if index < remainder else 0)})
                for index, scene in enumerate(scenes)
            ]
        return self._with_timeline(scenes)

    def _with_timeline(self, scenes: list[DemoScene]) -> list[DemoScene]:
        current = 0
        timeline: list[DemoScene] = []
        for scene in scenes:
            start = current
            end = start + scene.estimatedSeconds
            timeline.append(scene.model_copy(update={"startSecond": start, "endSecond": end}))
            current = end
        return timeline

    def _scene(
        self,
        index: int,
        endpoint: str,
        request: DemoScenarioRequest,
        seconds: int,
    ) -> DemoScene:
        configs = {
            "/agents/profile/infer": (
                "对话式画像抽取",
                "输入学生自然语言对话、目标、偏好和学习记录。",
                "输出 8 个画像维度、证据和置信度。",
                "证明不是表单画像，而是可随学更新的智能体画像。",
                "若接口失败，展示 smoke_profile_infer.py 的 JSON 输出截图。",
            ),
            "/agents/prerequisite/diagnose": (
                "先修诊断",
                "输入目标知识点和最近薄弱点。",
                "输出准备度、先修缺口、诊断题和补救动作。",
                "把个性化学习入口从直接生成资源升级为先诊断再学习。",
                "使用离线模板返回确定性结果。",
            ),
            "/agents/resources/curate": (
                "资源策展",
                "输入时间预算、候选资源和薄弱点。",
                "输出资源包、覆盖图和学习顺序。",
                "回应赛题中资源繁杂无序、难以精准匹配的问题。",
                "保留候选资源文本，离线也能生成资源包。",
            ),
            "/agents/resource-generation": (
                "多智能体资源生成",
                "输入画像、课程、主题、资源类型和 RAG 资料。",
                "输出讲解文档、思维导图、练习题、拓展阅读和实操案例。",
                "展示 LangGraph/LangChain/RAG/Embedding 的核心主程能力。",
                "若云模型不可用，offline provider 保证结构化演示不中断。",
            ),
            "/agents/assessment/grade": (
                "测评批改与画像更新",
                "输入题目和学生答案。",
                "输出得分、逐题反馈、薄弱点和画像更新建议。",
                "形成学习效果评估和动态资源调整闭环。",
                "可直接使用 smoke_assessment.py 的固定题目。",
            ),
            "/agents/report/portfolio": (
                "学习档案报告",
                "输入资源、测评、答疑、代码练习和复盘证据。",
                "输出证据时间线、掌握雷达、风险和教师评语草稿。",
                "让教师端能看到可解释的成长证据，而不是单次聊天结果。",
                "若历史数据不足，使用演示样例生成报告。",
            ),
            "/agents/trace/explain": (
                "智能体链路追踪",
                "输入任务名、参与 Agent、引用和降级事件。",
                "输出步骤、质量门禁、fallback 和复现说明。",
                "解决评委对黑盒生成、防幻觉和可复现性的疑问。",
                "追踪接口只记录摘要，不暴露模型隐藏推理。",
            ),
            "/agents/code/project-review": (
                "项目级代码审查",
                "输入多文件代码片段。",
                "输出分层缺陷、测试缺口、安全提示和重构任务。",
                "体现 AI 辅助编程和工程实践能力，不止做题。",
                "使用内置静态规则也可离线审查。",
            ),
            "/agents/class/analytics": (
                "班级学习分析",
                "输入学生学习快照。",
                "输出班级掌握度、参与度、干预分组和资源缺口。",
                "把个体智能体能力扩展到教师端班级治理。",
                "用 mock 班级快照即可演示。",
            ),
        }
        title, input_setup, expected, talking, fallback = configs.get(endpoint, (
            endpoint,
            f"调用 `{endpoint}` 的标准演示请求。",
            "输出结构化 JSON 和引用证据。",
            "展示系统可扩展的智能体端点。",
            "保留 smoke 输出作为备用。",
        ))
        return DemoScene(
            order=index,
            title=title,
            endpoint=endpoint,
            startSecond=0,
            endSecond=0,
            inputSetup=input_setup,
            expectedOutput=expected,
            talkingPoint=talking,
            fallbackPlan=fallback,
            estimatedSeconds=seconds,
        )

    def _highlights(self, request: DemoScenarioRequest) -> list[str]:
        return [
            "多智能体不是概念图，实际端点覆盖画像、诊断、生成、评估、报告和追踪。",
            "所有核心输出保留 citations、evidence、confidenceScore 或 qualityGates，便于防幻觉答辩。",
            "offline provider 保证无密钥环境可复现，接入讯飞星火后可替换生成能力。",
            f"演示围绕 `{request.courseTitle}` 和同一学生画像展开，避免功能割裂。",
        ]

    def _checklist(self, request: DemoScenarioRequest, scenes: list[DemoScene]) -> list[str]:
        checklist = [
            "启动 Python 服务：uvicorn main:app --host 0.0.0.0 --port 9001。",
            "提前运行 scripts/smoke_full_ai_agents.py，保留终端输出截图。",
            "准备同一名学生画像、同一门课程、同一薄弱主题，保证故事线一致。",
            "前端每个 AI 调用都展示 loading、引用展开、失败重试和 trace 抽屉。",
        ]
        checklist.extend(f"场景 {scene.order}: 准备 `{scene.endpoint}` 的请求体。" for scene in scenes[:4])
        if request.riskConcerns:
            checklist.append(f"答辩风险预案：{compact('；'.join(request.riskConcerns), 160)}")
        return checklist[:10]

    def _risk_playbook(self, request: DemoScenarioRequest) -> list[DemoRiskPlan]:
        concerns = request.riskConcerns or [
            "网络或模型密钥不可用",
            "评委追问防幻觉依据",
            "前端接口联调不稳定",
        ]
        playbook = []
        for concern in concerns[:6]:
            if "网络" in concern or "密钥" in concern or "模型" in concern:
                mitigation = "切换 offline provider，并展示 smoke_full_ai_agents.py 的可复现输出。"
                artifact = "终端 smoke 输出和 /agents/providers/status"
            elif "幻觉" in concern or "引用" in concern:
                mitigation = "展开 citations、qualityGates 和 content audit 结果，说明证据覆盖。"
                artifact = "/agents/trace/explain 与 /agents/safety/audit 响应"
            elif "前端" in concern or "联调" in concern:
                mitigation = "直接调用 Python FastAPI Swagger 或 PowerShell API 示例展示核心能力。"
                artifact = "docs/API_EXAMPLES.md"
            else:
                mitigation = "保留对应 smoke 脚本输出和结构化 JSON，确保可演示、可复核。"
                artifact = "单功能 smoke 脚本"
            playbook.append(DemoRiskPlan(
                concern=concern,
                mitigation=mitigation,
                fallbackArtifact=artifact,
            ))
        return playbook

    def _timeline_markdown(self, scenes: list[DemoScene]) -> str:
        lines = ["| 时间 | 场景 | 端点 | 讲解重点 |", "| --- | --- | --- | --- |"]
        for scene in scenes:
            start = self._format_time(scene.startSecond)
            end = self._format_time(scene.endSecond)
            lines.append(f"| {start}-{end} | {scene.title} | `{scene.endpoint}` | {scene.talkingPoint} |")
        return "\n".join(lines)

    def _format_time(self, second: int) -> str:
        minutes, seconds = divmod(second, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _success_metrics(self) -> list[str]:
        return [
            "7 分钟内完整展示诊断 -> 资源 -> 学习 -> 测评 -> 档案 -> 追踪闭环。",
            "至少展示 5 类个性化资源和 1 个多模态脚本。",
            "至少展示 1 次画像维度自动更新。",
            "至少展示 1 个引用证据和 1 个质量门禁。",
            "演示失败时能用 smoke 输出证明 Python Agent 可独立运行。",
        ]
