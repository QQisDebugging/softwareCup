package com.qqisdebugging.softwarecup.backend.profile;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import java.util.List;

public record UpdateProfileDimensionsRequest(
        @Valid @NotEmpty List<ProfileDimensionRequest> dimensions,
        String reason) {
}
