package com.qqisdebugging.softwarecup.backend.upload;

import java.time.Instant;

public record UploadAssetResponse(
        String id,
        String originalFilename,
        String contentType,
        Long sizeBytes,
        String storagePath,
        String purpose,
        String courseId,
        String uploaderRole,
        String materialType,
        String parseStatus,
        String parseMessage,
        String extractedTextPreview,
        String knowledgePointsJson,
        String courseDraftJson,
        Instant createdAt) {
    static UploadAssetResponse from(UploadedAsset asset) {
        return new UploadAssetResponse(
                asset.getId(),
                asset.getOriginalFilename(),
                asset.getContentType(),
                asset.getSizeBytes(),
                asset.getStoragePath(),
                asset.getPurpose(),
                asset.getCourseId(),
                asset.getUploaderRole(),
                asset.getMaterialType(),
                asset.getParseStatus(),
                asset.getParseMessage(),
                asset.getExtractedTextPreview(),
                asset.getKnowledgePointsJson(),
                asset.getCourseDraftJson(),
                asset.getCreatedAt());
    }
}
