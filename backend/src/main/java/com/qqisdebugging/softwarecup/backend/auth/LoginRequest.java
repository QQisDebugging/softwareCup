package com.qqisdebugging.softwarecup.backend.auth;

import jakarta.validation.constraints.NotBlank;

public record LoginRequest(
        @NotBlank String username,
        @NotBlank String password,
        @NotBlank String role) {
}
