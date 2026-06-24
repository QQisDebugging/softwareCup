package com.qqisdebugging.softwarecup.backend.assignment;

import java.util.Map;

/**
 * 学生提交作业/测试。homework 用 content；quiz 用 answers（题目id -> 选项序号）。
 */
public record SubmitAssignmentRequest(
        String studentProfileId,
        String content,
        Map<String, Integer> answers) {
}
