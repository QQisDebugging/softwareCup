package com.qqisdebugging.softwarecup.backend.task;

import java.time.Instant;

public record TaskStepResponse(
        String id,
        String taskId,
        String agentKey,
        Integer stepOrder,
        String stepName,
        String status,
        String inputSummary,
        String outputSummary,
        Integer progressPercent,
        Instant startedAt,
        Instant finishedAt,
        Long durationMs,
        String errorMessage,
        Instant updatedAt) {
    public static TaskStepResponse from(TaskStep step) {
        return new TaskStepResponse(
                step.getId(),
                step.getTaskId(),
                step.getAgentKey(),
                step.getStepOrder(),
                step.getStepName(),
                step.getStatus(),
                step.getInputSummary(),
                step.getOutputSummary(),
                step.getProgressPercent(),
                step.getStartedAt(),
                step.getFinishedAt(),
                step.getDurationMs(),
                step.getErrorMessage(),
                step.getUpdatedAt());
    }
}
