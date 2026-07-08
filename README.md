# DrayFrogd V2

FastAPI + React intraday auto-trading bot with Bybit demo/live mode, Supabase journaling, and structured stop-loss reason tracking.

## Local run

Backend:

```powershell
py -3 -m pip install -r requirements.txt
py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

## Required manual secrets

Backend env:
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD_HASH`
- `SESSION_SECRET`
- `BYBIT_DEMO_API_KEY`
- `BYBIT_DEMO_API_SECRET`
- `BYBIT_LIVE_API_KEY`
- `BYBIT_LIVE_API_SECRET`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

Frontend env:
- `VITE_API_BASE_URL`

## Deployment

- Push repo to GitHub
- Create two Render services from `render.yaml`
- Set backend env vars in Render
- Set frontend `VITE_API_BASE_URL` to deployed backend URL
- Create Supabase tables `trade_journal` and `bot_events` matching backend payload keys

## Notes

- Default execution mode is `demo`
- Live mode stays blocked until live Bybit keys are present and admin switches mode
- Closed loss trades store `sl_hit_reason`
