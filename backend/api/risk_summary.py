import requests
import os
from typing import Dict, Optional


def generate_ai_summary(
    metrics_data: Dict, style: str = "detailed", perplexity_token: Optional[str] = None
) -> str:
    """
    Generate AI summary from risk metrics using Perplexity API.

    Args:
        metrics_data: Your metrics dict with 'portfolio_summary' and 'details'
        style: 'concise', 'detailed' (default), or 'technical'
        perplexity_token: Perplexity API token (or set PERPLEXITY_API_KEY env var)

    Returns:
        Summary string with risk analysis
    """

    # Get Perplexity token
    token = perplexity_token or os.getenv("PERPLEXITY_API_KEY")

    # If no token, return rule-based summary (fallback)
    if not token:
        return _fallback_summary(metrics_data)

    try:
        # Create prompt
        prompt = _create_prompt(metrics_data, style)

        # Call Perplexity API
        summary = _call_perplexity(prompt, token)

        return summary

    except Exception as e:
        print(f"Perplexity API failed: {e}. Using fallback.")
        return _fallback_summary(metrics_data)


def _create_prompt(metrics_data: Dict, style: str) -> str:
    """Create balanced, accessible prompts for both retail and professional investors."""

    details = metrics_data.get("details", [])
    portfolio = metrics_data.get("portfolio_summary", {})

    # Single ticker
    if len(details) == 1:
        d = details[0]
        ticker = d["ticker"]
        vol = d["historical_volatility"]
        var = d["VaR_95"]
        cvar = d["CVaR_95"]
        garch = d.get("forecasted_volatility_garch")
        xgb = d.get("forecasted_volatility_xgboost")
        lstm = d.get("forecasted_volatility_lstm")

        if style == "concise":
            return f"""Analyze this stock's risk in 3 clear sentences for both retail and professional investors.

Stock: {ticker}
• Volatility: {vol:.4f} ({vol*100:.2f}%)
• VaR (95%): {var:.4f} ({var*100:.2f}%)
• CVaR (95%): {cvar:.4f} ({cvar*100:.2f}%)

Provide:
1. Risk level classification (LOW/MODERATE/HIGH/EXTREME)
2. What this volatility means practically (expected price swings)
3. Who should invest (conservative/moderate/aggressive)

Be clear and use the exact numbers."""

        elif style == "detailed":
            forecast_info = ""
            if garch and xgb and lstm:
                avg_forecast = (garch + xgb + lstm) / 3
                forecast_info = f"""
• GARCH Forecast: {garch:.4f} ({garch*100:.2f}%)
• XGBoost Forecast: {xgb:.4f} ({xgb*100:.2f}%)
• LSTM Forecast: {lstm:.4f} ({lstm*100:.2f}%)
• Average Forecast: {avg_forecast:.4f} ({avg_forecast*100:.2f}%)
"""

            return f"""Provide a balanced risk analysis for {ticker} suitable for both retail and institutional investors.

CURRENT METRICS:
• Historical Volatility: {vol:.4f} ({vol*100:.2f}%)
• Value at Risk (VaR₉₅): {var:.4f} ({var*100:.2f}%)
• Conditional VaR (CVaR₉₅): {cvar:.4f} ({cvar*100:.2f}%)

VOLATILITY FORECASTS (if available):
{forecast_info}

Write 3-4 concise paragraphs covering:

1. RISK CLASSIFICATION: State the risk level (LOW/LOW-MODERATE/MODERATE/MODERATE-HIGH/HIGH/EXTREME) and explain what {vol*100:.2f}% volatility means in plain English (typical daily price swings, comparison to market average).

2. LOSS POTENTIAL: Explain VaR and CVaR in practical terms - on a $10,000 investment, what losses are possible? Use the actual {var*100:.2f}% and {cvar*100:.2f}% numbers.

3. FUTURE OUTLOOK: If forecasts are available, briefly compare them to current volatility. Is risk increasing, decreasing, or stable? What does this mean for investors?

4. RECOMMENDATION: Who should invest (conservative/moderate/aggressive)? What position size is appropriate? Any specific risk management tips (stop losses, position limits).

Be clear, precise, and actionable. Use all the numbers provided. Write in accessible language that both beginners and professionals can understand."""

        else:  # technical
            return f"""Provide technical risk analysis for {ticker}.

Metrics:
σ = {vol:.4f}, VaR₉₅ = {var:.4f}, CVaR₉₅ = {cvar:.4f}

Analyze: volatility regime, tail risk (CVaR/VaR ratio), distribution properties, and risk-adjusted implications. Use quantitative terminology but keep it concise (2-3 paragraphs)."""

    # Portfolio
    else:
        tickers = portfolio.get("tickers", [])
        ticker_str = ", ".join(tickers[:5])
        if len(tickers) > 5:
            ticker_str += f"... (+{len(tickers)-5} more)"

        avg_vol = portfolio.get("average_volatility", 0)
        avg_var = portfolio.get("average_VaR_95", 0)
        avg_cvar = portfolio.get("average_CVaR_95", 0)
        n = len(tickers)

        # Calculate statistics
        valid_details = [d for d in details if "error" not in d]

        if valid_details:
            vol_list = [d["historical_volatility"] for d in valid_details]
            vol_min = min(vol_list)
            vol_max = max(vol_list)
            vol_std = (sum((v - avg_vol) ** 2 for v in vol_list) / len(vol_list)) ** 0.5

            # Find top risky stocks
            sorted_stocks = sorted(
                valid_details, key=lambda x: x["historical_volatility"], reverse=True
            )
            top_3_risky = [
                (d["ticker"], d["historical_volatility"]) for d in sorted_stocks[:3]
            ]

        if style == "concise":
            return f"""Summarize this portfolio's risk in 3-4 sentences.

Portfolio: {n} stocks - {ticker_str}
• Average Volatility: {avg_vol:.4f} ({avg_vol*100:.2f}%)
• Average VaR (95%): {avg_var:.4f} ({avg_var*100:.2f}%)
• Average CVaR (95%): {avg_cvar:.4f} ({avg_cvar*100:.2f}%)
• Volatility Range: {vol_min:.4f} to {vol_max:.4f}

Provide:
1. Overall risk level with the specific volatility number
2. Diversification quality assessment
3. Any concentration concerns
4. Clear recommendation for investor type"""

        elif style == "detailed":
            risky_stocks_str = ", ".join(
                [f"{t} ({v*100:.1f}%)" for t, v in top_3_risky]
            )

            return f"""Provide a balanced portfolio risk analysis for both retail and institutional investors.

PORTFOLIO: {n} Securities
Holdings: {ticker_str}

AGGREGATE METRICS:
• Average Volatility: {avg_vol:.4f} ({avg_vol*100:.2f}%)
• Average VaR (95%): {avg_var:.4f} ({avg_var*100:.2f}%)
• Average CVaR (95%): {avg_cvar:.4f} ({avg_cvar*100:.2f}%)
• Volatility Range: {vol_min:.4f} ({vol_min*100:.2f}%) to {vol_max:.4f} ({vol_max*100:.2f}%)
• Std Deviation: {vol_std:.4f}

TOP 3 RISKIEST: {risky_stocks_str}

Write 3-4 concise paragraphs covering:

1. OVERALL RISK: Classify portfolio risk level using the {avg_vol*100:.2f}% average volatility. Compare to market benchmarks (S&P 500 ~15-18%). What type of investor is this for?

2. DIVERSIFICATION: Evaluate the volatility range ({vol_min*100:.2f}% to {vol_max*100:.2f}%). Is this well-diversified or concentrated? Does the {(vol_max-vol_min)*100:.2f} percentage point spread indicate good risk distribution?

3. KEY RISKS: Discuss the riskiest holdings. What % of portfolio do they represent? Are there concentration concerns? On a $100,000 portfolio, what are realistic loss scenarios using VaR and CVaR?

4. RECOMMENDATIONS: Should any positions be reduced? How should investors monitor this? Rebalancing suggestions? Suitable allocation % of total net worth?

Be clear, precise, and actionable. Use all numbers provided. Accessible for both beginners and professionals."""

        else:  # technical
            return f"""Technical portfolio analysis.

N={n}, σ̄={avg_vol:.4f}, VaR₉₅={avg_var:.4f}, CVaR₉₅={avg_cvar:.4f}
Range=[{vol_min:.4f}, {vol_max:.4f}], σ(σ)={vol_std:.4f}

Analyze: portfolio risk regime, dispersion characteristics, diversification quality, tail risk, and optimization implications. Keep concise (2-3 paragraphs)."""


