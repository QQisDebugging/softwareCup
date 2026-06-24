package com.qqisdebugging.softwarecup.backend.assignment;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CourseAssignmentRepository extends JpaRepository<CourseAssignment, String> {
    List<CourseAssignment> findByCourseIdOrderByCreatedAtAsc(String courseId);
}
