package com.qqisdebugging.softwarecup.backend.demo;

import java.util.List;

public record ContestRequirementEvidence(
        String requirementCode,
        String category,
        String title,
        String status,
        Integer score,
        String target,
        String actual,
        List<String> evidenceEndpoints,
        List<String> evidenceNotes) {
}
