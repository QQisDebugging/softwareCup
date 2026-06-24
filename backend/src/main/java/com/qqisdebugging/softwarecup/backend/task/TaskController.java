package com.qqisdebugging.softwarecup.backend.task;

import jakarta.validation.Valid;
import com.qqisdebugging.softwarecup.backend.course.LearningResourceResponse;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@RestController
@RequestMapping("/api/tasks")
public class TaskController {
    private final GenerationTaskService generationTaskService;

    public TaskController(GenerationTaskService generationTaskService) {
        this.generationTaskService = generationTaskService;
    }

    @PostMapping("/resource-generation")
    GenerationTaskResponse createResourceGenerationTask(@Valid @RequestBody CreateResourceTaskRequest request) {
        return generationTaskService.createResourceTask(request);
    }

    @GetMapping
    List<GenerationTaskResponse> listTasks(
            @RequestParam(required = false) String courseId,
            @RequestParam(required = false) String studentProfileId,
            @RequestParam(required = false) String status) {
        return generationTaskService.listRecentTasks(courseId, studentProfileId, status);
    }

    @GetMapping("/{taskId}")
    GenerationTaskResponse getTask(@PathVariable String taskId) {
        return generationTaskService.getTask(taskId);
    }

    @GetMapping("/{taskId}/steps")
    List<TaskStepResponse> listSteps(@PathVariable String taskId) {
        return generationTaskService.listSteps(taskId);
    }

    @GetMapping("/{taskId}/model-invocations")
    List<ModelInvocationResponse> listModelInvocations(@PathVariable String taskId) {
        return generationTaskService.listModelInvocations(taskId);
    }

    @GetMapping("/{taskId}/audits")
    List<GenerationAuditResponse> listAudits(@PathVariable String taskId) {
        return generationTaskService.listAudits(taskId);
    }

    @PostMapping("/{taskId}/review-decision")
    ReviewDecisionResponse reviewDecision(
            @PathVariable String taskId,
            @Valid @RequestBody ReviewDecisionRequest request) {
        return generationTaskService.reviewDecision(taskId, request);
    }

    @PostMapping("/{taskId}/publish")
    List<LearningResourceResponse> publishTaskResources(
            @PathVariable String taskId,
            @Valid @RequestBody(required = false) PublishTaskResourcesRequest request) {
        return generationTaskService.publishTaskResources(taskId, request);
    }

    @GetMapping("/{taskId}/events")
    SseEmitter streamEvents(@PathVariable String taskId) {
        return generationTaskService.subscribeEvents(taskId);
    }
}
