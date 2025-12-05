import os
import requests
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from datetime import datetime
load_dotenv()
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
# ============================================================
# MARKET CYCLES EDUCATION DATA
# ============================================================
MARKET_CYCLES = {
    # Short-term trading cycles
    "7": {"name": "Weekly", "reason": "Trading week cycle", "type": "✅ Standard"},
    "14": {"name": "Bi-weekly", "reason": "Options expiry cycle", "type": "✅ Standard"},
    "21": {"name": "Monthly Trading", "reason": "~Trading month (21 business days)", "type": "✅ Standard"},
    "30": {"name": "Calendar Month", "reason": "Monthly reporting period", "type": "✅ Standard"},
    # Medium-term cycles
    "60": {"name": "Bi-monthly", "reason": "2-month trend analysis", "type": "✅ Standard"},
    "90": {"name": "Quarterly", "reason": "Earnings cycle (Q1, Q2, Q3, Q4)", "type": "✅ Standard"},
    "180": {"name": "Semi-Annual", "reason": "Half-year business cycle", "type": "✅ Standard"},
    # Long-term cycles
    "252": {"name": "Trading Year", "reason": "Full year of trading days", "type": "✅ Standard"},
    "365": {"name": "Calendar Year", "reason": "Annual reporting cycle", "type": "✅ Standard"},
    "730": {"name": "2 Years", "reason": "Long-term trend analysis", "type": "✅ Standard"},
}
ODD_TIMEFRAMES = [
    40, 50, 70, 80, 100, 110, 120, 140, 150, 160, 170, 190,
    200, 210, 220, 240, 260, 280, 300, 320, 340
]
# ============================================================
# HELPER FUNCTIONS
# ============================================================
def analyze_timeframe(days):
    """
    Analyzes if the requested timeframe aligns with market cycles.
    Returns educational message if it's an odd choice.
    """
    days_str = str(days)
    # Perfect match - no education needed
    if days_str in MARKET_CYCLES:
        return {
            "is_standard": True,
            "message": None,
            "cycle_info": MARKET_CYCLES[days_str]
        }
    # Odd timeframe - educate!
    if days in ODD_TIMEFRAMES or days > 400:
        # Find closest standard timeframe
        closest = min(MARKET_CYCLES.keys(),
                     key=lambda x: abs(int(x) - days))
        cycle_info = MARKET_CYCLES[closest]
        return {
            "is_standard": False,
            "requested_days": days,
            "suggested_days": int(closest),
            "message": f"""*Why Market Cycles Matter*
Markets operate in natural rhythms driven by institutional activity:
• 📅 *Earnings Reports* — Quarterly disclosures create inflection points
• 📊 *Economic Data* — Monthly and quarterly releases drive sentiment
• 💼 *Institutional Rebalancing* — Funds adjust at cycle boundaries
• 🌍 *Seasonal Patterns* — Calendar effects influence market behavior
*The Challenge with {days}-Day Analysis*
Non-standard timeframes can produce misleading patterns because:
• They don't align with earnings cycles
• Institutional traders don't use them
• Patterns may not repeat reliably
• Backtests won't match forward results
*Institutional Standard: {closest} Days*
This period captures the _{cycle_info['name']}_ cycle, ensuring your analysis aligns with how professional traders view the market.""",
            "cycle_info": cycle_info
        }
    # Close enough to standard - allow but inform
    return {
        "is_standard": False,
        "message": f"📊 Analyzing {days} days. Note: Standard cycles are 7, 21, 30, 90, 180, 252, or 365 days.",
        "cycle_info": None
    }
def is_education_question(text):
    """Detect if user is asking an education question vs risk analysis"""
    education_keywords = [
        "why", "what is", "explain", "how does", "what does", "tell me about",
        "help me understand", "what's", "why is", "why do", "when should",
        "difference between", "better to"
    ]
    return any(keyword in text.lower() for keyword in education_keywords)
def call_risk_api(ticker, days=90):
    """Call the Risk API for analysis"""
    try:
        print(f"🔗 Calling Risk API: http://localhost:8081/analyze?ticker={ticker}&days={days}")
        response = requests.get(
            "http://localhost:8081/analyze",
            params={"ticker": ticker, "days": days},
            timeout=10
        )
        print(f"📥 API Response Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response: {data}")
            return data
        else:
            print(f"❌ API returned status {response.status_code}: {response.text}")
            return None
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: Cannot reach Risk API at localhost:8081")
        return None
    except Exception as e:
        print(f"❌ Error calling Risk API: {e}")
        return None
