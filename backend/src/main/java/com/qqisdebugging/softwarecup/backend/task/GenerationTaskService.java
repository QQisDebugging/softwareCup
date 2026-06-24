package com.qqisdebugging.softwarecup.backend.task;

import com.qqisdebugging.softwarecup.backend.common.NotFoundException;
import com.qqisdebugging.softwarecup.backend.course.CourseService;
import com.qqisdebugging.softwarecup.backend.course.LearningResourceRepository;
import com.qqisdebugging.softwarecup.backend.course.LearningResourceResponse;
import com.qqisdebugging.softwarecup.backend.course.ResourceType;
import com.qqisdebugging.softwarecup.backend.profile.ProfileService;
import java.util.List;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
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
    private final LearningResourceRepository resourceRepository;

    public GenerationTaskService(
            GenerationTaskRepository taskRepository,
            ProfileService profileService,
            CourseService courseService,
            GenerationTaskRunner generationTaskRunner,
            GenerationTaskTransactions transactions,
            TaskProgressPublisher progressPublisher,
            LearningResourceRepository resourceRepository) {
        this.taskRepository = taskRepository;
        this.profileService = profileService;
        this.courseService = courseService;
        this.generationTaskRunner = generationTaskRunner;
        this.transactions = transactions;
        this.progressPublisher = progressPublisher;
        this.resourceRepository = resourceRepository;
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
        return GenerationTaskResponse.from(task, false);
    }

    @Transactional(readOnly = true)
    public List<GenerationTaskResponse> listRecentTasks(String courseId, String studentProfileId, String status) {
        Specification<GenerationTask> spec = (root, query, criteriaBuilder) -> criteriaBuilder.conjunction();
        if (hasText(courseId)) {
            spec = spec.and((root, query, criteriaBuilder) ->
                    criteriaBuilder.equal(root.get("courseId"), courseId.trim()));
        }
        if (hasText(studentProfileId)) {
            spec = spec.and((root, query, criteriaBuilder) ->
                    criteriaBuilder.equal(root.get("studentProfileId"), studentProfileId.trim()));
        }
        if (hasText(status)) {
            String normalizedStatus = status.trim().toUpperCase(java.util.Locale.ROOT);
            spec = spec.and((root, query, criteriaBuilder) ->
                    criteriaBuilder.equal(root.get("status"), normalizedStatus));
        }
        return taskRepository.findAll(
                        spec,
                        PageRequest.of(0, 50, Sort.by(Sort.Direction.DESC, "createdAt")))
                .getContent()
                .stream()
                .map(task -> GenerationTaskResponse.from(task, hasPublishedResources(task.getId())))
                .toList();
    }

    @Transactional(readOnly = true)
    public GenerationTaskResponse getTask(String taskId) {
        GenerationTask task = requireTask(taskId);
        return GenerationTaskResponse.from(task, hasPublishedResources(task.getId()));
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

    public List<LearningResourceResponse> publishTaskResources(String taskId, PublishTaskResourcesRequest request) {
        String publisherName = request == null ? null : request.publisherName();
        String publishNote = request == null ? null : request.publishNote();
        return transactions.publishTaskResources(taskId, publisherName, publishNote).stream()
                .map(LearningResourceResponse::from)
                .toList();
    }

    public ReviewDecisionResponse reviewDecision(String taskId, ReviewDecisionRequest request) {
        GenerationTaskTransactions.ReviewDecisionResult result = transactions.applyReviewDecision(
                taskId,
                request.decision(),
                request.reviewer(),
                request.note());
        return new ReviewDecisionResponse(
                taskId,
                request.decision(),
                request.reviewer(),
                request.note(),
                result.resources().stream().map(LearningResourceResponse::from).toList(),
                GenerationAuditResponse.from(result.audit()));
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

    private boolean hasText(String value) {
        return value != null && !value.isBlank();
    }

    private boolean hasPublishedResources(String taskId) {
        return resourceRepository.findBySourceTaskIdOrderByCreatedAtDesc(taskId).stream()
                .anyMatch(resource -> "PUBLISHED".equals(resource.getReviewStatus()));
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
