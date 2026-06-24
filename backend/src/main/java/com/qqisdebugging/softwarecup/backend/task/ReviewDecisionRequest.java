package com.qqisdebugging.softwarecup.backend.task;

import jakarta.validation.constraints.NotNull;

public record ReviewDecisionRequest(
        @NotNull ReviewDecision decision,
        String reviewer,
        String note) {
}
