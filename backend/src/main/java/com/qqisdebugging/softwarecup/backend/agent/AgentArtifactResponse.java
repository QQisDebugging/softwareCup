package com.qqisdebugging.softwarecup.backend.agent;

import java.time.Instant;

public record AgentArtifactResponse(
        String id,
        String studentProfileId,
        String courseId,
        String artifactType,
        String agentEndpoint,
        String topic,
        String status,
        String requestSummary,
        String payloadJson,
        String citationsJson,
        String safetySummary,
        String traceId,
        Long latencyMs,
        String errorMessage,
        Instant createdAt) {
    static AgentArtifactResponse from(AgentArtifact artifact) {
        return new AgentArtifactResponse(
                artifact.getId(),
                artifact.getStudentProfileId(),
                artifact.getCourseId(),
                artifact.getArtifactType(),
                artifact.getAgentEndpoint(),
                artifact.getTopic(),
                artifact.getStatus(),
                artifact.getRequestSummary(),
                artifact.getPayloadJson(),
                artifact.getCitationsJson(),
                artifact.getSafetySummary(),
                artifact.getTraceId(),
                artifact.getLatencyMs(),
                artifact.getErrorMessage(),
                artifact.getCreatedAt());
    }
}
