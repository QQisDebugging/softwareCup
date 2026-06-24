package com.qqisdebugging.softwarecup.backend.task;

import com.qqisdebugging.softwarecup.backend.course.LearningResourceResponse;
import java.util.List;

public record ReviewDecisionResponse(
        String taskId,
        ReviewDecision decision,
        String reviewer,
        String note,
        List<LearningResourceResponse> resources,
        GenerationAuditResponse audit) {
}
