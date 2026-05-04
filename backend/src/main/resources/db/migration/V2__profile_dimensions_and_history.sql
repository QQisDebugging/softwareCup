create table profile_dimensions (
    id varchar(36) primary key,
    profile_id varchar(36) not null references student_profiles(id),
    dimension_key varchar(80) not null,
    dimension_name varchar(120) not null,
    dimension_value text not null,
    evidence text not null,
    confidence_score numeric(5, 2) not null,
    source varchar(80) not null,
    created_at timestamp not null,
    updated_at timestamp not null,
    constraint uk_profile_dimension unique (profile_id, dimension_key)
);

create table profile_history (
    id varchar(36) primary key,
    profile_id varchar(36) not null references student_profiles(id),
    event_type varchar(80) not null,
    dimension_key varchar(80) not null,
    previous_value text,
    new_value text not null,
    evidence text not null,
    source varchar(80) not null,
    created_at timestamp not null
);

create index idx_profile_dimensions_profile on profile_dimensions(profile_id);
create index idx_profile_history_profile_time on profile_history(profile_id, created_at desc);
