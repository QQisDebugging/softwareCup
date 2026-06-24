create table if not exists course_doubt_records (
    id varchar(36) primary key,
    student_profile_id varchar(36) not null references student_profiles(id),
    course_id varchar(36) not null references courses(id),
    conversation_id varchar(36),
    question text not null,
    summary text not null,
    signals_json text not null,
    created_at timestamp not null
);

create index if not exists idx_course_doubt_records_profile_course
    on course_doubt_records(student_profile_id, course_id, created_at);

create index if not exists idx_course_doubt_records_course
    on course_doubt_records(course_id, created_at);
