package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.validation.Valid;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/learning")
public class LearningController {
    private final LearningService learningService;

    public LearningController(LearningService learningService) {
        this.learningService = learningService;
    }

    @GetMapping("/paths")
    List<LearningPathResponse> listPaths(
            @RequestParam String studentProfileId,
            @RequestParam(required = false) String courseId) {
        return learningService.listPaths(studentProfileId, courseId);
    }

    @GetMapping("/paths/{pathId}")
    LearningPathResponse getPath(@PathVariable String pathId) {
        return learningService.getPath(pathId);
    }

    @GetMapping("/recommendations")
    List<ResourceRecommendationResponse> listRecommendations(@RequestParam String studentProfileId) {
        return learningService.listRecommendations(studentProfileId);
    }

    @PostMapping("/events")
    LearningEventResponse recordEvent(@Valid @RequestBody CreateLearningEventRequest request) {
        return learningService.recordEvent(request);
    }

    @GetMapping("/events")
    List<LearningEventResponse> listEvents(@RequestParam String studentProfileId) {
        return learningService.listEvents(studentProfileId);
    }

    @PostMapping("/quiz-attempts")
    QuizAttemptResponse recordQuizAttempt(@Valid @RequestBody CreateQuizAttemptRequest request) {
        return learningService.recordQuizAttempt(request);
    }

    @GetMapping("/mastery")
    List<KnowledgeMasteryResponse> listMastery(
            @RequestParam String studentProfileId,
            @RequestParam String courseId) {
        return learningService.listMastery(studentProfileId, courseId);
    }

    @GetMapping("/evaluation-reports")
    List<EvaluationReportResponse> listEvaluationReports(
            @RequestParam String studentProfileId,
            @RequestParam String courseId) {
        return learningService.listEvaluationReports(studentProfileId, courseId);
    }
}
