package com.qqisdebugging.softwarecup.backend.assignment;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.qqisdebugging.softwarecup.backend.common.NotFoundException;
import com.qqisdebugging.softwarecup.backend.course.CourseService;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AssignmentService {
    private final CourseAssignmentRepository assignmentRepository;
    private final AssignmentSubmissionRepository submissionRepository;
    private final CourseService courseService;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public AssignmentService(
            CourseAssignmentRepository assignmentRepository,
            AssignmentSubmissionRepository submissionRepository,
            CourseService courseService) {
        this.assignmentRepository = assignmentRepository;
        this.submissionRepository = submissionRepository;
        this.courseService = courseService;
    }

    @Transactional
    public AssignmentResponse createAssignment(String courseId, CreateAssignmentRequest request) {
        courseService.requireCourse(courseId);
        String type = "quiz".equalsIgnoreCase(request.type()) ? "quiz" : "homework";
        CourseAssignment assignment = assignmentRepository.save(new CourseAssignment(
                courseId,
                type,
                requireText(request.title(), "未命名任务"),
                requireText(request.publisher(), "课程教师"),
                request.description() == null ? "" : request.description(),
                request.deadlineLabel(),
                request.estimatedMinutes() == null ? 20 : request.estimatedMinutes(),
                writeJson("quiz".equals(type) ? safeList(request.questions()) : List.of())));
        // 老师视角下发完整题目（含答案）
        return AssignmentResponse.from(assignment, null, objectMapper, true);
    }

    @Transactional(readOnly = true)
    public List<AssignmentResponse> listAssignments(String courseId, String studentProfileId) {
        return assignmentRepository.findByCourseIdOrderByCreatedAtAsc(courseId).stream()
                .map(assignment -> {
                    AssignmentSubmission submission = studentProfileId == null || studentProfileId.isBlank()
                            ? null
                            : submissionRepository
                                    .findByAssignmentIdAndStudentProfileId(assignment.getId(), studentProfileId)
                                    .orElse(null);
                    // 已提交后才下发答案，便于前端展示对错
                    return AssignmentResponse.from(assignment, submission, objectMapper, submission != null);
                })
                .toList();
    }

    @Transactional
    public AssignmentResponse submitAssignment(String assignmentId, SubmitAssignmentRequest request) {
        CourseAssignment assignment = requireAssignment(assignmentId);
        if (request.studentProfileId() == null || request.studentProfileId().isBlank()) {
            throw new IllegalArgumentException("studentProfileId is required");
        }
        String content = "";
        String answersJson = "{}";
        Integer score = null;
        Integer total = null;

        if ("quiz".equals(assignment.getType())) {
            Map<String, Integer> answers = request.answers() == null ? Map.of() : request.answers();
            answersJson = writeJson(answers);
            List<CreateAssignmentRequest.QuizQuestionPayload> questions = parseQuestions(assignment.getQuestionsJson());
            int correct = 0;
            for (CreateAssignmentRequest.QuizQuestionPayload question : questions) {
                Integer chosen = answers.get(question.id());
                if (chosen != null && question.answer() != null && chosen.equals(question.answer())) {
                    correct++;
                }
            }
            score = correct;
            total = questions.size();
        } else {
            content = request.content() == null ? "" : request.content().trim();
            if (content.isEmpty()) {
                throw new IllegalArgumentException("Homework content is required");
            }
        }

        AssignmentSubmission submission = submissionRepository
                .findByAssignmentIdAndStudentProfileId(assignmentId, request.studentProfileId())
                .orElse(null);
        if (submission == null) {
            submission = new AssignmentSubmission(
                    assignmentId,
                    request.studentProfileId(),
                    assignment.getCourseId(),
                    content,
                    answersJson,
                    score,
                    total);
        } else {
            submission.update(content, answersJson, score, total);
        }
        AssignmentSubmission saved = submissionRepository.save(submission);
        return AssignmentResponse.from(assignment, saved, objectMapper, true);
    }

    private List<CreateAssignmentRequest.QuizQuestionPayload> parseQuestions(String json) {
        try {
            if (json == null || json.isBlank()) {
                return List.of();
            }
            List<CreateAssignmentRequest.QuizQuestionPayload> parsed = objectMapper.readValue(
                    json,
                    objectMapper.getTypeFactory().constructCollectionType(
                            List.class, CreateAssignmentRequest.QuizQuestionPayload.class));
            return parsed == null ? List.of() : parsed;
        } catch (Exception ex) {
            return List.of();
        }
    }

    private CourseAssignment requireAssignment(String assignmentId) {
        return assignmentRepository.findById(assignmentId)
                .orElseThrow(() -> new NotFoundException("Assignment not found: " + assignmentId));
    }

    private String requireText(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value.trim();
    }

    private <T> List<T> safeList(List<T> value) {
        return value == null ? List.of() : value;
    }

    private String writeJson(Object value) {
        try {
            return objectMapper.writeValueAsString(value);
        } catch (Exception ex) {
            return "[]";
        }
    }
}
