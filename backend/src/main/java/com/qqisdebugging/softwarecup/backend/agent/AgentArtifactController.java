package com.qqisdebugging.softwarecup.backend.agent;

import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/agent-artifacts")
public class AgentArtifactController {
    private final AgentArtifactService artifactService;

    public AgentArtifactController(AgentArtifactService artifactService) {
        this.artifactService = artifactService;
    }

    @GetMapping
    List<AgentArtifactResponse> listArtifacts(
            @RequestParam(required = false) String studentProfileId,
            @RequestParam(required = false) String courseId,
            @RequestParam(required = false) String artifactType) {
        return artifactService.listArtifacts(studentProfileId, courseId, artifactType);
    }
}
