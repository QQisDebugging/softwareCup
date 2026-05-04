package com.qqisdebugging.softwarecup.backend.course;

import com.qqisdebugging.softwarecup.backend.common.NotFoundException;
import java.util.Comparator;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class CourseService {
    private final CourseRepository courseRepository;
    private final LearningResourceRepository resourceRepository;

    public CourseService(CourseRepository courseRepository, LearningResourceRepository resourceRepository) {
        this.courseRepository = courseRepository;
        this.resourceRepository = resourceRepository;
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
    public List<LearningResourceResponse> listResources(String courseId) {
        requireCourse(courseId);
        return resourceRepository.findByCourseIdOrderByCreatedAtDesc(courseId).stream()
                .map(LearningResourceResponse::from)
                .toList();
    }

    public Course requireCourse(String courseId) {
        return courseRepository.findById(courseId)
                .orElseThrow(() -> new NotFoundException("Course not found: " + courseId));
    }
}
