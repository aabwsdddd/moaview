# MoaView API

FastAPI service backed by fixture data only.

## Run

```bash
python -m pip install -r services/api/requirements.txt
uvicorn services.api.app.main:app --reload --host 0.0.0.0 --port 8000
```

## Health

`GET /health` returns:

```json
{"status":"ok","service":"api"}
```
