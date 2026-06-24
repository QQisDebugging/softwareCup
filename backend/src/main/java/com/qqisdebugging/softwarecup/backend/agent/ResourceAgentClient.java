package com.qqisdebugging.softwarecup.backend.agent;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Duration;
import java.util.Map;
import java.util.function.Supplier;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestClient;

@Component
public class ResourceAgentClient {
    private static final int MAX_ATTEMPTS = 3;
    private static final Duration RETRY_DELAY = Duration.ofMillis(800);

    private final RestClient resourceAgentRestClient;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public ResourceAgentClient(RestClient resourceAgentRestClient) {
        this.resourceAgentRestClient = resourceAgentRestClient;
    }

    public ResourceAgentResponse generate(ResourceAgentRequest request) {
        String body = withAgentRetry("resource generation", () -> resourceAgentRestClient.post()
                .uri("/agents/resource-generation")
                .body(request)
                .retrieve()
                .body(String.class));
        return parseResourceGenerationResponse(request, body);
    }

    private ResourceAgentResponse parseResourceGenerationResponse(ResourceAgentRequest request, String body) {
        String responseBody = body == null ? "" : body.trim();
        if (responseBody.isBlank()) {
            throw new AgentUpstreamException("Resource agent returned an empty response");
        }
        try {
            ResourceAgentResponse response = objectMapper.readValue(responseBody, ResourceAgentResponse.class);
            if (response == null || !hasText(response.content())) {
                throw new AgentUpstreamException("Resource agent returned JSON without resource content");
            }
            if (Boolean.TRUE.equals(response.fallbackUsed())
                    || (response.provider() != null && response.provider().toLowerCase(java.util.Locale.ROOT).contains("fallback"))) {
                throw new AgentUpstreamException("Resource agent returned fallback output");
            }
            return response;
        } catch (JsonProcessingException ex) {
            throw new AgentUpstreamException("Resource agent returned non-JSON response", ex);
        }
    }

    private boolean hasText(String value) {
        return value != null && !value.isBlank();
    }

    public TutoringAgentResponse tutor(TutoringAgentRequest request) {
        return withAgentRetry("tutoring", () -> resourceAgentRestClient.post()
                .uri("/agents/tutoring")
                .body(request)
                .retrieve()
                .body(TutoringAgentResponse.class));
    }

    public AssessmentGenerateAgentResponse generateAssessment(AssessmentGenerateAgentRequest request) {
        return withAgentRetry("assessment generation", () -> resourceAgentRestClient.post()
                .uri("/agents/assessment/generate")
                .body(request)
                .retrieve()
                .body(AssessmentGenerateAgentResponse.class));
    }

    public AssessmentGradeAgentResponse gradeAssessment(AssessmentGradeAgentRequest request) {
        return withAgentRetry("assessment grading", () -> resourceAgentRestClient.post()
                .uri("/agents/assessment/grade")
                .body(request)
                .retrieve()
                .body(AssessmentGradeAgentResponse.class));
    }

    public Map<String, Object> proxy(String agentPath, Map<String, Object> request) {
        return withAgentRetry(agentPath, () -> resourceAgentRestClient.post()
                .uri(agentPath)
                .body(request)
                .retrieve()
                .body(new ParameterizedTypeReference<>() {
                }));
    }

    public Map<String, Object> providerStatus() {
        return withAgentRetry("provider status", () -> resourceAgentRestClient.get()
                .uri("/agents/providers/status")
                .retrieve()
                .body(new ParameterizedTypeReference<>() {
                }));
    }

    public Map<String, Object> providerConfig(Map<String, Object> request) {
        return withAgentRetry("provider config", () -> resourceAgentRestClient.post()
                .uri("/agents/providers/config")
                .body(request)
                .retrieve()
                .body(new ParameterizedTypeReference<>() {
                }));
    }

    private <T> T withAgentRetry(String operation, Supplier<T> call) {
        RestClientException last = null;
        for (int attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
            try {
                return call.get();
            } catch (RestClientException ex) {
                last = ex;
                if (attempt == MAX_ATTEMPTS) {
                    break;
                }
                sleepBeforeRetry();
            }
        }
        String message = last == null ? "unknown error" : last.getMessage();
        throw new AgentUpstreamException(
                "Resource agent API call failed after " + MAX_ATTEMPTS + " attempts for " + operation + ": " + message,
                last);
    }

    private void sleepBeforeRetry() {
        try {
            Thread.sleep(RETRY_DELAY.toMillis());
        } catch (InterruptedException ex) {
            Thread.currentThread().interrupt();
            throw new AgentUpstreamException("Interrupted while retrying resource agent API call", ex);
        }
    }
}
