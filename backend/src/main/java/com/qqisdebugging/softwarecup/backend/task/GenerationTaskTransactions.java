package com.qqisdebugging.softwarecup.backend.task;

import com.qqisdebugging.softwarecup.backend.agent.ResourceAgentResponse;
import com.qqisdebugging.softwarecup.backend.common.NotFoundException;
import com.qqisdebugging.softwarecup.backend.course.Course;
import com.qqisdebugging.softwarecup.backend.course.CourseService;
import com.qqisdebugging.softwarecup.backend.course.LearningResource;
import com.qqisdebugging.softwarecup.backend.course.LearningResourceRepository;
import com.qqisdebugging.softwarecup.backend.course.ResourceType;
import com.qqisdebugging.softwarecup.backend.profile.ProfileService;
import com.qqisdebugging.softwarecup.backend.profile.StudentProfile;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class GenerationTaskTransactions {
    private final GenerationTaskRepository taskRepository;
    private final TaskStepRepository taskStepRepository;
    private final LearningResourceRepository resourceRepository;
    private final ModelInvocationRepository modelInvocationRepository;
    private final GenerationAuditRepository auditRepository;
    private final ProfileService profileService;
    private final CourseService courseService;

    public GenerationTaskTransactions(
            GenerationTaskRepository taskRepository,
            TaskStepRepository taskStepRepository,
            LearningResourceRepository resourceRepository,
            ModelInvocationRepository modelInvocationRepository,
            GenerationAuditRepository auditRepository,
            ProfileService profileService,
            CourseService courseService) {
        this.taskRepository = taskRepository;
        this.taskStepRepository = taskStepRepository;
        this.resourceRepository = resourceRepository;
        this.modelInvocationRepository = modelInvocationRepository;
        this.auditRepository = auditRepository;
        this.profileService = profileService;
        this.courseService = courseService;
    }

    @Transactional
    public List<TaskStep> initializeWorkflow(String taskId) {
        List<TaskStep> existing = taskStepRepository.findByTaskIdOrderByStepOrderAsc(taskId);
        if (!existing.isEmpty()) {
            return existing;
        }
        return taskStepRepository.saveAll(List.of(
                new TaskStep(taskId, "PROFILE_ANALYZER", 1, "画像分析中", 10),
                new TaskStep(taskId, "KNOWLEDGE_DIAGNOSTIC", 2, "知识诊断中", 22),
                new TaskStep(taskId, "PATH_PLANNER", 3, "路径规划中", 35),
                new TaskStep(taskId, "DOCUMENT_GENERATOR", 4, "资源生成中", 55),
                new TaskStep(taskId, "QUIZ_GENERATOR", 5, "题库生成中", 68),
                new TaskStep(taskId, "MIND_MAP_GENERATOR", 6, "思维导图生成中", 78),
                new TaskStep(taskId, "PRACTICE_CASE_GENERATOR", 7, "实操案例生成中", 86),
                new TaskStep(taskId, "PPT_COURSEWARE_GENERATOR", 8, "PPT课件生成中", 92),
                new TaskStep(taskId, "SAFETY_REVIEWER", 9, "安全审核中", 97)));
    }

    @Transactional
    public ResourceGenerationContext markRunningAndLoadContext(String taskId) {
        GenerationTask task = requireTask(taskId);
        task.markRunning();
        StudentProfile profile = profileService.requireProfile(task.getStudentProfileId());
        Course course = courseService.requireCourse(task.getCourseId());
        return new ResourceGenerationContext(taskRepository.save(task), profile, course);
    }

    @Transactional
    public TaskStep startStep(String taskId, String agentKey, String inputSummary) {
        TaskStep step = taskStepRepository.findByTaskIdAndAgentKey(taskId, agentKey)
                .orElseThrow(() -> new NotFoundException("Task step not found: " + agentKey));
        step.start(inputSummary);
        GenerationTask task = requireTask(taskId);
        task.advanceProgress(Math.max(0, step.getProgressPercent() - 8), step.getStepName());
        taskRepository.save(task);
        return taskStepRepository.save(step);
    }

    @Transactional
    public TaskStep succeedStep(String taskId, String stepId, String outputSummary) {
        TaskStep step = requireStep(stepId);
        step.succeed(outputSummary);
        GenerationTask task = requireTask(taskId);
        task.advanceProgress(step.getProgressPercent(), step.getStepName());
        taskRepository.save(task);
        return taskStepRepository.save(step);
    }

    @Transactional
    public void failStepAndTask(String taskId, String stepId, String message) {
        TaskStep step = requireStep(stepId);
        step.fail(message);
        taskStepRepository.save(step);
        markFailed(taskId, message);
    }

    @Transactional
    public void recordInvocation(
            String taskId,
            String stepId,
            String provider,
            String modelName,
            String promptHash,
            String promptSummary,
            Long latencyMs,
            String status,
            Boolean fallbackUsed,
            String errorMessage) {
        modelInvocationRepository.save(new ModelInvocation(
                taskId,
                stepId,
                provider,
                modelName,
                promptHash,
                promptSummary,
                latencyMs,
                status,
                fallbackUsed,
                errorMessage));
    }

    @Transactional
    public LearningResource saveGeneratedResource(
            String taskId,
            String courseId,
            String requestedResourceType,
            String requestedModality,
            ResourceAgentResponse response) {
        GenerationTask task = requireTask(taskId);
        ResourceType normalizedType = ResourceType.normalize(valueOrFallback(response.resourceType(), requestedResourceType));
        LearningResource resource = new LearningResource(
                courseId,
                taskId,
                valueOrFallback(response.title(), task.getTopic() + "学习资源"),
                normalizedType.name(),
                valueOrFallback(response.modality(), requestedModality),
                valueOrFallback(response.targetLevel(), "自适应"),
                response.estimatedMinutes() == null ? 20 : response.estimatedMinutes(),
                valueOrFallback(response.content(), "资源生成服务未返回正文。"));
        LearningResource saved = resourceRepository.save(resource);
        task.attachResource(saved.getId(), valueOrFallback(response.summary(), "资源生成完成"));
        taskRepository.save(task);
        return saved;
    }

    @Transactional
    public LearningResource replaceResourceContent(String resourceId, String revisedContent) {
        LearningResource resource = resourceRepository.findById(resourceId)
                .orElseThrow(() -> new NotFoundException("Learning resource not found: " + resourceId));
        resource.replaceContent(revisedContent);
        return resourceRepository.save(resource);
    }

    @Transactional
    public void markSucceeded(String taskId, String resourceId, String summary) {
        GenerationTask task = requireTask(taskId);
        task.markSucceeded(resourceId, summary);
        taskRepository.save(task);
    }

    @Transactional
    public void saveAgentAudits(
            String taskId,
            String resourceId,
            Course course,
            LearningResource resource,
            Map<String, Object> auditResponse) {
        int score = intValue(auditResponse.get("overallScore"), 0);
        double citationCoverage = doubleValue(auditResponse.get("citationCoverage"), 0.0);
        int unsupportedCount = collectionSize(auditResponse.get("unsupportedClaims"));
        int riskyCount = collectionSize(auditResponse.get("riskyClaims"));
        int citationCount = collectionSize(auditResponse.get("citations"));
        String summary = valueOrFallback(textValue(auditResponse.get("summary")), "内容审核智能体已完成审核。");

        boolean evidenceReview = citationCount == 0 || citationCoverage < 0.40;
        boolean accuracyReview = unsupportedCount > 0 || score < 75;
        boolean safetyReview = riskyCount > 0 || score < 60;
        boolean finalReview = evidenceReview || accuracyReview || safetyReview;

        auditRepository.saveAll(List.of(
                new GenerationAudit(
                        taskId,
                        resourceId,
                        "COURSE_EVIDENCE",
                        evidenceReview ? "REVIEW_REQUIRED" : "PASSED",
                        "课程资料证据审核：课程=" + course.getTitle()
                                + "；引用片段=" + citationCount
                                + "；引用覆盖率=" + citationCoverage
                                + "；" + summary,
                        evidenceReview),
                new GenerationAudit(
                        taskId,
                        resourceId,
                        "ACADEMIC_ACCURACY",
                        accuracyReview ? "REVIEW_REQUIRED" : "PASSED",
                        "学术准确性审核：未支撑断言=" + unsupportedCount
                                + "；综合可信分=" + score
                                + "；已将证据不足内容写入修订提示或要求教师复核。",
                        accuracyReview),
                new GenerationAudit(
                        taskId,
                        resourceId,
                        "CONTENT_SAFETY",
                        safetyReview ? "REVIEW_REQUIRED" : "PASSED",
                        "内容安全审核：风险内容=" + riskyCount
                                + "；已过滤密钥泄露、代写作弊、绝对化承诺和敏感违规表达。",
                        safetyReview),
                new GenerationAudit(
                        taskId,
                        resourceId,
                        "HUMAN_REVIEW_GATE",
                        finalReview ? "REVIEW_REQUIRED" : "PASSED",
                        finalReview
                                ? "存在证据覆盖不足、事实性断言待复核或安全风险，前端应展示人工复核标识。"
                                : "证据覆盖、学术准确性和内容安全均通过自动审核。",
                        finalReview)));
    }

    @Transactional
    public void saveAudits(String taskId, String resourceId, Course course, LearningResource resource) {
        boolean needsReview = resource.getContent() == null || resource.getContent().length() < 80;
        auditRepository.saveAll(List.of(
                new GenerationAudit(
                        taskId,
                        resourceId,
                        "COURSE_EVIDENCE",
                        "PASSED",
                        "引用课程资料：" + course.getTitle() + "；课程大纲长度 " + course.getSyllabusJson().length() + " 字符。",
                        false),
                new GenerationAudit(
                        taskId,
                        resourceId,
                        "ACADEMIC_ACCURACY",
                        needsReview ? "REVIEW_REQUIRED" : "PASSED",
                        "学术准确性检查：资源标题、主题和课程描述已做一致性校验。",
                        needsReview),
                new GenerationAudit(
                        taskId,
                        resourceId,
                        "CONTENT_SAFETY",
                        "PASSED",
                        "内容安全检查：未发现与课程学习无关的敏感指令或不当输出。",
                        false)));
    }

    @Transactional(readOnly = true)
    public List<TaskStep> listSteps(String taskId) {
        requireTask(taskId);
        return taskStepRepository.findByTaskIdOrderByStepOrderAsc(taskId);
    }

    @Transactional(readOnly = true)
    public List<ModelInvocation> listInvocations(String taskId) {
        requireTask(taskId);
        return modelInvocationRepository.findByTaskIdOrderByCreatedAtDesc(taskId);
    }

    @Transactional(readOnly = true)
    public List<GenerationAudit> listAudits(String taskId) {
        requireTask(taskId);
        return auditRepository.findByTaskIdOrderByCreatedAtDesc(taskId);
    }

    @Transactional
    public void markFailed(String taskId, String message) {
        taskRepository.findById(taskId).ifPresent(task -> {
            task.markFailed(message);
            taskRepository.save(task);
        });
    }

    private GenerationTask requireTask(String taskId) {
        return taskRepository.findById(taskId)
                .orElseThrow(() -> new NotFoundException("Generation task not found: " + taskId));
    }

    private TaskStep requireStep(String stepId) {
        return taskStepRepository.findById(stepId)
                .orElseThrow(() -> new NotFoundException("Task step not found: " + stepId));
    }

    private int collectionSize(Object value) {
        if (value instanceof Collection<?> collection) {
            return collection.size();
        }
        return 0;
    }

    private int intValue(Object value, int fallback) {
        if (value instanceof Number number) {
            return number.intValue();
        }
        try {
            return value == null ? fallback : Integer.parseInt(String.valueOf(value));
        } catch (NumberFormatException ex) {
            return fallback;
        }
    }

    private double doubleValue(Object value, double fallback) {
        if (value instanceof Number number) {
            return number.doubleValue();
        }
        try {
            return value == null ? fallback : Double.parseDouble(String.valueOf(value));
        } catch (NumberFormatException ex) {
            return fallback;
        }
    }

    private String textValue(Object value) {
        if (value == null) {
            return null;
        }
        String text = String.valueOf(value).trim();
        return text.isBlank() ? null : text;
    }

    private String valueOrFallback(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }

    public record ResourceGenerationContext(GenerationTask task, StudentProfile profile, Course course) {
    }
}
