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

    @Column(nullable = false, length = 40)
    private String reviewStatus;

    private Instant publishedAt;

    @Column(length = 80)
    private String publishedBy;

    @Column(columnDefinition = "text")
    private String publishNote;

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
        this.reviewStatus = "REVIEWING";
    }

    @jakarta.persistence.PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID().toString();
        }
        if (reviewStatus == null || reviewStatus.isBlank()) {
            reviewStatus = "REVIEWING";
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

    public void markReadyForPublish() {
        if (!"PUBLISHED".equals(reviewStatus)) {
            reviewStatus = "READY_TO_PUBLISH";
        }
    }

    public void markReviewRequired() {
        if (!"PUBLISHED".equals(reviewStatus)) {
            reviewStatus = "REVIEW_REQUIRED";
        }
    }

    public void publish(String publisherName, String note) {
        if (!"READY_TO_PUBLISH".equals(reviewStatus) && !"APPROVED".equals(reviewStatus)) {
            throw new IllegalStateException("Resource is not ready to publish: " + reviewStatus);
        }
        reviewStatus = "PUBLISHED";
        publishedAt = Instant.now();
        publishedBy = publisherName == null || publisherName.isBlank() ? "课程教师" : publisherName.trim();
        publishNote = note == null || note.isBlank() ? "教师已确认审核证据并发布给学生。" : note.trim();
    }

    public void applyReviewDecision(String decision, String reviewer, String note) {
        reviewStatus = decision;
        publishedBy = reviewer == null || reviewer.isBlank() ? null : reviewer.trim();
        publishNote = note == null || note.isBlank() ? null : note.trim();
        if ("APPROVED".equals(decision)) {
            publishedAt = Instant.now();
        } else {
            publishedAt = null;
        }
    }

    public String getReviewStatus() {
        return reviewStatus;
    }

    public Instant getPublishedAt() {
        return publishedAt;
    }

    public String getPublishedBy() {
        return publishedBy;
    }

    public String getPublishNote() {
        return publishNote;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }
}
