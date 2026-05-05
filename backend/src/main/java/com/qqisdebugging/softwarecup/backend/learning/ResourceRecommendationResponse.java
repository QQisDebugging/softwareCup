package com.qqisdebugging.softwarecup.backend.learning;

import java.math.BigDecimal;
import java.time.Instant;

public record ResourceRecommendationResponse(
        String id,
        String studentProfileId,
        String courseId,
        String resourceId,
        String reason,
        BigDecimal priorityScore,
        String status,
        Instant createdAt) {
    public static ResourceRecommendationResponse from(ResourceRecommendation recommendation) {
        return new ResourceRecommendationResponse(
                recommendation.getId(),
                recommendation.getStudentProfileId(),
                recommendation.getCourseId(),
                recommendation.getResourceId(),
                recommendation.getReason(),
                recommendation.getPriorityScore(),
                recommendation.getStatus(),
                recommendation.getCreatedAt());
    }
}
