# MoaView API Contract

The initial API is fixture-backed. It does not scrape production platforms, does not connect to Naver, KakaoPage, or Ridi, and does not require platform login or Supabase credentials for tests.

## Base conventions

- MVP product flow: Search → Work Detail → Platform Comparison → Favorite → Platform Click Tracking.
- Fixture timestamps and source URLs are returned so the UI can show price source and last updated time.
- Coupon prices are labeled as expected prices when user action is required; cashback adjusted prices are estimated value and are not cash discounts.
- Event payloads must include `anonymous_session_id` when `user_id` is not available.

## `GET /health`

Returns service health.

Response body:

```json
{"status":"ok","service":"api"}
```

## Compatibility endpoints

### `GET /works?q={query}`

Compatibility alias for the original fixture work search. Searches fixture works by title or author.

Response body:

```json
{
  "items": [
    {
      "id": "work_moonlight_archive",
      "title": "달빛 기록관",
      "authors": ["한서윤"],
      "type": "webtoon",
      "status": "ongoing",
      "description": "비밀스러운 기록관에서 시작되는 판타지 로맨스."
    }
  ],
  "count": 1
}
```

### `GET /offers?work_id={work_id}`

Compatibility endpoint for the original calculated fixture offers. Every offer includes source URL and last verified time from the fixture plus the deterministic `calculated_price` object.

Calculated price object:

```json
{
  "base_price": 400,
  "instant_discounted_price": 360,
  "coupon_expected_price": 324,
  "cashback_adjusted_price": null,
  "effective_price_for_sort": 324,
  "price_confidence": "estimated",
  "calculation_note": "Automatic instant discounts are treated as confirmed. Coupon price is expected because coupon terms require user action or issuance.",
  "applied_promotion_ids": ["promo_kakao_10_percent_auto"],
  "applied_coupon_ids": ["coupon_kakao_code_fixture"],
  "calculated_at": "2026-05-01T09:10:00Z"
}
```

## New `/api/*` endpoints

### `GET /api/search?q={query}`

Searches fixture works by title or author and returns result cards enriched with platform comparison summary fields.

Response example:

```json
{
  "items": [
    {
      "id": "work_moonlight_archive",
      "title": "달빛 기록관",
      "authors": ["한서윤"],
      "content_type": "webtoon",
      "platforms": [
        {
          "id": "platform_naver_webtoon",
          "label": "네이버웹툰",
          "offer_id": "offer_naver_moonlight",
          "source_url": "https://example.com/naver/moonlight-archive",
          "last_updated_at": "2026-05-01T09:00:00Z"
        },
        {
          "id": "platform_kakaopage",
          "label": "카카오페이지",
          "offer_id": "offer_kakao_moonlight",
          "source_url": "https://example.com/kakao/moonlight-archive",
          "last_updated_at": "2026-05-01T09:10:00Z"
        }
      ],
      "max_free_episodes": 7,
      "lowest_confirmed_price": 300,
      "lowest_coupon_expected_price": 324,
      "best_platform_label": "네이버웹툰"
    }
  ],
  "count": 1
}
```

### `GET /api/works/{work_id}`

Returns work detail metadata and available platforms. `genre` is included when fixture data provides it; otherwise it is `null`.

Response example:

```json
{
  "id": "work_moonlight_archive",
  "title": "달빛 기록관",
  "authors": ["한서윤"],
  "content_type": "webtoon",
  "genre": null,
  "status": "ongoing",
  "description": "비밀스러운 기록관에서 시작되는 판타지 로맨스.",
  "available_platforms": [
    {
      "id": "platform_naver_webtoon",
      "label": "네이버웹툰",
      "offer_id": "offer_naver_moonlight",
      "source_url": "https://example.com/naver/moonlight-archive",
      "last_updated_at": "2026-05-01T09:00:00Z"
    },
    {
      "id": "platform_kakaopage",
      "label": "카카오페이지",
      "offer_id": "offer_kakao_moonlight",
      "source_url": "https://example.com/kakao/moonlight-archive",
      "last_updated_at": "2026-05-01T09:10:00Z"
    }
  ]
}
```

Unknown work IDs return `404` with `{"detail":"Work not found"}`.

