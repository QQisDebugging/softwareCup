alter table uploaded_assets add column course_id varchar(36);
alter table uploaded_assets add column uploader_role varchar(40) not null default 'student';
alter table uploaded_assets add column material_type varchar(80) not null default 'FILE';
alter table uploaded_assets add column parse_status varchar(40) not null default 'STORED';
alter table uploaded_assets add column parse_message text not null default '';
alter table uploaded_assets add column extracted_text_preview text not null default '';
alter table uploaded_assets add column knowledge_points_json text not null default '[]';
alter table uploaded_assets add column course_draft_json text not null default '{}';

create index idx_uploaded_assets_course_time on uploaded_assets(course_id, created_at desc);
