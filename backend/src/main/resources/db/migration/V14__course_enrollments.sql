create table course_enrollments (
    id varchar(36) primary key,
    course_id varchar(36) not null references courses(id),
    student_profile_id varchar(36) not null references student_profiles(id),
    status varchar(40) not null,
    created_at timestamp not null,
    updated_at timestamp not null,
    constraint uq_course_enrollments_course_student unique (course_id, student_profile_id)
);

create index idx_course_enrollments_student_status
    on course_enrollments(student_profile_id, status);
