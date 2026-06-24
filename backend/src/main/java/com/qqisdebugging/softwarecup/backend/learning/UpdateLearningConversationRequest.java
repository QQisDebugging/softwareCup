package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.validation.constraints.Size;

public record UpdateLearningConversationRequest(
        @Size(max = 180) String title,
        Boolean archived) {
}
