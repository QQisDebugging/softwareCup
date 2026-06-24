insert into student_profiles (
    id, student_name, major, current_level, learning_goal, preferences, constraints_text, dialogue_summary, created_at, updated_at
)
select
    '30000000-0000-0000-0000-000000000001',
    '张同学',
    '软件工程',
    '大二，Java 基础薄弱，刚接触 Spring Boot',
    '两周内掌握 Spring Boot Controller、Service、Repository 分层，并能完成一个资料上传与课程资源生成接口',
    '喜欢图解、流程图、短练习和项目化案例；希望先看核心概念，再做分层练习',
    '每天可学习 45 分钟，晚间学习为主，期望系统自动安排复习和测评',
    '学生说明自己 Java 基础一般，最困惑 Controller 为什么不直接写复杂业务逻辑，希望系统根据课程 PPT、教材章节和个人薄弱点生成讲义、练习、思维导图和实操任务。',
    current_timestamp,
    current_timestamp
where not exists (select 1 from student_profiles where id = '30000000-0000-0000-0000-000000000001');

insert into profile_dimensions (
    id, profile_id, dimension_key, dimension_name, dimension_value, evidence, confidence_score, source, created_at, updated_at
)
select * from (
    select '31000000-0000-0000-0000-000000000001' as id, '30000000-0000-0000-0000-000000000001' as profile_id, 'KNOWLEDGE_FOUNDATION' as dimension_key, '知识基础' as dimension_name, 'Java 语法能完成课堂练习，但 Web 分层、依赖注入和数据库访问还不稳定。' as dimension_value, '来自对话式画像：学生明确提到 Java 基础薄弱、刚接触 Spring Boot。' as evidence, 0.86 as confidence_score, 'seed_dialogue_profile' as source, current_timestamp as created_at, current_timestamp as updated_at
    union all select '31000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000001', 'COGNITIVE_STYLE', '认知风格', '先图解再代码的视觉化学习者，适合流程图、接口调用链和分层案例。', '来自偏好描述：喜欢图解、流程图和项目化案例。', 0.82, 'seed_dialogue_profile', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000001', 'LEARNING_GOAL', '学习目标', '两周内完成 Spring Boot 分层理解，并能独立实现资料上传与课程资源生成接口。', '来自学生学习目标。', 0.90, 'seed_dialogue_profile', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000004', '30000000-0000-0000-0000-000000000001', 'ERROR_PRONE_POINTS', '易错点偏好', '容易把 Controller、Service、Repository 职责混在一起，接口异常处理和数据落库验证不足。', '来自最近一次测评与学习事件。', 0.78, 'assessment_analyzer', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000005', '30000000-0000-0000-0000-000000000001', 'RESOURCE_PREFERENCE', '资源偏好', '优先推送讲解文档、思维导图、分层练习、短视频脚本和实操案例。', '来自对话偏好和资源点击行为。', 0.84, 'recommendation_agent', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000006', '30000000-0000-0000-0000-000000000001', 'TIME_CONSTRAINT', '时间约束', '每天 45 分钟，晚间学习，适合 15-25 分钟颗粒度的路径节点。', '来自学生时间约束。', 0.88, 'seed_dialogue_profile', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000007', '30000000-0000-0000-0000-000000000001', 'MASTERY_WEAKNESS', '薄弱掌握点', 'Controller 分层、Repository 数据访问和异常处理需要优先补齐。', '来自 6/10 练习得分和答疑问题聚类。', 0.76, 'learning_loop_analyzer', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000008', '30000000-0000-0000-0000-000000000001', 'LEARNING_BEHAVIOR_PATTERN', '学习行为模式', '偏好先浏览讲义再做题，遇到抽象分层概念时会主动提问。', '来自资源停留时长、练习提交和答疑记录。', 0.74, 'learning_event_analyzer', current_timestamp, current_timestamp
) seed
where not exists (
    select 1 from profile_dimensions existing
    where existing.profile_id = seed.profile_id and existing.dimension_key = seed.dimension_key
);