def _call_perplexity(prompt: str, token: str, max_retries: int = 3) -> str:
    """Call Perplexity API with proper error handling."""

    url = "https://api.perplexity.ai/chat/completions"

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": """You are a professional financial analyst who explains risk clearly to both retail investors and institutions.

Your style:
- Clear, precise language - no jargon unless necessary
- Always use specific numbers from the data
- Practical explanations (e.g., "on a $10,000 investment...")
- Actionable recommendations
- Balanced tone - honest about risks without being alarmist

Keep analysis concise but comprehensive - quality over quantity.
And keep it like a normal paragraph, no bullet points, no code style output.""",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "top_p": 0.9,
        "max_tokens": 800,  # Reasonable length
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"].strip()
                    return content
                else:
                    raise Exception("Unexpected API response format")

            elif response.status_code == 401:
                raise Exception("Invalid Perplexity API key")

            elif response.status_code == 429:
                print(f"Rate limit hit, retry {attempt + 1}/{max_retries}")
                import time

                time.sleep(5 * (attempt + 1))
                continue

            else:
                print(f"API error: {response.status_code}")
                if attempt < max_retries - 1:
                    import time

                    time.sleep(3)
                    continue
                else:
                    raise Exception(f"API failed with status {response.status_code}")

        except requests.exceptions.Timeout:
            print(f"Timeout, retry {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                import time

                time.sleep(3)
                continue
            else:
                raise Exception("Request timed out")

        except Exception as e:
            if "Invalid" in str(e) or "key" in str(e).lower():
                raise
            if attempt < max_retries - 1:
                import time

                time.sleep(3)
                continue
            else:
                raise

    raise Exception("Perplexity API failed after retries")


def _fallback_summary(metrics_data: Dict) -> str:
    """Clean, concise rule-based summary."""

    details = metrics_data.get("details", [])
    portfolio = metrics_data.get("portfolio_summary", {})

    # Single ticker
    if len(details) == 1:
        d = details[0]
        ticker = d["ticker"]
        vol = d["historical_volatility"]
        var = abs(d["VaR_95"])
        cvar = abs(d["CVaR_95"])

        # Risk classification
        if vol > 0.5:
            risk = "EXTREME RISK"
            investor = "Only for aggressive traders with very high risk tolerance"
            allocation = "Max 2-3% of portfolio"
        elif vol > 0.4:
            risk = "HIGH RISK"
            investor = "Aggressive investors only"
            allocation = "Limit to 5-8% of portfolio"
        elif vol > 0.3:
            risk = "MODERATE-HIGH RISK"
            investor = "Moderate to aggressive investors"
            allocation = "10-15% allocation recommended"
        elif vol > 0.25:
            risk = "MODERATE RISK"
            investor = "Balanced portfolios"
            allocation = "15-20% allocation"
        elif vol > 0.15:
            risk = "LOW-MODERATE RISK"
            investor = "Most investors"
            allocation = "Can be a core holding (20-30%)"
        else:
            risk = "LOW RISK"
            investor = "Conservative investors"
            allocation = "Suitable as core holding (30-40%)"

        # Calculate practical loss example
        var_on_10k = var * 10000
        cvar_on_10k = cvar * 10000

        summary = f"""📊 {ticker} - Risk Analysis

