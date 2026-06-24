package com.qqisdebugging.softwarecup.backend.agent;

public record ResourceAgentResponse(
        String title,
        String resourceType,
        String modality,
        String targetLevel,
        Integer estimatedMinutes,
        String content,
        String summary,
        String provider,
        String model,
        String executionMode,
        Boolean fallbackUsed) {
}
