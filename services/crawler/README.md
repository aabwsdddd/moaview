# Crawler

The MVP crawler is fixture-only and never connects to real platforms.

## Adapters

`services/crawler/mock_crawler.py` defines the `PlatformAdapter` interface and the mock implementations:

- `MockNaverWebtoonAdapter`
- `MockKakaoPageAdapter`
- `MockRidiAdapter`

Each adapter supports:

- `search_works(query)`
- `fetch_work_detail(platform_work_id)`
- `fetch_offers(platform_work_id)`
- `fetch_promotions(platform_work_id)`
- `fetch_coupons(platform_work_id)`
- `fetch_rankings()`

All methods read `packages/fixtures/*.json` only.

## Mock crawl command

```bash
make crawl-mock
```

or:

```bash
python services/crawler/run_mock_crawl.py
```

The job calculates prices, compares them with the previous local snapshot, and writes fixture-compatible JSON records to `.local/crawl-state`:

- `snapshot.json`
- `price_history.json`
- `crawl_logs.json`
- `notification_events.json`

Production crawling is not implemented. Do not add scraping, platform login integration, authenticated requests, or anti-bot bypass logic before `docs/CRAWLER_POLICY.md` is reviewed.
