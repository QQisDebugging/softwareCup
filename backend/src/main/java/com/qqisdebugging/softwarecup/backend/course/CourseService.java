package com.qqisdebugging.softwarecup.backend.course;

import com.qqisdebugging.softwarecup.backend.common.NotFoundException;
import com.qqisdebugging.softwarecup.backend.assignment.CourseAssignment;
import com.qqisdebugging.softwarecup.backend.assignment.CourseAssignmentRepository;
import com.qqisdebugging.softwarecup.backend.profile.ProfileService;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class CourseService {
    private final CourseRepository courseRepository;
    private final LearningResourceRepository resourceRepository;
    private final CourseEnrollmentRepository enrollmentRepository;
    private final CourseAssignmentRepository assignmentRepository;
    private final ProfileService profileService;

    public CourseService(
            CourseRepository courseRepository,
            LearningResourceRepository resourceRepository,
            CourseEnrollmentRepository enrollmentRepository,
            CourseAssignmentRepository assignmentRepository,
            ProfileService profileService) {
        this.courseRepository = courseRepository;
        this.resourceRepository = resourceRepository;
        this.enrollmentRepository = enrollmentRepository;
        this.assignmentRepository = assignmentRepository;
        this.profileService = profileService;
    }

    @Transactional(readOnly = true)
    public List<CourseResponse> listCourses() {
        return courseRepository.findAll().stream()
                .sorted(Comparator.comparing(Course::getCreatedAt).reversed())
                .map(CourseResponse::from)
                .toList();
    }

    @Transactional
    public CourseResponse createCourse(CreateCourseRequest request) {
        Course course = new Course(
                request.title(),
                request.department(),
                request.description(),
                request.creditHours(),
                request.syllabusJson());
        return CourseResponse.from(courseRepository.save(course));
    }

    @Transactional(readOnly = true)
    public CourseResponse getCourse(String courseId) {
        return CourseResponse.from(requireCourse(courseId));
    }

    @Transactional(readOnly = true)
    public List<LearningResourceResponse> listResources(String courseId, boolean publishedOnly) {
        requireCourse(courseId);
        List<LearningResource> resources = publishedOnly
                ? resourceRepository.findByCourseIdAndReviewStatusInOrderByCreatedAtDesc(
                        courseId,
                        List.of("PUBLISHED", "APPROVED"))
                : resourceRepository.findByCourseIdOrderByCreatedAtDesc(courseId);
        return resources.stream()
                .map(LearningResourceResponse::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public CourseActivityResponse getCourseActivity(String courseId) {
        Course course = requireCourse(courseId);
        String courseTitle = course.getTitle();

        // 老师发布：本课程已发布/已审核通过的资源
        List<LearningResource> published = resourceRepository
                .findByCourseIdAndReviewStatusInOrderByCreatedAtDesc(courseId, List.of("PUBLISHED", "APPROVED"));
        List<CourseActivityResponse.ActivityItem> publishItems = new ArrayList<>();
        for (LearningResource r : published.stream().limit(5).toList()) {
            publishItems.add(new CourseActivityResponse.ActivityItem(
                    "发布了资源《" + r.getTitle() + "》",
                    courseTitle,
                    courseId,
                    (r.getPublishedBy() == null || r.getPublishedBy().isBlank() ? "课程教师" : r.getPublishedBy())
                            + " · " + (r.getResourceType() == null ? "学习资源" : r.getResourceType()),
                    r.getPublishedAt() != null ? r.getPublishedAt() : r.getCreatedAt()));
        }

        // 待提交提醒：本课程的作业/测试
        List<CourseAssignment> assignments = assignmentRepository.findByCourseIdOrderByCreatedAtAsc(courseId);
        List<CourseActivityResponse.ActivityItem> todoItems = new ArrayList<>();
        for (CourseAssignment a : assignments.stream().limit(5).toList()) {
            todoItems.add(new CourseActivityResponse.ActivityItem(
                    a.getTitle(),
                    courseTitle,
                    courseId,
                    a.getPublisher() + " 发布 · " + (a.getDeadlineLabel() == null ? "待提交" : a.getDeadlineLabel()),
                    a.getCreatedAt()));
        }

        List<CourseActivityResponse.ActivityGroup> groups = new ArrayList<>();
        if (!publishItems.isEmpty()) {
            groups.add(new CourseActivityResponse.ActivityGroup("publish", "老师发布", publishItems));
        }
        if (!todoItems.isEmpty()) {
            groups.add(new CourseActivityResponse.ActivityGroup("todo", "待提交提醒", todoItems));
        }
        return new CourseActivityResponse(groups);
    }

    @Transactional
    public CourseEnrollmentResponse joinCourse(String courseId, JoinCourseRequest request) {
        Course course = requireCourse(courseId);
        profileService.requireProfile(request.studentProfileId());
        CourseEnrollment enrollment = enrollmentRepository
                .findByCourseIdAndStudentProfileId(courseId, request.studentProfileId())
                .orElseGet(() -> new CourseEnrollment(courseId, request.studentProfileId()));
        enrollment.activate();
        return CourseEnrollmentResponse.from(enrollmentRepository.save(enrollment), course);
    }

    @Transactional(readOnly = true)
    public List<CourseEnrollmentResponse> listEnrolledCourses(String studentProfileId) {
        profileService.requireProfile(studentProfileId);
        return enrollmentRepository.findByStudentProfileIdAndStatusOrderByCreatedAtDesc(studentProfileId, "ACTIVE")
                .stream()
                .map(enrollment -> CourseEnrollmentResponse.from(enrollment, requireCourse(enrollment.getCourseId())))
                .toList();
    }

    public Course requireCourse(String courseId) {
        return courseRepository.findById(courseId)
                .orElseThrow(() -> new NotFoundException("Course not found: " + courseId));
    }

    @Transactional(readOnly = true)
    public List<TeacherClassResponse> listTeacherClasses() {
        return courseRepository.findAll().stream()
                .sorted(Comparator.comparing(Course::getCreatedAt).reversed())
                .map(course -> new TeacherClassResponse(
                        course.getId(),
                        course.getTitle(),
                        course.getDepartment(),
                        enrollmentRepository.countByCourseId(course.getId())))
                .toList();
    }
}
