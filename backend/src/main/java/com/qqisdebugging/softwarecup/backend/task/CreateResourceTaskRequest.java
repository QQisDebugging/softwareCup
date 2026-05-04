package com.qqisdebugging.softwarecup.backend.task;

import jakarta.validation.constraints.NotBlank;

public record CreateResourceTaskRequest(
        @NotBlank String studentProfileId,
        @NotBlank String courseId,
        @NotBlank String topic,
        @NotBlank String resourceType,
        @NotBlank String modality,
        @NotBlank String prompt) {
}
