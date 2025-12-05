"""
EVITO/Empire Unified Color Guide - Quantum Nordic OS
Brand Identity: Premium tech-human fusion with neon accents
"""
# =============================================
# QUANTUM NORDIC OS - CORE BRAND COLORS
# =============================================
BRAND_COLORS = {
    # Core palette
    "background": "#060A12",      # Deep obsidian blue
    "highlight": "#00F0FF",       # Cold neon cyan
    "text_primary": "#F7F9FA",    # Primary text
    "muted_ui": "#1A1F29",        # Muted UI elements
    "accent_warning": "#FF3850",  # Rare use - critical warnings
    # Extended palette
    "glass_panel": "rgba(26, 31, 41, 0.6)",  # Glassmorphism
    "neon_glow": "#00F0FF",       # Edge glow
    "particle": "rgba(0, 240, 255, 0.3)"  # Background particles
}
# =============================================
# RISK COLORS (EVITO) - Adapted to brand
# =============================================
RISK_COLORS = {
    "high": "#FF3850",      # Brand accent warning - high risk
    "medium": "#00F0FF",    # Cyan - medium risk (watch closely)
    "low": "#00F0FF",       # Cyan - low risk (opportunity)
    "neutral": "#1A1F29"    # Muted for neutral states
}
# =============================================
# MOAT COLORS (EMPIRE) - Adapted to brand
# =============================================
MOAT_COLORS = {
    "strong": "#00F0FF",    # Cyan - strong moat (aligned with brand)
    "moderate": "#F7F9FA",  # White - moderate confidence
    "weak": "#FF3850"       # Warning red - weak moat
}
# =============================================
# SLACK COLORS (Maintains Slack compatibility)
# =============================================
SLACK_COLORS = {
    # Standard Slack colors (but we'll use custom formatting)
    "good": "#00F0FF",      # Map to brand cyan
    "warning": "#F7F9FA",   # Map to white
    "danger": "#FF3850"     # Map to accent warning
}
# =============================================
# UI ELEMENT COLORS
# =============================================
UI_COLORS = {
    "primary_action": "#00F0FF",    # Cyan - primary CTAs
    "secondary_action": "#1A1F29",  # Muted - secondary actions
    "success": "#00F0FF",           # Cyan - success states
    "warning": "#F7F9FA",           # White - caution
    "danger": "#FF3850",            # Red - errors/critical
    "info": "#00F0FF",              # Cyan - informational
    "disabled": "#1A1F29"           # Muted - disabled states
}
# =============================================
# PANEL IDENTITIES (For the 3-model system)
# =============================================
PANEL_COLORS = {
    "buffett": {
        "primary": "#00F0FF",
        "glyph": "●",
        "label": "Value Model"
    },
    "dalio": {
        "primary": "#F7F9FA",
        "glyph": "◆",
        "label": "Macro Model"
    },
    "tangen": {
        "primary": "#00F0FF",
        "glyph": "■",
        "label": "Pragmatic Model"
    }
}
# =============================================
# TYPOGRAPHY SPECS (for documentation)
# =============================================
TYPOGRAPHY = {
    "title": {
        "family": "SF Pro Display, Söhne",
        "weight": "600-700"
    },
    "body": {
        "family": "Inter",
        "weight": "400-500"
    },
    "code": {
        "family": "JetBrains Mono",
        "weight": "300"
    }
}
# =============================================
# HELPER FUNCTIONS
# =============================================
def get_risk_color(risk_score):
    """
    Get color based on risk score (0-100)
    Quantum Nordic OS style
    Args:
        risk_score (int): Risk score from 0-100
    Returns:
        str: Hex color code
    """
    if risk_score >= 70:
        return RISK_COLORS["high"]      # Red warning
    elif risk_score >= 50:
        return RISK_COLORS["medium"]    # Cyan caution
    else:
        return RISK_COLORS["low"]       # Cyan opportunity
def get_moat_color(confidence_score):
    """
    Get color based on moat confidence (1-10)
    Args:
        confidence_score (float): Confidence from 1-10
    Returns:
        str: Hex color code
    """
    if confidence_score >= 8:
        return MOAT_COLORS["strong"]     # Cyan
    elif confidence_score >= 5:
        return MOAT_COLORS["moderate"]   # White
    else:
        return MOAT_COLORS["weak"]       # Red
def get_slack_color_for_risk(risk_score):
    """
    Get Slack-compatible color for risk visualization
    Args:
        risk_score (int): Risk score from 0-100
    Returns:
        str: Hex color for Slack attachment border
    """
    if risk_score >= 70:
        return BRAND_COLORS["accent_warning"]  # #FF3850
    elif risk_score >= 50:
        return BRAND_COLORS["text_primary"]    # #F7F9FA
    else:
        return BRAND_COLORS["highlight"]       # #00F0FF
# =============================================
# EMOJI/GLYPH MAPPINGS (Brand-aligned)
# =============================================
RISK_GLYPHS = {
    "high": "●",        # Solid circle - critical
    "medium": "◆",      # Diamond - watch
    "low": "○"          # Open circle - opportunity
}
MOAT_GLYPHS = {
    "strong": "■",      # Solid square - fortress
    "moderate": "◆",    # Diamond - conditional
    "weak": "□"         # Empty square - vulnerable
}
def get_risk_glyph(risk_score):
    """Get brand glyph based on risk score"""
    if risk_score >= 70:
        return RISK_GLYPHS["high"]
    elif risk_score >= 50:
        return RISK_GLYPHS["medium"]
    else:
        return RISK_GLYPHS["low"]
def get_moat_glyph(confidence_score):
    """Get brand glyph based on moat confidence"""
    if confidence_score >= 8:
        return MOAT_GLYPHS["strong"]
    elif confidence_score >= 5:
        return MOAT_GLYPHS["moderate"]
    else:
        return MOAT_GLYPHS["weak"]
# =============================================
# SLACK BLOCK STYLING HELPERS
# =============================================
def get_panel_identity(model_name):
    """
    Get panel identity for the 3-model system
    Args:
        model_name (str): 'buffett', 'dalio', or 'tangen'
    Returns:
        dict: Panel visual identity
    """
    return PANEL_COLORS.get(model_name.lower(), {
        "primary": BRAND_COLORS["highlight"],
        "glyph": "●",
        "label": "Unknown Model"
    })
def format_panel_header(ticker):
    """
    Create Quantum Nordic OS style header
    Returns:
        str: Formatted header text
    """
    return f"⚡ PANEL ENGINE ONLINE · {ticker}"
def format_consensus_message():
    """Panel consensus reached message"""
    return "◆ Consensus Reached: Deploy Intelligence Sequence"
# =============================================
# EXPORT ALL
# =============================================
__all__ = [
    'BRAND_COLORS',
    'RISK_COLORS',
    'MOAT_COLORS',
    'SLACK_COLORS',
    'UI_COLORS',
    'PANEL_COLORS',
    'TYPOGRAPHY',
    'get_risk_color',
    'get_moat_color',
    'get_slack_color_for_risk',
    'get_risk_glyph',
    'get_moat_glyph',
    'get_panel_identity',
    'format_panel_header',
    'format_consensus_message',
    'RISK_GLYPHS',
    'MOAT_GLYPHS'
]
