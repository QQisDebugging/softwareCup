package com.qqisdebugging.softwarecup.backend.learning;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CourseDoubtRecordRepository extends JpaRepository<CourseDoubtRecord, String> {
    List<CourseDoubtRecord> findByStudentProfileIdAndCourseIdOrderByCreatedAtDesc(
            String studentProfileId, String courseId);

    List<CourseDoubtRecord> findByCourseIdOrderByCreatedAtDesc(String courseId);
}
