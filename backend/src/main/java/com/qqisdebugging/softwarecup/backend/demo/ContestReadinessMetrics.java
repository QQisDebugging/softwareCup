package com.qqisdebugging.softwarecup.backend.demo;

public record ContestReadinessMetrics(
        Long courseCount,
        Long studentProfileCount,
        Integer profileDimensionCount,
        Integer profileHistoryCount,
        Integer enabledAgentCount,
        Integer resourceTypeCount,
        Integer taskCount,
        Integer successfulTaskCount,
        Integer taskStepCount,
        Integer modelInvocationCount,
        Integer generationAuditCount,
        Integer reviewRequiredAuditCount,
        Integer humanReviewGateCount,
        Integer learningPathCount,
        Integer learningPathNodeCount,
        Integer resourceRecommendationCount,
        Integer learningEventCount,
        Integer tutoringSessionCount,
        Integer quizAttemptCount,
        Integer knowledgeMasteryCount,
        Integer evaluationReportCount,
        Integer agentArtifactCount) {
}
