package com.qqisdebugging.softwarecup.backend.agent;

import java.util.Map;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AgentProxyController {
    private final ResourceAgentClient client;

    public AgentProxyController(ResourceAgentClient client) {
        this.client = client;
    }

    @PostMapping("/api/learning/path-plans")
    Map<String, Object> planPath(@RequestBody Map<String, Object> request) {
        return client.proxy("/agents/path/plan", request);
    }

    @PostMapping("/api/learning/knowledge-graphs")
    Map<String, Object> buildKnowledgeGraph(@RequestBody Map<String, Object> request) {
        return client.proxy("/agents/knowledge/graph", request);
    }

    @PostMapping("/api/learning/content-audits")
    Map<String, Object> auditContent(@RequestBody Map<String, Object> request) {
        return client.proxy("/agents/safety/audit", request);
    }

    @PostMapping("/api/teaching/course-diagnostics")
    Map<String, Object> diagnoseCourse(@RequestBody Map<String, Object> request) {
        return client.proxy("/agents/course/diagnose", request);
    }

    @PostMapping("/api/learning/code-practice/generate")
    Map<String, Object> generateCodePractice(@RequestBody Map<String, Object> request) {
        return client.proxy("/agents/code/practice/generate", request);
    }

    @PostMapping("/api/learning/code-practice/grade")
    Map<String, Object> gradeCodePractice(@RequestBody Map<String, Object> request) {
        return client.proxy("/agents/code/practice/grade", request);
    }

    @PostMapping("/api/learning/storyboards")
    Map<String, Object> createStoryboard(@RequestBody Map<String, Object> request) {
        return client.proxy("/agents/multimodal/storyboard", request);
    }

    @PostMapping("/api/learning/prerequisites/diagnose")
    Map<String, Object> diagnosePrerequisites(@RequestBody Map<String, Object> request) {
        return client.proxy("/agents/prerequisite/diagnose", request);
    }

    @PostMapping("/api/learning/resource-bundles/curate")
    Map<String, Object> curateResourceBundle(@RequestBody Map<String, Object> request) {
        return client.proxy("/agents/resources/curate", request);
    }

    @PostMapping("/api/learning/portfolio-reports")
    Map<String, Object> createPortfolioReport(@RequestBody Map<String, Object> request) {
        return client.proxy("/agents/report/portfolio", request);
    }

    @PostMapping("/api/learning/agent-traces")
    Map<String, Object> explainAgentTrace(@RequestBody Map<String, Object> request) {
        return client.proxy("/agents/trace/explain", request);
    }

    @PostMapping("/api/profiles/agent-infer")
    Map<String, Object> inferProfile(@RequestBody Map<String, Object> request) {
        return client.proxy("/agents/profile/infer", request);
    }

    @PostMapping("/api/learning/events/analyze")
    Map<String, Object> analyzeLearningEvents(@RequestBody Map<String, Object> request) {
        return client.proxy("/agents/learning/events/analyze", request);
    }

    @PostMapping("/api/learning/assessments/item-analysis")
    Map<String, Object> analyzeAssessmentItems(@RequestBody Map<String, Object> request) {
        return client.proxy("/agents/assessment/item-analysis", request);
    }

    @PostMapping("/api/learning/code-projects/review")
    Map<String, Object> reviewCodeProject(@RequestBody Map<String, Object> request) {
        return client.proxy("/agents/code/project-review", request);
    }

    @PostMapping("/api/teaching/class-analytics")
    Map<String, Object> analyzeClass(@RequestBody Map<String, Object> request) {
        return client.proxy("/agents/class/analytics", request);
    }

    @PostMapping("/api/demo/scenario-plans")
    Map<String, Object> planDemoScenario(@RequestBody Map<String, Object> request) {
        return client.proxy("/agents/demo/scenario-plan", request);
    }
}
