from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from learning_agent.config import AgentSettings
from learning_agent.resource_templates import compact
from learning_agent.schemas import (
    AgentCallRecommendation,
    AgentRunRecordRequest,
    AgentRunRecordResponse,
    CourseCoverageGap,
    CourseCoverageRadarItem,
    CourseCoverageRequest,
    CourseCoverageResponse,
    DefenseFeatureMatrixItem,
    DefensePackRequest,
    DefensePackResponse,
    DefenseQAItem,
    ErrorBookRequest,
    ErrorBookResponse,
    ErrorCluster,
    ExtractedQuestion,
    GraphRagPathStep,
    GraphRagQueryRequest,
    GraphRagQueryResponse,
    HumanReviewDecision,
    HumanReviewRequest,
    HumanReviewResponse,
    KnowledgeMatch,
    OcrQuestionRequest,
    OcrQuestionResponse,
    ProfileDimensionUpdate,
    RagEvaluationRequest,
    RagEvaluationResponse,
    RagMetricScore,
    ReviewScheduleItem,
    VoicePackageRequest,
    VoicePackageResponse,
    VoiceSegment,
)
from learning_agent.vector_store import InMemoryVectorStore


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[\w\u4e00-\u9fff]+", text) if len(token.strip()) > 1}


def _overlap(left: str, right: str) -> float:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens:
        return 0.0
    return min(1.0, len(left_tokens & right_tokens) / len(left_tokens))


def _score_to_level(score: int) -> str:
    if score >= 85:
        return "低风险"
    if score >= 70:
        return "中风险"
    return "高风险"


def _knowledge_points(text: str) -> list[str]:
    candidates = [
        "RAG", "Embedding", "LangGraph", "LangChain", "REST API", "Spring Boot", "Controller",
        "Service", "Repository", "SQL", "数据库", "向量检索", "知识图谱", "防幻觉", "学习画像",
        "测评", "错题", "多模态", "OCR", "语音合成", "代码审查",
    ]
    points = [item for item in candidates if item.lower() in text.lower()]
    if not points:
        words = [token for token, _count in Counter(_tokens(text)).most_common(5)]
        points = words[:3] or ["课程核心概念"]
    return points[:8]


class RagEvaluationAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def evaluate(self, request: RagEvaluationRequest) -> RagEvaluationResponse:
        citations = request.citations or self.vector_store.search(
            self._query(request),
            top_k=request.topK,
        )
        contexts = request.contexts or [item.text for item in citations]
        context_text = "\n".join(contexts)
        expected = request.expectedAnswer or request.question

        unsupported = self._unsupported_claims(request.answer, context_text)
        faithfulness = max(0.0, 1 - len(unsupported) / max(1, len(self._sentences(request.answer))))
        answer_relevancy = max(_overlap(request.question, request.answer), _overlap(request.answer, request.question))
        context_precision = self._context_precision(request.question, contexts)
        context_recall = max(_overlap(expected, context_text), _overlap(request.answer, context_text))
        groundedness = _overlap(request.answer, context_text)
        citation_coverage = min(1.0, len(citations) / max(3, request.topK))
        metric_values = {
            "faithfulness": faithfulness,
            "answerRelevancy": answer_relevancy,
            "contextPrecision": context_precision,
            "contextRecall": context_recall,
            "groundedness": groundedness,
            "citationCoverage": citation_coverage,
        }
        overall = round(sum(metric_values.values()) / len(metric_values) * 100)
        breakdown = [
            RagMetricScore(
                name=name,
                score=round(value, 3),
                evidence=self._metric_evidence(name, value, citations, unsupported),
                recommendation=self._metric_recommendation(name, value),
            )
            for name, value in metric_values.items()
        ]
        improvement_actions = [
            item.recommendation
            for item in breakdown
            if item.score < 0.72
        ][:6]
        if not improvement_actions:
            improvement_actions = ["当前回答具备较好的引用支撑，可进入教师审核或发布环节。"]
        return RagEvaluationResponse(
            overallScore=overall,
            faithfulness=round(faithfulness, 3),
            answerRelevancy=round(answer_relevancy, 3),
            contextPrecision=round(context_precision, 3),
            contextRecall=round(context_recall, 3),
            groundedness=round(groundedness, 3),
            citationCoverage=round(citation_coverage, 3),
            metricBreakdown=breakdown,
            unsupportedClaims=unsupported[:8],
            improvementActions=improvement_actions,
            citations=citations,
            summary=f"RAG 质量评测完成：总体 {overall}/100，风险等级 `{_score_to_level(overall)}`。",
        )

    def _query(self, request: RagEvaluationRequest) -> str:
        return "\n".join([request.courseTitle, request.question, request.answer, request.expectedAnswer])

    def _sentences(self, text: str) -> list[str]:
        return [item.strip() for item in re.split(r"[。！？.!?\n]+", text) if item.strip()]

    def _unsupported_claims(self, answer: str, context_text: str) -> list[str]:
        unsupported: list[str] = []
        for sentence in self._sentences(answer):
            if len(sentence) < 8:
                continue
            if _overlap(sentence, context_text) < 0.18 and any(token in sentence for token in ["一定", "全部", "唯一", "最佳", "必须", "证明", "不会"]):
                unsupported.append(sentence)
        return unsupported

    def _context_precision(self, query: str, contexts: list[str]) -> float:
        if not contexts:
            return 0.0
        scores = [_overlap(query, context) for context in contexts[:8]]
        return sum(scores) / len(scores)

    def _metric_evidence(
        self,
        name: str,
        value: float,
        citations: list[KnowledgeMatch],
        unsupported: list[str],
    ) -> str:
        if name == "faithfulness" and unsupported:
            return f"发现 {len(unsupported)} 个可能缺少依据的断言。"
        if citations:
            return f"评测关联 {len(citations)} 条引用，最高相似度 {citations[0].score}。"
        return "未提供或检索到足够引用。"

    def _metric_recommendation(self, name: str, value: float) -> str:
        if value >= 0.72:
            return f"{name} 达到演示阈值，保留当前证据。"
        mapping = {
            "faithfulness": "删除绝对化表述，补充每个结论对应的课程资料引用。",
            "answerRelevancy": "重写回答开头，直接回应学生问题和薄弱点。",
            "contextPrecision": "缩小检索 query，加入课程、章节、知识点过滤条件。",
            "contextRecall": "补充更多课程文档或把教师讲义作为 documentTexts 导入。",
            "groundedness": "把答案拆成带引用的短段落，避免长段自由发挥。",
            "citationCoverage": "前端必须展示 citations，并要求至少 3 条可展开依据。",
        }
        return mapping.get(name, "补充证据并重新生成。")


class AgentRunStore:
    def __init__(self, settings: AgentSettings) -> None:
        self.path = settings.project_root / "agents" / "resource-agent" / "data" / "agent_runs.jsonl"

    def record(self, request: AgentRunRecordRequest) -> AgentRunRecordResponse:
        run_id = request.runId or f"run-{uuid4().hex[:12]}"
        created_at = datetime.now(timezone.utc)
        record = request.model_dump(mode="json")
        record.update({
            "runId": run_id,
            "createdAt": created_at.isoformat(),
        })
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return self._response(record)

    def get(self, run_id: str) -> AgentRunRecordResponse | None:
        for record in reversed(self._records()):
            if record.get("runId") == run_id:
                return self._response(record)
        return None

    def recent(self, limit: int = 20) -> list[AgentRunRecordResponse]:
        return [self._response(record) for record in self._records()[-limit:]][::-1]

    def _records(self) -> list[dict]:
        if not self.path.exists():
            return []
        records = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    records.append(json.loads(line))
        return records

    def _response(self, record: dict) -> AgentRunRecordResponse:
        gates = [
            f"{gate.get('name', 'gate')}={gate.get('status', 'unknown')}"
            for gate in record.get("qualityGates", [])
        ]
        steps = record.get("steps", [])
        replay_lines = [
            f"# {record.get('taskName', 'Agent Run')}",
            f"- runId: `{record.get('runId')}`",
            f"- endpoint: `{record.get('endpoint', '')}`",
            f"- provider: `{record.get('provider', '')}`; fallback={record.get('fallbackUsed', False)}",
        ]
        for step in steps:
            replay_lines.append(
                f"- Step {step.get('order')}: {step.get('agentName')} -> {compact(str(step.get('outputSummary', '')), 120)}"
            )
        return AgentRunRecordResponse(
            runId=str(record.get("runId", "")),
            taskName=str(record.get("taskName", "")),
            endpoint=str(record.get("endpoint", "")),
            createdAt=datetime.fromisoformat(str(record.get("createdAt"))),
            provider=str(record.get("provider", "")),
            fallbackUsed=bool(record.get("fallbackUsed", False)),
            stepCount=len(steps),
            qualityGateSummary=gates,
            replayMarkdown="\n".join(replay_lines),
            record=record,
        )


class HumanReviewAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def review(self, request: HumanReviewRequest) -> HumanReviewResponse:
        citations = request.citations or self.vector_store.search(
            f"{request.courseTitle} {request.resourceTitle} {request.content[:500]}",
            top_k=self.settings.retrieval_top_k,
        )
        risk_reasons = self._risk_reasons(request, citations)
        score = max(0.0, 1 - len(risk_reasons) * 0.18)
        needs_review = bool(risk_reasons) or len(citations) < 2
        decision = HumanReviewDecision(
            autoApproved=not needs_review and score >= 0.82,
            needsTeacherReview=needs_review,
            riskLevel=_score_to_level(round(score * 100)),
            confidenceScore=round(score, 2),
        )
        suggestions = self._suggestions(risk_reasons)
        return HumanReviewResponse(
            decision=decision,
            riskReasons=risk_reasons,
            revisionSuggestions=suggestions,
            publishChecklist=self._checklist(request, citations),
            requiredReviewerRoles=self._roles(risk_reasons),
            citations=citations,
            summary=f"`{request.resourceTitle}` 人审预检完成：{decision.riskLevel}，需要教师审核={decision.needsTeacherReview}。",
        )

    def _risk_reasons(self, request: HumanReviewRequest, citations: list[KnowledgeMatch]) -> list[str]:
        content = request.content
        reasons = []
        if len(citations) < 2:
            reasons.append("引用依据不足，前端发布前需要补充可展开 citations。")
        if re.search(r"100%|一定|绝对|唯一|永远|保证", content):
            reasons.append("存在绝对化表述，可能引发防幻觉或过度承诺风险。")
        if re.search(r"密钥|token|password|api_secret", content, re.I):
            reasons.append("内容疑似包含敏感配置或密钥字段。")
        if len(content.strip()) < 80:
            reasons.append("资源内容过短，难以支撑完整学习目标。")
        if request.rubric and not any(_overlap(item, content) > 0.15 for item in request.rubric):
            reasons.append("内容与教师审核 rubric 对齐度不足。")
        return reasons

    def _suggestions(self, risk_reasons: list[str]) -> list[str]:
        if not risk_reasons:
            return ["保持引用区、学习目标和测评闭环，允许教师一键发布。"]
        return [
            "为每个核心结论追加课程资料引用或上传教师讲义。",
            "把绝对化结论改为有条件、可验证的表述。",
            "发布前调用 `/agents/safety/audit` 和 `/agents/evaluation/rag-quality` 复核。",
            "让教师在前端审核页确认适用对象、难度和课时安排。",
        ]

    def _checklist(self, request: HumanReviewRequest, citations: list[KnowledgeMatch]) -> list[str]:
        return [
            f"确认资源标题 `{request.resourceTitle}` 与课程 `{request.courseTitle or '未指定课程'}` 匹配。",
            f"确认目标对象 `{request.targetAudience}` 能理解当前难度。",
            f"确认 citations 可展开，当前 {len(citations)} 条。",
            "确认无敏感信息、无事实性硬伤、无未经证据支撑的绝对化结论。",
            "确认后续练习、答疑或测评入口已经配置。",
        ]

    def _roles(self, risk_reasons: list[str]) -> list[str]:
        roles = ["任课教师"]
        if any("敏感" in item for item in risk_reasons):
            roles.append("系统管理员")
        if any("引用" in item or "幻觉" in item for item in risk_reasons):
            roles.append("课程负责人")
        return roles


class VoicePackageAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def build(self, request: VoicePackageRequest) -> VoicePackageResponse:
        citations = self.vector_store.search(
            f"{request.courseTitle} {request.topic} {request.script[:400]}",
            top_k=self.settings.retrieval_top_k,
        )
        sentences = [item.strip() for item in re.split(r"[。！？.!?\n]+", request.script) if item.strip()]
        if not sentences:
            sentences = [f"围绕 {request.topic} 进行课程讲解。"]
        target_seconds = request.targetDurationMinutes * 60
        selected = sentences[:10]
        per_segment = max(12, target_seconds // max(1, len(selected)))
        segments: list[VoiceSegment] = []
        current = 0
        for index, sentence in enumerate(selected, start=1):
            end = min(target_seconds, current + per_segment)
            segments.append(VoiceSegment(
                order=index,
                startSecond=current,
                endSecond=end,
                narration=sentence,
                subtitle=compact(sentence, 80),
                visualCue=f"展示 `{request.topic}` 的第 {index} 个关键画面或板书。",
            ))
            current = end
            if current >= target_seconds:
                break
        subtitle = self._srt(segments)
        return VoicePackageResponse(
            packageTitle=f"{request.topic} 语音讲解包",
            estimatedDurationSeconds=segments[-1].endSecond if segments else target_seconds,
            voiceConfig={
                "provider": "xfyun_tts_ready",
                "voiceStyle": request.voiceStyle,
                "speed": 50,
                "volume": 70,
                "pitch": 50,
                "format": "mp3",
            },
            segments=segments,
            subtitleSrt=subtitle,
            productionChecklist=[
                "调用讯飞语音合成前确认 XFYUN_APP_ID/APIKey/APISecret 或 APIPassword 已配置。",
                "前端播放时同步展示 subtitleSrt，便于无声环境演示。",
                "视频脚本与 storyboard 的 sceneNo 对齐，避免素材错位。",
                "保留离线旁白文本，TTS 失败时仍可演示。",
            ],
            citations=citations,
            summary=f"`{request.topic}` 已生成 {len(segments)} 段旁白和 SRT 字幕，可对接讯飞 TTS。",
        )

    def _srt(self, segments: list[VoiceSegment]) -> str:
        lines = []
        for segment in segments:
            lines.extend([
                str(segment.order),
                f"{self._fmt(segment.startSecond)} --> {self._fmt(segment.endSecond)}",
                segment.subtitle,
                "",
            ])
        return "\n".join(lines).strip()

    def _fmt(self, second: int) -> str:
        minutes, seconds = divmod(second, 60)
        return f"00:{minutes:02d}:{seconds:02d},000"


class OcrQuestionAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def extract(self, request: OcrQuestionRequest) -> OcrQuestionResponse:
        text = request.ocrText.strip() or f"图片 `{request.imageName or '未命名图片'}` 待 OCR，当前使用占位文本。"
        citations = self.vector_store.search(
            f"{request.courseTitle} {text[:500]}",
            top_k=self.settings.retrieval_top_k,
        )
        questions = self._questions(text)
        points = sorted({point for question in questions for point in question.knowledgePoints}) or _knowledge_points(text)
        calls = [
            AgentCallRecommendation(
                priority=1,
                agentEndpoint="/agents/tutoring",
                reason="对 OCR 题目生成可引用解题讲解。",
                payloadHint={"question": questions[0].stem if questions else text[:80]},
            ),
            AgentCallRecommendation(
                priority=2,
                agentEndpoint="/agents/assessment/item-analysis",
                reason="把题目写入题目质量和误区聚类分析。",
                payloadHint={"knowledgePoints": points},
            ),
        ]
        return OcrQuestionResponse(
            extractedText=text,
            questions=questions,
            detectedKnowledgePoints=points,
            nextAgentCalls=calls,
            citations=citations,
            summary=f"OCR 题目解析完成：识别 {len(questions)} 道题，知识点 {', '.join(points[:4])}。",
        )

    def _questions(self, text: str) -> list[ExtractedQuestion]:
        blocks = [item.strip() for item in re.split(r"\n\s*\n|(?=\d+[.、])", text) if item.strip()]
        if not blocks:
            blocks = [text]
        questions = []
        for index, block in enumerate(blocks[:6], start=1):
            options = re.findall(r"[A-D][.、)]\s*([^\n]+)", block)
            stem = re.sub(r"[A-D][.、)]\s*[^\n]+", "", block).strip()
            points = _knowledge_points(block)
            questions.append(ExtractedQuestion(
                id=f"ocr-q{index}",
                questionType="选择题" if options else "主观题",
                stem=compact(stem or block, 180),
                options=options[:4],
                knowledgePoints=points,
                solutionSteps=[
                    f"定位题干中的核心知识点：{', '.join(points[:3])}。",
                    "回到课程资料或 RAG 引用中查找定义、边界和例子。",
                    "给出答案后追加错因提示，便于写入错题本。",
                ],
                confidenceScore=0.82 if options or "?" in block or "？" in block else 0.68,
            ))
        return questions


class GraphRagQueryAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def query(self, request: GraphRagQueryRequest) -> GraphRagQueryResponse:
        citations = self.vector_store.search(
            " ".join([request.courseTitle, request.query, *request.weaknessSignals]),
            top_k=max(8, self.settings.retrieval_top_k),
        )
        text = "\n".join([request.query, *request.weaknessSignals, *(item.text for item in citations[:4])])
        concepts = _knowledge_points(text)
        steps = [
            GraphRagPathStep(
                order=index,
                concept=concept,
                relation="相关/先修/应用" if index > 1 else "查询入口",
                evidence=compact(citations[(index - 1) % len(citations)].text, 140) if citations else request.query,
            )
            for index, concept in enumerate(concepts[:8], start=1)
        ]
        answer = self._answer_outline(request, concepts, citations)
        confidence = min(0.95, 0.45 + len(citations) * 0.05 + len(concepts) * 0.03)
        return GraphRagQueryResponse(
            answerOutline=answer,
            queryMode=request.mode,
            expandedConcepts=concepts,
            retrievalPath=steps,
            localCitations=citations[:6],
            globalSummary=self._global_summary(concepts, citations),
            confidenceScore=round(confidence, 2),
            followUpQueries=[f"{concept} 的先修知识是什么？" for concept in concepts[:3]],
            summary=f"GraphRAG 查询完成：{request.mode} 模式，扩展 {len(concepts)} 个概念，返回 {len(citations)} 条证据。",
        )

    def _answer_outline(
        self,
        request: GraphRagQueryRequest,
        concepts: list[str],
        citations: list[KnowledgeMatch],
    ) -> str:
        evidence = compact(citations[0].text, 220) if citations else "当前知识库缺少强相关资料。"
        return (
            f"问题：{request.query}\n"
            f"核心概念：{', '.join(concepts[:5])}\n"
            f"回答路径：先解释入口概念，再说明先修关系，最后给出学习或实践动作。\n"
            f"关键证据：{evidence}"
        )

    def _global_summary(self, concepts: list[str], citations: list[KnowledgeMatch]) -> str:
        titles = [item.title for item in citations[:4]]
        return f"全局视角覆盖 {', '.join(concepts[:5])}；证据来源包括 {', '.join(titles) if titles else '待补充课程资料'}。"


class ErrorBookAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def analyze(self, request: ErrorBookRequest) -> ErrorBookResponse:
        citations = self.vector_store.search(
            f"{request.courseTitle} {request.topic} {' '.join(item.knowledgePoint for item in request.attempts)}",
            top_k=self.settings.retrieval_top_k,
        )
        wrong = [item for item in request.attempts if not item.correct or item.score < item.maxScore * 0.7]
        grouped: dict[str, list] = defaultdict(list)
        for attempt in wrong:
            grouped[attempt.knowledgePoint].append(attempt)
        clusters = [
            ErrorCluster(
                name=f"{point} 易错簇",
                questionIds=[item.questionId for item in items],
                knowledgePoints=[point],
                rootCause=self._root_cause(items),
                correctionStrategy=f"先复习 `{point}` 的定义和边界，再完成 2 道变式题和 1 次口头复述。",
                priority=index,
            )
            for index, (point, items) in enumerate(sorted(grouped.items(), key=lambda item: len(item[1]), reverse=True), start=1)
        ]
        if not clusters:
            clusters = [ErrorCluster(
                name="保持巩固",
                questionIds=[],
                knowledgePoints=request.recentWeaknesses[:2] or ["综合应用"],
                rootCause="近期错题较少，主要风险是遗忘。",
                correctionStrategy="安排间隔复习和综合题保持稳定。",
                priority=1,
            )]
        schedule = self._schedule(clusters)
        updates = [
            ProfileDimensionUpdate(
                dimensionKey="ERROR_BOOK_FOCUS",
                dimensionName="错题本重点",
                value=", ".join(cluster.name for cluster in clusters[:3]),
                evidence=f"分析 {len(request.attempts)} 次作答记录，其中 {len(wrong)} 条需要复盘。",
                confidenceScore=0.82,
                source="error_book_agent",
            )
        ]
        return ErrorBookResponse(
            errorBookTitle=f"{request.courseTitle} - {request.topic}",
            masteryTrend=self._trend(request.attempts),
            errorClusters=clusters,
            reviewSchedule=schedule,
            personalizedRemediation=[cluster.correctionStrategy for cluster in clusters[:5]],
            nextAssessmentPlan=[
                "下一轮测评错题知识点占 60%，相邻知识点迁移题占 30%，综合应用题占 10%。",
                "连续两次正确后降低复习频率，仍错误则调用 `/agents/resources/curate` 生成补救包。",
            ],
            citations=citations,
            profileDimensionUpdates=updates,
            summary=f"错题本分析完成：形成 {len(clusters)} 个易错簇，趋势 `{self._trend(request.attempts)}`。",
        )

    def _root_cause(self, attempts: list) -> str:
        text = " ".join(f"{item.answerSummary} {item.feedback}" for item in attempts)
        if "概念" in text or "定义" in text:
            return "概念边界不清。"
        if "代码" in text or "实现" in text:
            return "能理解概念，但工程实现迁移不足。"
        return "题型识别和关键条件提取不稳定。"

    def _trend(self, attempts: list) -> str:
        if not attempts:
            return "数据不足"
        avg = sum(item.score / item.maxScore for item in attempts) / len(attempts)
        if avg >= 0.85:
            return "稳定提升"
        if avg >= 0.65:
            return "波动巩固"
        return "需要集中补救"

    def _schedule(self, clusters: list[ErrorCluster]) -> list[ReviewScheduleItem]:
        offsets = [1, 3, 7, 14]
        schedule = []
        for index, cluster in enumerate(clusters[:4]):
            point = cluster.knowledgePoints[0] if cluster.knowledgePoints else "综合应用"
            schedule.append(ReviewScheduleItem(
                dayOffset=offsets[index],
                task=f"复盘 `{cluster.name}` 并完成 2 道变式题。",
                targetKnowledgePoint=point,
                successCriteria="能说清错因，并在同类题中达到 80% 以上正确率。",
            ))
        return schedule


class CourseCoverageAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def analyze(self, request: CourseCoverageRequest) -> CourseCoverageResponse:
        citations = self.vector_store.search(
            f"{request.courseTitle} {' '.join(request.chapters)}",
            top_k=max(8, self.settings.retrieval_top_k),
        )
        resource_map = self._coverage_map(request.resourceInventory)
        assessment_map = self._coverage_map(request.assessmentInventory)
        chapters = request.chapters or _knowledge_points(" ".join(item.text for item in citations[:4]))
        resource_scores = []
        assessment_scores = []
        gaps = []
        for chapter in chapters:
            resources = resource_map.get(chapter, set())
            assessments = assessment_map.get(chapter, set())
            resource_score = min(100, round(len(resources) / max(1, len(request.targetResourceTypes)) * 100))
            assessment_score = min(100, round(len(assessments) / 3 * 100))
            resource_scores.append(resource_score)
            assessment_scores.append(assessment_score)
            missing_resources = [item for item in request.targetResourceTypes if item not in resources]
            missing_assessments = [item for item in ["选择题", "主观题", "代码题"] if item not in assessments]
            if missing_resources or missing_assessments:
                gaps.append(CourseCoverageGap(
                    knowledgePoint=chapter,
                    missingResourceTypes=missing_resources[:5],
                    missingAssessmentTypes=missing_assessments[:3],
                    severity="高" if resource_score < 40 or assessment_score < 40 else "中",
                    suggestedAgent="/agents/resources/curate" if missing_resources else "/agents/assessment/generate",
                ))
        resource_avg = round(sum(resource_scores) / max(1, len(resource_scores)))
        assessment_avg = round(sum(assessment_scores) / max(1, len(assessment_scores)))
        radar = [
            CourseCoverageRadarItem(dimension="资源类型覆盖", score=resource_avg, evidence=f"目标资源类型 {len(request.targetResourceTypes)} 类。"),
            CourseCoverageRadarItem(dimension="测评题型覆盖", score=assessment_avg, evidence="按选择题、主观题、代码题三类估算。"),
            CourseCoverageRadarItem(dimension="RAG 资料支撑", score=min(100, len(citations) * 12), evidence=f"检索到 {len(citations)} 条课程证据。"),
            CourseCoverageRadarItem(dimension="课程建设闭环", score=75 if request.resourceInventory and request.assessmentInventory else 45, evidence="同时检查资源和测评库存。"),
        ]
        return CourseCoverageResponse(
            courseId=request.courseId,
            courseTitle=request.courseTitle,
            resourceCoverageScore=resource_avg,
            assessmentCoverageScore=assessment_avg,
            coverageRadar=radar,
            gaps=gaps[:12],
            buildPlan=self._build_plan(gaps),
            citations=citations,
            summary=f"`{request.courseTitle}` 覆盖率分析完成：资源 {resource_avg}/100，测评 {assessment_avg}/100，发现 {len(gaps)} 个缺口。",
        )

    def _coverage_map(self, items: list) -> dict[str, set[str]]:
        result: dict[str, set[str]] = defaultdict(set)
        for item in items:
            item_type = getattr(item, "resourceType", getattr(item, "questionType", "未知"))
            for point in item.knowledgePoints:
                result[point].add(item_type)
        return result

    def _build_plan(self, gaps: list[CourseCoverageGap]) -> list[str]:
        if not gaps:
            return ["课程资源和测评覆盖较完整，下一步做质量评测和学生效果回流。"]
        return [
            f"优先补齐 `{gap.knowledgePoint}`：缺资源 {', '.join(gap.missingResourceTypes) or '无'}；缺测评 {', '.join(gap.missingAssessmentTypes) or '无'}。"
            for gap in gaps[:6]
        ]


class DefensePackAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def build(self, request: DefensePackRequest) -> DefensePackResponse:
        citations = self.vector_store.search(
            f"{request.projectName} {request.competitionTrack} {' '.join(request.implementedFeatures)} {' '.join(request.techStack)}",
            top_k=max(8, self.settings.retrieval_top_k),
        )
        features = request.implementedFeatures or [
            "对话式学习画像", "RAG 个性化资源生成", "自适应测评", "防幻觉审计", "教师端班级分析",
        ]
        matrix = self._matrix(features)
        qa_pairs = self._qa(request, citations)
        return DefensePackResponse(
            packTitle=f"{request.projectName} 答辩材料包",
            openingScript=(
                f"我们项目面向 {request.competitionTrack}，核心不是单次聊天生成，而是把画像、RAG、资源、测评、"
                "错题、班级分析和可追踪审计串成可复现的学习闭环。"
            ),
            featureMatrix=matrix,
            qaPairs=qa_pairs,
            apiChecklist=self._api_checklist(request),
            openSourceNotes=[
                "提交文档显著列出 LangGraph/LangChain/FastAPI/Pydantic/httpx 等依赖及许可证。",
                "讯飞星火、OCR、TTS 等外部能力只通过环境变量配置密钥，不提交到仓库。",
                "离线 provider 仅用于无密钥演示和容灾，不冒充真实云模型效果。",
            ],
            riskResponses=self._risk_responses(request.riskConcerns),
            finalDemoScript=[
                "先展示学生画像和先修诊断，证明个性化入口。",
                "再展示 RAG 资源生成、引用依据和内容安全审计。",
                "随后展示测评批改、错题本、画像更新和学习档案。",
                "最后展示项目代码审查、班级分析、Agent trace、RAG 评测和答辩包。",
            ],
            citations=citations,
            summary=f"答辩包生成完成：{len(matrix)} 个评分点、{len(qa_pairs)} 个问答、{len(citations)} 条证据。",
        )

    def _matrix(self, features: list[str]) -> list[DefenseFeatureMatrixItem]:
        endpoint_map = {
            "画像": "/agents/profile/infer",
            "RAG": "/agents/resource-generation",
            "资源": "/agents/resources/curate",
            "测评": "/agents/assessment/grade",
            "错题": "/agents/assessment/error-book",
            "班级": "/agents/class/analytics",
            "防幻觉": "/agents/evaluation/rag-quality",
            "多模态": "/agents/multimodal/voice-package",
            "代码": "/agents/code/project-review",
        }
        matrix = []
        for feature in features[:10]:
            endpoint = next((value for key, value in endpoint_map.items() if key.lower() in feature.lower()), "/agents/trace/explain")
            matrix.append(DefenseFeatureMatrixItem(
                scoringPoint=feature,
                implementedEvidence=f"已提供结构化接口 `{endpoint}`、smoke 测试和 citations/qualityGates 字段。",
                demoEndpoint=endpoint,
                differentiator="输出可落库、可追踪、可解释，失败时可离线降级。",
            ))
        return matrix

    def _qa(self, request: DefensePackRequest, citations: list[KnowledgeMatch]) -> list[DefenseQAItem]:
        evidence = compact(citations[0].text, 140) if citations else "代码端点和 smoke 输出。"
        return [
            DefenseQAItem(
                question="你们的多智能体不是概念图吗？",
                answer="不是。Python 主程拆成画像、RAG、资源规划、生成、安全审计、测评、错题、班级分析和追踪等可调用端点。",
                evidence=evidence,
            ),
            DefenseQAItem(
                question="如何防止大模型胡编？",
                answer="每个核心输出带 citations，另有内容安全审计、RAG 质量评测、人审预检和质量门禁。",
                evidence="/agents/evaluation/rag-quality、/agents/review/human-gate、/agents/safety/audit。",
            ),
            DefenseQAItem(
                question="讯飞 API 不可用怎么办？",
                answer="ProviderRouter 会自动降级到 offline provider，演示链路不中断，同时记录 fallback 事件供答辩说明。",
                evidence=str(request.apiStatus or {"fallbackProvider": "offline"}),
            ),
            DefenseQAItem(
                question="系统如何体现教师端价值？",
                answer="教师端可查看课程覆盖率、班级风险画像、干预分组、资源缺口、学习档案和审核清单。",
                evidence="/agents/course/coverage、/agents/class/analytics、/agents/report/portfolio。",
            ),
        ]

    def _api_checklist(self, request: DefensePackRequest) -> list[str]:
        return [
            "申请讯飞星火大模型 APIPassword 或 APIKey/APISecret。",
            "如演示 OCR，申请讯飞 OCR 服务并准备拍照题目样例。",
            "如演示语音，申请讯飞在线语音合成服务并准备 voice 参数。",
            f"当前 API 状态摘要：{json.dumps(request.apiStatus, ensure_ascii=False)[:240] if request.apiStatus else '待配置'}。",
        ]

    def _risk_responses(self, concerns: list[str]) -> list[str]:
        defaults = ["网络不可用", "评委追问防幻觉", "前端联调不稳定"]
        return [
            f"{concern}: 使用 smoke 输出、结构化 JSON、trace 回放和离线 provider 兜底。"
            for concern in (concerns or defaults)[:8]
        ]
