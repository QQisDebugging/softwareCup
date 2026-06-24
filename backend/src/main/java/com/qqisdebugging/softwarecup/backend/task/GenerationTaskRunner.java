package com.qqisdebugging.softwarecup.backend.task;
import com.qqisdebugging.softwarecup.backend.agent.ResourceAgentClient;
import com.qqisdebugging.softwarecup.backend.agent.ResourceAgentRequest;
import com.qqisdebugging.softwarecup.backend.agent.ResourceAgentResponse;
import com.qqisdebugging.softwarecup.backend.agent.AgentArtifactService;
import com.qqisdebugging.softwarecup.backend.config.AgentProperties;
import com.qqisdebugging.softwarecup.backend.course.LearningResource;
import com.qqisdebugging.softwarecup.backend.course.ResourceType;
import com.qqisdebugging.softwarecup.backend.learning.LearningService;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

@Component
public class GenerationTaskRunner {
    private final GenerationTaskTransactions transactions;
    private final ResourceAgentClient resourceAgentClient;
    private final LearningService learningService;
    private final AgentProperties agentProperties;
    private final TaskProgressPublisher progressPublisher;
    private final AgentArtifactService agentArtifactService;

    public GenerationTaskRunner(
            GenerationTaskTransactions transactions,
            ResourceAgentClient resourceAgentClient,
            LearningService learningService,
            AgentProperties agentProperties,
            TaskProgressPublisher progressPublisher,
            AgentArtifactService agentArtifactService) {
        this.transactions = transactions;
        this.resourceAgentClient = resourceAgentClient;
        this.learningService = learningService;
        this.agentProperties = agentProperties;
        this.progressPublisher = progressPublisher;
        this.agentArtifactService = agentArtifactService;
    }

    @Async
    public void runResourceGeneration(String taskId, String resourceType, String modality) {
        try {
            transactions.initializeWorkflow(taskId);
            GenerationTaskTransactions.ResourceGenerationContext context = transactions.markRunningAndLoadContext(taskId);
            publish(taskId, "TASK_RUNNING", 5, "任务启动", TaskStatus.RUNNING.name(), "高级课程资源任务开始执行");

            runProfileAnalyzerStep(taskId, context);
            runKnowledgeDiagnosticStep(taskId, context);

            AgentPathPlan path = runPathPlannerStep(taskId, context);
            LearningResource resource = runDocumentGeneratorStep(taskId, context, resourceType, modality);

            LearningResource quizResource = runCompanionResourceStep(
                    taskId,
                    "QUIZ_GENERATOR",
                    "素材=" + resource.getTitle(),
                    "生成配套练习：5 道选择题 + 1 个案例题，覆盖课程关键能力点。",
                    context,
                    ResourceType.QUIZ_PRACTICE,
                    "课程测验",
                    "文本题库+自动改写",
                    18,
                    quizContent(context));

            LearningResource mindMapResource = runCompanionResourceStep(
                    taskId,
                    "MIND_MAP_GENERATOR",
                    "素材=" + resource.getTitle(),
                    "生成知识导图，帮助梳理课程模块与调用关系。",
                    context,
                    ResourceType.KNOWLEDGE_MIND_MAP,
                    "知识图谱导图",
                    "Mermaid+图结构",
                    12,
                    mindMapContent(context));

            LearningResource readingResource = runCompanionResourceStep(
                    taskId,
                    "EXTENDED_READING_GENERATOR",
                    "课程路径=" + path.title(),
                    "生成课程扩展阅读，提供背景、关键术语与深入问题。",
                    context,
                    ResourceType.EXTENDED_READING,
                    "延伸阅读",
                    "阅读清单+反思问题",
                    20,
                    readingContent(context));

            LearningResource videoResource = runCompanionResourceStep(
                    taskId,
                    "VIDEO_SCRIPT_GENERATOR",
                    "素材=" + resource.getTitle() + "，学情目标=" + context.profile().getLearningGoal(),
                    "生成 5-10 分钟教学脚本（视频/动画），含解说要点与可视化建议。",
                    context,
                    ResourceType.VIDEO_ANIMATION_SCRIPT,
                    "教学视频/动画脚本",
                    "场景+对白+镜头提示",
                    8,
                    videoScriptContent(context));

            LearningResource practiceResource = runCompanionResourceStep(
                    taskId,
                    "PRACTICE_CASE_GENERATOR",
                    "课程路径=" + path.title(),
                    "生成课程实践案例，覆盖真实场景、任务步骤、验收标准与评分标准。",
                    context,
                    ResourceType.PRACTICE_CASE,
                    "实训案例",
                    "项目任务+修复练习",
                    35,
                    practiceCaseContent(context));

            LearningResource pptResource = runCompanionResourceStep(
                    taskId,
                    "PPT_COURSEWARE_GENERATOR",
                    "素材=" + resource.getTitle() + "，课程路径=" + path.title(),
                    "生成 6-8 页课程 PPT 脚本（讲义+课件结构+可视化建议），支持教师直接导出。",
                    context,
                    ResourceType.PPT_COURSEWARE,
                    "PPT讲稿+课件结构",
                    "PPT讲稿+课件结构",
                    15,
                    pptContent(context));

            resource = runSafetyReviewStep(taskId, context, resource);

            learningService.recommendGeneratedResource(
                    context.profile(),
                    context.course(),
                    resource,
                    "根据画像与课程目标生成学习建议与教学任务，帮助学生快速进入下一步学习。");
            int generatedTypeCount = List.of(
                    resource,
                    quizResource,
                    mindMapResource,
                    readingResource,
                    videoResource,
                    practiceResource,
                    pptResource).size();
            recordOrchestrationTrace(taskId, context, resource, generatedTypeCount);
            transactions.markSucceeded(
                    taskId,
                    resource.getId(),
                    "高级课程资源生成完成，共产出 "
                            + generatedTypeCount
                            + " 种教学资源，已推送学习推荐与课程素材库");
            publish(taskId, "TASK_SUCCEEDED", 100, "任务完成", TaskStatus.SUCCEEDED.name(), "高级课程资源任务已完成");
        } catch (Exception ex) {
            String message = exceptionMessage(ex);
            if (!(ex instanceof StepFailedException)) {
                transactions.markFailed(taskId, message);
            }
            publish(taskId, "TASK_FAILED", 100, "任务失败", TaskStatus.FAILED.name(), message);
        }
    }

