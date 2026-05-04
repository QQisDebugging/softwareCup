package com.qqisdebugging.softwarecup.backend.profile;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "profile_history")
public class ProfileHistory {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 36)
    private String profileId;

    @Column(nullable = false, length = 80)
    private String eventType;

    @Column(nullable = false, length = 80)
    private String dimensionKey;

    @Column(columnDefinition = "text")
    private String previousValue;

    @Column(nullable = false, columnDefinition = "text")
    private String newValue;

    @Column(nullable = false, columnDefinition = "text")
    private String evidence;

    @Column(nullable = false, length = 80)
    private String source;

    @Column(nullable = false)
    private Instant createdAt;

    protected ProfileHistory() {
    }

    public ProfileHistory(
            String profileId,
            String eventType,
            String dimensionKey,
            String previousValue,
            String newValue,
            String evidence,
            String source) {
        this.profileId = profileId;
        this.eventType = eventType;
        this.dimensionKey = dimensionKey;
        this.previousValue = previousValue;
        this.newValue = newValue;
        this.evidence = evidence;
        this.source = source;
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

    public String getProfileId() {
        return profileId;
    }

    public String getEventType() {
        return eventType;
    }

    public String getDimensionKey() {
        return dimensionKey;
    }

    public String getPreviousValue() {
        return previousValue;
    }

    public String getNewValue() {
        return newValue;
    }

    public String getEvidence() {
        return evidence;
    }

    public String getSource() {
        return source;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
