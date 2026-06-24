package com.qqisdebugging.softwarecup.backend.assignment;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AssignmentSubmissionRepository extends JpaRepository<AssignmentSubmission, String> {
    Optional<AssignmentSubmission> findByAssignmentIdAndStudentProfileId(String assignmentId, String studentProfileId);

    List<AssignmentSubmission> findByStudentProfileIdAndCourseId(String studentProfileId, String courseId);

    List<AssignmentSubmission> findByAssignmentId(String assignmentId);
}
