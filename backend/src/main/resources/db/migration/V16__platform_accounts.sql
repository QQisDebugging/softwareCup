create table if not exists platform_accounts (
    id varchar(36) primary key,
    username varchar(64) not null unique,
    password_hash varchar(128) not null,
    role varchar(20) not null,
    display_name varchar(80) not null,
    title varchar(80) not null,
    home varchar(240) not null,
    department varchar(160) not null,
    status varchar(20) not null,
    created_at timestamp not null,
    updated_at timestamp not null
);

insert into platform_accounts (
    id, username, password_hash, role, display_name, title, home, department, status, created_at, updated_at
)
select
    'student-zhang',
    'zhang.student',
    '0c65e8206c2a719cfb36563cf7d8bf84df7d802f603145cac0d6bdeadca58e5b',
    'student',
    '张同学',
    '学生',
    '个性化学习、自建课程与 AI 辅导',
    '软件工程 2024 级',
    'active',
    current_timestamp,
    current_timestamp
where not exists (select 1 from platform_accounts where username = 'zhang.student');

insert into platform_accounts (
    id, username, password_hash, role, display_name, title, home, department, status, created_at, updated_at
)
select
    'teacher-li',
    'li.teacher',
    '5faa480061ea56890bc2e0b903f893f133c07701871c1beb1b9a91f094658c0b',
    'teacher',
    '李老师',
    '课程教师',
    '课程资源、班级学情与智能体审核',
    '人工智能与教学实训教研组',
    'active',
    current_timestamp,
    current_timestamp
where not exists (select 1 from platform_accounts where username = 'li.teacher');

create index if not exists idx_platform_accounts_role_status
    on platform_accounts(role, status);
