package com.qqisdebugging.softwarecup.backend.profile;

import java.util.Arrays;

public enum ProfileDimensionType {
    KNOWLEDGE_FOUNDATION("知识基础"),
    COGNITIVE_STYLE("认知风格"),
    LEARNING_GOAL("学习目标"),
    INTEREST_DIRECTION("兴趣方向"),
    ERROR_PRONE_POINTS("易错点"),
    TIME_CONSTRAINT("时间约束"),
    RESOURCE_PREFERENCE("资源偏好"),
    MASTERY_WEAKNESS("掌握度/薄弱点"),
    LEARNING_BEHAVIOR_PATTERN("学习行为模式");

    private final String displayName;

    ProfileDimensionType(String displayName) {
        this.displayName = displayName;
    }

    public String displayName() {
        return displayName;
    }

    public static String displayNameFor(String key, String fallback) {
        if (fallback != null && !fallback.isBlank()) {
            return fallback;
        }
        return Arrays.stream(values())
                .filter(type -> type.name().equalsIgnoreCase(key))
                .findFirst()
                .map(ProfileDimensionType::displayName)
                .orElse(key);
    }
}