def get_risk_insight(risk_level, ticker):
    """Generate contextual insight based on risk level"""
    insights = {
        "Low": f"{ticker} shows stable patterns with minimal volatility. Suitable for conservative positions.",
        "Medium": f"{ticker} displays moderate risk characteristics. Consider position sizing and stops.",
        "High": f"{ticker} exhibits elevated risk metrics. Recommended for experienced traders only.",
        "Critical": f"{ticker} shows extreme volatility. High risk of significant loss. Proceed with caution."
    }
    return insights.get(risk_level, f"Analysis complete for {ticker}.")
def format_risk_response(ticker, days, data):
    """Format risk analysis into premium Slack blocks"""
    risk_score = data.get("risk_score", 0)
    risk_level = data.get("risk_level", "Unknown")
    analysis = data.get("analysis", {})
    factors = data.get("factors", [])
    # Premium emoji mapping
    emoji_map = {
        "Low": "🟢",
        "Medium": "🟡",
        "High": "🟠",
        "Critical": "🔴"
    }
    emoji = emoji_map.get(risk_level, "⚪")
    # Risk level colors
    color_map = {
        "Low": "#2eb886",      # Green
        "Medium": "#daa038",   # Yellow/Gold
        "High": "#e2511c",     # Orange
        "Critical": "#cc1f1a"  # Red
    }
    color = color_map.get(risk_level, "#cccccc")
    # Confidence indicator
    confidence = analysis.get("confidence", 0)
    confidence_bars = "█" * int(confidence * 10) + "░" * (10 - int(confidence * 10))
    # Trend indicator
    trend = analysis.get("trend", "neutral")
    trend_emoji = "📈" if trend == "bullish" else "📉" if trend == "bearish" else "➡️"
    # Build premium blocks
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{emoji} {ticker} Risk Assessment",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Risk Level*\n{risk_level}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Risk Score*\n{risk_score}/100"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Analysis Period*\n{days} days"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Market Trend*\n{trend_emoji} {trend.title()}"
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Key Metrics*\n"
                       f"• Volatility: `{analysis.get('volatility', 0):.1f}%`\n"
                       f"• Confidence: {confidence_bars} `{confidence:.0%}`"
            }
        }
    ]
    # Add factors if available
    if factors:
        factors_text = "*Risk Factors*\n"
        for factor in factors[:3]:  # Top 3 factors
            score = factor.get('score', 0)
            name = factor.get('name', 'Unknown')
            bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
            factors_text += f"• {name}: {bar} `{score}`\n"
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": factors_text
            }
        })
    # Add action buttons
    blocks.extend([
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 Detailed Analysis",
                        "emoji": True
                    },
                    "value": f"detailed_{ticker}_{days}",
                    "action_id": "show_detailed_analysis",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📈 Historical View",
                        "emoji": True
                    },
                    "value": f"history_{ticker}",
                    "action_id": "show_history"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔔 Set Alert",
                        "emoji": True
                    },
                    "value": f"alert_{ticker}",
                    "action_id": "set_alert"
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"⚡️ Powered by EVITO AI  •  Updated: <!date^{int(datetime.now().timestamp())}^{{date_short_pretty}} at {{time}}|just now>"
                }
            ]
        }
    ])
    return {
        "text": f"Risk analysis for {ticker}",
        "blocks": blocks,
        "attachments": [
            {
                "color": color,
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"_{get_risk_insight(risk_level, ticker)}_"
                        }
                    }
                ]
            }
        ]
    }
