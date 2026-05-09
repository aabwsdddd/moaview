# MoaView Deployment Guide

MoaView MVP is designed to deploy as separate fixture-safe services:

- **Next.js web app** on Vercel (`apps/web`).
- **FastAPI API** on Railway (`services/api`).
- **Railway Cron worker** for the notification worker and mock crawler (`services/worker`, `services/crawler`).
- **Supabase** for future Postgres/Auth-backed persistence.
- **Resend** for notification email delivery when dry-run mode is disabled.

The MVP must remain runnable without external credentials. Production scraping, platform login integration, Naver/KakaoPage/Ridi connections, built-in reader, OCR, AI recommendations, comments, payments, and platform account credential storage are intentionally not implemented.

## Required environment variables

Use `.env.example` as the source of truth. Do not commit real secrets.

| Variable | Used by | Required for fixture tests? | Notes |
| --- | --- | --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | Vercel web | Yes, with local default | Public URL of the FastAPI API, for example `https://moaview-api.up.railway.app`. |
| `MOAVIEW_WEB_BASE_URL` | Worker emails | No | Public web URL used in notification CTA links. |
| `DATABASE_URL` | Future API/worker DB writes, seed script | No | Supabase Postgres connection string. Fixture tests can leave blank. |
| `NEXT_PUBLIC_SUPABASE_URL` | Web auth | No | Public Supabase project URL. Blank enables fixture-auth guidance. |
| `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | Web auth | No | Preferred public browser key for Supabase Auth. |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Web auth fallback | No | Compatibility fallback for older Supabase setups. |
| `SUPABASE_SERVICE_ROLE_KEY` | Server-only future API/worker tasks | No | Secret. Never expose to client components or `NEXT_PUBLIC_*`. |
| `RESEND_API_KEY` | Worker email sending | No | Required only when `NOTIFICATION_DRY_RUN=false`. |
| `RESEND_FROM_EMAIL` | Worker email sending | No | Sender identity verified in Resend for real delivery. |
| `NOTIFICATION_DRY_RUN` | Worker | Yes | Keep `true` in CI and fixture-only local runs. |
| `MOAVIEW_CRAWL_STATE_DIR` | Mock crawler/worker | No | Local JSON state directory, default `.local/crawl-state`. |

## Vercel: Next.js web app

1. Create a Vercel project from this repository.
2. Set **Root Directory** to `apps/web`.
3. Use the default Next.js framework preset.
4. Set environment variables:
   - `NEXT_PUBLIC_API_BASE_URL` to the public Railway API URL.
   - Optional Supabase Auth values if testing real Supabase login: `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` or `NEXT_PUBLIC_SUPABASE_ANON_KEY`.
5. Deploy.

The web app remains fixture-safe when Supabase variables are blank: login/favorite UI shows guidance and no real OAuth flow is started.

## Railway: FastAPI API

1. Create a Railway service from this repository.
2. Use a Python runtime.
3. Install dependencies with:

   ```bash
   python -m pip install -r services/api/requirements.txt
   ```

4. Start the API with:

   ```bash
   python -m uvicorn services.api.app.main:app --host 0.0.0.0 --port $PORT
   ```

5. Set `DATABASE_URL` only when you are ready to connect Supabase Postgres-backed persistence. The current MVP API uses fixture data and passes tests without it.
6. Verify the deployment by opening `/health`.

## Railway Cron: mock crawler and notification worker

Create separate Railway cron jobs or services for fixture-safe jobs.

Mock crawler command:

```bash
python services/crawler/run_mock_crawl.py
```

Notification worker command:

```bash
python services/worker/send_notifications.py
```

Recommended worker variables:

- `NOTIFICATION_DRY_RUN=true` until a Resend sender is verified and you intentionally enable email delivery.
- `MOAVIEW_WEB_BASE_URL` set to the Vercel web URL.
- `RESEND_API_KEY` and `RESEND_FROM_EMAIL` only for real email sending.
- `MOAVIEW_CRAWL_STATE_DIR` if using a custom writable state location.

The crawler is **MockCrawler only**. Do not add production scraping or connect to Naver Webtoon, KakaoPage, Ridi, authenticated pages, paywalls, or anti-bot-protected pages before `docs/CRAWLER_POLICY.md` is reviewed and the product policy changes.

## Supabase: Postgres/Auth

1. Create a Supabase project.
2. Apply `supabase/migrations/202605090001_initial_schema.sql` to initialize fixture-compatible tables.
3. Optionally load fixture seed data with `make seed` after setting `DATABASE_URL` locally.
4. Configure OAuth providers only for Supabase Auth login. Do not configure platform account login.
5. Keep `SUPABASE_SERVICE_ROLE_KEY` server-only.

## Resend: email

1. Create and verify a sending domain/sender in Resend.
2. Set `RESEND_FROM_EMAIL` to that verified sender.
3. Set `RESEND_API_KEY` in the Railway worker only.
4. Switch `NOTIFICATION_DRY_RUN=false` only after checking dry-run email output.

Tests and CI must keep dry-run mode enabled and must not send real email.

## Fixture-only behavior that remains

- Search, work detail, offers, promotions, coupons, analytics, crawler changes, and notification records are fixture-backed.
- Platform source URLs use fixture URLs and are for CTA-flow verification only.
- E2E tests mock event writes where needed and require no Supabase, Resend, Railway, or platform credentials.

## Intentionally not implemented yet

- Production scraping.
- Direct Naver, KakaoPage, or Ridi integrations.
- Platform login or credential storage.
- Built-in webtoon/novel reader.
- OCR.
- AI recommendations.
- Comments/reviews/community features.
- Payments.
- Production admin authorization; current admin pages are MVP placeholders.
