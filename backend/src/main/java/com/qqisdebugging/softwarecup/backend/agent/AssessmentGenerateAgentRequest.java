package com.qqisdebugging.softwarecup.backend.agent;

import java.util.List;

public record AssessmentGenerateAgentRequest(
        String studentProfileId,
        String courseId,
        String studentProfileSummary,
        String courseTitle,
        String topic,
        String difficulty,
        List<String> questionTypes,
        Integer count,
        List<String> knowledgeBasePaths,
        List<String> documentTexts) {
}
