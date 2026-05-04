package com.qqisdebugging.softwarecup.backend.profile;

import java.time.Instant;

public record ProfileHistoryResponse(
        String id,
        String profileId,
        String eventType,
        String dimensionKey,
        String previousValue,
        String newValue,
        String evidence,
        String source,
        Instant createdAt) {
    static ProfileHistoryResponse from(ProfileHistory history) {
        return new ProfileHistoryResponse(
                history.getId(),
                history.getProfileId(),
                history.getEventType(),
                history.getDimensionKey(),
                history.getPreviousValue(),
                history.getNewValue(),
                history.getEvidence(),
                history.getSource(),
                history.getCreatedAt());
    }
}
