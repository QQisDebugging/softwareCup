package com.qqisdebugging.softwarecup.backend.agent;

import java.util.Map;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
public class ResourceAgentClient {
    private final RestClient resourceAgentRestClient;

    public ResourceAgentClient(RestClient resourceAgentRestClient) {
        this.resourceAgentRestClient = resourceAgentRestClient;
    }

    public ResourceAgentResponse generate(ResourceAgentRequest request) {
        return resourceAgentRestClient.post()
                .uri("/agents/resource-generation")
                .body(request)
                .retrieve()
                .body(ResourceAgentResponse.class);
    }

    public TutoringAgentResponse tutor(TutoringAgentRequest request) {
        return resourceAgentRestClient.post()
                .uri("/agents/tutoring")
                .body(request)
                .retrieve()
                .body(TutoringAgentResponse.class);
    }

    public AssessmentGenerateAgentResponse generateAssessment(AssessmentGenerateAgentRequest request) {
        return resourceAgentRestClient.post()
                .uri("/agents/assessment/generate")
                .body(request)
                .retrieve()
                .body(AssessmentGenerateAgentResponse.class);
    }

    public AssessmentGradeAgentResponse gradeAssessment(AssessmentGradeAgentRequest request) {
        return resourceAgentRestClient.post()
                .uri("/agents/assessment/grade")
                .body(request)
                .retrieve()
                .body(AssessmentGradeAgentResponse.class);
    }

    public Map<String, Object> proxy(String agentPath, Map<String, Object> request) {
        return resourceAgentRestClient.post()
                .uri(agentPath)
                .body(request)
                .retrieve()
                .body(new ParameterizedTypeReference<>() {
                });
    }
}
