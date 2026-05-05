package com.qqisdebugging.softwarecup.backend.learning;

import java.math.BigDecimal;
import java.time.Instant;

public record EvaluationReportResponse(
        String id,
        String studentProfileId,
        String courseId,
        String reportSummary,
        BigDecimal overallScore,
        String strengths,
        String weaknesses,
        String recommendationStrategy,
        Instant createdAt) {
    public static EvaluationReportResponse from(EvaluationReport report) {
        return new EvaluationReportResponse(
                report.getId(),
                report.getStudentProfileId(),
                report.getCourseId(),
                report.getReportSummary(),
                report.getOverallScore(),
                report.getStrengths(),
                report.getWeaknesses(),
                report.getRecommendationStrategy(),
                report.getCreatedAt());
    }
}
