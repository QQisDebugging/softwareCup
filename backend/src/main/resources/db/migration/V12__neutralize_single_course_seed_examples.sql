update courses
set title = '工程实践与项目开发',
    department = '项目制课程与工程训练',
    description = '围绕课程资料导入、项目任务拆解、过程评价和成果复盘组织学习，适合作为学生自建课或教师班级课的通用工程实践样本。',
    syllabus_json = '{"weeks":[{"week":1,"topic":"项目背景与资料准备"},{"week":2,"topic":"任务拆解与方案设计"},{"week":3,"topic":"实践推进与问题诊断"},{"week":4,"topic":"成果提交与复盘"},{"week":5,"topic":"质量检查与同伴互评"},{"week":6,"topic":"学习证据沉淀"}],"knowledgePoints":["项目背景","任务流程","资料整理","成果要求","质量检查","复盘改进"]}',
    updated_at = current_timestamp
where id = '10000000-0000-0000-0000-000000000002';

update learning_resources
set title = '课程项目实训任务',
    content = '# 课程项目实训任务

围绕当前课程资料完成一个综合任务：明确任务目标、整理资料依据、拆分关键步骤、提交成果说明，并把练习、答疑和测评证据回写到学习画像。'
where id = '20000000-0000-0000-0000-000000000002';

update student_profiles
set major = '课程方向待填写',
    current_level = '已完成课程导入，基础水平待由对话、测评和学习事件确认。',
    learning_goal = '围绕当前课程完成阶段学习目标，并形成可追踪的学习路径、资源偏好和薄弱点记录。',
    preferences = '喜欢先看结构化讲解，再完成练习、案例或项目任务。',
    constraints_text = '每天可学习 45 分钟，适合短任务、阶段测评和周末综合练习。',
    dialogue_summary = '学生希望围绕当前课程补齐基础，主要困难集中在概念关系、步骤迁移和综合应用表达，偏好结构图、例题拆解和项目化任务。',
    updated_at = current_timestamp
where id = '30000000-0000-0000-0000-000000000001';

update profile_dimensions
set dimension_value = '能完成部分课堂练习，但核心概念关系、步骤迁移和综合应用还不稳定。',
    evidence = '来自对话式画像：学生希望围绕当前课程补齐基础，并说明概念关系和做题步骤不够清楚。',
    updated_at = current_timestamp
where id = '31000000-0000-0000-0000-000000000001';

update profile_dimensions
set dimension_value = '先看结构图和例题，再完成练习或项目任务，适合图解、案例和短测结合。',
    evidence = '来自偏好描述：喜欢结构图、例题拆解和项目化任务。',
    updated_at = current_timestamp
where id = '31000000-0000-0000-0000-000000000002';

update profile_dimensions
set dimension_value = '两周内完成当前章节核心知识点理解，并能在综合任务中正确应用。',
    evidence = '来自学生学习目标。',
    updated_at = current_timestamp
where id = '31000000-0000-0000-0000-000000000003';

update profile_dimensions
set dimension_value = '容易在核心概念辨析、步骤迁移和综合题表达上出错，需要结合测评持续补齐。',
    evidence = '来自最近一次测评与学习事件。',
    updated_at = current_timestamp
where id = '31000000-0000-0000-0000-000000000004';

update profile_dimensions
set dimension_value = '核心概念、步骤迁移和综合应用需要优先补齐。',
    evidence = '来自练习得分和答疑问题聚类。',
    updated_at = current_timestamp
where id = '31000000-0000-0000-0000-000000000007';

update profile_history
set new_value = '能完成部分课堂练习，但核心概念关系、步骤迁移和综合应用还不稳定。'
where id = '32000000-0000-0000-0000-000000000001';

update profile_history
set new_value = '核心概念、步骤迁移和综合应用需要优先补齐。',
    evidence = '练习测评和智能答疑触发画像随学随新。'
where id = '32000000-0000-0000-0000-000000000002';

update learning_paths
set title = '张同学的当前课程补齐路径',
    updated_at = current_timestamp
where id = '40000000-0000-0000-0000-000000000001';

update learning_path_nodes
set knowledge_point = '核心概念关系'
where id = '41000000-0000-0000-0000-000000000001';

update learning_path_nodes
set knowledge_point = '步骤迁移与方法选择'
where id = '41000000-0000-0000-0000-000000000002';