🎯 RISK LEVEL: {risk}
Historical Volatility: {vol:.2%} (annualized)

📉 LOSS POTENTIAL:
• Value at Risk (95% confidence): {var:.2%}
  → On $10,000 investment: ${abs(var_on_10k):,.0f} maximum loss expected
• Conditional VaR (worst 5% scenarios): {cvar:.2%}
  → Average loss in bad scenarios: ${abs(cvar_on_10k):,.0f}

🎓 WHAT THIS MEANS:
{ticker}'s {vol:.2%} volatility means typical daily swings of ±{(vol/16):.1%}. At 95% confidence, daily losses shouldn't exceed {var:.2%}. However, in the worst 5% of days, average loss is {cvar:.2%}.

💡 RECOMMENDATION:
• Investor Type: {investor}
• Position Size: {allocation}
• Risk Management: Use stop losses at {var*1.5:.1%}, monitor regularly
"""

        # Add forecast info if available
        garch = d.get("forecasted_volatility_garch")
        xgb = d.get("forecasted_volatility_xgboost")
        lstm = d.get("forecasted_volatility_lstm")

        if garch and xgb and lstm:
            avg_forecast = (garch + xgb + lstm) / 3
            change = (avg_forecast / vol - 1) * 100
            trend = (
                "increasing"
                if change > 5
                else "decreasing" if change < -5 else "stable"
            )

            summary += f"""