    private void runRuleStep(String taskId, String agentKey, String inputSummary, String outputSummary) {
        TaskStep step = transactions.startStep(taskId, agentKey, inputSummary);
        try {
            publish(taskId, "STEP_STARTED", step.getProgressPercent() - 8, step.getStepName(), step.getStatus(), inputSummary);
            long start = System.nanoTime();
            transactions.recordInvocation(
                    taskId,
                    step.getId(),
                    "backend_orchestrator",
                    "structured-agent",
                    promptHash(inputSummary),
                    inputSummary,
                    elapsedMs(start),
                    "SUCCEEDED",
                    false,
                    null);
            TaskStep done = transactions.succeedStep(taskId, step.getId(), outputSummary);
            publish(taskId, "STEP_SUCCEEDED", done.getProgressPercent(), done.getStepName(), done.getStatus(), outputSummary);
        } catch (Exception ex) {
            throw failStartedStep(taskId, step, ex);
        }
    }

    private void runProfileAnalyzerStep(
            String taskId,
            GenerationTaskTransactions.ResourceGenerationContext context) {
        TaskStep step = transactions.startStep(taskId, "PROFILE_ANALYZER", "画像推断=" + context.profile().getStudentName());
        try {
            publish(taskId, "STEP_STARTED", step.getProgressPercent() - 8, step.getStepName(), step.getStatus(), step.getInputSummary());
            long start = System.nanoTime();
            Map<String, Object> request = profileInferRequest(context);
            Map<String, Object> response = agentArtifactService.invokeAndStore(
                    "PROFILE_INFERENCE",
                    "/agents/profile/infer",
                    request);
            transactions.recordInvocation(
                    taskId,
                    step.getId(),
                    textOrFallback(response.get("provider"), agentProperties.getProvider()),
                    textOrFallback(response.get("model"), agentProperties.getModel()),
                    promptHash(request.toString()),
                    "画像推断 Agent 成功，维度数=" + collectionSize(response.get("dimensions")),
                    elapsedMs(start),
                    "SUCCEEDED",
                    Boolean.TRUE.equals(response.get("fallbackUsed")),
                    null);
            TaskStep done = transactions.succeedStep(
                    taskId,
                    step.getId(),
                    textOrFallback(response.get("summary"), "画像推断完成")
                            + "；维度数=" + collectionSize(response.get("dimensions"))
                            + "，信号数=" + collectionSize(response.get("extractedSignals")));
            publish(taskId, "STEP_SUCCEEDED", done.getProgressPercent(), done.getStepName(), done.getStatus(), done.getOutputSummary());
        } catch (Exception ex) {
            throw failStartedStep(taskId, step, ex);
        }
    }

