# MoaView Acceptance Criteria

## Task 3: Price, Promotion, and Coupon Calculation

The pricing logic is accepted when all of the following are true:

- Pricing is deterministic and implemented as pure Python functions for fixture-backed API use only.
- Inputs include `paid_episode_price`, `currency_type`, `free_episode_count`, `wait_free_available`, `promotions`, `coupons`, and a current timestamp.
- Outputs include `base_price`, `instant_discounted_price`, `coupon_expected_price`, `cashback_adjusted_price`, `effective_price_for_sort`, `price_confidence`, `calculation_note`, `applied_promotion_ids`, `applied_coupon_ids`, and `calculated_at`.
- Expired and future promotions/coupons are ignored.
- Automatic `instant_discount` promotions are treated as confirmed discounts.
- Downloadable, auto-issued, or known-code coupons can affect only the expected coupon price, never the confirmed instant price.
- User-targeted coupons, unknown code-required coupons, and first-purchase-only coupons without known eligibility are informational and are not applied to sorting.
- Coupon `min_purchase_amount` and `max_discount_amount` terms are respected.
- Cashback is exposed only as `cashback_adjusted_price` and described as an adjusted estimated value, not a cash discount.
- Fixture data includes examples for instant discount, cashback, free episode events, downloadable coupons, capped coupons, and known code-required coupons.
- No production scraping, platform login integration, or live Naver/KakaoPage/Ridi connection is introduced.
- Pricing and coupon tests pass, and `make check` passes.

## Task 5: Supabase Auth Integration and Favorite Works Flow

The auth and favorites flow is accepted when all of the following are true:

- The Next.js app exposes `/login` with email magic link UI and Google OAuth copy/wiring through Supabase Auth.
- The global header shows the logged-in email and a logout action when Supabase returns a user, otherwise it shows a login link.
- The work detail UI includes a favorite CTA and shows `로그인 후 찜할 수 있어요` for logged-out users.
- `/favorites` renders the user's favorite works from the Task 4 `/api/favorites` contract and shows an empty state when none are returned.
- Supabase browser/server utility functions safely return `null` when public Supabase env vars are missing, so tests and fixture-only local development do not need production credentials.
- `.env.example` documents `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, and `NEXT_PUBLIC_API_BASE_URL`.
- Tests cover login page rendering, logged-out favorite guidance, favorites empty state, and missing-env Supabase utility behavior.
- No platform login integration, platform credential storage, payments, real email sending, real scraping, or production crawling is introduced.

## Task 6: Full Frontend MVP Flow

The frontend MVP flow is accepted when all of the following are true:

- `/` includes a search input plus fixture-backed popular works, free/event works when available, and recent update sections when timestamps are available.
- `/search?q={query}` reads the URL query, renders result cards with title, authors, content type, platforms, max free episodes, lowest confirmed price, and lowest coupon expected price.
- A performed search attempts to record `POST /api/events/search` with an anonymous session id when a user id is unavailable.
- Search result cards navigate to `/works/[work_id]`.
- `/works/[work_id]` renders a work hero with title, authors, content type, status, genre when available, and description when available.
- The work detail platform comparison table shows platform, free episode count, wait-free availability, base price, instant discounted price, coupon expected price, cashback adjusted price, price confidence, source URL, and last updated time for every offer.
- Price labels clearly separate `확정가`, `쿠폰 적용 예상가`, and `캐시백 포함 체감가`; coupon expected prices are never labeled as confirmed prices.
- Each offer exposes `calculation_note` in expandable help text.
- CTA buttons `무료로 보기`, `최저가로 보기`, and `쿠폰 받고 보기` record `POST /api/events/platform-click` before opening the fixture destination URL.
- `/favorites` continues to use the Task 5 auth/favorites behavior.
- `/notifications` renders fixture notification events or a clear empty state.
- `/admin/merge-review` explains that it is a manual dedup/merge review placeholder and does not add complex admin auth.
- The app works with fixture-backed API responses and does not require real scraping, platform login, paywall access, OCR, a built-in reader, comments, reviews, payments, or production crawling.
- Component tests cover search cards, coupon expected price labeling, and CTA click event recording; Playwright E2E scaffold covers the search → detail → comparison → CTA flow.
- `make check` passes.
