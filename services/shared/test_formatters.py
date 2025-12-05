#!/usr/bin/env python3
"""Test the Quantum Nordic OS Slack formatters"""
import json
from slack_blocks import format_risk_analysis, format_ticker_error
print("╔═══════════════════════════════════════════════════════════╗")
print("║  QUANTUM NORDIC OS - SLACK BLOCK KIT TEST                ║")
print("╚═══════════════════════════════════════════════════════════╝\n")
# Test 1: High Risk Analysis (TSLA)
print("=" * 60)
print("TEST 1: HIGH RISK ANALYSIS (TSLA - 75% Risk)")
print("=" * 60)
evito_result_high = {
    "success": True,
    "ticker": "TSLA",
    "risk_score": 75,
    "factors": [
        "High volatility stock",
        "Strong social media presence",
        "Elevated options activity"
    ],
    "verdict": "75% - High sell-the-news risk",
    "recommendation": "Consider waiting for pullback",
    "horizon": 30
}
formatted_high = format_risk_analysis(evito_result_high)
print(json.dumps(formatted_high, indent=2))
# Test 2: Medium Risk Analysis (NVDA)
print("\n" + "=" * 60)
print("TEST 2: MEDIUM RISK ANALYSIS (NVDA - 60% Risk)")
print("=" * 60)
evito_result_medium = {
    "success": True,
    "ticker": "NVDA",
    "risk_score": 60,
    "factors": [
        "Tech sector exposure",
        "Earnings sensitive",
        "High institutional ownership"
    ],
    "verdict": "60% - Moderate risk",
    "recommendation": "Watch for entry points",
    "horizon": 30
}
formatted_medium = format_risk_analysis(evito_result_medium)
print(json.dumps(formatted_medium, indent=2))
# Test 3: Low Risk Analysis (AAPL)
print("\n" + "=" * 60)
print("TEST 3: LOW RISK ANALYSIS (AAPL - 35% Risk)")
print("=" * 60)
evito_result_low = {
    "success": True,
    "ticker": "AAPL",
    "risk_score": 35,
    "factors": [
        "Blue chip stability",
        "Lower volatility expected",
        "Consistent revenue streams"
    ],
    "verdict": "35% - Low risk",
    "recommendation": "Relatively stable outlook",
    "horizon": 30
}
formatted_low = format_risk_analysis(evito_result_low)
print(json.dumps(formatted_low, indent=2))
# Test 4: Error with suggestions
print("\n" + "=" * 60)
print("TEST 4: ERROR WITH SUGGESTIONS (TSLS typo)")
print("=" * 60)
error_result = {
    "success": False,
    "ticker_entered": "TSLS",
    "suggestions": ["TSLA", "SQ", "SNOW"],
    "error": "Ticker 'TSLS' not recognized. Did you mean: TSLA?"
}
formatted_error = format_ticker_error(error_result)
print(json.dumps(formatted_error, indent=2))
print("\n" + "=" * 60)
print("✅ ALL TESTS COMPLETE")
print("=" * 60)
print("\n📋 Color Codes Used:")
print(f"  High Risk:   #FF3850 (Accent Warning)")
print(f"  Medium Risk: #F7F9FA (Text Primary)")
print(f"  Low Risk:    #00F0FF (Neon Cyan)")
print(f"  Background:  #060A12 (Deep Obsidian)")
print("\n⚡ Quantum Nordic OS Style Applied")
