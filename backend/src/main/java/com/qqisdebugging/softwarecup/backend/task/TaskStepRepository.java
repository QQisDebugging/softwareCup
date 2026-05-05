package com.qqisdebugging.softwarecup.backend.task;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TaskStepRepository extends JpaRepository<TaskStep, String> {
    List<TaskStep> findByTaskIdOrderByStepOrderAsc(String taskId);

    Optional<TaskStep> findByTaskIdAndAgentKey(String taskId, String agentKey);
}
