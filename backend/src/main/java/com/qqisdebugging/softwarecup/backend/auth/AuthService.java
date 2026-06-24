package com.qqisdebugging.softwarecup.backend.auth;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {
    private static final String TEACHER_INVITE_CODE = "TEACHER-2026";

    private final PlatformAccountRepository accountRepository;

    public AuthService(PlatformAccountRepository accountRepository) {
        this.accountRepository = accountRepository;
    }

    @Transactional(readOnly = true)
    public PlatformAccountResponse login(LoginRequest request) {
        String username = normalizeUsername(request.username());
        PlatformAccount account = accountRepository.findByUsernameIgnoreCase(username)
                .orElseThrow(() -> new IllegalArgumentException("账号不存在"));
        if (!account.getRole().equals(request.role())) {
            throw new IllegalArgumentException("账号角色不匹配");
        }
        if (!"active".equals(account.getStatus())) {
            throw new IllegalArgumentException("账号尚未启用");
        }
        if (!account.getPasswordHash().equals(hashPassword(username, request.password()))) {
            throw new IllegalArgumentException("密码错误");
        }
        return PlatformAccountResponse.from(account);
    }

    @Transactional
    public PlatformAccountResponse register(RegisterAccountRequest request) {
        String username = normalizeUsername(request.username());
        if (accountRepository.existsByUsernameIgnoreCase(username)) {
            throw new IllegalArgumentException("账号已存在");
        }
        if ("teacher".equals(request.role()) && !TEACHER_INVITE_CODE.equals(request.inviteCode())) {
            throw new IllegalArgumentException("教师注册需要有效邀请码");
        }

        String role = request.role();
        String displayName = request.name().trim();
        String department = cleanOptional(request.department(), "teacher".equals(role) ? "课程教学团队" : "学习者");
        PlatformAccount account = new PlatformAccount(
                username,
                hashPassword(username, request.password()),
                role,
                displayName,
                "teacher".equals(role) ? "课程教师" : "学生",
                "teacher".equals(role) ? "课程资源、班级学情与智能体审核" : "个性化学习、自建课程与 AI 辅导",
                department);
        return PlatformAccountResponse.from(accountRepository.save(account));
    }

    private static String normalizeUsername(String username) {
        return username.trim().toLowerCase();
    }

    private static String cleanOptional(String value, String fallback) {
        if (value == null || value.isBlank()) {
            return fallback;
        }
        return value.trim();
    }

    static String hashPassword(String username, String password) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] bytes = digest.digest((normalizeUsername(username) + ":" + password).getBytes(StandardCharsets.UTF_8));
            StringBuilder builder = new StringBuilder(bytes.length * 2);
            for (byte b : bytes) {
                builder.append(String.format("%02x", b));
            }
            return builder.toString();
        } catch (NoSuchAlgorithmException ex) {
            throw new IllegalStateException("SHA-256 is not available", ex);
        }
    }
}
