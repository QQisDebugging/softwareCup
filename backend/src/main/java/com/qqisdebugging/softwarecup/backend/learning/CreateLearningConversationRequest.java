package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record CreateLearningConversationRequest(
        @NotBlank String studentProfileId,
        @NotBlank String courseId,
        @Size(max = 180) String title) {
}
