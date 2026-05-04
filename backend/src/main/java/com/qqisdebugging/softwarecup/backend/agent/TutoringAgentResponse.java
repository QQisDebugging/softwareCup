package com.qqisdebugging.softwarecup.backend.agent;

import java.util.List;

public record TutoringAgentResponse(
        String answer,
        List<AgentKnowledgeMatch> citations,
        List<String> followUpQuestions,
        List<String> learningActions,
        List<String> profileSignals,
        String mermaidDiagram,
        String provider,
        Boolean fallbackUsed) {
}
