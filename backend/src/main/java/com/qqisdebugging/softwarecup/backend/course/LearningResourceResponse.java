package com.qqisdebugging.softwarecup.backend.course;

import java.time.Instant;

public record LearningResourceResponse(
        String id,
        String courseId,
        String sourceTaskId,
        String title,
        String resourceType,
        String resourceTypeName,
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
                ResourceType.normalize(resource.getResourceType()).displayName(),
                resource.getModality(),
                resource.getTargetLevel(),
                resource.getEstimatedMinutes(),
                resource.getContent(),
                resource.getCreatedAt(),
                resource.getUpdatedAt());
    }
}