🔮 OUTLOOK:
Forecasted volatility: {avg_forecast:.2%} ({trend}, {change:+.1f}% change)
Models suggest risk is {trend} in the near term.
"""

        return summary

    # Portfolio
    else:
        valid_details = [d for d in details if "error" not in d]
        n = len(valid_details)

        tickers_list = [d["ticker"] for d in valid_details]
        tickers_display = ", ".join(tickers_list[:5])
        if n > 5:
            tickers_display += f" (+{n-5} more)"

        avg_vol = portfolio.get("average_volatility", 0)
        avg_var = abs(portfolio.get("average_VaR_95", 0))
        avg_cvar = abs(portfolio.get("average_CVaR_95", 0))

        # Calculate dispersion
        vol_list = [d["historical_volatility"] for d in valid_details]
        vol_min = min(vol_list) if vol_list else 0
        vol_max = max(vol_list) if vol_list else 0
        vol_range = vol_max - vol_min

        # Risk classification
        if avg_vol > 0.4:
            risk = "HIGH RISK"
            investor = "Aggressive growth investors"
        elif avg_vol > 0.3:
            risk = "MODERATE-HIGH RISK"
            investor = "Growth-oriented investors"
        elif avg_vol > 0.25:
            risk = "MODERATE RISK"
            investor = "Balanced investors"
        elif avg_vol > 0.2:
            risk = "LOW-MODERATE RISK"
            investor = "Conservative to moderate investors"
        else:
            risk = "LOW RISK"
            investor = "Conservative investors"

        # Diversification quality
        if vol_range < 0.15:
            div_quality = "Well-diversified"
        elif vol_range < 0.25:
            div_quality = "Moderately diversified"
        else:
            div_quality = "Concentrated risk profile"

        # Find top risky stocks
        sorted_stocks = sorted(
            valid_details, key=lambda x: x["historical_volatility"], reverse=True
        )
        top_risky = ", ".join(
            [
                f"{d['ticker']} ({d['historical_volatility']:.1%})"
                for d in sorted_stocks[:3]
            ]
        )

        # Practical loss examples
        var_on_100k = avg_var * 100000
        cvar_on_100k = avg_cvar * 100000

        summary = f"""📊 Portfolio Risk Analysis - {n} Securities

Holdings: {tickers_display}

🎯 OVERALL RISK: {risk}
Average Volatility: {avg_vol:.2%}

📉 LOSS POTENTIAL (on $100,000 portfolio):
• Value at Risk (95%): ${var_on_100k:,.0f}
• Conditional VaR (worst 5%): ${cvar_on_100k:,.0f}

📊 DIVERSIFICATION: {div_quality}
• Volatility Range: {vol_min:.1%} to {vol_max:.1%}
• Spread: {vol_range:.1%} percentage points

⚠️  HIGHEST RISK POSITIONS:
{top_risky}

💡 RECOMMENDATION:
• Suitable For: {investor}
• Diversification: {div_quality} - {"consider adding lower volatility assets" if vol_range > 0.25 else "good risk distribution"}
• Monitoring: {"Daily during volatile periods" if avg_vol > 0.3 else "Weekly review recommended"}
• Action: {"Consider reducing exposure to highest volatility stocks" if avg_vol > 0.35 else "Maintain current allocation with quarterly rebalancing"}
"""

        return summary


def get_risk_level(metrics_data: Dict) -> str:
    """
    Get simple risk level classification.
    Returns: 'LOW', 'LOW-MODERATE', 'MODERATE', 'MODERATE-HIGH', or 'HIGH'
    """
    portfolio = metrics_data.get("portfolio_summary", {})
    avg_vol = portfolio.get("average_volatility", 0)
    avg_cvar = abs(portfolio.get("average_CVaR_95", 0))

    if avg_vol > 0.5 or avg_cvar > 0.12:
        return "HIGH"
    elif avg_vol > 0.4 or avg_cvar > 0.09:
        return "MODERATE-HIGH"
    elif avg_vol > 0.3 or avg_cvar > 0.06:
        return "MODERATE"
    elif avg_vol > 0.2 or avg_cvar > 0.04:
        return "LOW-MODERATE"
    else:
        return "LOW"
