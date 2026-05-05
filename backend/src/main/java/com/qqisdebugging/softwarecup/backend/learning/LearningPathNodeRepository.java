package com.qqisdebugging.softwarecup.backend.learning;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface LearningPathNodeRepository extends JpaRepository<LearningPathNode, String> {
    List<LearningPathNode> findByPathIdOrderByNodeOrderAsc(String pathId);
}
