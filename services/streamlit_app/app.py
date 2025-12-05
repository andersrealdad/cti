#!/usr/bin/env python3
"""
EVITO News & Risk Stream (Streamlit)
- Consumes EVITO Risk API
- Renders ticker cards with risk score, level, factors
- Optional auto-refresh
- Optional headline fetch (Google News RSS); can be disabled via DISABLE_NEWS=1
"""
import json
import os
import textwrap
import time
import uuid
from hashlib import sha1
from pathlib import Path

import requests
import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from inout_store import (
    NEWS_IN,
    NEWS_OUT,
    BRIEFS_IN,
    BRIEFS_OUT,
    DEBATES_IN,
    DEBATES_OUT,
    list_md,
    read_md,
    write_md,
    move_md,
)

# Load .env robustly from project root
root_env = Path.cwd() / ".env"
if root_env.exists():
    load_dotenv(root_env)
else:
    # fallback: resolve relative to file location
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")



# -----------------------------
# 1) MOCK DATA FOR DEMO
# -----------------------------

MOCK_BRIEFS = {
    "POWER": """...Din 'Strøm er den nye oljen'-brief her...""",
    "SAMSUNG": """...Din Samsung thesis vs audit brief her...""",
    "NVDA": """...GPU bottleneck brief...""",
    "__DEFAULT__": """Fallback brief if nothing matches."""
}

MOCK_AGENTS = {
    "Audit Agent": """
        You are an Audit Agent. Your job is to evaluate whether an investment thesis
        is stronger than the theories and evidence it is built upon.
        You flag confirmation bias, emotional reasoning, unsupported extrapolations,
        and identify which parts are supported, inferred, or speculative.
    """,
    "Flashlight Agent": """
        You extract hidden risks, correlations and blind spots that a human investor
        will almost always overlook. You increase the investor's 'vision' by 10x.
        You are the flashlight in the dark.
    """,
    # etc...
}

# -----------------------------
# 2) EXISTING CONSTANTS
# -----------------------------

PERSONAS = {
    "None": "",
    "Buffett": "You are Warren Buffett: value investing, moats, margin of safety, long-term discipline.",
    "Risk Officer": "You are a Chief Risk Officer: focus on liquidity, tail risk, concentration, compliance.",
    "Tech Strategist": "You are a pragmatic tech strategist: product cycles, infra, AI moats, competitive landscape.",
}

API_URL = os.getenv("EVITO_API_URL", "http://localhost:8081")
DEFAULT_TICKERS = ["TSLA", "AAPL", "NVDA", "SPY"]
STANDARD_CYCLES = [7, 21, 30, 90, 180, 252, 365]
RISK_COLORS = {"Low": "#2eb886", "Medium": "#daa038", "High": "#d9831f", "Critical": "#d14c41"}
DISABLE_NEWS = os.getenv("DISABLE_NEWS", "0") == "1"
QUEUE_PATH = Path("data/review_queue.jsonl")
LIB_PATH = Path("data/library.jsonl")
NEWS_SOURCES_PATH = Path("data/news_sources.jsonl")
CUSTOM_NEWS_PATH = Path("data/custom_news.jsonl")
PREBAKED_PATH = Path("data/prebaked_briefs.jsonl")
AI_UNIVERSE_PATH = Path("data/ai_universe.jsonl")
FEATURED_LIMIT = 5

EMBEDDER = SentenceTransformer("all-MiniLM-L6-v2")

MODEL_REGISTRY = [
    {
        "label": "GPT-4o",
        "provider": "openai",
        "model": "gpt-4o",
        "base_url": os.getenv("OPENAI_BASE", "https://api.openai.com/v1"),
        "api_key": os.getenv("OPENAI_API_KEY"),
    },
    {
        "label": "o1-preview",
        "provider": "openai",
        "model": "o1-preview",
        "base_url": os.getenv("OPENAI_BASE", "https://api.openai.com/v1"),
        "api_key": os.getenv("OPENAI_API_KEY"),
    },
    {
        "label": "xAI",
        "provider": "openai",
        "model": os.getenv("XAI_MODEL", "grok-2"),
        "base_url": os.getenv("XAI_BASE", "https://api.x.ai/v1"),
        "api_key": os.getenv("XAI_API_KEY"),
    },
    {
        "label": "Mistral",
        "provider": "openai",
        "model": os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
        "base_url": os.getenv("MISTRAL_BASE", "https://api.mistral.ai/v1"),
        "api_key": os.getenv("MISTRAL_API_KEY"),
    },
    {
        "label": "Anthropic",
        "provider": "anthropic",
        "model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
    },
]

