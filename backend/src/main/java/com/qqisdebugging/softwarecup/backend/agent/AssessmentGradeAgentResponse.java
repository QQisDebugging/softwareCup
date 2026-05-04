package com.qqisdebugging.softwarecup.backend.agent;

import java.util.List;

public record AssessmentGradeAgentResponse(
        Integer score,
        Integer maxScore,
        String masteryLevel,
        String feedback,
        List<QuestionGradeResult> questionResults,
        List<String> weaknessSignals,
        List<String> nextResourceTypes,
        List<ProfileDimensionUpdate> profileDimensionUpdates) {
}