    private void runKnowledgeDiagnosticStep(
            String taskId,
            GenerationTaskTransactions.ResourceGenerationContext context) {
        TaskStep step = transactions.startStep(taskId, "KNOWLEDGE_DIAGNOSTIC", "课程诊断=" + context.course().getTitle());
        try {
            publish(taskId, "STEP_STARTED", step.getProgressPercent() - 8, step.getStepName(), step.getStatus(), step.getInputSummary());
            long start = System.nanoTime();
            Map<String, Object> request = courseDiagnosisRequest(context);
            Map<String, Object> response = agentArtifactService.invokeAndStore(
                    "COURSE_DIAGNOSIS",
                    "/agents/course/diagnose",
                    request);
            transactions.recordInvocation(
                    taskId,
                    step.getId(),
                    textOrFallback(response.get("provider"), agentProperties.getProvider()),
                    textOrFallback(response.get("model"), agentProperties.getModel()),
                    promptHash(request.toString()),
                    "课程诊断 Agent 成功，覆盖分=" + textOrFallback(response.get("coverageScore"), "-"),
                    elapsedMs(start),
                    "SUCCEEDED",
                    Boolean.TRUE.equals(response.get("fallbackUsed")),
                    null);
            TaskStep done = transactions.succeedStep(
                    taskId,
                    step.getId(),
                    textOrFallback(response.get("summary"), "课程诊断完成")
                            + "；缺口知识点=" + collectionSize(response.get("missingKnowledgePoints"))
                            + "，缺口资源类型=" + collectionSize(response.get("missingResourceTypes")));
            publish(taskId, "STEP_SUCCEEDED", done.getProgressPercent(), done.getStepName(), done.getStatus(), done.getOutputSummary());
        } catch (Exception ex) {
            throw failStartedStep(taskId, step, ex);
        }
    }

    private LearningResource runCompanionResourceStep(
            String taskId,
            String agentKey,
            String inputSummary,
            String outputSummary,
            GenerationTaskTransactions.ResourceGenerationContext context,
            ResourceType resourceType,
            String titleSuffix,
            String modality,
            int estimatedMinutes,
            String content) {
        TaskStep step = transactions.startStep(taskId, agentKey, inputSummary);
        try {
            publish(taskId, "STEP_STARTED", step.getProgressPercent() - 8, step.getStepName(), step.getStatus(), inputSummary);
            long start = System.nanoTime();
            ResourceAgentResponse response = resourceAgentClient.generate(new ResourceAgentRequest(
                    taskId + "-" + agentKey.toLowerCase(java.util.Locale.ROOT),
                    context.profile().getId(),
                    context.course().getId(),
                    context.profile().getDialogueSummary(),
                    context.course().getTitle(),
                    context.task().getTopic(),
                    resourceType.name(),
                    modality,
                    content,
                    List.of(),
                    List.of(
                            textOrFallback(context.task().getPrompt(), ""),
                            textOrFallback(context.course().getDescription(), ""),
                            textOrFallback(context.course().getSyllabusJson(), ""),
                            textOrFallback(context.profile().getLearningGoal(), ""),
                            outputSummary),
                    List.of(resourceType.displayName())));
            if (Boolean.TRUE.equals(response.fallbackUsed())) {
                throw new IllegalStateException(agentKey + " returned fallback output");
            }
            LearningResource saved = transactions.saveCompanionResource(
                    taskId,
                    context.course().getId(),
                    resourceType,
                    textOrFallback(response.title(), context.task().getTopic() + " - " + titleSuffix),
                    textOrFallback(response.modality(), modality),
                    textOrFallback(response.targetLevel(), context.profile().getCurrentLevel()),
                    response.estimatedMinutes() == null ? estimatedMinutes : response.estimatedMinutes(),
                    response.content());
            transactions.recordInvocation(
                    taskId,
                    step.getId(),
                    textOrFallback(response.provider(), agentProperties.getProvider()),
                    textOrFallback(response.model(), agentProperties.getModel()),
                    promptHash(content),
                    context.task().getTopic() + " / " + resourceType.displayName(),
                    elapsedMs(start),
                    "SUCCEEDED",
                    false,
                    null);
            TaskStep done = transactions.succeedStep(taskId, step.getId(), outputSummary + "，已保存资源：" + saved.getTitle());
            publish(taskId, "STEP_SUCCEEDED", done.getProgressPercent(), done.getStepName(), done.getStatus(), done.getOutputSummary());
            return saved;
        } catch (Exception ex) {
            throw failStartedStep(taskId, step, ex);
        }
    }

