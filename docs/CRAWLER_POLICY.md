# Crawler Policy

MoaView's MVP crawler is **fixture-only**. The implemented crawler adapter system reads local JSON files from `packages/fixtures`, calculates prices with the existing pricing module, detects mock changes, and writes local JSON state under `.local/crawl-state`.

## Production crawling status

Production crawling is **not implemented**. The codebase must not connect to Naver Webtoon, KakaoPage, Ridi, or any external platform for crawler data until this policy is reviewed and an explicit production crawling design is approved.

## Allowed MVP crawler behavior

- Use local fixture files only: `works.json`, `offers.json`, `promotions.json`, and `coupons.json`.
- Simulate platform adapters for local development and tests:
  - `MockNaverWebtoonAdapter`
  - `MockKakaoPageAdapter`
  - `MockRidiAdapter`
- Calculate offer prices through `services.api.app.pricing.calculate_offer_price`.
- Detect changes from the previous local snapshot:
  - price changed
  - free episode count increased
  - wait-free availability changed
  - new promotion started
  - new downloadable coupon appeared
  - coupon expected price decreased
- Persist fixture-compatible records locally under `.local/crawl-state`:
  - `snapshot.json`
  - `price_history.json`
  - `crawl_logs.json`
  - `notification_events.json`
- Simulate deterministic adapter failures and retries for crawler reliability tests.

## Prohibited behavior

Crawler code must not:

- Scrape production pages.
- Log in to platform accounts.
- Request authenticated platform pages.
- Bypass login, paywalls, access controls, robots.txt, terms, anti-bot systems, rate limits, or technical protections.
- Store original cover images unless explicit rights and storage policy are approved.
- Treat user-specific coupons as confirmed prices unless platform account state is known.
- Send real user notification emails from mock crawler output.

## Database integration

Local JSON persistence is the default and required MVP behavior. Live database writes are not required for the mock crawler. Any future database writer must remain optional behind `DATABASE_URL`, preserve the same record shapes as the local JSON files, and keep production crawling disabled until this policy is reviewed.

## Running the mock crawler

```bash
make crawl-mock
```

Equivalent direct command:

```bash
python services/crawler/run_mock_crawl.py
```

The command creates or updates `.local/crawl-state`. That directory is intentionally ignored by Git.
