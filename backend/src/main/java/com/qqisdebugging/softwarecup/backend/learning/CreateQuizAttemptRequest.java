package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;

public record CreateQuizAttemptRequest(
        @NotBlank String studentProfileId,
        @NotBlank String courseId,
        String resourceId,
        @NotNull BigDecimal score,
        @NotNull BigDecimal maxScore,
        @NotNull Integer correctCount,
        @NotNull Integer totalCount,
        String weakPoints) {
}
