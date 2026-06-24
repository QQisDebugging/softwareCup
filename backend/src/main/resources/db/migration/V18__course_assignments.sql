create table if not exists course_assignments (
    id varchar(36) primary key,
    course_id varchar(36) not null references courses(id),
    type varchar(20) not null,
    title varchar(200) not null,
    publisher varchar(80) not null,
    description text not null,
    deadline_label varchar(80),
    estimated_minutes integer not null,
    questions_json text not null,
    created_at timestamp not null,
    updated_at timestamp not null
);

create table if not exists assignment_submissions (
    id varchar(36) primary key,
    assignment_id varchar(36) not null references course_assignments(id) on delete cascade,
    student_profile_id varchar(36) not null,
    course_id varchar(36) not null,
    content text not null,
    answers_json text not null,
    score integer,
    total integer,
    submitted_at timestamp not null,
    constraint uq_assignment_student unique (assignment_id, student_profile_id)
);

create index if not exists idx_course_assignments_course
    on course_assignments(course_id, created_at);

create index if not exists idx_assignment_submissions_student
    on assignment_submissions(student_profile_id, course_id);

-- 为首个示例课程预置一份测试和一份作业，便于演示课程任务功能
insert into course_assignments (id, course_id, type, title, publisher, description, deadline_label, estimated_minutes, questions_json, created_at, updated_at)
values (
    '20000000-0000-0000-0000-0000000000a1',
    '10000000-0000-0000-0000-000000000001',
    'quiz',
    'HTTP 协议与请求响应 章节短测',
    '李老师',
    '围绕本章核心知识点的限时小测，提交后自动评分。',
    '明天 23:59 截止',
    12,
    '[{"id":"q1","stem":"HTTP 请求中用于定位资源的部分是？","options":["请求方法","URL","请求头","响应体"],"answer":1},{"id":"q2","stem":"表示“资源未找到”的 HTTP 状态码是？","options":["200","301","404","500"],"answer":2},{"id":"q3","stem":"以下哪个方法通常用于提交表单数据？","options":["GET","POST","HEAD","OPTIONS"],"answer":1}]',
    current_timestamp,
    current_timestamp
);

insert into course_assignments (id, course_id, type, title, publisher, description, deadline_label, estimated_minutes, questions_json, created_at, updated_at)
values (
    '20000000-0000-0000-0000-0000000000a2',
    '10000000-0000-0000-0000-000000000001',
    'homework',
    '实验报告：智能体评估实验',
    '张老师',
    '完成本章实验并提交报告，说明实验设计、关键步骤、结果与改进方向。',
    '3 天后截止',
    45,
    '[]',
    current_timestamp,
    current_timestamp
);
