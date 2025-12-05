#!/usr/bin/env python3
"""
EVITO Slack Risk Bot (MVP)

- Listens to the /risk slash command
- Parses input like:
    /risk
    /risk TSLA
    /risk TSLA 120
    /risk 75
- Returns a clean text-based risk snapshot (dummy data for now)
"""

import os
import re
from pathlib import Path

from dotenv import /.env
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# -------------------------------------------------------------------
# Environment / config
# -------------------------------------------------------------------
# Repo layout (simplified):
# EVITO/
#   .env              ← her ligger nøklene dine
#   services/
#     slackbot/
#       slack_risk_bot.py
#
# Vi peker eksplisitt på EVITO/.env slik at det ikke er tvil.
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]  # .../EVITO
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
FINNHUB_KEY = os.getenv("FINNHUB_KEY")
if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN or not SLACK_SIGNING_SECRET:
    raise RuntimeError(
        "Missing one of SLACK_BOT_TOKEN / SLACK_APP_TOKEN / SLACK_SIGNING_SECRET "
        "in environment. Set them before running this script."
    )

app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
)


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def is_number(value: str) -> bool:
    """Return True if value looks like a number (int or float)."""
    return bool(re.fullmatch(r"\d+(\.\d+)?", value))


def get_risk_snapshot(ticker: str, level: str | None = None) -> str:
    """
    Dummy risk snapshot generator.

    TODO:
    - Replace this with a real call to your risk engine, for example:
        from services.risk.risk_bot import get_risk_for_ticker
    """
    ticker = ticker.upper()

    # Dummy values – just so you see something working in Slack.
    insider_risk = "48% (normal)"
    overbought_state = "NEUTRAL"
    volatility = "8.2% (stable)"
    flow = "Mild accumulation"
    macro = "Moderate"

    lines = []
    lines.append(f"*{ticker}* — 90d Risk Snapshot")
    lines.append(f"• Insider risk: {insider_risk}")
    lines.append(f"• Overbought/Oversold: {overbought_state}")
    lines.append(f"• Volatility range: {volatility}")
    lines.append(f"• Institutional flow: {flow}")
    lines.append(f"• Macro sensitivity: {macro}")

    if level is not None:
        lines.append(f"• Price level provided: {level}")

    lines.append("")
    lines.append("Skriv 1, 2 eller 3 for valg:")
    lines.append("1. Følg – daglig oppdatering")
    lines.append("2. Investor Relations")
    lines.append("3. Send til EVITO.AI for dyp analyse")

    return "\n".join(lines)


# -------------------------------------------------------------------
# /risk slash command handler
# -------------------------------------------------------------------

@app.command("/risk")
def handle_risk_command(ack, respond, command):
    """
    Examples:
      /risk
      /risk TSLA
      /risk TSLA 120
      /risk 75
    """
    # Always ack first so Slack knows we received the command
    ack()

    text = (command.get("text") or "").strip()
    parts = [p for p in text.split() if p]

    # No arguments: show help/usage
    if len(parts) == 0:
        respond(
            "Gi meg en ticker eller et nivå.\n"
            "Eksempler:\n"
            "• `/risk TSLA`\n"
            "• `/risk BTC`\n"
            "• `/risk TSLA 120`\n"
            "• `/risk 75`"
        )
        return

    # One argument: could be ticker OR a number
    if len(parts) == 1:
        arg = parts[0]

        # If it looks like a number, ask how to interpret it
        if is_number(arg):
            respond(
                f"Jeg ser du sendte tallet *{arg}*.\n"
                "Skal jeg tolke det som:\n"
                "1. Price target (bruk: `/risk TSLA "
                f"{arg}`)\n"
                f"2. Risk filter (tickere med risk > {arg})?\n"
                "3. Noe annet? Forklar kort."
            )
            return
        else:
            # Treat as ticker only
            ticker = arg.upper()
            reply = get_risk_snapshot(ticker)
            respond(reply)
            return

    # Two or more arguments: assume TICKER [LEVEL]
    ticker = parts[0].upper()
    level = None

    if len(parts) >= 2 and is_number(parts[1]):
        level = parts[1]

    # If second arg isn't numeric, we ignore it for now
    reply = get_risk_snapshot(ticker, level)
    respond(reply)


# -------------------------------------------------------------------
# Main entrypoint
# -------------------------------------------------------------------

if __name__ == "__main__":
    print("⚡️ Starting EVITO Slack Risk Bot (MVP)...")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()


