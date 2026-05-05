package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.util.List;

public record CreateTutoringRequest(
        @NotBlank String studentProfileId,
        @NotBlank String courseId,
        @NotBlank @Size(max = 4000) String question,
        List<String> conversationHistory,
        String modality,
        List<String> knowledgeBasePaths,
        List<String> documentTexts) {
}
