# MoaView Playwright E2E tests

The E2E suite verifies the fixture-only MVP flow without Supabase, Resend, Railway, or real platform credentials.

Covered flow:

1. Home page loads.
2. User searches the fixture work `달빛 기록관`.
3. User opens the work detail page.
4. Platform comparison table is visible.
5. Confirmed price (`확정가`) is visible.
6. Coupon expected price (`쿠폰 적용 예상가`) is visible and labeled as expected.
7. Cashback adjusted price (`캐시백 포함 체감가`) is visible and described as estimated/체감.
8. User clicks a platform CTA.
9. Platform-click event is mocked and asserted.
10. Favorites flow shows logged-out login guidance in fixture-auth mode.

Run locally:

```bash
npm install
npx playwright install chromium
npm run e2e
```

`playwright.config.ts` starts the fixture FastAPI API on `127.0.0.1:8000` and the Next.js app on `127.0.0.1:3000` when they are not already running. It passes both `MOAVIEW_API_BASE_URL` and `NEXT_PUBLIC_API_BASE_URL` as `http://127.0.0.1:8000` to the Next.js web server so server components and client-side event calls use the same fixture API.

The core `GET /api/search?q=달빛` contract is not mocked in Playwright. The test first verifies the live fixture API returns `달빛 기록관`, then verifies the server-rendered `/search?q=달빛` page contains the same title. Only analytics event endpoints are mocked at the browser network layer to keep event assertions deterministic.
