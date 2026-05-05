package com.qqisdebugging.softwarecup.backend.task;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface GenerationAuditRepository extends JpaRepository<GenerationAudit, String> {
    List<GenerationAudit> findByTaskIdOrderByCreatedAtDesc(String taskId);
}
