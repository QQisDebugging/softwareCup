from learning_agent.config import AgentSettings
from learning_agent.resource_templates import compact
from learning_agent.schemas import (
    KnowledgeMatch,
    ProfileContradiction,
    ProfileDimensionUpdate,
    ProfileInferRequest,
    ProfileInferResponse,
)
from learning_agent.vector_store import InMemoryVectorStore


class ProfileInferenceAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def infer(self, request: ProfileInferRequest) -> ProfileInferResponse:
        citations = self.vector_store.search(self._query(request), top_k=self.settings.retrieval_top_k)
        text = self._all_text(request)
        signals = self._signals(text)
        dimensions = self._dimensions(request, text, signals)
        contradictions = self._contradictions(text)
        questions = self._follow_up_questions(dimensions, contradictions)
        summary = (
            f"已从 {len(request.dialogueTurns)} 轮对话和 {len(request.learningRecords)} 条学习记录中"
            f"抽取 {len(dimensions)} 个画像维度、{len(signals)} 条信号。"
        )
        return ProfileInferResponse(
            studentProfileId=request.studentProfileId,
            dimensions=dimensions,
            extractedSignals=signals,
            contradictions=contradictions,
            followUpQuestions=questions,
            citations=citations,
            summary=summary,
        )

    def _query(self, request: ProfileInferRequest) -> str:
        return "\n".join([
            request.courseTitle,
            request.declaredMajor,
            request.currentLevel,
            request.learningGoal,
            request.preferences,
            request.constraintsText,
            *request.dialogueTurns,
            *request.learningRecords,
            *request.assessmentSummaries,
            *request.tutoringSummaries,
        ])

    def _all_text(self, request: ProfileInferRequest) -> str:
        return "\n".join([
            request.declaredMajor,
            request.currentLevel,
            request.learningGoal,
            request.preferences,
            request.constraintsText,
            *request.dialogueTurns,
            *request.learningRecords,
            *request.assessmentSummaries,
            *request.tutoringSummaries,
        ])

    def _signals(self, text: str) -> list[str]:
        rules = [
            ("基础弱", ["基础弱", "较弱", "零基础", "不熟", "不会", "看不懂"]),
            ("偏好图解", ["图解", "思维导图", "可视化", "流程图"]),
            ("偏好案例", ["案例", "项目", "实操", "实践"]),
            ("偏好短视频", ["短视频", "视频", "动画", "分镜"]),
            ("时间受限", ["每天", "分钟", "时间少", "碎片"]),
            ("主动提问", ["为什么", "怎么", "追问", "提问"]),
            ("错题复盘", ["错题", "复盘", "反思", "总结"]),
            ("代码薄弱", ["代码", "编程", "调试", "报错"]),
            ("分层职责薄弱", ["Controller", "Service", "Repository", "分层"]),
        ]
        signals = [name for name, keywords in rules if any(keyword in text for keyword in keywords)]
        return list(dict.fromkeys(signals))[:12]

    def _dimensions(
        self,
        request: ProfileInferRequest,
        text: str,
        signals: list[str],
    ) -> list[ProfileDimensionUpdate]:
        evidence = compact(text or "缺少对话证据，使用默认画像。", 220)
        foundation = "基础补强型" if "基础弱" in signals else request.currentLevel or "待进一步诊断"
        style = "图解+案例驱动" if {"偏好图解", "偏好案例"} & set(signals) else request.preferences or "待确认"
        goal = request.learningGoal or self._guess_goal(text)
        error_points = self._error_points(text, signals)
        constraints = request.constraintsText or ("时间受限，需要短任务" if "时间受限" in signals else "待确认")
        return [
            self._dimension("KNOWLEDGE_FOUNDATION", "知识基础", foundation, evidence, 0.78),
            self._dimension("COGNITIVE_STYLE", "认知风格", style, evidence, 0.74),
            self._dimension("LEARNING_GOAL", "学习目标", goal, evidence, 0.75),
            self._dimension("INTEREST_DIRECTION", "兴趣方向", request.declaredMajor or request.courseTitle or "待确认", evidence, 0.68),
            self._dimension("ERROR_PRONE_POINTS", "易错点", error_points, evidence, 0.76),
            self._dimension("TIME_CONSTRAINT", "时间约束", constraints, evidence, 0.7),
            self._dimension("RESOURCE_PREFERENCE", "资源偏好", style, evidence, 0.72),
            self._dimension("MASTERY_WEAKNESS", "掌握度/薄弱点", self._mastery(text, signals), evidence, 0.73),
        ]

    def _dimension(
        self,
        key: str,
        name: str,
        value: str,
        evidence: str,
        confidence: float,
    ) -> ProfileDimensionUpdate:
        return ProfileDimensionUpdate(
            dimensionKey=key,
            dimensionName=name,
            value=value,
            evidence=evidence,
            confidenceScore=confidence,
            source="profile_inference_agent",
        )

    def _guess_goal(self, text: str) -> str:
        if "Spring" in text or "REST" in text:
            return "掌握 Spring Boot REST API 分层开发"
        if "算法" in text:
            return "提升算法题解和复杂度分析能力"
        return "提升课程核心知识掌握度"

    def _error_points(self, text: str, signals: list[str]) -> str:
        points = []
        if "分层职责薄弱" in signals:
            points.append("Controller/Service/Repository 职责边界")
        if "代码薄弱" in signals:
            points.append("代码调试与实操迁移")
        if "错题复盘" in signals:
            points.append("错因分类需要持续沉淀")
        return "、".join(points) if points else "待通过测评进一步识别"

    def _mastery(self, text: str, signals: list[str]) -> str:
        if "基础弱" in signals:
            return "当前处于基础补强阶段，适合先修诊断和低门槛案例。"
        if "错题复盘" in signals:
            return "已出现复盘行为，可进入闭环复测。"
        return "需要结合测评结果确认掌握度。"

    def _contradictions(self, text: str) -> list[ProfileContradiction]:
        contradictions: list[ProfileContradiction] = []
        if "零基础" in text and ("高阶" in text or "竞赛" in text):
            contradictions.append(ProfileContradiction(
                field="知识基础/学习目标",
                evidenceA="学生自述零基础或基础弱。",
                evidenceB="同时提出高阶或竞赛目标。",
                resolutionQuestion="你希望先补基础再冲刺高阶，还是已有部分基础但表达为零基础？",
            ))
        if "不喜欢视频" in text and "短视频" in text:
            contradictions.append(ProfileContradiction(
                field="资源偏好",
                evidenceA="学生表达不喜欢视频。",
                evidenceB="同时提出短视频或视频资源需求。",
                resolutionQuestion="你更偏好图文讲义，还是可以接受 3-5 分钟短视频？",
            ))
        return contradictions[:4]

    def _follow_up_questions(
        self,
        dimensions: list[ProfileDimensionUpdate],
        contradictions: list[ProfileContradiction],
    ) -> list[str]:
        questions = [item.resolutionQuestion for item in contradictions]
        known = {dimension.dimensionKey for dimension in dimensions if "待确认" not in dimension.value}
        if "TIME_CONSTRAINT" not in known:
            questions.append("你每天大概能投入多少分钟学习这门课？")
        if "ERROR_PRONE_POINTS" not in known:
            questions.append("最近一次做题或写代码时，最常卡在哪一步？")
        questions.append("你希望下一份资源更偏讲解、图解、练习题、实操项目还是短视频脚本？")
        return questions[:5]
