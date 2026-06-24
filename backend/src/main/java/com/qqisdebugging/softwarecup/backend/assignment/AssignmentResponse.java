package com.qqisdebugging.softwarecup.backend.assignment;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Instant;
import java.util.List;

public record AssignmentResponse(
        String id,
        String courseId,
        String type,
        String title,
        String publisher,
        String description,
        String deadlineLabel,
        Integer estimatedMinutes,
        List<QuizQuestionView> questions,
        SubmissionView submission,
        Instant createdAt) {

    public record QuizQuestionView(String id, String stem, List<String> options, Integer answer) {
    }

    public record SubmissionView(String content, java.util.Map<String, Integer> answers, Integer score, Integer total, Instant submittedAt) {
    }

    public static AssignmentResponse from(
            CourseAssignment assignment,
            AssignmentSubmission submission,
            ObjectMapper objectMapper,
            boolean includeAnswerKey) {
        List<QuizQuestionView> questions = List.of();
        try {
            if (assignment.getQuestionsJson() != null && !assignment.getQuestionsJson().isBlank()) {
                List<QuizQuestionView> parsed = objectMapper.readValue(
                        assignment.getQuestionsJson(),
                        objectMapper.getTypeFactory().constructCollectionType(List.class, QuizQuestionView.class));
                questions = parsed == null ? List.of() : parsed;
            }
        } catch (Exception ignored) {
            questions = List.of();
        }
        // 学生未提交前不下发正确答案，避免泄题
        if (!includeAnswerKey) {
            questions = questions.stream()
                    .map(q -> new QuizQuestionView(q.id(), q.stem(), q.options(), null))
                    .toList();
        }
        SubmissionView submissionView = null;
        if (submission != null) {
            java.util.Map<String, Integer> answers = java.util.Map.of();
            try {
                if (submission.getAnswersJson() != null && !submission.getAnswersJson().isBlank()) {
                    answers = objectMapper.readValue(
                            submission.getAnswersJson(),
                            objectMapper.getTypeFactory().constructMapType(
                                    java.util.Map.class, String.class, Integer.class));
                }
            } catch (Exception ignored) {
                answers = java.util.Map.of();
            }
            submissionView = new SubmissionView(
                    submission.getContent(),
                    answers,
                    submission.getScore(),
                    submission.getTotal(),
                    submission.getSubmittedAt());
        }
        return new AssignmentResponse(
                assignment.getId(),
                assignment.getCourseId(),
                assignment.getType(),
                assignment.getTitle(),
                assignment.getPublisher(),
                assignment.getDescription(),
                assignment.getDeadlineLabel(),
                assignment.getEstimatedMinutes(),
                questions,
                submissionView,
                assignment.getCreatedAt());
    }
}
