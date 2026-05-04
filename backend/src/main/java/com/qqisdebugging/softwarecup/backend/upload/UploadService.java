package com.qqisdebugging.softwarecup.backend.upload;

import com.qqisdebugging.softwarecup.backend.config.StorageProperties;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDate;
import java.util.Comparator;
import java.util.List;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

@Service
public class UploadService {
    private final UploadedAssetRepository repository;
    private final Path storageRoot;

    public UploadService(UploadedAssetRepository repository, StorageProperties storageProperties) {
        this.repository = repository;
        this.storageRoot = storageProperties.getRoot().toAbsolutePath().normalize();
    }

    @Transactional
    public UploadAssetResponse store(MultipartFile file, String purpose) {
        if (file.isEmpty()) {
            throw new IllegalArgumentException("Uploaded file is empty");
        }
        try {
            String safeName = sanitize(file.getOriginalFilename());
            String storedName = UUID.randomUUID() + "-" + safeName;
            Path dateDir = storageRoot.resolve(LocalDate.now().toString()).normalize();
            Files.createDirectories(dateDir);
            Path target = dateDir.resolve(storedName).normalize();
            if (!target.startsWith(storageRoot)) {
                throw new IllegalArgumentException("Invalid storage path");
            }
            file.transferTo(target);
            UploadedAsset saved = repository.save(new UploadedAsset(
                    safeName,
                    file.getContentType() == null ? "application/octet-stream" : file.getContentType(),
                    file.getSize(),
                    storageRoot.relativize(target).toString(),
                    purpose));
            return UploadAssetResponse.from(saved);
        } catch (IOException ex) {
            throw new IllegalStateException("Failed to store uploaded file: " + ex.getMessage(), ex);
        }
    }

    @Transactional(readOnly = true)
    public List<UploadAssetResponse> listUploads() {
        return repository.findAll().stream()
                .sorted(Comparator.comparing(UploadedAsset::getCreatedAt).reversed())
                .map(UploadAssetResponse::from)
                .toList();
    }

    private String sanitize(String filename) {
        String value = filename == null || filename.isBlank() ? "upload.bin" : filename;
        return value.replaceAll("[\\\\/:*?\"<>|]", "_");
    }
}
