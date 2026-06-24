package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.validation.constraints.Size;
import java.util.List;

public record SendLearningConversationMessageRequest(
        @Size(max = 4000) String content,
        @Size(max = 4000) String message,
        String modality,
        List<String> knowledgeBasePaths,
        List<String> documentTexts) {
}