insert into profile_history (
    id, profile_id, event_type, dimension_key, previous_value, new_value, evidence, source, created_at
)
select * from (
    select '32000000-0000-0000-0000-000000000001' as id, '30000000-0000-0000-0000-000000000001' as profile_id, 'DIMENSION_CREATED' as event_type, 'KNOWLEDGE_FOUNDATION' as dimension_key, null as previous_value, 'Java 语法能完成课堂练习，但 Web 分层、依赖注入和数据库访问还不稳定。' as new_value, '对话式画像初始化。' as evidence, 'seed_dialogue_profile' as source, current_timestamp as created_at
    union all select '32000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000001', 'DIMENSION_UPDATED', 'MASTERY_WEAKNESS', '初始未知', 'Controller 分层、Repository 数据访问和异常处理需要优先补齐。', '练习测评和智能答疑触发画像随学随新。', 'learning_loop_analyzer', current_timestamp
    union all select '32000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000001', 'DIMENSION_UPDATED', 'RESOURCE_PREFERENCE', '讲义优先', '讲义、思维导图、练习、视频脚本和实操案例组合推送。', '学生连续打开讲义和实操任务，反馈图解更容易理解。', 'recommendation_agent', current_timestamp
) seed
where not exists (select 1 from profile_history existing where existing.id = seed.id);

insert into learning_paths (
    id, student_profile_id, course_id, title, status, created_at, updated_at
)
select
    '40000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000002',
    '张同学的 Spring Boot 分层补齐路径',
    'ACTIVE',
    current_timestamp,
    current_timestamp
where not exists (select 1 from learning_paths where id = '40000000-0000-0000-0000-000000000001');

insert into learning_path_nodes (
    id, path_id, node_order, knowledge_point, resource_id, estimated_minutes, prerequisite_node_id, status, created_at, updated_at
)
select * from (
    select '41000000-0000-0000-0000-000000000001' as id, '40000000-0000-0000-0000-000000000001' as path_id, 1 as node_order, 'Controller 与 Service 分层职责' as knowledge_point, '20000000-0000-0000-0000-000000000002' as resource_id, 18 as estimated_minutes, null as prerequisite_node_id, 'READY' as status, current_timestamp as created_at, current_timestamp as updated_at
    union all select '41000000-0000-0000-0000-000000000002', '40000000-0000-0000-0000-000000000001', 2, 'Repository 数据访问与实体建模', '20000000-0000-0000-0000-000000000002', 22, '41000000-0000-0000-0000-000000000001', 'READY', current_timestamp, current_timestamp
    union all select '41000000-0000-0000-0000-000000000003', '40000000-0000-0000-0000-000000000001', 3, '资料上传接口异常处理', '20000000-0000-0000-0000-000000000002', 20, '41000000-0000-0000-0000-000000000002', 'WAITING', current_timestamp, current_timestamp
    union all select '41000000-0000-0000-0000-000000000004', '40000000-0000-0000-0000-000000000001', 4, '上传资料到课程草稿的实操项目', '20000000-0000-0000-0000-000000000002', 35, '41000000-0000-0000-0000-000000000003', 'LOCKED', current_timestamp, current_timestamp
) seed
where not exists (select 1 from learning_path_nodes existing where existing.id = seed.id);

insert into resource_recommendations (
    id, student_profile_id, course_id, resource_id, reason, priority_score, status, created_at
)
select * from (
    select '42000000-0000-0000-0000-000000000001' as id, '30000000-0000-0000-0000-000000000001' as student_profile_id, '10000000-0000-0000-0000-000000000002' as course_id, '20000000-0000-0000-0000-000000000002' as resource_id, '学生在 Controller 分层和资料上传接口上暴露薄弱点，优先推送项目化实操任务。' as reason, 0.94 as priority_score, 'PUSHED' as status, current_timestamp as created_at
    union all select '42000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', '需要理解画像诊断到资源生成的整体流程，推荐先看流程说明。', 0.86, 'PUSHED', current_timestamp
    union all select '42000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000003', '学生需要用短测验验证基础概念掌握度，推荐过程评价练习。', 0.78, 'QUEUED', current_timestamp
) seed
where not exists (select 1 from resource_recommendations existing where existing.id = seed.id);

insert into learning_events (
    id, student_profile_id, course_id, resource_id, event_type, duration_seconds, feedback_score, event_payload, topic, payload_json, created_at
)
select * from (
    select '43000000-0000-0000-0000-000000000001' as id, '30000000-0000-0000-0000-000000000001' as student_profile_id, '10000000-0000-0000-0000-000000000002' as course_id, '20000000-0000-0000-0000-000000000002' as resource_id, 'RESOURCE_VIEW' as event_type, 640 as duration_seconds, 4 as feedback_score, '{"note":"完整阅读 Spring Boot REST API 实训任务"}' as event_payload, 'Spring Boot REST API' as topic, '{"durationSeconds":640,"feedbackScore":4,"device":"web"}' as payload_json, current_timestamp as created_at
    union all select '43000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000002', 'TUTORING_QUESTION', 180, 5, '{"question":"Controller 为什么不直接写复杂业务逻辑？"}', 'Controller 分层', '{"question":"Controller 为什么不直接写复杂业务逻辑？","resolved":true}', current_timestamp
    union all select '43000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000002', 'QUIZ_SUBMIT', 420, 3, '{"score":6,"maxScore":10}', 'Repository 数据访问', '{"score":6,"maxScore":10,"weakPoints":["Repository 数据访问","异常处理"]}', current_timestamp
) seed
where not exists (select 1 from learning_events existing where existing.id = seed.id);