update learning_path_nodes
set knowledge_point = '综合题表达与证据引用'
where id = '41000000-0000-0000-0000-000000000003';

update learning_path_nodes
set knowledge_point = '课程项目综合任务'
where id = '41000000-0000-0000-0000-000000000004';

update resource_recommendations
set reason = '学生在当前知识点练习和综合任务上暴露薄弱点，优先推送项目化实操任务。'
where id = '42000000-0000-0000-0000-000000000001';

update learning_events
set event_payload = '{"note":"完整阅读课程项目实训任务"}',
    topic = '当前章节核心知识点',
    payload_json = '{"durationSeconds":640,"feedbackScore":4,"device":"web"}'
where id = '43000000-0000-0000-0000-000000000001';

update learning_events
set event_payload = '{"question":"这个知识点和前后章节有什么关系？"}',
    topic = '概念关系',
    payload_json = '{"question":"这个知识点和前后章节有什么关系？","resolved":true}'
where id = '43000000-0000-0000-0000-000000000002';

update learning_events
set topic = '步骤迁移',
    payload_json = '{"score":6,"maxScore":10,"weakPoints":["核心概念辨析","步骤迁移"]}'
where id = '43000000-0000-0000-0000-000000000003';

update quiz_attempts
set topic = '当前章节核心知识点',
    weak_points = '核心概念辨析、步骤迁移、综合应用',
    questions_json = '[{"type":"single","stem":"当前知识点最适合先掌握哪类关系？"},{"type":"judge","stem":"只记结论就可以稳定完成所有综合题。"}]',
    answers_json = '[{"answer":"概念关系与适用条件"},{"answer":"错误"}]',
    grading_json = '{"summary":"能识别基础概念，但对迁移应用和综合表达掌握不稳。","nextActions":["补看概念关系图解","完成综合应用练习"]}'
where id = '44000000-0000-0000-0000-000000000001';

update knowledge_mastery
set knowledge_point = '核心概念关系',
    evidence_summary = '答疑后能解释当前知识点与前后章节的关系。'
where id = '45000000-0000-0000-0000-000000000001';

update knowledge_mastery
set knowledge_point = '步骤迁移',
    evidence_summary = '练习中能完成基本步骤，但复杂情境迁移还需巩固。'
where id = '45000000-0000-0000-0000-000000000002';

update knowledge_mastery
set knowledge_point = '综合应用表达',
    evidence_summary = '测评暴露综合题表达和证据引用不足。'
where id = '45000000-0000-0000-0000-000000000003';

update knowledge_mastery
set knowledge_point = '项目任务复盘',
    evidence_summary = '能提交基础任务，但对质量检查和复盘改进不稳定。'
where id = '45000000-0000-0000-0000-000000000004';

update evaluation_reports
set report_summary = '张同学已完成当前课程项目任务阅读和一次阶段测评，当前整体掌握度 63%。系统建议继续推送概念关系、步骤迁移和综合应用练习。',
    strengths = '学习目标明确，愿意通过答疑澄清概念关系；对图解和项目化案例反馈较好。',
    weaknesses = '核心概念辨析、步骤迁移和综合表达仍是高风险点，测评正确率 6/10。',
    recommendation_strategy = '下一轮优先推送：1. 概念关系图解；2. 综合应用练习；3. 项目任务复盘；4. 完成后再次短测并更新画像。'
where id = '46000000-0000-0000-0000-000000000001';

update tutoring_sessions
set question = '这个知识点和前后章节有什么关系？',
    answer = '可以先看它解决的问题，再看前置概念提供了哪些条件，最后用一道综合题检查是否能迁移应用。学习时建议按“概念关系、适用条件、例题步骤、错因复盘”四步推进。',
    citations_json = '[{"title":"当前课程资料","evidence":"课程资料包含核心概念、例题步骤和综合任务"}]',
    follow_up_questions_json = '["这个知识点常见错因是什么？","我应该先做哪类练习？"]',
    learning_actions_json = '["复习概念关系图解","完成一道综合应用题","记录错因并更新画像"]',
    profile_signals_json = '{"weakness":"概念迁移","preference":"图解+例题","confidence":0.78}',
    mermaid_diagram = 'flowchart LR\nA[前置概念] --> B[当前知识点]\nB --> C[例题步骤]\nC --> D[综合应用]\nD --> E[错因复盘]'
where id = '47000000-0000-0000-0000-000000000001';
