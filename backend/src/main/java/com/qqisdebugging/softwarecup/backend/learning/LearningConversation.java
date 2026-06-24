package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "learning_conversations")
public class LearningConversation {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 36)
    private String studentProfileId;

    @Column(nullable = false, length = 36)
    private String courseId;

    @Column(nullable = false, length = 180)
    private String title;

    @Column(nullable = false)
    private Boolean archived = false;

    private Instant archivedAt;

    @Column(length = 500)
    private String lastMessagePreview;

    private Instant lastMessageAt;

    @Column(nullable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private Instant updatedAt;

    protected LearningConversation() {
    }

    public LearningConversation(String studentProfileId, String courseId, String title) {
        this.studentProfileId = studentProfileId;
        this.courseId = courseId;
        this.title = title;
        this.archived = false;
    }

    @PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID().toString();
        }
        Instant now = Instant.now();
        createdAt = now;
        updatedAt = now;
    }

    @PreUpdate
    void preUpdate() {
        updatedAt = Instant.now();
    }

    public void updateTitle(String title) {
        this.title = title;
    }

    public void setArchived(boolean archived) {
        this.archived = archived;
        this.archivedAt = archived ? Instant.now() : null;
    }

    public void markMessage(String content, Instant messageAt) {
        this.lastMessagePreview = preview(content);
        this.lastMessageAt = messageAt;
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

    public String getTitle() {
        return title;
    }

    public Boolean getArchived() {
        return archived;
    }

    public Instant getArchivedAt() {
        return archivedAt;
    }

    public String getLastMessagePreview() {
        return lastMessagePreview;
    }

    public Instant getLastMessageAt() {
        return lastMessageAt;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }

    private String preview(String content) {
        if (content == null) {
            return null;
        }
        String normalized = content.replace('\n', ' ').trim();
        return normalized.length() <= 500 ? normalized : normalized.substring(0, 500);
    }
}
