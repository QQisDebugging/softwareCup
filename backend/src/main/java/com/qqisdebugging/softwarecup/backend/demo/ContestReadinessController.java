package com.qqisdebugging.softwarecup.backend.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/demo")
public class ContestReadinessController {
    private final ContestReadinessService readinessService;

    public ContestReadinessController(ContestReadinessService readinessService) {
        this.readinessService = readinessService;
    }

    @GetMapping("/readiness-report")
    ContestReadinessResponse readinessReport(
            @RequestParam(required = false) String studentProfileId,
            @RequestParam(required = false) String courseId,
            @RequestParam(required = false) String taskId) {
        return readinessService.buildReport(studentProfileId, courseId, taskId);
    }
}
