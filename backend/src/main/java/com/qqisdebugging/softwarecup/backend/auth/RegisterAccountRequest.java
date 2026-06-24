package com.qqisdebugging.softwarecup.backend.auth;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record RegisterAccountRequest(
        @NotBlank @Pattern(regexp = "^[a-z0-9._-]{4,32}$") String username,
        @NotBlank @Size(min = 8, max = 80) String password,
        @NotBlank @Pattern(regexp = "student|teacher") String role,
        @NotBlank @Size(max = 80) String name,
        @Size(max = 160) String department,
        String inviteCode) {
}
