package com.qqisdebugging.softwarecup.backend.profile;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.Valid;
import java.util.List;

public record BuildProfileRequest(
        @NotBlank String studentName,
        @NotBlank String major,
        @NotBlank String currentLevel,
        @NotBlank String learningGoal,
        @NotBlank String preferences,
        @NotBlank String constraintsText,
        @NotEmpty List<String> dialogueTurns,
        @Valid List<ProfileDimensionRequest> dimensions) {
}
