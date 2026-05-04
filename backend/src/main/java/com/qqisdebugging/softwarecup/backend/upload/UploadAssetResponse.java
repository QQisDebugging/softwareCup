package com.qqisdebugging.softwarecup.backend.upload;

import java.time.Instant;

public record UploadAssetResponse(
        String id,
        String originalFilename,
        String contentType,
        Long sizeBytes,
        String storagePath,
        String purpose,
        Instant createdAt) {
    static UploadAssetResponse from(UploadedAsset asset) {
        return new UploadAssetResponse(
                asset.getId(),
                asset.getOriginalFilename(),
                asset.getContentType(),
                asset.getSizeBytes(),
                asset.getStoragePath(),
                asset.getPurpose(),
                asset.getCreatedAt());
    }
}
