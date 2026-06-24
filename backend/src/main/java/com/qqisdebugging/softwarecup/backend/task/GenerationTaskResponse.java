package com.qqisdebugging.softwarecup.backend.task;

import java.time.Instant;
import java.util.Map;

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
        Boolean hasPublishedResources,
        Boolean learningAvailable,
        Map<String, Object> uiAction,
        Integer progressPercent,
        String currentStep,
        Instant createdAt,
        Instant updatedAt) {
    static GenerationTaskResponse from(GenerationTask task) {
        return from(task, true);
    }

    static GenerationTaskResponse from(GenerationTask task, boolean hasPublishedResources) {
        boolean learningAvailable = TaskStatus.SUCCEEDED.name().equals(task.getStatus()) && hasPublishedResources;
        Map<String, Object> uiAction = Map.of(
                "kind", learningAvailable ? "OPEN_LEARNING" : "STAY_ON_TASK",
                "route", learningAvailable ? "/learning" : "",
                "reason", learningAvailable
                        ? "PUBLISHED_RESOURCE_AVAILABLE"
                        : "WAIT_FOR_PUBLISHED_RESOURCE");
        return new GenerationTaskResponse(
                task.getId(),
                task.getStudentProfileId(),
                task.getCourseId(),
                task.getTaskType(),
                task.getStatus(),
                task.getTopic(),
                task.getPrompt(),
                hasPublishedResources ? task.getResultSummary() : null,
                task.getErrorMessage(),
                task.getCreatedResourceId(),
                hasPublishedResources,
                learningAvailable,
                uiAction,
                task.getProgressPercent(),
                task.getCurrentStep(),
                task.getCreatedAt(),
                task.getUpdatedAt());
    }
}