insert into quiz_attempts (
    id, student_profile_id, course_id, resource_id, topic, score, max_score, correct_count, total_count, weak_points, mastery_level, questions_json, answers_json, grading_json, submitted_at, created_at
)
select
    '44000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000002',
    '20000000-0000-0000-0000-000000000002',
    'Spring Boot Controller 与 REST API',
    6,
    10,
    6,
    10,
    'Repository 数据访问、异常处理、DTO 边界',
    '需要巩固',
    '[{"type":"single","stem":"Controller 层最适合承担哪类职责？"},{"type":"judge","stem":"Repository 可以直接处理复杂业务流程。"}]',
    '[{"answer":"接收请求并调用 Service"},{"answer":"错误"}]',
    '{"summary":"能识别基础分层，但对 Repository 边界和异常处理掌握不稳。","nextActions":["补看分层职责图解","完成资料上传接口实操"]}',
    current_timestamp,
    current_timestamp
where not exists (select 1 from quiz_attempts where id = '44000000-0000-0000-0000-000000000001');

insert into knowledge_mastery (
    id, student_profile_id, course_id, knowledge_point, mastery_score, evidence_summary, updated_at
)
select * from (
    select '45000000-0000-0000-0000-000000000001' as id, '30000000-0000-0000-0000-000000000001' as student_profile_id, '10000000-0000-0000-0000-000000000002' as course_id, 'Controller 分层' as knowledge_point, 0.72 as mastery_score, '答疑后能解释 Controller 不应承载复杂业务逻辑。' as evidence_summary, current_timestamp as updated_at
    union all select '45000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002', 'Service 业务逻辑', 0.68, '练习中能把核心业务放入 Service，但参数校验边界还需巩固。', current_timestamp
    union all select '45000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002', 'Repository 数据访问', 0.48, '测评暴露 Repository 与业务逻辑混用风险。', current_timestamp
    union all select '45000000-0000-0000-0000-000000000004', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002', '文件上传异常处理', 0.55, '能完成基础上传，但对空文件、路径安全和解析失败兜底不稳定。', current_timestamp
) seed
where not exists (select 1 from knowledge_mastery existing where existing.id = seed.id);

insert into evaluation_reports (
    id, student_profile_id, course_id, report_summary, overall_score, strengths, weaknesses, recommendation_strategy, created_at
)
select
    '46000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000002',
    '张同学已完成 Spring Boot REST API 实训任务阅读和一次分层测评，当前整体掌握度 63%。系统建议继续推送 Repository 数据访问、异常处理和上传接口实操任务。',
    0.63,
    '学习目标明确，愿意通过答疑澄清 Controller 与 Service 边界；对项目化案例反馈较好。',
    'Repository 数据访问、DTO 边界和异常处理仍是高风险点，测评正确率 6/10。',
    '下一轮优先推送：1. 分层职责图解；2. 文件上传异常处理练习；3. 资料上传到课程草稿的实操项目；4. 完成后再次短测并更新画像。',
    current_timestamp
where not exists (select 1 from evaluation_reports where id = '46000000-0000-0000-0000-000000000001');

insert into learning_paths (
    id, student_profile_id, course_id, title, status, created_at, updated_at
)
select
    '40000000-0000-0000-0000-000000000002',
    '30000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000001',
    '张同学的 AI 个性化学习智能体实践路径',
    'ACTIVE',
    current_timestamp,
    current_timestamp
where not exists (select 1 from learning_paths where id = '40000000-0000-0000-0000-000000000002');

