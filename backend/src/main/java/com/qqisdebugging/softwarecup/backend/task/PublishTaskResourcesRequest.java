package com.qqisdebugging.softwarecup.backend.task;

import jakarta.validation.constraints.Size;

public record PublishTaskResourcesRequest(
        @Size(max = 80)
        String publisherName,

        @Size(max = 2000)
        String publishNote) {
}
