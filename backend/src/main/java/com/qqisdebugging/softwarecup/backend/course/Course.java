package com.qqisdebugging.softwarecup.backend.course;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "courses")
public class Course {
    @Id
    @Column(length = 36)
    private String id;

    @Column(nullable = false, length = 160)
    private String title;

    @Column(nullable = false, length = 160)
    private String department;

    @Column(nullable = false, columnDefinition = "text")
    private String description;

    @Column(nullable = false)
    private Integer creditHours;

    @Column(nullable = false, columnDefinition = "text")
    private String syllabusJson;

    @Column(nullable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private Instant updatedAt;

    protected Course() {
    }

    public Course(String title, String department, String description, Integer creditHours, String syllabusJson) {
        this.title = title;
        this.department = department;
        this.description = description;
        this.creditHours = creditHours;
        this.syllabusJson = syllabusJson;
    }

    @jakarta.persistence.PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID().toString();
        }
        Instant now = Instant.now();
        createdAt = now;
        updatedAt = now;
    }

    @jakarta.persistence.PreUpdate
    void preUpdate() {
        updatedAt = Instant.now();
    }

    public String getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public String getDepartment() {
        return department;
    }

    public String getDescription() {
        return description;
    }

    public Integer getCreditHours() {
        return creditHours;
    }

    public String getSyllabusJson() {
        return syllabusJson;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }
}
