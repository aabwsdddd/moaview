-- Minimal fixture-compatible seed data for local development.
-- This file intentionally avoids production scraping data and external platform connections.

insert into platforms (code, name, homepage_url, robots_url)
values
    ('NAVER_WEBTOON', '네이버웹툰', 'https://comic.naver.com', 'https://comic.naver.com/robots.txt'),
    ('KAKAO_PAGE', '카카오페이지', 'https://page.kakao.com', 'https://page.kakao.com/robots.txt'),
    ('RIDI', '리디', 'https://ridibooks.com', 'https://ridibooks.com/robots.txt')
on conflict (code) do update set
    name = excluded.name,
    homepage_url = excluded.homepage_url,
    robots_url = excluded.robots_url,
    updated_at = now();

insert into works (fixture_key, title, normalized_title, content_type, status, description)
values
    ('work_moonlight_archive', '달빛 기록관', '달빛 기록관', 'WEBTOON', 'ONGOING', '비밀스러운 기록관에서 시작되는 판타지 로맨스.'),
    ('work_clockwork_palace', '태엽 궁전의 소설가', '태엽 궁전의 소설가', 'WEBNOVEL', 'COMPLETED', '기계 궁전에서 계약 연재를 시작한 작가의 모험.')
on conflict (fixture_key) do update set
    title = excluded.title,
    normalized_title = excluded.normalized_title,
    content_type = excluded.content_type,
    status = excluded.status,
    description = excluded.description,
    updated_at = now();

insert into creators (fixture_key, display_name, normalized_name)
values
    ('creator_han_seoyun', '한서윤', '한서윤'),
    ('creator_min_doha', '민도하', '민도하'),
    ('creator_studio_moa', 'Studio Moa', 'studio moa')
on conflict (fixture_key) do update set
    display_name = excluded.display_name,
    normalized_name = excluded.normalized_name,
    updated_at = now();

insert into work_creators (work_id, creator_id, role, display_order)
select w.id, c.id, seed.role::creator_role, seed.display_order
from (values
    ('work_moonlight_archive', 'creator_han_seoyun', 'AUTHOR', 1),
    ('work_clockwork_palace', 'creator_min_doha', 'AUTHOR', 1),
    ('work_clockwork_palace', 'creator_studio_moa', 'STUDIO', 2)
) as seed(work_fixture_key, creator_fixture_key, role, display_order)
join works w on w.fixture_key = seed.work_fixture_key
join creators c on c.fixture_key = seed.creator_fixture_key
on conflict (work_id, creator_id, role) do update set
    display_order = excluded.display_order;

insert into platform_works (work_id, platform_id, platform_work_key, title_on_platform, platform_url, is_available, last_matched_at)
select w.id, p.id, seed.platform_work_key, seed.title_on_platform, seed.platform_url, true, '2026-05-01T09:00:00Z'::timestamptz
from (values
    ('work_moonlight_archive', 'NAVER_WEBTOON', 'naver-moonlight-archive', '달빛 기록관', 'https://example.com/naver/moonlight-archive'),
    ('work_moonlight_archive', 'KAKAO_PAGE', 'kakao-moonlight-archive', '달빛 기록관', 'https://example.com/kakao/moonlight-archive'),
    ('work_clockwork_palace', 'RIDI', 'ridi-clockwork-palace', '태엽 궁전의 소설가', 'https://example.com/ridi/clockwork-palace')
) as seed(work_fixture_key, platform_code, platform_work_key, title_on_platform, platform_url)
join works w on w.fixture_key = seed.work_fixture_key
join platforms p on p.code = seed.platform_code
on conflict (platform_id, platform_work_key) do update set
    title_on_platform = excluded.title_on_platform,
    platform_url = excluded.platform_url,
    is_available = excluded.is_available,
    last_matched_at = excluded.last_matched_at,
    updated_at = now();

insert into offers (platform_work_id, currency_code, base_price, free_episode_count, wait_free_available, source_url, source_type, last_updated_at)
select pw.id, 'KRW', seed.base_price, seed.free_episode_count, seed.wait_free_available, seed.source_url, 'FIXTURE'::offer_source_type, seed.last_updated_at::timestamptz
from (values
    ('NAVER_WEBTOON', 'naver-moonlight-archive', 300, 5, true, 'https://example.com/naver/moonlight-archive', '2026-05-01T09:00:00Z'),
    ('KAKAO_PAGE', 'kakao-moonlight-archive', 400, 7, true, 'https://example.com/kakao/moonlight-archive', '2026-05-01T09:10:00Z'),
    ('RIDI', 'ridi-clockwork-palace', 100, 10, false, 'https://example.com/ridi/clockwork-palace', '2026-05-01T10:00:00Z')
) as seed(platform_code, platform_work_key, base_price, free_episode_count, wait_free_available, source_url, last_updated_at)
join platforms p on p.code = seed.platform_code
join platform_works pw on pw.platform_id = p.id and pw.platform_work_key = seed.platform_work_key
on conflict (platform_work_id, source_type) do update set
    base_price = excluded.base_price,
    free_episode_count = excluded.free_episode_count,
    wait_free_available = excluded.wait_free_available,
    source_url = excluded.source_url,
    last_updated_at = excluded.last_updated_at,
    updated_at = now();

insert into promotions (fixture_key, platform_id, promotion_type, title, description, free_episode_count, starts_at, ends_at, source_url, source_type, last_updated_at)
select seed.fixture_key, p.id, seed.promotion_type::promotion_type, seed.title, seed.description, seed.free_episode_count,
       seed.starts_at::timestamptz, seed.ends_at::timestamptz, seed.source_url, 'FIXTURE'::offer_source_type, seed.last_updated_at::timestamptz
