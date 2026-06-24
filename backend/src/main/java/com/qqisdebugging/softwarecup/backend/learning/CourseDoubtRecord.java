package com.qqisdebugging.softwarecup.backend.learning;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

/**
 * 课程疑惑记录：学生在某课程内部 AI 助教对话中产生的每一轮疑问与总结，
 * 按 (studentProfileId, courseId) 沉淀为该用户该课程专属的疑惑文档，
 * 可用于学习画像更新与反馈教师。
 */
@Entity
@Table(name = "course_doubt_records")
public class CourseDoubtRecord {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 36)
    private String studentProfileId;

    @Column(nullable = false, length = 36)
    private String courseId;

    @Column(length = 36)
    private String conversationId;

    @Column(nullable = false, columnDefinition = "text")
    private String question;

    @Column(nullable = false, columnDefinition = "text")
    private String summary;

    @Column(nullable = false, columnDefinition = "text")
    private String signalsJson;

    @Column(nullable = false)
    private Instant createdAt;

    protected CourseDoubtRecord() {
    }

    public CourseDoubtRecord(
            String studentProfileId,
            String courseId,
            String conversationId,
            String question,
            String summary,
            String signalsJson) {
        this.studentProfileId = studentProfileId;
        this.courseId = courseId;
        this.conversationId = conversationId;
        this.question = question;
        this.summary = summary;
        this.signalsJson = signalsJson;
    }

    @PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID().toString();
        }
        if (createdAt == null) {
            createdAt = Instant.now();
        }
    }

    public String getId() {
        return id;
    }

    public String getStudentProfileId() {
        return studentProfileId;
    }

    public String getCourseId() {
        return courseId;
    }

    public String getConversationId() {
        return conversationId;
    }

    public String getQuestion() {
        return question;
    }

    public String getSummary() {
        return summary;
    }

    public String getSignalsJson() {
        return signalsJson;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
