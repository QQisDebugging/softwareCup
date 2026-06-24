package com.qqisdebugging.softwarecup.backend.learning;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface LearningConversationRepository extends JpaRepository<LearningConversation, String> {
    List<LearningConversation> findByStudentProfileIdAndArchivedOrderByUpdatedAtDesc(
            String studentProfileId,
            Boolean archived);

    List<LearningConversation> findByStudentProfileIdAndCourseIdAndArchivedOrderByUpdatedAtDesc(
            String studentProfileId,
            String courseId,
            Boolean archived);
}
