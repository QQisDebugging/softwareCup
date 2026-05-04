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
