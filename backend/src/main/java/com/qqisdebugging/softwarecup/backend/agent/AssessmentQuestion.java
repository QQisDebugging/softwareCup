package com.qqisdebugging.softwarecup.backend.agent;

import java.util.List;

public record AssessmentQuestion(
        String id,
        String type,
        String stem,
        List<String> options,
        String answer,
        String rubric,
        String explanation,
        String difficulty,
        List<String> knowledgePoints,
        Integer score) {
}
