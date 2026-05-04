package com.qqisdebugging.softwarecup.backend.profile;

import java.math.BigDecimal;
import java.time.Instant;

public record ProfileDimensionResponse(
        String id,
        String profileId,
        String dimensionKey,
        String dimensionName,
        String value,
        String evidence,
        BigDecimal confidenceScore,
        String source,
        Instant createdAt,
        Instant updatedAt) {
    static ProfileDimensionResponse from(ProfileDimension dimension) {
        return new ProfileDimensionResponse(
                dimension.getId(),
                dimension.getProfileId(),
                dimension.getDimensionKey(),
                dimension.getDimensionName(),
                dimension.getDimensionValue(),
                dimension.getEvidence(),
                dimension.getConfidenceScore(),
                dimension.getSource(),
                dimension.getCreatedAt(),
                dimension.getUpdatedAt());
    }
}
