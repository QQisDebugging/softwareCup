package com.qqisdebugging.softwarecup.backend.task;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface GenerationTaskRepository extends JpaRepository<GenerationTask, String> {
    List<GenerationTask> findTop50ByOrderByCreatedAtDesc();
}
