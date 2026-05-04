package com.qqisdebugging.softwarecup.backend.profile;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import java.math.BigDecimal;

public record ProfileDimensionRequest(
        @NotBlank String dimensionKey,
        String dimensionName,
        @NotBlank String value,
        String evidence,
        @DecimalMin("0.00") @DecimalMax("1.00") BigDecimal confidenceScore,
        String source) {
}
