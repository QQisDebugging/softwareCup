package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "resource_recommendations")
public class ResourceRecommendation {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 36)
    private String studentProfileId;

    @Column(nullable = false, length = 36)
    private String courseId;

    @Column(nullable = false, length = 36)
    private String resourceId;

    @Column(nullable = false, columnDefinition = "text")
    private String reason;

    @Column(nullable = false)
    private BigDecimal priorityScore;

    @Column(nullable = false, length = 40)
    private String status;

    @Column(nullable = false)
    private Instant createdAt;

    protected ResourceRecommendation() {
    }

    public ResourceRecommendation(
            String studentProfileId,
            String courseId,
            String resourceId,
            String reason,
            BigDecimal priorityScore) {
        this.studentProfileId = studentProfileId;
        this.courseId = courseId;
        this.resourceId = resourceId;
        this.reason = reason;
        this.priorityScore = priorityScore;
        this.status = "PUSHED";
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

    public String getReason() {
        return reason;
    }

    public BigDecimal getPriorityScore() {
        return priorityScore;
    }

    public String getStatus() {
        return status;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
