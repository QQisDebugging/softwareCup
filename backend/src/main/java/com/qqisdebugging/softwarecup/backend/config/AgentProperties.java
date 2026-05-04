package com.qqisdebugging.softwarecup.backend.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "softwarecup.agent")
public class AgentProperties {
    private String resourceBaseUrl = "http://localhost:9001";
    private int connectTimeoutMs = 3000;
    private int readTimeoutMs = 30000;

    public String getResourceBaseUrl() {
        return resourceBaseUrl;
    }

    public void setResourceBaseUrl(String resourceBaseUrl) {
        this.resourceBaseUrl = resourceBaseUrl;
    }

    public int getConnectTimeoutMs() {
        return connectTimeoutMs;
    }

    public void setConnectTimeoutMs(int connectTimeoutMs) {
        this.connectTimeoutMs = connectTimeoutMs;
    }

    public int getReadTimeoutMs() {
        return readTimeoutMs;
    }

    public void setReadTimeoutMs(int readTimeoutMs) {
        this.readTimeoutMs = readTimeoutMs;
    }
}
