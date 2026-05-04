package com.qqisdebugging.softwarecup.backend.agent;

public record ResourceAgentRequest(
        String taskId,
        String studentProfileId,
        String courseId,
        String studentProfileSummary,
        String courseTitle,
        String topic,
        String resourceType,
        String modality,
        String prompt) {
}
