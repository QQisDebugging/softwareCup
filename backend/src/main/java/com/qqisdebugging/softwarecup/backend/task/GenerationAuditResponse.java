package com.qqisdebugging.softwarecup.backend.task;

import java.time.Instant;

public record GenerationAuditResponse(
        String id,
        String taskId,
        String resourceId,
        String auditType,
        String status,
        String evidenceSummary,
        Boolean reviewerRequired,
        Instant createdAt) {
    public static GenerationAuditResponse from(GenerationAudit audit) {
        return new GenerationAuditResponse(
                audit.getId(),
                audit.getTaskId(),
                audit.getResourceId(),
                audit.getAuditType(),
                audit.getStatus(),
                audit.getEvidenceSummary(),
                audit.getReviewerRequired(),
                audit.getCreatedAt());
    }
}
