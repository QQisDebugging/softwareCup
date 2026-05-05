package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "learning_events")
public class LearningEvent {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 36)
    private String studentProfileId;

    @Column(nullable = false, length = 36)
    private String courseId;

    @Column(length = 36)
    private String resourceId;

    @Column(nullable = false, length = 80)
    private String eventType;

    private Integer durationSeconds;

    private Integer feedbackScore;

    @Column(columnDefinition = "text")
    private String eventPayload;

    @Column(nullable = false)
    private Instant createdAt;

    protected LearningEvent() {
    }

    public LearningEvent(
            String studentProfileId,
            String courseId,
            String resourceId,
            String eventType,
            Integer durationSeconds,
            Integer feedbackScore,
            String eventPayload) {
        this.studentProfileId = studentProfileId;
        this.courseId = courseId;
        this.resourceId = resourceId;
        this.eventType = eventType;
        this.durationSeconds = durationSeconds;
        this.feedbackScore = feedbackScore;
        this.eventPayload = eventPayload;
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

    public String getResourceId() {
        return resourceId;
    }

    public String getEventType() {
        return eventType;
    }

    public Integer getDurationSeconds() {
        return durationSeconds;
    }

    public Integer getFeedbackScore() {
        return feedbackScore;
    }

    public String getEventPayload() {
        return eventPayload;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
