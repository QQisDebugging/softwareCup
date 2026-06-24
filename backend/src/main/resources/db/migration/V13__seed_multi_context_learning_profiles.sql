insert into student_profiles (
    id, student_name, major, current_level, learning_goal, preferences, constraints_text, dialogue_summary, created_at, updated_at
)
select * from (
    select '30000000-0000-0000-0000-000000000002' as id,
           '李同学' as student_name,
           '数据处理与办公应用' as major,
           '能完成基础表格操作，但对公式组合、图表选择和数据解释不稳定。' as current_level,
           '一周内完成数据清洗、公式计算、图表表达和结论说明的完整练习。' as learning_goal,
           '偏好步骤清单、操作录屏脚本和即时练习反馈。' as preferences,
           '每天 30 分钟，适合拆成 10-15 分钟的小任务。' as constraints_text,
           '学生正在学习数据处理课程，主要困难是公式组合和图表解读，偏好步骤化讲解与短练习。' as dialogue_summary,
           current_timestamp as created_at,
           current_timestamp as updated_at
    union all
    select '30000000-0000-0000-0000-000000000003',
           '王同学',
           '通识基础与数字素养',
           '计算机基础概念较零散，能按步骤操作，但容易忘记概念边界和安全注意事项。',
           '两周内补齐计算机基础、信息安全和 AI 工具使用的核心概念。',
           '偏好生活化案例、概念卡片和低门槛小测。',
           '工作日只能学习 20 分钟，周末可完成一次综合复盘。',
           '学生需要补齐通识基础，主要卡点是概念混淆和应用场景判断，适合卡片化讲解和低压力测评。',
           current_timestamp,
           current_timestamp
    union all
    select '30000000-0000-0000-0000-000000000004',
           '陈同学',
           '项目制课程与工程训练',
           '能理解项目目标，但任务拆解、资料引用和成果复盘不够稳定。',
           '完成一个项目式课程任务，能够提交资料依据、过程记录和成果说明。',
           '偏好任务看板、案例拆解、阶段检查和教师反馈。',
           '每周三次集中学习，每次约 60 分钟。',
           '学生正在进行项目制课程训练，需要把资料、任务、产出和复盘串起来，适合看板式路径与过程证据提醒。',
           current_timestamp,
           current_timestamp
) seed
where not exists (select 1 from student_profiles existing where existing.id = seed.id);

