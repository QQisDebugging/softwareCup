package com.qqisdebugging.softwarecup.backend.task;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ModelInvocationRepository extends JpaRepository<ModelInvocation, String> {
    List<ModelInvocation> findByTaskIdOrderByCreatedAtDesc(String taskId);
}