# ============================================================
# SLACK COMMAND HANDLER
# ============================================================
@app.command("/risk")
def handle_risk_command(ack, command, say):
    """Handle /risk slash command"""
    ack()  # Acknowledge immediately
    text = command.get("text", "").strip()
    user = command.get("user_id")
    print(f"📥 /risk command received: '{text}' from user {user}")
    if not text:
        say({
            "text": "How to use /risk",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "⚡️ EVITO AI Risk Intelligence",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Professional-grade risk analysis at your fingertips.*\n\n"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Quick Start Commands*"
                    },
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Risk Analysis*\n`/risk TICKER [DAYS]`"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Market Education*\n`/risk Why 90 days?`"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Example Analyses*\n"
                               "• `/risk TSLA` — Standard quarterly analysis\n"
                               "• `/risk AAPL 180` — Semi-annual risk assessment\n"
                               "• `/risk NVDA 365` — Full trading year view"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "💎 Premium AI-powered risk intelligence  •  Real-time market analysis"
                        }
                    ]
                }
            ]
        })
        return
    # Check if it's an education question
    if is_education_question(text):
        say("🤔 Analyzing your question...")
        try:
            response = requests.post(
                "http://localhost:8082/ask",
                json={"question": text},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "I couldn't generate an answer.")
                say({
                    "text": "Market Education",
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": "🎓 Market Intelligence",
                                "emoji": True
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": answer
                            }
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"📚 Based on {data.get('context_used', 0)} institutional knowledge sources  •  ⚡️ Powered by EVITO AI"
                                }
                            ]
                        }
                    ]
                })
            else:
                say({
                    "text": "Education service unavailable",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "⚠️ *Education Service Unavailable*\n\nThe AI education service isn't running. Start it with:\n```python services/market_education/rag_service.py```"
                            }
                        }
                    ]
                })
        except Exception as e:
            print(f"Error calling education service: {e}")
            say({
                "text": "Error",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "❌ Unable to process education request. Please try again."
                        }
                    }
                ]
            })
        return
    # Parse ticker and days from command
    parts = text.upper().split()
    ticker = parts[0]
    # Try to parse days (default to 90)
    days = 90
    if len(parts) > 1:
        try:
            days = int(parts[1])
        except ValueError:
            say(f"⚠️ Invalid days value: '{parts[1]}'. Using default 90 days.")
            days = 90
    print(f"   Analyzing {ticker} for {days} days")
    # 🎓 EDUCATIONAL CHECK
    timeframe_analysis = analyze_timeframe(days)
    # If it's an odd timeframe, educate first!
    if not timeframe_analysis["is_standard"] and timeframe_analysis.get("suggested_days"):
        suggested = timeframe_analysis["suggested_days"]
        say({
            "text": f"Market Intelligence: {days}-day Analysis Review",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🎓 Market Cycle Intelligence",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Analysis Period Review: {days} Days*\n\n"
                               f"Our AI has detected that your requested timeframe doesn't align "
                               f"with institutional market cycles. This may result in less reliable patterns."
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": timeframe_analysis["message"]
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🎯 Recommended Alternative*\n"
                               f"*{suggested} days* — _{timeframe_analysis['cycle_info']['name']}_\n"
                               f"_{timeframe_analysis['cycle_info']['reason']}_"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": f"✅ Use {suggested}-Day Analysis",
                                "emoji": True
                            },
                            "value": f"analyze_{ticker}_{suggested}",
                            "action_id": "use_suggested_cycle",
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": f"Continue with {days} Days",
                                "emoji": True
                            },
                            "value": f"analyze_{ticker}_{days}",
                            "action_id": "use_original_cycle"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📚 Learn More",
                                "emoji": True
                            },
                            "value": "learn_cycles",
                            "action_id": "learn_market_cycles"
                        }
                    ]
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "💡 EVITO AI recommendations based on institutional trading patterns"
                        }
                    ]
                }
            ]
        })
        return
    # Standard timeframe - proceed with analysis
    if timeframe_analysis.get("cycle_info"):
        cycle_name = timeframe_analysis["cycle_info"]["name"]
        say(f"⚡️ Analyzing {ticker} over {days} days ({cycle_name} cycle)...")
    else:
        say(f"⚡️ Analyzing {ticker} over {days} days...")
    # Call Risk API
    data = call_risk_api(ticker, days)
    if data:
        response = format_risk_response(ticker, days, data)
        say(response)
    else:
        say({
            "text": "Analysis Error",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"❌ *Unable to Analyze {ticker}*\n\nPlease verify:\n"
                               f"• Ticker symbol is valid\n"
                               f"• Risk API is running: `python services/risk_bot_api/evito_api_server.py`"
                    }
                }
            ]
        })
