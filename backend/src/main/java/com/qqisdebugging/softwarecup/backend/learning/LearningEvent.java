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

    @Column(length = 36)
    private String courseId;

    @Column(nullable = false, length = 80)
    private String eventType;

    @Column(length = 180)
    private String topic;

    @Column(nullable = false, columnDefinition = "text")
    private String payloadJson;

    @Column(nullable = false)
    private Instant createdAt;

    protected LearningEvent() {
    }

    public LearningEvent(
            String studentProfileId,
            String courseId,
            String eventType,
            String topic,
            String payloadJson) {
        this.studentProfileId = studentProfileId;
        this.courseId = courseId;
        this.eventType = eventType;
        this.topic = topic;
        this.payloadJson = payloadJson;
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

    public String getEventType() {
        return eventType;
    }

    public String getTopic() {
        return topic;
    }

    public String getPayloadJson() {
        return payloadJson;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
