package com.qqisdebugging.softwarecup.backend.agent;

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
}
