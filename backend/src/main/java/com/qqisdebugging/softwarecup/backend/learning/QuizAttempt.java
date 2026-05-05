package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
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

    @Column(nullable = false)
    private Instant submittedAt;

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
    }

    @jakarta.persistence.PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID().toString();
        }
        submittedAt = Instant.now();
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

    public Instant getSubmittedAt() {
        return submittedAt;
    }
}
