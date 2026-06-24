package com.qqisdebugging.softwarecup.backend.learning;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.qqisdebugging.softwarecup.backend.agent.AgentKnowledgeMatch;
import com.qqisdebugging.softwarecup.backend.agent.AgentUpstreamException;
import com.qqisdebugging.softwarecup.backend.agent.AssessmentGenerateAgentRequest;
import com.qqisdebugging.softwarecup.backend.agent.AssessmentGenerateAgentResponse;
import com.qqisdebugging.softwarecup.backend.agent.AssessmentGradeAgentRequest;
import com.qqisdebugging.softwarecup.backend.agent.AssessmentGradeAgentResponse;
import com.qqisdebugging.softwarecup.backend.agent.ProfileDimensionUpdate;
import com.qqisdebugging.softwarecup.backend.agent.ResourceAgentClient;
import com.qqisdebugging.softwarecup.backend.agent.TutoringAgentRequest;
import com.qqisdebugging.softwarecup.backend.agent.TutoringAgentResponse;
import com.qqisdebugging.softwarecup.backend.course.Course;
import com.qqisdebugging.softwarecup.backend.course.CourseService;
import com.qqisdebugging.softwarecup.backend.profile.ProfileDetailResponse;
import com.qqisdebugging.softwarecup.backend.profile.ProfileDimensionRequest;
import com.qqisdebugging.softwarecup.backend.profile.ProfileService;
import com.qqisdebugging.softwarecup.backend.profile.StudentProfile;
import com.qqisdebugging.softwarecup.backend.profile.UpdateProfileDimensionsRequest;
import java.math.BigDecimal;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class LearningLoopService {
    private static final List<String> DEFAULT_QUESTION_TYPES =
            List.of("选择题", "判断题", "简答题", "代码纠错题");

    private final ProfileService profileService;
    private final CourseService courseService;
    private final ResourceAgentClient resourceAgentClient;
    private final LearningEventRepository eventRepository;
    private final TutoringSessionRepository tutoringSessionRepository;
    private final QuizAttemptRepository quizAttemptRepository;
    private final ObjectMapper objectMapper;

    public LearningLoopService(
            ProfileService profileService,
            CourseService courseService,
            ResourceAgentClient resourceAgentClient,
            LearningEventRepository eventRepository,
            TutoringSessionRepository tutoringSessionRepository,
            QuizAttemptRepository quizAttemptRepository) {
        this.profileService = profileService;
        this.courseService = courseService;
        this.resourceAgentClient = resourceAgentClient;
        this.eventRepository = eventRepository;
        this.tutoringSessionRepository = tutoringSessionRepository;
        this.quizAttemptRepository = quizAttemptRepository;
        this.objectMapper = new ObjectMapper();
    }

    @Transactional
    public TutoringSessionResponse tutor(CreateTutoringRequest request) {
        StudentProfile profile = profileService.requireProfile(request.studentProfileId());
        Course course = courseService.requireCourse(request.courseId());
        TutoringAgentResponse response = tutoringResponse(profile, course, request);

        TutoringSession saved = tutoringSessionRepository.save(new TutoringSession(
                profile.getId(),
                course.getId(),
                request.question(),
                valueOrFallback(response.answer(), "智能体未返回答复。"),
                writeJson(safeList(response.citations())),
                writeJson(safeList(response.followUpQuestions())),
                writeJson(safeList(response.learningActions())),
                writeJson(safeList(response.profileSignals())),
                valueOrFallback(response.mermaidDiagram(), ""),
                valueOrFallback(response.provider(), "unknown"),
                Boolean.TRUE.equals(response.fallbackUsed())));
        eventRepository.save(new LearningEvent(
                profile.getId(),
                course.getId(),
                "TUTORING_COMPLETED",
                summarizeText(request.question(), 180),
                writeJson(response)));
        return toTutoringResponse(saved);
    }

    @Transactional
    public AssessmentGenerateAgentResponse generateAssessment(GenerateAssessmentRequest request) {
        StudentProfile profile = profileService.requireProfile(request.studentProfileId());
        Course course = courseService.requireCourse(request.courseId());
        AssessmentGenerateAgentResponse response = generateAssessmentResponse(profile, course, request);
        eventRepository.save(new LearningEvent(
                profile.getId(),
                course.getId(),
                "ASSESSMENT_GENERATED",
                request.topic(),
                writeJson(response)));
        return response;
    }

    @Transactional
    public GradeAssessmentResponse gradeAssessment(GradeAssessmentRequest request) {
        StudentProfile profile = profileService.requireProfile(request.studentProfileId());
        Course course = courseService.requireCourse(request.courseId());
        AssessmentGradeAgentResponse response = gradeAssessmentResponse(profile, course, request);

        QuizAttempt saved = quizAttemptRepository.save(new QuizAttempt(
                profile.getId(),
                course.getId(),
                request.topic(),
                response.score() == null ? 0 : response.score(),
                response.maxScore() == null ? 1 : response.maxScore(),
                valueOrFallback(response.masteryLevel(), "未判定"),
                writeJson(safeList(request.questions())),
                writeJson(safeList(request.answers())),
                writeJson(response)));

        ProfileDetailResponse updatedProfile = profileService.getProfileDetail(profile.getId());
        List<ProfileDimensionRequest> dimensions = toProfileDimensionRequests(response.profileDimensionUpdates());
        if (!dimensions.isEmpty()) {
            updatedProfile = profileService.updateDimensions(
                    profile.getId(),
                    new UpdateProfileDimensionsRequest(dimensions, "测评结果自动更新画像"));
        }
        eventRepository.save(new LearningEvent(
                profile.getId(),
                course.getId(),
                "ASSESSMENT_GRADED",
                request.topic(),
                writeJson(response)));

        return new GradeAssessmentResponse(
                saved.getId(),
                profile.getId(),
                course.getId(),
                request.topic(),
                response.score(),
                response.maxScore(),
                response.masteryLevel(),
                response.feedback(),
                safeList(response.questionResults()),
                safeList(response.weaknessSignals()),
                safeList(response.nextResourceTypes()),
                safeList(response.profileDimensionUpdates()),
                updatedProfile,
                saved.getCreatedAt());
    }

    @Transactional(readOnly = true)
    public List<LearningEventResponse> listEvents(String studentProfileId) {
        profileService.requireProfile(studentProfileId);
        return eventRepository.findTop100ByStudentProfileIdOrderByCreatedAtDesc(studentProfileId).stream()
                .map(LearningEventResponse::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<TutoringSessionResponse> listTutoringSessions(String studentProfileId) {
        profileService.requireProfile(studentProfileId);
        return tutoringSessionRepository.findTop30ByStudentProfileIdOrderByCreatedAtDesc(studentProfileId).stream()
                .map(this::toTutoringResponse)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<QuizAttemptResponse> listQuizAttempts(String studentProfileId) {
        profileService.requireProfile(studentProfileId);
        return quizAttemptRepository.findTop30ByStudentProfileIdOrderByCreatedAtDesc(studentProfileId).stream()
                .map(QuizAttemptResponse::from)
                .toList();
    }

    private TutoringAgentResponse tutoringResponse(
            StudentProfile profile,
            Course course,
            CreateTutoringRequest request) {
        try {
            TutoringAgentResponse response = requireResponse(resourceAgentClient.tutor(new TutoringAgentRequest(
                    null,
                    profile.getId(),
                    course.getId(),
                    profile.getDialogueSummary(),
                    course.getTitle(),
                    request.question(),
                    safeList(request.conversationHistory()),
                    valueOrFallback(request.modality(), "文本+图解"),
                    safeList(request.knowledgeBasePaths()),
                    safeList(request.documentTexts()))), "Tutoring agent returned empty response");
            if (!hasText(response.answer())) {
                throw new IllegalStateException("Tutoring agent returned empty answer");
            }
            rejectFallbackTutoring(response);
            return response;
        } catch (RuntimeException ex) {
            throw new AgentUpstreamException("Tutoring agent call failed: " + exceptionMessage(ex), ex);
        }
    }

    private AssessmentGenerateAgentResponse generateAssessmentResponse(
            StudentProfile profile,
            Course course,
            GenerateAssessmentRequest request) {
        List<String> questionTypes = safeListOrDefault(request.questionTypes(), DEFAULT_QUESTION_TYPES);
        int count = request.count() == null ? 6 : Math.max(1, Math.min(12, request.count()));
        try {
            return requireResponse(resourceAgentClient.generateAssessment(new AssessmentGenerateAgentRequest(
                    profile.getId(),
                    course.getId(),
                    profile.getDialogueSummary(),
                    course.getTitle(),
                    request.topic(),
                    valueOrFallback(request.difficulty(), "自适应"),
                    questionTypes,
                    count,
                    safeList(request.knowledgeBasePaths()),
                    safeList(request.documentTexts()))), "Assessment generator returned empty response");
        } catch (RuntimeException ex) {
            throw new AgentUpstreamException("Assessment agent generation failed: " + exceptionMessage(ex), ex);
        }
    }

    private AssessmentGradeAgentResponse gradeAssessmentResponse(
            StudentProfile profile,
            Course course,
            GradeAssessmentRequest request) {
        try {
            return requireResponse(resourceAgentClient.gradeAssessment(new AssessmentGradeAgentRequest(
                    profile.getId(),
                    course.getId(),
                    profile.getDialogueSummary(),
                    course.getTitle(),
                    request.topic(),
                    safeList(request.questions()),
                    safeList(request.answers()))), "Assessment grader returned empty response");
        } catch (RuntimeException ex) {
            throw new AgentUpstreamException("Assessment agent grading failed: " + exceptionMessage(ex), ex);
        }
    }

    private TutoringSessionResponse toTutoringResponse(TutoringSession session) {
        return new TutoringSessionResponse(
                session.getId(),
                session.getStudentProfileId(),
                session.getCourseId(),
                session.getQuestion(),
                session.getAnswer(),
                readJson(session.getCitationsJson(), new TypeReference<List<AgentKnowledgeMatch>>() {}),
                readStringList(session.getFollowUpQuestionsJson()),
                readStringList(session.getLearningActionsJson()),
                readStringList(session.getProfileSignalsJson()),
                session.getMermaidDiagram(),
                session.getProvider(),
                session.getFallbackUsed(),
                session.getCreatedAt());
    }

    private List<ProfileDimensionRequest> toProfileDimensionRequests(List<ProfileDimensionUpdate> updates) {
        return safeList(updates).stream()
                .filter(update -> hasText(update.dimensionKey()) && hasText(update.value()))
                .map(update -> new ProfileDimensionRequest(
                        update.dimensionKey(),
                        update.dimensionName(),
                        update.value(),
                        valueOrFallback(update.evidence(), "测评批改结果触发画像更新"),
                        update.confidenceScore() == null ? new BigDecimal("0.70") : update.confidenceScore(),
                        valueOrFallback(update.source(), "assessment_agent")))
                .toList();
    }

    private String writeJson(Object value) {
        try {
            return objectMapper.writeValueAsString(value);
        } catch (JsonProcessingException ex) {
            throw new IllegalStateException("Failed to serialize learning loop payload", ex);
        }
    }

    private <T> T readJson(String json, TypeReference<T> type) {
        try {
            return objectMapper.readValue(json, type);
        } catch (JsonProcessingException ex) {
            throw new IllegalStateException("Failed to deserialize learning loop payload", ex);
        }
    }

    private List<String> readStringList(String json) {
        if (json == null || json.isBlank()) return List.of();
        try {
            JsonNode node = objectMapper.readTree(json);
            if (node == null || node.isNull()) return List.of();
            if (node.isArray()) {
                return objectMapper.convertValue(node, new TypeReference<List<Object>>() {}).stream()
                        .map(this::stringifyLearningSignal)
                        .filter(this::hasText)
                        .toList();
            }
            if (node.isTextual()) return List.of(node.asText());
            if (node.isObject()) {
                return objectMapper.convertValue(node, new TypeReference<java.util.Map<String, Object>>() {}).entrySet().stream()
                        .flatMap(entry -> {
                            Object value = entry.getValue();
                            if (value instanceof List<?> list) {
                                return list.stream().map(this::stringifyLearningSignal);
                            }
                            return java.util.stream.Stream.of(stringifyLearningSignal(value));
                        })
                        .filter(this::hasText)
                        .toList();
            }
            return List.of(node.asText());
        } catch (JsonProcessingException ex) {
            return List.of(json);
        }
    }

    private String stringifyLearningSignal(Object value) {
        if (value == null) return "";
        if (value instanceof String text) return text;
        if (value instanceof java.util.Map<?, ?> map) {
            Object readable = map.get("title");
            if (readable == null) readable = map.get("text");
            if (readable == null) readable = map.get("question");
            if (readable == null) readable = map.get("action");
            if (readable == null) readable = map.get("signal");
            if (readable == null) readable = map.get("reason");
            if (readable != null) return String.valueOf(readable);
        }
        return String.valueOf(value);
    }

    private <T> T requireResponse(T response, String message) {
        if (response == null) {
            throw new IllegalStateException(message);
        }
        return response;
    }

    private void rejectFallbackTutoring(TutoringAgentResponse response) {
        String provider = valueOrFallback(response.provider(), "");
        if (Boolean.TRUE.equals(response.fallbackUsed())
                || provider.toLowerCase(Locale.ROOT).contains("fallback")) {
            throw new IllegalStateException("Tutoring agent returned fallback output");
        }
    }

    private <T> List<T> safeList(List<T> values) {
        return values == null ? List.of() : values;
    }

    private <T> List<T> safeListOrDefault(List<T> values, List<T> fallback) {
        return values == null || values.isEmpty() ? fallback : values;
    }

    private boolean hasText(String value) {
        return value != null && !value.isBlank();
    }

    private String exceptionMessage(Exception ex) {
        return ex.getMessage() == null ? ex.getClass().getSimpleName() : ex.getMessage();
    }

    private String valueOrFallback(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }

    private String summarizeText(String value, int limit) {
        if (value == null) {
            return null;
        }
        String normalized = value.replace('\n', ' ').trim();
        if (normalized.length() <= limit) {
            return normalized;
        }
        return normalized.substring(0, limit);
    }
}
