package com.qqisdebugging.softwarecup.backend.task;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "generation_audits")
public class GenerationAudit {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 36)
    private String taskId;

    @Column(length = 36)
    private String resourceId;

    @Column(nullable = false, length = 80)
    private String auditType;

    @Column(nullable = false, length = 40)
    private String status;

    @Column(nullable = false, columnDefinition = "text")
    private String evidenceSummary;

    @Column(nullable = false)
    private Boolean reviewerRequired;

    @Column(nullable = false)
    private Instant createdAt;

    protected GenerationAudit() {
    }

    public GenerationAudit(
            String taskId,
            String resourceId,
            String auditType,
            String status,
            String evidenceSummary,
            Boolean reviewerRequired) {
        this.taskId = taskId;
        this.resourceId = resourceId;
        this.auditType = auditType;
        this.status = status;
        this.evidenceSummary = evidenceSummary;
        this.reviewerRequired = reviewerRequired;
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

    public String getResourceId() {
        return resourceId;
    }

    public String getAuditType() {
        return auditType;
    }

    public String getStatus() {
        return status;
    }

    public String getEvidenceSummary() {
        return evidenceSummary;
    }

    public Boolean getReviewerRequired() {
        return reviewerRequired;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