insert into profile_dimensions (
    id, profile_id, dimension_key, dimension_name, dimension_value, evidence, confidence_score, source, created_at, updated_at
)
select * from (
    select '31000000-0000-0000-0000-000000000101' as id, '30000000-0000-0000-0000-000000000002' as profile_id, 'KNOWLEDGE_FOUNDATION' as dimension_key, '知识基础' as dimension_name, '基础表格操作可完成，公式组合、数据清洗和图表解释需要补强。' as dimension_value, '对话中明确提到会基础操作，但公式和图表解释容易卡住。' as evidence, 0.84 as confidence_score, 'multi_context_seed' as source, current_timestamp as created_at, current_timestamp as updated_at
    union all select '31000000-0000-0000-0000-000000000102', '30000000-0000-0000-0000-000000000002', 'COGNITIVE_STYLE', '认知风格', '适合按步骤清单推进，配合操作示例和即时反馈。', '偏好步骤清单和操作录屏脚本。', 0.80, 'multi_context_seed', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000103', '30000000-0000-0000-0000-000000000002', 'LEARNING_GOAL', '学习目标', '完成数据清洗、公式计算、图表表达和结论说明的完整练习。', '来自学生阶段目标。', 0.88, 'multi_context_seed', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000104', '30000000-0000-0000-0000-000000000002', 'MASTERY_WEAKNESS', '掌握短板', '公式嵌套、图表选择和结论表达需要优先补齐。', '来自测评和练习表现摘要。', 0.78, 'multi_context_seed', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000105', '30000000-0000-0000-0000-000000000002', 'TIME_CONSTRAINT', '时间约束', '每天 30 分钟，适合 10-15 分钟短任务。', '来自学生时间说明。', 0.86, 'multi_context_seed', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000201', '30000000-0000-0000-0000-000000000003', 'KNOWLEDGE_FOUNDATION', '知识基础', '计算机基础概念较零散，需要先建立概念卡片和场景判断。', '对话中提到容易忘记概念边界和安全注意事项。', 0.82, 'multi_context_seed', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000202', '30000000-0000-0000-0000-000000000003', 'COGNITIVE_STYLE', '认知风格', '适合生活化案例、概念卡片和低门槛小测。', '来自学习偏好描述。', 0.79, 'multi_context_seed', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000203', '30000000-0000-0000-0000-000000000003', 'LEARNING_GOAL', '学习目标', '补齐计算机基础、信息安全和 AI 工具使用的核心概念。', '来自学生目标描述。', 0.87, 'multi_context_seed', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000204', '30000000-0000-0000-0000-000000000003', 'ERROR_PRONE_POINTS', '易错点', '容易混淆概念边界，对信息安全场景判断不稳定。', '来自错题与答疑摘要。', 0.76, 'multi_context_seed', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000205', '30000000-0000-0000-0000-000000000003', 'TIME_CONSTRAINT', '时间约束', '工作日 20 分钟，周末完成一次综合复盘。', '来自学生时间说明。', 0.85, 'multi_context_seed', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000301', '30000000-0000-0000-0000-000000000004', 'KNOWLEDGE_FOUNDATION', '知识基础', '能理解项目目标，但任务拆解、资料引用和成果复盘不稳定。', '对话中提到项目目标能理解，但过程组织不稳。', 0.83, 'multi_context_seed', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000302', '30000000-0000-0000-0000-000000000004', 'COGNITIVE_STYLE', '认知风格', '适合任务看板、案例拆解、阶段检查和教师反馈。', '来自学习偏好描述。', 0.81, 'multi_context_seed', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000303', '30000000-0000-0000-0000-000000000004', 'LEARNING_GOAL', '学习目标', '完成项目式课程任务，提交资料依据、过程记录和成果说明。', '来自学生项目目标。', 0.89, 'multi_context_seed', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000304', '30000000-0000-0000-0000-000000000004', 'MASTERY_WEAKNESS', '掌握短板', '任务拆解、证据引用和复盘改进需要优先补齐。', '来自项目过程记录和教师反馈。', 0.77, 'multi_context_seed', current_timestamp, current_timestamp
    union all select '31000000-0000-0000-0000-000000000305', '30000000-0000-0000-0000-000000000004', 'TIME_CONSTRAINT', '时间约束', '每周三次集中学习，每次约 60 分钟。', '来自学生时间说明。', 0.86, 'multi_context_seed', current_timestamp, current_timestamp
) seed
where not exists (
    select 1 from profile_dimensions existing
    where existing.profile_id = seed.profile_id and existing.dimension_key = seed.dimension_key
);

insert into profile_history (
    id, profile_id, event_type, dimension_key, previous_value, new_value, evidence, source, created_at
)
select * from (
    select '32000000-0000-0000-0000-000000000101' as id, '30000000-0000-0000-0000-000000000002' as profile_id, 'DIMENSION_CREATED' as event_type, 'KNOWLEDGE_FOUNDATION' as dimension_key, null as previous_value, '公式组合、数据清洗和图表解释需要补强。' as new_value, '数据处理课程对话初始化。' as evidence, 'multi_context_seed' as source, current_timestamp as created_at
    union all select '32000000-0000-0000-0000-000000000201', '30000000-0000-0000-0000-000000000003', 'DIMENSION_CREATED', 'KNOWLEDGE_FOUNDATION', null, '计算机基础概念较零散，需要概念卡片和场景判断。', '通识基础课程对话初始化。', 'multi_context_seed', current_timestamp
    union all select '32000000-0000-0000-0000-000000000301', '30000000-0000-0000-0000-000000000004', 'DIMENSION_CREATED', 'KNOWLEDGE_FOUNDATION', null, '项目任务拆解、资料引用和成果复盘不稳定。', '项目制课程对话初始化。', 'multi_context_seed', current_timestamp
) seed
where not exists (select 1 from profile_history existing where existing.id = seed.id);
