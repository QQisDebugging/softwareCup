package com.qqisdebugging.softwarecup.backend.course;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "learning_resources")
public class LearningResource {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 36)
    private String courseId;

    @Column(length = 36)
    private String sourceTaskId;

    @Column(nullable = false, length = 180)
    private String title;

    @Column(nullable = false, length = 60)
    private String resourceType;

    @Column(nullable = false, length = 60)
    private String modality;

    @Column(nullable = false, length = 80)
    private String targetLevel;

    @Column(nullable = false)
    private Integer estimatedMinutes;

    @Column(nullable = false, columnDefinition = "text")
    private String content;

    @Column(nullable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private Instant updatedAt;

    protected LearningResource() {
    }

    public LearningResource(
            String courseId,
            String sourceTaskId,
            String title,
            String resourceType,
            String modality,
            String targetLevel,
            Integer estimatedMinutes,
            String content) {
        this.courseId = courseId;
        this.sourceTaskId = sourceTaskId;
        this.title = title;
        this.resourceType = resourceType;
        this.modality = modality;
        this.targetLevel = targetLevel;
        this.estimatedMinutes = estimatedMinutes;
        this.content = content;
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

    public String getCourseId() {
        return courseId;
    }

    public String getSourceTaskId() {
        return sourceTaskId;
    }

    public String getTitle() {
        return title;
    }

    public String getResourceType() {
        return resourceType;
    }

    public String getModality() {
        return modality;
    }

    public String getTargetLevel() {
        return targetLevel;
    }

    public Integer getEstimatedMinutes() {
        return estimatedMinutes;
    }

    public String getContent() {
        return content;
    }

    public void replaceContent(String content) {
        if (content == null || content.isBlank()) {
            throw new IllegalArgumentException("Resource content cannot be blank");
        }
        this.content = content;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }
}
