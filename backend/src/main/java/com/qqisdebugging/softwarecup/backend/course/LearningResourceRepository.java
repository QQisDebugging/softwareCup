package com.qqisdebugging.softwarecup.backend.course;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface LearningResourceRepository extends JpaRepository<LearningResource, String> {
    List<LearningResource> findByCourseIdOrderByCreatedAtDesc(String courseId);

    List<LearningResource> findByCourseIdAndReviewStatusOrderByCreatedAtDesc(String courseId, String reviewStatus);

    List<LearningResource> findByCourseIdAndReviewStatusInOrderByCreatedAtDesc(String courseId, List<String> reviewStatuses);

    List<LearningResource> findBySourceTaskIdOrderByCreatedAtDesc(String sourceTaskId);
}
