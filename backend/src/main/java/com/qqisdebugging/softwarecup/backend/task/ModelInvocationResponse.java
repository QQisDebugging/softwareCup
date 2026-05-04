package com.qqisdebugging.softwarecup.backend.task;

import java.time.Instant;

public record ModelInvocationResponse(
        String id,
        String taskId,
        String stepId,
        String provider,
        String modelName,
        String promptHash,
        String promptSummary,
        Long latencyMs,
        String status,
        Boolean fallbackUsed,
        String errorMessage,
        Instant createdAt) {
    public static ModelInvocationResponse from(ModelInvocation invocation) {
        return new ModelInvocationResponse(
                invocation.getId(),
                invocation.getTaskId(),
                invocation.getStepId(),
                invocation.getProvider(),
                invocation.getModelName(),
                invocation.getPromptHash(),
                invocation.getPromptSummary(),
                invocation.getLatencyMs(),
                invocation.getStatus(),
                invocation.getFallbackUsed(),
                invocation.getErrorMessage(),
                invocation.getCreatedAt());
    }
}
