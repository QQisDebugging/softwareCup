package com.qqisdebugging.softwarecup.backend.learning;

import java.math.BigDecimal;
import java.time.Instant;

public record KnowledgeMasteryResponse(
        String id,
        String studentProfileId,
        String courseId,
        String knowledgePoint,
        BigDecimal masteryScore,
        String evidenceSummary,
        Instant updatedAt) {
    public static KnowledgeMasteryResponse from(KnowledgeMastery mastery) {
        return new KnowledgeMasteryResponse(
                mastery.getId(),
                mastery.getStudentProfileId(),
                mastery.getCourseId(),
                mastery.getKnowledgePoint(),
                mastery.getMasteryScore(),
                mastery.getEvidenceSummary(),
                mastery.getUpdatedAt());
    }
}
