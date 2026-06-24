package com.qqisdebugging.softwarecup.backend.course;

import jakarta.validation.constraints.NotBlank;

public record JoinCourseRequest(@NotBlank String studentProfileId) {
}
