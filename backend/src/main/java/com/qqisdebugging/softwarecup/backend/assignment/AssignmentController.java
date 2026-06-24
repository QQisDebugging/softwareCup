package com.qqisdebugging.softwarecup.backend.assignment;

import jakarta.validation.Valid;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AssignmentController {
    private final AssignmentService assignmentService;

    public AssignmentController(AssignmentService assignmentService) {
        this.assignmentService = assignmentService;
    }

    @GetMapping("/api/courses/{courseId}/assignments")
    List<AssignmentResponse> listAssignments(
            @PathVariable String courseId,
            @RequestParam(required = false) String studentProfileId) {
        return assignmentService.listAssignments(courseId, studentProfileId);
    }

    @PostMapping("/api/courses/{courseId}/assignments")
    AssignmentResponse createAssignment(
            @PathVariable String courseId,
            @Valid @RequestBody CreateAssignmentRequest request) {
        return assignmentService.createAssignment(courseId, request);
    }

    @PostMapping("/api/assignments/{assignmentId}/submissions")
    AssignmentResponse submitAssignment(
            @PathVariable String assignmentId,
            @Valid @RequestBody SubmitAssignmentRequest request) {
        return assignmentService.submitAssignment(assignmentId, request);
    }
}