### `GET /api/works/{work_id}/offers`

Returns flattened platform comparison rows for one work. These rows use the same fixture data and deterministic pricing module as `GET /offers`.

Response example:

```json
{
  "items": [
    {
      "id": "offer_kakao_moonlight",
      "work_id": "work_moonlight_archive",
      "platform": "카카오페이지",
      "platform_id": "platform_kakaopage",
      "source_url": "https://example.com/kakao/moonlight-archive",
      "last_updated_at": "2026-05-01T09:10:00Z",
      "free_episode_count": 7,
      "wait_free_available": true,
      "base_price": 400,
      "instant_discounted_price": 360,
      "coupon_expected_price": 324,
      "cashback_adjusted_price": null,
      "effective_price_for_sort": 324,
      "price_confidence": "estimated",
      "calculation_note": "Automatic instant discounts are treated as confirmed. Coupon price is expected because coupon terms require user action or issuance.",
      "active_promotions": [
        {
          "id": "promo_kakao_spring_wait_free",
          "platform": "카카오페이지",
          "promotion_type": "free_episode_event",
          "title": "봄맞이 기다무 확대"
        }
      ],
      "active_coupons": [
        {
          "id": "coupon_kakao_code_fixture",
          "platform": "카카오페이지",
          "coupon_type": "code_required",
          "coupon_code": "FIXTURE10",
          "title": "fixture 코드 10% 쿠폰",
          "label": "쿠폰 적용 예상가"
        }
      ]
    }
  ],
  "count": 2
}
```

### `POST /api/favorites`

Adds a work to the in-memory MVP favorites store. Full Supabase Auth integration can replace this storage later.

Request example:

```json
{
  "work_id": "work_moonlight_archive"
}
```

Response example:

```json
{
  "item": {
    "user_id": "fixture_user",
    "work_id": "work_moonlight_archive",
    "created_at": "2026-05-09T00:00:00Z",
    "work": {
      "id": "work_moonlight_archive",
      "title": "달빛 기록관",
      "authors": ["한서윤"],
      "content_type": "webtoon"
    }
  },
  "count": 1
}
```

### `DELETE /api/favorites/{work_id}`

Removes a work from the in-memory favorites store. Deleting an absent favorite is idempotent.

Response example:

```json
{
  "deleted": true,
  "work_id": "work_moonlight_archive",
  "count": 0
}
```

### `GET /api/favorites`

Lists in-memory favorites with embedded work detail summaries.

Response example:

```json
{
  "items": [
    {
      "user_id": "fixture_user",
      "work_id": "work_moonlight_archive",
      "created_at": "2026-05-09T00:00:00Z",
      "work": {
        "id": "work_moonlight_archive",
        "title": "달빛 기록관",
        "authors": ["한서윤"],
        "content_type": "webtoon"
      }
    }
  ],
  "count": 1
}
```

### `GET /api/notifications`

Returns fixture-compatible notification event records. Until the notification worker is implemented, this endpoint projects notification-like records from in-memory detail-view and platform-click events.

Response example:

```json
{
  "items": [
    {
      "id": "notification_event_platform-click_1",
      "event_type": "platform-click",
      "work_id": "work_moonlight_archive",
      "user_id": null,
      "anonymous_session_id": "anon_1",
      "payload": {
        "event_type": "platform-click",
        "work_id": "work_moonlight_archive",
        "offer_id": "offer_kakao_moonlight"
      },
      "created_at": "2026-05-09T12:00:00Z"
    }
  ],
  "count": 1
}
```

### `POST /api/events/search`

Records a search analytics event.

Request example:

```json
{
  "anonymous_session_id": "anon_1",
  "query": "달빛",
  "result_count": 1
}
```

Response example:

```json
{
  "item": {
    "id": "event_search_1",
    "event_type": "search",
    "user_id": null,
    "anonymous_session_id": "anon_1",
    "query": "달빛",
    "result_count": 1,
    "created_at": "2026-05-09T00:00:00Z"
  },
  "count": 1
}
```

### `POST /api/events/detail-view`

Records a work detail view analytics event.

Request example:

```json
{
  "anonymous_session_id": "anon_1",
  "work_id": "work_moonlight_archive"
}
```

