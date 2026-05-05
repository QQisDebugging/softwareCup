package com.qqisdebugging.softwarecup.backend.agent;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AgentDefinitionRepository extends JpaRepository<AgentDefinition, String> {
    List<AgentDefinition> findByEnabledTrueOrderBySortOrderAsc();
}
