package com.qqisdebugging.softwarecup.backend.agent;

import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/agents")
public class AgentDefinitionController {
    private final AgentDefinitionRepository repository;

    public AgentDefinitionController(AgentDefinitionRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    List<AgentDefinitionResponse> listAgents() {
        return repository.findByEnabledTrueOrderBySortOrderAsc().stream()
                .map(AgentDefinitionResponse::from)
                .toList();
    }
}
