package com.qqisdebugging.softwarecup.backend.agent;

import java.util.Map;

public record AgentKnowledgeMatch(
        String id,
        Double score,
        String text,
        String source,
        String title,
        Map<String, Object> metadata) {
}
