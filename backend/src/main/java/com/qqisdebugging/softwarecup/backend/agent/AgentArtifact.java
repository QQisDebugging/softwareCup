package com.qqisdebugging.softwarecup.backend.agent;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "agent_artifacts")
public class AgentArtifact {
    @Id
    @Column(length = 36)
    private String id;

    @Column(length = 36)
    private String studentProfileId;

    @Column(length = 36)
    private String courseId;

    @Column(nullable = false, length = 80)
    private String artifactType;

    @Column(nullable = false, length = 160)
    private String agentEndpoint;

    @Column(length = 180)
    private String topic;

    @Column(nullable = false, length = 80)
    private String status;

    @Column(nullable = false, columnDefinition = "text")
    private String requestSummary;

    @Column(nullable = false, columnDefinition = "text")
    private String payloadJson;

    @Column(nullable = false, columnDefinition = "text")
    private String citationsJson;

    @Column(nullable = false, columnDefinition = "text")
    private String safetySummary;

    @Column(length = 120)
    private String traceId;

    private Long latencyMs;

    @Column(columnDefinition = "text")
    private String errorMessage;

    @Column(nullable = false)
    private Instant createdAt;

    protected AgentArtifact() {
    }

    public AgentArtifact(
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
            String errorMessage) {
        this.studentProfileId = studentProfileId;
        this.courseId = courseId;
        this.artifactType = artifactType;
        this.agentEndpoint = agentEndpoint;
        this.topic = topic;
        this.status = status;
        this.requestSummary = requestSummary;
        this.payloadJson = payloadJson;
        this.citationsJson = citationsJson;
        this.safetySummary = safetySummary;
        this.traceId = traceId;
        this.latencyMs = latencyMs;
        this.errorMessage = errorMessage;
    }

    @PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID().toString();
        }
        createdAt = Instant.now();
    }

    public String getId() {
        return id;
    }

    public String getStudentProfileId() {
        return studentProfileId;
    }

    public String getCourseId() {
        return courseId;
    }

    public String getArtifactType() {
        return artifactType;
    }

    public String getAgentEndpoint() {
        return agentEndpoint;
    }

    public String getTopic() {
        return topic;
    }

    public String getStatus() {
        return status;
    }

    public String getRequestSummary() {
        return requestSummary;
    }

    public String getPayloadJson() {
        return payloadJson;
    }

    public String getCitationsJson() {
        return citationsJson;
    }

    public String getSafetySummary() {
        return safetySummary;
    }

    public String getTraceId() {
        return traceId;
    }

    public Long getLatencyMs() {
        return latencyMs;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
