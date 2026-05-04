package com.qqisdebugging.softwarecup.backend.course;

public record ResourceTypeResponse(
        String code,
        String displayName) {
    public static ResourceTypeResponse from(ResourceType type) {
        return new ResourceTypeResponse(type.name(), type.displayName());
    }
}
