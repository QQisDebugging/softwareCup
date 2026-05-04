package com.qqisdebugging.softwarecup.backend.profile;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "student_profiles")
public class StudentProfile {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 80)
    private String studentName;

    @Column(nullable = false, length = 120)
    private String major;

    @Column(nullable = false, length = 80)
    private String currentLevel;

    @Column(nullable = false, columnDefinition = "text")
    private String learningGoal;

    @Column(nullable = false, columnDefinition = "text")
    private String preferences;

    @Column(nullable = false, name = "constraints_text", columnDefinition = "text")
    private String constraintsText;

    @Column(nullable = false, columnDefinition = "text")
    private String dialogueSummary;

    @Column(nullable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private Instant updatedAt;

    protected StudentProfile() {
    }

    public StudentProfile(
            String studentName,
            String major,
            String currentLevel,
            String learningGoal,
            String preferences,
            String constraintsText,
            String dialogueSummary) {
        this.studentName = studentName;
        this.major = major;
        this.currentLevel = currentLevel;
        this.learningGoal = learningGoal;
        this.preferences = preferences;
        this.constraintsText = constraintsText;
        this.dialogueSummary = dialogueSummary;
    }

    @jakarta.persistence.PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID().toString();
        }
        Instant now = Instant.now();
        createdAt = now;
        updatedAt = now;
    }

    @jakarta.persistence.PreUpdate
    void preUpdate() {
        updatedAt = Instant.now();
    }

    public String getId() {
        return id;
    }

    public String getStudentName() {
        return studentName;
    }

    public String getMajor() {
        return major;
    }

    public String getCurrentLevel() {
        return currentLevel;
    }

    public String getLearningGoal() {
        return learningGoal;
    }

    public String getPreferences() {
        return preferences;
    }

    public String getConstraintsText() {
        return constraintsText;
    }

    public String getDialogueSummary() {
        return dialogueSummary;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }
}
