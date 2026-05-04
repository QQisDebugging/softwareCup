create table student_profiles (
    id varchar(36) primary key,
    student_name varchar(80) not null,
    major varchar(120) not null,
    current_level varchar(80) not null,
    learning_goal text not null,
    preferences text not null,
    constraints_text text not null,
    dialogue_summary text not null,
    created_at timestamp not null,
    updated_at timestamp not null
);

create table courses (
    id varchar(36) primary key,
    title varchar(160) not null,
    department varchar(160) not null,
    description text not null,
    credit_hours integer not null,
    syllabus_json text not null,
    created_at timestamp not null,
    updated_at timestamp not null
);

create table learning_resources (
    id varchar(36) primary key,
    course_id varchar(36) not null references courses(id),
    source_task_id varchar(36),
    title varchar(180) not null,
    resource_type varchar(60) not null,
    modality varchar(60) not null,
    target_level varchar(80) not null,
    estimated_minutes integer not null,
    content text not null,
    created_at timestamp not null,
    updated_at timestamp not null
);

create table generation_tasks (
    id varchar(36) primary key,
    student_profile_id varchar(36) references student_profiles(id),
    course_id varchar(36) references courses(id),
    task_type varchar(80) not null,
    status varchar(40) not null,
    topic varchar(180) not null,
    prompt text not null,
    result_summary text,
    error_message text,
    created_resource_id varchar(36),
    created_at timestamp not null,
    updated_at timestamp not null
);

create table uploaded_assets (
    id varchar(36) primary key,
    original_filename varchar(255) not null,
    content_type varchar(120) not null,
    size_bytes bigint not null,
    storage_path text not null,
    purpose varchar(120) not null,
    created_at timestamp not null
);

create index idx_resources_course_id on learning_resources(course_id);
create index idx_tasks_status on generation_tasks(status);
create index idx_tasks_student_course on generation_tasks(student_profile_id, course_id);
