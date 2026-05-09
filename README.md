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