# ============================================================
# BUTTON ACTION HANDLERS
# ============================================================
@app.action("use_suggested_cycle")
def handle_suggested_cycle(ack, body, say):
    """User clicked to use the suggested cycle"""
    ack()
    value = body["actions"][0]["value"]
    _, ticker, days = value.split("_")
    days = int(days)
    cycle_info = MARKET_CYCLES.get(str(days), {})
    cycle_name = cycle_info.get("name", "")
    say(f"✅ Excellent choice! Analyzing {ticker} over {days} days ({cycle_name} cycle)...")
    # Call Risk API
    data = call_risk_api(ticker, days)
    if data:
        response = format_risk_response(ticker, days, data)
        say(response)
    else:
        say(f"❌ Could not analyze {ticker}.")
@app.action("use_original_cycle")
def handle_original_cycle(ack, body, say):
    """User clicked to continue with original cycle"""
    ack()
    value = body["actions"][0]["value"]
    _, ticker, days = value.split("_")
    days = int(days)
    say(f"📊 Proceeding with {days} days analysis for {ticker}...")
    # Call Risk API
    data = call_risk_api(ticker, days)
    if data:
        response = format_risk_response(ticker, days, data)
        say(response)
    else:
        say(f"❌ Could not analyze {ticker}.")
@app.action("learn_market_cycles")
def handle_learn_cycles(ack, say):
    """User clicked to learn more about market cycles"""
    ack()
    say({
        "text": "Market Cycles Education",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📚 Understanding Market Cycles",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Why Market Cycles Matter*\n\n"
                           "Markets don't move randomly — they follow natural rhythms driven by institutional activity:\n\n"
                           "• 📅 *Earnings Reports* — Quarterly disclosures (every 90 days)\n"
                           "• 📊 *Economic Data* — Monthly and quarterly releases\n"
                           "• 💼 *Institutional Rebalancing* — Funds adjust quarterly/annually\n"
                           "• 🌍 *Seasonal Patterns* — Calendar effects and tax seasons"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*The Problem with Random Timeframes*\n\n"
                           "Using non-standard periods (like 80 or 143 days) can:\n"
                           "• Create false patterns that don't repeat\n"
                           "• Miss key cycle boundaries (earnings releases)\n"
                           "• Misalign with institutional analysis windows\n"
                           "• Lead to incorrect trading conclusions"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*Short-term Trading*\n• 7 days — Weekly cycle\n• 21 days — Trading month\n• 30 days — Calendar month"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Medium-term Business*\n• 90 days — Quarterly earnings\n• 180 days — Semi-annual trends"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Long-term Strategic*\n• 252 days — Trading year\n• 365 days — Calendar year\n• 730 days — 2-year trend"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*💡 Pro Tip*\nWhen in doubt, use 90 days — it aligns with earnings and captures meaningful trends."
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🎓 EVITO AI Market Intelligence  •  Institutional-grade education"
                    }
                ]
            }
        ]
    })
# Stub handlers for premium buttons
@app.action("show_detailed_analysis")
def handle_detailed_analysis(ack, say):
    ack()
    say("📊 *Detailed Analysis*\n\n_This feature is coming soon. It will provide in-depth technical analysis, sector comparisons, and historical performance metrics._")
@app.action("show_history")
def handle_history(ack, say):
    ack()
    say("📈 *Historical View*\n\n_This feature is coming soon. It will display risk trends over time with interactive charts._")
@app.action("set_alert")
def handle_alert(ack, say):
    ack()
    say("🔔 *Set Alert*\n\n_This feature is coming soon. You'll be able to set custom risk level alerts and receive notifications._")
# ============================================================
# REGULAR MESSAGE HANDLER (OPTIONAL)
# ============================================================
@app.event("message")
def handle_message(event, say):
    """Handle regular messages (optional)"""
    text = event.get("text", "")
    # Ignore bot messages
    if event.get("bot_id"):
        return
    print(f"📥 Message received: '{text}'")
# ============================================================
# START THE BOT
# ============================================================
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    print("\n" + "="*60)
    print("⚡️ EVITO AI - Premium Risk Intelligence Bot")
    print("="*60)
    print("\n💎 Features:")
    print("  • Professional risk analysis")
    print("  • Market cycle education")
    print("  • Real-time insights")
    print("  • Interactive intelligence")
    print("\n💡 Commands:")
    print("  /risk TICKER           - Quarterly analysis")
    print("  /risk TICKER DAYS      - Custom timeframe")
    print("  /risk [question]       - Market education")
    print("\n" + "="*60 + "\n")
    handler.start()

