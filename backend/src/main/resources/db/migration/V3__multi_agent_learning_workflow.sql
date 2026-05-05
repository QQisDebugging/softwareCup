alter table generation_tasks add column progress_percent integer not null default 0;
alter table generation_tasks add column current_step varchar(160);

create table agent_definitions (
    id varchar(36) primary key,
    agent_key varchar(80) not null unique,
    display_name varchar(120) not null,
    responsibility text not null,
    input_contract text not null,
    output_contract text not null,
    enabled boolean not null,
    sort_order integer not null,
    created_at timestamp not null
);

create table task_steps (
    id varchar(36) primary key,
    task_id varchar(36) not null references generation_tasks(id),
    agent_key varchar(80) not null,
    step_order integer not null,
    step_name varchar(120) not null,
    status varchar(40) not null,
    input_summary text,
    output_summary text,
    progress_percent integer not null,
    started_at timestamp,
    finished_at timestamp,
    duration_ms bigint,
    error_message text,
    created_at timestamp not null,
    updated_at timestamp not null
);

create table model_invocations (
    id varchar(36) primary key,
    task_id varchar(36) references generation_tasks(id),
    step_id varchar(36) references task_steps(id),
    provider varchar(80) not null,
    model_name varchar(120) not null,
    prompt_hash varchar(80) not null,
    prompt_summary text not null,
    latency_ms bigint,
    status varchar(40) not null,
    fallback_used boolean not null,
    error_message text,
    created_at timestamp not null
);

create table generation_audits (
    id varchar(36) primary key,
    task_id varchar(36) not null references generation_tasks(id),
    resource_id varchar(36),
    audit_type varchar(80) not null,
    status varchar(40) not null,
    evidence_summary text not null,
    reviewer_required boolean not null,
    created_at timestamp not null
);

create table learning_paths (
    id varchar(36) primary key,
    student_profile_id varchar(36) not null references student_profiles(id),
    course_id varchar(36) not null references courses(id),
    title varchar(180) not null,
    status varchar(40) not null,
    created_at timestamp not null,
    updated_at timestamp not null
);

create table learning_path_nodes (
    id varchar(36) primary key,
    path_id varchar(36) not null references learning_paths(id),
    node_order integer not null,
    knowledge_point varchar(180) not null,
    resource_id varchar(36),
    estimated_minutes integer not null,
    prerequisite_node_id varchar(36),
    status varchar(40) not null,
    created_at timestamp not null,
    updated_at timestamp not null
);

create table resource_recommendations (
    id varchar(36) primary key,
    student_profile_id varchar(36) not null references student_profiles(id),
    course_id varchar(36) not null references courses(id),
    resource_id varchar(36) not null references learning_resources(id),
    reason text not null,
    priority_score numeric(5,2) not null,
    status varchar(40) not null,
    created_at timestamp not null
);

create table learning_events (
    id varchar(36) primary key,
    student_profile_id varchar(36) not null references student_profiles(id),
    course_id varchar(36) not null references courses(id),
    resource_id varchar(36),
    event_type varchar(80) not null,
    duration_seconds integer,
    feedback_score integer,
    event_payload text,
    created_at timestamp not null
);

create table quiz_attempts (
    id varchar(36) primary key,
    student_profile_id varchar(36) not null references student_profiles(id),
    course_id varchar(36) not null references courses(id),
    resource_id varchar(36),
    score numeric(6,2) not null,
    max_score numeric(6,2) not null,
    correct_count integer not null,
    total_count integer not null,
    weak_points text,
    submitted_at timestamp not null
);

create table knowledge_mastery (
    id varchar(36) primary key,
    student_profile_id varchar(36) not null references student_profiles(id),
    course_id varchar(36) not null references courses(id),
    knowledge_point varchar(180) not null,
    mastery_score numeric(5,2) not null,
    evidence_summary text not null,
    updated_at timestamp not null,
    unique(student_profile_id, course_id, knowledge_point)
);

create table evaluation_reports (
    id varchar(36) primary key,
    student_profile_id varchar(36) not null references student_profiles(id),
    course_id varchar(36) not null references courses(id),
    report_summary text not null,
    overall_score numeric(5,2) not null,
    strengths text not null,
    weaknesses text not null,
    recommendation_strategy text not null,
    created_at timestamp not null
);

create index idx_task_steps_task_order on task_steps(task_id, step_order);
create index idx_model_invocations_task on model_invocations(task_id);
create index idx_generation_audits_task on generation_audits(task_id);
create index idx_learning_paths_profile_course on learning_paths(student_profile_id, course_id);
create index idx_path_nodes_path_order on learning_path_nodes(path_id, node_order);
create index idx_recommendations_profile on resource_recommendations(student_profile_id, created_at);
create index idx_learning_events_profile_time on learning_events(student_profile_id, created_at);
create index idx_quiz_attempts_profile_course on quiz_attempts(student_profile_id, course_id);
create index idx_mastery_profile_course on knowledge_mastery(student_profile_id, course_id);
create index idx_evaluation_reports_profile_course on evaluation_reports(student_profile_id, course_id, created_at);

insert into agent_definitions (
    id, agent_key, display_name, responsibility, input_contract, output_contract, enabled, sort_order, created_at
) values
('11111111-1111-1111-1111-111111111111', 'PROFILE_ANALYZER', '画像分析智能体', '解析学习画像维度，形成资源生成约束和个性化重点。', 'student_profile + profile_dimensions', '画像摘要、目标、偏好、约束', true, 10, current_timestamp),
('22222222-2222-2222-2222-222222222222', 'KNOWLEDGE_DIAGNOSTIC', '知识诊断智能体', '结合课程主题和画像推断先修基础、薄弱点和易错点。', 'course + topic + profile_summary', '知识诊断摘要、薄弱点', true, 20, current_timestamp),
('33333333-3333-3333-3333-333333333333', 'PATH_PLANNER', '路径规划智能体', '生成学习路径节点、前置依赖、预计时长和推荐策略。', 'diagnosis + syllabus', 'learning_path + path_nodes', true, 30, current_timestamp),
('44444444-4444-4444-4444-444444444444', 'DOCUMENT_GENERATOR', '文档生成智能体', '调用资源生成服务产出指定类型学习资源。', 'task_prompt + profile + course', 'learning_resource', true, 40, current_timestamp),
('55555555-5555-5555-5555-555555555555', 'QUIZ_GENERATOR', '题库生成智能体', '围绕当前知识点规划练习题、测验和反馈维度。', 'topic + diagnosis', 'quiz_blueprint', true, 50, current_timestamp),
('66666666-6666-6666-6666-666666666666', 'MIND_MAP_GENERATOR', '思维导图生成智能体', '抽取知识结构并规划思维导图节点。', 'course_topic + resource_summary', 'mind_map_outline', true, 60, current_timestamp),
('77777777-7777-7777-7777-777777777777', 'PRACTICE_CASE_GENERATOR', '实操案例生成智能体', '生成项目化实践任务和验收标准。', 'topic + student_goal', 'practice_case_outline', true, 70, current_timestamp),
('88888888-8888-8888-8888-888888888888', 'SAFETY_REVIEWER', '安全审核智能体', '检查引用证据、学术准确性、内容安全和人工复核需求。', 'generated_resource + course_evidence', 'generation_audit', true, 80, current_timestamp);
