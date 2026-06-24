package com.qqisdebugging.softwarecup.backend.learning;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Instant;
import java.util.List;

public record CourseDoubtRecordResponse(
        String id,
        String studentProfileId,
        String courseId,
        String conversationId,
        String question,
        String summary,
        List<String> signals,
        Instant createdAt) {

    public static CourseDoubtRecordResponse from(CourseDoubtRecord record, ObjectMapper objectMapper) {
        List<String> signals = List.of();
        try {
            if (record.getSignalsJson() != null && !record.getSignalsJson().isBlank()) {
                signals = objectMapper.readValue(
                        record.getSignalsJson(),
                        objectMapper.getTypeFactory().constructCollectionType(List.class, String.class));
            }
        } catch (Exception ignored) {
            signals = List.of();
        }
        return new CourseDoubtRecordResponse(
                record.getId(),
                record.getStudentProfileId(),
                record.getCourseId(),
                record.getConversationId(),
                record.getQuestion(),
                record.getSummary(),
                signals,
                record.getCreatedAt());
    }
}
