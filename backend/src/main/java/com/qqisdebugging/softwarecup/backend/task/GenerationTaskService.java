package com.qqisdebugging.softwarecup.backend.task;

import com.qqisdebugging.softwarecup.backend.common.NotFoundException;
import com.qqisdebugging.softwarecup.backend.course.CourseService;
import com.qqisdebugging.softwarecup.backend.course.ResourceType;
import com.qqisdebugging.softwarecup.backend.profile.ProfileService;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@Service
public class GenerationTaskService {
    private final GenerationTaskRepository taskRepository;
    private final ProfileService profileService;
    private final CourseService courseService;
    private final GenerationTaskRunner generationTaskRunner;
    private final GenerationTaskTransactions transactions;
    private final TaskProgressPublisher progressPublisher;

    public GenerationTaskService(
            GenerationTaskRepository taskRepository,
            ProfileService profileService,
            CourseService courseService,
            GenerationTaskRunner generationTaskRunner,
            GenerationTaskTransactions transactions,
            TaskProgressPublisher progressPublisher) {
        this.taskRepository = taskRepository;
        this.profileService = profileService;
        this.courseService = courseService;
        this.generationTaskRunner = generationTaskRunner;
        this.transactions = transactions;
        this.progressPublisher = progressPublisher;
    }

    public GenerationTaskResponse createResourceTask(CreateResourceTaskRequest request) {
        profileService.requireProfile(request.studentProfileId());
        courseService.requireCourse(request.courseId());
        ResourceType resourceType = ResourceType.normalize(request.resourceType());
        GenerationTask task = taskRepository.save(new GenerationTask(
                request.studentProfileId(),
                request.courseId(),
                request.topic(),
                request.prompt()));
        runAfterCommit(task.getId(), resourceType.name(), request.modality());
        return GenerationTaskResponse.from(task);
    }

    @Transactional(readOnly = true)
    public List<GenerationTaskResponse> listRecentTasks() {
        return taskRepository.findTop50ByOrderByCreatedAtDesc().stream()
                .map(GenerationTaskResponse::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public GenerationTaskResponse getTask(String taskId) {
        return GenerationTaskResponse.from(requireTask(taskId));
    }

    @Transactional(readOnly = true)
    public List<TaskStepResponse> listSteps(String taskId) {
        return transactions.listSteps(taskId).stream()
                .map(TaskStepResponse::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<ModelInvocationResponse> listModelInvocations(String taskId) {
        return transactions.listInvocations(taskId).stream()
                .map(ModelInvocationResponse::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<GenerationAuditResponse> listAudits(String taskId) {
        return transactions.listAudits(taskId).stream()
                .map(GenerationAuditResponse::from)
                .toList();
    }

    public SseEmitter subscribeEvents(String taskId) {
        requireTask(taskId);
        SseEmitter emitter = progressPublisher.subscribe(taskId);
        GenerationTask task = requireTask(taskId);
        progressPublisher.publish(TaskProgressEvent.of(
                taskId,
                "TASK_SNAPSHOT",
                task.getProgressPercent(),
                task.getCurrentStep(),
                task.getStatus(),
                task.getResultSummary()));
        return emitter;
    }

    private GenerationTask requireTask(String taskId) {
        return taskRepository.findById(taskId)
                .orElseThrow(() -> new NotFoundException("Generation task not found: " + taskId));
    }

    private void runAfterCommit(String taskId, String resourceType, String modality) {
        if (!TransactionSynchronizationManager.isSynchronizationActive()) {
            generationTaskRunner.runResourceGeneration(taskId, resourceType, modality);
            return;
        }
        TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
            @Override
            public void afterCommit() {
                generationTaskRunner.runResourceGeneration(taskId, resourceType, modality);
            }
        });
    }
}
