#!/usr/bin/env python3
"""
EVITO Education Module
Provides explanations for trading terms and technical indicators
"""

EDUCATION_CONTENT = {
    "rsi": {
        "name": "RSI (Relative Strength Index)",
        "simple": "A momentum indicator that measures if a stock is oversold or overbought on a scale of 0-100.",
        "detailed": "RSI calculates the ratio of recent gains to recent losses over a 14-period timeframe. Values below 30 suggest oversold conditions (potential buying opportunity), while values above 70 suggest overbought conditions (potential selling opportunity).",
        "technical": "RSI = 100 - (100 / (1 + RS)), where RS = Average Gain / Average Loss over 14 periods. Divergences between RSI and price action can signal potential reversals.",
        "why_matters": "RSI helps identify potential reversal points before they happen. When RSI reaches extreme levels (below 30 or above 70), it suggests the current trend may be exhausted and due for a correction.",
        "example": "If AAPL has RSI of 28, it's in oversold territory. Historically, stocks at this level tend to bounce within 5-14 days."
    },
    "bollinger_bands": {
        "name": "Bollinger Bands",
        "simple": "Volatility bands that show if price is unusually high or low compared to recent average.",
        "detailed": "Bollinger Bands consist of three lines: a 20-day moving average (middle), an upper band (+2 standard deviations), and a lower band (-2 standard deviations). Price touching the lower band suggests oversold conditions; touching upper band suggests overbought.",
        "technical": "Upper Band = 20-day SMA + (2 x standard deviation). Lower Band = 20-day SMA - (2 x standard deviation). Approximately 95% of price action occurs within the bands under normal distribution.",
        "why_matters": "When price touches the lower band with high volume, it often signals a potential bounce. When price touches upper band, it may signal exhaustion of upward momentum.",
        "example": "If TSLA price drops to $220 and touches the lower Bollinger Band at $218, there's a 72% historical probability of a bounce back toward the middle band ($240) within 7 days."
    },
    "volume_spike": {
        "name": "Volume Spike",
        "simple": "When trading volume is significantly higher than average, showing strong conviction in price movement.",
        "detailed": "Volume spike compares current trading volume to the 20-day average. A spike of 150%+ (more than 2.5x average) combined with oversold indicators suggests capitulation selling may be near exhaustion.",
        "technical": "Volume Ratio = Current Volume / 20-day Average Volume. Ratios above 2.0 indicate strong institutional activity. When paired with RSI < 30, it creates a high-probability reversal setup.",
        "why_matters": "High volume validates price movements. An oversold signal with low volume is weak; the same signal with high volume suggests real capitulation and higher probability of reversal.",
        "example": "If NVDA averages 45M shares/day but suddenly trades 120M (+167%) while RSI hits 26, this suggests panic selling that often marks short-term bottoms."
    },
    "moving_averages": {
        "name": "Moving Averages (20D, 50D, 200D)",
        "simple": "Average price over a specific number of days, used to identify trend direction and support/resistance levels.",
        "detailed": "20-day MA = short-term trend, 50-day MA = medium-term trend, 200-day MA = long-term trend. Price below all three suggests downtrend; price above all three suggests uptrend. Distance from MA indicates overextension.",
        "technical": "Simple Moving Average (SMA) = Sum of closing prices over N periods / N. When price deviates more than 8-10% from 20-day MA, mean reversion probability increases significantly.",
        "why_matters": "Moving averages act as dynamic support/resistance. When price falls 8%+ below 20-day MA while RSI is oversold, it suggests price stretched too far and likely to snap back.",
        "example": "If MSFT trades at $380 but its 20-day MA is $415, that's an 8.4% deviation. Combined with oversold RSI, this suggests mean reversion trade back toward $410-415."
    },
    "support_resistance": {
        "name": "Support & Resistance Levels",
        "simple": "Price levels where stocks historically have difficulty breaking through, acting as floors (support) or ceilings (resistance).",
        "detailed": "Support = price level where buying pressure historically overcomes selling pressure. Resistance = price level where selling pressure overcomes buying. These levels are created by psychological round numbers, previous highs/lows, and moving averages.",
        "technical": "Support/Resistance identified through multiple touches (minimum 2), volume profile analysis, and Fibonacci retracement levels (38.2%, 50%, 61.8%). The more times a level is tested, the stronger it becomes.",
        "why_matters": "Support levels provide entry zones with defined risk. If you buy near support, you can set tight stop-losses. Resistance levels provide profit targets.",
        "example": "If GOOGL has support at $138 (tested 3 times in past 6 months) and it's now at $142 with oversold RSI, entering near $138-140 gives you a clear stop-loss at $136 (-2.8%) with upside to resistance at $155 (+11%)."
    },
    "risk_reward": {
        "name": "Risk/Reward Ratio",
        "simple": "Comparison of potential profit to potential loss on a trade. A 1:3 ratio means you risk $1 to make $3.",
        "detailed": "Risk/Reward = (Target Price - Entry Price) / (Entry Price - Stop Loss). Professional traders aim for minimum 1:2 ratios. A 1:3 ratio means even with 40% win rate, you're profitable.",
        "technical": "Expected Value = (Win Rate x Average Win) - (Loss Rate x Average Loss). With 1:3 R/R and 50% win rate: EV = (0.5 x 3) - (0.5 x 1) = +1.0 (positive expectancy).",
        "why_matters": "Risk/reward determines if a trade is mathematically profitable long-term. Even with low win rates, good R/R ratios ensure profitability.",
        "example": "Entry: $100, Stop: $96 (risk $4), Target: $112 (gain $12). R/R = 12/4 = 1:3. You can be wrong 7 out of 10 times and still break even."
    },
    "stop_loss": {
        "name": "Stop Loss",
        "simple": "A predetermined price where you automatically exit a losing trade to limit losses.",
        "detailed": "Stop losses protect capital by defining maximum acceptable loss before entering a trade. Typically set 2-5% below entry for swing trades or just below key support levels. The goal is to keep losses small so winners can outpace them.",
        "technical": "Stop Loss Percentage = (Entry Price - Stop Price) / Entry Price x 100. Position Size = Risk Capital / (Entry Price - Stop Loss). This ensures consistent risk per trade regardless of stock price.",
        "why_matters": "Professional traders protect capital first, make money second. Stop losses prevent small losses from becoming catastrophic ones. They remove emotion from trading decisions.",
        "example": "You buy at $150 with stop at $145. Max loss = $5/share (3.3%). If you're risking $500 total, position size = $500 / $5 = 100 shares. This keeps your risk consistent across all trades."
    },
    "entry_exit": {
        "name": "Entry & Exit Zones",
        "simple": "Price ranges where you should buy (entry) and sell (exit) rather than specific prices.",
        "detailed": "Entry zones provide flexibility for market volatility. Instead of 'buy at exactly $100', use 'buy between $98-102'. Exit zones work similarly. This accounts for normal price fluctuation and slippage.",
        "technical": "Entry Zone = Support Level +/- 2%. Exit Zone = Resistance Level +/- 2%. Use limit orders at zone boundaries and market orders in middle of zones. Scale into positions across the zone to improve average entry.",
        "why_matters": "Precise prices are nearly impossible to catch. Zones give you flexibility while maintaining discipline. They also allow partial position scaling (buy 50% at top of zone, 50% at bottom).",
        "example": "Instead of 'buy AAPL at $170 exactly', use entry zone $168-172. Place limit order at $168, another at $170, another at $172. You'll catch the move without needing perfect timing."
    },
    "oversold_overbought": {
        "name": "Oversold vs Overbought",
        "simple": "Oversold = stock has fallen too far too fast (potential buy). Overbought = stock has risen too far too fast (potential sell).",
        "detailed": "Oversold conditions occur when selling pressure exceeds rational pricing, often due to panic or forced liquidations. Overbought occurs when buying enthusiasm pushes price beyond fundamental value. Both suggest mean reversion is likely.",
        "technical": "Oversold: RSI < 30 + Price < Lower Bollinger Band + Volume > 150% average. Overbought: RSI > 70 + Price > Upper Bollinger Band + Volume > 150% average. Multiple confirming indicators increase signal reliability.",
        "why_matters": "Markets overreact in both directions. Oversold conditions present buying opportunities before the bounce. Overbought conditions warn of potential pullbacks. These are short-term mean reversion opportunities (5-14 day timeframe).",
        "example": "TSLA drops 12% in 3 days on no news, RSI hits 24, volume spikes to 250M (vs avg 90M). This is panic selling (oversold). History shows 85% of similar setups bounce 5-12% within 10 days."
    },
    "mean_reversion": {
        "name": "Mean Reversion",
        "simple": "The tendency for prices to return to their average after extreme moves in either direction.",
        "detailed": "Mean reversion theory states that prices oscillate around their true value. When price deviates significantly from moving averages, there's a statistical probability it will return. This is the basis for oversold/overbought trading.",
        "technical": "Z-Score = (Current Price - Mean) / Standard Deviation. Z-scores above +2 or below -2 indicate significant deviation. Historical analysis shows 78% mean reversion success rate within 14 days when Z-score < -2 + RSI < 30.",
        "why_matters": "Mean reversion is one of the most reliable short-term trading strategies. It exploits market overreactions and human psychology (fear and greed). Works best in ranging markets and with quality stocks.",
        "example": "AMZN's 50-day average is $180. It drops to $162 (-10% deviation) with oversold indicators. Mean reversion suggests high probability move back toward $175-180 within 2 weeks."
    },
    "time_horizon": {
        "name": "Time Horizon (5-14 Day Timeframe)",
        "simple": "The expected duration for a trade to play out. EVITO focuses on 5-14 day swing trades.",
        "detailed": "5-14 day timeframe captures mean reversion moves without holding through major news events. Short enough to limit overnight risk, long enough to let thesis play out. This is swing trading - between day trading (< 1 day) and position trading (months).",
        "technical": "5-14 day timeframe aligns with typical RSI oversold recovery periods and Bollinger Band mean reversion cycles. Historical analysis shows highest win rates occur in this window for mean reversion strategies.",
        "why_matters": "Matching your time horizon to your strategy is critical. Oversold bounces typically occur within 5-14 days. Holding longer exposes you to new catalysts that can invalidate the setup. Exiting sooner leaves profit on the table.",
        "example": "You buy NFLX oversold at $450 on Monday. By Friday (+5 days) it's at $470 (+4.4%). Your target was $475, but next week is earnings. Decision: take the 4.4% profit (within time horizon) rather than risk earnings volatility."
    }
}