# 🔥 DEBUG HER (etter lista)
print("DEBUG OPENAI KEY PRESENT:", bool(os.getenv("OPENAI_API_KEY")))
print("DEBUG OPENAI KEY STARTS WITH:", (os.getenv("OPENAI_API_KEY") or "")[:7])

PERSONAS = {
    "None": "",
    "Buffett": "You are Warren Buffett: value investing, moats, margin of safety, long-term discipline.",
    "Risk Officer": "You are a Chief Risk Officer: focus on liquidity, tail risk, concentration, compliance.",
    "Tech Strategist": "You are a pragmatic tech strategist: product cycles, infra, AI moats, competitive landscape.",
}

SLACK_BROADCAST_WEBHOOK = os.getenv("SLACK_BROADCAST_WEBHOOK")


def call_api(ticker: str, days: int):
    resp = requests.post(f"{API_URL}/analyze", json={"ticker": ticker, "days": days}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def risk_bar(score: int) -> str:
    filled = int(score / 10)
    return "█" * filled + "░" * (10 - filled)


def read_jsonl_safe(path: Path):
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def write_jsonl_append(path: Path, obj: dict):
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj) + "\n")


def fetch_news(ticker: str, limit: int = 5, enabled_sources=None):
    """
    Fetch headlines for ticker from custom JSONL + enabled RSS sources.
    """
    if DISABLE_NEWS:
        return []

    headlines = []

    # Custom curated news
    for obj in read_jsonl_safe(CUSTOM_NEWS_PATH):
        if obj.get("ticker", "").upper() == ticker.upper():
            headlines.append(
                {
                    "title": obj.get("title"),
                    "link": obj.get("link"),
                    "source": obj.get("source", "custom"),
                    "summary": obj.get("summary"),
                }
            )

    # RSS sources
    if enabled_sources is None:
        enabled_sources = []
    try:
        import feedparser  # Optional dep
    except ImportError:
        feedparser = None

    if feedparser:
        for src in enabled_sources:
            url = src.get("url")
            name = src.get("name", "rss")
            if not url:
                continue
            feed = feedparser.parse(url)
            for entry in feed.entries[:limit]:
                title = getattr(entry, "title", "")
                summary = getattr(entry, "summary", "")
                link = getattr(entry, "link", "")
                # Simple ticker filter: ticker symbol in title/summary
                if ticker.upper() in title.upper() or ticker.upper() in summary.upper():
                    headlines.append(
                        {"title": title, "link": link, "source": name, "summary": summary}
                    )

    return headlines[:limit]


def ensure_dirs():
    for p in [QUEUE_PATH, LIB_PATH, NEWS_SOURCES_PATH, CUSTOM_NEWS_PATH]:
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            p.touch()


