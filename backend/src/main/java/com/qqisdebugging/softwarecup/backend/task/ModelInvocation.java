package com.qqisdebugging.softwarecup.backend.task;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "model_invocations")
public class ModelInvocation {
    @Id
    @Column(length = 36)
    private String id;

    @Column(length = 36)
    private String taskId;

    @Column(length = 36)
    private String stepId;

    @Column(nullable = false, length = 80)
    private String provider;

    @Column(nullable = false, length = 120)
    private String modelName;

    @Column(nullable = false, length = 80)
    private String promptHash;

    @Column(nullable = false, columnDefinition = "text")
    private String promptSummary;

    private Long latencyMs;

    @Column(nullable = false, length = 40)
    private String status;

    @Column(nullable = false)
    private Boolean fallbackUsed;

    @Column(columnDefinition = "text")
    private String errorMessage;

    @Column(nullable = false)
    private Instant createdAt;

    protected ModelInvocation() {
    }

    public ModelInvocation(
            String taskId,
            String stepId,
            String provider,
            String modelName,
            String promptHash,
            String promptSummary,
            Long latencyMs,
            String status,
            Boolean fallbackUsed,
            String errorMessage) {
        this.taskId = taskId;
        this.stepId = stepId;
        this.provider = provider;
        this.modelName = modelName;
        this.promptHash = promptHash;
        this.promptSummary = promptSummary;
        this.latencyMs = latencyMs;
        this.status = status;
        this.fallbackUsed = fallbackUsed;
        this.errorMessage = errorMessage;
    }

    @jakarta.persistence.PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID().toString();
        }
        createdAt = Instant.now();
    }

    public String getId() {
        return id;
    }

    public String getTaskId() {
        return taskId;
    }

    public String getStepId() {
        return stepId;
    }

    public String getProvider() {
        return provider;
    }

    public String getModelName() {
        return modelName;
    }

    public String getPromptHash() {
        return promptHash;
    }

    public String getPromptSummary() {
        return promptSummary;
    }

    public Long getLatencyMs() {
        return latencyMs;
    }

    public String getStatus() {
        return status;
    }

    public Boolean getFallbackUsed() {
        return fallbackUsed;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
