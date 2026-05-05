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
package com.qqisdebugging.softwarecup.backend.learning;

import com.qqisdebugging.softwarecup.backend.agent.AssessmentAnswer;
import com.qqisdebugging.softwarecup.backend.agent.AssessmentGradeAgentResponse;
import com.qqisdebugging.softwarecup.backend.agent.AssessmentQuestion;
import java.time.Instant;
import java.util.List;

public record QuizAttemptResponse(
        String id,
        String studentProfileId,
        String courseId,
        String topic,
        Integer score,
        Integer maxScore,
        String masteryLevel,
        List<AssessmentQuestion> questions,
        List<AssessmentAnswer> answers,
        AssessmentGradeAgentResponse grading,
        Instant createdAt) {
}
