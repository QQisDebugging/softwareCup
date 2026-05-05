package com.qqisdebugging.softwarecup.backend.agent;

import java.util.Map;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AgentProxyController {
    private final AgentArtifactService artifactService;

    public AgentProxyController(AgentArtifactService artifactService) {
        this.artifactService = artifactService;
    }

    @PostMapping("/api/learning/path-plans")
    Map<String, Object> planPath(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("LEARNING_PATH_PLAN", "/agents/path/plan", request);
    }

    @PostMapping("/api/learning/knowledge-graphs")
    Map<String, Object> buildKnowledgeGraph(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("KNOWLEDGE_GRAPH", "/agents/knowledge/graph", request);
    }

    @PostMapping("/api/learning/content-audits")
    Map<String, Object> auditContent(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("CONTENT_AUDIT", "/agents/safety/audit", request);
    }

    @PostMapping("/api/teaching/course-diagnostics")
    Map<String, Object> diagnoseCourse(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("COURSE_DIAGNOSIS", "/agents/course/diagnose", request);
    }

    @PostMapping("/api/learning/code-practice/generate")
    Map<String, Object> generateCodePractice(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("CODE_PRACTICE", "/agents/code/practice/generate", request);
    }

    @PostMapping("/api/learning/code-practice/grade")
    Map<String, Object> gradeCodePractice(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("CODE_PRACTICE_GRADE", "/agents/code/practice/grade", request);
    }

    @PostMapping("/api/learning/storyboards")
    Map<String, Object> createStoryboard(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("MULTIMODAL_STORYBOARD", "/agents/multimodal/storyboard", request);
    }

    @PostMapping("/api/learning/prerequisites/diagnose")
    Map<String, Object> diagnosePrerequisites(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("PREREQUISITE_DIAGNOSIS", "/agents/prerequisite/diagnose", request);
    }

    @PostMapping("/api/learning/resource-bundles/curate")
    Map<String, Object> curateResourceBundle(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("RESOURCE_BUNDLE", "/agents/resources/curate", request);
    }

    @PostMapping("/api/learning/portfolio-reports")
    Map<String, Object> createPortfolioReport(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("PORTFOLIO_REPORT", "/agents/report/portfolio", request);
    }

    @PostMapping("/api/learning/agent-traces")
    Map<String, Object> explainAgentTrace(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("AGENT_TRACE", "/agents/trace/explain", request);
    }

    @PostMapping("/api/profiles/agent-infer")
    Map<String, Object> inferProfile(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("PROFILE_INFERENCE", "/agents/profile/infer", request);
    }

    @PostMapping("/api/learning/events/analyze")
    Map<String, Object> analyzeLearningEvents(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("LEARNING_EVENT_ANALYSIS", "/agents/learning/events/analyze", request);
    }

    @PostMapping("/api/learning/assessments/item-analysis")
    Map<String, Object> analyzeAssessmentItems(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("ASSESSMENT_ITEM_ANALYSIS", "/agents/assessment/item-analysis", request);
    }

    @PostMapping("/api/learning/code-projects/review")
    Map<String, Object> reviewCodeProject(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("CODE_PROJECT_REVIEW", "/agents/code/project-review", request);
    }

    @PostMapping("/api/teaching/class-analytics")
    Map<String, Object> analyzeClass(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("CLASS_ANALYTICS", "/agents/class/analytics", request);
    }

    @PostMapping("/api/demo/scenario-plans")
    Map<String, Object> planDemoScenario(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("DEMO_SCENARIO_PLAN", "/agents/demo/scenario-plan", request);
    }
}
