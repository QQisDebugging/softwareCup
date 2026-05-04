package com.qqisdebugging.softwarecup.backend.config;

import java.nio.file.Path;
import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "softwarecup.storage")
public class StorageProperties {
    private Path root = Path.of("uploads");

    public Path getRoot() {
        return root;
    }

    public void setRoot(Path root) {
        this.root = root;
    }
}
