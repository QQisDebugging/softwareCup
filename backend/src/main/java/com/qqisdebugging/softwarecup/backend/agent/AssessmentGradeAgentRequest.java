package com.qqisdebugging.softwarecup.backend.agent;

import java.util.List;

public record AssessmentGradeAgentRequest(
        String studentProfileId,
        String courseId,
        String studentProfileSummary,
        String courseTitle,
        String topic,
        List<AssessmentQuestion> questions,
        List<AssessmentAnswer> answers) {
}
