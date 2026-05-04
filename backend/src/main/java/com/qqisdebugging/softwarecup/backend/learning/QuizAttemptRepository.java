package com.qqisdebugging.softwarecup.backend.learning;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface QuizAttemptRepository extends JpaRepository<QuizAttempt, String> {
    List<QuizAttempt> findTop30ByStudentProfileIdOrderByCreatedAtDesc(String studentProfileId);
}
