-- Initial MoaView database schema for fixture-backed MVP data.
-- This schema intentionally supports mock/fixture ingestion only; do not add real scraping here.

create extension if not exists pgcrypto;

create type content_type as enum ('WEBTOON', 'WEBNOVEL');
create type creator_role as enum ('AUTHOR', 'ARTIST', 'ADAPTER', 'STUDIO', 'ORIGINAL_AUTHOR');
create type work_status as enum ('ONGOING', 'COMPLETED', 'HIATUS', 'UNKNOWN');
create type offer_source_type as enum ('FIXTURE', 'MOCK_CRAWLER', 'MANUAL_REVIEW', 'PLATFORM_PUBLIC');
create type promotion_type as enum (
    'instant_discount',
    'cashback',
    'bonus_currency',
    'free_episode_event',
    'bundle_discount'
);
create type coupon_discount_type as enum ('amount', 'percent');
create type price_confidence as enum ('confirmed', 'estimated', 'user_targeted_unknown');
create type crawl_status as enum ('success', 'failed', 'skipped');
create type merge_review_status as enum ('open', 'approved', 'rejected');

create table users_profile (
    user_id uuid primary key references auth.users(id) on delete cascade,
    display_name text,
    locale text not null default 'ko-KR',
    marketing_email_opt_in boolean not null default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table works (
    id uuid primary key default gen_random_uuid(),
    fixture_key text unique,
    title text not null,
    normalized_title text not null,
    content_type content_type not null,
    status work_status not null default 'UNKNOWN',
    description text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table creators (
    id uuid primary key default gen_random_uuid(),
    fixture_key text unique,
    display_name text not null,
    normalized_name text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table work_creators (
    work_id uuid not null references works(id) on delete cascade,
    creator_id uuid not null references creators(id) on delete cascade,
    role creator_role not null default 'AUTHOR',
    display_order integer not null default 0,
    primary key (work_id, creator_id, role)
);

create table platforms (
    id uuid primary key default gen_random_uuid(),
    code text not null unique,
    name text not null,
    homepage_url text,
    terms_url text,
    robots_url text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table platform_works (
    id uuid primary key default gen_random_uuid(),
    work_id uuid not null references works(id) on delete cascade,
    platform_id uuid not null references platforms(id) on delete cascade,
    platform_work_key text not null,
    title_on_platform text not null,
    platform_url text not null,
    is_available boolean not null default true,
    last_matched_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (platform_id, platform_work_key),
    unique (work_id, platform_id)
);

create table offers (
    id uuid primary key default gen_random_uuid(),
    platform_work_id uuid not null references platform_works(id) on delete cascade,
    currency_code char(3) not null default 'KRW',
    base_price integer not null check (base_price >= 0),
    free_episode_count integer not null default 0 check (free_episode_count >= 0),
    wait_free_available boolean not null default false,
    source_url text not null,
    source_type offer_source_type not null default 'FIXTURE',
    last_updated_at timestamptz not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (platform_work_id, source_type)
);

create table promotions (
    id uuid primary key default gen_random_uuid(),
    fixture_key text unique,
    platform_id uuid not null references platforms(id) on delete cascade,
    promotion_type promotion_type not null,
    title text not null,
    description text,
    discount_amount integer check (discount_amount is null or discount_amount >= 0),
    discount_percent numeric(5,2) check (discount_percent is null or discount_percent >= 0),
    cashback_percent numeric(5,2) check (cashback_percent is null or cashback_percent >= 0),
    bonus_currency_amount integer check (bonus_currency_amount is null or bonus_currency_amount >= 0),
    free_episode_count integer check (free_episode_count is null or free_episode_count >= 0),
    bundle_size integer check (bundle_size is null or bundle_size > 0),
    starts_at timestamptz,
    ends_at timestamptz,
    source_url text,
    source_type offer_source_type not null default 'FIXTURE',
    last_updated_at timestamptz not null default now(),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table coupons (
    id uuid primary key default gen_random_uuid(),
    fixture_key text unique,
    platform_id uuid not null references platforms(id) on delete cascade,
    coupon_code text,
    title text not null,
    discount_type coupon_discount_type not null,
    discount_value numeric(12,2) not null check (discount_value >= 0),
    min_purchase_amount integer check (min_purchase_amount is null or min_purchase_amount >= 0),
    max_discount_amount integer check (max_discount_amount is null or max_discount_amount >= 0),
    downloadable boolean not null default false,
    auto_issued boolean not null default false,
    code_required boolean not null default false,
    first_purchase_only boolean not null default false,
    user_targeted boolean not null default false,
    starts_at timestamptz,
    ends_at timestamptz,
    source_url text,
    source_type offer_source_type not null default 'FIXTURE',
    last_updated_at timestamptz not null default now(),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table computed_offer_prices (
    id uuid primary key default gen_random_uuid(),
    fixture_key text unique,
    offer_id uuid not null references offers(id) on delete cascade,
    coupon_id uuid references coupons(id) on delete set null,
    promotion_id uuid references promotions(id) on delete set null,
    applied_coupon_ids text[] not null default '{}'::text[],
    applied_promotion_ids text[] not null default '{}'::text[],
    currency_code char(3) not null default 'KRW',
    base_price integer not null check (base_price >= 0),
    instant_discounted_price integer not null check (instant_discounted_price >= 0),
    coupon_expected_price integer check (coupon_expected_price is null or coupon_expected_price >= 0),
    cashback_adjusted_price integer check (cashback_adjusted_price is null or cashback_adjusted_price >= 0),
    effective_price_for_sort integer not null check (effective_price_for_sort >= 0),
    price_confidence price_confidence not null,
    calculation_note text not null,
    calculated_at timestamptz not null default now(),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (offer_id, coupon_id, promotion_id)
);

create table favorites (
    user_id uuid not null references users_profile(user_id) on delete cascade,
    work_id uuid not null references works(id) on delete cascade,
    created_at timestamptz not null default now(),
    primary key (user_id, work_id)
);

create table notification_rules (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users_profile(user_id) on delete cascade,
    work_id uuid references works(id) on delete cascade,
    platform_id uuid references platforms(id) on delete cascade,
    max_effective_price integer check (max_effective_price is null or max_effective_price >= 0),
    notify_on_free_episode_event boolean not null default true,
    email_enabled boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table notification_events (
    id uuid primary key default gen_random_uuid(),
    notification_rule_id uuid references notification_rules(id) on delete set null,
    user_id uuid references users_profile(user_id) on delete set null,
    work_id uuid references works(id) on delete set null,
    offer_id uuid references offers(id) on delete set null,
    event_type text not null,
    payload jsonb not null default '{}'::jsonb,
    email_to text,
    provider_message_id text,
    created_at timestamptz not null default now()
);

create table search_events (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references users_profile(user_id) on delete set null,
    query text not null,
    result_count integer not null default 0 check (result_count >= 0),
    created_at timestamptz not null default now()
);

create table detail_view_events (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references users_profile(user_id) on delete set null,
    work_id uuid not null references works(id) on delete cascade,
    created_at timestamptz not null default now()
);

create table click_events (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references users_profile(user_id) on delete set null,
    work_id uuid references works(id) on delete set null,
    offer_id uuid references offers(id) on delete set null,
    platform_id uuid references platforms(id) on delete set null,
    destination_url text not null,
    referrer text,
    created_at timestamptz not null default now()
);

create table price_history (
    id uuid primary key default gen_random_uuid(),
    offer_id uuid not null references offers(id) on delete cascade,
    base_price integer not null check (base_price >= 0),
    instant_discounted_price integer not null check (instant_discounted_price >= 0),
    coupon_expected_price integer check (coupon_expected_price is null or coupon_expected_price >= 0),
    cashback_adjusted_price integer check (cashback_adjusted_price is null or cashback_adjusted_price >= 0),
    effective_price_for_sort integer not null check (effective_price_for_sort >= 0),
    recorded_at timestamptz not null default now()
);

create table crawl_logs (
    id uuid primary key default gen_random_uuid(),
    platform_id uuid references platforms(id) on delete set null,
    adapter_name text not null default 'MockCrawler',
    status crawl_status not null,
    started_at timestamptz not null default now(),
    finished_at timestamptz,
    items_seen integer not null default 0 check (items_seen >= 0),
    error_message text,
    notes text
);

create table raw_platform_data (
    id uuid primary key default gen_random_uuid(),
    platform_id uuid not null references platforms(id) on delete cascade,
    platform_work_id uuid references platform_works(id) on delete set null,
    crawl_log_id uuid references crawl_logs(id) on delete set null,
    source_url text not null,
    source_type offer_source_type not null default 'MOCK_CRAWLER',
    payload jsonb not null,
    captured_at timestamptz not null default now()
);

create table merge_review_queue (
    id uuid primary key default gen_random_uuid(),
    candidate_work_id uuid references works(id) on delete set null,
    candidate_platform_work_id uuid references platform_works(id) on delete set null,
    suspected_duplicate_work_id uuid references works(id) on delete set null,
    reason text not null,
    status merge_review_status not null default 'open',
    reviewed_by uuid references users_profile(user_id) on delete set null,
    reviewed_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index works_content_type_idx on works (content_type);
create index works_normalized_title_idx on works (normalized_title);
create index creators_normalized_name_idx on creators (normalized_name);
create index offers_last_updated_at_idx on offers (last_updated_at desc);
create index computed_offer_prices_sort_idx on computed_offer_prices (effective_price_for_sort, price_confidence);
create index search_events_created_at_idx on search_events (created_at desc);
create index click_events_created_at_idx on click_events (created_at desc);
create index crawl_logs_started_at_idx on crawl_logs (started_at desc);
