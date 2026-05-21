package com.qqisdebugging.softwarecup.backend.agent;

import java.util.List;

public record ResourceAgentRequest(
        String taskId,
        String studentProfileId,
        String courseId,
        String studentProfileSummary,
        String courseTitle,
        String topic,
        String resourceType,
        String modality,
        String prompt,
        List<String> knowledgeBasePaths,
        List<String> documentTexts,
        List<String> targetResourceTypes) {
}