    private AgentPathPlan runPathPlannerStep(
            String taskId,
            GenerationTaskTransactions.ResourceGenerationContext context) {
        TaskStep step = transactions.startStep(taskId, "PATH_PLANNER", "主题=" + context.task().getTopic());
        try {
            publish(taskId, "STEP_STARTED", step.getProgressPercent() - 8, step.getStepName(), step.getStatus(), step.getInputSummary());
            long start = System.nanoTime();
            Map<String, Object> request = pathPlanRequest(context);
            Map<String, Object> response = agentArtifactService.invokeAndStore(
                    "LEARNING_PATH_PLAN",
                    "/agents/path/plan",
                    request);
            AgentPathPlan path = AgentPathPlan.from(response);
            transactions.recordInvocation(
                    taskId,
                    step.getId(),
                    textOrFallback(response.get("provider"), agentProperties.getProvider()),
                    textOrFallback(response.get("model"), agentProperties.getModel()),
                    promptHash(writePathPromptSummary(request)),
                    "课程路径生成成功：" + path.title(),
                    elapsedMs(start),
                    "SUCCEEDED",
                    Boolean.TRUE.equals(response.get("fallbackUsed")),
                    null);
            TaskStep done = transactions.succeedStep(
                    taskId,
                    step.getId(),
                    "路径规划完成，课程路径=" + path.title() + "，阶段数=" + path.stageCount());
            publish(taskId, "STEP_SUCCEEDED", done.getProgressPercent(), done.getStepName(), done.getStatus(), done.getOutputSummary());
            return path;
        } catch (Exception ex) {
            throw failStartedStep(taskId, step, ex);
        }
    }

