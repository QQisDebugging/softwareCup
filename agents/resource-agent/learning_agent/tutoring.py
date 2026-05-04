from learning_agent.config import AgentSettings
from learning_agent.llm import ProviderRouter
from learning_agent.resource_templates import compact, mermaid_map
from learning_agent.safety import ContentSafetyReview
from learning_agent.schemas import KnowledgeMatch, TutoringRequest, TutoringResponse
from learning_agent.vector_store import InMemoryVectorStore


class TutoringAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store
        self.provider_router = ProviderRouter(settings)
        self.safety = ContentSafetyReview()

    def answer(self, request: TutoringRequest) -> TutoringResponse:
        citations = self.vector_store.search(
            query=self._query(request),
            top_k=self.settings.retrieval_top_k,
        )
        system_prompt = (
            "你是高校课程智能辅导 Agent。回答必须基于课程资料、学生画像和上下文，"
            "发现资料不足时要说明不确定性，并给出下一步学习建议。"
        )
        user_prompt = self._user_prompt(request, citations)
        raw_answer, provider, fallback = self.provider_router.complete(system_prompt, user_prompt)
        answer = self._assemble_answer(request, citations, raw_answer, provider, fallback)
        answer, safety_issues = self.safety.sanitize(answer)
        if safety_issues:
            answer += "\n\n> 安全处理：" + "；".join(safety_issues)
        return TutoringResponse(
            answer=answer,
            citations=citations,
            followUpQuestions=self._follow_ups(request, citations),
            learningActions=self._learning_actions(request),
            profileSignals=self._profile_signals(request),
            mermaidDiagram=mermaid_map(request.question),
            provider=provider,
            fallbackUsed=fallback,
        )

    def _query(self, request: TutoringRequest) -> str:
        return "\n".join(
            [
                request.courseTitle,
                request.question,
                request.studentProfileSummary,
                "\n".join(request.conversationHistory[-6:]),
            ]
        )

    def _user_prompt(self, request: TutoringRequest, citations: list[KnowledgeMatch]) -> str:
        context = "\n\n".join(f"[{item.title}] {compact(item.text, 360)}" for item in citations[:5])
        history = "\n".join(request.conversationHistory[-6:]) or "无"
        return f"""课程：{request.courseTitle}
学生画像：{request.studentProfileSummary}
对话历史：{history}
学生问题：{request.question}
回答形式：{request.modality}
RAG资料：{context or '未命中课程资料'}

请输出：1. 直接回答；2. 推理步骤；3. 常见误区；4. 下一步练习。"""

    def _assemble_answer(
        self,
        request: TutoringRequest,
        citations: list[KnowledgeMatch],
        raw_answer: str,
        provider: str,
        fallback: bool,
    ) -> str:
        citation_lines = "\n".join(
            f"- [{index}] {item.title}，来源 `{item.source}`，相关度 {item.score}：{compact(item.text, 120)}"
            for index, item in enumerate(citations[:5], start=1)
        ) or "- 未命中资料。建议先上传课程讲义、教材或项目说明。"
        uncertainty = (
            "当前回答已结合检索资料。"
            if citations
            else "当前知识库没有命中强相关资料，以下回答按课程通用知识给出，需要教师或资料复核。"
        )
        return f"""# 智能辅导答复

问题：{request.question}
课程：{request.courseTitle}
模型提供方：{provider}{"（已降级）" if fallback else ""}

## 直接回答
{compact(raw_answer, 1200)}

## 分步讲解
1. 先确认问题涉及的核心概念和先修知识。
2. 再把概念放回 `{request.courseTitle}` 的真实任务场景中。
3. 最后用一个小练习验证是否真的理解，而不是只记住定义。

## 图解脚本
{mermaid_map(request.question)}

## 资料依据
{citation_lines}

## 防幻觉说明
{uncertainty}"""

    def _follow_ups(self, request: TutoringRequest, citations: list[KnowledgeMatch]) -> list[str]:
        return [
            f"你能用自己的话复述 `{request.question}` 的关键步骤吗？",
            "这个问题在你的项目里对应哪个文件、接口或实验任务？",
            "你最不确定的是概念定义、代码实现，还是调试过程？",
        ][: 2 if citations else 3]

    def _learning_actions(self, request: TutoringRequest) -> list[str]:
        return [
            "阅读答复中的资料依据并标出不理解的术语。",
            "完成一个 10 分钟复述任务，把概念解释给同伴或写成 5 行笔记。",
            "提交一个最小练习结果，系统会根据反馈更新画像。",
        ]

    def _profile_signals(self, request: TutoringRequest) -> list[str]:
        text = request.question + "\n" + request.studentProfileSummary
        signals = []
        if any(keyword in text for keyword in ["不会", "不懂", "混淆", "错误", "weak", "confused"]):
            signals.append("MASTERY_WEAKNESS")
        if any(keyword in text for keyword in ["图", "视频", "动画", "diagram", "visual"]):
            signals.append("COGNITIVE_STYLE")
        if not signals:
            signals.append("LEARNING_GOAL")
        return signals

