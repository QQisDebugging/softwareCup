package com.qqisdebugging.softwarecup.backend.agent;

import java.util.List;

public record AssessmentGenerateAgentResponse(
        String title,
        String topic,
        List<AssessmentQuestion> questions,
        List<AgentKnowledgeMatch> citations,
        String summary) {
}
