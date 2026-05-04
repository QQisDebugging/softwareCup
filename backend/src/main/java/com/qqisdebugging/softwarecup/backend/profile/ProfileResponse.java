package com.qqisdebugging.softwarecup.backend.profile;

import java.time.Instant;

public record ProfileResponse(
        String id,
        String studentName,
        String major,
        String currentLevel,
        String learningGoal,
        String preferences,
        String constraintsText,
        String dialogueSummary,
        Instant createdAt,
        Instant updatedAt) {
    static ProfileResponse from(StudentProfile profile) {
        return new ProfileResponse(
                profile.getId(),
                profile.getStudentName(),
                profile.getMajor(),
                profile.getCurrentLevel(),
                profile.getLearningGoal(),
                profile.getPreferences(),
                profile.getConstraintsText(),
                profile.getDialogueSummary(),
                profile.getCreatedAt(),
                profile.getUpdatedAt());
    }
}
