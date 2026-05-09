# MoaView

MoaView는 웹툰/웹소설을 어디서 가장 싸고 편하게 볼 수 있는지 빠르게 찾게 해주는 통합 탐색 서비스입니다.

## MVP Goal

사용자가 작품을 검색하고, 여러 플랫폼의 무료 회차/가격/이벤트/쿠폰 조건을 비교한 뒤, 가장 유리한 플랫폼으로 이동하도록 만듭니다.

## Initial Scope

초기 MVP는 실제 크롤링 없이 fixture 데이터를 사용합니다.

포함 기능:
- 로그인
- 작품 검색
- 작품 상세
- 플랫폼별 가격 비교
- 쿠폰 적용 예상가 비교
- 찜
- 이메일 알림 이벤트
- 플랫폼 클릭 추적
- Mock crawler

제외 기능:
- 플랫폼 로그인 연동
- 자체 뷰어
- OCR
- AI 추천
- 리뷰/댓글/커뮤니티
- 자체 결제
- 실제 production scraping

## Tech Stack

- Frontend: Next.js, TypeScript, Tailwind
- Backend: FastAPI
- Database/Auth: Supabase
- Email: Resend
- Worker/Cron: Railway
- Crawler: MockCrawler first, Playwright later

## Development Phases

1. Project scaffold
2. Database schema
3. Price and coupon calculation
4. API
5. Frontend
6. Mock crawler
7. Analytics dashboard

## Current Status

Planning and initial scaffold stage.

## Supabase Auth local setup

The web app uses Supabase Auth for the MVP login and favorites flow, but it must remain runnable in fixture-only mode.

1. Copy `apps/web/.env.example` to `apps/web/.env.local`.
2. Set `NEXT_PUBLIC_SUPABASE_URL` and either `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` or `NEXT_PUBLIC_SUPABASE_ANON_KEY` for local Supabase Auth.
3. Keep `SUPABASE_SERVICE_ROLE_KEY` server-only. Do not expose it in client components.
4. Set `NEXT_PUBLIC_API_BASE_URL` to the fixture-backed FastAPI service, for example `http://localhost:8000`.
5. If Supabase env vars are blank, the Next.js app renders in development/test fixture mode: login controls show safe guidance, Google OAuth is not started, and tests do not require real credentials.

This task does not implement platform account login, platform credential storage, payments, real email sending, or production scraping.

## Frontend MVP run steps

The Next.js app now implements the fixture-backed user flow: Home → Search → Work Detail → Platform Comparison → External Platform CTA.

1. Install JavaScript dependencies from the repository root:
   ```bash
   npm install
   ```
2. Start the fixture-backed FastAPI service in one terminal:
   ```bash
   make api
   ```
3. Start the web app in another terminal:
   ```bash
   npm --workspace apps/web run dev
   ```
4. Open `http://localhost:3000`, search for `달빛` or `한서윤`, open a result, compare platform offers, favorite the work if logged in through Supabase Auth, and click one of the external CTA buttons.

Useful frontend routes:
- `/` — search entry, popular fixture works, free/event works, recent update section.
- `/search?q=달빛` — fixture search result cards and search event recording.
- `/works/work_moonlight_archive` — detail hero, favorite CTA, and platform comparison table.
- `/favorites` — Task 5 favorites list/empty state.
- `/notifications` — fixture-compatible notification event list/empty state.
- `/admin/merge-review` — manual dedup/merge review placeholder.

The frontend remains fixture-safe: it does not scrape platforms, bypass login, connect to platform accounts, render a built-in reader, or treat coupon expected prices as confirmed prices.

## Mock crawler

Task 7 adds a fixture-only mock crawler adapter system. It does **not** implement production crawling and does **not** connect to Naver Webtoon, KakaoPage, Ridi, or any external platform.

Run the mock crawler:

```bash
make crawl-mock
```

Equivalent direct command:

```bash
python services/crawler/run_mock_crawl.py
```

The command reads `packages/fixtures/works.json`, `offers.json`, `promotions.json`, and `coupons.json`; calculates prices with the existing pricing module; detects changes against the previous snapshot; and writes local JSON records under `.local/crawl-state`.

Generated local files:

- `snapshot.json`
- `price_history.json`
- `crawl_logs.json`
- `notification_events.json`

`.local/` is ignored by Git. Live database writes are intentionally not required for the MVP; future DB integration must be optional behind `DATABASE_URL`. Production scraping remains out of scope until `docs/CRAWLER_POLICY.md` is reviewed.

## Email notification worker

Task 8 adds a fixture-safe email notification worker for mock-crawler notification events. The worker reads pending records from `.local/crawl-state/notification_events.json`, joins offer details from `.local/crawl-state/snapshot.json`, groups notifications by `email_to`, renders Korean email subject/body copy, and marks each event as `dry_run_sent`, `sent`, `skipped_missing_email`, `skipped_duplicate`, or `failed` inside the event payload.

Run the notification worker after `make crawl-mock` has produced local crawler state:

```bash
make worker-notifications
```

Equivalent direct command:

```bash
python services/worker/send_notifications.py
```

Environment variables:

- `RESEND_API_KEY=` — Resend API key for future real email delivery; not required when dry-run is enabled.
- `RESEND_FROM_EMAIL=MoaView <notifications@moaview.local>` — sender used for non-dry-run Resend calls.
- `NOTIFICATION_DRY_RUN=true` — default-safe mode that logs email payloads and records `dry_run:*` provider message ids instead of sending network email.
- `MOAVIEW_WEB_BASE_URL=http://localhost:3000` — base URL used to render CTA links back to MoaView work detail pages.

The worker intentionally does not send real emails in tests, does not require real Resend credentials in development, does not implement Web Push, does not integrate platform login, and does not scrape authenticated platform pages.
