alter table learning_resources add column review_status varchar(40);
alter table learning_resources add column published_at timestamp;
alter table learning_resources add column published_by varchar(80);
alter table learning_resources add column publish_note text;

update learning_resources
set
    review_status = 'PUBLISHED',
    published_at = coalesce(updated_at, created_at),
    published_by = '课程教师',
    publish_note = '种子课程资源已完成教师确认，可供学生学习。'
where review_status is null;

alter table learning_resources alter column review_status set not null;

create index idx_resources_course_review on learning_resources(course_id, review_status);
create index idx_resources_source_task on learning_resources(source_task_id);
