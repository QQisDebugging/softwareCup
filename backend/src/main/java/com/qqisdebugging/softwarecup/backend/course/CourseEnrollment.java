package com.qqisdebugging.softwarecup.backend.course;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "course_enrollments")
public class CourseEnrollment {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 36)
    private String courseId;

    @Column(nullable = false, length = 36)
    private String studentProfileId;

    @Column(nullable = false, length = 40)
    private String status;

    @Column(nullable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private Instant updatedAt;

    protected CourseEnrollment() {
    }

    public CourseEnrollment(String courseId, String studentProfileId) {
        this.courseId = courseId;
        this.studentProfileId = studentProfileId;
        this.status = "ACTIVE";
    }

    @jakarta.persistence.PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID().toString();
        }
        if (status == null || status.isBlank()) {
            status = "ACTIVE";
        }
        Instant now = Instant.now();
        createdAt = now;
        updatedAt = now;
    }

    @jakarta.persistence.PreUpdate
    void preUpdate() {
        updatedAt = Instant.now();
    }

    public void activate() {
        status = "ACTIVE";
    }

    public String getId() {
        return id;
    }

    public String getCourseId() {
        return courseId;
    }

    public String getStudentProfileId() {
        return studentProfileId;
    }

    public String getStatus() {
        return status;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }
}
