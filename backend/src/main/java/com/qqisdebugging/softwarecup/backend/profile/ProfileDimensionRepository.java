package com.qqisdebugging.softwarecup.backend.profile;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProfileDimensionRepository extends JpaRepository<ProfileDimension, String> {
    List<ProfileDimension> findByProfileIdOrderByDimensionKeyAsc(String profileId);

    Optional<ProfileDimension> findByProfileIdAndDimensionKey(String profileId, String dimensionKey);
}