Response example:

```json
{
  "item": {
    "id": "event_detail-view_1",
    "event_type": "detail-view",
    "user_id": null,
    "anonymous_session_id": "anon_1",
    "work_id": "work_moonlight_archive",
    "created_at": "2026-05-09T00:00:00Z"
  },
  "count": 1
}
```

### `POST /api/events/platform-click`

Records an external platform CTA click. The stored event includes the work, platform, offer, CTA type, effective price at click, destination URL, and click timestamp. If `effective_price_at_click`, `destination_url`, or `platform_id` are omitted, the API derives them from the fixture offer.

Request example:

```json
{
  "anonymous_session_id": "anon_1",
  "work_id": "work_moonlight_archive",
  "platform_id": "platform_kakaopage",
  "offer_id": "offer_kakao_moonlight",
  "cta_type": "compare_cta",
  "effective_price_at_click": 324,
  "destination_url": "https://example.com/kakao/moonlight-archive",
  "clicked_at": "2026-05-09T12:00:00Z"
}
```

Response example:

```json
{
  "item": {
    "id": "event_platform-click_1",
    "event_type": "platform-click",
    "user_id": null,
    "anonymous_session_id": "anon_1",
    "work_id": "work_moonlight_archive",
    "platform_id": "platform_kakaopage",
    "offer_id": "offer_kakao_moonlight",
    "cta_type": "compare_cta",
    "effective_price_at_click": 324,
    "destination_url": "https://example.com/kakao/moonlight-archive",
    "clicked_at": "2026-05-09T12:00:00Z"
  },
  "count": 1
}
```

## Pricing calculation rules

- `base_price` is the original paid episode price.
- Automatic `instant_discount` promotions reduce `instant_discounted_price` and can be `confirmed`.
- Downloadable, auto-issued, and fixture-known code coupons can reduce `coupon_expected_price` only.
- User-targeted coupons, unknown code-required coupons, and first-purchase-only coupons without known eligibility stay informational.
- Expired or future promotions/coupons do not apply.
- Coupon `min_purchase_amount` and `max_discount_amount` are enforced.
- Cashback is exposed as `cashback_adjusted_price` only and is not a direct cash discount.
- `effective_price_for_sort` uses the best clear expected coupon price when available; otherwise it uses the confirmed instant discounted price. Cashback does not reduce the sort price.

## Database schema and seed contract

The initial Supabase schema lives in `supabase/migrations/202605090001_initial_schema.sql`. It is fixture-compatible only and must not be used to connect to or scrape Naver, KakaoPage, Ridi, or any authenticated platform pages.

Content records support `WEBTOON` and `WEBNOVEL` through the `content_type` enum. Offer rows must retain `source_url`, `source_type`, and `last_updated_at` so the UI can display the price source and last updated time.

Promotion rows use the `promotion_type` enum values `instant_discount`, `cashback`, `bonus_currency`, `free_episode_event`, and `bundle_discount`. Coupon rows keep separate flags for `downloadable`, `auto_issued`, `code_required`, `first_purchase_only`, and `user_targeted` so user-specific coupons are never treated as confirmed prices without known account state.

Computed prices are stored in `computed_offer_prices` with `base_price`, `instant_discounted_price`, `coupon_expected_price`, `cashback_adjusted_price`, `effective_price_for_sort`, `price_confidence`, `calculation_note`, `applied_promotion_ids`, `applied_coupon_ids`, and `calculated_at`. `price_confidence` separates confirmed automatic discounts, estimated coupon/cashback outcomes, and user-targeted unknown states.

Local seed data is intentionally small and fixture-like. Validate it with:

```bash
python scripts/seed_db.py
```

Apply it to a local Supabase/Postgres database with `psql` available by setting `DATABASE_URL` and running:

```bash
make seed
```

## Mock crawler local record contract

The mock crawler is not an HTTP API and does not scrape production platforms. It is a fixture-only job invoked with `make crawl-mock` or `python services/crawler/run_mock_crawl.py`. By default it writes generated JSON files to `.local/crawl-state`.

### `snapshot.json`