def append_jsonl(path: Path, entry: dict):
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def read_jsonl(path: Path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_ai_universe():
    """
    Load AI universe entries from JSONL.
    Each line: {ticker, name, theme, rsi}
    """
    if not AI_UNIVERSE_PATH.exists():
        return []
    entries = []
    for line in AI_UNIVERSE_PATH.read_text().splitlines():
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except Exception:
            continue
    return entries


def classify_rsi(rsi):
    """Classify RSI into Overbought/Oversold/Neutral."""
    try:
        value = float(rsi)
    except Exception:
        return "Neutral"
    if value >= 70:
        return "Overbought"
    if value <= 30:
        return "Oversold"
    return "Neutral"


def load_prebaked_briefs():
    """
    Load pre-baked briefs from local JSONL.
    Each line: {ticker, persona, model, text}
    Returns list[dict]. Missing file -> [].
    """
    if not PREBAKED_PATH.exists():
        return []
    return read_jsonl(PREBAKED_PATH)


def embed_text(text: str):
    return EMBEDDER.encode(text, normalize_embeddings=True).tolist()


def upsert_to_library(entry: dict):
    # Placeholder: write to local library JSONL; swap with vector DB upsert as needed.
    append_jsonl(LIB_PATH, entry)


def infer_from_filename(filename: str):
    """
    Infer ticker/persona from a filename like TSLA_Buffett.md.
    Returns (ticker, persona).
    """
    stem = Path(filename).stem
    parts = stem.split("_")
    ticker = parts[0].upper() if parts else "UNK"
    persona = parts[1] if len(parts) > 1 else "None"
    return ticker, persona


def brief_from_risk(data: dict) -> str:
    bar = risk_bar(data.get("risk_score", 0))
    factors = data.get("factors", []) or ["No factors listed"]

    # Hent volatility/trend trygt fra enten toppnivå eller analysis-blokka
    vol = data.get("volatility") or data.get("analysis", {}).get("volatility", "n/a")
    trend = data.get("trend") or data.get("analysis", {}).get("trend", "n/a")

    lines = [
        f"Title: Risk Snapshot {data.get('ticker')} ({data.get('days')}d)",
        f"TL;DR: {data.get('risk_level')} risk, score {data.get('risk_score')}",
        f"Volatility: {vol} · Trend: {trend}",
        "Factors:",
    ]
    lines.extend([f"- {f}" for f in factors])
    lines.append(f"Score bar: {bar}")
    return "\n".join(lines)


def build_payload(data: dict, headlines: list[dict]) -> dict:
    return {
        "ticker": data.get("ticker"),
        "days": data.get("days"),
        "risk_score": data.get("risk_score"),
        "risk_level": data.get("risk_level"),
        "volatility": data.get("volatility"),
        "trend": data.get("trend"),
        "factors": data.get("factors", []),
        "headlines": headlines,
        "timestamp": data.get("timestamp"),
    }


def make_prompt(payload: dict, persona_text: str) -> tuple[str, str]:
    prompt = textwrap.dedent(
        f"""
        SYSTEM: You write concise tech/AI market briefs for investors. Use only provided data. No fabrications. Max 280 words.
        {persona_text}
        USER: Structured data: {json.dumps(payload)}
        Write:
        - Title (strong hook)
        - TL;DR (3 bullets)
        - Market Setup (1 short paragraph)
        - Why Now (1–2 short paragraphs)
        - Risks (bullets)
        - Watch List / Catalysts (bullets with timeframes)
        - Bottom Line (1 sentence, actionable)
        Tone: analytical, plain English, no hype.
        """
    ).strip()
    prompt_version = sha1(prompt.encode("utf-8")).hexdigest()[:10]
    return prompt, prompt_version


def call_model(entry: dict, prompt: str) -> str:
    provider = entry.get("provider")
    if provider == "openai":
        try:
            from openai import OpenAI
        except Exception:
            return "Model client missing; showing placeholder brief."
        client = OpenAI(base_url=entry.get("base_url"), api_key=entry.get("api_key"))
        resp = client.chat.completions.create(
            model=entry.get("model"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()
    if provider == "anthropic":
        try:
            import anthropic
        except Exception:
            return "Model client missing; showing placeholder brief."
        client = anthropic.Anthropic(api_key=entry.get("api_key"))
        resp = client.messages.create(
            model=entry.get("model"),
            max_tokens=800,
            temperature=0.4,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text.strip()
    return "Unsupported provider; placeholder brief."


def broadcast_slack(text: str):
    if not SLACK_BROADCAST_WEBHOOK:
        return False
    try:
        requests.post(SLACK_BROADCAST_WEBHOOK, json={"text": text}, timeout=5)
        return True
    except Exception:
        return False


st.set_page_config(page_title="EVITO News Stream", layout="wide")
st.title("📰 EVITO News & Risk Stream")
ensure_dirs()

tab_dashboard, tab_review, tab_pipelines = st.tabs(["Dashboard", "Review / Library", "Pipelines: IN / OUT"])

with tab_dashboard:
    with st.sidebar:
        st.markdown("### Controls")
        ticker = st.text_input("Ticker", "TSLA").upper()
        days = st.selectbox("Cycle (days)", STANDARD_CYCLES, index=STANDARD_CYCLES.index(30))
        auto = st.checkbox("Auto-refresh watchlist", value=False)
        interval = st.slider("Refresh every (sec)", 10, 120, 30)
        watchlist = st.multiselect("Watchlist", DEFAULT_TICKERS, DEFAULT_TICKERS)
        watchlist = watchlist or [ticker]
        show_news = st.checkbox("Show headlines (RSS)", value=not DISABLE_NEWS)
        debug_mode = st.checkbox("Debug: show model/brief info", value=False)

    # AI Universe section
    st.markdown("### 🔎 AI Universe – Overbought / Oversold")
    ai_universe = load_ai_universe()
    if ai_universe:
        df = pd.DataFrame(ai_universe)
        if not df.empty:
            df["state"] = df["rsi"].apply(classify_rsi)
            filter_text = st.text_input("Filter (ticker/name/theme)", "", key="ai_filter")
            if filter_text:
                name_col = df["name"].astype(str) if "name" in df else pd.Series([], dtype=str)
                theme_col = df["theme"].astype(str) if "theme" in df else pd.Series([], dtype=str)
                mask = (
                    df["ticker"].astype(str).str.contains(filter_text, case=False, na=False)
                    | name_col.str.contains(filter_text, case=False, na=False)
                    | theme_col.str.contains(filter_text, case=False, na=False)
                )
                df = df[mask]
            df = df.sort_values(by="rsi", ascending=False, na_position="last")
            cols = [c for c in ["ticker", "name", "theme", "rsi", "state"] if c in df.columns]
            st.dataframe(df[cols], use_container_width=True)
    else:
        st.caption("No ai_universe.jsonl found in data/.")

    cols = st.columns(max(1, len(watchlist)))

    # Featured strip (last 5 winners)
    lib_entries = read_jsonl(LIB_PATH)
    winners = [e for e in lib_entries if e.get("winner")]
    if winners:
        st.markdown("#### ⭐ Featured Briefs (last 5 winners)")
        for e in winners[-FEATURED_LIMIT:][::-1]:
            st.markdown(
                f"- **{e['ticker']} ({e['days']}d)** • model: {e.get('model')} • persona: {e.get('persona')} • {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(e.get('timestamp', 0)))}"
            )

    for i, t in enumerate(watchlist):
        try:
            data = call_api(t, days)
            color = RISK_COLORS.get(data.get("risk_level"), "#439fe0")
            with cols[i]:
                st.markdown(f"#### {t} · {data['days']}d")
                st.markdown(f"**{data['risk_level']}** — Score: {data['risk_score']}  {risk_bar(data['risk_score'])}")
                vol = data.get("volatility") or data.get("analysis", {}).get("volatility", "n/a")
                trend = data.get("trend") or data.get("analysis", {}).get("trend", "n/a")
                st.markdown(f"Volatility: `{vol}` · Trend: `{trend}`")
                st.markdown("**Factors**")
                factors = data.get("factors", []) or []
                if factors:
                    for f in factors:
                        if isinstance(f, dict):
                            fname = f.get("name", "Factor")
                            fscore = f.get("score", "n/a")
                            st.markdown(f"- **{fname}**: `{fscore}`")
                        else:
                            st.markdown(f"- {f}")
                else:
                    st.markdown("- No factors listed")
                # News sources controls
                sources = read_jsonl_safe(NEWS_SOURCES_PATH)
                enabled_labels = [s.get("name") for s in sources]
                enabled_selection = st.multiselect("Enabled news sources", enabled_labels, enabled_labels, key=f"sources_{t}")
                enabled_sources = [s for s in sources if s.get("name") in enabled_selection]

                # Add a new source
                with st.expander("Add news source"):
                    new_name = st.text_input("Source name", key=f"src_name_{t}")
                    new_url = st.text_input("Source URL", key=f"src_url_{t}")
                    if st.button("Add source", key=f"add_src_{t}"):
                        if new_name and new_url:
                            write_jsonl_append(NEWS_SOURCES_PATH, {"name": new_name, "url": new_url, "type": "rss"})
                            st.success("Source added. Reload to use it.")
                        else:
                            st.warning("Provide both name and URL.")

                headlines = fetch_news(t, enabled_sources=enabled_sources) if (show_news and not DISABLE_NEWS) else []
                if headlines:
                    st.markdown("**Headlines**")
                    for h in headlines:
                        st.markdown(f"- [{h['title']}]({h['link']})")

                # Debate / Brief generation
                st.markdown("### 🤖 AI Debate")
                prebaked_all = load_prebaked_briefs()
                prebaked_for_ticker = [b for b in prebaked_all if b.get("ticker", "").upper() == t.upper()]

                if debug_mode:
                    st.caption("Debug: showing model/brief info")

                persona_choice = st.selectbox("Persona", list(PERSONAS.keys()), index=0, key=f"persona_{t}")

                # Persona-based Markdown template creation into briefs_in/
                if st.button(f"Create Persona MD for {t}", key=f"persona_md_{t}"):
                    template = f"""# {t} · Persona: {persona_choice}

## Raw thesis
(Paste the raw investment thesis here)

## Persona’s take
(Write from the perspective of {persona_choice})

## Risks / Edge cases
(List risks, weak assumptions, edge cases)

## Audit / Validation
(Citations, data checks, sanity checks)
"""
                    filename = f"{t}_{persona_choice}.md".replace(" ", "_")
                    write_md(BRIEFS_IN, filename, template)
                    st.success(f"Saved to briefs_in as {filename}")

                # If we have pre-baked briefs for this ticker, render them and skip live calls
                if prebaked_for_ticker:
                    st.caption("Pre-baked briefs per persona from data/prebaked_briefs.jsonl")
                    # Group by persona for clean rendering
                    persona_map = {}
                    for b in prebaked_for_ticker:
                        persona_map.setdefault(b.get("persona", "None"), []).append(b)
                    for persona_key, briefs_list in persona_map.items():
                        for idx, brief in enumerate(briefs_list):
                            st.markdown(f"**{persona_key}** ({brief.get('model', 'unknown')})")
                            st.text_area(
                                "Brief",
                                brief.get("text", ""),
                                height=220,
                                key=f"prebrief_{t}_{persona_key}_{idx}",
                            )
                            st.caption("Context used: pre-baked file")
                            c1, c2, c3 = st.columns(3)
                            meta = {
                                "id": str(uuid.uuid4()),
                                "ticker": t,
                                "days": days,
                                "model": brief.get("model", "prebaked"),
                                "persona": persona_key,
                                "timestamp": time.time(),
                                "text": brief.get("text", ""),
                                "prompt_version": "prebaked",
                                "headlines": [h["title"] for h in headlines],
                            }
                            with c1:
                                if st.button(f"Queue ({persona_key})", key=f"queue_pre_{t}_{persona_key}_{idx}"):
                                    append_jsonl(QUEUE_PATH, meta)
                                    st.success("Queued for review")
                            with c2:
                                if st.button(f"Save DB ({persona_key})", key=f"save_pre_{t}_{persona_key}_{idx}"):
                                    vec = embed_text(meta["text"])
                                    meta["embedding"] = vec
                                    upsert_to_library(meta)
                                    st.success("Saved to library (pre-baked).")
                            with c3:
                                if st.button(f"Mark winner ({persona_key})", key=f"winner_pre_{t}_{persona_key}_{idx}"):
                                    vec = embed_text(meta["text"])
                                    meta["embedding"] = vec
                                    meta["winner"] = True
                                    upsert_to_library(meta)
                                    broadcast_slack(f"🏆 Featured Brief ({t}): {persona_key}\n{meta['text'][:500]}...")
                                    st.success("Winner saved (pre-baked) and broadcast attempted.")
                    # Skip live model generation when pre-baked briefs exist
                    st.markdown(f"<div style='color:{color};font-weight:600'>⚡️ Powered by EVITO AI</div>", unsafe_allow_html=True)
                    continue

                available_models = [m for m in MODEL_REGISTRY if m.get("api_key")]
                if debug_mode:
                    st.write("DEBUG MODELS:", [(m["label"], bool(m.get("api_key"))) for m in available_models])

                model_labels = [m["label"] for m in available_models]

                if not available_models:
                    st.info("No models configured (no API keys). Showing mock brief.")
                    brief = MOCK_BRIEFS.get(t.upper(), MOCK_BRIEFS["__DEFAULT__"])
                    st.text_area("Brief (mock)", brief, height=220, key=f"brief_mock_{t}")
                    st.caption("Context used: None (mock)")
                    c1, c2, c3 = st.columns(3)
                    meta = {
                        "id": str(uuid.uuid4()),
                        "ticker": t,
                        "days": days,
                        "model": "mock",
                        "persona": "None",
                        "timestamp": time.time(),
                        "text": brief,
                        "prompt_version": "mock",
                        "headlines": [h["title"] for h in headlines],
                    }
                    with c1:
                        if st.button(f"Queue (mock)", key=f"queue_brief_mock_{t}"):
                            append_jsonl(QUEUE_PATH, meta)
                            st.success("Queued for review")
                    with c2:
                        if st.button(f"Save DB (mock)", key=f"save_brief_mock_{t}"):
                            vec = embed_text(brief)
                            meta["embedding"] = vec
                            upsert_to_library(meta)
                            st.success("Saved to library (local). Replace stub with vector DB upsert.")
                    with c3:
                        if st.button(f"Mark winner (mock)", key=f"winner_mock_{t}"):
                            vec = embed_text(brief)
                            meta["embedding"] = vec
                            meta["winner"] = True
                            upsert_to_library(meta)
                            broadcast_slack(f"🏆 Featured Brief ({t}): mock\n{brief[:500]}...")
                            st.success("Winner saved (local) and broadcast attempted.")
                    # Skip model loop when none configured
                    continue

                selected_models = st.multiselect(
                    "Models", model_labels, model_labels[: min(2, len(model_labels))], key=f"models_{t}"
                )

                include_news = bool(headlines)
                payload = build_payload(data, headlines)

                if st.button(f"Generate briefs for {t}", key=f"gen_{t}"):
                    for label in selected_models:
                        model = next((m for m in available_models if m["label"] == label), None)
                        if not model:
                            st.warning(f"Model {label} not configured.")
                            continue
                        persona_text = PERSONAS.get(persona_choice, "")
                        prompt, prompt_version = make_prompt(payload, persona_text)
                        with st.spinner(f"Generating {label}..."):
                            brief = call_model(model, prompt)
                            if (not brief) or ("Model client missing" in brief) or ("Unsupported provider" in brief):
                                brief = MOCK_BRIEFS.get(t.upper(), MOCK_BRIEFS["__DEFAULT__"])

                        context_badge = f"Persona: {persona_choice} • News: {'on' if include_news else 'off'} • Prompt: {prompt_version}"
                        st.markdown(f"**{label}** — {context_badge}")
                        st.text_area("Brief", brief, height=220, key=f"brief_out_{label}_{t}")
                        st.caption("Context used: " + (", ".join([h['title'] for h in headlines]) if headlines else "None"))

                        # Actions per brief
                        c1, c2, c3 = st.columns(3)
                        meta = {
                            "id": str(uuid.uuid4()),
                            "ticker": t,
                            "days": days,
                            "model": label,
                            "persona": persona_choice,
                            "timestamp": time.time(),
                            "text": brief,
                            "prompt_version": prompt_version,
                            "headlines": [h["title"] for h in headlines],
                        }
                        with c1:
                            if st.button(f"Queue ({label})", key=f"queue_brief_{label}_{t}"):
                                append_jsonl(QUEUE_PATH, meta)
                                st.success("Queued for review")
                        with c2:
                            if st.button(f"Save DB ({label})", key=f"save_brief_{label}_{t}"):
                                vec = embed_text(brief)
                                meta["embedding"] = vec
                                upsert_to_library(meta)
                                st.success("Saved to library (local). Replace stub with vector DB upsert.")
                        with c3:
                            if st.button(f"Mark winner ({label})", key=f"winner_{label}_{t}"):
                                vec = embed_text(brief)
                                meta["embedding"] = vec
                                meta["winner"] = True
                                upsert_to_library(meta)
                                broadcast_slack(f"🏆 Featured Brief ({t}): {label}\n{brief[:500]}...")
                                st.success("Winner saved (local) and broadcast attempted.")

                st.markdown(f"<div style='color:{color};font-weight:600'>⚡️ Powered by EVITO AI</div>", unsafe_allow_html=True)
        except Exception as e:
            with cols[i]:
                st.error(f"{t}: {e}")

    if auto:
        time.sleep(interval)
        st.rerun()

with tab_review:
    st.markdown("### Review Queue")
    queue_entries = read_jsonl(QUEUE_PATH)
    if not queue_entries:
        st.info("Queue is empty.")
    else:
        selected_ids = st.multiselect(
            "Select entries to save",
            options=[e["id"] for e in queue_entries],
            format_func=lambda i: next(e for e in queue_entries if e["id"] == i)["ticker"],
        )
        if st.button("Save selected to DB (with embeddings)", key="save_selected"):
            for e in queue_entries:
                if e["id"] in selected_ids:
                    vec = embed_text(e["text"])
                    entry = dict(e)
                    entry["embedding"] = vec
                    upsert_to_library(entry)
            st.success("Selected entries saved (local stub).")
            # Remove saved from queue
            remaining = [e for e in queue_entries if e["id"] not in selected_ids]
            QUEUE_PATH.unlink(missing_ok=True)
            for e in remaining:
                append_jsonl(QUEUE_PATH, e)
        st.markdown("#### Queue Items")
        for e in queue_entries:
            with st.expander(f"{e['ticker']} ({e['days']}d) • {e['id'][:8]}"):
                st.write(e["text"])

    st.markdown("### Library Snapshot (last 20)")
    lib_entries = read_jsonl(LIB_PATH)
    if not lib_entries:
        st.info("Library is empty.")
    else:
        for e in lib_entries[-20:][::-1]:
            st.markdown(f"- **{e['ticker']} ({e['days']}d)** model: {e.get('model')} persona: {e.get('persona')} at {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(e.get('timestamp', 0)))}")

with tab_pipelines:
    st.markdown("### Pipelines: IN / OUT")
    st.caption("Drop Markdown files into data/*_in, move them to *_out when processed, and promote OUT briefs to the library.")

    sources = [
        ("NEWS", NEWS_IN, NEWS_OUT),
        ("BRIEFS", BRIEFS_IN, BRIEFS_OUT),
        ("DEBATES", DEBATES_IN, DEBATES_OUT),
    ]

    for label, in_dir, out_dir in sources:
        st.markdown(f"#### {label}")
        col_in, col_out = st.columns(2)

        with col_in:
            st.markdown("**IN**")
            in_files = list_md(in_dir)
            in_options = [f["name"] for f in in_files]
            sel_in = st.selectbox(f"{label} IN files", ["(none)"] + in_options, key=f"{label}_in_sel")
            if sel_in != "(none)":
                path = next(f["path"] for f in in_files if f["name"] == sel_in)
                content = read_md(path)
                st.text_area("Content", content, height=220, key=f"{label}_in_content_{sel_in}")
                if st.button("Send to OUT", key=f"{label}_move_{sel_in}"):
                    move_md(path, out_dir)
                    st.success("Moved to OUT")
                    st.experimental_rerun()

        with col_out:
            st.markdown("**OUT**")
            out_files = list_md(out_dir)
            out_options = [f["name"] for f in out_files]
            sel_out = st.selectbox(f"{label} OUT files", ["(none)"] + out_options, key=f"{label}_out_sel")
            if sel_out != "(none)":
                path = next(f["path"] for f in out_files if f["name"] == sel_out)
                content = read_md(path)
                st.text_area("Content", content, height=220, key=f"{label}_out_content_{sel_out}")
                if label == "BRIEFS":
                    if st.button("Promote to library (audited brief)", key=f"{label}_promote_{sel_out}"):
                        ticker_inferred, persona_inferred = infer_from_filename(sel_out)
                        meta = {
                            "id": str(uuid.uuid4()),
                            "ticker": ticker_inferred,
                            "days": 0,
                            "model": "external-llm",
                            "persona": persona_inferred,
                            "timestamp": time.time(),
                            "text": content,
                            "prompt_version": "persona_md_v1",
                            "headlines": [],
                            "audited": True,
                        }
                        vec = embed_text(content)
                        meta["embedding"] = vec
                        upsert_to_library(meta)
                        st.success("Promoted to library as audited brief.")
