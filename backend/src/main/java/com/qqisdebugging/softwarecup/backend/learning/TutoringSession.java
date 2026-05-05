package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "tutoring_sessions")
public class TutoringSession {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 36)
    private String studentProfileId;

    @Column(nullable = false, length = 36)
    private String courseId;

    @Column(nullable = false, columnDefinition = "text")
    private String question;

    @Column(nullable = false, columnDefinition = "text")
    private String answer;

    @Column(nullable = false, columnDefinition = "text")
    private String citationsJson;

    @Column(nullable = false, columnDefinition = "text")
    private String followUpQuestionsJson;

    @Column(nullable = false, columnDefinition = "text")
    private String learningActionsJson;

    @Column(nullable = false, columnDefinition = "text")
    private String profileSignalsJson;

    @Column(nullable = false, columnDefinition = "text")
    private String mermaidDiagram;

    @Column(nullable = false, length = 80)
    private String provider;

    @Column(nullable = false)
    private Boolean fallbackUsed;

    @Column(nullable = false)
    private Instant createdAt;

    protected TutoringSession() {
    }

    public TutoringSession(
            String studentProfileId,
            String courseId,
            String question,
            String answer,
            String citationsJson,
            String followUpQuestionsJson,
            String learningActionsJson,
            String profileSignalsJson,
            String mermaidDiagram,
            String provider,
            Boolean fallbackUsed) {
        this.studentProfileId = studentProfileId;
        this.courseId = courseId;
        this.question = question;
        this.answer = answer;
        this.citationsJson = citationsJson;
        this.followUpQuestionsJson = followUpQuestionsJson;
        this.learningActionsJson = learningActionsJson;
        this.profileSignalsJson = profileSignalsJson;
        this.mermaidDiagram = mermaidDiagram;
        this.provider = provider;
        this.fallbackUsed = fallbackUsed;
    }

    @jakarta.persistence.PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID().toString();
        }
        createdAt = Instant.now();
    }

    public String getId() {
        return id;
    }

    public String getStudentProfileId() {
        return studentProfileId;
    }

    public String getCourseId() {
        return courseId;
    }

    public String getQuestion() {
        return question;
    }

    public String getAnswer() {
        return answer;
    }

    public String getCitationsJson() {
        return citationsJson;
    }

    public String getFollowUpQuestionsJson() {
        return followUpQuestionsJson;
    }

    public String getLearningActionsJson() {
        return learningActionsJson;
    }

    public String getProfileSignalsJson() {
        return profileSignalsJson;
    }

    public String getMermaidDiagram() {
        return mermaidDiagram;
    }

    public String getProvider() {
        return provider;
    }

    public Boolean getFallbackUsed() {
        return fallbackUsed;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
