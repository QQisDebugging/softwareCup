package com.qqisdebugging.softwarecup.backend.upload;

import jakarta.validation.constraints.NotBlank;
import java.util.List;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@Validated
@RestController
@RequestMapping("/api/uploads")
public class UploadController {
    private final UploadService uploadService;

    public UploadController(UploadService uploadService) {
        this.uploadService = uploadService;
    }

    @PostMapping
    UploadAssetResponse upload(@RequestParam("file") MultipartFile file, @RequestParam @NotBlank String purpose) {
        return uploadService.store(file, purpose);
    }

    @GetMapping
    List<UploadAssetResponse> listUploads() {
        return uploadService.listUploads();
    }
}
