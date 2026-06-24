package com.qqisdebugging.softwarecup.backend.auth;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PlatformAccountRepository extends JpaRepository<PlatformAccount, String> {
    Optional<PlatformAccount> findByUsernameIgnoreCase(String username);

    boolean existsByUsernameIgnoreCase(String username);
}
