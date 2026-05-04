package com.qqisdebugging.softwarecup.backend.task;

import com.qqisdebugging.softwarecup.backend.common.NotFoundException;
import com.qqisdebugging.softwarecup.backend.course.CourseService;
import com.qqisdebugging.softwarecup.backend.profile.ProfileService;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class GenerationTaskService {
    private final GenerationTaskRepository taskRepository;
    private final ProfileService profileService;
    private final CourseService courseService;
    private final GenerationTaskRunner generationTaskRunner;

    public GenerationTaskService(
            GenerationTaskRepository taskRepository,
            ProfileService profileService,
            CourseService courseService,
            GenerationTaskRunner generationTaskRunner) {
        this.taskRepository = taskRepository;
        this.profileService = profileService;
        this.courseService = courseService;
        this.generationTaskRunner = generationTaskRunner;
    }

    @Transactional
    public GenerationTaskResponse createResourceTask(CreateResourceTaskRequest request) {
        profileService.requireProfile(request.studentProfileId());
        courseService.requireCourse(request.courseId());
        GenerationTask task = taskRepository.save(new GenerationTask(
                request.studentProfileId(),
                request.courseId(),
                request.topic(),
                request.prompt()));
        generationTaskRunner.runResourceGeneration(task.getId(), request.resourceType(), request.modality());
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

    private GenerationTask requireTask(String taskId) {
        return taskRepository.findById(taskId)
                .orElseThrow(() -> new NotFoundException("Generation task not found: " + taskId));
    }
}
