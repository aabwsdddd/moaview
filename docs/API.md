# MoaView API Contract

The initial API is fixture-backed. It does not scrape production platforms and it does not require platform login.

## `GET /health`

Returns service health.

Response body:

```json
{"status":"ok","service":"api"}
```

## `GET /works?q={query}`

Searches fixture works by title or author.

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

## `GET /offers?work_id={work_id}`

Lists fixture platform offers. Every offer includes base price, automatic discount, coupon expected discount, cashback rate, free episode count, wait-free availability, source URL, and last verified time.

Coupon values are expected prices when user action is required; cashback values are estimated value, not cash discounts.


## Database schema and seed contract

The initial Supabase schema lives in `supabase/migrations/202605090001_initial_schema.sql`. It is fixture-compatible only and must not be used to connect to or scrape Naver, KakaoPage, Ridi, or any authenticated platform pages.

Content records support `WEBTOON` and `WEBNOVEL` through the `content_type` enum. Offer rows must retain `source_url`, `source_type`, and `last_updated_at` so the UI can display the price source and last updated time.

Promotion rows use the `promotion_type` enum values `instant_discount`, `cashback`, `bonus_currency`, `free_episode_event`, and `bundle_discount`. Coupon rows keep separate flags for `downloadable`, `auto_issued`, `code_required`, `first_purchase_only`, and `user_targeted` so user-specific coupons are never treated as confirmed prices without known account state.

Computed prices are stored in `computed_offer_prices` with `base_price`, `instant_discounted_price`, `coupon_expected_price`, `cashback_adjusted_price`, `effective_price_for_sort`, `price_confidence`, and `calculation_note`. `price_confidence` separates confirmed automatic discounts from estimated coupon/cashback outcomes.

Local seed data is intentionally small and fixture-like. Validate it with:

```bash
python scripts/seed_db.py
```

Apply it to a local Supabase/Postgres database with `psql` available by setting `DATABASE_URL` and running:

```bash
make seed
```
