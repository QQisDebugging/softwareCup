package com.qqisdebugging.softwarecup.backend.agent;

public record AgentDefinitionResponse(
        String id,
        String agentKey,
        String displayName,
        String responsibility,
        String inputContract,
        String outputContract,
        Integer sortOrder) {
    public static AgentDefinitionResponse from(AgentDefinition definition) {
        return new AgentDefinitionResponse(
                definition.getId(),
                definition.getAgentKey(),
                definition.getDisplayName(),
                definition.getResponsibility(),
                definition.getInputContract(),
                definition.getOutputContract(),
                definition.getSortOrder());
    }
}
