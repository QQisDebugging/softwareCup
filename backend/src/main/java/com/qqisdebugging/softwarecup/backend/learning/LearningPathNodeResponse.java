package com.qqisdebugging.softwarecup.backend.learning;

public record LearningPathNodeResponse(
        String id,
        Integer nodeOrder,
        String knowledgePoint,
        String resourceId,
        Integer estimatedMinutes,
        String prerequisiteNodeId,
        String status) {
    public static LearningPathNodeResponse from(LearningPathNode node) {
        return new LearningPathNodeResponse(
                node.getId(),
                node.getNodeOrder(),
                node.getKnowledgePoint(),
                node.getResourceId(),
                node.getEstimatedMinutes(),
                node.getPrerequisiteNodeId(),
                node.getStatus());
    }
}
