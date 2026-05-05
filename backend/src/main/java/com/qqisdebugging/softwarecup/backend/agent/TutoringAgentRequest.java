package com.qqisdebugging.softwarecup.backend.agent;

import java.util.List;

public record TutoringAgentRequest(
        String sessionId,
        String studentProfileId,
        String courseId,
        String studentProfileSummary,
        String courseTitle,
        String question,
        List<String> conversationHistory,
        String modality,
        List<String> knowledgeBasePaths,
        List<String> documentTexts) {
}
