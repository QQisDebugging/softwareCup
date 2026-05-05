package com.qqisdebugging.softwarecup.backend.agent;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import java.util.Map;
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
        String studentProfileId = textValue(request.get("studentProfileId"));
        String courseId = textValue(request.get("courseId"));
        String topic = textValue(request.get("topic"));
        String traceId = textValue(request.get("traceId"));
        try {
            Map<String, Object> response = client.proxy(agentEndpoint, request);
            repository.save(new AgentArtifact(
                    studentProfileId,
                    courseId,
                    artifactType,
                    agentEndpoint,
                    topic,
                    "SUCCEEDED",
                    compact(writeJson(request), 1200),
                    writeJson(response),
                    writeJson(response.get("citations")),
                    safetySummary(response),
                    traceId,
                    elapsedMs(start),
                    null));
            return response;
        } catch (RestClientException ex) {
            repository.save(new AgentArtifact(
                    studentProfileId,
                    courseId,
                    artifactType,
                    agentEndpoint,
                    topic,
                    "FAILED",
                    compact(writeJson(request), 1200),
                    "{}",
                    "[]",
                    "代理调用失败，未形成可审核产物。",
                    traceId,
                    elapsedMs(start),
                    compact(ex.getMessage(), 2000)));
            throw ex;
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
