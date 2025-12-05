# EVITO Context Map (quick reference)

Use this as a single-page reminder of what’s in play so you can feed it to an AI for mindmapping or recall.

## Core services
- Risk API: `services/risk_bot_api/evito_api_server.py` (port 8081, endpoint `/analyze`). Depends on Postgres env vars; uses enhanced risk logic + LLM formatting in some routes.
- Streamlit app: `services/streamlit_app/app.py` (UI for risk cards + AI Debate + queue/library + mock fallback). Depends on EVITO API + model keys.
- Slack bot: `services/slackbot/slack_risk_bot.py` (dummy snapshot now; should call the API).
- Email bot: `services/email_handler/email_bot.py` (polls Gmail, calls API, replies via SMTP).

## Streamlit app data flow
- Fetch risk data: `EVITO_API_URL` `/analyze` → risk card per ticker.
- AI Debate: payload (risk + headlines) → prompt + persona → model call (OpenAI/Anthropic/etc.) → brief text. If no models/failure → `MOCK_BRIEFS`.
- Actions per brief: Queue (JSONL, no embedding), Save (JSONL with embedding), Winner (embedding + `winner=True`, optional Slack webhook).
- Storage (JSONL stubs in repo root `data/`):
  - `data/review_queue.jsonl`: queued briefs.
  - `data/library.jsonl`: saved briefs (with embedding), winners flagged.
- Embeddings: `sentence-transformers` (all-MiniLM-L6-v2) used when saving to library.
- Featured strip: last 5 winners from library.

## Headlines
- Default: Google News RSS via `fetch_news`. Disable with `DISABLE_NEWS=1`.
- To use your own conviction-testing items: replace `fetch_news` to read a custom JSONL (e.g., `data/custom_news.jsonl`).

## Personas (app)
- None, Buffett, Risk Officer, Tech Strategist. Mock agents are defined but only used via fallback text.

## Environment (auto-loaded from `~/EVITO/.env`)
- API: `EVITO_API_URL` (default `http://localhost:8081`)
- Models (only shown if key is set): `OPENAI_API_KEY` (+ optional `OPENAI_BASE`), `XAI_*`, `MISTRAL_*`, `ANTHROPIC_*`
- News: `DISABLE_NEWS=1` to turn off RSS
- Slack broadcast: `SLACK_BROADCAST_WEBHOOK` (winner posts)

## Data you can export for mindmaps
- Risk outputs: call `/analyze` per ticker; save JSON.
- Briefs: export `data/library.jsonl` (has text, model, persona, headlines, prompt_version, winner flag, embedding).
- Queue: `data/review_queue.jsonl` (text + metadata).
- Optional: Postgres schema in `services/shared/init.sql` (user_api_keys, user_contexts, moat_datasets).

## Current gaps / notes
- Slack bot still dummy; should call Risk API for real data.
- JSONL storage is a stub; swap `upsert_to_library` with your vector DB client when ready.
- If no model keys are set, the app shows mock briefs so the UI always has content.
- Torch warnings in logs are harmless.

## Quick run
```bash
cd ~/EVITO
source .venv/bin/activate
python services/risk_bot_api/evito_api_server.py  # in another shell; /health should be 200
streamlit run services/streamlit_app/app.py --server.port 8501
```
