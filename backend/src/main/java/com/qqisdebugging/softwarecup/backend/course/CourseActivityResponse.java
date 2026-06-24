package com.qqisdebugging.softwarecup.backend.course;

import java.time.Instant;
import java.util.List;

/**
 * 课程动态聚合：把"老师发布的资源 / 课程作业 / AI 推荐资源"聚合为可直接展示的动态分组，
 * 供学生课程页的"课程动态"区使用，替代前端写死的演示数据。
 */
public record CourseActivityResponse(List<ActivityGroup> groups) {

    public record ActivityGroup(String key, String title, List<ActivityItem> items) {
    }

    public record ActivityItem(
            String title,
            String courseTitle,
            String courseId,
            String detail,
            Instant time) {
    }
}
