package com.qqisdebugging.softwarecup.backend.course;

import jakarta.validation.Valid;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/courses")
public class CourseController {
    private final CourseService courseService;

    public CourseController(CourseService courseService) {
        this.courseService = courseService;
    }

    @GetMapping
    List<CourseResponse> listCourses() {
        return courseService.listCourses();
    }

    @PostMapping
    CourseResponse createCourse(@Valid @RequestBody CreateCourseRequest request) {
        return courseService.createCourse(request);
    }

    @GetMapping("/{courseId}")
    CourseResponse getCourse(@PathVariable String courseId) {
        return courseService.getCourse(courseId);
    }

    @GetMapping("/{courseId}/resources")
    List<LearningResourceResponse> listResources(@PathVariable String courseId) {
        return courseService.listResources(courseId);
    }
}
