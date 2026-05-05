from collections import Counter

from learning_agent.config import AgentSettings
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
from learning_agent.vector_store import InMemoryVectorStore


class ClassAnalyticsAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def analyze(self, request: ClassAnalyticsRequest) -> ClassAnalyticsResponse:
        citations = self.vector_store.search(self._query(request), top_k=self.settings.retrieval_top_k)
        mastery = self._class_mastery(request.snapshots)
        engagement = self._engagement(request.snapshots)
        top_weaknesses = self._top_weaknesses(request.snapshots)
        risk_profiles = self._student_risk_profiles(request.snapshots)
        groups = self._intervention_groups(request.snapshots, top_weaknesses)
        gaps = self._resource_gaps(top_weaknesses, request.snapshots)
        priority = self._intervention_priority(groups, gaps, risk_profiles)
        actions = self._teacher_actions(request, groups, gaps, priority)
        class_trend = self._class_trend(mastery, engagement, risk_profiles)
        summary = (
            f"{request.timeRange} `{request.topic}` 班级分析完成：平均掌握度 {mastery}/100，"
            f"平均参与度 {engagement}/100，趋势 `{class_trend}`，识别 {len(groups)} 个干预分组。"
        )
        return ClassAnalyticsResponse(
            classMasteryAverage=mastery,
            engagementAverage=engagement,
            classTrend=class_trend,
            topWeaknesses=top_weaknesses,
            studentRiskProfiles=risk_profiles,
            interventionGroups=groups,
            resourceGaps=gaps,
            interventionPriority=priority,
            teacherActions=actions,
            citations=citations,
            summary=summary,
        )

    def _query(self, request: ClassAnalyticsRequest) -> str:
        snapshots = "\n".join(
            f"{item.studentName} {item.profileSummary} {' '.join(item.weaknessSignals)} {' '.join(item.learningEvents)}"
            for item in request.snapshots
        )
        return "\n".join([request.courseTitle, request.topic, request.timeRange, snapshots, "班级 学情 分层干预 资源缺口"])

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
            if any("复盘" in item or "总结" in item for item in snapshot.learningEvents):
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
        if any("复盘" in item or "总结" in item for item in snapshot.learningEvents):
            score += 8
        return min(96, score)

    def _student_risk_profiles(self, snapshots: list[StudentLearningSnapshot]) -> list[StudentRiskProfile]:
        profiles: list[StudentRiskProfile] = []
        for snapshot in snapshots:
            mastery = self._student_mastery(snapshot)
            engagement = self._student_engagement(snapshot)
            risk_level = self._risk_level(mastery, engagement, snapshot)
            profiles.append(StudentRiskProfile(
                studentProfileId=snapshot.studentProfileId,
                studentName=snapshot.studentName,
                masteryScore=mastery,
                engagementScore=engagement,
                riskLevel=risk_level,
                primaryWeaknesses=snapshot.weaknessSignals[:4],
                recommendedAction=self._student_action(mastery, engagement, snapshot),
            ))
        severity_order = {"高": 0, "中": 1, "低": 2}
        profiles.sort(key=lambda item: (severity_order.get(item.riskLevel, 3), item.masteryScore, item.engagementScore))
        return profiles[:50]

    def _risk_level(self, mastery: int, engagement: int, snapshot: StudentLearningSnapshot) -> str:
        if mastery < 60 or engagement < 45:
            return "高"
        if mastery < 75 or engagement < 65 or len(snapshot.weaknessSignals) >= 3:
            return "中"
        return "低"

    def _student_action(self, mastery: int, engagement: int, snapshot: StudentLearningSnapshot) -> str:
        if mastery < 60:
            return "先做先修诊断和基础补救资源，再安排低难度复测。"
        if engagement < 55:
            return "推送短时资源包，并用一次答疑任务唤醒主动提问。"
        if snapshot.codePracticeCount == 0:
            return "安排代码实操或项目迁移任务，补足实践证据。"
        return "进入拓展阅读、同伴讲解或高阶项目挑战。"

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
                name="基础补救组",
                criteria="最近测评均分低于 60",
                studentProfileIds=low_score,
                recommendedAgent="/agents/prerequisite/diagnose",
                action="先做入口诊断，再推送基础讲解、思维导图和错题复盘卡。",
            ))
        low_engagement = [
            item.studentProfileId
            for item in snapshots
            if item.completedResources <= 1 and item.tutoringCount == 0
        ]
        if low_engagement:
            groups.append(ClassInterventionGroup(
                name="低参与唤醒组",
                criteria="资源完成少且没有答疑互动",
                studentProfileIds=low_engagement,
                recommendedAgent="/agents/resources/curate",
                action="推送 15 分钟内可完成的微资源，并设置一次低门槛 checkpoint。",
            ))
        practice_gap = [
            item.studentProfileId
            for item in snapshots
            if item.codePracticeCount == 0 and any("代码" in signal or "分层" in signal or "REST" in signal for signal in item.weaknessSignals)
        ]
        if practice_gap:
            groups.append(ClassInterventionGroup(
                name="实操迁移组",
                criteria="工程主题薄弱但缺少代码练习",
                studentProfileIds=practice_gap,
                recommendedAgent="/agents/code/practice/generate",
                action="生成分层改造或代码纠错题，要求提交运行截图和错因复盘。",
            ))
        for weakness in top_weaknesses[:2]:
            affected = [
                item.studentProfileId
                for item in snapshots
                if weakness in item.weaknessSignals
            ]
            if len(affected) >= 2:
                groups.append(ClassInterventionGroup(
                    name=f"{weakness} 共性薄弱组",
                    criteria=f"至少 2 名学生出现 `{weakness}`",
                    studentProfileIds=affected,
                    recommendedAgent="/agents/multimodal/storyboard",
                    action=f"生成 `{weakness}` 的 5 分钟图解微课和 3 道变式题。",
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
            resource_type = "实操案例" if any(key in weakness for key in ["代码", "分层", "REST", "接口"]) else "讲解文档+思维导图"
            gaps.append(ClassResourceGap(
                knowledgePoint=weakness,
                affectedStudents=affected,
                missingResourceType=resource_type,
                suggestedAction=f"调用 `/agents/resources/curate` 和 `/agents/assessment/item-analysis` 补齐 `{weakness}` 的资源与变式题。",
            ))
        return gaps

    def _intervention_priority(
        self,
        groups: list[ClassInterventionGroup],
        gaps: list[ClassResourceGap],
        risk_profiles: list[StudentRiskProfile],
    ) -> list[str]:
        high_risk_count = sum(1 for profile in risk_profiles if profile.riskLevel == "高")
        priority = []
        if high_risk_count:
            priority.append(f"先处理 {high_risk_count} 名高风险学生，避免薄弱点继续固化。")
        priority.extend(
            f"{group.name}: {len(group.studentProfileIds)} 人，建议调用 {group.recommendedAgent}。"
            for group in groups[:3]
        )
        priority.extend(
            f"补齐 `{gap.knowledgePoint}` 的 `{gap.missingResourceType}`，影响 {gap.affectedStudents} 人。"
            for gap in gaps[:2]
        )
        return priority[:7]

    def _class_trend(
        self,
        mastery: int,
        engagement: int,
        risk_profiles: list[StudentRiskProfile],
    ) -> str:
        high_risk_count = sum(1 for profile in risk_profiles if profile.riskLevel == "高")
        if mastery >= 78 and engagement >= 70 and high_risk_count == 0:
            return "整体稳定提升"
        if high_risk_count >= max(1, len(risk_profiles) // 3):
            return "分化明显，需要分层干预"
        if engagement < 55:
            return "参与度偏低"
        if mastery < 65:
            return "掌握度偏低"
        return "基本稳定，需补齐共性薄弱点"

    def _teacher_actions(
        self,
        request: ClassAnalyticsRequest,
        groups: list[ClassInterventionGroup],
        gaps: list[ClassResourceGap],
        priority: list[str],
    ) -> list[str]:
        actions = [
            f"先处理人数最多的干预组：`{groups[0].name}`。" if groups else "先补充学习事件和测评记录，再重新分析班级学情。",
            f"围绕 `{request.topic}` 建立一次课后闭环：资源推送 -> 练习 -> 批改 -> 学习档案。",
        ]
        actions.extend(priority[:2])
        actions.extend(
            f"为 `{gap.knowledgePoint}` 补充 `{gap.missingResourceType}`，影响 {gap.affectedStudents} 名学生。"
            for gap in gaps[:4]
        )
        actions.append("教师端展示时保留学生分组依据，避免只给出黑盒推荐。")
        return actions[:7]
