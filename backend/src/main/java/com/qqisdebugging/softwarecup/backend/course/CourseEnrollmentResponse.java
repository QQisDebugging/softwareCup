package com.qqisdebugging.softwarecup.backend.course;

import java.time.Instant;

public record CourseEnrollmentResponse(
        String id,
        String courseId,
        String studentProfileId,
        String status,
        Instant createdAt,
        Instant updatedAt,
        CourseResponse course) {
    static CourseEnrollmentResponse from(CourseEnrollment enrollment, Course course) {
        return new CourseEnrollmentResponse(
                enrollment.getId(),
                enrollment.getCourseId(),
                enrollment.getStudentProfileId(),
                enrollment.getStatus(),
                enrollment.getCreatedAt(),
                enrollment.getUpdatedAt(),
                CourseResponse.from(course));
    }
}
