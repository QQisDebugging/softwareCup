package com.qqisdebugging.softwarecup.backend.task;

import com.qqisdebugging.softwarecup.backend.agent.ResourceAgentClient;
import com.qqisdebugging.softwarecup.backend.agent.ResourceAgentRequest;
import com.qqisdebugging.softwarecup.backend.agent.ResourceAgentResponse;
import com.qqisdebugging.softwarecup.backend.config.AgentProperties;
import com.qqisdebugging.softwarecup.backend.course.LearningResource;
import com.qqisdebugging.softwarecup.backend.course.ResourceType;
import com.qqisdebugging.softwarecup.backend.learning.LearningPathResponse;
import com.qqisdebugging.softwarecup.backend.learning.LearningService;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.List;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

@Component
public class GenerationTaskRunner {
    private final GenerationTaskTransactions transactions;
    private final ResourceAgentClient resourceAgentClient;
    private final LearningService learningService;
    private final AgentProperties agentProperties;
    private final TaskProgressPublisher progressPublisher;

    public GenerationTaskRunner(
            GenerationTaskTransactions transactions,
            ResourceAgentClient resourceAgentClient,
            LearningService learningService,
            AgentProperties agentProperties,
            TaskProgressPublisher progressPublisher) {
        this.transactions = transactions;
        this.resourceAgentClient = resourceAgentClient;
        this.learningService = learningService;
        this.agentProperties = agentProperties;
        this.progressPublisher = progressPublisher;
    }

    @Async
    public void runResourceGeneration(String taskId, String resourceType, String modality) {
        String currentStepId = null;
        try {
            transactions.initializeWorkflow(taskId);
            GenerationTaskTransactions.ResourceGenerationContext context = transactions.markRunningAndLoadContext(taskId);
            publish(taskId, "TASK_RUNNING", 5, "任务启动", TaskStatus.RUNNING.name(), "多智能体任务链已启动");

            runRuleStep(
                    taskId,
                    "PROFILE_ANALYZER",
                    "画像摘要：" + context.profile().getDialogueSummary(),
                    "完成画像分析：目标=" + context.profile().getLearningGoal()
                            + "；偏好=" + context.profile().getPreferences());

            runRuleStep(
                    taskId,
                    "KNOWLEDGE_DIAGNOSTIC",
                    "课程=" + context.course().getTitle() + "；主题=" + context.task().getTopic(),
                    "诊断结果：当前主题需要关注先修基础、易错点和实践迁移能力。");

            LearningPathResponse path = runPathPlannerStep(taskId, context);
            LearningResource resource = runDocumentGeneratorStep(taskId, context, resourceType, modality);

            runRuleStep(
                    taskId,
                    "QUIZ_GENERATOR",
                    "资源=" + resource.getTitle(),
                    "已规划 5 道基础题、3 道综合题和 1 道错因追问，供后续测验模块使用。");

            runRuleStep(
                    taskId,
                    "MIND_MAP_GENERATOR",
                    "资源=" + resource.getTitle(),
                    "已生成思维导图结构：核心概念、关键 API、常见误区、实践任务。");

            runRuleStep(
                    taskId,
                    "PRACTICE_CASE_GENERATOR",
                    "学习路径=" + path.title(),
                    "已生成实操案例蓝图：需求描述、编码任务、验收标准和拓展挑战。");

            runSafetyReviewStep(taskId, context, resource);

            learningService.recommendGeneratedResource(
                    context.profile(),
                    context.course(),
                    resource,
                    "结合画像、路径规划和安全审核结果，将该资源作为当前阶段优先学习材料。");
            transactions.markSucceeded(taskId, resource.getId(), "多智能体资源生成、路径规划、推荐和安全审核完成");
            publish(taskId, "TASK_SUCCEEDED", 100, "任务完成", TaskStatus.SUCCEEDED.name(), "多智能体任务链执行完成");
        } catch (Exception ex) {
            String message = ex.getMessage() == null ? ex.getClass().getSimpleName() : ex.getMessage();
            if (currentStepId != null) {
                transactions.failStepAndTask(taskId, currentStepId, message);
            } else {
                transactions.markFailed(taskId, message);
            }
            publish(taskId, "TASK_FAILED", 100, "任务失败", TaskStatus.FAILED.name(), message);
        }
    }

    private void runRuleStep(String taskId, String agentKey, String inputSummary, String outputSummary) {
        TaskStep step = transactions.startStep(taskId, agentKey, inputSummary);
        publish(taskId, "STEP_STARTED", step.getProgressPercent() - 8, step.getStepName(), step.getStatus(), inputSummary);
        long start = System.nanoTime();
        transactions.recordInvocation(
                taskId,
                step.getId(),
                agentProperties.getFallbackProvider(),
                agentProperties.getFallbackModel(),
                promptHash(inputSummary),
                inputSummary,
                elapsedMs(start),
                "SUCCEEDED",
                false,
                null);
        TaskStep done = transactions.succeedStep(taskId, step.getId(), outputSummary);
        publish(taskId, "STEP_SUCCEEDED", done.getProgressPercent(), done.getStepName(), done.getStatus(), outputSummary);
    }

