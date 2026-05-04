package com.qqisdebugging.softwarecup.backend.task;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "generation_tasks")
public class GenerationTask {
    @Id
    @Column(length = 36)
    private String id;

    @Column(length = 36)
    private String studentProfileId;

    @Column(length = 36)
    private String courseId;

    @Column(nullable = false, length = 80)
    private String taskType;

    @Column(nullable = false, length = 40)
    private String status;

    @Column(nullable = false, length = 180)
    private String topic;

    @Column(nullable = false, columnDefinition = "text")
    private String prompt;

    @Column(columnDefinition = "text")
    private String resultSummary;

    @Column(columnDefinition = "text")
    private String errorMessage;

    @Column(length = 36)
    private String createdResourceId;

    @Column(nullable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private Instant updatedAt;

    protected GenerationTask() {
    }

    public GenerationTask(String studentProfileId, String courseId, String topic, String prompt) {
        this.studentProfileId = studentProfileId;
        this.courseId = courseId;
        this.taskType = "RESOURCE_GENERATION";
        this.status = TaskStatus.PENDING.name();
        this.topic = topic;
        this.prompt = prompt;
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

    public void markRunning() {
        status = TaskStatus.RUNNING.name();
    }

    public void markSucceeded(String resourceId, String summary) {
        status = TaskStatus.SUCCEEDED.name();
        createdResourceId = resourceId;
        resultSummary = summary;
        errorMessage = null;
    }

    public void markFailed(String message) {
        status = TaskStatus.FAILED.name();
        errorMessage = message;
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

    public String getTaskType() {
        return taskType;
    }

    public String getStatus() {
        return status;
    }

    public String getTopic() {
        return topic;
    }

    public String getPrompt() {
        return prompt;
    }

    public String getResultSummary() {
        return resultSummary;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public String getCreatedResourceId() {
        return createdResourceId;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }
}
