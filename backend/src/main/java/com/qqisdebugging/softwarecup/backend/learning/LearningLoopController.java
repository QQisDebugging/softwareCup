package com.qqisdebugging.softwarecup.backend.learning;

import com.qqisdebugging.softwarecup.backend.agent.AssessmentGenerateAgentResponse;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/learning")
public class LearningLoopController {
    private final LearningLoopService learningLoopService;

    public LearningLoopController(LearningLoopService learningLoopService) {
        this.learningLoopService = learningLoopService;
    }

    @PostMapping("/tutoring")
    TutoringSessionResponse tutor(@Valid @RequestBody CreateTutoringRequest request) {
        return learningLoopService.tutor(request);
    }

    @PostMapping("/assessments/generate")
    AssessmentGenerateAgentResponse generateAssessment(@Valid @RequestBody GenerateAssessmentRequest request) {
        return learningLoopService.generateAssessment(request);
    }

    @PostMapping("/assessments/grade")
    GradeAssessmentResponse gradeAssessment(@Valid @RequestBody GradeAssessmentRequest request) {
        return learningLoopService.gradeAssessment(request);
    }

    @GetMapping("/agent-events")
    List<LearningEventResponse> listEvents(@RequestParam String studentProfileId) {
        return learningLoopService.listEvents(studentProfileId);
    }

    @GetMapping("/tutoring")
    List<TutoringSessionResponse> listTutoringSessions(@RequestParam String studentProfileId) {
        return learningLoopService.listTutoringSessions(studentProfileId);
    }

    @GetMapping("/attempts")
    List<QuizAttemptResponse> listQuizAttempts(@RequestParam String studentProfileId) {
        return learningLoopService.listQuizAttempts(studentProfileId);
    }
}
