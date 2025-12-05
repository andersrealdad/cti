"""
Slack Block Kit Formatter - Quantum Nordic OS Style
Premium tech-human fusion with neon accents
"""
from datetime import datetime
from color_guide import (
    get_risk_color,
    get_risk_glyph,
    get_moat_color,
    get_moat_glyph,
    get_slack_color_for_risk,
    format_panel_header,
    format_consensus_message,
    BRAND_COLORS,
    PANEL_COLORS
)
# =============================================
# EVITO RISK ANALYSIS BLOCKS - QUANTUM NORDIC OS
# =============================================
def format_risk_analysis(result):
    """
    Format EVITO risk analysis in Quantum Nordic OS style
    Args:
        result (dict): Output from EVITO API /analyze endpoint
    Returns:
        dict: Slack blocks JSON with brand styling
    """
    ticker = result.get('ticker', 'UNKNOWN')
    risk_score = result.get('risk_score', 50)
    factors = result.get('factors', [])
    verdict = result.get('verdict', '')
    recommendation = result.get('recommendation', '')
    horizon = result.get('horizon', 30)
    # Get brand glyph and color
    glyph = get_risk_glyph(risk_score)
    color = get_slack_color_for_risk(risk_score)
    # Build factors list with glyphs
    factors_text = '\n'.join([f"◆ {factor}" for factor in factors]) if factors else "○ No specific risk factors identified"
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": format_panel_header(ticker),
                "emoji": False
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"```Risk Analysis Engine · Horizon: {horizon}D```"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*{glyph} Risk Score*\n`{risk_score}%`"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Status*\n{verdict.split(' - ')[1] if ' - ' in verdict else verdict}"
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
                "text": f"*◆ Intelligence Brief*\n{factors_text}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*⚡ Tactical Recommendation*\n_{recommendation}_"
            }
        },
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
                        "text": "◆ Deploy Panel Analysis",
                        "emoji": False
                    },
                    "value": f"deep_{ticker}",
                    "action_id": "deep_analysis",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "○ Track Signal",
                        "emoji": False
                    },
                    "value": f"follow_{ticker}",
                    "action_id": "follow_ticker"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "⟳ Refresh",
                        "emoji": False
                    },
                    "value": f"refresh_{ticker}",
                    "action_id": "refresh_analysis"
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"⚡ EVITO Risk Engine · {datetime.utcnow().strftime('%H:%M UTC')}"
                }
            ]
        }
    ]
    # Add color bar (Slack attachment style)
    return {
        "blocks": blocks,
        "attachments": [{
            "color": color,
            "blocks": []
        }]
    }
# =============================================
# EVITO ERROR BLOCKS - QUANTUM NORDIC OS
# =============================================
def format_ticker_error(error_result):
    """
    Format ticker validation error with suggestions
    Quantum Nordic OS style
    Args:
        error_result (dict): Error response from EVITO API
    Returns:
        dict: Slack blocks JSON
    """
    ticker = error_result.get('ticker_entered', '')
    suggestions = error_result.get('suggestions', [])
    error = error_result.get('error', 'Invalid ticker')
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*● System Alert*\n```{error}```\n\nYou entered: `{ticker}`"
            }
        }
    ]
    if suggestions:
        # Add suggestion section
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*◆ Did you mean one of these?*"
            }
        })
        # Add suggestion buttons
        suggestion_buttons = [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": f"○ {suggest}",
                    "emoji": False
                },
                "value": f"analyze_{suggest}",
                "action_id": f"suggest_{suggest}"
            }
            for suggest in suggestions[:5]  # Max 5 suggestions
        ]
        blocks.append({
            "type": "actions",
            "elements": suggestion_buttons
        })
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": "⚡ EVITO Risk Engine · Input Validation"
            }
        ]
    })
    return {
        "blocks": blocks,
        "attachments": [{
            "color": BRAND_COLORS["accent_warning"],  # Red for errors
            "blocks": []
        }]
    }
# =============================================
# EXPORT ALL
# =============================================
__all__ = [
    'format_risk_analysis',
    'format_ticker_error'
]
