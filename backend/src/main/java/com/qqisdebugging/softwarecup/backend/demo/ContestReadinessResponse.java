package com.qqisdebugging.softwarecup.backend.demo;

import java.time.Instant;
import java.util.List;

public record ContestReadinessResponse(
        Instant generatedAt,
        String scope,
        Integer overallScore,
        String summary,
        ContestReadinessMetrics metrics,
        List<ContestRequirementEvidence> requirements,
        List<String> demoHighlights,
        List<String> recommendedDemoFlow) {
}
