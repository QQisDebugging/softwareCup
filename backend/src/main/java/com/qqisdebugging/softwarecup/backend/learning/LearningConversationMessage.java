package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "learning_conversation_messages")
public class LearningConversationMessage {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 36)
    private String conversationId;

    @Column(nullable = false, length = 20)
    private String role;

    @Column(nullable = false, columnDefinition = "text")
    private String content;

    @Column(nullable = false, columnDefinition = "text")
    private String citationsJson;

    @Column(nullable = false, columnDefinition = "text")
    private String followUpQuestionsJson;

    @Column(nullable = false, columnDefinition = "text")
    private String learningActionsJson;

    @Column(nullable = false, columnDefinition = "text")
    private String profileSignalsJson;

    @Column(nullable = false, columnDefinition = "text")
    private String mermaidDiagram;

    @Column(length = 80)
    private String provider;

    private Boolean fallbackUsed;

    @Column(nullable = false)
    private Instant createdAt;

    protected LearningConversationMessage() {
    }

    public LearningConversationMessage(
            String conversationId,
            String role,
            String content,
            String citationsJson,
            String followUpQuestionsJson,
            String learningActionsJson,
            String profileSignalsJson,
            String mermaidDiagram,
            String provider,
            Boolean fallbackUsed) {
        this.conversationId = conversationId;
        this.role = role;
        this.content = content;
        this.citationsJson = citationsJson;
        this.followUpQuestionsJson = followUpQuestionsJson;
        this.learningActionsJson = learningActionsJson;
        this.profileSignalsJson = profileSignalsJson;
        this.mermaidDiagram = mermaidDiagram;
        this.provider = provider;
        this.fallbackUsed = fallbackUsed;
    }

    public static LearningConversationMessage user(String conversationId, String content) {
        return new LearningConversationMessage(
                conversationId, "user", content, "[]", "[]", "[]", "[]", "", null, null);
    }

    @PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID().toString();
        }
        createdAt = Instant.now();
    }

    public String getId() {
        return id;
    }

    public String getConversationId() {
        return conversationId;
    }

    public String getRole() {
        return role;
    }

    public String getContent() {
        return content;
    }

    public String getCitationsJson() {
        return citationsJson;
    }

    public String getFollowUpQuestionsJson() {
        return followUpQuestionsJson;
    }

    public String getLearningActionsJson() {
        return learningActionsJson;
    }

    public String getProfileSignalsJson() {
        return profileSignalsJson;
    }

    public String getMermaidDiagram() {
        return mermaidDiagram;
    }

    public String getProvider() {
        return provider;
    }

    public Boolean getFallbackUsed() {
        return fallbackUsed;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
