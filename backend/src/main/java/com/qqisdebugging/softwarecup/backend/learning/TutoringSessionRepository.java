package com.qqisdebugging.softwarecup.backend.learning;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TutoringSessionRepository extends JpaRepository<TutoringSession, String> {
    List<TutoringSession> findTop30ByStudentProfileIdOrderByCreatedAtDesc(String studentProfileId);
}
