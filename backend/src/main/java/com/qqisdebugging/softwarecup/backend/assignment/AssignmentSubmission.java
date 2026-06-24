package com.qqisdebugging.softwarecup.backend.assignment;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.time.Instant;
import java.util.UUID;

/**
 * 学生对某作业/测试的提交。homework 存文本 content；quiz 存答案 answersJson 与自动评分 score/total。
 * 每个 (assignmentId, studentProfileId) 只保留一条，重复提交即更新。
 */
@Entity
@Table(
        name = "assignment_submissions",
        uniqueConstraints = @UniqueConstraint(columnNames = {"assignment_id", "student_profile_id"}))
public class AssignmentSubmission {
    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "assignment_id", nullable = false, length = 36)
    private String assignmentId;

    @Column(name = "student_profile_id", nullable = false, length = 36)
    private String studentProfileId;

    @Column(nullable = false, length = 36)
    private String courseId;

    @Column(nullable = false, columnDefinition = "text")
    private String content;

    @Column(nullable = false, columnDefinition = "text")
    private String answersJson;

    private Integer score;

    private Integer total;

    @Column(nullable = false)
    private Instant submittedAt;

    protected AssignmentSubmission() {
    }

    public AssignmentSubmission(
            String assignmentId,
            String studentProfileId,
            String courseId,
            String content,
            String answersJson,
            Integer score,
            Integer total) {
        this.assignmentId = assignmentId;
        this.studentProfileId = studentProfileId;
        this.courseId = courseId;
        this.content = content;
        this.answersJson = answersJson;
        this.score = score;
        this.total = total;
    }

    @PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID().toString();
        }
        if (submittedAt == null) {
            submittedAt = Instant.now();
        }
    }

    @PreUpdate
    void preUpdate() {
        submittedAt = Instant.now();
    }

    public void update(String content, String answersJson, Integer score, Integer total) {
        this.content = content;
        this.answersJson = answersJson;
        this.score = score;
        this.total = total;
    }

    public String getId() {
        return id;
    }

    public String getAssignmentId() {
        return assignmentId;
    }

    public String getStudentProfileId() {
        return studentProfileId;
    }

    public String getCourseId() {
        return courseId;
    }

    public String getContent() {
        return content;
    }

    public String getAnswersJson() {
        return answersJson;
    }

    public Integer getScore() {
        return score;
    }

    public Integer getTotal() {
        return total;
    }

    public Instant getSubmittedAt() {
        return submittedAt;
    }
}
