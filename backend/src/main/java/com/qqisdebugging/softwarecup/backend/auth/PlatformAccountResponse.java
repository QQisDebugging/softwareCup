package com.qqisdebugging.softwarecup.backend.auth;

public record PlatformAccountResponse(
        String id,
        String username,
        String role,
        String name,
        String title,
        String home,
        String homeRoute,
        String department,
        String status) {
    static PlatformAccountResponse from(PlatformAccount account) {
        return new PlatformAccountResponse(
                account.getId(),
                account.getUsername(),
                account.getRole(),
                account.getDisplayName(),
                account.getTitle(),
                account.getHome(),
                "teacher".equals(account.getRole()) ? "/teacher" : "/dashboard",
                account.getDepartment(),
                account.getStatus());
    }
}
