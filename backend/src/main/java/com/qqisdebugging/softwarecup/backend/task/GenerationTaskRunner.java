package com.qqisdebugging.softwarecup.backend.task;

import com.qqisdebugging.softwarecup.backend.agent.ResourceAgentClient;
import com.qqisdebugging.softwarecup.backend.agent.ResourceAgentRequest;
import com.qqisdebugging.softwarecup.backend.agent.ResourceAgentResponse;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

@Component
public class GenerationTaskRunner {
    private final GenerationTaskTransactions transactions;
    private final ResourceAgentClient resourceAgentClient;

    public GenerationTaskRunner(GenerationTaskTransactions transactions, ResourceAgentClient resourceAgentClient) {
        this.transactions = transactions;
        this.resourceAgentClient = resourceAgentClient;
    }

    @Async
    public void runResourceGeneration(String taskId, String resourceType, String modality) {
        try {
            GenerationTaskTransactions.ResourceGenerationContext context = transactions.markRunningAndLoadContext(taskId);
            ResourceAgentResponse agentResponse = resourceAgentClient.generate(new ResourceAgentRequest(
                    taskId,
                    context.profile().getId(),
                    context.course().getId(),
                    context.profile().getDialogueSummary(),
                    context.course().getTitle(),
                    context.task().getTopic(),
                    resourceType,
                    modality,
                    context.task().getPrompt()));
            transactions.saveGeneratedResource(taskId, context.course().getId(), resourceType, modality, agentResponse);
        } catch (Exception ex) {
            transactions.markFailed(taskId, ex.getMessage() == null ? ex.getClass().getSimpleName() : ex.getMessage());
        }
    }
}
