package com.qqisdebugging.softwarecup.backend.learning;

import com.qqisdebugging.softwarecup.backend.common.NotFoundException;
import com.qqisdebugging.softwarecup.backend.course.Course;
import com.qqisdebugging.softwarecup.backend.course.CourseService;
import com.qqisdebugging.softwarecup.backend.course.LearningResource;
import com.qqisdebugging.softwarecup.backend.course.LearningResourceRepository;
import com.qqisdebugging.softwarecup.backend.course.ResourceType;
import com.qqisdebugging.softwarecup.backend.profile.ProfileDimensionRequest;
import com.qqisdebugging.softwarecup.backend.profile.ProfileDimensionType;
import com.qqisdebugging.softwarecup.backend.profile.ProfileService;
import com.qqisdebugging.softwarecup.backend.profile.StudentProfile;
import com.qqisdebugging.softwarecup.backend.profile.UpdateProfileDimensionsRequest;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class LearningService {
    private final LearningPathRepository pathRepository;
    private final LearningPathNodeRepository nodeRepository;
    private final ResourceRecommendationRepository recommendationRepository;
    private final LearningEventRepository eventRepository;
    private final QuizAttemptRepository quizAttemptRepository;
    private final KnowledgeMasteryRepository masteryRepository;
    private final EvaluationReportRepository evaluationReportRepository;
    private final LearningResourceRepository resourceRepository;
    private final ProfileService profileService;
    private final CourseService courseService;

    public LearningService(
            LearningPathRepository pathRepository,
            LearningPathNodeRepository nodeRepository,
            ResourceRecommendationRepository recommendationRepository,
            LearningEventRepository eventRepository,
            QuizAttemptRepository quizAttemptRepository,
            KnowledgeMasteryRepository masteryRepository,
            EvaluationReportRepository evaluationReportRepository,
            LearningResourceRepository resourceRepository,
            ProfileService profileService,
            CourseService courseService) {
        this.pathRepository = pathRepository;
        this.nodeRepository = nodeRepository;
        this.recommendationRepository = recommendationRepository;
        this.eventRepository = eventRepository;
        this.quizAttemptRepository = quizAttemptRepository;
        this.masteryRepository = masteryRepository;
        this.evaluationReportRepository = evaluationReportRepository;
        this.resourceRepository = resourceRepository;
        this.profileService = profileService;
        this.courseService = courseService;
    }

    @Transactional
    public LearningPathResponse createInitialPath(StudentProfile profile, Course course, String topic) {
        LearningPath path = pathRepository.save(new LearningPath(
                profile.getId(),
                course.getId(),
                topic + " 个性化学习路径"));
        LearningPathNode node1 = nodeRepository.save(new LearningPathNode(
                path.getId(), 1, topic + " 先修基础回顾", null, 15, null, "READY"));
        LearningPathNode node2 = nodeRepository.save(new LearningPathNode(
                path.getId(), 2, topic + " 核心概念讲解", null, 25, node1.getId(), "LOCKED"));
        LearningPathNode node3 = nodeRepository.save(new LearningPathNode(
                path.getId(), 3, topic + " 练习测验与错因分析", null, 20, node2.getId(), "LOCKED"));
        nodeRepository.save(new LearningPathNode(
                path.getId(), 4, topic + " 项目化实操案例", null, 35, node3.getId(), "LOCKED"));
        return LearningPathResponse.from(path, nodeRepository.findByPathIdOrderByNodeOrderAsc(path.getId()));
    }

    @Transactional
    public ResourceRecommendationResponse recommendGeneratedResource(
            StudentProfile profile,
            Course course,
            LearningResource resource,
            String reason) {
        ResourceRecommendation recommendation = recommendationRepository.save(new ResourceRecommendation(
                profile.getId(),
                course.getId(),
                resource.getId(),
                reason,
                BigDecimal.valueOf(0.92)));
        attachResourceToLatestPath(profile.getId(), course.getId(), resource.getId());
        upsertMastery(
                profile.getId(),
                course.getId(),
                resource.getTitle(),
                BigDecimal.valueOf(0.55),
                "根据资源生成任务建立初始掌握度，等待学习行为和测验结果校准。");
        evaluationReportRepository.save(new EvaluationReport(
                profile.getId(),
                course.getId(),
                "已完成个性化资源推送，当前评估基于画像、课程主题和生成资源建立初始基线。",
                BigDecimal.valueOf(0.58),
                "学习目标明确，资源偏好和时间约束已进入推荐策略。",
                "掌握度仍需通过练习记录、停留时长和反馈继续校准。",
                "优先推送核心讲解文档，再安排测验、思维导图和实操案例巩固。"));
        return ResourceRecommendationResponse.from(recommendation);
    }

    @Transactional(readOnly = true)
    public List<LearningPathResponse> listPaths(String studentProfileId, String courseId) {
        profileService.requireProfile(studentProfileId);
        List<LearningPath> paths = courseId == null || courseId.isBlank()
                ? pathRepository.findByStudentProfileIdOrderByCreatedAtDesc(studentProfileId)
                : pathRepository.findByStudentProfileIdAndCourseIdOrderByCreatedAtDesc(studentProfileId, courseId);
        return paths.stream()
                .map(path -> LearningPathResponse.from(path, nodeRepository.findByPathIdOrderByNodeOrderAsc(path.getId())))
                .toList();
    }

    @Transactional(readOnly = true)
    public LearningPathResponse getPath(String pathId) {
        LearningPath path = pathRepository.findById(pathId)
                .orElseThrow(() -> new NotFoundException("Learning path not found: " + pathId));
        return LearningPathResponse.from(path, nodeRepository.findByPathIdOrderByNodeOrderAsc(pathId));
    }

    @Transactional(readOnly = true)
    public List<ResourceRecommendationResponse> listRecommendations(String studentProfileId) {
        profileService.requireProfile(studentProfileId);
        return recommendationRepository.findByStudentProfileIdOrderByCreatedAtDesc(studentProfileId).stream()
                .map(ResourceRecommendationResponse::from)
                .toList();
    }

    @Transactional
    public LearningEventResponse recordEvent(CreateLearningEventRequest request) {
        profileService.requireProfile(request.studentProfileId());
        courseService.requireCourse(request.courseId());
        LearningEvent event = eventRepository.save(new LearningEvent(
                request.studentProfileId(),
                request.courseId(),
                request.resourceId(),
                request.eventType(),
                request.durationSeconds(),
                request.feedbackScore(),
                request.eventPayload()));
        updateLearningStateFromEvent(request);
        return LearningEventResponse.from(event);
    }

    @Transactional(readOnly = true)
    public List<LearningEventResponse> listEvents(String studentProfileId) {
        profileService.requireProfile(studentProfileId);
        return eventRepository.findTop50ByStudentProfileIdOrderByCreatedAtDesc(studentProfileId).stream()
                .map(LearningEventResponse::from)
                .toList();
    }

    @Transactional
    public QuizAttemptResponse recordQuizAttempt(CreateQuizAttemptRequest request) {
        profileService.requireProfile(request.studentProfileId());
        courseService.requireCourse(request.courseId());
        QuizAttempt attempt = quizAttemptRepository.save(new QuizAttempt(
                request.studentProfileId(),
                request.courseId(),
                request.resourceId(),
                request.score(),
                request.maxScore(),
                request.correctCount(),
                request.totalCount(),
                request.weakPoints()));
        BigDecimal masteryScore = request.maxScore().compareTo(BigDecimal.ZERO) == 0
                ? BigDecimal.ZERO
                : request.score().divide(request.maxScore(), 2, RoundingMode.HALF_UP);
        upsertMastery(
                request.studentProfileId(),
                request.courseId(),
                valueOrFallback(request.weakPoints(), "综合测验"),
                masteryScore,
                "基于最近一次测验得分 " + request.score() + "/" + request.maxScore() + " 动态更新。");
        evaluationReportRepository.save(new EvaluationReport(
                request.studentProfileId(),
                request.courseId(),
                "测验提交后自动生成阶段性评估报告。",
                masteryScore,
                "正确题数 " + request.correctCount() + "/" + request.totalCount(),
                valueOrFallback(request.weakPoints(), "暂无明显薄弱点"),
                "针对薄弱点追加练习题和实操案例，并调整后续资源优先级。"));
        return QuizAttemptResponse.from(attempt);
    }

    @Transactional(readOnly = true)
    public List<KnowledgeMasteryResponse> listMastery(String studentProfileId, String courseId) {
        profileService.requireProfile(studentProfileId);
        courseService.requireCourse(courseId);
        return masteryRepository.findByStudentProfileIdAndCourseIdOrderByKnowledgePointAsc(studentProfileId, courseId).stream()
                .map(KnowledgeMasteryResponse::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<EvaluationReportResponse> listEvaluationReports(String studentProfileId, String courseId) {
        profileService.requireProfile(studentProfileId);
        courseService.requireCourse(courseId);
        return evaluationReportRepository.findTop20ByStudentProfileIdAndCourseIdOrderByCreatedAtDesc(studentProfileId, courseId).stream()
                .map(EvaluationReportResponse::from)
                .toList();
    }

    private void upsertMastery(
            String studentProfileId,
            String courseId,
            String knowledgePoint,
            BigDecimal masteryScore,
            String evidenceSummary) {
        KnowledgeMastery mastery = masteryRepository
                .findByStudentProfileIdAndCourseIdAndKnowledgePoint(studentProfileId, courseId, knowledgePoint)
                .orElseGet(() -> new KnowledgeMastery(studentProfileId, courseId, knowledgePoint, masteryScore, evidenceSummary));
        mastery.update(masteryScore, evidenceSummary);
        masteryRepository.save(mastery);
    }

    private void updateLearningStateFromEvent(CreateLearningEventRequest request) {
        LearningResource resource = null;
        if (hasText(request.resourceId())) {
            resource = resourceRepository.findById(request.resourceId()).orElse(null);
        }
        String eventType = valueOrFallback(request.eventType(), "LEARNING_EVENT");
        String eventTypeUpper = eventType.toUpperCase(Locale.ROOT);
        String resourceName = resource == null ? "未绑定具体资源" : resource.getTitle();
        String resourceTypeName = resource == null
                ? "学习资源"
                : ResourceType.normalize(resource.getResourceType()).displayName();
        BigDecimal behaviorScore = inferBehaviorScore(eventTypeUpper, request.feedbackScore());
        if (resource != null) {
            upsertMastery(
                    request.studentProfileId(),
                    request.courseId(),
                    resource.getTitle(),
                    behaviorScore,
                    "学习事件 `" + eventType + "` 自动更新；资源类型=" + resourceTypeName
                            + "；停留=" + valueOrFallback(request.durationSeconds(), 0) + " 秒"
                            + "；反馈=" + valueOrFallback(request.feedbackScore(), -1) + "。");
        }

        List<ProfileDimensionRequest> updates = new ArrayList<>();
        String evidence = "学习事件自动分析：eventType=" + eventType
                + "，resource=" + resourceName
                + "，durationSeconds=" + valueOrFallback(request.durationSeconds(), 0)
                + "，feedbackScore=" + valueOrFallback(request.feedbackScore(), -1);
        updates.add(new ProfileDimensionRequest(
                ProfileDimensionType.LEARNING_BEHAVIOR_PATTERN.name(),
                ProfileDimensionType.LEARNING_BEHAVIOR_PATTERN.displayName(),
                behaviorValue(eventTypeUpper, resourceTypeName, request.durationSeconds(), request.feedbackScore()),
                evidence,
                new BigDecimal("0.68"),
                "learning_event_analyzer"));
        if (request.feedbackScore() != null && request.feedbackScore() <= 2) {
            updates.add(new ProfileDimensionRequest(
                    ProfileDimensionType.MASTERY_WEAKNESS.name(),
                    ProfileDimensionType.MASTERY_WEAKNESS.displayName(),
                    "最近在 `" + resourceName + "` 学习反馈偏低，建议追加讲解文档、PPT课件和分层练习进行补救。",
                    evidence,
                    new BigDecimal("0.73"),
                    "learning_event_analyzer"));
        }
        profileService.updateDimensions(
                request.studentProfileId(),
                new UpdateProfileDimensionsRequest(updates, "学习行为记录触发画像随学随新"));

        if (eventTypeUpper.contains("COMPLETE") || eventTypeUpper.contains("FINISH") || eventTypeUpper.contains("FEEDBACK")) {
            evaluationReportRepository.save(new EvaluationReport(
                    request.studentProfileId(),
                    request.courseId(),
                    "学习行为事件触发阶段性评估更新。",
                    behaviorScore,
                    request.feedbackScore() != null && request.feedbackScore() >= 4
                            ? "当前资源反馈较好，可继续推送同类型资源。"
                            : "已产生可用于画像更新的学习行为证据。",
                    request.feedbackScore() != null && request.feedbackScore() <= 2
                            ? "资源理解或匹配度偏低，需要补救资源。"
                            : "仍需结合测验和答疑记录进一步验证掌握度。",
                    "根据事件类型、停留时长和反馈分动态调整后续资源优先级。"));
        }
    }

    private BigDecimal inferBehaviorScore(String eventType, Integer feedbackScore) {
        if (feedbackScore != null) {
            return BigDecimal.valueOf(Math.max(0, Math.min(5, feedbackScore)))
                    .divide(BigDecimal.valueOf(5), 2, RoundingMode.HALF_UP);
        }
        if (eventType.contains("COMPLETE") || eventType.contains("FINISH")) {
            return new BigDecimal("0.72");
        }
        if (eventType.contains("QUIZ") || eventType.contains("SUBMIT")) {
            return new BigDecimal("0.64");
        }
        if (eventType.contains("VIEW") || eventType.contains("OPEN")) {
            return new BigDecimal("0.48");
        }
        return new BigDecimal("0.50");
    }

    private String behaviorValue(String eventType, String resourceTypeName, Integer durationSeconds, Integer feedbackScore) {
        String stage;
        if (eventType.contains("COMPLETE") || eventType.contains("FINISH")) {
            stage = "完成型学习行为";
        } else if (eventType.contains("VIEW") || eventType.contains("OPEN")) {
            stage = "浏览型学习行为";
        } else if (eventType.contains("FEEDBACK")) {
            stage = "反馈型学习行为";
        } else {
            stage = "过程型学习行为";
        }
        return stage + "；最近资源类型=" + resourceTypeName
                + "；停留=" + valueOrFallback(durationSeconds, 0) + " 秒"
                + "；反馈=" + valueOrFallback(feedbackScore, -1);
    }

    private void attachResourceToLatestPath(String studentProfileId, String courseId, String resourceId) {
        List<LearningPath> paths = pathRepository.findByStudentProfileIdAndCourseIdOrderByCreatedAtDesc(studentProfileId, courseId);
        if (paths.isEmpty()) {
            return;
        }
        List<LearningPathNode> nodes = nodeRepository.findByPathIdOrderByNodeOrderAsc(paths.get(0).getId());
        for (LearningPathNode node : nodes) {
            if (node.getResourceId() == null || node.getResourceId().isBlank()) {
                node.attachResource(resourceId);
            }
        }
        nodeRepository.saveAll(nodes);
    }

    private String valueOrFallback(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }

    private Integer valueOrFallback(Integer value, Integer fallback) {
        return value == null ? fallback : value;
    }

    private boolean hasText(String value) {
        return value != null && !value.isBlank();
    }
}
