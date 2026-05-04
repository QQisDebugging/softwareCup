package com.qqisdebugging.softwarecup.backend.common;

import java.time.Instant;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class HealthController {

    @GetMapping("/health")
    Map<String, Object> health() {
        return Map.of(
                "service", "software-cup-learning-backend",
                "status", "UP",
                "timestamp", Instant.now());
    }
}
