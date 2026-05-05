package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import java.util.List;

public record GenerateAssessmentRequest(
        @NotBlank String studentProfileId,
        @NotBlank String courseId,
        @NotBlank @jakarta.validation.constraints.Size(max = 180) String topic,
        String difficulty,
        List<String> questionTypes,
        @Min(1) @Max(12) Integer count,
        List<String> knowledgeBasePaths,
        List<String> documentTexts) {
}