    private LearningResource runDocumentGeneratorStep(
            String taskId,
            GenerationTaskTransactions.ResourceGenerationContext context,
            String resourceType,
            String modality) {
        TaskStep step = transactions.startStep(taskId, "DOCUMENT_GENERATOR", context.task().getPrompt());
        try {
            publish(taskId, "STEP_STARTED", step.getProgressPercent() - 8, step.getStepName(), step.getStatus(), "\u8c03\u7528\u8d44\u6e90\u751f\u6210\u670d\u52a1");
            long start = System.nanoTime();
            ResourceAgentResponse response = resourceAgentClient.generate(new ResourceAgentRequest(
                    taskId,
                    context.profile().getId(),
                    context.course().getId(),
                    context.profile().getDialogueSummary(),
                    context.course().getTitle(),
                    context.task().getTopic(),
                    resourceType,
                    modality,
                    context.task().getPrompt(),
                    List.of(),
                    List.of(context.course().getDescription(), context.course().getSyllabusJson()),
                    Arrays.stream(ResourceType.values()).map(ResourceType::displayName).toList()));
            if (Boolean.TRUE.equals(response.fallbackUsed())) {
                throw new IllegalStateException("Document generator returned fallback output");
            }
            transactions.recordInvocation(
                    taskId,
                    step.getId(),
                    textOrFallback(response.provider(), agentProperties.getProvider()),
                    textOrFallback(response.model(), agentProperties.getModel()),
                    promptHash(context.task().getPrompt()),
                    context.task().getTopic() + " / " + ResourceType.normalize(resourceType).displayName(),
                    elapsedMs(start),
                    "SUCCEEDED",
                    Boolean.TRUE.equals(response.fallbackUsed()),
                    null);
            LearningResource resource = transactions.saveGeneratedResource(taskId, context.course().getId(), resourceType, modality, response);
            TaskStep done = transactions.succeedStep(
                    taskId,
                    step.getId(),
                    "课程资源生成成功：" + resource.getTitle());
            publish(taskId, "STEP_SUCCEEDED", done.getProgressPercent(), done.getStepName(), done.getStatus(), done.getOutputSummary());
            return resource;
        } catch (Exception ex) {
            transactions.recordInvocation(
                    taskId,
                    step.getId(),
                    agentProperties.getProvider(),
                    agentProperties.getModel(),
                    promptHash(context.task().getPrompt()),
                    context.task().getTopic() + " / " + ResourceType.normalize(resourceType).displayName(),
                    elapsedMs(System.nanoTime()),
                    "FAILED",
                    false,
                    exceptionMessage(ex));
            throw failStartedStep(taskId, step, ex);
        }
    }

    private LearningResource runSafetyReviewStep(
            String taskId,
            GenerationTaskTransactions.ResourceGenerationContext context,
            LearningResource resource) {
        TaskStep step = transactions.startStep(taskId, "SAFETY_REVIEWER", "\u5185\u5bb9\u5be9\u67e5=" + resource.getTitle());
        try {
            publish(taskId, "STEP_STARTED", step.getProgressPercent() - 8, step.getStepName(), step.getStatus(), step.getInputSummary());
            long start = System.nanoTime();
            Map<String, Object> auditResponse = agentArtifactService.invokeAndStore(
                    "CONTENT_AUDIT",
                    "/agents/safety/audit",
                    auditRequest(context, resource));
            LearningResource reviewedResource = applyAuditRevision(resource, auditResponse);
            transactions.saveAgentAudits(taskId, reviewedResource.getId(), context.course(), reviewedResource, auditResponse);
            transactions.recordInvocation(
                    taskId,
                    step.getId(),
                    textOrFallback(auditResponse.get("provider"), agentProperties.getProvider()),
                    textOrFallback(auditResponse.get("model"), agentProperties.getModel()),
                    promptHash(resource.getContent()),
                    "\u5b89\u5168\u5ba1\u67e5\u6210\u529f",
                    elapsedMs(start),
                    "SUCCEEDED",
                    false,
                    null);
            TaskStep done = transactions.succeedStep(taskId, step.getId(), auditOutputSummary(auditResponse));
            publish(taskId, "STEP_SUCCEEDED", done.getProgressPercent(), done.getStepName(), done.getStatus(), done.getOutputSummary());
            return reviewedResource;
        } catch (Exception ex) {
            throw failStartedStep(taskId, step, ex);
        }
    }

    private RuntimeException failStartedStep(String taskId, TaskStep step, Exception ex) {
        String message = exceptionMessage(ex);
        transactions.failStepAndTask(taskId, step.getId(), message);
        return new StepFailedException(message, ex);
    }

    private Map<String, Object> pathPlanRequest(GenerationTaskTransactions.ResourceGenerationContext context) {
        Map<String, Object> request = new LinkedHashMap<>();
        request.put("traceId", context.task().getId());
        request.put("studentProfileId", context.profile().getId());
        request.put("courseId", context.course().getId());
        request.put("studentProfileSummary", context.profile().getDialogueSummary());
        request.put("courseTitle", context.course().getTitle());
        request.put("topic", context.task().getTopic());
        request.put("goal", context.profile().getLearningGoal());
        request.put("timeframeDays", 7);
        request.put("dailyMinutes", 45);
        request.put("weaknessSignals", List.of(context.profile().getCurrentLevel(), context.task().getPrompt()));
        request.put("completedResources", List.of());
        request.put("recentScores", List.of());
        request.put("documentTexts", List.of(context.course().getDescription(), context.course().getSyllabusJson()));
        return request;
    }

