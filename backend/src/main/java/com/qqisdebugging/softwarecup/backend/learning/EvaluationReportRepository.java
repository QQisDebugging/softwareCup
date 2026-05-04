package com.qqisdebugging.softwarecup.backend.learning;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface EvaluationReportRepository extends JpaRepository<EvaluationReport, String> {
    List<EvaluationReport> findTop20ByStudentProfileIdAndCourseIdOrderByCreatedAtDesc(String studentProfileId, String courseId);
}
