package com.qqisdebugging.softwarecup.backend.upload;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "uploaded_assets")
public class UploadedAsset {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false)
    private String originalFilename;

    @Column(nullable = false, length = 120)
    private String contentType;

    @Column(nullable = false)
    private Long sizeBytes;

    @Column(nullable = false, columnDefinition = "text")
    private String storagePath;

    @Column(nullable = false, length = 120)
    private String purpose;

    @Column(nullable = false)
    private Instant createdAt;

    protected UploadedAsset() {
    }

    public UploadedAsset(String originalFilename, String contentType, Long sizeBytes, String storagePath, String purpose) {
        this.originalFilename = originalFilename;
        this.contentType = contentType;
        this.sizeBytes = sizeBytes;
        this.storagePath = storagePath;
        this.purpose = purpose;
    }

    @jakarta.persistence.PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID().toString();
        }
        createdAt = Instant.now();
    }

    public String getId() {
        return id;
    }

    public String getOriginalFilename() {
        return originalFilename;
    }

    public String getContentType() {
        return contentType;
    }

    public Long getSizeBytes() {
        return sizeBytes;
    }

    public String getStoragePath() {
        return storagePath;
    }

    public String getPurpose() {
        return purpose;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
