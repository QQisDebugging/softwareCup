package com.qqisdebugging.softwarecup.backend.learning;

import java.math.BigDecimal;
import java.time.Instant;

public record QuizAttemptResponse(
        String id,
        String studentProfileId,
        String courseId,
        String resourceId,
        BigDecimal score,
        BigDecimal maxScore,
        Integer correctCount,
        Integer totalCount,
        String weakPoints,
        Instant submittedAt) {
    public static QuizAttemptResponse from(QuizAttempt attempt) {
        return new QuizAttemptResponse(
                attempt.getId(),
                attempt.getStudentProfileId(),
                attempt.getCourseId(),
                attempt.getResourceId(),
                attempt.getScore(),
                attempt.getMaxScore(),
                attempt.getCorrectCount(),
                attempt.getTotalCount(),
                attempt.getWeakPoints(),
                attempt.getSubmittedAt());
    }
}
