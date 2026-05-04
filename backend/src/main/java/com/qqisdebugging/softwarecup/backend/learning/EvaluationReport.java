package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "evaluation_reports")
public class EvaluationReport {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 36)
    private String studentProfileId;

    @Column(nullable = false, length = 36)
    private String courseId;

    @Column(nullable = false, columnDefinition = "text")
    private String reportSummary;

    @Column(nullable = false)
    private BigDecimal overallScore;

    @Column(nullable = false, columnDefinition = "text")
    private String strengths;

    @Column(nullable = false, columnDefinition = "text")
    private String weaknesses;

    @Column(nullable = false, columnDefinition = "text")
    private String recommendationStrategy;

    @Column(nullable = false)
    private Instant createdAt;

    protected EvaluationReport() {
    }

    public EvaluationReport(
            String studentProfileId,
            String courseId,
            String reportSummary,
            BigDecimal overallScore,
            String strengths,
            String weaknesses,
            String recommendationStrategy) {
        this.studentProfileId = studentProfileId;
        this.courseId = courseId;
        this.reportSummary = reportSummary;
        this.overallScore = overallScore;
        this.strengths = strengths;
        this.weaknesses = weaknesses;
        this.recommendationStrategy = recommendationStrategy;
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

    public String getReportSummary() {
        return reportSummary;
    }

    public BigDecimal getOverallScore() {
        return overallScore;
    }

    public String getStrengths() {
        return strengths;
    }

    public String getWeaknesses() {
        return weaknesses;
    }

    public String getRecommendationStrategy() {
        return recommendationStrategy;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