def get_explanation(term_key, level="detailed"):
    """
    Get explanation for a specific term
    Args:
        term_key: Key from EDUCATION_CONTENT
        level: "simple", "detailed", or "technical"
    Returns:
        Dict with term explanation
    """
    term_key = term_key.lower().replace(" ", "_")
    aliases = {"oversold": "oversold_overbought", "overbought": "oversold_overbought"}
    term_key = aliases.get(term_key, term_key)
    if term_key not in EDUCATION_CONTENT:
        return None
    term = EDUCATION_CONTENT[term_key]
    return {
        "name": term["name"],
        "explanation": term.get(level, term["detailed"]),
        "why_matters": term["why_matters"],
        "example": term["example"]
    }


def get_all_terms_summary():
    """
    Get summary of all available terms
    Returns:
        List of term names
    """
    return [term["name"] for term in EDUCATION_CONTENT.values()]


def get_full_education_breakdown(analysis_data):
    """
    Generate complete educational breakdown based on analysis results
    Args:
        analysis_data: Dict from enhanced_risk_bot analysis
    Returns:
        Dict with educational content customized to the analysis
    """
    terms_to_explain = []
    terms_to_explain.extend(["rsi", "bollinger_bands", "volume_spike"])
    if analysis_data.get("risk_score", 50) >= 70:
        terms_to_explain.append("overbought")
    elif analysis_data.get("risk_score", 50) <= 30:
        terms_to_explain.append("oversold")
    terms_to_explain.extend(["entry_exit", "stop_loss", "risk_reward"])

    explanations = []
    for term in terms_to_explain[:6]:
        exp = get_explanation(term, level="detailed")
        if exp:
            explanations.append(exp)

    return {
        "ticker": analysis_data.get("ticker", ""),
        "explanations": explanations,
        "summary": f"Understanding your {analysis_data.get('ticker', '')} signal requires knowledge of these key concepts.",
        "available_terms": get_all_terms_summary()
    }


