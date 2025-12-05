# risk_bot.py - Enhanced with validation and fuzzy matching
import sys
import json
from datetime import datetime
from difflib import get_close_matches
import re
from zoneinfo import ZoneInfo
# Known tickers (expand this list or fetch from API)
KNOWN_TICKERS = [
    "AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "AMD",
    "GME", "AMC", "PLTR", "COIN", "ROKU", "SNOW", "NET", "CRWD",
    "SHOP", "SQ", "PYPL", "V", "MA", "JPM", "BAC", "WFC",
    "SPY", "QQQ", "IWM", "DIA", "VTI", "VOO"
]
def validate_ticker(ticker):
    """
    Validate ticker format and check if it's known
    Returns: (is_valid, suggestions, error_message)
    """
    ticker = ticker.upper().strip()
    # Check format (1-5 letters, alphanumeric)
    if not re.match(r'^[A-Z]{1,5}$', ticker):
        return False, [], "Invalid ticker format. Use 1-5 letters (e.g., TSLA, AAPL)"
    # Check if known
    if ticker in KNOWN_TICKERS:
        return True, [], None
    # Find similar tickers (fuzzy match)
    suggestions = get_close_matches(ticker, KNOWN_TICKERS, n=3, cutoff=0.6)
    if suggestions:
        return False, suggestions, f"Ticker '{ticker}' not recognized. Did you mean: {', '.join(suggestions)}?"
    else:
        # Allow unknown tickers with warning
        return True, [], f"Warning: '{ticker}' is not in known ticker list, proceeding anyway..."
def validate_horizon(horizon):
    """
    Validate horizon parameter
    Returns: (is_valid, error_message)
    """
    try:
        horizon = int(horizon)
        if horizon < 1:
            return False, "Horizon must be at least 1 day"
        if horizon > 365:
            return False, "Horizon cannot exceed 365 days"
        return True, None
    except ValueError:
        return False, "Horizon must be a number"
def analyze_ticker(ticker, horizon=30):
    """
    Risk analysis logic
    """
    risk_factors = []
    risk_score = 50
    # High volatility stocks
    if ticker in ["TSLA", "GME", "AMC", "PLTR"]:
        risk_score = 75
        risk_factors.append("High volatility stock")
        risk_factors.append("Strong social media presence")
    # Tech stocks
    elif ticker in ["NVDA", "AMD", "MSFT", "GOOGL", "META"]:
        risk_score = 60
        risk_factors.append("Tech sector exposure")
        risk_factors.append("Earnings sensitive")
    # Blue chips (lower risk)
    elif ticker in ["AAPL", "JPM", "V", "MA"]:
        risk_score = 35
        risk_factors.append("Blue chip stability")
        risk_factors.append("Lower volatility expected")
    # Crypto-related
    elif ticker in ["COIN", "MSTR"]:
        risk_score = 80
        risk_factors.append("Crypto market correlation")
        risk_factors.append("High volatility")
    # Adjust for timeframe
    if horizon < 7:
        risk_score += 15
        risk_factors.append("Short timeframe amplifies risk")
    elif horizon > 90:
        risk_score -= 10
        risk_factors.append("Longer timeframe reduces short-term noise")
    # Cap at 0-100
    risk_score = max(0, min(100, risk_score))
    # Determine verdict
    if risk_score > 70:
        verdict = f"{risk_score}% - High sell-the-news risk"
        recommendation = "Consider waiting for pullback"
    elif risk_score > 50:
        verdict = f"{risk_score}% - Moderate risk"
        recommendation = "Watch for entry points"
    else:
        verdict = f"{risk_score}% - Low risk"
        recommendation = "Relatively stable outlook"
    now_oslo = datetime.now(ZoneInfo("Europe/Oslo"))
    return {
        "success": True,
        "ticker": ticker,
        "horizon": horizon,
        "risk_score": risk_score,
        "factors": risk_factors,
        "verdict": verdict,
        "recommendation": recommendation,
        "timestamp": now_oslo.isoformat(),
    }
def main():
    """
    Main execution with validation
    """
    # Check arguments
    if len(sys.argv) < 2:
        error_response = {
            "success": False,
            "error": "Missing ticker argument",
            "usage": "python3 risk_bot.py TICKER [HORIZON]",
            "example": "python3 risk_bot.py TSLA 30"
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)
    ticker = sys.argv[1].upper().strip()
    horizon_arg = sys.argv[2] if len(sys.argv) > 2 else "30"
    # Validate ticker
    ticker_valid, suggestions, ticker_error = validate_ticker(ticker)
    if not ticker_valid and suggestions:
        # Ticker not found but we have suggestions
        error_response = {
            "success": False,
            "error": ticker_error,
            "ticker_entered": ticker,
            "suggestions": suggestions,
            "action": "Please retry with correct ticker or choose from suggestions"
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)
    # Show warning if unknown ticker but proceed
    warning = None
    if ticker_error and not suggestions:
        warning = ticker_error
    # Validate horizon
    horizon_valid, horizon_error = validate_horizon(horizon_arg)
    if not horizon_valid:
        error_response = {
            "success": False,
            "error": horizon_error,
            "horizon_entered": horizon_arg,
            "valid_range": "1-365 days"
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)
    horizon = int(horizon_arg)
    # Run analysis
    result = analyze_ticker(ticker, horizon)
    # Add warning if any
    if warning:
        result["warning"] = warning
    # Print result
    print(json.dumps(result, indent=2))
if __name__ == "__main__":
    main()
