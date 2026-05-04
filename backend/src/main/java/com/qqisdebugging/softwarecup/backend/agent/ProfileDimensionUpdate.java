package com.qqisdebugging.softwarecup.backend.agent;

import java.math.BigDecimal;

public record ProfileDimensionUpdate(
        String dimensionKey,
        String dimensionName,
        String value,
        String evidence,
        BigDecimal confidenceScore,
        String source) {
}
