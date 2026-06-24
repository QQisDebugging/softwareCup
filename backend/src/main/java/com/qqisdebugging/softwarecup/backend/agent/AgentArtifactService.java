package com.qqisdebugging.softwarecup.backend.agent;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestClientException;

@Service
public class AgentArtifactService {
    private final ResourceAgentClient client;
    private final AgentArtifactRepository repository;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public AgentArtifactService(ResourceAgentClient client, AgentArtifactRepository repository) {
        this.client = client;
        this.repository = repository;
    }

    public Map<String, Object> invokeAndStore(
            String artifactType,
            String agentEndpoint,
            Map<String, Object> request) {
        long start = System.nanoTime();
        if (request == null) {
            request = new LinkedHashMap<>();
        }
        String traceId = valueOrFallback(textValue(request.get("traceId")), "agent-" + UUID.randomUUID());
        request.put("traceId", traceId);
        String studentProfileId = textValue(request.get("studentProfileId"));
        String courseId = textValue(request.get("courseId"));
        String topic = textValue(request.get("topic"));
        Map<String, Object> response;
        String status = "SUCCEEDED";
        String errorMessage = null;
        try {
            Map<String, Object> upstreamResponse = client.proxy(agentEndpoint, request);
            if (upstreamResponse == null) {
                throw new IllegalStateException("Agent returned empty response");
            }
            response = new LinkedHashMap<>(upstreamResponse);
            rejectFallbackOrFailed(agentEndpoint, response);
            normalizeResponseMetadata(response, traceId);
        } catch (RuntimeException ex) {
            status = "FAILED";
            errorMessage = compact(ex.getMessage(), 2000);
            response = new LinkedHashMap<>(Map.of(
                    "status", status,
                    "agentEndpoint", agentEndpoint,
                    "error", errorMessage == null ? "Agent upstream call failed" : errorMessage));
        }
        AgentArtifact saved = repository.save(new AgentArtifact(
                studentProfileId,
                courseId,
                artifactType,
                agentEndpoint,
                topic,
                status,
                compact(writeJson(request), 1200),
                writeJson(response),
                writeJson(response.get("citations")),
                safetySummary(response),
                traceId,
                elapsedMs(start),
                errorMessage));
        if ("FAILED".equals(status)) {
            throw new AgentUpstreamException("Agent upstream call failed: " + errorMessage);
        }
        response.putIfAbsent("artifactId", saved.getId());
        response.putIfAbsent("artifactStatus", status);
        response.putIfAbsent("traceId", traceId);
        response.putIfAbsent("uiAction", Map.of(
                "kind", "DISPLAY_ARTIFACT",
                "route", "",
                "reason", "AGENT_ARTIFACT_CREATED"));
        return response;
    }

    private void normalizeResponseMetadata(Map<String, Object> response, String traceId) {
        response.putIfAbsent("traceId", traceId);
        if (hasText(textValue(response.get("provider"))) && hasText(textValue(response.get("model")))) {
            return;
        }
        Map<String, Object> status = providerStatusOrEmpty();
        putIfBlank(response, "provider", status.getOrDefault("activeProvider", status.get("configuredProvider")));
        String provider = textValue(response.get("provider"));
        Object model = status.get("model");
        if (!hasText(textValue(model))) {
            model = "openai_compatible".equalsIgnoreCase(valueOrFallback(provider, ""))
                    ? status.get("openaiModel")
                    : status.get("xfyunModel");
        }
        putIfBlank(response, "model", model);
    }

    private Map<String, Object> providerStatusOrEmpty() {
        try {
            Map<String, Object> status = client.providerStatus();
            return status == null ? Map.of() : status;
        } catch (RuntimeException ex) {
            return Map.of();
        }
    }

    private void putIfBlank(Map<String, Object> target, String key, Object value) {
        if (!hasText(textValue(target.get(key))) && hasText(textValue(value))) {
            target.put(key, value);
        }
    }

    private void rejectFallbackOrFailed(String agentEndpoint, Map<String, Object> response) {
        String status = textValue(response.get("status"));
        String provider = textValue(response.get("provider"));
        boolean fallbackUsed = Boolean.TRUE.equals(response.get("fallbackUsed"));
        if ("FALLBACK".equalsIgnoreCase(valueOrFallback(status, ""))
                || "FAILED".equalsIgnoreCase(valueOrFallback(status, ""))
                || fallbackUsed
                || valueOrFallback(provider, "").toLowerCase(java.util.Locale.ROOT).contains("fallback")) {
            throw new IllegalStateException("Agent endpoint " + agentEndpoint + " returned non-authoritative output");
        }
    }

    @Transactional(readOnly = true)
    public List<AgentArtifactResponse> listArtifacts(String studentProfileId, String courseId, String artifactType) {
        List<AgentArtifact> artifacts;
        if (hasText(studentProfileId) && hasText(courseId)) {
            artifacts = repository.findTop50ByStudentProfileIdAndCourseIdOrderByCreatedAtDesc(studentProfileId, courseId);
        } else if (hasText(studentProfileId)) {
            artifacts = repository.findTop50ByStudentProfileIdOrderByCreatedAtDesc(studentProfileId);
        } else if (hasText(courseId)) {
            artifacts = repository.findTop50ByCourseIdOrderByCreatedAtDesc(courseId);
        } else if (hasText(artifactType)) {
            artifacts = repository.findTop50ByArtifactTypeOrderByCreatedAtDesc(artifactType);
        } else {
            artifacts = repository.findTop50ByOrderByCreatedAtDesc();
        }
        return artifacts.stream()
                .filter(artifact -> !hasText(artifactType) || artifactType.equals(artifact.getArtifactType()))
                .map(AgentArtifactResponse::from)
                .toList();
    }

    private String safetySummary(Map<String, Object> response) {
        Object summary = response.get("summary");
        Object unsupportedClaims = response.get("unsupportedClaims");
        Object riskyClaims = response.get("riskyClaims");
        if (unsupportedClaims != null || riskyClaims != null) {
            return "已记录内容审核字段；unsupportedClaims="
                    + compact(String.valueOf(unsupportedClaims), 240)
                    + "；riskyClaims="
                    + compact(String.valueOf(riskyClaims), 240);
        }
        if (summary != null) {
            return "已保存 Agent 输出摘要，前端可结合引用字段复核：" + compact(String.valueOf(summary), 360);
        }
        return "已保存 Agent 原始结构化产物，建议前端展示引用、摘要和 traceId。";
    }

    private String writeJson(Object value) {
        if (value == null) {
            return "[]";
        }
        try {
            return objectMapper.writeValueAsString(value);
        } catch (JsonProcessingException ex) {
            return "\"" + compact(String.valueOf(value), 1000).replace("\"", "\\\"") + "\"";
        }
    }

    private Long elapsedMs(long startNanos) {
        return (System.nanoTime() - startNanos) / 1_000_000;
    }

    private String textValue(Object value) {
        return value == null ? null : compact(String.valueOf(value), 180);
    }

    private boolean hasText(String value) {
        return value != null && !value.isBlank();
    }

    private String valueOrFallback(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }

    private String compact(String value, int limit) {
        if (value == null) {
            return null;
        }
        String normalized = value.replaceAll("\\s+", " ").trim();
        if (normalized.length() <= limit) {
            return normalized;
        }
        return normalized.substring(0, Math.max(0, limit - 3)).trim() + "...";
    }
}
