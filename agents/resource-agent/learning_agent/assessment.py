from learning_agent.config import AgentSettings
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.resource_templates import compact, infer_target_level
from learning_agent.schemas import (
    AssessmentAnswer,
    AssessmentGenerateRequest,
    AssessmentGenerateResponse,
    AssessmentGradeRequest,
    AssessmentGradeResponse,
    AssessmentQuestion,
    KnowledgeMatch,
    ProfileDimensionUpdate,
    QuestionGradeResult,
)
from learning_agent.vector_store import InMemoryVectorStore


class AssessmentAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store
        self.embedding_model = HashingEmbeddingModel(settings.embedding_dimensions)

    def generate(self, request: AssessmentGenerateRequest) -> AssessmentGenerateResponse:
        citations = self.vector_store.search(self._query(request), top_k=self.settings.retrieval_top_k)
        questions = [
            self._build_question(request, citations, index)
            for index in range(request.count)
        ]
        return AssessmentGenerateResponse(
            title=f"{request.topic} 自适应测评",
            topic=request.topic,
            questions=questions,
            citations=citations,
            summary=f"已根据画像层级 `{infer_target_level(request.studentProfileSummary)}` 生成 {len(questions)} 道测评题。",
        )

    def grade(self, request: AssessmentGradeRequest) -> AssessmentGradeResponse:
        answer_map = {answer.questionId: answer for answer in request.answers}
        results = [self._grade_question(question, answer_map.get(question.id)) for question in request.questions]
        score = sum(result.score for result in results)
        max_score = sum(result.maxScore for result in results) or 1
        ratio = score / max_score
        mastery = self._mastery_level(ratio)
        weak_points = [
            result.knowledgePoint
            for result in results
            if not result.correct
        ] or ["暂未发现明显薄弱点，建议提高题目难度继续测评"]
        feedback = self._feedback(request.topic, ratio, weak_points)
        return AssessmentGradeResponse(
            score=score,
            maxScore=max_score,
            masteryLevel=mastery,
            feedback=feedback,
            questionResults=results,
            weaknessSignals=weak_points,
            nextResourceTypes=self._next_resources(ratio),
            profileDimensionUpdates=self._profile_updates(request, mastery, feedback, weak_points, ratio),
        )

    def _query(self, request: AssessmentGenerateRequest) -> str:
        return "\n".join([
            request.courseTitle,
            request.topic,
            request.difficulty,
            request.studentProfileSummary,
        ])

    def _build_question(
        self,
        request: AssessmentGenerateRequest,
        citations: list[KnowledgeMatch],
        index: int,
    ) -> AssessmentQuestion:
        question_type = request.questionTypes[index % len(request.questionTypes)]
        difficulty = request.difficulty if request.difficulty != "自适应" else infer_target_level(request.studentProfileSummary)
        evidence = compact(citations[index % len(citations)].text, 120) if citations else request.topic
        qid = f"q{index + 1}"
        if "选择" in question_type:
            return AssessmentQuestion(
                id=qid,
                type="选择题",
                stem=f"关于 `{request.topic}`，以下哪一项最符合课程资料中的工程实践要求？",
                options=[
                    "A. Controller 可以直接承载所有业务规则",
                    "B. Controller 负责请求响应，复杂业务应下沉到 Service",
                    "C. Repository 应处理页面交互逻辑",
                    "D. DTO 只用于数据库建表",
                ],
                answer="B",
                rubric="选择 B 得满分；能说明分层职责可作为解释加分依据。",
                explanation=f"依据资料片段：{evidence}",
                difficulty=difficulty,
                knowledgePoints=[request.topic, "工程分层", "职责边界"],
                score=10,
            )
        if "判断" in question_type:
            return AssessmentQuestion(
                id=qid,
                type="判断题",
                stem=f"`{request.topic}` 只要能运行，就不需要考虑可维护性和测试边界。",
                answer="错误",
                rubric="回答错误并说明可维护性/测试边界得满分。",
                explanation=f"课程强调工程实践，不仅要求运行成功，也要求结构清晰。依据：{evidence}",
                difficulty=difficulty,
                knowledgePoints=[request.topic, "可维护性"],
                score=10,
            )
        if "代码" in question_type or "纠错" in question_type:
            return AssessmentQuestion(
                id=qid,
                type="代码纠错题",
                stem=(
                    f"阅读伪代码：`Controller -> Repository -> DB`。请指出它在 `{request.topic}` "
                    "学习场景中的问题，并给出改造后的调用链。"
                ),
                answer="Controller -> Service -> Repository -> DB",
                rubric="指出 Controller 直接访问 Repository 的职责混淆，并写出 Service 层改造链路。",
                explanation=f"该题考查职责边界和项目迁移能力。依据：{evidence}",
                difficulty=difficulty,
                knowledgePoints=[request.topic, "代码实操", "分层改造"],
                score=15,
            )
        return AssessmentQuestion(
            id=qid,
            type="简答题",
            stem=f"结合 `{request.courseTitle}`，用 120 字说明 `{request.topic}` 的作用、常见误区和一个应用场景。",
            answer=f"应说明 {request.topic} 的职责、边界、误区和项目案例。",
            rubric="覆盖作用、误区、应用场景三点得满分；缺一项扣分。",
            explanation=f"简答题用于检测概念迁移和表达能力。依据：{evidence}",
            difficulty=difficulty,
            knowledgePoints=[request.topic, "概念迁移"],
            score=15,
        )

    def _grade_question(self, question: AssessmentQuestion, answer: AssessmentAnswer | None) -> QuestionGradeResult:
        if answer is None or not answer.answer.strip():
            return QuestionGradeResult(
                questionId=question.id,
                score=0,
                maxScore=question.score,
                correct=False,
                feedback="未作答，需要回到讲解资源补齐概念。",
                knowledgePoint=question.knowledgePoints[0] if question.knowledgePoints else question.type,
            )
        normalized_answer = answer.answer.strip().lower()
        normalized_expected = question.answer.strip().lower()
        if question.type in {"选择题", "判断题"}:
            correct = normalized_answer in {normalized_expected, normalized_expected[:1]}
            score = question.score if correct else 0
        else:
            expected_tokens = set(self.embedding_model.tokens(question.answer + " " + question.rubric))
            answer_tokens = set(self.embedding_model.tokens(answer.answer))
            overlap = len(expected_tokens & answer_tokens)
            ratio = min(1.0, overlap / max(4, len(expected_tokens)))
            score = round(question.score * ratio)
            correct = score >= int(question.score * 0.7)
        return QuestionGradeResult(
            questionId=question.id,
            score=score,
            maxScore=question.score,
            correct=correct,
            feedback=self._question_feedback(question, correct, score),
            knowledgePoint=question.knowledgePoints[0] if question.knowledgePoints else question.type,
        )

    def _question_feedback(self, question: AssessmentQuestion, correct: bool, score: int) -> str:
        if correct:
            return f"掌握较好，得分 {score}/{question.score}。建议继续做迁移题。"
        return f"该题暴露 `{question.knowledgePoints[0] if question.knowledgePoints else question.type}` 薄弱点：{question.explanation}"

    def _mastery_level(self, ratio: float) -> str:
        if ratio >= 0.85:
            return "掌握稳定"
        if ratio >= 0.65:
            return "基本掌握"
        if ratio >= 0.4:
            return "部分掌握"
        return "需要补救"

    def _feedback(self, topic: str, ratio: float, weak_points: list[str]) -> str:
        return (
            f"`{topic}` 当前测评正确率约 {ratio:.0%}。"
            f"主要需要关注：{'、'.join(dict.fromkeys(weak_points))}。"
        )

    def _next_resources(self, ratio: float) -> list[str]:
        if ratio >= 0.85:
            return ["高阶项目实训", "拓展阅读", "同伴讲解任务"]
        if ratio >= 0.65:
            return ["代码/项目实操案例", "分层练习题", "错题复盘卡"]
        return ["专业课程讲解文档", "知识点思维导图", "短视频讲解脚本", "基础补救练习"]

    def _profile_updates(
        self,
        request: AssessmentGradeRequest,
        mastery: str,
        feedback: str,
        weak_points: list[str],
        ratio: float,
    ) -> list[ProfileDimensionUpdate]:
        confidence = min(0.92, max(0.62, 0.55 + ratio * 0.35))
        return [
            ProfileDimensionUpdate(
                dimensionKey="MASTERY_WEAKNESS",
                dimensionName="掌握度/薄弱点",
                value=f"{request.topic}：{mastery}；薄弱点：{'、'.join(dict.fromkeys(weak_points))}",
                evidence=feedback,
                confidenceScore=round(confidence, 2),
                source="assessment_agent",
            ),
            ProfileDimensionUpdate(
                dimensionKey="ERROR_PRONE_POINTS",
                dimensionName="易错点",
                value=f"{request.topic} 测评暴露的问题集中在：{'、'.join(dict.fromkeys(weak_points))}",
                evidence=feedback,
                confidenceScore=round(confidence, 2),
                source="assessment_agent",
            ),
        ]

