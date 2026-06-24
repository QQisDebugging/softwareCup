package com.qqisdebugging.softwarecup.backend.course;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CourseEnrollmentRepository extends JpaRepository<CourseEnrollment, String> {
    Optional<CourseEnrollment> findByCourseIdAndStudentProfileId(String courseId, String studentProfileId);

    List<CourseEnrollment> findByStudentProfileIdAndStatusOrderByCreatedAtDesc(String studentProfileId, String status);

    long countByCourseId(String courseId);
}
