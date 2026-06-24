package com.qqisdebugging.softwarecup.backend.assignment;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

/**
 * 课程作业/测试（老师发布）。type 为 homework（作业，文本作答）或 quiz（测试，选择题自动评分）。
 * quiz 的题目以 JSON 存于 questionsJson。
 */
@Entity
@Table(name = "course_assignments")
public class CourseAssignment {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 36)
    private String courseId;

    @Column(nullable = false, length = 20)
    private String type;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(nullable = false, length = 80)
    private String publisher;

    @Column(nullable = false, columnDefinition = "text")
    private String description;

    @Column(length = 80)
    private String deadlineLabel;

    @Column(nullable = false)
    private Integer estimatedMinutes;

    @Column(nullable = false, columnDefinition = "text")
    private String questionsJson;

    @Column(nullable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private Instant updatedAt;

    protected CourseAssignment() {
    }

    public CourseAssignment(
            String courseId,
            String type,
            String title,
            String publisher,
            String description,
            String deadlineLabel,
            Integer estimatedMinutes,
            String questionsJson) {
        this.courseId = courseId;
        this.type = type;
        this.title = title;
        this.publisher = publisher;
        this.description = description;
        this.deadlineLabel = deadlineLabel;
        this.estimatedMinutes = estimatedMinutes;
        this.questionsJson = questionsJson;
    }

    @PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID().toString();
        }
        Instant now = Instant.now();
        if (createdAt == null) {
            createdAt = now;
        }
        updatedAt = now;
    }

    @PreUpdate
    void preUpdate() {
        updatedAt = Instant.now();
    }

    public String getId() {
        return id;
    }

    public String getCourseId() {
        return courseId;
    }

    public String getType() {
        return type;
    }

    public String getTitle() {
        return title;
    }

    public String getPublisher() {
        return publisher;
    }

    public String getDescription() {
        return description;
    }

    public String getDeadlineLabel() {
        return deadlineLabel;
    }

    public Integer getEstimatedMinutes() {
        return estimatedMinutes;
    }

    public String getQuestionsJson() {
        return questionsJson;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }
}
