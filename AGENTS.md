# AGENTS.md

## Project
MoaView is a Korean webtoon/web novel platform comparison MVP.

Core flow:
Search → Work Detail → Platform Comparison → External Platform Click

## MVP Scope
Implement:
- Supabase Auth login
- Search by title and author
- Work detail page
- Platform offer comparison
- Favorite works
- Email notification event records
- Platform click tracking
- Admin review queue
- Fixture-based data
- Mock crawler adapter

Do not implement:
- Platform login integration
- Built-in reader
- OCR
- AI recommendations
- Comments, reviews, community
- Payments
- Production scraping before data policy review

## Tech Stack
- Web: Next.js, TypeScript, Tailwind, Zustand
- API: FastAPI, Python
- DB: Supabase Postgres
- Auth: Supabase Auth
- Email: Resend
- Worker/Cron: Railway
- Crawler: MockCrawler first, Playwright later
- Tests: pytest, Vitest, Playwright

## Price Rules
Every offer must show:
- base price
- instant discounted price
- coupon expected price
- cashback adjusted price
- free episode count
- wait-free availability
- source URL
- last verified time

Coupon prices must be labeled carefully:
- confirmed price: automatic discounts only
- coupon expected price: user must download or receive coupon
- cashback adjusted price: estimated value, not cash discount

Never label a user-specific coupon as confirmed unless the platform account state is known.

## Crawler Safety
- Do not bypass login, paywalls, access controls, or anti-bot systems.
- Do not scrape authenticated pages.
- Respect robots.txt and platform terms.
- Store only what is needed for comparison.
- Do not store original cover images unless allowed.
- Production crawling must be added only after docs/CRAWLER_POLICY.md is reviewed.

## Done Definition
A task is done only when:
- Relevant tests are added.
- Fixture data is updated if needed.
- make check passes.
- API contract is documented.
- UI shows price source and last updated time.
