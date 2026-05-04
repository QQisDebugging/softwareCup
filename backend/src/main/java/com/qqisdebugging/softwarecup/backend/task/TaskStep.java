package com.qqisdebugging.softwarecup.backend.task;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Duration;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "task_steps")
public class TaskStep {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 36)
    private String taskId;

    @Column(nullable = false, length = 80)
    private String agentKey;

    @Column(nullable = false)
    private Integer stepOrder;

    @Column(nullable = false, length = 120)
    private String stepName;

    @Column(nullable = false, length = 40)
    private String status;

    @Column(columnDefinition = "text")
    private String inputSummary;

    @Column(columnDefinition = "text")
    private String outputSummary;

    @Column(nullable = false)
    private Integer progressPercent;

    private Instant startedAt;

    private Instant finishedAt;

    private Long durationMs;

    @Column(columnDefinition = "text")
    private String errorMessage;

    @Column(nullable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private Instant updatedAt;

    protected TaskStep() {
    }

    public TaskStep(String taskId, String agentKey, Integer stepOrder, String stepName, Integer progressPercent) {
        this.taskId = taskId;
        this.agentKey = agentKey;
        this.stepOrder = stepOrder;
        this.stepName = stepName;
        this.progressPercent = progressPercent;
        this.status = TaskStepStatus.PENDING.name();
    }

    @jakarta.persistence.PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID().toString();
        }
        Instant now = Instant.now();
        createdAt = now;
        updatedAt = now;
    }

    @jakarta.persistence.PreUpdate
    void preUpdate() {
        updatedAt = Instant.now();
    }

    public void start(String inputSummary) {
        this.status = TaskStepStatus.RUNNING.name();
        this.inputSummary = inputSummary;
        this.startedAt = Instant.now();
        this.errorMessage = null;
    }

    public void succeed(String outputSummary) {
        this.status = TaskStepStatus.SUCCEEDED.name();
        this.outputSummary = outputSummary;
        this.finishedAt = Instant.now();
        if (startedAt != null) {
            this.durationMs = Duration.between(startedAt, finishedAt).toMillis();
        }
    }

    public void fail(String message) {
        this.status = TaskStepStatus.FAILED.name();
        this.errorMessage = message;
        this.finishedAt = Instant.now();
        if (startedAt != null) {
            this.durationMs = Duration.between(startedAt, finishedAt).toMillis();
        }
    }

    public String getId() {
        return id;
    }

    public String getTaskId() {
        return taskId;
    }

    public String getAgentKey() {
        return agentKey;
    }

    public Integer getStepOrder() {
        return stepOrder;
    }

    public String getStepName() {
        return stepName;
    }

    public String getStatus() {
        return status;
    }

    public String getInputSummary() {
        return inputSummary;
    }

    public String getOutputSummary() {
        return outputSummary;
    }

    public Integer getProgressPercent() {
        return progressPercent;
    }

    public Instant getStartedAt() {
        return startedAt;
    }

    public Instant getFinishedAt() {
        return finishedAt;
    }

    public Long getDurationMs() {
        return durationMs;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }
}
