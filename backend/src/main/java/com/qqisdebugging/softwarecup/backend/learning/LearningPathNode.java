package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "learning_path_nodes")
public class LearningPathNode {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 36)
    private String pathId;

    @Column(nullable = false)
    private Integer nodeOrder;

    @Column(nullable = false, length = 180)
    private String knowledgePoint;

    @Column(length = 36)
    private String resourceId;

    @Column(nullable = false)
    private Integer estimatedMinutes;

    @Column(length = 36)
    private String prerequisiteNodeId;

    @Column(nullable = false, length = 40)
    private String status;

    @Column(nullable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private Instant updatedAt;

    protected LearningPathNode() {
    }

    public LearningPathNode(
            String pathId,
            Integer nodeOrder,
            String knowledgePoint,
            String resourceId,
            Integer estimatedMinutes,
            String prerequisiteNodeId,
            String status) {
        this.pathId = pathId;
        this.nodeOrder = nodeOrder;
        this.knowledgePoint = knowledgePoint;
        this.resourceId = resourceId;
        this.estimatedMinutes = estimatedMinutes;
        this.prerequisiteNodeId = prerequisiteNodeId;
        this.status = status;
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

    public void attachResource(String resourceId) {
        this.resourceId = resourceId;
    }

    public String getId() {
        return id;
    }

    public String getPathId() {
        return pathId;
    }

    public Integer getNodeOrder() {
        return nodeOrder;
    }

    public String getKnowledgePoint() {
        return knowledgePoint;
    }

    public String getResourceId() {
        return resourceId;
    }

    public Integer getEstimatedMinutes() {
        return estimatedMinutes;
    }

    public String getPrerequisiteNodeId() {
        return prerequisiteNodeId;
    }

    public String getStatus() {
        return status;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }
}
