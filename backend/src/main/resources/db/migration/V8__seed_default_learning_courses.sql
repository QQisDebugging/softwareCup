insert into courses (
    id, title, department, description, credit_hours, syllabus_json, created_at, updated_at
)
select
    '10000000-0000-0000-0000-000000000001',
    'AI 个性化学习智能体实践',
    '人工智能与教学实训',
    '围绕学生画像诊断、学习资源生成、学习路径规划、智能答疑和过程性评价组织课程，适合作为软件杯赛题的完整实践课程。',
    48,
    '{"weeks":[{"week":1,"topic":"学习画像与证据采集"},{"week":2,"topic":"课程知识库与资料解析"},{"week":3,"topic":"个性化资源生成"},{"week":4,"topic":"学习路径规划"},{"week":5,"topic":"智能答疑与引用依据"},{"week":6,"topic":"测评反馈与学情评价"}],"knowledgePoints":["学习画像","知识点抽取","资源生成","路径规划","智能答疑","过程评价"]}',
    current_timestamp,
    current_timestamp
where not exists (select 1 from courses where id = '10000000-0000-0000-0000-000000000001');

insert into courses (
    id, title, department, description, credit_hours, syllabus_json, created_at, updated_at
)
select
    '10000000-0000-0000-0000-000000000002',
    'Java Web 工程化实训',
    '计算机科学与技术',
    '以 Spring Boot、REST API、数据库建模、文件上传和部署测试为主线，支撑学生按资料自建课程并生成实训资源。',
    64,
    '{"weeks":[{"week":1,"topic":"Spring Boot 项目结构"},{"week":2,"topic":"Controller 与 Service 分层"},{"week":3,"topic":"Repository 与数据库建模"},{"week":4,"topic":"REST API 设计"},{"week":5,"topic":"文件上传与资料解析"},{"week":6,"topic":"测试、部署与质量保障"}],"knowledgePoints":["Spring Boot","REST API","数据库建模","文件上传","课程资料解析","工程化测试"]}',
    current_timestamp,
    current_timestamp
where not exists (select 1 from courses where id = '10000000-0000-0000-0000-000000000002');

insert into courses (
    id, title, department, description, credit_hours, syllabus_json, created_at, updated_at
)
select
    '10000000-0000-0000-0000-000000000003',
    '大学计算机基础自适应训练',
    '通识教育与数字素养',
    '面向基础薄弱、目标差异较大的学生，展示画像诊断、薄弱点补齐、练习推荐和学习进度跟踪。',
    32,
    '{"weeks":[{"week":1,"topic":"计算机系统与网络基础"},{"week":2,"topic":"办公软件与数据处理"},{"week":3,"topic":"程序设计入门"},{"week":4,"topic":"AI 工具与信息安全"}],"knowledgePoints":["计算机基础","数据处理","程序设计入门","信息安全","学习诊断"]}',
    current_timestamp,
    current_timestamp
where not exists (select 1 from courses where id = '10000000-0000-0000-0000-000000000003');

insert into learning_resources (
    id, course_id, source_task_id, title, resource_type, modality, target_level, estimated_minutes, content, created_at, updated_at
)
select
    '20000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000001',
    null,
    '画像诊断到资源生成流程说明',
    'COURSE_EXPLANATION_DOCUMENT',
    '图文讲义',
    '进阶',
    18,
    '# 画像诊断到资源生成流程\n\n1. 汇总学生目标、偏好、约束和测评证据。\n2. 抽取课程知识点并建立课程上下文。\n3. 由智能体生成讲解文档、练习、思维导图和实操任务。\n4. 经过安全审核后推送到学习路径。',
    current_timestamp,
    current_timestamp
where not exists (select 1 from learning_resources where id = '20000000-0000-0000-0000-000000000001');

insert into learning_resources (
    id, course_id, source_task_id, title, resource_type, modality, target_level, estimated_minutes, content, created_at, updated_at
)
select
    '20000000-0000-0000-0000-000000000002',
    '10000000-0000-0000-0000-000000000002',
    null,
    'Spring Boot REST API 实训任务',
    'PRACTICE_CASE',
    '项目实操',
    '中级',
    35,
    '# Spring Boot REST API 实训任务\n\n完成课程资料上传接口，要求保存原始文件、记录课程归属、解析文本预览、抽取知识点，并返回可用于课程草稿的结构化 JSON。',
    current_timestamp,
    current_timestamp
where not exists (select 1 from learning_resources where id = '20000000-0000-0000-0000-000000000002');

insert into learning_resources (
    id, course_id, source_task_id, title, resource_type, modality, target_level, estimated_minutes, content, created_at, updated_at
)
select
    '20000000-0000-0000-0000-000000000003',
    '10000000-0000-0000-0000-000000000003',
    null,
    '智能答疑与过程评价练习',
    'QUIZ_PRACTICE',
    '练习测评',
    '基础',
    20,
    '# 智能答疑与过程评价练习\n\n围绕学生最近一次学习事件生成 5 道检查题，并把答题结果写入薄弱点、掌握度和下一步学习建议。',
    current_timestamp,
    current_timestamp
where not exists (select 1 from learning_resources where id = '20000000-0000-0000-0000-000000000003');
