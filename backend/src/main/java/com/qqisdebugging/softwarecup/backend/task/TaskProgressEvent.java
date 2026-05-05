package com.qqisdebugging.softwarecup.backend.task;

import java.time.Instant;

public record TaskProgressEvent(
        String taskId,
        String eventType,
        Integer progressPercent,
        String currentStep,
        String status,
        String message,
        Instant timestamp) {
    public static TaskProgressEvent of(
            String taskId,
            String eventType,
            Integer progressPercent,
            String currentStep,
            String status,
            String message) {
        return new TaskProgressEvent(taskId, eventType, progressPercent, currentStep, status, message, Instant.now());
    }
}