```json
{
  "schema_version": 1,
  "generated_at": "2026-05-09T00:00:00Z",
  "database_url_present": false,
  "offers": {
    "offer_kakao_moonlight": {
      "offer": {
        "id": "offer_kakao_moonlight",
        "work_id": "work_moonlight_archive",
        "platform": "카카오페이지",
        "platform_work_id": "kakaopage:work_moonlight_archive",
        "base_price_krw": 400,
        "free_episode_count": 7,
        "wait_free_available": true,
        "source_url": "https://example.com/kakao/moonlight-archive",
        "last_verified_at": "2026-05-01T09:10:00Z"
      },
      "calculated_price": {
        "base_price": 400,
        "instant_discounted_price": 360,
        "coupon_expected_price": 324,
        "cashback_adjusted_price": null,
        "effective_price_for_sort": 324,
        "price_confidence": "estimated",
        "calculation_note": "Coupon price is expected because coupon terms require user action or issuance.",
        "applied_promotion_ids": ["promo_kakao_10_percent_auto"],
        "applied_coupon_ids": ["coupon_kakao_code_fixture"],
        "calculated_at": "2026-05-01T09:10:00Z"
      },
      "promotion_ids": ["promo_kakao_10_percent_auto", "promo_kakao_spring_wait_free"],
      "downloadable_coupon_ids": [],
      "coupon_ids": ["coupon_kakao_code_fixture"]
    }
  }
}
```

### `price_history.json`

Records are compatible with the `price_history` table fields and include `changed_fields` for local debugging.

```json
[
  {
    "id": "2fe69c2f-d8e0-5d2c-9b0b-e09c9d1f2c02",
    "offer_id": "offer_kakao_moonlight",
    "base_price": 500,
    "instant_discounted_price": 450,
    "coupon_expected_price": 405,
    "cashback_adjusted_price": null,
    "effective_price_for_sort": 405,
    "recorded_at": "2026-05-09T00:00:00Z",
    "changed_fields": ["base_price", "instant_discounted_price", "coupon_expected_price", "effective_price_for_sort"]
  }
]
```

### `crawl_logs.json`

Records are compatible with the `crawl_logs` table fields. Simulated failures and retries are deterministic and are logged here.

```json
[
  {
    "id": "30a3f9b6-7d4c-45cc-9872-08e7f95b9d53",
    "platform_id": "kakaopage",
    "adapter_name": "MockKakaoPageAdapter",
    "status": "success",
    "started_at": "2026-05-09T00:00:00Z",
    "finished_at": "2026-05-09T00:00:01Z",
    "items_seen": 2,
    "error_message": null,
    "notes": "fixture-only mock crawl"
  }
]
```

### `notification_events.json`

Records are compatible with the `notification_events` table fields. Supported mock event types are:

- `free_episode_count_increased`
- `work_became_free`
- `wait_free_availability_changed`
- `new_promotion_started`
- `instant_discount_promotion_started`
- `new_downloadable_coupon`
- `coupon_expected_price_decreased`
- `cashback_event_started`

```json
[
  {
    "id": "6cb00b5b-cb56-51bc-912e-c1ab1a5d909a",
    "notification_rule_id": null,
    "user_id": null,
    "work_id": "work_moonlight_archive",
    "offer_id": "offer_naver_moonlight",
    "event_type": "free_episode_count_increased",
    "payload": {
      "previous_free_episode_count": 5,
      "current_free_episode_count": 8,
      "platform": "네이버웹툰"
    },
    "email_to": null,
    "provider_message_id": null,
    "created_at": "2026-05-09T00:00:00Z"
  }
]
```

### Notification worker delivery fields

`services/worker/send_notifications.py` updates local notification event records after processing. Dry-run and sent events keep `provider_message_id`; idempotency is also recorded in `.local/crawl-state/sent_notifications.json`. Delivery status is stored under `payload.notification_status` with values such as `dry_run_sent`, `sent`, `skipped_missing_email`, `skipped_duplicate`, or `failed`.

Email copy must preserve the pricing labels used by the API: automatic discounts are rendered as confirmed prices, coupon prices are rendered as `쿠폰 적용 예상가`, and cashback values are rendered as estimated adjusted value, not cash discounts.
