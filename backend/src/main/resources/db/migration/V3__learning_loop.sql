create table learning_events (
    id varchar(36) primary key,
    student_profile_id varchar(36) not null references student_profiles(id),
    course_id varchar(36) references courses(id),
    event_type varchar(80) not null,
    topic varchar(180),
    payload_json text not null,
    created_at timestamp not null
);

create table tutoring_sessions (
    id varchar(36) primary key,
    student_profile_id varchar(36) not null references student_profiles(id),
    course_id varchar(36) not null references courses(id),
    question text not null,
    answer text not null,
    citations_json text not null,
    follow_up_questions_json text not null,
    learning_actions_json text not null,
    profile_signals_json text not null,
    mermaid_diagram text not null,
    provider varchar(80) not null,
    fallback_used boolean not null,
    created_at timestamp not null
);

create table quiz_attempts (
    id varchar(36) primary key,
    student_profile_id varchar(36) not null references student_profiles(id),
    course_id varchar(36) not null references courses(id),
    topic varchar(180) not null,
    score integer not null,
    max_score integer not null,
    mastery_level varchar(80) not null,
    questions_json text not null,
    answers_json text not null,
    grading_json text not null,
    created_at timestamp not null
);

create index idx_learning_events_profile_time on learning_events(student_profile_id, created_at desc);
create index idx_tutoring_sessions_profile_time on tutoring_sessions(student_profile_id, created_at desc);
create index idx_quiz_attempts_profile_time on quiz_attempts(student_profile_id, created_at desc);
