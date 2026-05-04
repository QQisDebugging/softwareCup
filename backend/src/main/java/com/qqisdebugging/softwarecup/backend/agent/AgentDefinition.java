package com.qqisdebugging.softwarecup.backend.agent;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;

@Entity
@Table(name = "agent_definitions")
public class AgentDefinition {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 80)
    private String agentKey;

    @Column(nullable = false, length = 120)
    private String displayName;

    @Column(nullable = false, columnDefinition = "text")
    private String responsibility;

    @Column(nullable = false, columnDefinition = "text")
    private String inputContract;

    @Column(nullable = false, columnDefinition = "text")
    private String outputContract;

    @Column(nullable = false)
    private Boolean enabled;

    @Column(nullable = false)
    private Integer sortOrder;

    @Column(nullable = false)
    private Instant createdAt;

    protected AgentDefinition() {
    }

    public String getId() {
        return id;
    }

    public String getAgentKey() {
        return agentKey;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getResponsibility() {
        return responsibility;
    }

    public String getInputContract() {
        return inputContract;
    }

    public String getOutputContract() {
        return outputContract;
    }

    public Boolean getEnabled() {
        return enabled;
    }

    public Integer getSortOrder() {
        return sortOrder;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
