package com.qqisdebugging.softwarecup.backend.upload;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UploadedAssetRepository extends JpaRepository<UploadedAsset, String> {
    List<UploadedAsset> findByCourseIdOrderByCreatedAtDesc(String courseId);
}
