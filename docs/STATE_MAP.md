# EVITO Current State (Context Map)

Use this to recover the big picture quickly. It reflects what’s actually in the repo now (not aspirational plans).

## High-level flow (today)
```
Users ──▶ Streamlit (services/streamlit_app/app.py)
        └─▶ AI Debate per ticker
            ├─▶ Models (if keys set) OR Mock briefs
            ├─▶ Queue/Save/Winner buttons
            └─▶ JSONL storage (queue/library)

Users ──▶ Email bot (services/email_handler/email_bot.py)
        └─▶ Calls Risk API (/analyze) ▶ Sends HTML reply

Slack bot (services/slackbot/slack_risk_bot.py)
        └─▶ Dummy snapshot; NOT calling Risk API yet

Risk API (services/risk_bot_api/evito_api_server.py, default port 8081)
        └─▶ Provides /analyze, /health, etc. to Streamlit/Email
```

## Services & Ports
- Risk API: `services/risk_bot_api/evito_api_server.py` (default 8081).
  - Compose currently maps risk-service to 8080; align to one port (recommend 8081) if containerized.
- Streamlit: `services/streamlit_app/app.py` (runs on 8501 when invoked).
- Slack bot: `services/slackbot/slack_risk_bot.py` (dummy; needs API wiring).
- Email bot: `services/email_handler/email_bot.py` (polls Gmail, calls API).
- Infra: `infra/docker-compose.yml` (n8n, risk-service, postgres, redis, llama stub).

## Storage (current)
- JSONL stubs in `data/`:
  - `data/review_queue.jsonl` → queued briefs (no embedding).
  - `data/library.jsonl` → saved briefs (with embedding) + winners.
- Embeddings: `sentence-transformers` (all-MiniLM-L6-v2) when saving to library.
- Postgres schema exists (`services/shared/init.sql`) but not wired to briefs.

## Streamlit app (what you see)
- Risk card per ticker (from Risk API).
- AI Debate section:
  - Models listed only if API keys are set (OpenAI/Anthropic/etc.).
  - If no models/keys or call fails → mock brief shown (from `MOCK_BRIEFS`).
  - Buttons per brief: Queue, Save DB, Mark winner (optionally broadcast via Slack webhook).
  - Featured strip shows last 5 winners (from library JSONL).
- Review tab:
  - Review Queue: select and save queued items (embeds + moves to library).
  - Library Snapshot: last 20 saved items.
- Headlines: Google News RSS by default; disable with `DISABLE_NEWS=1`. Not yet using custom feed.

## Environment (auto-loaded from `~/EVITO/.env`)
- `EVITO_API_URL` (default `http://localhost:8081`)
- `DISABLE_NEWS=1` to hide RSS
- Model keys (only models with keys appear):
  - `OPENAI_API_KEY` (+ optional `OPENAI_BASE`)
  - `XAI_*` (unset if no credits)
  - `MISTRAL_*`
  - `ANTHROPIC_*`
- Slack broadcast: `SLACK_BROADCAST_WEBHOOK` (for winner posts)

## What’s functional vs. placeholder
- Functional: Risk API; Streamlit (with mock fallback); Email bot; JSONL queue/library; embedding on save.
- Placeholder/incomplete:
  - Slack bot: dummy; does not call Risk API.
  - Llama service in compose: not configured with a model/port.
  - Compose port alignment for risk-service (8080 vs. 8081) needs a decision.
  - Custom news feed not wired; RSS only.
  - Portfolio upload/modals in Slack/Streamlit: not present in current app.py.

## Quick demo script (works even without model keys)
1) Start Risk API (if not already): `python services/risk_bot_api/evito_api_server.py` → check `curl http://localhost:8081/health`.
2) Start Streamlit (venv active): `streamlit run services/streamlit_app/app.py --server.port 8501`.
3) In http://localhost:8501 → Dashboard:
   - Pick a ticker.
   - If no model keys: mock brief appears under “AI Debate”; use Queue/Save/Winner to populate Review/Library.
   - If a key is set (e.g., OPENAI_API_KEY): select model/persona, click “Generate briefs,” then use Queue/Save/Winner.
4) Review tab: see queued items and library snapshot; winners show on the Featured strip.

## Suggested next fixes (after demo)
- Wire Slack bot to call Risk API (replace dummy snapshot).
- Replace JSONL stubs with real vector DB (embed + upsert).
- Align risk-service port across API/compose (choose 8081 or 8080).
- Add custom news feed (replace fetch_news with your JSONL).
- Optional: add Slack “Send brief” button in Streamlit for chatbar use.

