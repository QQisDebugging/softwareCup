package com.qqisdebugging.softwarecup.backend.task;

import java.time.Instant;

public record GenerationTaskResponse(
        String id,
        String studentProfileId,
        String courseId,
        String taskType,
        String status,
        String topic,
        String prompt,
        String resultSummary,
        String errorMessage,
        String createdResourceId,
        Integer progressPercent,
        String currentStep,
        Instant createdAt,
        Instant updatedAt) {
    static GenerationTaskResponse from(GenerationTask task) {
        return new GenerationTaskResponse(
                task.getId(),
                task.getStudentProfileId(),
                task.getCourseId(),
                task.getTaskType(),
                task.getStatus(),
                task.getTopic(),
                task.getPrompt(),
                task.getResultSummary(),
                task.getErrorMessage(),
                task.getCreatedResourceId(),
                task.getProgressPercent(),
                task.getCurrentStep(),
                task.getCreatedAt(),
                task.getUpdatedAt());
    }
}
