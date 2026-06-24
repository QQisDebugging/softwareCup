package com.qqisdebugging.softwarecup.backend.agent;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
public record AgentKnowledgeMatch(
        String id,
        Double score,
        String text,
        String source,
        String title,
        Map<String, Object> metadata) {
}
