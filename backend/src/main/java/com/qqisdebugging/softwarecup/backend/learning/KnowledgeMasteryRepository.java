package com.qqisdebugging.softwarecup.backend.learning;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface KnowledgeMasteryRepository extends JpaRepository<KnowledgeMastery, String> {
    List<KnowledgeMastery> findByStudentProfileIdAndCourseIdOrderByKnowledgePointAsc(String studentProfileId, String courseId);

    Optional<KnowledgeMastery> findByStudentProfileIdAndCourseIdAndKnowledgePoint(
            String studentProfileId,
            String courseId,
            String knowledgePoint);
}
