package com.qqisdebugging.softwarecup.backend.learning;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.qqisdebugging.softwarecup.backend.agent.AgentKnowledgeMatch;
import com.qqisdebugging.softwarecup.backend.agent.AgentUpstreamException;
import com.qqisdebugging.softwarecup.backend.agent.ResourceAgentClient;
import com.qqisdebugging.softwarecup.backend.agent.TutoringAgentRequest;
import com.qqisdebugging.softwarecup.backend.agent.TutoringAgentResponse;
import com.qqisdebugging.softwarecup.backend.common.NotFoundException;
import com.qqisdebugging.softwarecup.backend.course.Course;
import com.qqisdebugging.softwarecup.backend.course.CourseService;
import com.qqisdebugging.softwarecup.backend.profile.ProfileService;
import com.qqisdebugging.softwarecup.backend.profile.StudentProfile;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Locale;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class LearningConversationService {
    private final LearningConversationRepository conversationRepository;
    private final LearningConversationMessageRepository messageRepository;
    private final ProfileService profileService;
    private final CourseService courseService;
    private final ResourceAgentClient resourceAgentClient;
    private final LearningEventRepository eventRepository;
    private final CourseDoubtRecordRepository doubtRecordRepository;
    private final ObjectMapper objectMapper;

    public LearningConversationService(
            LearningConversationRepository conversationRepository,
            LearningConversationMessageRepository messageRepository,
            ProfileService profileService,
            CourseService courseService,
            ResourceAgentClient resourceAgentClient,
            LearningEventRepository eventRepository,
            CourseDoubtRecordRepository doubtRecordRepository) {
        this.conversationRepository = conversationRepository;
        this.messageRepository = messageRepository;
        this.profileService = profileService;
        this.courseService = courseService;
        this.resourceAgentClient = resourceAgentClient;
        this.eventRepository = eventRepository;
        this.doubtRecordRepository = doubtRecordRepository;
        this.objectMapper = new ObjectMapper();
    }

    @Transactional
    public LearningConversationResponse createConversation(CreateLearningConversationRequest request) {
        StudentProfile profile = profileService.requireProfile(request.studentProfileId());
        Course course = courseService.requireCourse(request.courseId());
        LearningConversation conversation = conversationRepository.save(new LearningConversation(
                profile.getId(),
                course.getId(),
                valueOrFallback(request.title(), course.getTitle() + " assistant")));
        return LearningConversationResponse.from(conversation);
    }

    @Transactional(readOnly = true)
    public List<LearningConversationResponse> listConversations(
            String studentProfileId,
            String courseId,
            Boolean archived) {
        profileService.requireProfile(studentProfileId);
        Boolean archivedFilter = archived == null ? Boolean.FALSE : archived;
        if (hasText(courseId)) {
            courseService.requireCourse(courseId);
            return conversationRepository
                    .findByStudentProfileIdAndCourseIdAndArchivedOrderByUpdatedAtDesc(
                            studentProfileId, courseId, archivedFilter)
                    .stream()
                    .map(LearningConversationResponse::from)
                    .toList();
        }
        return conversationRepository
                .findByStudentProfileIdAndArchivedOrderByUpdatedAtDesc(studentProfileId, archivedFilter)
                .stream()
                .map(LearningConversationResponse::from)
                .toList();
    }

    @Transactional
    public LearningConversationResponse updateConversation(
            String conversationId,
            UpdateLearningConversationRequest request) {
        LearningConversation conversation = requireConversation(conversationId);
        if (hasText(request.title())) {
            conversation.updateTitle(request.title().trim());
        }
        if (request.archived() != null) {
            conversation.setArchived(request.archived());
        }
        return LearningConversationResponse.from(conversationRepository.save(conversation));
    }

    @Transactional
    public void deleteConversation(String conversationId) {
        LearningConversation conversation = requireConversation(conversationId);
        messageRepository.deleteByConversationId(conversation.getId());
        conversationRepository.delete(conversation);
    }

    @Transactional(readOnly = true)
    public List<LearningConversationMessageResponse> listMessages(String conversationId) {
        requireConversation(conversationId);
        return messageRepository.findByConversationIdOrderByCreatedAtAscIdAsc(conversationId).stream()
                .map(this::toMessageResponse)
                .toList();
    }

    @Transactional
    public SendLearningConversationMessageResponse sendMessage(
            String conversationId,
            SendLearningConversationMessageRequest request) {
        LearningConversation conversation = requireConversation(conversationId);
        if (Boolean.TRUE.equals(conversation.getArchived())) {
            throw new IllegalArgumentException("Cannot send messages to an archived conversation");
        }
        String content = firstText(request.content(), request.message());
        if (!hasText(content)) {
            throw new IllegalArgumentException("Message content is required");
        }

        StudentProfile profile = profileService.requireProfile(conversation.getStudentProfileId());
        Course course = courseService.requireCourse(conversation.getCourseId());
        List<LearningConversationMessage> previousMessages =
                messageRepository.findByConversationIdOrderByCreatedAtAscIdAsc(conversation.getId());

        LearningConversationMessage userMessage = messageRepository.save(
                LearningConversationMessage.user(conversation.getId(), content.trim()));

        TutoringAgentResponse agentResponse = tutoringResponse(
                conversation,
                profile,
                course,
                content.trim(),
                previousMessages,
                request);

        LearningConversationMessage assistantMessage = messageRepository.save(new LearningConversationMessage(
                conversation.getId(),
                "assistant",
                agentResponse.answer().trim(),
                writeJson(safeList(agentResponse.citations())),
                writeJson(safeList(agentResponse.followUpQuestions())),
                writeJson(safeList(agentResponse.learningActions())),
                writeJson(safeList(agentResponse.profileSignals())),
                valueOrFallback(agentResponse.mermaidDiagram(), ""),
                valueOrFallback(agentResponse.provider(), "unknown"),
                Boolean.TRUE.equals(agentResponse.fallbackUsed())));

        if (shouldAutoRenameConversation(conversation, course)) {
            conversation.updateTitle(conversationTitleFromQuestion(content, course));
        }
        conversation.markMessage(assistantMessage.getContent(), safeInstant(assistantMessage.getCreatedAt()));
        LearningConversation savedConversation = conversationRepository.save(conversation);
        eventRepository.save(new LearningEvent(
                profile.getId(),
                course.getId(),
                "CONVERSATION_MESSAGE_SENT",
                summarizeText(content, 180),
                writeJson(new ConversationEventPayload(
                        conversation.getId(),
                        userMessage.getId(),
                        assistantMessage.getId(),
                        summarizeText(content, 220),
                        summarizeText(assistantMessage.getContent(), 420),
                        summarizeDoubts(content, agentResponse),
                        safeStringList(agentResponse.learningActions()),
                        valueOrFallback(agentResponse.provider(), "unknown"),
                        Boolean.TRUE.equals(agentResponse.fallbackUsed())))));

        // 课程内部助教：把本轮疑惑沉淀为该用户该课程专属的疑惑文档（供画像/教师反馈使用）。
        // 精练原则：只记录学生的问题本身，不堆叠 AI 回答；信号用于画像分析。
        List<String> doubts = summarizeDoubts(content, agentResponse);
        doubtRecordRepository.save(new CourseDoubtRecord(
                profile.getId(),
                course.getId(),
                conversation.getId(),
                summarizeText(content, 120),
                "",
                writeJson(doubts)));

        return new SendLearningConversationMessageResponse(
                LearningConversationResponse.from(savedConversation),
                toMessageResponse(userMessage),
                toMessageResponse(assistantMessage));
    }

    @Transactional(readOnly = true)
    public List<CourseDoubtRecordResponse> listCourseDoubts(String studentProfileId, String courseId) {
        return doubtRecordRepository
                .findByStudentProfileIdAndCourseIdOrderByCreatedAtDesc(studentProfileId, courseId)
                .stream()
                .map(record -> CourseDoubtRecordResponse.from(record, objectMapper))
                .toList();
    }

    private LearningConversation requireConversation(String conversationId) {
        return conversationRepository.findById(conversationId)
                .orElseThrow(() -> new NotFoundException("Learning conversation not found: " + conversationId));
    }

    private TutoringAgentResponse tutoringResponse(
            LearningConversation conversation,
            StudentProfile profile,
            Course course,
            String content,
            List<LearningConversationMessage> previousMessages,
            SendLearningConversationMessageRequest request) {
        try {
            TutoringAgentResponse response = resourceAgentClient.tutor(new TutoringAgentRequest(
                    conversation.getId(),
                    profile.getId(),
                    course.getId(),
                    profile.getDialogueSummary(),
                    course.getTitle(),
                    content,
                    toConversationHistory(previousMessages),
                    valueOrFallback(request.modality(), "text"),
                    safeList(request.knowledgeBasePaths()),
                    safeList(request.documentTexts())));
            if (response == null || !hasText(response.answer())) {
                throw new IllegalStateException("Tutoring agent returned empty answer");
            }
            if (Boolean.TRUE.equals(response.fallbackUsed())
                    || valueOrFallback(response.provider(), "").toLowerCase(Locale.ROOT).contains("fallback")) {
                throw new IllegalStateException("Tutoring agent returned fallback output");
            }
            return response;
        } catch (RuntimeException ex) {
            String reason = ex.getMessage() == null ? ex.getClass().getSimpleName() : ex.getMessage();
            throw new AgentUpstreamException("Conversation agent call failed: " + reason, ex);
        }
    }

    private List<String> toConversationHistory(List<LearningConversationMessage> messages) {
        return messages.stream()
                .map(message -> message.getRole() + ": " + summarizeText(message.getContent(), 1200))
                .toList();
    }

    private LearningConversationMessageResponse toMessageResponse(LearningConversationMessage message) {
        return new LearningConversationMessageResponse(
                message.getId(),
                message.getConversationId(),
                message.getRole(),
                message.getContent(),
                readJson(message.getCitationsJson(), new TypeReference<List<AgentKnowledgeMatch>>() {}),
                readStringList(message.getFollowUpQuestionsJson()),
                readStringList(message.getLearningActionsJson()),
                readStringList(message.getProfileSignalsJson()),
                message.getMermaidDiagram(),
                message.getProvider(),
                message.getFallbackUsed(),
                message.getCreatedAt());
    }

    private String writeJson(Object value) {
        try {
            return objectMapper.writeValueAsString(value);
        } catch (JsonProcessingException ex) {
            throw new IllegalStateException("Failed to serialize learning conversation payload", ex);
        }
    }

    private <T> T readJson(String json, TypeReference<T> type) {
        try {
            return objectMapper.readValue(json, type);
        } catch (JsonProcessingException ex) {
            throw new IllegalStateException("Failed to deserialize learning conversation payload", ex);
        }
    }

    private List<String> readStringList(String json) {
        if (json == null || json.isBlank()) {
            return List.of();
        }
        try {
            JsonNode node = objectMapper.readTree(json);
            if (node == null || node.isNull()) {
                return List.of();
            }
            if (node.isArray()) {
                return objectMapper.convertValue(node, new TypeReference<List<Object>>() {}).stream()
                        .map(this::stringifyLearningSignal)
                        .filter(this::hasText)
                        .toList();
            }
            if (node.isTextual()) {
                return List.of(node.asText());
            }
            return List.of(node.asText());
        } catch (JsonProcessingException ex) {
            return List.of(json);
        }
    }

    private String stringifyLearningSignal(Object value) {
        if (value == null) {
            return "";
        }
        if (value instanceof String text) {
            return text;
        }
        if (value instanceof java.util.Map<?, ?> map) {
            Object readable = map.get("title");
            if (readable == null) readable = map.get("text");
            if (readable == null) readable = map.get("question");
            if (readable == null) readable = map.get("action");
            if (readable == null) readable = map.get("signal");
            if (readable == null) readable = map.get("reason");
            if (readable != null) {
                return String.valueOf(readable);
            }
        }
        return String.valueOf(value);
    }

    private <T> List<T> safeList(List<T> values) {
        return values == null ? List.of() : values;
    }

    private List<String> safeStringList(List<String> values) {
        return values == null
                ? List.of()
                : values.stream().filter(this::hasText).map(String::trim).toList();
    }

    private List<String> summarizeDoubts(String question, TutoringAgentResponse response) {
        List<String> signals = safeStringList(response.profileSignals());
        if (!signals.isEmpty()) {
            return signals.stream().limit(4).toList();
        }
        List<String> followUps = safeStringList(response.followUpQuestions());
        if (!followUps.isEmpty()) {
            return followUps.stream().limit(4).toList();
        }
        String compactQuestion = summarizeText(question, 80);
        return hasText(compactQuestion) ? List.of("学生疑问：" + compactQuestion) : List.of("本轮对话产生新的课程疑问");
    }

    private String firstText(String first, String second) {
        if (hasText(first)) {
            return first;
        }
        return second;
    }

    private String valueOrFallback(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value.trim();
    }

    private boolean hasText(String value) {
        return value != null && !value.isBlank();
    }

    private Instant safeInstant(Instant value) {
        return value == null ? Instant.now() : value;
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

    private boolean shouldAutoRenameConversation(LearningConversation conversation, Course course) {
        String title = valueOrFallback(conversation.getTitle(), "");
        if (!hasText(title)) {
            return true;
        }
        String courseTitle = valueOrFallback(course.getTitle(), "");
        return title.equals(courseTitle + " assistant")
                || title.equals(courseTitle + " AI 助手")
                || title.equals("AI 助手会话")
                || title.endsWith(" AI 助手");
    }

    private String conversationTitleFromQuestion(String question, Course course) {
        String title = summarizeText(question, 32);
        if (!hasText(title)) {
            title = valueOrFallback(course.getTitle(), "新对话");
        }
        return title.length() > 32 ? title.substring(0, 32) : title;
    }

    private record ConversationEventPayload(
            String conversationId,
            String userMessageId,
            String assistantMessageId,
            String question,
            String answerSummary,
            List<String> doubtPoints,
            List<String> learningActions,
            String provider,
            boolean fallbackUsed) {
    }
}
