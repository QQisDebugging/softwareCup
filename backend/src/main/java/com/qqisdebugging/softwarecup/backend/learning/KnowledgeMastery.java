package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "knowledge_mastery")
public class KnowledgeMastery {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 36)
    private String studentProfileId;

    @Column(nullable = false, length = 36)
    private String courseId;

    @Column(nullable = false, length = 180)
    private String knowledgePoint;

    @Column(nullable = false)
    private BigDecimal masteryScore;

    @Column(nullable = false, columnDefinition = "text")
    private String evidenceSummary;

    @Column(nullable = false)
    private Instant updatedAt;

    protected KnowledgeMastery() {
    }

    public KnowledgeMastery(
            String studentProfileId,
            String courseId,
            String knowledgePoint,
            BigDecimal masteryScore,
            String evidenceSummary) {
        this.studentProfileId = studentProfileId;
        this.courseId = courseId;
        this.knowledgePoint = knowledgePoint;
        this.masteryScore = masteryScore;
        this.evidenceSummary = evidenceSummary;
    }

    @jakarta.persistence.PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID().toString();
        }
        updatedAt = Instant.now();
    }

    @jakarta.persistence.PreUpdate
    void preUpdate() {
        updatedAt = Instant.now();
    }

    public void update(BigDecimal masteryScore, String evidenceSummary) {
        this.masteryScore = masteryScore;
        this.evidenceSummary = evidenceSummary;
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

    public String getKnowledgePoint() {
        return knowledgePoint;
    }

    public BigDecimal getMasteryScore() {
        return masteryScore;
    }

    public String getEvidenceSummary() {
        return evidenceSummary;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }
}
