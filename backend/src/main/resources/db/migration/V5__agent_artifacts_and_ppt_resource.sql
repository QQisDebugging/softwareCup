create table agent_artifacts (
    id varchar(36) primary key,
    student_profile_id varchar(36),
    course_id varchar(36),
    artifact_type varchar(80) not null,
    agent_endpoint varchar(160) not null,
    topic varchar(180),
    status varchar(80) not null,
    request_summary text not null,
    payload_json text not null,
    citations_json text not null,
    safety_summary text not null,
    trace_id varchar(120),
    latency_ms bigint,
    error_message text,
    created_at timestamp not null
);

create index idx_agent_artifacts_profile_time on agent_artifacts(student_profile_id, created_at desc);
create index idx_agent_artifacts_course_time on agent_artifacts(course_id, created_at desc);
create index idx_agent_artifacts_type_time on agent_artifacts(artifact_type, created_at desc);
create index idx_agent_artifacts_trace on agent_artifacts(trace_id);

insert into agent_definitions (
    id, agent_key, display_name, responsibility, input_contract, output_contract, enabled, sort_order, created_at
) values
('99999999-9999-9999-9999-999999999999', 'PPT_COURSEWARE_GENERATOR', 'PPT课件生成智能体', '将讲解文档、思维导图、练习与实操任务组织为课堂展示型课件和讲稿。', 'generated_resource + learning_path + profile', 'ppt_outline + teaching_script', true, 75, current_timestamp);
