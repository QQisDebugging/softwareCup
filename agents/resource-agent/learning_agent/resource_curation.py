from learning_agent.config import AgentSettings
from learning_agent.resource_templates import compact, infer_target_level
from learning_agent.schemas import (
    CoverageMapItem,
    CuratedResource,
    KnowledgeMatch,
    ProfileDimensionUpdate,
    ResourceCurationRequest,
    ResourceCurationResponse,
)
from learning_agent.vector_store import InMemoryVectorStore


class ResourceCurationAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def curate(self, request: ResourceCurationRequest) -> ResourceCurationResponse:
        citations = self.vector_store.search(self._query(request), top_k=max(10, self.settings.retrieval_top_k))
        target_level = (
            infer_target_level(request.studentProfileSummary)
            if request.targetLevel == "自适应"
            else request.targetLevel
        )
        resource_types = request.resourceTypes or self._default_resource_types(request, target_level)
        curated = self._curated_resources(request, target_level, resource_types, citations)
        coverage = self._coverage_map(request, curated)
        usage_plan = self._usage_plan(request, curated)
        summary = (
            f"已为 `{request.topic}` 策展 {len(curated)} 个资源，目标层级 `{target_level}`，"
            f"总时长约 {sum(item.estimatedMinutes for item in curated)} 分钟。"
        )
        return ResourceCurationResponse(
            bundleTitle=f"{request.topic} 个性化资源包",
            targetLevel=target_level,
            curatedResources=curated,
            coverageMap=coverage,
            usagePlan=usage_plan,
            citations=citations,
            summary=summary,
            profileDimensionUpdates=self._profile_updates(request, target_level, summary),
        )

    def _query(self, request: ResourceCurationRequest) -> str:
        return "\n".join([
            request.courseTitle,
            request.topic,
            request.studentProfileSummary,
            " ".join(request.resourceTypes),
            " ".join(request.weaknesses),
            " ".join(request.candidateResources),
            "资源 推荐 策展 题库 实训 视频 文档",
        ])

    def _default_resource_types(self, request: ResourceCurationRequest, target_level: str) -> list[str]:
        if "高阶" in target_level:
            return ["拓展阅读", "项目实训", "代码实操", "综合测评", "同伴讲解任务"]
        if "实践" in target_level:
            return ["讲解文档", "实操案例", "代码练习", "错题复盘卡", "短视频脚本"]
        if request.weaknesses:
            return ["基础讲解文档", "知识点思维导图", "入口诊断题", "错题复盘卡", "短视频脚本"]
        return ["讲解文档", "知识点思维导图", "练习题", "实操案例", "拓展阅读"]

    def _curated_resources(
        self,
        request: ResourceCurationRequest,
        target_level: str,
        resource_types: list[str],
        citations: list[KnowledgeMatch],
    ) -> list[CuratedResource]:
        resources: list[CuratedResource] = []
        remaining = request.timeBudgetMinutes
        weak_points = request.weaknesses or [request.topic, "概念迁移", "实操验证"]
        for index, resource_type in enumerate(resource_types[:8], start=1):
            citation = citations[(index - 1) % len(citations)] if citations else None
            weak_point = weak_points[(index - 1) % len(weak_points)]
            minutes = self._estimate_minutes(resource_type, index, remaining)
            remaining = max(0, remaining - minutes)
            source_title = citation.title if citation else "待补充课程资料"
            evidence = compact(citation.text, 100) if citation else f"围绕 `{request.topic}` 的默认课程资源模板。"
            resources.append(CuratedResource(
                rank=index,
                title=f"{request.topic} - {weak_point} {resource_type}",
                resourceType=resource_type,
                difficulty=self._difficulty(target_level, index),
                estimatedMinutes=minutes,
                sourceTitle=source_title,
                reason=f"匹配 `{target_level}` 画像，优先覆盖 `{weak_point}`。依据：{evidence}",
                usageOrder=self._usage_order(index),
                citationIds=[citation.id] if citation else [],
            ))
            if remaining <= 8 and index >= 4:
                break
        return resources

    def _estimate_minutes(self, resource_type: str, index: int, remaining: int) -> int:
        base = 10 + index * 3
        if any(keyword in resource_type for keyword in ["项目", "实训", "代码", "实操"]):
            base += 10
        if any(keyword in resource_type for keyword in ["视频", "短视频", "分镜"]):
            base += 4
        if remaining <= 0:
            return max(8, min(base, 25))
        return max(8, min(base, remaining))

    def _difficulty(self, target_level: str, index: int) -> str:
        if "高阶" in target_level:
            return "进阶" if index <= 2 else "挑战"
        if "基础" in target_level:
            return "基础" if index <= 4 else "巩固"
        if index <= 2:
            return "基础"
        if index <= 5:
            return "进阶"
        return "挑战"

    def _usage_order(self, index: int) -> str:
        phases = ["入口诊断", "概念建立", "图解理解", "实操迁移", "错题复盘", "闭环复测", "拓展挑战", "成果沉淀"]
        return phases[min(index - 1, len(phases) - 1)]

    def _coverage_map(self, request: ResourceCurationRequest, resources: list[CuratedResource]) -> list[CoverageMapItem]:
        points = list(dict.fromkeys([request.topic, *request.weaknesses, "概念理解", "实操验证", "错题复盘"]))[:8]
        coverage: list[CoverageMapItem] = []
        for index, point in enumerate(points):
            matched = [
                resource.title
                for resource in resources
                if point in resource.title or index % max(1, len(resources)) == (resource.rank - 1) % max(1, len(resources))
            ][:3]
            gap_level = "已覆盖" if matched else "待补充"
            recommendation = (
                "按资源顺序学习并完成 checkpoint。"
                if matched
                else f"补充 `{point}` 的讲解或练习资源。"
            )
            coverage.append(CoverageMapItem(
                knowledgePoint=point,
                coveredBy=matched,
                gapLevel=gap_level,
                recommendation=recommendation,
            ))
        return coverage

    def _usage_plan(self, request: ResourceCurationRequest, resources: list[CuratedResource]) -> list[str]:
        if not resources:
            return [f"先导入 `{request.courseTitle}` 的讲义、实验文档和题库，再重新策展资源。"]
        return [
            f"{resource.usageOrder}：学习 `{resource.title}`，预计 {resource.estimatedMinutes} 分钟，完成后记录一个证据产物。"
            for resource in resources
        ] + [
            "学习结束后调用 `/agents/assessment/grade` 或 `/agents/report/portfolio` 写回掌握度证据。"
        ]

    def _profile_updates(
        self,
        request: ResourceCurationRequest,
        target_level: str,
        evidence: str,
    ) -> list[ProfileDimensionUpdate]:
        return [
            ProfileDimensionUpdate(
                dimensionKey="RESOURCE_BUNDLE_PREFERENCE",
                dimensionName="资源包偏好",
                value=f"{request.topic}：{target_level}，偏向 {'、'.join(request.resourceTypes or ['自适应资源组合'])}",
                evidence=evidence,
                confidenceScore=0.73,
                source="resource_curation_agent",
            )
        ]
