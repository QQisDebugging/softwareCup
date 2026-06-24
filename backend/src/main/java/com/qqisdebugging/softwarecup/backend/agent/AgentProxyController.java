package com.qqisdebugging.softwarecup.backend.agent;

import com.qqisdebugging.softwarecup.backend.course.Course;
import com.qqisdebugging.softwarecup.backend.course.CourseService;
import com.qqisdebugging.softwarecup.backend.course.TeacherClassResponse;
import com.qqisdebugging.softwarecup.backend.profile.ProfileService;
import com.qqisdebugging.softwarecup.backend.profile.StudentProfile;
import java.util.List;
import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AgentProxyController {
    private final AgentArtifactService artifactService;
    private final ResourceAgentClient resourceAgentClient;
    private final ProfileService profileService;
    private final CourseService courseService;

    public AgentProxyController(
            AgentArtifactService artifactService,
            ResourceAgentClient resourceAgentClient,
            ProfileService profileService,
            CourseService courseService) {
        this.artifactService = artifactService;
        this.resourceAgentClient = resourceAgentClient;
        this.profileService = profileService;
        this.courseService = courseService;
    }

    @GetMapping("/api/agents/providers/status")
    Map<String, Object> providerStatus() {
        try {
            Map<String, Object> status = new LinkedHashMap<>(resourceAgentClient.providerStatus());
            status.put("serviceOnline", true);
            status.put("agentReady", agentReady(status));
            status.putIfAbsent("uiAction", Map.of("kind", "NONE", "reason", "PROVIDER_STATUS_ONLY"));
            return status;
        } catch (RuntimeException ex) {
            Map<String, Object> status = new LinkedHashMap<>();
            status.put("serviceOnline", false);
            status.put("agentReady", false);
            status.put("configuredProvider", "unreachable");
            status.put("activeProvider", "unavailable");
            status.put("xfyunConfigured", false);
            status.put("fallbackProvider", "none");
            status.put("lastError", ex.getMessage() == null ? ex.getClass().getSimpleName() : ex.getMessage());
            return status;
        }
    }

    @PostMapping("/api/agents/providers/config")
    Map<String, Object> updateProviderConfig(@RequestBody Map<String, Object> request) {
        Map<String, Object> result = new LinkedHashMap<>(resourceAgentClient.providerConfig(request));
        result.put("serviceOnline", true);
        result.put("agentReady", agentReady(result));
        result.putIfAbsent("uiAction", Map.of("kind", "NONE", "reason", "PROVIDER_CONFIG_UPDATED"));
        return result;
    }

    @GetMapping("/api/teaching/classes")
    List<TeacherClassResponse> listTeacherClasses() {
        return courseService.listTeacherClasses();
    }

    private boolean agentReady(Map<String, Object> status) {
        Object lastError = status.get("lastError");
        if (lastError != null && !String.valueOf(lastError).isBlank()) {
            return false;
        }
        String activeProvider = String.valueOf(status.getOrDefault("activeProvider", status.get("configuredProvider")));
        if ("openai_compatible".equalsIgnoreCase(activeProvider)) {
            return Boolean.TRUE.equals(status.get("openaiConfigured"));
        }
        if (Boolean.FALSE.equals(status.get("xfyunConfigured"))) {
            return false;
        }
        int todayCalls = intValue(status.get("xfyunTodayCalls"), -1);
        int dailyLimit = intValue(status.get("xfyunDailyCallLimit"), intValue(status.get("xfyunDailyLimit"), -1));
        if (todayCalls >= 0 && dailyLimit >= 0 && todayCalls >= dailyLimit) {
            return false;
        }
        return true;
    }

    @PostMapping("/api/learning/path-plans")
    Map<String, Object> planPath(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore(
                "LEARNING_PATH_PLAN",
                "/agents/path/plan",
                requireFields(enrichAgentRequest(request), "studentProfileId", "courseId", "topic"));
    }

    @PostMapping("/api/learning/knowledge-graphs")
    Map<String, Object> buildKnowledgeGraph(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore(
                "KNOWLEDGE_GRAPH",
                "/agents/knowledge/graph",
                requireFields(enrichAgentRequest(request), "courseId", "topic"));
    }

    @PostMapping("/api/learning/content-audits")
    Map<String, Object> auditContent(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("CONTENT_AUDIT", "/agents/safety/audit", enrichAgentRequest(request));
    }

    @PostMapping("/api/teaching/course-diagnostics")
    Map<String, Object> diagnoseCourse(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore(
                "COURSE_DIAGNOSIS",
                "/agents/course/diagnose",
                requireFields(enrichAgentRequest(request), "courseId"));
    }

    @PostMapping("/api/teaching/course-structures")
    Map<String, Object> buildCourseStructure(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("COURSE_STRUCTURE", "/agents/course/structure", enrichAgentRequest(request));
    }

    @PostMapping("/api/learning/code-practice/generate")
    Map<String, Object> generateCodePractice(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("CODE_PRACTICE", "/agents/code/practice/generate", enrichAgentRequest(request));
    }

    @PostMapping("/api/learning/code-practice/grade")
    Map<String, Object> gradeCodePractice(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("CODE_PRACTICE_GRADE", "/agents/code/practice/grade", enrichAgentRequest(request));
    }

    @PostMapping("/api/learning/storyboards")
    Map<String, Object> createStoryboard(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("MULTIMODAL_STORYBOARD", "/agents/multimodal/storyboard", enrichAgentRequest(request));
    }

    @PostMapping("/api/learning/prerequisites/diagnose")
    Map<String, Object> diagnosePrerequisites(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("PREREQUISITE_DIAGNOSIS", "/agents/prerequisite/diagnose", enrichAgentRequest(request));
    }

    @PostMapping("/api/learning/resource-bundles/curate")
    Map<String, Object> curateResourceBundle(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore(
                "RESOURCE_BUNDLE",
                "/agents/resources/curate",
                requireFields(enrichAgentRequest(request), "studentProfileId", "courseId", "topic"));
    }

    @PostMapping("/api/learning/portfolio-reports")
    Map<String, Object> createPortfolioReport(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("PORTFOLIO_REPORT", "/agents/report/portfolio", enrichAgentRequest(request));
    }

    @PostMapping("/api/learning/agent-traces")
    Map<String, Object> explainAgentTrace(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("AGENT_TRACE", "/agents/trace/explain", enrichAgentRequest(request));
    }

    @PostMapping("/api/profiles/agent-infer")
    Map<String, Object> inferProfile(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("PROFILE_INFERENCE", "/agents/profile/infer", enrichAgentRequest(request));
    }

    @PostMapping("/api/learning/events/analyze")
    Map<String, Object> analyzeLearningEvents(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("LEARNING_EVENT_ANALYSIS", "/agents/learning/events/analyze", enrichAgentRequest(request));
    }

    @PostMapping("/api/learning/assessments/item-analysis")
    Map<String, Object> analyzeAssessmentItems(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("ASSESSMENT_ITEM_ANALYSIS", "/agents/assessment/item-analysis", enrichAgentRequest(request));
    }

    @PostMapping("/api/learning/code-projects/review")
    Map<String, Object> reviewCodeProject(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("CODE_PROJECT_REVIEW", "/agents/code/project-review", enrichAgentRequest(request));
    }

    @PostMapping("/api/teaching/class-analytics")
    Map<String, Object> analyzeClass(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore(
                "CLASS_ANALYTICS",
                "/agents/class/analytics",
                requireSnapshots(requireFields(enrichAgentRequest(request), "courseId")));
    }

    @PostMapping({"/api/teaching/scenario-plans", "/api/demo/scenario-plans"})
    Map<String, Object> planTeachingScenario(@RequestBody Map<String, Object> request) {
        return artifactService.invokeAndStore("TEACHING_SCENARIO_PLAN", "/agents/teaching/scenario-plan", enrichAgentRequest(request));
    }

    private Map<String, Object> enrichAgentRequest(Map<String, Object> request) {
        Map<String, Object> enriched = new LinkedHashMap<>();
        if (request != null) {
            enriched.putAll(request);
        }

        StudentProfile profile = loadProfile(text(enriched.get("studentProfileId")));
        Course course = loadCourse(text(enriched.get("courseId")));
        if (profile != null) {
            putIfBlank(enriched, "studentProfileSummary", profile.getDialogueSummary());
            putIfBlank(enriched, "studentName", profile.getStudentName());
            putIfBlank(enriched, "declaredMajor", profile.getMajor());
            putIfBlank(enriched, "currentLevel", profile.getCurrentLevel());
            putIfBlank(enriched, "learningGoal", profile.getLearningGoal());
            putIfBlank(enriched, "preferences", profile.getPreferences());
            putIfBlank(enriched, "constraintsText", profile.getConstraintsText());
        }
        if (course != null) {
            putIfBlank(enriched, "courseTitle", course.getTitle());
            putIfBlank(enriched, "courseDescription", course.getDescription());
            putIfBlank(enriched, "syllabusText", course.getSyllabusJson());
        }

        alias(enriched, "studentProfileSummary", "dialogueSummary");
        alias(enriched, "courseTitle", "courseName");
        alias(enriched, "topic", "targetTopic");
        alias(enriched, "targetTopic", "topic");
        alias(enriched, "goal", "targetOutcome");
        alias(enriched, "targetLevel", "currentLevel");
        putIfBlank(enriched, "courseDescription", text(enriched.get("courseTitle")));
        putIfBlank(enriched, "syllabusText", text(enriched.get("courseDescription")));
        putIfBlank(enriched, "projectTitle", text(enriched.get("topic")));
        putIfBlank(enriched, "userIntent", text(enriched.get("topic")));
        putIfBlank(enriched, "taskName", text(enriched.get("topic")));

        normalizeCodePracticeGrade(enriched);
        return enriched;
    }

    private void normalizeCodePracticeGrade(Map<String, Object> request) {
        if (!request.containsKey("exercise")) {
            Map<String, Object> exercise = new LinkedHashMap<>();
            String topic = textOrFallback(request.get("topic"), "代码练习");
            exercise.put("id", "frontend-practice");
            exercise.put("title", topic);
            exercise.put("scenario", textOrFallback(request.get("prompt"), topic));
            exercise.put("language", textOrFallback(request.get("language"), "Java"));
            exercise.put("starterCode", textOrFallback(request.get("starterCode"), ""));
            exercise.put("referenceSolution", textOrFallback(request.get("referenceSolution"), ""));
            exercise.put("rubric", listOrDefault(request.get("rubric"), List.of("概念准确", "步骤完整", "可运行", "表达清晰")));
            exercise.put("testCases", listOrDefault(request.get("testCases"), List.of("说明关键步骤", "给出最小可验证示例")));
            exercise.put("estimatedMinutes", 20);
            request.put("exercise", exercise);
        }
        putIfBlank(request, "submissionCode", textOrFallback(request.get("submission"), ""));
    }

    private StudentProfile loadProfile(String profileId) {
        if (!hasText(profileId)) {
            return null;
        }
        return profileService.requireProfile(profileId);
    }

    private Course loadCourse(String courseId) {
        if (!hasText(courseId)) {
            return null;
        }
        return courseService.requireCourse(courseId);
    }

    private void alias(Map<String, Object> request, String target, String source) {
        if (!hasText(text(request.get(target))) && hasText(text(request.get(source)))) {
            request.put(target, request.get(source));
        }
    }

    private void putIfBlank(Map<String, Object> request, String key, String value) {
        if (!hasText(text(request.get(key))) && hasText(value)) {
            request.put(key, value);
        }
    }

    private Map<String, Object> requireFields(Map<String, Object> request, String... fields) {
        for (String field : fields) {
            if (!hasText(text(request.get(field)))) {
                throw new IllegalArgumentException("Agent request requires " + field);
            }
        }
        return request;
    }

    private Map<String, Object> requireSnapshots(Map<String, Object> request) {
        Object snapshots = request.get("snapshots");
        if (!(snapshots instanceof List<?> list) || list.isEmpty()) {
            throw new IllegalArgumentException("Class analytics requires real student snapshots");
        }
        return request;
    }

    private String text(Object value) {
        return value == null ? null : String.valueOf(value).trim();
    }

    private String textOrFallback(Object value, String fallback) {
        String text = text(value);
        return hasText(text) ? text : fallback;
    }

    private List<?> listOrDefault(Object value, List<?> fallback) {
        return value instanceof List<?> list && !list.isEmpty() ? list : fallback;
    }

    private int intValue(Object value, int fallback) {
        if (value instanceof Number number) {
            return number.intValue();
        }
        if (value == null) {
            return fallback;
        }
        try {
            return Integer.parseInt(String.valueOf(value));
        } catch (NumberFormatException ex) {
            return fallback;
        }
    }

    private boolean hasText(String value) {
        return value != null && !value.isBlank();
    }
}
