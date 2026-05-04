package com.qqisdebugging.softwarecup.backend.learning;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface LearningEventRepository extends JpaRepository<LearningEvent, String> {
    List<LearningEvent> findTop50ByStudentProfileIdOrderByCreatedAtDesc(String studentProfileId);
}
