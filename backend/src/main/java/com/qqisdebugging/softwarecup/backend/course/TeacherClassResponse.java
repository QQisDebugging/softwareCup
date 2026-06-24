package com.qqisdebugging.softwarecup.backend.course;

/**
 * 教师班级视图：以真实课程为单位聚合学生人数，替代教师画像页写死的班级选项。
 */
public record TeacherClassResponse(
        String courseId,
        String courseTitle,
        String department,
        long studentCount) {
}
