package com.qqisdebugging.softwarecup.backend.course;

import java.time.Instant;

public record CourseResponse(
        String id,
        String title,
        String department,
        String description,
        Integer creditHours,
        String syllabusJson,
        Instant createdAt,
        Instant updatedAt) {
    static CourseResponse from(Course course) {
        return new CourseResponse(
                course.getId(),
                course.getTitle(),
                course.getDepartment(),
                course.getDescription(),
                course.getCreditHours(),
                course.getSyllabusJson(),
                course.getCreatedAt(),
                course.getUpdatedAt());
    }
}