insert into learning_path_nodes (
    id, path_id, node_order, knowledge_point, resource_id, estimated_minutes, prerequisite_node_id, status, created_at, updated_at
)
select * from (
    select '41000000-0000-0000-0000-000000000011' as id, '40000000-0000-0000-0000-000000000002' as path_id, 1 as node_order, '对话式学习画像构建' as knowledge_point, '20000000-0000-0000-0000-000000000001' as resource_id, 18 as estimated_minutes, null as prerequisite_node_id, 'READY' as status, current_timestamp as created_at, current_timestamp as updated_at
    union all select '41000000-0000-0000-0000-000000000012', '40000000-0000-0000-0000-000000000002', 2, '多智能体资源生成流程', '20000000-0000-0000-0000-000000000001', 24, '41000000-0000-0000-0000-000000000011', 'READY', current_timestamp, current_timestamp
    union all select '41000000-0000-0000-0000-000000000013', '40000000-0000-0000-0000-000000000002', 3, '学习路径规划与资源推送', '20000000-0000-0000-0000-000000000001', 22, '41000000-0000-0000-0000-000000000012', 'WAITING', current_timestamp, current_timestamp
    union all select '41000000-0000-0000-0000-000000000014', '40000000-0000-0000-0000-000000000002', 4, '学习效果评估与动态调整', '20000000-0000-0000-0000-000000000001', 20, '41000000-0000-0000-0000-000000000013', 'LOCKED', current_timestamp, current_timestamp
) seed
where not exists (select 1 from learning_path_nodes existing where existing.id = seed.id);

insert into knowledge_mastery (
    id, student_profile_id, course_id, knowledge_point, mastery_score, evidence_summary, updated_at
)
select * from (
    select '45000000-0000-0000-0000-000000000011' as id, '30000000-0000-0000-0000-000000000001' as student_profile_id, '10000000-0000-0000-0000-000000000001' as course_id, '学习画像' as knowledge_point, 0.78 as mastery_score, '能说明画像维度与资源推荐之间的关系。' as evidence_summary, current_timestamp as updated_at
    union all select '45000000-0000-0000-0000-000000000012', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', '资源生成', 0.66, '了解多智能体协作流程，但对安全审核和证据引用还需巩固。', current_timestamp
    union all select '45000000-0000-0000-0000-000000000013', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', '路径规划', 0.61, '能理解路径节点顺序，但还需要结合测评结果动态调整。', current_timestamp
    union all select '45000000-0000-0000-0000-000000000014', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', '学习评估', 0.58, '知道使用练习和学习事件作为证据，但评估指标解释不够稳定。', current_timestamp
) seed
where not exists (select 1 from knowledge_mastery existing where existing.id = seed.id);

insert into evaluation_reports (
    id, student_profile_id, course_id, report_summary, overall_score, strengths, weaknesses, recommendation_strategy, created_at
)
select
    '46000000-0000-0000-0000-000000000002',
    '30000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000001',
    '张同学已经理解画像驱动资源推荐的基本逻辑，但对多智能体安全审核、学习路径动态调整和效果评估指标仍需通过案例巩固。',
    0.67,
    '能把学生画像、课程资料和资源推荐联系起来，适合继续通过流程图和实操任务学习。',
    '多智能体协作中的证据引用、防幻觉审核和评估闭环解释还不够完整。',
    '下一轮优先推送：画像到资源生成流程说明、路径规划案例、短测题和一个完整的个性化资源生成实操任务。',
    current_timestamp
where not exists (select 1 from evaluation_reports where id = '46000000-0000-0000-0000-000000000002');

insert into tutoring_sessions (
    id, student_profile_id, course_id, question, answer, citations_json, follow_up_questions_json, learning_actions_json, profile_signals_json, mermaid_diagram, provider, fallback_used, created_at
)
select
    '47000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000002',
    'Controller 为什么不应该直接写复杂业务逻辑？',
    'Controller 更适合处理请求入口、参数接收、权限与响应封装；复杂业务逻辑放在 Service 中，可以让代码更容易测试、复用和维护。Repository 只负责数据访问，避免把业务规则散落到数据库访问层。',
    '[{"title":"Java Web 工程化实训","evidence":"课程大纲包含 Controller、Service、Repository 分层"}]',
    '["Service 层应该如何设计方法边界？","上传资料接口的异常应该在哪一层处理？"]',
    '["复习分层职责图解","完成上传接口异常处理练习","再做一次 5 题短测"]',
    '{"weakness":"Controller 分层","preference":"图解+实操案例","confidence":0.78}',
    'flowchart LR\nA[请求进入 Controller] --> B[参数校验与响应封装]\nB --> C[Service 执行业务规则]\nC --> D[Repository 访问数据]\nD --> C\nC --> B',
    'offline-resource-agent',
    true,
    current_timestamp
where not exists (select 1 from tutoring_sessions where id = '47000000-0000-0000-0000-000000000001');
