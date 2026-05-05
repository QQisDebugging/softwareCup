package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "quiz_attempts")
public class QuizAttempt {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 36)
    private String studentProfileId;

    @Column(nullable = false, length = 36)
    private String courseId;

    @Column(length = 36)
    private String resourceId;

    @Column(nullable = false, length = 180)
    private String topic = "general-assessment";

    @Column(nullable = false)
    private BigDecimal score;

    @Column(nullable = false)
    private BigDecimal maxScore;

    @Column(nullable = false)
    private Integer correctCount;

    @Column(nullable = false)
    private Integer totalCount;

    @Column(columnDefinition = "text")
    private String weakPoints;

    @Column(nullable = false, length = 80)
    private String masteryLevel = "ungraded";

    @Column(nullable = false, columnDefinition = "text")
    private String questionsJson = "[]";

    @Column(nullable = false, columnDefinition = "text")
    private String answersJson = "[]";

    @Column(nullable = false, columnDefinition = "text")
    private String gradingJson = "{}";

    @Column(nullable = false)
    private Instant submittedAt;

    @Column(nullable = false)
    private Instant createdAt;

    protected QuizAttempt() {
    }

    public QuizAttempt(
            String studentProfileId,
            String courseId,
            String resourceId,
            BigDecimal score,
            BigDecimal maxScore,
            Integer correctCount,
            Integer totalCount,
            String weakPoints) {
        this.studentProfileId = studentProfileId;
        this.courseId = courseId;
        this.resourceId = resourceId;
        this.score = score;
        this.maxScore = maxScore;
        this.correctCount = correctCount;
        this.totalCount = totalCount;
        this.weakPoints = weakPoints;
        this.topic = valueOrDefault(weakPoints, "general-assessment");
        this.masteryLevel = "manual-submission";
    }

    public QuizAttempt(
            String studentProfileId,
            String courseId,
            String topic,
            Integer score,
            Integer maxScore,
            String masteryLevel,
            String questionsJson,
            String answersJson,
            String gradingJson) {
        this.studentProfileId = studentProfileId;
        this.courseId = courseId;
        this.topic = valueOrDefault(topic, "agent-assessment");
        this.score = BigDecimal.valueOf(score == null ? 0 : score);
        this.maxScore = BigDecimal.valueOf(maxScore == null || maxScore == 0 ? 1 : maxScore);
        this.correctCount = score == null ? 0 : score;
        this.totalCount = maxScore == null || maxScore == 0 ? 1 : maxScore;
        this.masteryLevel = valueOrDefault(masteryLevel, "ungraded");
        this.questionsJson = valueOrDefault(questionsJson, "[]");
        this.answersJson = valueOrDefault(answersJson, "[]");
        this.gradingJson = valueOrDefault(gradingJson, "{}");
        this.weakPoints = this.masteryLevel;
    }

    @PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID().toString();
        }
        Instant now = Instant.now();
        if (submittedAt == null) {
            submittedAt = now;
        }
        if (createdAt == null) {
            createdAt = submittedAt;
        }
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

    public String getTopic() {
        return topic;
    }

    public BigDecimal getScore() {
        return score;
    }

    public BigDecimal getMaxScore() {
        return maxScore;
    }

    public Integer getCorrectCount() {
        return correctCount;
    }

    public Integer getTotalCount() {
        return totalCount;
    }

    public String getWeakPoints() {
        return weakPoints;
    }

    public String getMasteryLevel() {
        return masteryLevel;
    }

    public String getQuestionsJson() {
        return questionsJson;
    }

    public String getAnswersJson() {
        return answersJson;
    }

    public String getGradingJson() {
        return gradingJson;
    }

    public Instant getSubmittedAt() {
        return submittedAt;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    private String valueOrDefault(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }
}
