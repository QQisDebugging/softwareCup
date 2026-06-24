package com.qqisdebugging.softwarecup.backend.task;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface GenerationTaskRepository extends JpaRepository<GenerationTask, String>, JpaSpecificationExecutor<GenerationTask> {
    List<GenerationTask> findTop50ByOrderByCreatedAtDesc();
}