from (values
    ('promo_spring_wait_free', 'KAKAO_PAGE', 'free_episode_event', '봄맞이 기다무 확대', 'fixture 전용 프로모션 데이터입니다.', 2, '2026-05-01T00:00:00Z', '2026-05-31T23:59:59Z', 'https://example.com/kakao/promotions/spring-wait-free', '2026-05-01T09:10:00Z')
) as seed(fixture_key, platform_code, promotion_type, title, description, free_episode_count, starts_at, ends_at, source_url, last_updated_at)
join platforms p on p.code = seed.platform_code
on conflict (fixture_key) do update set
    platform_id = excluded.platform_id,
    promotion_type = excluded.promotion_type,
    title = excluded.title,
    description = excluded.description,
    free_episode_count = excluded.free_episode_count,
    starts_at = excluded.starts_at,
    ends_at = excluded.ends_at,
    source_url = excluded.source_url,
    last_updated_at = excluded.last_updated_at,
    updated_at = now();

insert into coupons (fixture_key, platform_id, title, discount_type, discount_value, downloadable, auto_issued, code_required, first_purchase_only, user_targeted, source_url, source_type, last_updated_at)
select seed.fixture_key, p.id, seed.title, seed.discount_type::coupon_discount_type, seed.discount_value,
       seed.downloadable, seed.auto_issued, seed.code_required, seed.first_purchase_only, seed.user_targeted,
       seed.source_url, 'FIXTURE'::offer_source_type, seed.last_updated_at::timestamptz
from (values
    ('coupon_first_read_20', 'NAVER_WEBTOON', '첫 열람 20% 쿠폰', 'percent', 20.00, true, false, false, true, false, 'https://example.com/naver/coupons/first-read-20', '2026-05-01T09:00:00Z'),
    ('coupon_ridi_weekend_20krw', 'RIDI', '주말 20원 쿠폰', 'amount', 20.00, true, false, false, false, false, 'https://example.com/ridi/coupons/weekend-20krw', '2026-05-01T10:00:00Z')
) as seed(fixture_key, platform_code, title, discount_type, discount_value, downloadable, auto_issued, code_required, first_purchase_only, user_targeted, source_url, last_updated_at)
join platforms p on p.code = seed.platform_code
on conflict (fixture_key) do update set
    platform_id = excluded.platform_id,
    title = excluded.title,
    discount_type = excluded.discount_type,
    discount_value = excluded.discount_value,
    downloadable = excluded.downloadable,
    auto_issued = excluded.auto_issued,
    code_required = excluded.code_required,
    first_purchase_only = excluded.first_purchase_only,
    user_targeted = excluded.user_targeted,
    source_url = excluded.source_url,
    last_updated_at = excluded.last_updated_at,
    updated_at = now();

insert into computed_offer_prices (fixture_key, offer_id, coupon_id, promotion_id, currency_code, base_price, instant_discounted_price, coupon_expected_price, cashback_adjusted_price, effective_price_for_sort, price_confidence, calculation_note)
select seed.fixture_key, o.id, c.id, pr.id, 'KRW', seed.base_price, seed.instant_discounted_price, seed.coupon_expected_price,
       seed.cashback_adjusted_price, seed.effective_price_for_sort, seed.price_confidence::price_confidence, seed.calculation_note
from (values
    ('computed_naver_moonlight_coupon', 'NAVER_WEBTOON', 'naver-moonlight-archive', 'coupon_first_read_20', null, 300, 300, 240, 228, 240, 'estimated', 'Coupon price requires user download; cashback adjusted price is estimated value, not a cash discount.'),
    ('computed_kakao_moonlight_wait_free', 'KAKAO_PAGE', 'kakao-moonlight-archive', null, 'promo_spring_wait_free', 400, 350, null, 333, 350, 'estimated', 'Instant discount is confirmed; cashback adjusted price is estimated value, not a cash discount.'),
    ('computed_ridi_clockwork_coupon', 'RIDI', 'ridi-clockwork-palace', 'coupon_ridi_weekend_20krw', null, 100, 90, 70, 68, 70, 'estimated', 'Coupon price requires user action; cashback adjusted price is estimated value, not a cash discount.')
) as seed(fixture_key, platform_code, platform_work_key, coupon_fixture_key, promotion_fixture_key, base_price, instant_discounted_price, coupon_expected_price, cashback_adjusted_price, effective_price_for_sort, price_confidence, calculation_note)
join platforms p on p.code = seed.platform_code
join platform_works pw on pw.platform_id = p.id and pw.platform_work_key = seed.platform_work_key
join offers o on o.platform_work_id = pw.id and o.source_type = 'FIXTURE'::offer_source_type
left join coupons c on c.fixture_key = seed.coupon_fixture_key
left join promotions pr on pr.fixture_key = seed.promotion_fixture_key
on conflict (fixture_key) do update set
    offer_id = excluded.offer_id,
    coupon_id = excluded.coupon_id,
    promotion_id = excluded.promotion_id,
    base_price = excluded.base_price,
    instant_discounted_price = excluded.instant_discounted_price,
    coupon_expected_price = excluded.coupon_expected_price,
    cashback_adjusted_price = excluded.cashback_adjusted_price,
    effective_price_for_sort = excluded.effective_price_for_sort,
    price_confidence = excluded.price_confidence,
    calculation_note = excluded.calculation_note,
    updated_at = now();
