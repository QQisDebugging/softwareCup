package com.qqisdebugging.softwarecup.backend.learning;

public record SendLearningConversationMessageResponse(
        LearningConversationResponse conversation,
        LearningConversationMessageResponse userMessage,
        LearningConversationMessageResponse assistantMessage) {
}
