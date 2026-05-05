package com.qqisdebugging.softwarecup.backend.course;

import java.util.Arrays;
import java.util.Locale;

public enum ResourceType {
    COURSE_EXPLANATION_DOCUMENT("课程讲解文档"),
    KNOWLEDGE_MIND_MAP("知识点思维导图"),
    QUIZ_PRACTICE("练习题/测验"),
    EXTENDED_READING("拓展阅读"),
    PRACTICE_CASE("实操案例"),
    VIDEO_ANIMATION_SCRIPT("视频讲解脚本/动画脚本");

    private final String displayName;

    ResourceType(String displayName) {
        this.displayName = displayName;
    }

    public String displayName() {
        return displayName;
    }

    public static ResourceType normalize(String value) {
        if (value == null || value.isBlank()) {
            return COURSE_EXPLANATION_DOCUMENT;
        }
        String normalized = value.trim().toUpperCase(Locale.ROOT).replace("-", "_").replace(" ", "_");
        return Arrays.stream(values())
                .filter(type -> type.name().equals(normalized) || type.displayName.equals(value.trim()))
                .findFirst()
                .orElseGet(() -> {
                    String text = value.trim();
                    if (text.contains("思维导图") || text.contains("mind")) {
                        return KNOWLEDGE_MIND_MAP;
                    }
                    if (text.contains("练习") || text.contains("测验") || text.contains("quiz")) {
                        return QUIZ_PRACTICE;
                    }
                    if (text.contains("阅读") || text.contains("拓展")) {
                        return EXTENDED_READING;
                    }
                    if (text.contains("案例") || text.contains("实操")) {
                        return PRACTICE_CASE;
                    }
                    if (text.contains("视频") || text.contains("动画") || text.contains("脚本")) {
                        return VIDEO_ANIMATION_SCRIPT;
                    }
                    return COURSE_EXPLANATION_DOCUMENT;
                });
    }
}
