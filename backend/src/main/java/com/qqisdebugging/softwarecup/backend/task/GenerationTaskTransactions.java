package com.qqisdebugging.softwarecup.backend.task;

import com.qqisdebugging.softwarecup.backend.agent.ResourceAgentResponse;
import com.qqisdebugging.softwarecup.backend.common.NotFoundException;
import com.qqisdebugging.softwarecup.backend.course.Course;
import com.qqisdebugging.softwarecup.backend.course.CourseService;
import com.qqisdebugging.softwarecup.backend.course.LearningResource;
import com.qqisdebugging.softwarecup.backend.course.LearningResourceRepository;
import com.qqisdebugging.softwarecup.backend.profile.ProfileService;
import com.qqisdebugging.softwarecup.backend.profile.StudentProfile;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class GenerationTaskTransactions {
    private final GenerationTaskRepository taskRepository;
    private final LearningResourceRepository resourceRepository;
    private final ProfileService profileService;
    private final CourseService courseService;

    public GenerationTaskTransactions(
            GenerationTaskRepository taskRepository,
            LearningResourceRepository resourceRepository,
            ProfileService profileService,
            CourseService courseService) {
        this.taskRepository = taskRepository;
        this.resourceRepository = resourceRepository;
        this.profileService = profileService;
        this.courseService = courseService;
    }

    @Transactional
    public ResourceGenerationContext markRunningAndLoadContext(String taskId) {
        GenerationTask task = requireTask(taskId);
        task.markRunning();
        StudentProfile profile = profileService.requireProfile(task.getStudentProfileId());
        Course course = courseService.requireCourse(task.getCourseId());
        return new ResourceGenerationContext(taskRepository.save(task), profile, course);
    }

    @Transactional
    public void saveGeneratedResource(
            String taskId,
            String courseId,
            String requestedResourceType,
            String requestedModality,
            ResourceAgentResponse response) {
        GenerationTask task = requireTask(taskId);
        String title = valueOrFallback(response.title(), task.getTopic() + "学习资源");
        LearningResource resource = new LearningResource(
                courseId,
                taskId,
                title,
                valueOrFallback(response.resourceType(), requestedResourceType),
                valueOrFallback(response.modality(), requestedModality),
                valueOrFallback(response.targetLevel(), "自适应"),
                response.estimatedMinutes() == null ? 20 : response.estimatedMinutes(),
                valueOrFallback(response.content(), "资源生成服务未返回正文。"));
        LearningResource saved = resourceRepository.save(resource);
        task.markSucceeded(saved.getId(), valueOrFallback(response.summary(), "资源生成完成"));
        taskRepository.save(task);
    }

    @Transactional
    public void markFailed(String taskId, String message) {
        taskRepository.findById(taskId).ifPresent(task -> {
            task.markFailed(message);
            taskRepository.save(task);
        });
    }

    private GenerationTask requireTask(String taskId) {
        return taskRepository.findById(taskId)
                .orElseThrow(() -> new NotFoundException("Generation task not found: " + taskId));
    }

    private String valueOrFallback(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }

    public record ResourceGenerationContext(GenerationTask task, StudentProfile profile, Course course) {
    }
}
