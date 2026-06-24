from learning_agent.config import AgentSettings
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.llm import ProviderRouter
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
from learning_agent.structured_output import as_float, as_int, as_list, as_text, complete_json
from learning_agent.vector_store import InMemoryVectorStore


class AssessmentAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store
        self.embedding_model = HashingEmbeddingModel(settings.embedding_dimensions)
        self.provider_router = ProviderRouter(settings)

    def generate(self, request: AssessmentGenerateRequest) -> AssessmentGenerateResponse:
        citations = self.vector_store.search(self._query(request), top_k=self.settings.retrieval_top_k)
        generated = self._llm_generate(request, citations)
        return self._generate_response_from_model(request, citations, generated)
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
        graded = self._llm_grade(request)
        return self._grade_response_from_model(request, graded)
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

    def _llm_generate(
        self,
        request: AssessmentGenerateRequest,
        citations: list[KnowledgeMatch],
    ) -> dict:
        context = "\n\n".join(
            f"[{index}] {match.title} ({match.source}, score={match.score}): {compact(match.text, 650)}"
            for index, match in enumerate(citations[:6], start=1)
        )
        system_prompt = (
            "You are an assessment design agent for a Chinese personalized learning product. "
            "Create grounded assessment items that test understanding, transfer, and practice. "
            "Return strict JSON only."
        )
        user_prompt = f"""
Return one JSON object in Chinese with this shape:
{{
  "title": "string",
  "summary": "string",
  "questions": [
    {{
      "id": "q1",
      "type": "选择题/判断题/简答题/代码纠错题/etc",
      "stem": "question text",
      "options": ["A. ...", "B. ..."],
      "answer": "standard answer",
      "rubric": "grading rubric",
      "explanation": "evidence-grounded explanation",
      "difficulty": "string",
      "knowledgePoints": ["string"],
      "score": 10
    }}
  ]
}}

Constraints:
- Generate exactly {request.count} questions.
- Follow requested question types when possible: {request.questionTypes}.
- Each question must reference the course/topic and be gradeable.
- Include at least one transfer/practice-oriented item when count >= 3.
- Do not invent unsupported outside facts.

Course: {request.courseTitle}
Topic: {request.topic}
Difficulty: {request.difficulty}
Learner profile: {request.studentProfileSummary}
Retrieved evidence:
{context or "No retrieved evidence."}
"""
        return complete_json(self.provider_router, system_prompt, user_prompt, "assessment generation")

    def _generate_response_from_model(
        self,
        request: AssessmentGenerateRequest,
        citations: list[KnowledgeMatch],
        generated: dict,
    ) -> AssessmentGenerateResponse:
        questions = self._questions_from_model(request, generated)
        if len(questions) < request.count:
            raise RuntimeError(f"Assessment agent returned {len(questions)} questions, expected {request.count}.")
        return AssessmentGenerateResponse(
            title=as_text(generated.get("title"), f"{request.topic} 自适应测评"),
            topic=request.topic,
            questions=questions[:request.count],
            citations=citations,
            summary=as_text(generated.get("summary"), f"已基于画像和 RAG 证据生成 {len(questions[:request.count])} 道测评题。"),
        )

    def _questions_from_model(
        self,
        request: AssessmentGenerateRequest,
        generated: dict,
    ) -> list[AssessmentQuestion]:
        items = [item for item in as_list(generated.get("questions")) if isinstance(item, dict)]
        questions: list[AssessmentQuestion] = []
        for index, item in enumerate(items, start=1):
            qid = as_text(item.get("id"), f"q{index}")
            question_type = as_text(
                item.get("type"),
                request.questionTypes[(index - 1) % len(request.questionTypes)] if request.questionTypes else "简答题",
            )
            questions.append(AssessmentQuestion(
                id=qid,
                type=question_type,
                stem=as_text(item.get("stem"), f"请说明 {request.topic} 的关键概念与应用场景。"),
                options=self._normalized_strings(item.get("options")),
                answer=as_text(item.get("answer"), "需覆盖关键概念、依据和应用场景。"),
                rubric=as_text(item.get("rubric"), "按概念准确性、证据引用、应用迁移和表达完整度评分。"),
                explanation=as_text(item.get("explanation"), "该题用于检查学习者是否能把知识点迁移到真实任务。"),
                difficulty=as_text(item.get("difficulty"), request.difficulty),
                knowledgePoints=self._normalized_strings(item.get("knowledgePoints")) or [request.topic],
                score=as_int(item.get("score"), 10, 1, 100),
            ))
        return questions

    def _llm_grade(self, request: AssessmentGradeRequest) -> dict:
        questions = [
            {
                "id": question.id,
                "type": question.type,
                "stem": question.stem,
                "answer": question.answer,
                "rubric": question.rubric,
                "score": question.score,
                "knowledgePoints": question.knowledgePoints,
            }
            for question in request.questions
        ]
        answers = [{"questionId": answer.questionId, "answer": answer.answer} for answer in request.answers]
        system_prompt = (
            "You are an evidence-based assessment grading agent. Grade strictly against the provided standard answers "
            "and rubrics. Return strict JSON only."
        )
        user_prompt = f"""
Return one JSON object in Chinese with this shape:
{{
  "masteryLevel": "string",
  "feedback": "overall feedback",
  "questionResults": [
    {{"questionId": "q1", "score": 0, "maxScore": 10, "correct": false, "feedback": "string", "knowledgePoint": "string"}}
  ],
  "weaknessSignals": ["string"],
  "nextResourceTypes": ["string"],
  "profileDimensionUpdates": [
    {{"dimensionKey": "MASTERY_WEAKNESS", "dimensionName": "掌握度/薄弱点", "value": "string", "evidence": "string", "confidenceScore": 0.8, "source": "assessment_agent"}}
  ]
}}

Constraints:
- Produce one questionResult for every question.
- Scores must be integers from 0 to maxScore.
- Do not reward answers that do not address the rubric.
- Highlight actionable weaknesses and next resource types.

Course: {request.courseTitle}
Topic: {request.topic}
Learner profile: {request.studentProfileSummary}
Questions:
{questions}
Student answers:
{answers}
"""
        return complete_json(self.provider_router, system_prompt, user_prompt, "assessment grading")

    def _grade_response_from_model(
        self,
        request: AssessmentGradeRequest,
        graded: dict,
    ) -> AssessmentGradeResponse:
        expected = {question.id: question for question in request.questions}
        result_items = [item for item in as_list(graded.get("questionResults")) if isinstance(item, dict)]
        results: list[QuestionGradeResult] = []
        for item in result_items:
            question_id = as_text(item.get("questionId"))
            if question_id not in expected:
                continue
            question = expected[question_id]
            max_score = as_int(item.get("maxScore"), question.score, 1, question.score)
            score = as_int(item.get("score"), 0, 0, max_score)
            results.append(QuestionGradeResult(
                questionId=question_id,
                score=score,
                maxScore=max_score,
                correct=bool(item.get("correct")) and score >= int(max_score * 0.7),
                feedback=as_text(item.get("feedback"), "已按标准答案和评分规则完成批改。"),
                knowledgePoint=as_text(
                    item.get("knowledgePoint"),
                    question.knowledgePoints[0] if question.knowledgePoints else request.topic,
                ),
            ))
        missing = sorted(set(expected) - {result.questionId for result in results})
        if missing:
            raise RuntimeError(f"Assessment grader missed question results for: {', '.join(missing)}")
        score = sum(result.score for result in results)
        max_score = sum(result.maxScore for result in results) or 1
        weakness_signals = self._normalized_strings(graded.get("weaknessSignals")) or [
            result.knowledgePoint for result in results if not result.correct
        ]
        return AssessmentGradeResponse(
            score=score,
            maxScore=max_score,
            masteryLevel=as_text(graded.get("masteryLevel"), self._mastery_level(score / max_score)),
            feedback=as_text(graded.get("feedback"), self._feedback(request.topic, score / max_score, weakness_signals)),
            questionResults=results,
            weaknessSignals=weakness_signals or ["暂未发现明显薄弱点"],
            nextResourceTypes=self._normalized_strings(graded.get("nextResourceTypes")) or self._next_resources(score / max_score),
            profileDimensionUpdates=self._profile_updates_from_model(request, graded, weakness_signals, score, max_score),
        )

    def _profile_updates_from_model(
        self,
        request: AssessmentGradeRequest,
        graded: dict,
        weakness_signals: list[str],
        score: int,
        max_score: int,
    ) -> list[ProfileDimensionUpdate]:
        items = [item for item in as_list(graded.get("profileDimensionUpdates")) if isinstance(item, dict)]
        updates: list[ProfileDimensionUpdate] = []
        for item in items[:4]:
            updates.append(ProfileDimensionUpdate(
                dimensionKey=as_text(item.get("dimensionKey"), "MASTERY_WEAKNESS"),
                dimensionName=as_text(item.get("dimensionName"), "掌握度/薄弱点"),
                value=as_text(item.get("value"), "；".join(weakness_signals) or "测评表现稳定"),
                evidence=as_text(item.get("evidence"), f"{request.topic} 测评得分 {score}/{max_score}"),
                confidenceScore=as_float(item.get("confidenceScore"), 0.78, 0.0, 1.0),
                source=as_text(item.get("source"), "assessment_agent"),
            ))
        if updates:
            return updates
        return [ProfileDimensionUpdate(
            dimensionKey="MASTERY_WEAKNESS",
            dimensionName="掌握度/薄弱点",
            value="；".join(weakness_signals) or "测评表现稳定",
            evidence=f"{request.topic} 测评得分 {score}/{max_score}",
            confidenceScore=0.78,
            source="assessment_agent",
        )]

    def _normalized_strings(self, value: object) -> list[str]:
        return [as_text(item) for item in as_list(value) if as_text(item)]

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
