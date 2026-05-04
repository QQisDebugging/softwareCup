package com.qqisdebugging.softwarecup.backend.learning;

import java.time.Instant;

public record LearningEventResponse(
        String id,
        String studentProfileId,
        String courseId,
        String eventType,
        String topic,
        String payloadJson,
        Instant createdAt) {

    public static LearningEventResponse from(LearningEvent event) {
        return new LearningEventResponse(
                event.getId(),
                event.getStudentProfileId(),
                event.getCourseId(),
                event.getEventType(),
                event.getTopic(),
                event.getPayloadJson(),
                event.getCreatedAt());
    }
}
