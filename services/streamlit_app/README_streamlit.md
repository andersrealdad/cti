# EVITO News & Risk Stream (Streamlit)

This app shows risk snapshots per ticker (e.g., “S&P 500 (SPY)” for the index ETF), runs AI “debates” to generate briefs, supports pre-baked briefs, persona markdown pipelines, IN/OUT file queues, lets you queue/review/save them, mark winners, and (optionally) broadcast to Slack. It uses the EVITO Risk API for data, multiple LLMs for briefs, and local JSONL/Markdown stubs for persistence.

## What this covers
- How risk data flows in.
- How AI briefs are generated (models/personas), mock + pre-baked fallback.
- Persona markdown pipeline to briefs_in/out.
- IN/OUT pipelines for news/briefs/debates.
- Queue/Library behavior.
- Optional Slack broadcast.
- Env vars and how to run.

## Architecture at a glance
- `services/streamlit_app/app.py`: Streamlit UI, AI Debate, pre-baked briefs, persona templates, IN/OUT pipelines, mocks, queue/library, AI Universe view.
- Risk data: EVITO Risk API (`EVITO_API_URL`, default `http://localhost:8081`).
- Models: OpenAI-compatible + Anthropic (only shown if API keys are set). Select as many as you like; embeddings for saves/winners always use MiniLM locally.
- Storage: local stubs:
  - `data/review_queue.jsonl` (queued briefs, no embedding)
  - `data/library.jsonl` (saved briefs with embeddings; winners marked)
  - `data/prebaked_briefs.jsonl` (optional pre-baked briefs per ticker/persona)
  - `data/ai_universe.jsonl` (RSI + meta for AI names; include an ETF column if desired)
  - IN/OUT folders (Markdown): `data/news_in/out`, `data/briefs_in/out`, `data/debates_in/out`
- Embeddings: `sentence-transformers` (all-MiniLM-L6-v2) for saved briefs.
- Optional Slack broadcast: `SLACK_BROADCAST_WEBHOOK` (winner posts).
- Headlines: Google News RSS by default; disable with `DISABLE_NEWS=1`.

## Data flow
1) Risk card: calls `EVITO_API_URL/analyze` per ticker/days. Shows risk level, score, factors (rendered as bullets), vol/trend.
2) AI Debate:
   - Builds a payload from the risk data + headlines (if enabled).
   - Persona select per ticker; “Create Persona MD” saves a markdown template to `data/briefs_in/` for external LLMs.
   - Pre-baked briefs: if `data/prebaked_briefs.jsonl` has entries for the ticker, they render instead of live calls.
   - Otherwise: Calls selected models from `MODEL_REGISTRY` (keys required). Pick as many models as you like; embeddings are always MiniLM when you Save/Winner.
   - If no models or call fails, shows a mock brief from `MOCK_BRIEFS`.
3) Brief actions (per brief):
   - Queue → append to `data/review_queue.jsonl` (no embedding).
   - Save DB → embed + append to `data/library.jsonl`.
   - Mark winner → embed + save with `winner=True`, optional Slack broadcast.
4) Review tab:
   - Review Queue: select and save queued items (embedding added) to library; removes from queue.
   - Library Snapshot: last 20 saved items; featured strip on Dashboard shows last 5 winners.
5) Pipelines tab:
   - IN/OUT views for NEWS, BRIEFS, DEBATES (Markdown files under `data/*_in`, `data/*_out`).
   - Move IN → OUT; view OUT content; promote `briefs_out` to library as audited briefs.
6) AI Universe:
   - Reads `data/ai_universe.jsonl` and shows RSI states (Overbought/Neutral/Oversold) with filterable table (add ETF info in the JSONL if needed).

## Mocks and pre-baked
- If pre-baked exists for a ticker, those briefs show and skip live calls.
- If no models are configured (no keys) or calls fail, a mock brief is shown with Queue/Save/Winner buttons.

## Environment variables (auto-loaded from `~/EVITO/.env`)
- `EVITO_API_URL` (default `http://localhost:8081`)
- `DISABLE_NEWS` (set `1` to hide RSS headlines)
- Model keys (only models with keys appear):
  - `OPENAI_API_KEY` (and optional `OPENAI_BASE`)
  - `XAI_API_KEY`, `XAI_BASE`, `XAI_MODEL`
  - `MISTRAL_API_KEY`, `MISTRAL_BASE`, `MISTRAL_MODEL`
  - `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`
- Slack broadcast (optional): `SLACK_BROADCAST_WEBHOOK`

## Running locally
1) Activate venv & install:
   ```bash
   cd ~/EVITO
   source .venv/bin/activate
   uv pip install -r services/streamlit_app/requirements.txt
   ```
2) Ensure Risk API is up:
   ```bash
   python services/risk_bot_api/evito_api_server.py
   curl http://localhost:8081/health  # should return 200
   ```
3) Run Streamlit:
   ```bash
   streamlit run services/streamlit_app/app.py --server.port 8501
   ```
4) Use the app (http://localhost:8501):
   - Dashboard → pick ticker/cycle.
   - “🤖 AI Debate”: if pre-baked exists, it shows; otherwise if no models, a mock brief appears; if a model key exists, select persona and as many models as you like, then “Generate briefs”.
   - Persona MD: click to spawn a template into `data/briefs_in/` for external LLMs.
   - Use Queue/Save/Winner to populate Review/Library; Review tab shows queue/library snapshots.
   - Pipelines tab to move IN→OUT and promote `briefs_out` to library.

## Slack & chat
- Winner broadcast: if `SLACK_BROADCAST_WEBHOOK` is set, marking a winner posts a truncated brief to Slack.
- For a chatbar to push to Slack, add a button to send the brief text to your Slack bot/webhook. No OpenCode required unless you want their UI/agent orchestration.

## Custom news
- Default: Google News RSS. Disable with `DISABLE_NEWS=1`.
- You can add sources in the sidebar or drop custom items into `data/custom_news.jsonl` filtered by ticker.

## Swap JSONL stubs for a real DB
- Replace `upsert_to_library` with your vector DB client.
- Keep metadata: `ticker`, `days`, `model`, `persona`, `timestamp`, `prompt_version`, `headlines`, `winner`, and `embedding`.

## What a brief is
- Text from a model, pre-baked, or mock with metadata:
  - `id`, `ticker`, `days`, `model`, `persona`, `timestamp`, `text`, `prompt_version`, `headlines`, `winner` (optional), `embedding` (when saved), `audited` (for OUT briefs promoted).
- Queue: stored raw in `review_queue.jsonl`.
- Library: stored with embedding in `library.jsonl`; winners flagged; OUT briefs can be promoted as audited.

## Quick demo steps (even with no keys)
1) Start API + Streamlit.
2) Dashboard → select ticker; pre-baked if present, else mock if no models.
3) Click Queue/Save/Winner to populate Review/Library.
4) Persona MD: generate a template into `data/briefs_in/`, process externally, drop result into `data/briefs_out/`, then promote from Pipelines tab.
5) Featured strip shows winners; Review tab shows queue/library snapshots.

## Notes
- Torch warnings about `torch.classes` are harmless.
- Do not upgrade/downgrade SDKs for this demo; the app works with current deps.
- Keep secrets only in your local `.env`; rotate if exposed.
