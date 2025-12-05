"""
EVITO Risk Analysis API
Provides risk analysis for stock tickers
"""
from flask import Flask, request, jsonify
from datetime import datetime
import os
app = Flask(__name__)
# ============================================================
# RISK ANALYSIS ENDPOINT
# ============================================================
@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    """Analyze risk for a given ticker - accepts both GET and POST"""
    # Handle both GET and POST methods
    if request.method == "POST":
        data = request.json or {}
        ticker = data.get("ticker", "")
        days = data.get("days", 90)
    else:  # GET
        ticker = request.args.get("ticker", "")
        days = request.args.get("days", 90, type=int)
    if not ticker:
        return jsonify({"error": "Ticker symbol required"}), 400
    ticker = ticker.upper()

    # Mock risk analysis (replace with your actual logic later)
    # Make score depend on ticker AND days so horizon changes reflect in output
    try:
        days_int = int(days)
    except Exception:
        days_int = 90

    risk_score = abs(hash(f"{ticker}-{days_int}")) % 100
    if risk_score < 30:
        risk_level = "Low"
    elif risk_score < 60:
        risk_level = "Medium"
    elif risk_score < 80:
        risk_level = "High"
    else:
        risk_level = "Critical"
    result = {
        "ticker": ticker,
        "days": days_int,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "timestamp": datetime.now().isoformat(),
        "analysis": {
            "volatility": round(risk_score * 0.8, 2),
            "trend": "bullish" if risk_score < 50 else "bearish",
            "confidence": round((100 - risk_score) / 100, 2)
        },
        "factors": [
            {"name": "Market Volatility", "score": risk_score},
            {"name": "Trend Strength", "score": 100 - risk_score},
            {"name": "Volume", "score": (risk_score + 50) % 100},
            {"name": "Horizon Sensitivity", "score": (days_int % 365) // 30},
        ]
    }
    return jsonify(result)
# ============================================================
# UTILITY ENDPOINTS
# ============================================================
@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "EVITO Risk Analysis API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })
@app.route("/info", methods=["GET"])
def info():
    """API information"""
    return jsonify({
        "service": "EVITO Risk Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "GET or POST - Analyze ticker risk (params: ticker, days)",
            "/health": "GET - Health check",
            "/info": "GET - API information",
            "/tickers": "GET - List supported tickers"
        },
        "examples": {
            "analyze_get": "GET /analyze?ticker=TSLA&days=90",
            "analyze_post": "POST /analyze with JSON {\"ticker\": \"TSLA\", \"days\": 90}"
        }
    })
@app.route("/tickers", methods=["GET"])
def tickers():
    """List some example tickers"""
    return jsonify({
        "tickers": [
            {"symbol": "TSLA", "name": "Tesla"},
            {"symbol": "AAPL", "name": "Apple"},
            {"symbol": "MSFT", "name": "Microsoft"},
            {"symbol": "GOOGL", "name": "Google"},
            {"symbol": "NVDA", "name": "NVIDIA"},
            {"symbol": "META", "name": "Meta"},
            {"symbol": "AMZN", "name": "Amazon"}
        ]
    })
@app.route("/explain", methods=["POST"])
def explain():
    """Explain risk analysis"""
    data = request.json or {}
    ticker = data.get("ticker", "")
    return jsonify({
        "ticker": ticker,
        "explanation": f"Risk analysis for {ticker} considers multiple factors including "
                      "historical volatility, trend strength, and trading volume. "
                      "The risk score is calculated on a scale of 0-100."
    })
@app.route("/feedback", methods=["POST"])
def feedback():
    """Accept user feedback"""
    data = request.json or {}
    feedback_entry = {
        "user": data.get("user", "anonymous"),
        "feedback": data.get("feedback", ""),
        "context": data.get("context", {}),
        "timestamp": datetime.now().isoformat()
    }
    # Log feedback (in production, save to database)
    print("\n" + "="*60)
    print("📣 NEW FEEDBACK RECEIVED")
    print("="*60)
    print(f"User: {feedback_entry['user']}")
    print(f"Time: {feedback_entry['timestamp']}")
    print(f"Feedback: {feedback_entry['feedback']}")
    print(f"Context: {feedback_entry['context']}")
    print("="*60 + "\n")
    return jsonify({
        "status": "success",
        "message": "Thank you for your feedback!"
    })
# ============================================================
# START SERVER
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("    ╔═══════════════════════════════════════╗")
    print("    ║     EVITO RISK ANALYSIS API           ║")
    print("    ║                                       ║")
    print("    ║  🚀 Running on port 8081             ║")
    print("    ║  📊 Enhanced risk analysis ready       ║")
    print("    ║  💡 GET /info for endpoints            ║")
    print("    ╚═══════════════════════════════════════╝")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=8081, debug=False)
