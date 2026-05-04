package com.qqisdebugging.softwarecup.backend.course;

import java.time.Instant;

public record LearningResourceResponse(
        String id,
        String courseId,
        String sourceTaskId,
        String title,
        String resourceType,
        String modality,
        String targetLevel,
        Integer estimatedMinutes,
        String content,
        Instant createdAt,
        Instant updatedAt) {
    public static LearningResourceResponse from(LearningResource resource) {
        return new LearningResourceResponse(
                resource.getId(),
                resource.getCourseId(),
                resource.getSourceTaskId(),
                resource.getTitle(),
                resource.getResourceType(),
                resource.getModality(),
                resource.getTargetLevel(),
                resource.getEstimatedMinutes(),
                resource.getContent(),
                resource.getCreatedAt(),
                resource.getUpdatedAt());
    }
}
