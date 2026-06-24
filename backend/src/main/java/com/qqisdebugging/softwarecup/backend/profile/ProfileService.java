package com.qqisdebugging.softwarecup.backend.profile;

import com.qqisdebugging.softwarecup.backend.agent.AgentArtifactService;
import com.qqisdebugging.softwarecup.backend.common.NotFoundException;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ProfileService {
    private static final BigDecimal DEFAULT_CONFIDENCE = new BigDecimal("0.70");

    private final StudentProfileRepository profileRepository;
    private final ProfileDimensionRepository dimensionRepository;
    private final ProfileHistoryRepository historyRepository;
    private final AgentArtifactService agentArtifactService;

    public ProfileService(
            StudentProfileRepository profileRepository,
            ProfileDimensionRepository dimensionRepository,
            ProfileHistoryRepository historyRepository,
            AgentArtifactService agentArtifactService) {
        this.profileRepository = profileRepository;
        this.dimensionRepository = dimensionRepository;
        this.historyRepository = historyRepository;
        this.agentArtifactService = agentArtifactService;
    }

    @Transactional
    public ProfileDetailResponse buildFromDialogue(BuildProfileRequest request) {
        String summary = summarizeDialogue(request.dialogueTurns());
        StudentProfile profile = new StudentProfile(
                request.studentName(),
                request.major(),
                request.currentLevel(),
                request.learningGoal(),
                request.preferences(),
                request.constraintsText(),
                summary);
        StudentProfile saved = profileRepository.save(profile);
        List<ProfileDimensionRequest> agentDimensions = inferDimensionsWithAgent(saved.getId(), request, summary);
        upsertDimensions(
                saved,
                mergeInitialDimensions(
                        mergeInitialDimensions(defaultDimensions(request, summary), agentDimensions),
                        request.dimensions()),
                "DIMENSION_CREATED",
                "dialogue_profile_builder",
                "对话式学习画像初始构建");
        return getProfileDetail(saved.getId());
    }

    @Transactional(readOnly = true)
    public List<ProfileResponse> listProfiles() {
        return profileRepository.findAll().stream()
                .sorted(Comparator.comparing(StudentProfile::getCreatedAt).reversed())
                .map(ProfileResponse::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public ProfileResponse getProfile(String profileId) {
        return ProfileResponse.from(requireProfile(profileId));
    }

    @Transactional(readOnly = true)
    public ProfileDetailResponse getProfileDetail(String profileId) {
        StudentProfile profile = requireProfile(profileId);
        return new ProfileDetailResponse(
                ProfileResponse.from(profile),
                listDimensions(profileId),
                listHistory(profileId).stream().limit(20).toList());
    }

    @Transactional(readOnly = true)
    public List<ProfileDimensionResponse> listDimensions(String profileId) {
        requireProfile(profileId);
        return dimensionRepository.findByProfileIdOrderByDimensionKeyAsc(profileId).stream()
                .map(ProfileDimensionResponse::from)
                .toList();
    }

    @Transactional
    public ProfileDetailResponse updateDimensions(String profileId, UpdateProfileDimensionsRequest request) {
        StudentProfile profile = requireProfile(profileId);
        upsertDimensions(
                profile,
                request.dimensions(),
                "DIMENSION_UPDATED",
                "learning_event_update",
                valueOrFallback(request.reason(), "学习行为触发画像动态更新"));
        profile.touch();
        profileRepository.save(profile);
        return getProfileDetail(profileId);
    }

    @Transactional(readOnly = true)
    public List<ProfileHistoryResponse> listHistory(String profileId) {
        requireProfile(profileId);
        return historyRepository.findByProfileIdOrderByCreatedAtDesc(profileId).stream()
                .map(ProfileHistoryResponse::from)
                .toList();
    }

    public StudentProfile requireProfile(String profileId) {
        return profileRepository.findById(profileId)
                .orElseThrow(() -> new NotFoundException("Student profile not found: " + profileId));
    }

    private String summarizeDialogue(List<String> dialogueTurns) {
        String joined = String.join("\n", dialogueTurns);
        if (joined.length() <= 1200) {
            return joined;
        }
        return joined.substring(0, 1200) + "...";
    }

    private List<ProfileDimensionRequest> defaultDimensions(BuildProfileRequest request, String summary) {
        String evidence = "初始对话自动抽取：" + summarizeText(summary, 260);
        return List.of(
                dimension(
                        ProfileDimensionType.KNOWLEDGE_FOUNDATION,
                        request.currentLevel(),
                        evidence,
                        "dialogue_profile_builder",
                        new BigDecimal("0.72")),
                dimension(
                        ProfileDimensionType.COGNITIVE_STYLE,
                        inferCognitiveStyle(request.preferences()),
                        evidence,
                        "dialogue_profile_builder",
                        new BigDecimal("0.66")),
                dimension(
                        ProfileDimensionType.LEARNING_GOAL,
                        request.learningGoal(),
                        evidence,
                        "dialogue_profile_builder",
                        new BigDecimal("0.78")),
                dimension(
                        ProfileDimensionType.INTEREST_DIRECTION,
                        inferInterestDirection(request.major(), summary),
                        evidence,
                        "dialogue_profile_builder",
                        new BigDecimal("0.62")),
                dimension(
                        ProfileDimensionType.ERROR_PRONE_POINTS,
                        inferErrorPronePoints(request.currentLevel(), summary),
                        evidence,
                        "dialogue_profile_builder",
                        new BigDecimal("0.58")),
                dimension(
                        ProfileDimensionType.TIME_CONSTRAINT,
                        request.constraintsText(),
                        evidence,
                        "dialogue_profile_builder",
                        new BigDecimal("0.76")),
                dimension(
                        ProfileDimensionType.RESOURCE_PREFERENCE,
                        request.preferences(),
                        evidence,
                        "dialogue_profile_builder",
                        new BigDecimal("0.74")),
                dimension(
                        ProfileDimensionType.MASTERY_WEAKNESS,
                        inferMasteryWeakness(request.currentLevel(), summary),
                        evidence,
                        "dialogue_profile_builder",
                        new BigDecimal("0.60")));
    }

    private List<ProfileDimensionRequest> inferDimensionsWithAgent(String profileId, BuildProfileRequest request, String summary) {
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("studentProfileId", profileId);
        payload.put("courseTitle", request.major());
        payload.put("declaredMajor", request.major());
        payload.put("currentLevel", request.currentLevel());
        payload.put("learningGoal", request.learningGoal());
        payload.put("topic", request.learningGoal());
        payload.put("preferences", request.preferences());
        payload.put("constraintsText", request.constraintsText());
        payload.put("dialogueTurns", request.dialogueTurns());
        payload.put("documentTexts", List.of(summary));
        Map<String, Object> response = agentArtifactService.invokeAndStore(
                "PROFILE_INFERENCE_MAIN_FLOW",
                "/agents/profile/infer",
                payload);
        List<ProfileDimensionRequest> dimensions = parseAgentDimensions(response.get("dimensions"));
        if (dimensions.isEmpty()) {
            throw new IllegalStateException("Profile inference agent returned no dimensions");
        }
        return dimensions;
    }

    private List<ProfileDimensionRequest> parseAgentDimensions(Object rawDimensions) {
        if (!(rawDimensions instanceof List<?> items)) {
            return List.of();
        }
        List<ProfileDimensionRequest> dimensions = new ArrayList<>();
        for (Object item : items) {
            if (!(item instanceof Map<?, ?> map)) {
                continue;
            }
            String key = stringValue(map.get("dimensionKey"));
            String value = stringValue(map.get("value"));
            if (key == null || value == null) {
                continue;
            }
            dimensions.add(new ProfileDimensionRequest(
                    key,
                    stringValue(map.get("dimensionName")),
                    value,
                    stringValue(map.get("evidence")),
                    decimalValue(map.get("confidenceScore")),
                    valueOrFallback(stringValue(map.get("source")), "profile_inference_agent")));
        }
        return dimensions;
    }

    private List<ProfileDimensionRequest> mergeInitialDimensions(
            List<ProfileDimensionRequest> defaults,
            List<ProfileDimensionRequest> overrides) {
        Map<String, ProfileDimensionRequest> merged = new LinkedHashMap<>();
        defaults.forEach(dimension -> merged.put(normalizeDimensionKey(dimension.dimensionKey()), dimension));
        if (overrides != null) {
            overrides.forEach(dimension -> merged.put(normalizeDimensionKey(dimension.dimensionKey()), dimension));
        }
        return new ArrayList<>(merged.values());
    }

    private void upsertDimensions(
            StudentProfile profile,
            List<ProfileDimensionRequest> dimensions,
            String defaultEventType,
            String fallbackSource,
            String fallbackEvidence) {
        for (ProfileDimensionRequest request : dimensions) {
            String key = normalizeDimensionKey(request.dimensionKey());
            String name = ProfileDimensionType.displayNameFor(key, request.dimensionName());
            String value = requireText(request.value(), "Dimension value cannot be blank: " + key);
            String evidence = valueOrFallback(request.evidence(), fallbackEvidence);
            String source = valueOrFallback(request.source(), fallbackSource);
            BigDecimal confidence = request.confidenceScore() == null ? DEFAULT_CONFIDENCE : request.confidenceScore();

            ProfileDimension dimension = dimensionRepository.findByProfileIdAndDimensionKey(profile.getId(), key)
                    .orElse(null);
            String previousValue = null;
            String eventType = defaultEventType;
            if (dimension == null) {
                dimension = new ProfileDimension(
                        profile.getId(),
                        key,
                        name,
                        value,
                        evidence,
                        confidence,
                        source);
            } else {
                previousValue = dimension.getDimensionValue();
                eventType = "DIMENSION_UPDATED";
                dimension.update(value, evidence, confidence, source);
            }
            dimensionRepository.save(dimension);
            historyRepository.save(new ProfileHistory(
                    profile.getId(),
                    eventType,
                    key,
                    previousValue,
                    value,
                    evidence,
                    source));
        }
    }

    private ProfileDimensionRequest dimension(
            ProfileDimensionType type,
            String value,
            String evidence,
            String source,
            BigDecimal confidenceScore) {
        return new ProfileDimensionRequest(
                type.name(),
                type.displayName(),
                value,
                evidence,
                confidenceScore,
                source);
    }

    private String normalizeDimensionKey(String key) {
        return requireText(key, "Dimension key cannot be blank")
                .trim()
                .replace('-', '_')
                .replace(' ', '_')
                .toUpperCase(java.util.Locale.ROOT);
    }

    private String inferCognitiveStyle(String preferences) {
        String text = preferences == null ? "" : preferences;
        if (text.contains("图") || text.toLowerCase(java.util.Locale.ROOT).contains("diagram")) {
            return "视觉化学习，适合图解、流程图和案例拆解";
        }
        if (text.contains("视频") || text.toLowerCase(java.util.Locale.ROOT).contains("video")) {
            return "视听结合学习，适合短视频脚本和分步演示";
        }
        if (text.contains("项目") || text.contains("案例")) {
            return "实践驱动学习，适合项目案例和任务式材料";
        }
        return "对话式学习，适合先概念解释再练习巩固";
    }

    private String inferInterestDirection(String major, String summary) {
        String basis = major == null || major.isBlank() ? "本专业" : major;
        if (summary.contains("Spring") || summary.contains("Java") || summary.contains("Web")) {
            return basis + "方向的 Java Web 工程实践";
        }
        if (summary.contains("人工智能") || summary.toLowerCase(java.util.Locale.ROOT).contains("ai")) {
            return basis + "方向的人工智能应用实践";
        }
        return basis + "方向的课程项目与真实应用场景";
    }

    private String inferErrorPronePoints(String currentLevel, String summary) {
        String text = currentLevel + "\n" + summary;
        if (text.contains("弱") || text.contains("薄弱") || text.contains("不熟")) {
            return "基础概念、工程分层和知识迁移容易出现断点";
        }
        if (text.contains("数据库") || text.contains("SQL")) {
            return "数据建模、查询逻辑和工程接口衔接需要重点跟踪";
        }
        return "初始阶段暂未完全暴露，后续通过练习错误和答疑记录动态识别";
    }

    private String inferMasteryWeakness(String currentLevel, String summary) {
        return "当前水平：" + currentLevel + "；薄弱点将结合资源浏览、练习得分和答疑记录持续更新。";
    }

    private String stringValue(Object value) {
        if (value == null) {
            return null;
        }
        String text = String.valueOf(value).trim();
        return text.isBlank() ? null : text;
    }

    private BigDecimal decimalValue(Object value) {
        if (value == null) {
            return DEFAULT_CONFIDENCE;
        }
        if (value instanceof Number number) {
            return BigDecimal.valueOf(number.doubleValue());
        }
        try {
            return new BigDecimal(String.valueOf(value));
        } catch (NumberFormatException ex) {
            return DEFAULT_CONFIDENCE;
        }
    }

    private String requireText(String value, String message) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(message);
        }
        return value.trim();
    }

    private String valueOrFallback(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }

    private String summarizeText(String value, int limit) {
        if (value.length() <= limit) {
            return value;
        }
        return value.substring(0, limit) + "...";
    }
}
