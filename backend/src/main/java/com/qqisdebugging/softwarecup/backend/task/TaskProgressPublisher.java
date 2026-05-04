package com.qqisdebugging.softwarecup.backend.task;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@Component
public class TaskProgressPublisher {
    private final Map<String, List<SseEmitter>> emitters = new ConcurrentHashMap<>();

    public SseEmitter subscribe(String taskId) {
        SseEmitter emitter = new SseEmitter(0L);
        emitters.computeIfAbsent(taskId, ignored -> new CopyOnWriteArrayList<>()).add(emitter);
        emitter.onCompletion(() -> remove(taskId, emitter));
        emitter.onTimeout(() -> remove(taskId, emitter));
        emitter.onError(ignored -> remove(taskId, emitter));
        send(emitter, "connected", TaskProgressEvent.of(taskId, "CONNECTED", 0, "已连接", "CONNECTED", "任务进度订阅已建立"));
        return emitter;
    }

    public void publish(TaskProgressEvent event) {
        List<SseEmitter> taskEmitters = emitters.getOrDefault(event.taskId(), List.of());
        for (SseEmitter emitter : taskEmitters) {
            send(emitter, event.eventType(), event);
        }
    }

    private void send(SseEmitter emitter, String eventName, TaskProgressEvent event) {
        try {
            emitter.send(SseEmitter.event().name(eventName).data(event));
        } catch (IOException | IllegalStateException ex) {
            emitter.completeWithError(ex);
        }
    }

    private void remove(String taskId, SseEmitter emitter) {
        List<SseEmitter> taskEmitters = emitters.get(taskId);
        if (taskEmitters != null) {
            taskEmitters.remove(emitter);
        }
    }
}
