package com.qqisdebugging.softwarecup.backend.learning;

import java.math.BigDecimal;
import java.time.Instant;

public record QuizAttemptResponse(
        String id,
        String studentProfileId,
        String courseId,
        String resourceId,
        String topic,
        BigDecimal score,
        BigDecimal maxScore,
        Integer correctCount,
        Integer totalCount,
        String weakPoints,
        String masteryLevel,
        String questionsJson,
        String answersJson,
        String gradingJson,
        Instant submittedAt,
        Instant createdAt) {
    public static QuizAttemptResponse from(QuizAttempt attempt) {
        return new QuizAttemptResponse(
                attempt.getId(),
                attempt.getStudentProfileId(),
                attempt.getCourseId(),
                attempt.getResourceId(),
                attempt.getTopic(),
                attempt.getScore(),
                attempt.getMaxScore(),
                attempt.getCorrectCount(),
                attempt.getTotalCount(),
                attempt.getWeakPoints(),
                attempt.getMasteryLevel(),
                attempt.getQuestionsJson(),
                attempt.getAnswersJson(),
                attempt.getGradingJson(),
                attempt.getSubmittedAt(),
                attempt.getCreatedAt());
    }
}