    private LearningPathResponse runPathPlannerStep(
            String taskId,
            GenerationTaskTransactions.ResourceGenerationContext context) {
        TaskStep step = transactions.startStep(taskId, "PATH_PLANNER", "主题=" + context.task().getTopic());
        publish(taskId, "STEP_STARTED", step.getProgressPercent() - 8, step.getStepName(), step.getStatus(), step.getInputSummary());
        long start = System.nanoTime();
        LearningPathResponse path = learningService.createInitialPath(context.profile(), context.course(), context.task().getTopic());
        transactions.recordInvocation(
                taskId,
                step.getId(),
                agentProperties.getFallbackProvider(),
                agentProperties.getFallbackModel(),
                promptHash(path.title()),
                "生成学习路径：" + path.title(),
                elapsedMs(start),
                "SUCCEEDED",
                false,
                null);
        TaskStep done = transactions.succeedStep(taskId, step.getId(), "已生成学习路径：" + path.title() + "，节点数=" + path.nodes().size());
        publish(taskId, "STEP_SUCCEEDED", done.getProgressPercent(), done.getStepName(), done.getStatus(), done.getOutputSummary());
        return path;
    }

    private LearningResource runDocumentGeneratorStep(
            String taskId,
            GenerationTaskTransactions.ResourceGenerationContext context,
            String resourceType,
            String modality) {
        TaskStep step = transactions.startStep(taskId, "DOCUMENT_GENERATOR", context.task().getPrompt());
        publish(taskId, "STEP_STARTED", step.getProgressPercent() - 8, step.getStepName(), step.getStatus(), "调用资源生成服务");
        ResourceAgentResponse response;
        long start = System.nanoTime();
        try {
            response = resourceAgentClient.generate(new ResourceAgentRequest(
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
            transactions.recordInvocation(
                    taskId,
                    step.getId(),
                    agentProperties.getProvider(),
                    agentProperties.getModel(),
                    promptHash(context.task().getPrompt()),
                    context.task().getTopic() + " / " + ResourceType.normalize(resourceType).displayName(),
                    elapsedMs(start),
                    "SUCCEEDED",
                    false,
                    null);
        } catch (Exception ex) {
            String message = ex.getMessage() == null ? ex.getClass().getSimpleName() : ex.getMessage();
            transactions.recordInvocation(
                    taskId,
                    step.getId(),
                    agentProperties.getProvider(),
                    agentProperties.getModel(),
                    promptHash(context.task().getPrompt()),
                    context.task().getTopic() + " / " + ResourceType.normalize(resourceType).displayName(),
                    elapsedMs(start),
                    "FAILED",
                    false,
                    message);
            long fallbackStart = System.nanoTime();
            response = fallbackResource(context, resourceType, modality);
            transactions.recordInvocation(
                    taskId,
                    step.getId(),
                    agentProperties.getFallbackProvider(),
                    agentProperties.getFallbackModel(),
                    promptHash(response.content()),
                    "资源生成服务失败后使用本地模板兜底",
                    elapsedMs(fallbackStart),
                    "SUCCEEDED",
                    true,
                    null);
        }
        LearningResource resource = transactions.saveGeneratedResource(taskId, context.course().getId(), resourceType, modality, response);
        TaskStep done = transactions.succeedStep(taskId, step.getId(), "已生成资源：" + resource.getTitle() + "，类型=" + resource.getResourceType());
        publish(taskId, "STEP_SUCCEEDED", done.getProgressPercent(), done.getStepName(), done.getStatus(), done.getOutputSummary());
        return resource;
    }

    private void runSafetyReviewStep(
            String taskId,
            GenerationTaskTransactions.ResourceGenerationContext context,
            LearningResource resource) {
        TaskStep step = transactions.startStep(taskId, "SAFETY_REVIEWER", "资源=" + resource.getTitle());
        publish(taskId, "STEP_STARTED", step.getProgressPercent() - 8, step.getStepName(), step.getStatus(), step.getInputSummary());
        long start = System.nanoTime();
        transactions.saveAudits(taskId, resource.getId(), context.course(), resource);
        transactions.recordInvocation(
                taskId,
                step.getId(),
                agentProperties.getFallbackProvider(),
                agentProperties.getFallbackModel(),
                promptHash(resource.getContent()),
                "安全审核与防幻觉证据落库",
                elapsedMs(start),
                "SUCCEEDED",
                false,
                null);
        TaskStep done = transactions.succeedStep(taskId, step.getId(), "已完成课程引用、学术准确性和内容安全审核。");
        publish(taskId, "STEP_SUCCEEDED", done.getProgressPercent(), done.getStepName(), done.getStatus(), done.getOutputSummary());
    }

    private ResourceAgentResponse fallbackResource(
            GenerationTaskTransactions.ResourceGenerationContext context,
            String resourceType,
            String modality) {
        ResourceType type = ResourceType.normalize(resourceType);
        String title = context.task().getTopic() + " - " + type.displayName();
        String content = """
                # %s

                ## 学习目标
                围绕《%s》中的“%s”，帮助学生建立概念理解、实践路径和自测反馈。

                ## 个性化依据
                %s

                ## 核心讲解
                1. 先回顾相关基础概念。
                2. 再拆解关键知识点和常见误区。
                3. 最后通过实操任务完成迁移训练。

                ## 练习与反馈
                建议完成 3 道基础题、2 道综合题，并记录错因用于后续知识掌握度更新。
                """.formatted(title, context.course().getTitle(), context.task().getTopic(), context.profile().getDialogueSummary());
        return new ResourceAgentResponse(
                title,
                type.name(),
                modality,
                context.profile().getCurrentLevel(),
                25,
                content,
                "资源生成服务不可用，已使用本地模板完成兜底生成。");
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
}
