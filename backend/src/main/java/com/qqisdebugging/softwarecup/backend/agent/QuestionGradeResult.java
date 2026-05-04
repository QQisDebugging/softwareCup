package com.qqisdebugging.softwarecup.backend.agent;

public record QuestionGradeResult(
        String questionId,
        Integer score,
        Integer maxScore,
        Boolean correct,
        String feedback,
        String knowledgePoint) {
}
