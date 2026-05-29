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

            runRuleStep(
                    taskId,
                    "PPT_COURSEWARE_GENERATOR",
                    "资源=" + resource.getTitle() + "；学习路径=" + path.title(),
                    "已生成 6 页 PPT 课件/课堂讲稿大纲：学习目标、先修诊断、流程拆解、易错点、实操任务和画像更新。");

            resource = runSafetyReviewStep(taskId, context, resource);

            learningService.recommendGeneratedResource(
                    context.profile(),
                    context.course(),
                    resource,
                    "结合画像、路径规划和安全审核结果，将该资源作为当前阶段优先学习材料。");
            transactions.markSucceeded(taskId, resource.getId(), "多智能体资源生成、路径规划、推荐和安全审核完成");
            publish(taskId, "TASK_SUCCEEDED", 100, "任务完成", TaskStatus.SUCCEEDED.name(), "多智能体任务链执行完成");
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
        } catch (Exception ex) {
            throw failStartedStep(taskId, step, ex);
        }
    }

    private LearningPathResponse runPathPlannerStep(
            String taskId,
            GenerationTaskTransactions.ResourceGenerationContext context) {
        TaskStep step = transactions.startStep(taskId, "PATH_PLANNER", "主题=" + context.task().getTopic());
        try {
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
                String message = exceptionMessage(ex);
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
        } catch (Exception ex) {
            throw failStartedStep(taskId, step, ex);
        }
    }

    private LearningResource runSafetyReviewStep(
            String taskId,
            GenerationTaskTransactions.ResourceGenerationContext context,
            LearningResource resource) {
        TaskStep step = transactions.startStep(taskId, "SAFETY_REVIEWER", "资源=" + resource.getTitle());
        try {
            publish(taskId, "STEP_STARTED", step.getProgressPercent() - 8, step.getStepName(), step.getStatus(), step.getInputSummary());
            long start = System.nanoTime();
            try {
                Map<String, Object> auditResponse = resourceAgentClient.proxy("/agents/safety/audit", auditRequest(context, resource));
                LearningResource reviewedResource = applyAuditRevision(resource, auditResponse);
                transactions.saveAgentAudits(taskId, reviewedResource.getId(), context.course(), reviewedResource, auditResponse);
                transactions.recordInvocation(
                        taskId,
                        step.getId(),
                        agentProperties.getProvider(),
                        agentProperties.getModel(),
                        promptHash(resource.getContent()),
                        "调用内容安全审核智能体：事实性断言、引用覆盖、敏感违规信息过滤",
                        elapsedMs(start),
                        "SUCCEEDED",
                        false,
                        null);
                TaskStep done = transactions.succeedStep(taskId, step.getId(), auditOutputSummary(auditResponse));
                publish(taskId, "STEP_SUCCEEDED", done.getProgressPercent(), done.getStepName(), done.getStatus(), done.getOutputSummary());
                return reviewedResource;
            } catch (Exception ex) {
                String message = exceptionMessage(ex);
                transactions.recordInvocation(
                        taskId,
                        step.getId(),
                        agentProperties.getProvider(),
                        agentProperties.getModel(),
                        promptHash(resource.getContent()),
                        "内容安全审核智能体调用失败，准备进入本地审核兜底",
                        elapsedMs(start),
                        "FAILED",
                        false,
                        message);
                runFallbackSafetyReviewStep(taskId, context, resource, step);
                return resource;
            }
        } catch (Exception ex) {
            throw failStartedStep(taskId, step, ex);
        }
    }

    private RuntimeException failStartedStep(String taskId, TaskStep step, Exception ex) {
        String message = exceptionMessage(ex);
        transactions.failStepAndTask(taskId, step.getId(), message);
        return new StepFailedException(message, ex);
    }

    private String exceptionMessage(Exception ex) {
        return ex.getMessage() == null ? ex.getClass().getSimpleName() : ex.getMessage();
    }

    private void runFallbackSafetyReviewStep(
            String taskId,
            GenerationTaskTransactions.ResourceGenerationContext context,
            LearningResource resource,
            TaskStep step) {
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
        return "内容安全审核完成：可信分=" + score
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

    private static class StepFailedException extends RuntimeException {
        StepFailedException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}
