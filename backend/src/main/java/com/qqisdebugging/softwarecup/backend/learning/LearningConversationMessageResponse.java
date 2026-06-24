package com.qqisdebugging.softwarecup.backend.learning;

import com.qqisdebugging.softwarecup.backend.agent.AgentKnowledgeMatch;
import java.time.Instant;
import java.util.List;

public record LearningConversationMessageResponse(
        String id,
        String conversationId,
        String role,
        String content,
        List<AgentKnowledgeMatch> citations,
        List<String> followUpQuestions,
        List<String> learningActions,
        List<String> profileSignals,
        String mermaidDiagram,
        String provider,
        Boolean fallbackUsed,
        Instant createdAt) {
}
