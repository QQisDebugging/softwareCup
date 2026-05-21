package com.qqisdebugging.softwarecup.backend.demo;

import com.qqisdebugging.softwarecup.backend.agent.AgentArtifact;
import com.qqisdebugging.softwarecup.backend.agent.AgentArtifactRepository;
import com.qqisdebugging.softwarecup.backend.agent.AgentDefinitionRepository;
import com.qqisdebugging.softwarecup.backend.course.Course;
import com.qqisdebugging.softwarecup.backend.course.CourseRepository;
import com.qqisdebugging.softwarecup.backend.course.ResourceType;
import com.qqisdebugging.softwarecup.backend.learning.EvaluationReport;
import com.qqisdebugging.softwarecup.backend.learning.EvaluationReportRepository;
import com.qqisdebugging.softwarecup.backend.learning.KnowledgeMastery;
import com.qqisdebugging.softwarecup.backend.learning.KnowledgeMasteryRepository;
import com.qqisdebugging.softwarecup.backend.learning.LearningEvent;
import com.qqisdebugging.softwarecup.backend.learning.LearningEventRepository;
import com.qqisdebugging.softwarecup.backend.learning.LearningPath;
import com.qqisdebugging.softwarecup.backend.learning.LearningPathNodeRepository;
import com.qqisdebugging.softwarecup.backend.learning.LearningPathRepository;
import com.qqisdebugging.softwarecup.backend.learning.QuizAttempt;
import com.qqisdebugging.softwarecup.backend.learning.QuizAttemptRepository;
import com.qqisdebugging.softwarecup.backend.learning.ResourceRecommendation;
import com.qqisdebugging.softwarecup.backend.learning.ResourceRecommendationRepository;
import com.qqisdebugging.softwarecup.backend.learning.TutoringSession;
import com.qqisdebugging.softwarecup.backend.learning.TutoringSessionRepository;
import com.qqisdebugging.softwarecup.backend.profile.ProfileDimensionRepository;
import com.qqisdebugging.softwarecup.backend.profile.ProfileHistoryRepository;
import com.qqisdebugging.softwarecup.backend.profile.StudentProfile;
import com.qqisdebugging.softwarecup.backend.profile.StudentProfileRepository;
import com.qqisdebugging.softwarecup.backend.task.GenerationAudit;
import com.qqisdebugging.softwarecup.backend.task.GenerationAuditRepository;
import com.qqisdebugging.softwarecup.backend.task.GenerationTask;
import com.qqisdebugging.softwarecup.backend.task.GenerationTaskRepository;
import com.qqisdebugging.softwarecup.backend.task.ModelInvocationRepository;
import com.qqisdebugging.softwarecup.backend.task.TaskStepRepository;
import java.time.Instant;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ContestReadinessService {
    private final CourseRepository courseRepository;
    private final StudentProfileRepository profileRepository;
    private final ProfileDimensionRepository dimensionRepository;
    private final ProfileHistoryRepository historyRepository;
    private final AgentDefinitionRepository agentDefinitionRepository;
    private final GenerationTaskRepository taskRepository;
    private final TaskStepRepository taskStepRepository;
    private final ModelInvocationRepository modelInvocationRepository;
    private final GenerationAuditRepository auditRepository;
    private final LearningPathRepository pathRepository;
    private final LearningPathNodeRepository pathNodeRepository;
    private final ResourceRecommendationRepository recommendationRepository;
    private final LearningEventRepository eventRepository;
    private final TutoringSessionRepository tutoringRepository;
    private final QuizAttemptRepository quizAttemptRepository;
    private final KnowledgeMasteryRepository masteryRepository;
    private final EvaluationReportRepository evaluationReportRepository;
    private final AgentArtifactRepository artifactRepository;

    public ContestReadinessService(
            CourseRepository courseRepository,
            StudentProfileRepository profileRepository,
            ProfileDimensionRepository dimensionRepository,
            ProfileHistoryRepository historyRepository,
            AgentDefinitionRepository agentDefinitionRepository,
            GenerationTaskRepository taskRepository,
            TaskStepRepository taskStepRepository,
            ModelInvocationRepository modelInvocationRepository,
            GenerationAuditRepository auditRepository,
            LearningPathRepository pathRepository,
            LearningPathNodeRepository pathNodeRepository,
            ResourceRecommendationRepository recommendationRepository,
            LearningEventRepository eventRepository,
            TutoringSessionRepository tutoringRepository,
            QuizAttemptRepository quizAttemptRepository,
            KnowledgeMasteryRepository masteryRepository,
            EvaluationReportRepository evaluationReportRepository,
            AgentArtifactRepository artifactRepository) {
        this.courseRepository = courseRepository;
        this.profileRepository = profileRepository;
        this.dimensionRepository = dimensionRepository;
        this.historyRepository = historyRepository;
        this.agentDefinitionRepository = agentDefinitionRepository;
        this.taskRepository = taskRepository;
        this.taskStepRepository = taskStepRepository;
        this.modelInvocationRepository = modelInvocationRepository;
        this.auditRepository = auditRepository;
        this.pathRepository = pathRepository;
        this.pathNodeRepository = pathNodeRepository;
        this.recommendationRepository = recommendationRepository;
        this.eventRepository = eventRepository;
        this.tutoringRepository = tutoringRepository;
        this.quizAttemptRepository = quizAttemptRepository;
        this.masteryRepository = masteryRepository;
        this.evaluationReportRepository = evaluationReportRepository;
        this.artifactRepository = artifactRepository;
    }

    @Transactional(readOnly = true)
    public ContestReadinessResponse buildReport(String requestedProfileId, String requestedCourseId, String requestedTaskId) {
        GenerationTask selectedTask = selectTask(requestedTaskId, requestedProfileId, requestedCourseId).orElse(null);
        String profileId = valueOrFallback(requestedProfileId, selectedTask == null ? null : selectedTask.getStudentProfileId());
        String courseId = valueOrFallback(requestedCourseId, selectedTask == null ? null : selectedTask.getCourseId());
        profileId = valueOrFallback(profileId, latestProfileId().orElse(null));
        courseId = valueOrFallback(courseId, latestCourseId().orElse(null));

        ContestReadinessMetrics metrics = metrics(profileId, courseId, selectedTask);
        List<ContestRequirementEvidence> requirements = List.of(
                profileRequirement(profileId, metrics),
                multiAgentRequirement(selectedTask, metrics),
                learningPathRequirement(profileId, courseId, metrics),
                tutoringRequirement(profileId, metrics),
                evaluationRequirement(profileId, courseId, metrics),
                safetyRequirement(selectedTask, metrics),
                progressRequirement(selectedTask, metrics),
                deliveryRequirement(metrics));
        int overall = (int) Math.round(requirements.stream()
                .mapToInt(ContestRequirementEvidence::score)
                .average()
                .orElse(0));
        return new ContestReadinessResponse(
                Instant.now(),
                scope(profileId, courseId, selectedTask),
                overall,
                summary(overall, metrics),
                metrics,
                requirements,
                demoHighlights(metrics),
                demoFlow(profileId, courseId, selectedTask));
    }

    private ContestReadinessMetrics metrics(String profileId, String courseId, GenerationTask selectedTask) {
        List<GenerationTask> tasks = taskRepository.findAll();
        List<GenerationTask> scopedTasks = tasks.stream()
                .filter(task -> !hasText(profileId) || Objects.equals(task.getStudentProfileId(), profileId))
                .filter(task -> !hasText(courseId) || Objects.equals(task.getCourseId(), courseId))
                .toList();
        List<GenerationAudit> audits = selectedTask == null
                ? auditRepository.findAll()
                : auditRepository.findByTaskIdOrderByCreatedAtDesc(selectedTask.getId());
        List<LearningPath> paths = pathRepository.findAll().stream()
                .filter(path -> !hasText(profileId) || Objects.equals(path.getStudentProfileId(), profileId))
                .filter(path -> !hasText(courseId) || Objects.equals(path.getCourseId(), courseId))
                .toList();
        int pathNodeCount = paths.stream()
                .mapToInt(path -> pathNodeRepository.findByPathIdOrderByNodeOrderAsc(path.getId()).size())
                .sum();
        List<AgentArtifact> artifacts = artifactRepository.findAll().stream()
                .filter(artifact -> !hasText(profileId) || Objects.equals(artifact.getStudentProfileId(), profileId))
                .filter(artifact -> !hasText(courseId) || Objects.equals(artifact.getCourseId(), courseId))
                .toList();
        return new ContestReadinessMetrics(
                courseRepository.count(),
                profileRepository.count(),
                hasText(profileId) ? dimensionRepository.findByProfileIdOrderByDimensionKeyAsc(profileId).size() : (int) dimensionRepository.count(),
                hasText(profileId) ? historyRepository.findByProfileIdOrderByCreatedAtDesc(profileId).size() : (int) historyRepository.count(),
                agentDefinitionRepository.findByEnabledTrueOrderBySortOrderAsc().size(),
                ResourceType.values().length,
                scopedTasks.size(),
                (int) scopedTasks.stream().filter(task -> "SUCCEEDED".equals(task.getStatus())).count(),
                selectedTask == null ? (int) taskStepRepository.count() : taskStepRepository.findByTaskIdOrderByStepOrderAsc(selectedTask.getId()).size(),
                selectedTask == null ? (int) modelInvocationRepository.count() : modelInvocationRepository.findByTaskIdOrderByCreatedAtDesc(selectedTask.getId()).size(),
                audits.size(),
                (int) audits.stream().filter(audit -> Boolean.TRUE.equals(audit.getReviewerRequired())).count(),
                (int) audits.stream().filter(audit -> "HUMAN_REVIEW_GATE".equals(audit.getAuditType())).count(),
                paths.size(),
                pathNodeCount,
                scopedRecommendations(profileId).size(),
                scopedEvents(profileId).size(),
                scopedTutoring(profileId).size(),
                scopedAttempts(profileId, courseId).size(),
                scopedMastery(profileId, courseId).size(),
                scopedReports(profileId, courseId).size(),
                artifacts.size());
    }

    private ContestRequirementEvidence profileRequirement(String profileId, ContestReadinessMetrics metrics) {
        int score = metrics.profileDimensionCount() >= 8 ? 100 : metrics.profileDimensionCount() >= 6 ? 85 : 45;
        if (metrics.profileHistoryCount() > 0) {
            score = Math.min(100, score + 5);
        }
        return evidence(
                "REQ-1",
                "基本功能",
                "对话式学习画像自主构建",
                score,
                "不少于 6 个画像维度，并支持随学随新。",
                "当前画像维度 " + metrics.profileDimensionCount() + " 个，画像历史 " + metrics.profileHistoryCount() + " 条。",
                List.of(
                        endpoint("/api/profiles/{profileId}/detail", profileId),
                        endpoint("/api/profiles/{profileId}/dimensions", profileId),
                        endpoint("/api/profiles/{profileId}/history", profileId),
                        endpoint("/api/agent-artifacts?studentProfileId={profileId}&artifactType=PROFILE_INFERENCE_MAIN_FLOW", profileId)),
                List.of("画像创建优先调用 ProfileInferenceAgent，失败时降级为规则画像。"));
    }

    private ContestRequirementEvidence multiAgentRequirement(GenerationTask task, ContestReadinessMetrics metrics) {
        int score = 0;
        if (metrics.enabledAgentCount() >= 8) {
            score += 35;
        }
        if (metrics.resourceTypeCount() >= 7) {
            score += 30;
        } else if (metrics.resourceTypeCount() >= 5) {
            score += 22;
        }
        if (metrics.taskStepCount() >= 9) {
            score += 25;
        }
        if (metrics.modelInvocationCount() > 0) {
            score += 10;
        }
        return evidence(
                "REQ-2",
                "基本功能",
                "多智能体协同资源生成",
                score,
                "体现多智能体架构，至少生成 5 种资源类型。",
                "启用智能体 " + metrics.enabledAgentCount()
                        + " 个，固定资源类型 " + metrics.resourceTypeCount()
                        + " 类，任务步骤 " + metrics.taskStepCount()
                        + " 条，模型调用记录 " + metrics.modelInvocationCount() + " 条。",
                List.of(
                        "/api/agents",
                        "/api/resource-types",
                        endpoint("/api/tasks/{taskId}/steps", task == null ? null : task.getId()),
                        endpoint("/api/tasks/{taskId}/model-invocations", task == null ? null : task.getId())),
                List.of("建议演示时打开任务步骤表，展示画像分析到安全审核的完整任务链。"));
    }

    private ContestRequirementEvidence learningPathRequirement(String profileId, String courseId, ContestReadinessMetrics metrics) {
        int score = 40;
        if (metrics.learningPathCount() > 0) {
            score += 25;
        }
        if (metrics.learningPathNodeCount() >= 3) {
            score += 20;
        }
        if (metrics.resourceRecommendationCount() > 0) {
            score += 15;
        }
        return evidence(
                "REQ-3",
                "基本功能",
                "个性化学习路径规划和资源推送",
                Math.min(score, 100),
                "明确学习步骤、顺序、前置依赖，并基于画像精准推送资源。",
                "学习路径 " + metrics.learningPathCount()
                        + " 条，路径节点 " + metrics.learningPathNodeCount()
                        + " 个，资源推荐 " + metrics.resourceRecommendationCount() + " 条。",
                List.of(
                        endpoint("/api/learning/paths?studentProfileId={profileId}&courseId={courseId}", profileId, courseId),
                        endpoint("/api/learning/recommendations?studentProfileId={profileId}", profileId)),
                List.of("路径节点可映射知识点、资源、预计时长、前置依赖和完成状态。"));
    }

    private ContestRequirementEvidence tutoringRequirement(String profileId, ContestReadinessMetrics metrics) {
        int score = metrics.tutoringSessionCount() > 0 ? 100 : 82;
        return evidence(
                "BONUS-1",
                "可选加分",
                "智能辅导与即时答疑",
                score,
                "提供即时、多模态答疑，输出文字、图解或脚本化讲解。",
                "已保存答疑会话 " + metrics.tutoringSessionCount() + " 条；Python TutoringAgent 已接入 Java 代理接口。",
                List.of(
                        "/api/learning/tutoring",
                        endpoint("/api/learning/tutoring?studentProfileId={profileId}", profileId)),
                List.of("建议初赛演示至少创建 1 次答疑会话，让报告从 READY 变成有真实记录的 PASSED。"));
    }

    private ContestRequirementEvidence evaluationRequirement(String profileId, String courseId, ContestReadinessMetrics metrics) {
        int score = 45;
        if (metrics.learningEventCount() > 0) {
            score += 15;
        }
        if (metrics.quizAttemptCount() > 0) {
            score += 15;
        }
        if (metrics.knowledgeMasteryCount() > 0) {
            score += 15;
        }
        if (metrics.evaluationReportCount() > 0) {
            score += 10;
        }
        return evidence(
                "BONUS-2",
                "可选加分",
                "学习效果评估和动态优化",
                Math.min(score, 100),
                "跟踪学习行为、练习测试和反馈，动态调整画像、路径和资源推送。",
                "学习事件 " + metrics.learningEventCount()
                        + " 条，测评记录 " + metrics.quizAttemptCount()
                        + " 条，掌握度 " + metrics.knowledgeMasteryCount()
                        + " 个，评估报告 " + metrics.evaluationReportCount() + " 份。",
                List.of(
                        endpoint("/api/learning/events?studentProfileId={profileId}", profileId),
                        endpoint("/api/learning/mastery?studentProfileId={profileId}&courseId={courseId}", profileId, courseId),
                        endpoint("/api/learning/evaluation-reports?studentProfileId={profileId}&courseId={courseId}", profileId, courseId)),
                List.of("建议演示先完成资源浏览/反馈/测评，再展示画像和掌握度被自动更新。"));
    }

    private ContestRequirementEvidence safetyRequirement(GenerationTask task, ContestReadinessMetrics metrics) {
        int score = 60;
        if (metrics.generationAuditCount() >= 4) {
            score += 20;
        }
        if (metrics.humanReviewGateCount() > 0) {
            score += 15;
        }
        if (metrics.reviewRequiredAuditCount() > 0) {
            score += 5;
        }
        return evidence(
                "NFR-1",
                "非功能",
                "防幻觉与内容安全过滤",
                Math.min(score, 100),
                "确保生成学术内容无事实性错误、无敏感违规信息，并可人工复核。",
                "生成审核 " + metrics.generationAuditCount()
                        + " 条，人工复核门禁 " + metrics.humanReviewGateCount()
                        + " 条，需要复核 " + metrics.reviewRequiredAuditCount() + " 条。",
                List.of(
                        "/api/learning/content-audits",
                        endpoint("/api/tasks/{taskId}/audits", task == null ? null : task.getId())),
                List.of("ContentAuditAgent 会输出 unsupportedClaims、riskyClaims 和 revisedContent。"));
    }

    private ContestRequirementEvidence progressRequirement(GenerationTask task, ContestReadinessMetrics metrics) {
        int score = 80;
        if (metrics.taskStepCount() >= 9) {
            score += 10;
        }
        if (metrics.modelInvocationCount() > 0) {
            score += 10;
        }
        return evidence(
                "NFR-2",
                "非功能",
                "生成进度追踪与可观测性",
                Math.min(score, 100),
                "提供进度追踪或流式呈现，避免长时间白屏等待。",
                "任务步骤 " + metrics.taskStepCount()
                        + " 条，模型调用 " + metrics.modelInvocationCount() + " 条，SSE 进度接口已开放。",
                List.of(
                        endpoint("/api/tasks/{taskId}/events", task == null ? null : task.getId()),
                        endpoint("/api/tasks/{taskId}/steps", task == null ? null : task.getId())),
                List.of("前端可展示：画像分析中 -> 路径规划中 -> 资源生成中 -> 安全审核中。"));
    }

    private ContestRequirementEvidence deliveryRequirement(ContestReadinessMetrics metrics) {
        int score = 70;
        if (metrics.courseCount() > 0) {
            score += 15;
        }
        if (metrics.agentArtifactCount() > 0) {
            score += 15;
        }
        return evidence(
                "NFR-3",
                "交付与文档",
                "完整课程数据、可运行文件和答辩证据",
                Math.min(score, 100),
                "自构造至少一门完整高校课程，并提供可运行源码、数据、配置和演示证据。",
                "课程 " + metrics.courseCount()
                        + " 门，Agent 结构化产物 " + metrics.agentArtifactCount() + " 个。",
                List.of(
                        "/api/courses",
                        "/api/agent-artifacts",
                        "/api/demo/readiness-report"),
                List.of("该报告可作为 PPT/视频里的评委模式截图。"));
    }

    private ContestRequirementEvidence evidence(
            String code,
            String category,
            String title,
            int score,
            String target,
            String actual,
            List<String> endpoints,
            List<String> notes) {
        return new ContestRequirementEvidence(
                code,
                category,
                title,
                status(score),
                Math.max(0, Math.min(100, score)),
                target,
                actual,
                endpoints,
                notes);
    }

    private Optional<GenerationTask> selectTask(String taskId, String profileId, String courseId) {
        if (hasText(taskId)) {
            return taskRepository.findById(taskId);
        }
        return taskRepository.findTop50ByOrderByCreatedAtDesc().stream()
                .filter(task -> !hasText(profileId) || Objects.equals(task.getStudentProfileId(), profileId))
                .filter(task -> !hasText(courseId) || Objects.equals(task.getCourseId(), courseId))
                .findFirst();
    }

    private List<ResourceRecommendation> scopedRecommendations(String profileId) {
        return recommendationRepository.findAll().stream()
                .filter(item -> !hasText(profileId) || Objects.equals(item.getStudentProfileId(), profileId))
                .toList();
    }

    private List<LearningEvent> scopedEvents(String profileId) {
        return eventRepository.findAll().stream()
                .filter(item -> !hasText(profileId) || Objects.equals(item.getStudentProfileId(), profileId))
                .toList();
    }

    private List<TutoringSession> scopedTutoring(String profileId) {
        return tutoringRepository.findAll().stream()
                .filter(item -> !hasText(profileId) || Objects.equals(item.getStudentProfileId(), profileId))
                .toList();
    }

    private List<QuizAttempt> scopedAttempts(String profileId, String courseId) {
        return quizAttemptRepository.findAll().stream()
                .filter(item -> !hasText(profileId) || Objects.equals(item.getStudentProfileId(), profileId))
                .filter(item -> !hasText(courseId) || Objects.equals(item.getCourseId(), courseId))
                .toList();
    }

    private List<KnowledgeMastery> scopedMastery(String profileId, String courseId) {
        return masteryRepository.findAll().stream()
                .filter(item -> !hasText(profileId) || Objects.equals(item.getStudentProfileId(), profileId))
                .filter(item -> !hasText(courseId) || Objects.equals(item.getCourseId(), courseId))
                .toList();
    }

    private List<EvaluationReport> scopedReports(String profileId, String courseId) {
        return evaluationReportRepository.findAll().stream()
                .filter(item -> !hasText(profileId) || Objects.equals(item.getStudentProfileId(), profileId))
                .filter(item -> !hasText(courseId) || Objects.equals(item.getCourseId(), courseId))
                .toList();
    }

    private Optional<String> latestProfileId() {
        return profileRepository.findAll().stream()
                .max(Comparator.comparing(StudentProfile::getCreatedAt))
                .map(StudentProfile::getId);
    }

    private Optional<String> latestCourseId() {
        return courseRepository.findAll().stream()
                .max(Comparator.comparing(Course::getCreatedAt))
                .map(Course::getId);
    }

    private String status(int score) {
        if (score >= 95) {
            return "EXCELLENT";
        }
        if (score >= 80) {
            return "PASSED";
        }
        if (score >= 60) {
            return "READY";
        }
        return "DEMO_DATA_NEEDED";
    }

    private String summary(int overall, ContestReadinessMetrics metrics) {
        return "初赛评委模式报告：总体达成度 " + overall
                + "/100；当前具备 " + metrics.enabledAgentCount()
                + " 个智能体、" + metrics.resourceTypeCount()
                + " 类资源、" + metrics.profileDimensionCount()
                + " 个画像维度、" + metrics.generationAuditCount()
                + " 条内容审核证据和 " + metrics.evaluationReportCount()
                + " 份评估报告。";
    }

    private List<String> demoHighlights(ContestReadinessMetrics metrics) {
        return List.of(
                "画像不是表单：已支持 ProfileInferenceAgent 从自然语言抽取 " + metrics.profileDimensionCount() + " 个维度。",
                "多智能体可观测：任务链、模型调用、耗时、失败兜底和审核结果均可查询。",
                "资源覆盖超要求：固定 " + metrics.resourceTypeCount() + " 类资源，超过题目至少 5 类要求。",
                "防幻觉可证明：generation_audits 保留课程证据、学术准确性、内容安全和人工复核门禁。",
                "学习闭环完整：学习事件、测评、掌握度、评估报告和资源推荐形成动态优化链路。");
    }

    private List<String> demoFlow(String profileId, String courseId, GenerationTask task) {
        return List.of(
                "1. 打开画像详情：" + endpoint("/api/profiles/{profileId}/detail", profileId),
                "2. 展示资源生成任务链：" + endpoint("/api/tasks/{taskId}/steps", task == null ? null : task.getId()),
                "3. 展示 7 类资源筛选：" + "/api/resource-types",
                "4. 展示路径与推荐：" + endpoint("/api/learning/paths?studentProfileId={profileId}&courseId={courseId}", profileId, courseId),
                "5. 展示内容审核门禁：" + endpoint("/api/tasks/{taskId}/audits", task == null ? null : task.getId()),
                "6. 展示学习效果闭环：" + endpoint("/api/learning/evaluation-reports?studentProfileId={profileId}&courseId={courseId}", profileId, courseId),
                "7. 最后展示本报告：" + "/api/demo/readiness-report");
    }

    private String scope(String profileId, String courseId, GenerationTask task) {
        return "studentProfileId=" + valueOrFallback(profileId, "ALL")
                + "; courseId=" + valueOrFallback(courseId, "ALL")
                + "; taskId=" + (task == null ? "LATEST_OR_ALL" : task.getId());
    }

    private String endpoint(String template, String value) {
        return hasText(value) ? template.replace("{profileId}", value).replace("{taskId}", value) : template;
    }

    private String endpoint(String template, String profileId, String courseId) {
        return template
                .replace("{profileId}", valueOrFallback(profileId, "{profileId}"))
                .replace("{courseId}", valueOrFallback(courseId, "{courseId}"));
    }

    private String valueOrFallback(String value, String fallback) {
        return hasText(value) ? value : fallback;
    }

    private boolean hasText(String value) {
        return value != null && !value.isBlank();
    }
}