    private Map<String, Object> profileInferRequest(GenerationTaskTransactions.ResourceGenerationContext context) {
        Map<String, Object> request = new LinkedHashMap<>();
        request.put("traceId", context.task().getId());
        request.put("studentProfileId", context.profile().getId());
        request.put("courseId", context.course().getId());
        request.put("courseTitle", context.course().getTitle());
        request.put("declaredMajor", context.profile().getMajor());
        request.put("currentLevel", context.profile().getCurrentLevel());
        request.put("learningGoal", context.profile().getLearningGoal());
        request.put("preferences", context.profile().getPreferences());
        request.put("constraintsText", context.profile().getConstraintsText());
        request.put("dialogueTurns", List.of(context.profile().getDialogueSummary()));
        request.put("learningRecords", List.of(context.task().getPrompt()));
        request.put("assessmentSummaries", List.of());
        request.put("tutoringSummaries", List.of());
        request.put("documentTexts", List.of(context.course().getDescription(), context.course().getSyllabusJson()));
        return request;
    }

    private Map<String, Object> courseDiagnosisRequest(GenerationTaskTransactions.ResourceGenerationContext context) {
        Map<String, Object> request = new LinkedHashMap<>();
        request.put("traceId", context.task().getId());
        request.put("courseId", context.course().getId());
        request.put("courseTitle", context.course().getTitle());
        request.put("courseDescription", context.course().getDescription());
        request.put("syllabusText", context.course().getSyllabusJson());
        request.put("targetStudentProfile", context.profile().getDialogueSummary());
        request.put("documentTexts", List.of(context.task().getPrompt(), context.profile().getLearningGoal()));
        return request;
    }

    private String writePathPromptSummary(Map<String, Object> request) {
        return "topic=" + textValue(request.get("topic"))
                + "; goal=" + textValue(request.get("goal"))
                + "; profile=" + textValue(request.get("studentProfileSummary"));
    }

    private String exceptionMessage(Exception ex) {
        return ex.getMessage() == null ? ex.getClass().getSimpleName() : ex.getMessage();
    }

    private void recordOrchestrationTrace(
            String taskId,
            GenerationTaskTransactions.ResourceGenerationContext context,
            LearningResource resource,
            int generatedTypeCount) {
        Map<String, Object> request = new LinkedHashMap<>();
        request.put("traceId", taskId);
        request.put("taskName", "个性化资源生成多智能体编排");
        request.put("userIntent", context.task().getPrompt());
        request.put("studentProfileId", context.profile().getId());
        request.put("courseId", context.course().getId());
        request.put("involvedAgents", List.of(
                "profile_agent",
                "course_knowledge_agent",
                "path_planner_agent",
                "resource_writer_agent",
                "quiz_generator_agent",
                "mind_map_agent",
                "storyboard_agent",
                "practice_case_agent",
                "content_audit_agent"));
        request.put("requestPayload", Map.of(
                "taskId", taskId,
                "courseTitle", context.course().getTitle(),
                "topic", context.task().getTopic(),
                "resourceType", context.task().getTaskType(),
                "providerPolicy", "核心正文、配套测验、导图、阅读、视频脚本、实训案例和 PPT 讲稿均通过资源生成智能体调用；fallbackUsed=true 时任务失败。"));
        request.put("responseSummary", "任务完成，生成 " + generatedTypeCount
                + " 类资源；主资源=" + resource.getTitle()
                + "；审核状态=" + resource.getReviewStatus());
        request.put("orchestrationNotes", List.of(
                "伴生资源步骤保存真实 provider/model 调用记录，便于回看每个智能体产物。",
                "同一星火 prompt 命中 Python 本地缓存时直接复用，不重复扣额度。"));
        request.put("safetyIssues", List.of());
        try {
            agentArtifactService.invokeAndStore("AGENT_ORCHESTRATION_TRACE", "/agents/trace/explain", request);
            publish(taskId, "AGENT_TRACE_RECORDED", 99, "智能体编排追踪", TaskStatus.RUNNING.name(), "已保存多智能体编排追踪 artifact");
        } catch (Exception ex) {
            publish(taskId, "AGENT_TRACE_SKIPPED", 99, "智能体编排追踪", TaskStatus.RUNNING.name(), exceptionMessage(ex));
        }
    }

