create table if not exists learning_conversations (
    id varchar(36) primary key,
    student_profile_id varchar(36) not null references student_profiles(id),
    course_id varchar(36) not null references courses(id),
    title varchar(180) not null,
    archived boolean not null,
    archived_at timestamp,
    last_message_preview varchar(500),
    last_message_at timestamp,
    created_at timestamp not null,
    updated_at timestamp not null
);

create table if not exists learning_conversation_messages (
    id varchar(36) primary key,
    conversation_id varchar(36) not null references learning_conversations(id) on delete cascade,
    role varchar(20) not null,
    content text not null,
    citations_json text not null,
    follow_up_questions_json text not null,
    learning_actions_json text not null,
    profile_signals_json text not null,
    mermaid_diagram text not null,
    provider varchar(80),
    fallback_used boolean,
    created_at timestamp not null
);

create index if not exists idx_learning_conversations_profile_course
    on learning_conversations(student_profile_id, course_id, archived, updated_at);

create index if not exists idx_learning_conversation_messages_conversation
    on learning_conversation_messages(conversation_id, created_at, id);
