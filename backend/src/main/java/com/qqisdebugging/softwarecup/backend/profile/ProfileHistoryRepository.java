package com.qqisdebugging.softwarecup.backend.profile;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProfileHistoryRepository extends JpaRepository<ProfileHistory, String> {
    List<ProfileHistory> findByProfileIdOrderByCreatedAtDesc(String profileId);
}
