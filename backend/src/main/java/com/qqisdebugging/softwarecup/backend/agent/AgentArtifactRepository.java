package com.qqisdebugging.softwarecup.backend.agent;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AgentArtifactRepository extends JpaRepository<AgentArtifact, String> {
    List<AgentArtifact> findTop50ByOrderByCreatedAtDesc();

    List<AgentArtifact> findTop50ByStudentProfileIdOrderByCreatedAtDesc(String studentProfileId);

    List<AgentArtifact> findTop50ByCourseIdOrderByCreatedAtDesc(String courseId);

    List<AgentArtifact> findTop50ByArtifactTypeOrderByCreatedAtDesc(String artifactType);

    List<AgentArtifact> findTop50ByStudentProfileIdAndCourseIdOrderByCreatedAtDesc(
            String studentProfileId,
            String courseId);
}
