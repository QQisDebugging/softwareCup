package com.qqisdebugging.softwarecup.backend.course;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record CreateCourseRequest(
        @NotBlank String title,
        @NotBlank String department,
        @NotBlank String description,
        @NotNull @Min(1) Integer creditHours,
        @NotBlank String syllabusJson) {
}
