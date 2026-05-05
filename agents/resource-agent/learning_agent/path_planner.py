from learning_agent.config import AgentSettings
from learning_agent.resource_templates import compact, infer_target_level
from learning_agent.schemas import (
    KnowledgeMatch,
    LearningPathPlanRequest,
    LearningPathPlanResponse,
    LearningPathStage,
    ProfileDimensionUpdate,
    ResourceRecommendation,
    ReviewCheckpoint,
)
from learning_agent.vector_store import InMemoryVectorStore


class PathPlannerAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def plan(self, request: LearningPathPlanRequest) -> LearningPathPlanResponse:
        citations = self.vector_store.search(self._query(request), top_k=self.settings.retrieval_top_k)
        target_level = infer_target_level(request.studentProfileSummary)
        weak_points = self._weak_points(request)
        stage_count = min(max(3, request.timeframeDays), 10)
        stages = [
            self._stage(request, citations, weak_points, index, stage_count)
            for index in range(stage_count)
        ]
        recommendations = self._recommendations(request, weak_points, target_level)
        checkpoints = self._checkpoints(request, stage_count)
        summary = (
            f"已为 `{request.topic}` 生成 {stage_count} 天路径，按 `{target_level}` "
            f"组织讲解、图解、练习、实操和复盘。"
        )
        return LearningPathPlanResponse(
            planTitle=f"{request.topic} 个性化学习路径",
            studentProfileId=request.studentProfileId,
            courseId=request.courseId,
            topic=request.topic,
            targetLevel=target_level,
            stages=stages,
            resourceRecommendations=recommendations,
            reviewCheckpoints=checkpoints,
            mermaidRoadmap=self._roadmap(request, stages),
            citations=citations,
            summary=summary,
            profileDimensionUpdates=self._profile_updates(request, weak_points, summary),
        )

    def _query(self, request: LearningPathPlanRequest) -> str:
        return "\n".join([
            request.courseTitle,
            request.topic,
            request.goal,
            request.studentProfileSummary,
            " ".join(request.weaknessSignals),
        ])

    def _weak_points(self, request: LearningPathPlanRequest) -> list[str]:
        candidates = [item.strip() for item in request.weaknessSignals if item.strip()]
        if candidates:
            return list(dict.fromkeys(candidates))[:5]
        text = request.studentProfileSummary + "\n" + request.topic
        if any(key in text for key in ["Controller", "Service", "Repository", "分层", "layer"]):
            return ["分层职责", "请求响应边界", "业务逻辑下沉"]
        if any(key in text for key in ["SQL", "数据库", "JPA"]):
            return ["数据建模", "事务边界", "查询调试"]
        return [request.topic, "概念迁移", "实操验证"]

    def _stage(
        self,
        request: LearningPathPlanRequest,
        citations: list[KnowledgeMatch],
        weak_points: list[str],
        index: int,
        stage_count: int,
    ) -> LearningPathStage:
        day = index + 1
        weak_point = weak_points[index % len(weak_points)]
        evidence = compact(citations[index % len(citations)].text, 90) if citations else request.topic
        phase_titles = [
            "定位薄弱点",
            "概念图解",
            "案例拆解",
            "分层练习",
            "错因复盘",
            "项目迁移",
            "综合测评",
        ]
        title = phase_titles[min(index, len(phase_titles) - 1)]
        if day == stage_count:
            title = "闭环复测与路径重排"
        return LearningPathStage(
            day=day,
            title=f"第 {day} 天：{title}",
            objective=f"围绕 `{weak_point}` 完成从资料理解到可验证输出的学习闭环。",
            learningActions=[
                f"阅读 RAG 依据片段：{evidence}",
                f"用自己的话写出 `{weak_point}` 的输入、处理和输出。",
                "把当天结论沉淀成 5 行学习笔记，并标注仍不确定的问题。",
            ],
            resourceTypes=self._resource_types(index),
            practiceTask=self._practice_task(request, weak_point, index),
            checkpoint=self._checkpoint_text(request, weak_point, index),
            estimatedMinutes=min(request.dailyMinutes, 30 + index * 5),
        )

    def _resource_types(self, index: int) -> list[str]:
        sequence = [
            ["专业课程讲解文档", "知识点思维导图"],
            ["短视频讲解脚本", "错题复盘卡"],
            ["代码/项目实操案例", "分层练习题"],
            ["拓展阅读材料", "综合测评题"],
        ]
        return sequence[index % len(sequence)]

    def _practice_task(self, request: LearningPathPlanRequest, weak_point: str, index: int) -> str:
        if index == 0:
            return f"列出 `{request.topic}` 中最容易混淆的 3 个概念，并为 `{weak_point}` 写一个反例。"
        if index % 3 == 1:
            return f"画出 `{weak_point}` 的 Mermaid 流程图，并说明每条边的依据。"
        if index % 3 == 2:
            return f"完成一个 30 分钟最小项目任务，证明自己能把 `{weak_point}` 用在真实场景。"
        return f"重做一次 `{request.topic}` 自适应测评，并比较画像薄弱点是否减少。"

    def _checkpoint_text(self, request: LearningPathPlanRequest, weak_point: str, index: int) -> str:
        if index == 0:
            return f"能解释 `{weak_point}` 的定义、边界和常见误区。"
        if index % 2 == 0:
            return f"能在 `{request.courseTitle}` 的项目案例中定位 `{weak_point}`。"
        return "能完成一次练习提交，并把错误原因写入复盘。"

    def _recommendations(
        self,
        request: LearningPathPlanRequest,
        weak_points: list[str],
        target_level: str,
    ) -> list[ResourceRecommendation]:
        resource_types = ["讲解文档", "知识点思维导图", "短视频脚本", "实操案例", "自适应测评"]
        return [
            ResourceRecommendation(
                priority=index + 1,
                resourceType=resource_type,
                title=f"{request.topic} - {weak_points[index % len(weak_points)]} {resource_type}",
                reason=f"匹配 `{target_level}` 学生画像，优先补齐 `{weak_points[index % len(weak_points)]}`。",
                estimatedMinutes=12 + index * 6,
            )
            for index, resource_type in enumerate(resource_types)
        ]

    def _checkpoints(self, request: LearningPathPlanRequest, stage_count: int) -> list[ReviewCheckpoint]:
        middle = max(1, round(stage_count / 2))
        return [
            ReviewCheckpoint(
                day=1,
                method="入口诊断",
                successCriteria=f"能说清 `{request.topic}` 的学习目标和当前薄弱点。",
            ),
            ReviewCheckpoint(
                day=middle,
                method="中途复盘",
                successCriteria="完成至少 1 个图解或实操交付物，并记录错因。",
            ),
            ReviewCheckpoint(
                day=stage_count,
                method="闭环复测",
                successCriteria="测评得分提升，画像中的薄弱点证据被更新。",
            ),
        ]

    def _roadmap(self, request: LearningPathPlanRequest, stages: list[LearningPathStage]) -> str:
        lines = ["```mermaid", "flowchart LR", f"  start([画像: {self._safe(request.studentProfileId)}])"]
        previous = "start"
        for index, stage in enumerate(stages, start=1):
            node = f"d{index}"
            lines.append(f"  {node}[{self._safe(stage.title)}]")
            lines.append(f"  {previous} --> {node}")
            previous = node
        lines.append("  review([测评批改])")
        lines.append("  profile([画像更新])")
        lines.append(f"  {previous} --> review --> profile")
        lines.append("```")
        return "\n".join(lines)

    def _profile_updates(
        self,
        request: LearningPathPlanRequest,
        weak_points: list[str],
        summary: str,
    ) -> list[ProfileDimensionUpdate]:
        return [
            ProfileDimensionUpdate(
                dimensionKey="LEARNING_GOAL",
                dimensionName="学习目标",
                value=f"{request.topic} 路径目标：{request.goal}",
                evidence=summary,
                confidenceScore=0.78,
                source="path_planner_agent",
            ),
            ProfileDimensionUpdate(
                dimensionKey="RESOURCE_PREFERENCE",
                dimensionName="资源偏好",
                value="推荐资源顺序：讲解文档 -> 图解 -> 视频脚本 -> 实操案例 -> 自适应测评",
                evidence=f"依据薄弱点：{'、'.join(weak_points)}",
                confidenceScore=0.72,
                source="path_planner_agent",
            ),
        ]

    def _safe(self, text: str) -> str:
        return text.replace('"', "").replace("`", "").replace("\n", " ")[:60]
