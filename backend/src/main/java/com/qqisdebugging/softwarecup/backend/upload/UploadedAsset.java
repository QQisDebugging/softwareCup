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

    @Column(length = 36)
    private String courseId;

    @Column(nullable = false, length = 40)
    private String uploaderRole = "student";

    @Column(nullable = false, length = 80)
    private String materialType = "FILE";

    @Column(nullable = false, length = 40)
    private String parseStatus = "STORED";

    @Column(nullable = false, columnDefinition = "text")
    private String parseMessage = "";

    @Column(nullable = false, columnDefinition = "text")
    private String extractedTextPreview = "";

    @Column(nullable = false, columnDefinition = "text")
    private String knowledgePointsJson = "[]";

    @Column(nullable = false, columnDefinition = "text")
    private String courseDraftJson = "{}";

    @Column(nullable = false)
    private Instant createdAt;

    protected UploadedAsset() {
    }

    public UploadedAsset(String originalFilename, String contentType, Long sizeBytes, String storagePath, String purpose) {
        this(originalFilename, contentType, sizeBytes, storagePath, purpose, null, "student", "FILE", "STORED", "", "", "[]", "{}");
    }

    public UploadedAsset(
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
            String courseDraftJson) {
        this.originalFilename = originalFilename;
        this.contentType = contentType;
        this.sizeBytes = sizeBytes;
        this.storagePath = storagePath;
        this.purpose = purpose;
        this.courseId = blankToNull(courseId);
        this.uploaderRole = valueOrDefault(uploaderRole, "student");
        this.materialType = valueOrDefault(materialType, "FILE");
        this.parseStatus = valueOrDefault(parseStatus, "STORED");
        this.parseMessage = valueOrDefault(parseMessage, "");
        this.extractedTextPreview = valueOrDefault(extractedTextPreview, "");
        this.knowledgePointsJson = valueOrDefault(knowledgePointsJson, "[]");
        this.courseDraftJson = valueOrDefault(courseDraftJson, "{}");
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

    public String getCourseId() {
        return courseId;
    }

    public String getUploaderRole() {
        return uploaderRole;
    }

    public String getMaterialType() {
        return materialType;
    }

    public String getParseStatus() {
        return parseStatus;
    }

    public String getParseMessage() {
        return parseMessage;
    }

    public String getExtractedTextPreview() {
        return extractedTextPreview;
    }

    public String getKnowledgePointsJson() {
        return knowledgePointsJson;
    }

    public String getCourseDraftJson() {
        return courseDraftJson;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void replaceAnalysis(
            String materialType,
            String parseStatus,
            String parseMessage,
            String extractedTextPreview,
            String knowledgePointsJson,
            String courseDraftJson) {
        this.materialType = valueOrDefault(materialType, this.materialType);
        this.parseStatus = valueOrDefault(parseStatus, this.parseStatus);
        this.parseMessage = valueOrDefault(parseMessage, "");
        this.extractedTextPreview = valueOrDefault(extractedTextPreview, "");
        this.knowledgePointsJson = valueOrDefault(knowledgePointsJson, "[]");
        this.courseDraftJson = valueOrDefault(courseDraftJson, "{}");
    }

    public void attachToCourse(String courseId) {
        this.courseId = blankToNull(courseId);
    }

    private String valueOrDefault(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }

    private String blankToNull(String value) {
        return value == null || value.isBlank() ? null : value;
    }
}
