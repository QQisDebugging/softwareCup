package com.qqisdebugging.softwarecup.backend.learning;

import com.qqisdebugging.softwarecup.backend.agent.AssessmentGenerateAgentResponse;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/learning")
public class LearningLoopController {
    private final LearningLoopService learningLoopService;
    private final LearningConversationService conversationService;

    public LearningLoopController(
            LearningLoopService learningLoopService,
            LearningConversationService conversationService) {
        this.learningLoopService = learningLoopService;
        this.conversationService = conversationService;
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

    @GetMapping("/conversations")
    List<LearningConversationResponse> listConversations(
            @RequestParam String studentProfileId,
            @RequestParam(required = false) String courseId,
            @RequestParam(required = false) Boolean archived) {
        return conversationService.listConversations(studentProfileId, courseId, archived);
    }

    @PostMapping("/conversations")
    LearningConversationResponse createConversation(@Valid @RequestBody CreateLearningConversationRequest request) {
        return conversationService.createConversation(request);
    }

    @PatchMapping("/conversations/{conversationId}")
    LearningConversationResponse updateConversation(
            @PathVariable String conversationId,
            @Valid @RequestBody UpdateLearningConversationRequest request) {
        return conversationService.updateConversation(conversationId, request);
    }

    @DeleteMapping("/conversations/{conversationId}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    void deleteConversation(@PathVariable String conversationId) {
        conversationService.deleteConversation(conversationId);
    }

    @GetMapping("/conversations/{conversationId}/messages")
    List<LearningConversationMessageResponse> listConversationMessages(@PathVariable String conversationId) {
        return conversationService.listMessages(conversationId);
    }

    @GetMapping("/course-doubts")
    List<CourseDoubtRecordResponse> listCourseDoubts(
            @RequestParam String studentProfileId,
            @RequestParam String courseId) {
        return conversationService.listCourseDoubts(studentProfileId, courseId);
    }

    @PostMapping("/conversations/{conversationId}/messages")
    SendLearningConversationMessageResponse sendConversationMessage(
            @PathVariable String conversationId,
            @Valid @RequestBody SendLearningConversationMessageRequest request) {
        return conversationService.sendMessage(conversationId, request);
    }

    @GetMapping("/attempts")
    List<QuizAttemptResponse> listQuizAttempts(@RequestParam String studentProfileId) {
        return learningLoopService.listQuizAttempts(studentProfileId);
    }
}
