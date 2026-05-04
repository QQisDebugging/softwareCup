package com.qqisdebugging.softwarecup.backend.upload;

import org.springframework.data.jpa.repository.JpaRepository;

public interface UploadedAssetRepository extends JpaRepository<UploadedAsset, String> {
}