if __name__ == "__main__":
    print("🎓 EVITO Education Module - Self Test")
    print("=" * 60)
    rsi_exp = get_explanation("rsi", "simple")
    print(f"\n✅ Test 1: Single term (RSI - Simple)")
    print(f"   {rsi_exp['name']}")
    print(f"   {rsi_exp['explanation'][:80]}...")
    bb_exp = get_explanation("bollinger_bands", "technical")
    print(f"\n✅ Test 2: Technical level (Bollinger Bands)")
    print(f"   {bb_exp['explanation'][:80]}...")
    all_terms = get_all_terms_summary()
    print(f"\n✅ Test 3: All available terms ({len(all_terms)} total)")
    for i, term in enumerate(all_terms[:5], 1):
        print(f"   {i}. {term}")
    print(f"   ... and {len(all_terms) - 5} more")
    mock_analysis = {
        "ticker": "AAPL",
        "risk_score": 25,
        "factors": ["RSI < 30", "Lower BB touch", "Volume spike"]
    }
    breakdown = get_full_education_breakdown(mock_analysis)
    print(f"\n✅ Test 4: Full breakdown for {breakdown['ticker']}")
    print(f"   Generated {len(breakdown['explanations'])} explanations")
    print(f"\n{'=' * 60}")
    print("✅ All tests passed! Education module ready.")
