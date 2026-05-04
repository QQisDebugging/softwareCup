package com.qqisdebugging.softwarecup.backend.learning;

import com.qqisdebugging.softwarecup.backend.agent.ProfileDimensionUpdate;
import com.qqisdebugging.softwarecup.backend.agent.QuestionGradeResult;
import com.qqisdebugging.softwarecup.backend.profile.ProfileDetailResponse;
import java.time.Instant;
import java.util.List;

public record GradeAssessmentResponse(
        String attemptId,
        String studentProfileId,
        String courseId,
        String topic,
        Integer score,
        Integer maxScore,
        String masteryLevel,
        String feedback,
        List<QuestionGradeResult> questionResults,
        List<String> weaknessSignals,
        List<String> nextResourceTypes,
        List<ProfileDimensionUpdate> profileDimensionUpdates,
        ProfileDetailResponse updatedProfile,
        Instant createdAt) {
}
