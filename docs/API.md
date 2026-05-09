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
