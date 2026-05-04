package com.qqisdebugging.softwarecup.backend.profile;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "profile_dimensions")
public class ProfileDimension {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 36)
    private String profileId;

    @Column(nullable = false, length = 80)
    private String dimensionKey;

    @Column(nullable = false, length = 120)
    private String dimensionName;

    @Column(nullable = false, columnDefinition = "text")
    private String dimensionValue;

    @Column(nullable = false, columnDefinition = "text")
    private String evidence;

    @Column(nullable = false, precision = 5, scale = 2)
    private BigDecimal confidenceScore;

    @Column(nullable = false, length = 80)
    private String source;

    @Column(nullable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private Instant updatedAt;

    protected ProfileDimension() {
    }

    public ProfileDimension(
            String profileId,
            String dimensionKey,
            String dimensionName,
            String dimensionValue,
            String evidence,
            BigDecimal confidenceScore,
            String source) {
        this.profileId = profileId;
        this.dimensionKey = dimensionKey;
        this.dimensionName = dimensionName;
        this.dimensionValue = dimensionValue;
        this.evidence = evidence;
        this.confidenceScore = confidenceScore;
        this.source = source;
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

    public void update(String value, String evidence, BigDecimal confidenceScore, String source) {
        this.dimensionValue = value;
        this.evidence = evidence;
        this.confidenceScore = confidenceScore;
        this.source = source;
    }

    public String getId() {
        return id;
    }

    public String getProfileId() {
        return profileId;
    }

    public String getDimensionKey() {
        return dimensionKey;
    }

    public String getDimensionName() {
        return dimensionName;
    }

    public String getDimensionValue() {
        return dimensionValue;
    }

    public String getEvidence() {
        return evidence;
    }

    public BigDecimal getConfidenceScore() {
        return confidenceScore;
    }

    public String getSource() {
        return source;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }
}
