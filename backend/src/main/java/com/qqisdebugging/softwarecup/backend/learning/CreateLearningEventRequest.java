package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.validation.constraints.NotBlank;

public record CreateLearningEventRequest(
        @NotBlank String studentProfileId,
        @NotBlank String courseId,
        String resourceId,
        @NotBlank String eventType,
        Integer durationSeconds,
        Integer feedbackScore,
        String eventPayload) {
}
