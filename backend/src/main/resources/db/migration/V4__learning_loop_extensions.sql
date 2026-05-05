alter table learning_events add column if not exists topic varchar(180);
alter table learning_events add column if not exists payload_json text not null default '{}';

alter table quiz_attempts add column if not exists topic varchar(180) not null default 'general-assessment';
alter table quiz_attempts add column if not exists mastery_level varchar(80) not null default 'ungraded';
alter table quiz_attempts add column if not exists questions_json text not null default '[]';
alter table quiz_attempts add column if not exists answers_json text not null default '[]';
alter table quiz_attempts add column if not exists grading_json text not null default '{}';
alter table quiz_attempts add column if not exists created_at timestamp not null default current_timestamp;

create table if not exists tutoring_sessions (
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

create index if not exists idx_tutoring_sessions_profile_time
    on tutoring_sessions(student_profile_id, created_at desc);

create index if not exists idx_quiz_attempts_profile_time
    on quiz_attempts(student_profile_id, created_at desc);
