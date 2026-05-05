package com.qqisdebugging.softwarecup.backend.learning;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface LearningPathRepository extends JpaRepository<LearningPath, String> {
    List<LearningPath> findByStudentProfileIdOrderByCreatedAtDesc(String studentProfileId);

    List<LearningPath> findByStudentProfileIdAndCourseIdOrderByCreatedAtDesc(String studentProfileId, String courseId);
}