    private Map<String, Object> auditRequest(
            GenerationTaskTransactions.ResourceGenerationContext context,
            LearningResource resource) {
        Map<String, Object> request = new LinkedHashMap<>();
        request.put("studentProfileId", context.profile().getId());
        request.put("courseId", context.course().getId());
        request.put("courseTitle", context.course().getTitle());
        request.put("topic", context.task().getTopic());
        request.put("content", resource.getContent());
        request.put("documentTexts", List.of(context.course().getDescription(), context.course().getSyllabusJson()));
        return request;
    }

    private String quizContent(GenerationTaskTransactions.ResourceGenerationContext context) {
        return """
                # %s - 课程测验

                ## 学情摘要
                %s

                ## 题目分布
                1. 选择题：5题（每题含 1 个场景干扰项）
                2. 简答题：2题（覆盖关键实现和边界条件）
                3. 案例题：1题（给出代码实现思路）
                ## 输出规范
                题目需给出标准答案、讲解点与易错提醒。""".formatted(context.task().getTopic(), context.profile().getDialogueSummary());
    }

    private String mindMapContent(GenerationTaskTransactions.ResourceGenerationContext context) {
        return """
                # %s - 知识导图

                ```mermaid
                mindmap
                  root((%s))
                    学习目标
                      需求理解
                      模块划分
                      关键边界
                    开发流程
                      Controller
                      Service
                      Repository
                    排障思路
                      输入校验
                      事务一致性
                      异常处理
                    课程复盘
                      练习题复核
                      讨论与优化
                ```

                ## 使用建议
                将导图转为课堂白板草图，逐层展开并加入真实案例。""".formatted(context.task().getTopic(), context.task().getTopic());
    }

    private String readingContent(GenerationTaskTransactions.ResourceGenerationContext context) {
        return """
                # %s - 延伸阅读

                ## 阅读目的
                在课程目标基础上补强工程背景、关键术语与常见误区。
                ## 建议目录
                1. 本模块背景与适用场景
                2. 接口、服务、仓储层职责划分
                3. 常见性能与一致性问题
                4. 学习扩展问题清单
                ## 实操提示
                每个主题附带最小复现样例和可复用伪代码。""".formatted(context.task().getTopic(), context.course().getTitle());
    }

    private String videoScriptContent(GenerationTaskTransactions.ResourceGenerationContext context) {
        return """
                # %s - 教学视频脚本

                | 场景 | 时长 | 讲解内容 | 画面提示 |
                | --- | ---: | --- | --- |
                | 1 | 30s | 课程导入与业务目标 | 使用真实业务切入点 |
                | 2 | 60s | 模块职责拆解 | 层级化画面演示 |
                | 3 | 90s | 错误案例与排查 | 高亮异常路径 |
                | 4 | 90s | 优化思路与扩展 | 列清单逐条解释 |
                | 5 | 60s | 本课回顾与课后任务 | 给出提交要求 |

                ## 课堂输出
                每个镜头给出关键台词、切换点和停顿提示，支持直接用于录制。""".formatted(context.task().getTopic());
    }

    private String practiceCaseContent(GenerationTaskTransactions.ResourceGenerationContext context) {
        return """
                # %s - 实训案例

                ## 任务背景
                学生已完成课程核心学习，需要通过一个真实案例完成服务优化闭环。
                ## 实现步骤
                1. 设计课程素材导入接口 `CourseMaterialController`
                2. 在 `CourseMaterialService` 中完成解析、归一化与持久化
                3. 仓储层完成素材检索与状态更新
                4. 返回值与错误码规范化处理
                ## 验收标准
                - 接口可正常上传/查询
                - 异常可快速定位
                - 日志与审计记录完整
                ## 扩展方向
                可加入自动评分脚本和教师批改视图。""".formatted(context.task().getTopic(), context.course().getTitle());
    }

