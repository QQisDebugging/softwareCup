package com.qqisdebugging.softwarecup.backend.learning;

import java.time.Instant;

public record LearningConversationResponse(
        String id,
        String studentProfileId,
        String courseId,
        String title,
        Boolean archived,
        Instant archivedAt,
        String lastMessagePreview,
        Instant lastMessageAt,
        Instant createdAt,
        Instant updatedAt) {
    public static LearningConversationResponse from(LearningConversation conversation) {
        return new LearningConversationResponse(
                conversation.getId(),
                conversation.getStudentProfileId(),
                conversation.getCourseId(),
                conversation.getTitle(),
                conversation.getArchived(),
                conversation.getArchivedAt(),
                conversation.getLastMessagePreview(),
                conversation.getLastMessageAt(),
                conversation.getCreatedAt(),
                conversation.getUpdatedAt());
    }
}
