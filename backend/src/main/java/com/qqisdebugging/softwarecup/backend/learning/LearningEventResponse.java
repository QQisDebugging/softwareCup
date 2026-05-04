package com.qqisdebugging.softwarecup.backend.learning;

import java.time.Instant;

public record LearningEventResponse(
        String id,
        String studentProfileId,
        String courseId,
        String resourceId,
        String eventType,
        Integer durationSeconds,
        Integer feedbackScore,
        String eventPayload,
        Instant createdAt) {
    public static LearningEventResponse from(LearningEvent event) {
        return new LearningEventResponse(
                event.getId(),
                event.getStudentProfileId(),
                event.getCourseId(),
                event.getResourceId(),
                event.getEventType(),
                event.getDurationSeconds(),
                event.getFeedbackScore(),
                event.getEventPayload(),
                event.getCreatedAt());
    }
}
