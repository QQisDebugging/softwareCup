package com.qqisdebugging.softwarecup.backend.learning;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ResourceRecommendationRepository extends JpaRepository<ResourceRecommendation, String> {
    List<ResourceRecommendation> findByStudentProfileIdOrderByCreatedAtDesc(String studentProfileId);
}
