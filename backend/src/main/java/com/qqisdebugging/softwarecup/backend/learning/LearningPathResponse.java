package com.qqisdebugging.softwarecup.backend.learning;

import java.time.Instant;
import java.util.List;

public record LearningPathResponse(
        String id,
        String studentProfileId,
        String courseId,
        String title,
        String status,
        List<LearningPathNodeResponse> nodes,
        Instant createdAt,
        Instant updatedAt) {
    public static LearningPathResponse from(LearningPath path, List<LearningPathNode> nodes) {
        return new LearningPathResponse(
                path.getId(),
                path.getStudentProfileId(),
                path.getCourseId(),
                path.getTitle(),
                path.getStatus(),
                nodes.stream().map(LearningPathNodeResponse::from).toList(),
                path.getCreatedAt(),
                path.getUpdatedAt());
    }
}
