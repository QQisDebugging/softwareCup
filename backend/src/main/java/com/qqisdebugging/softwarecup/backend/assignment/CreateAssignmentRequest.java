package com.qqisdebugging.softwarecup.backend.assignment;

import java.util.List;

/**
 * 老师发布作业/测试的请求。questions 仅在 type=quiz 时使用。
 */
public record CreateAssignmentRequest(
        String type,
        String title,
        String publisher,
        String description,
        String deadlineLabel,
        Integer estimatedMinutes,
        List<QuizQuestionPayload> questions) {

    public record QuizQuestionPayload(String id, String stem, List<String> options, Integer answer) {
    }
}
