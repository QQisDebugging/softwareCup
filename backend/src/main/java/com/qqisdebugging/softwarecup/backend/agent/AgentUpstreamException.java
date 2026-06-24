package com.qqisdebugging.softwarecup.backend.agent;

public class AgentUpstreamException extends RuntimeException {
    public AgentUpstreamException(String message) {
        super(message);
    }

    public AgentUpstreamException(String message, Throwable cause) {
        super(message, cause);
    }
}
