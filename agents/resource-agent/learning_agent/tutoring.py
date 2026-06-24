from learning_agent.config import AgentSettings
from learning_agent.llm import ProviderRouter
from learning_agent.resource_templates import compact, mermaid_map, preserve_text
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
            filters={"courseId": request.courseId} if request.courseId else None,
            soft_keys={"courseId"},
        )
        # 只保留本课程相关资料：排除比赛元数据（题目说明）等通用噪音片段
        citations = [c for c in citations if not self._is_noise_citation(c)]
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

    def _is_noise_citation(self, citation: KnowledgeMatch) -> bool:
        """排除与课程教学无关的比赛说明/平台元数据片段。"""
        haystack = f"{citation.title} {citation.source}".lower()
        noise_markers = ["题目说明", "reference", "竞赛", "比赛", "评分标准", "提交要求"]
        return any(marker.lower() in haystack for marker in noise_markers)

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

请用规范的 Markdown 输出（使用 ## 小标题、有序/无序列表，代码用```代码块），依次包含：
## 直接回答
## 常见误区
## 下一步练习"""

    def _assemble_answer(
        self,
        request: TutoringRequest,
        citations: list[KnowledgeMatch],
        raw_answer: str,
        provider: str,
        fallback: bool,
    ) -> str:
        # 只保留相关度较高的资料，并用简洁的标题呈现，避免把原始 json 片段堆到正文里
        relevant = [c for c in citations if c.score >= 0.08][:3]
        citation_lines = "\n".join(
            f"- {self._clean_citation_title(item)}"
            for item in relevant
        )
        # 模型主回答放在最前，并保留其 Markdown 结构（标题、列表、代码块）；
        # mermaid 图解通过独立的 mermaidDiagram 字段返回，不再塞进正文，避免结构被破坏。
        if citation_lines:
            return f"""{preserve_text(raw_answer, 4000)}

## 参考资料
{citation_lines}"""
        return preserve_text(raw_answer, 4000)

    def _clean_citation_title(self, item: KnowledgeMatch) -> str:
        title = (item.title or "").strip()
        # 课程 json 标题常形如 java-web-software-engineering，转成更友好的名称
        if not title or title.lower().endswith("engineering"):
            return "课程核心资料"
        return compact(title, 40)

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

