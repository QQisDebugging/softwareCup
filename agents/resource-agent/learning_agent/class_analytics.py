from collections import Counter
import json

from learning_agent.config import AgentSettings
from learning_agent.llm import ProviderRouter
from learning_agent.resource_templates import compact
from learning_agent.schemas import (
    ClassAnalyticsRequest,
    ClassAnalyticsResponse,
    ClassInterventionGroup,
    ClassResourceGap,
    KnowledgeMatch,
    StudentLearningSnapshot,
    StudentRiskProfile,
)
from learning_agent.structured_output import as_int, as_list, as_text, complete_json
from learning_agent.vector_store import InMemoryVectorStore


class ClassAnalyticsAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store
        self.provider_router = ProviderRouter(settings)

    def analyze(self, request: ClassAnalyticsRequest) -> ClassAnalyticsResponse:
        citations = self.vector_store.search(self._query(request), top_k=max(6, self.settings.retrieval_top_k))
        baseline = self._baseline(request)
        analysis = self._llm_analysis(request, citations, baseline)
        provider = as_text(analysis.get("_provider"), self.provider_router.active_name)

        top_weaknesses = self._require_strings(analysis.get("topWeaknesses"), "topWeaknesses", limit=8)
        risk_profiles = self._risk_profiles_from_model(analysis.get("studentRiskProfiles"), request.snapshots)
        intervention_groups = self._groups_from_model(analysis.get("interventionGroups"), request.snapshots)
        resource_gaps = self._gaps_from_model(analysis.get("resourceGaps"))
        intervention_priority = self._require_strings(
            analysis.get("interventionPriority"),
            "interventionPriority",
            limit=8,
        )
        teacher_actions = self._require_strings(analysis.get("teacherActions"), "teacherActions", limit=8)
        summary = as_text(analysis.get("summary"))
        class_trend = as_text(analysis.get("classTrend"))
        if not summary or not class_trend:
            raise RuntimeError("Class analytics agent returned incomplete trend or summary.")

        return ClassAnalyticsResponse(
            classMasteryAverage=as_int(analysis.get("classMasteryAverage"), baseline["classMasteryAverage"], 0, 100),
            engagementAverage=as_int(analysis.get("engagementAverage"), baseline["engagementAverage"], 0, 100),
            classTrend=class_trend,
            topWeaknesses=top_weaknesses,
            studentRiskProfiles=risk_profiles,
            interventionGroups=intervention_groups,
            resourceGaps=resource_gaps,
            interventionPriority=intervention_priority,
            teacherActions=teacher_actions,
            citations=citations,
            summary=summary,
            provider=provider,
            model=self._model_name(provider),
            executionMode=as_text(analysis.get("_executionMode"), "LLM"),
            fallbackUsed=bool(analysis.get("_fallbackUsed", False)),
        )

    def _llm_analysis(
        self,
        request: ClassAnalyticsRequest,
        citations: list[KnowledgeMatch],
        baseline: dict,
    ) -> dict:
        evidence = "\n\n".join(
            f"[{index}] {item.title} ({item.source}, score={item.score}): {compact(item.text, 700)}"
            for index, item in enumerate(citations[:8], start=1)
        )
        system_prompt = (
            "You are a class-learning analytics agent for a Chinese teaching platform. "
            "Use the supplied student snapshots, deterministic baseline, and retrieved evidence to produce "
            "actionable teacher interventions. Return strict JSON only. Do not use Markdown."
        )
        user_prompt = f"""
Return one JSON object in Chinese with this exact shape:
{{
  "classMasteryAverage": 68,
  "engagementAverage": 61,
  "classTrend": "short trend label",
  "topWeaknesses": ["specific shared weakness"],
  "studentRiskProfiles": [
    {{
      "studentProfileId": "id from input",
      "studentName": "name from input",
      "masteryScore": 0,
      "engagementScore": 0,
      "riskLevel": "high/medium/low or Chinese equivalent",
      "primaryWeaknesses": ["weakness"],
      "recommendedAction": "teacher action"
    }}
  ],
  "interventionGroups": [
    {{
      "name": "group name",
      "criteria": "why these students are grouped",
      "studentProfileIds": ["ids from input"],
      "recommendedAgent": "/agents/resources/curate",
      "action": "next intervention"
    }}
  ],
  "resourceGaps": [
    {{
      "knowledgePoint": "weak point",
      "affectedStudents": 1,
      "missingResourceType": "resource type",
      "suggestedAction": "what to generate or review"
    }}
  ],
  "interventionPriority": ["ordered priority"],
  "teacherActions": ["teacher-facing action"],
  "summary": "short evidence-based conclusion"
}}

Rules:
- Use only studentProfileId values present in the input snapshots.
- Scores must be integers from 0 to 100.
- Every intervention group must include at least one known studentProfileId.
- recommendedAgent should name a real backend agent endpoint when possible:
  /agents/course/diagnose, /agents/resources/curate, /agents/assessment/item-analysis,
  /agents/code/practice/generate, /agents/teaching/scenario-plan.
- If the evidence is thin, include a teacherAction that asks for the missing evidence instead of pretending certainty.

Course id: {request.courseId}
Course title: {request.courseTitle}
Topic: {request.topic}
Time range: {request.timeRange}

Student snapshots:
{compact(json.dumps(self._snapshots_payload(request.snapshots), ensure_ascii=False), 9000)}

Deterministic baseline for cross-check:
{compact(json.dumps(baseline, ensure_ascii=False), 5000)}

Retrieved evidence:
{evidence or "No retrieved evidence."}
"""
        return complete_json(self.provider_router, system_prompt, user_prompt, "class analytics")

    def _baseline(self, request: ClassAnalyticsRequest) -> dict:
        mastery = self._class_mastery(request.snapshots)
        engagement = self._engagement(request.snapshots)
        top_weaknesses = self._top_weaknesses(request.snapshots)
        risk_profiles = self._student_risk_profiles(request.snapshots)
        groups = self._intervention_groups(request.snapshots, top_weaknesses)
        gaps = self._resource_gaps(top_weaknesses, request.snapshots)
        priority = self._intervention_priority(groups, gaps, risk_profiles)
        actions = self._teacher_actions(request, groups, gaps, priority)
        return {
            "classMasteryAverage": mastery,
            "engagementAverage": engagement,
            "classTrend": self._class_trend(mastery, engagement, risk_profiles),
            "topWeaknesses": top_weaknesses,
            "studentRiskProfiles": [item.model_dump() for item in risk_profiles],
            "interventionGroups": [item.model_dump() for item in groups],
            "resourceGaps": [item.model_dump() for item in gaps],
            "interventionPriority": priority,
            "teacherActions": actions,
        }

    def _query(self, request: ClassAnalyticsRequest) -> str:
        snapshots = "\n".join(
            f"{item.studentName} {item.profileSummary} {' '.join(item.weaknessSignals)} {' '.join(item.learningEvents)}"
            for item in request.snapshots
        )
        return "\n".join([request.courseTitle, request.topic, request.timeRange, snapshots, "class analytics intervention"])

    def _class_mastery(self, snapshots: list[StudentLearningSnapshot]) -> int:
        scores = [
            score
            for snapshot in snapshots
            for score in snapshot.recentScores
            if 0 <= score <= 100
        ]
        if not scores:
            return 55
        return round(sum(scores) / len(scores))

    def _engagement(self, snapshots: list[StudentLearningSnapshot]) -> int:
        if not snapshots:
            return 0
        scores = []
        for snapshot in snapshots:
            score = 30
            score += min(25, snapshot.completedResources * 6)
            score += min(20, snapshot.tutoringCount * 8)
            score += min(20, snapshot.codePracticeCount * 10)
            if any("review" in item.lower() or "summary" in item.lower() or "复盘" in item or "总结" in item for item in snapshot.learningEvents):
                score += 8
            scores.append(min(96, score))
        return round(sum(scores) / len(scores))

    def _student_mastery(self, snapshot: StudentLearningSnapshot) -> int:
        valid_scores = [score for score in snapshot.recentScores if 0 <= score <= 100]
        if not valid_scores:
            return 55
        return round(sum(valid_scores) / len(valid_scores))

    def _student_engagement(self, snapshot: StudentLearningSnapshot) -> int:
        score = 30
        score += min(25, snapshot.completedResources * 6)
        score += min(20, snapshot.tutoringCount * 8)
        score += min(20, snapshot.codePracticeCount * 10)
        if any("review" in item.lower() or "summary" in item.lower() or "复盘" in item or "总结" in item for item in snapshot.learningEvents):
            score += 8
        return min(96, score)

    def _student_risk_profiles(self, snapshots: list[StudentLearningSnapshot]) -> list[StudentRiskProfile]:
        profiles: list[StudentRiskProfile] = []
        for snapshot in snapshots:
            mastery = self._student_mastery(snapshot)
            engagement = self._student_engagement(snapshot)
            profiles.append(StudentRiskProfile(
                studentProfileId=snapshot.studentProfileId,
                studentName=snapshot.studentName,
                masteryScore=mastery,
                engagementScore=engagement,
                riskLevel=self._risk_level(mastery, engagement, snapshot),
                primaryWeaknesses=snapshot.weaknessSignals[:4],
                recommendedAction=self._student_action(mastery, engagement, snapshot),
            ))
        severity_order = {"high": 0, "medium": 1, "low": 2}
        profiles.sort(key=lambda item: (severity_order.get(item.riskLevel, 3), item.masteryScore, item.engagementScore))
        return profiles[:50]

    def _risk_level(self, mastery: int, engagement: int, snapshot: StudentLearningSnapshot) -> str:
        if mastery < 60 or engagement < 45:
            return "high"
        if mastery < 75 or engagement < 65 or len(snapshot.weaknessSignals) >= 3:
            return "medium"
        return "low"

    def _student_action(self, mastery: int, engagement: int, snapshot: StudentLearningSnapshot) -> str:
        if mastery < 60:
            return "Run prerequisite diagnosis and assign low-difficulty remediation before retest."
        if engagement < 55:
            return "Push a short resource bundle and require one tutoring checkpoint."
        if snapshot.codePracticeCount == 0:
            return "Assign code practice or a transfer task to collect practice evidence."
        return "Move to extension reading, peer explanation, or project challenge."

    def _top_weaknesses(self, snapshots: list[StudentLearningSnapshot]) -> list[str]:
        counter: Counter[str] = Counter()
        for snapshot in snapshots:
            counter.update(signal for signal in snapshot.weaknessSignals if signal.strip())
        return [item for item, _ in counter.most_common(8)]

    def _intervention_groups(
        self,
        snapshots: list[StudentLearningSnapshot],
        top_weaknesses: list[str],
    ) -> list[ClassInterventionGroup]:
        groups: list[ClassInterventionGroup] = []
        low_score = [
            item.studentProfileId
            for item in snapshots
            if item.recentScores and sum(item.recentScores) / len(item.recentScores) < 60
        ]
        if low_score:
            groups.append(ClassInterventionGroup(
                name="Foundation remediation group",
                criteria="Recent assessment average below 60",
                studentProfileIds=low_score,
                recommendedAgent="/agents/prerequisite/diagnose",
                action="Run entry diagnosis, then push basic explanation, mind map, and error-review cards.",
            ))
        low_engagement = [
            item.studentProfileId
            for item in snapshots
            if item.completedResources <= 1 and item.tutoringCount == 0
        ]
        if low_engagement:
            groups.append(ClassInterventionGroup(
                name="Low engagement group",
                criteria="Few completed resources and no tutoring interaction",
                studentProfileIds=low_engagement,
                recommendedAgent="/agents/resources/curate",
                action="Push a resource bundle that can be finished within 15 minutes and set one low-barrier checkpoint.",
            ))
        practice_gap = [
            item.studentProfileId
            for item in snapshots
            if item.codePracticeCount == 0 and any("code" in signal.lower() or "REST" in signal or "接口" in signal or "代码" in signal for signal in item.weaknessSignals)
        ]
        if practice_gap:
            groups.append(ClassInterventionGroup(
                name="Practice transfer group",
                criteria="Engineering topic is weak but code practice evidence is missing",
                studentProfileIds=practice_gap,
                recommendedAgent="/agents/code/practice/generate",
                action="Generate tiered refactoring or debugging exercises and require run evidence plus reflection.",
            ))
        for weakness in top_weaknesses[:2]:
            affected = [
                item.studentProfileId
                for item in snapshots
                if weakness in item.weaknessSignals
            ]
            if len(affected) >= 2:
                groups.append(ClassInterventionGroup(
                    name=f"{weakness} shared weakness group",
                    criteria=f"At least 2 students show `{weakness}`.",
                    studentProfileIds=affected,
                    recommendedAgent="/agents/multimodal/storyboard",
                    action=f"Generate a 5-minute visual explanation and 3 variant questions for `{weakness}`.",
                ))
        groups.sort(key=lambda item: len(item.studentProfileIds), reverse=True)
        return groups[:6]

    def _resource_gaps(
        self,
        top_weaknesses: list[str],
        snapshots: list[StudentLearningSnapshot],
    ) -> list[ClassResourceGap]:
        gaps: list[ClassResourceGap] = []
        for weakness in top_weaknesses[:6]:
            affected = sum(1 for snapshot in snapshots if weakness in snapshot.weaknessSignals)
            resource_type = "hands-on case" if any(key in weakness for key in ["code", "REST", "interface", "代码", "接口"]) else "explanation document + mind map"
            gaps.append(ClassResourceGap(
                knowledgePoint=weakness,
                affectedStudents=affected,
                missingResourceType=resource_type,
                suggestedAction=f"Call /agents/resources/curate and /agents/assessment/item-analysis for `{weakness}`.",
            ))
        return gaps

    def _intervention_priority(
        self,
        groups: list[ClassInterventionGroup],
        gaps: list[ClassResourceGap],
        risk_profiles: list[StudentRiskProfile],
    ) -> list[str]:
        high_risk_count = sum(1 for profile in risk_profiles if profile.riskLevel == "high")
        priority = []
        if high_risk_count:
            priority.append(f"Handle {high_risk_count} high-risk students first to stop weakness accumulation.")
        priority.extend(
            f"{group.name}: {len(group.studentProfileIds)} students, suggested agent {group.recommendedAgent}."
            for group in groups[:3]
        )
        priority.extend(
            f"Fill `{gap.knowledgePoint}` with `{gap.missingResourceType}`, affecting {gap.affectedStudents} students."
            for gap in gaps[:2]
        )
        return priority[:7]

    def _class_trend(
        self,
        mastery: int,
        engagement: int,
        risk_profiles: list[StudentRiskProfile],
    ) -> str:
        high_risk_count = sum(1 for profile in risk_profiles if profile.riskLevel == "high")
        if mastery >= 78 and engagement >= 70 and high_risk_count == 0:
            return "stable upward trend"
        if high_risk_count >= max(1, len(risk_profiles) // 3):
            return "clear stratification, needs tiered intervention"
        if engagement < 55:
            return "low engagement"
        if mastery < 65:
            return "low mastery"
        return "basically stable, shared weaknesses need resources"

    def _teacher_actions(
        self,
        request: ClassAnalyticsRequest,
        groups: list[ClassInterventionGroup],
        gaps: list[ClassResourceGap],
        priority: list[str],
    ) -> list[str]:
        actions = [
            f"Prioritize the largest intervention group: `{groups[0].name}`." if groups else "Collect learning events and assessments before rerunning class analytics.",
            f"Build a post-class loop around `{request.topic}`: resource push -> practice -> grading -> portfolio evidence.",
        ]
        actions.extend(priority[:2])
        actions.extend(
            f"Create `{gap.missingResourceType}` for `{gap.knowledgePoint}`, affecting {gap.affectedStudents} students."
            for gap in gaps[:4]
        )
        actions.append("Keep the grouping evidence visible on the teacher side to avoid black-box recommendations.")
        return actions[:7]

    def _risk_profiles_from_model(
        self,
        value: object,
        snapshots: list[StudentLearningSnapshot],
    ) -> list[StudentRiskProfile]:
        known = {item.studentProfileId: item for item in snapshots}
        profiles: list[StudentRiskProfile] = []
        for item in as_list(value)[:50]:
            if not isinstance(item, dict):
                continue
            student_id = as_text(item.get("studentProfileId"))
            if student_id not in known:
                continue
            snapshot = known[student_id]
            profiles.append(StudentRiskProfile(
                studentProfileId=student_id,
                studentName=as_text(item.get("studentName"), snapshot.studentName),
                masteryScore=as_int(item.get("masteryScore"), self._student_mastery(snapshot), 0, 100),
                engagementScore=as_int(item.get("engagementScore"), self._student_engagement(snapshot), 0, 100),
                riskLevel=as_text(item.get("riskLevel"), self._risk_level(self._student_mastery(snapshot), self._student_engagement(snapshot), snapshot)),
                primaryWeaknesses=self._strings(item.get("primaryWeaknesses"))[:6] or snapshot.weaknessSignals[:4],
                recommendedAction=as_text(item.get("recommendedAction"), self._student_action(self._student_mastery(snapshot), self._student_engagement(snapshot), snapshot)),
            ))
        if not profiles:
            raise RuntimeError("Class analytics agent returned no valid student risk profiles.")
        return profiles

    def _groups_from_model(
        self,
        value: object,
        snapshots: list[StudentLearningSnapshot],
    ) -> list[ClassInterventionGroup]:
        known_ids = {item.studentProfileId for item in snapshots}
        groups: list[ClassInterventionGroup] = []
        for item in as_list(value)[:8]:
            if not isinstance(item, dict):
                continue
            ids = [student_id for student_id in self._strings(item.get("studentProfileIds")) if student_id in known_ids]
            if not ids:
                continue
            groups.append(ClassInterventionGroup(
                name=as_text(item.get("name"), "Intervention group"),
                criteria=as_text(item.get("criteria"), "Grouped by shared evidence."),
                studentProfileIds=ids,
                recommendedAgent=as_text(item.get("recommendedAgent"), "/agents/resources/curate"),
                action=as_text(item.get("action"), "Generate targeted resources and reassess."),
            ))
        if not groups:
            raise RuntimeError("Class analytics agent returned no valid intervention groups.")
        return groups

    def _gaps_from_model(self, value: object) -> list[ClassResourceGap]:
        gaps: list[ClassResourceGap] = []
        for item in as_list(value)[:10]:
            if not isinstance(item, dict):
                continue
            gaps.append(ClassResourceGap(
                knowledgePoint=as_text(item.get("knowledgePoint"), "Shared weakness"),
                affectedStudents=as_int(item.get("affectedStudents"), 1, 0),
                missingResourceType=as_text(item.get("missingResourceType"), "Targeted practice"),
                suggestedAction=as_text(item.get("suggestedAction"), "Generate a targeted resource and follow-up assessment."),
            ))
        if not gaps:
            raise RuntimeError("Class analytics agent returned no resource gap analysis.")
        return gaps

    def _require_strings(self, value: object, field_name: str, *, limit: int) -> list[str]:
        strings = self._strings(value)[:limit]
        if not strings:
            raise RuntimeError(f"Class analytics agent returned empty {field_name}.")
        return strings

    def _strings(self, value: object) -> list[str]:
        return [as_text(item) for item in as_list(value) if as_text(item)]

    def _snapshots_payload(self, snapshots: list[StudentLearningSnapshot]) -> list[dict]:
        return [
            {
                "studentProfileId": item.studentProfileId,
                "studentName": item.studentName,
                "profileSummary": item.profileSummary,
                "recentScores": item.recentScores,
                "completedResources": item.completedResources,
                "tutoringCount": item.tutoringCount,
                "codePracticeCount": item.codePracticeCount,
                "weaknessSignals": item.weaknessSignals,
                "learningEvents": item.learningEvents,
            }
            for item in snapshots[:80]
        ]

    def _model_name(self, provider: str) -> str:
        return self.settings.openai_model if provider == "openai_compatible" else self.settings.xfyun_model