    private String pptContent(GenerationTaskTransactions.ResourceGenerationContext context) {
        return """
                # %s - 课程PPT脚本

                | 页码 | 标题 | 关键讲解点 | 交付动作 |
                | --- | --- | --- | --- |
                | 1 | 课程总览 | 业务场景与学习目标 | 讲清任务边界 |
                | 2 | 架构拆解 | Controller-Service-Repository | 指出演讲重点 |
                | 3 | 异常排查 | 输入校验与事务安全 | 给出排障清单 |
                | 4 | 优化建议 | 性能与可维护性 | 给出改进方案 |
                | 5 | 测试验证 | 单元/集成测试流程 | 演示验证结果 |
                | 6 | 课堂复盘 | 按学情调整讲解 | 输出总结 |

                ## 班主任说明
                课程导向清晰，支持课堂即用。""".formatted(context.task().getTopic(), context.profile().getDialogueSummary());
    }

    private LearningResource applyAuditRevision(LearningResource resource, Map<String, Object> auditResponse) {
        String revisedContent = textValue(auditResponse.get("revisedContent"));
        if (!shouldUseRevisedContent(auditResponse, revisedContent, resource.getContent())) {
            return resource;
        }
        return transactions.replaceResourceContent(resource.getId(), revisedContent);
    }

    private boolean shouldUseRevisedContent(
            Map<String, Object> auditResponse,
            String revisedContent,
            String originalContent) {
        if (revisedContent == null || revisedContent.equals(originalContent)) {
            return false;
        }
        int score = intValue(auditResponse.get("overallScore"), 100);
        return score < 90
                || collectionSize(auditResponse.get("unsupportedClaims")) > 0
                || collectionSize(auditResponse.get("riskyClaims")) > 0;
    }

    private String auditOutputSummary(Map<String, Object> auditResponse) {
        int score = intValue(auditResponse.get("overallScore"), 0);
        int unsupported = collectionSize(auditResponse.get("unsupportedClaims"));
        int risky = collectionSize(auditResponse.get("riskyClaims"));
        return "内容审核完成：可信分=" + score
                + "；未支撑断言=" + unsupported
                + "；风险内容=" + risky
                + "。证据不足或风险内容已写入审核记录和资源修订稿。";
    }

    private int collectionSize(Object value) {
        if (value instanceof java.util.Collection<?> collection) {
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

    private String textValue(Object value) {
        if (value == null) {
            return null;
        }
        String text = String.valueOf(value).trim();
        return text.isBlank() ? null : text;
    }

    private String textOrFallback(Object value, String fallback) {
        String text = textValue(value);
        return text == null ? fallback : text;
    }

    private void publish(String taskId, String eventType, Integer progress, String currentStep, String status, String message) {
        progressPublisher.publish(TaskProgressEvent.of(taskId, eventType, progress, currentStep, status, message));
    }

    private Long elapsedMs(long startNanos) {
        return (System.nanoTime() - startNanos) / 1_000_000;
    }

    private String promptHash(String value) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest((value == null ? "" : value).getBytes(StandardCharsets.UTF_8));
            StringBuilder builder = new StringBuilder();
            for (int i = 0; i < 12 && i < hash.length; i++) {
                builder.append(String.format("%02x", hash[i]));
            }
            return builder.toString();
        } catch (NoSuchAlgorithmException ex) {
            return Integer.toHexString((value == null ? "" : value).hashCode());
        }
    }

    private record AgentPathPlan(String title, int stageCount, String summary) {
        static AgentPathPlan from(Map<String, Object> response) {
            String title = value(response.get("planTitle"), "个性化学习路径");
            Object stages = response.get("stages");
            int stageCount = stages instanceof List<?> list ? list.size() : 0;
            String summary = value(response.get("summary"), title);
            return new AgentPathPlan(title, stageCount, summary);
        }

        private static String value(Object value, String fallback) {
            if (value == null) {
                return fallback;
            }
            String text = String.valueOf(value).trim();
            return text.isBlank() ? fallback : text;
        }
    }

    private static class StepFailedException extends RuntimeException {
        StepFailedException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}
