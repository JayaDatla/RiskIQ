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

        # Calculate average forecast and trend
        forecast_info = ""
        trend_analysis = ""
        if garch and xgb and lstm:
            avg_forecast = (garch + xgb + lstm) / 3
            change_pct = ((avg_forecast / vol) - 1) * 100
            trend = (
                "increasing"
                if change_pct > 5
                else "decreasing" if change_pct < -5 else "stable"
            )

            forecast_info = f"""
VOLATILITY FORECASTS:
• GARCH Model: {garch:.4f} ({garch*100:.2f}%)
• XGBoost Model: {xgb:.4f} ({xgb*100:.2f}%)
• LSTM Model: {lstm:.4f} ({lstm*100:.2f}%)
• Average Forecast: {avg_forecast:.4f} ({avg_forecast*100:.2f}%)
• Trend: {trend.upper()} ({change_pct:+.1f}% vs current)
"""
            trend_analysis = f"The forecasted volatility is {trend} with an average prediction of {avg_forecast*100:.2f}%, representing a {change_pct:+.1f}% change from current levels."
        else:
            forecast_info = "\nVOLATILITY FORECASTS: Not available for this analysis."
            trend_analysis = "Forecasting data is not available, so focus on historical patterns and current metrics."

        if style == "concise":
            return f"""Analyze this stock's risk comprehensively in 4-5 clear sentences for both retail and professional investors.

Stock: {ticker}

HISTORICAL METRICS:
• Current Volatility: {vol:.4f} ({vol*100:.2f}%)
• VaR (95%): {var:.4f} ({var*100:.2f}%)
• CVaR (95%): {cvar:.4f} ({cvar*100:.2f}%)
{forecast_info}

Provide:
1. Risk level classification (LOW/MODERATE/HIGH/EXTREME) based on {vol*100:.2f}% volatility
2. Historical context: What this volatility means practically (expected price swings, comparison to market average ~15-18%)
3. Forecast outlook: {trend_analysis}
4. Investment recommendation: Who should invest (conservative/moderate/aggressive) and appropriate position sizing

Be clear, use all the exact numbers provided, and connect historical performance with future expectations."""

        elif style == "detailed":
            return f"""Provide a comprehensive risk analysis for {ticker} suitable for both retail and institutional investors, integrating both historical performance and forward-looking forecasts.

HISTORICAL METRICS:
• Historical Volatility: {vol:.4f} ({vol*100:.2f}% annualized)
• Value at Risk (VaR₉₅): {var:.4f} ({var*100:.2f}%)
• Conditional VaR (CVaR₉₅): {cvar:.4f} ({cvar*100:.2f}%)
{forecast_info}

Write 4-5 detailed paragraphs covering:

1. RISK CLASSIFICATION & HISTORICAL CONTEXT: 
   State the risk level (LOW/LOW-MODERATE/MODERATE/MODERATE-HIGH/HIGH/EXTREME) based on the {vol*100:.2f}% historical volatility. Explain what this volatility means in plain English - typical daily price swings (use {(vol/16)*100:.2f}% as daily estimate), how it compares to market average (S&P 500 ~15-18%), and what investors have experienced historically with this stock.

2. LOSS POTENTIAL & PRACTICAL IMPLICATIONS: 
   Explain VaR and CVaR in practical terms. On a $10,000 investment, what losses are possible? Use the actual {var*100:.2f}% VaR (meaning 95% of the time losses won't exceed this) and {cvar*100:.2f}% CVaR (average loss in the worst 5% of cases). Calculate and state dollar amounts explicitly.

3. FORWARD-LOOKING FORECAST ANALYSIS: 
   {trend_analysis} Discuss each forecasting model's prediction (GARCH: {garch*100:.2f if garch else 'N/A'}%, XGBoost: {xgb*100:.2f if xgb else 'N/A'}%, LSTM: {lstm*100:.2f if lstm else 'N/A'}%). Explain what the consensus forecast means - is risk accelerating, moderating, or holding steady? How should investors adjust their expectations based on this outlook?

4. INTEGRATED RISK ASSESSMENT: 
   Synthesize historical and forecast data. If forecasts show increasing volatility, what does this mean on top of already {vol*100:.2f}% volatility? If decreasing, is this a good entry point? Discuss the reliability of forecasts given the historical pattern.

5. ACTIONABLE RECOMMENDATIONS: 
   Who should invest (conservative/moderate/aggressive)? What position size is appropriate (give specific % of portfolio)? Risk management tips: suggest stop-loss levels (e.g., {var*1.5*100:.1f}%), position limits, and monitoring frequency. Should investors wait for forecast trends to materialize or act now?

Be thorough, precise, and actionable. Use ALL numbers provided. Connect historical reality with forecasted expectations. Write in accessible language that both beginners and professionals can understand."""

        else:  # technical
            forecast_metrics = ""
            if garch and xgb and lstm:
                avg_forecast = (garch + xgb + lstm) / 3
                forecast_metrics = (
                    f", σ̂ = {avg_forecast:.4f}, Δσ = {((avg_forecast/vol)-1)*100:+.1f}%"
                )

            return f"""Provide comprehensive technical risk analysis for {ticker} incorporating both realized and forecasted volatility.

METRICS:
Historical: σ = {vol:.4f}, VaR₉₅ = {var:.4f}, CVaR₉₅ = {cvar:.4f}
Forecasts: GARCH = {garch:.4f if garch else 'N/A'}, XGBoost = {xgb:.4f if xgb else 'N/A'}, LSTM = {lstm:.4f if lstm else 'N/A'}{forecast_metrics}

Analyze in 3-4 paragraphs:
1. Volatility regime classification and historical distribution properties (examine CVaR/VaR ratio for tail thickness)
2. Model-based forecast analysis: consensus view, model divergence, and volatility term structure implications
3. Forward risk-adjusted metrics: how forecasted volatility impacts Sharpe ratios, position sizing under Kelly criterion, and optimal leverage
4. Quantitative recommendations: VaR-based position limits, volatility targeting strategies, and hedge ratios

Use quantitative terminology and cite all metrics."""

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

            # Gather forecast data for portfolio
            forecast_data = []
            for d in valid_details:
                garch = d.get("forecasted_volatility_garch")
                xgb = d.get("forecasted_volatility_xgboost")
                lstm = d.get("forecasted_volatility_lstm")
                if garch and xgb and lstm:
                    avg_forecast = (garch + xgb + lstm) / 3
                    forecast_data.append(
                        {
                            "ticker": d["ticker"],
                            "current": d["historical_volatility"],
                            "forecast": avg_forecast,
                            "change": ((avg_forecast / d["historical_volatility"]) - 1)
                            * 100,
                        }
                    )

            forecast_summary = ""
            if forecast_data:
                avg_forecast_vol = sum(f["forecast"] for f in forecast_data) / len(
                    forecast_data
                )
                avg_change = sum(f["change"] for f in forecast_data) / len(
                    forecast_data
                )
                increasing = sum(1 for f in forecast_data if f["change"] > 5)
                decreasing = sum(1 for f in forecast_data if f["change"] < -5)
                stable = len(forecast_data) - increasing - decreasing

                forecast_summary = f"""
PORTFOLIO FORECAST SUMMARY:
• Securities with Forecasts: {len(forecast_data)} of {n}
• Average Forecasted Volatility: {avg_forecast_vol:.4f} ({avg_forecast_vol*100:.2f}%)
• Average Change: {avg_change:+.1f}%
• Trend Distribution: {increasing} increasing, {decreasing} decreasing, {stable} stable
• Top Volatile Forecasts: {", ".join([f"{f['ticker']} ({f['forecast']*100:.1f}%)" for f in sorted(forecast_data, key=lambda x: x['forecast'], reverse=True)[:3]])}
"""
            else:
                forecast_summary = "\nPORTFOLIO FORECASTS: Limited forecast data available for this portfolio."

        if style == "concise":
            risky_stocks_str = ", ".join(
                [f"{t} ({v*100:.1f}%)" for t, v in top_3_risky]
            )

            return f"""Provide a comprehensive portfolio risk summary in 5-6 sentences, covering both historical performance and forward outlook.

Portfolio: {n} stocks - {ticker_str}

HISTORICAL METRICS:
• Average Volatility: {avg_vol:.4f} ({avg_vol*100:.2f}%)
• Average VaR (95%): {avg_var:.4f} ({avg_var*100:.2f}%)
• Average CVaR (95%): {avg_cvar:.4f} ({avg_cvar*100:.2f}%)
• Volatility Range: {vol_min:.4f} to {vol_max:.4f}
• Top 3 Riskiest: {risky_stocks_str}
{forecast_summary}

Provide:
1. Overall risk level with specific {avg_vol*100:.2f}% volatility context and comparison to market benchmarks
2. Historical diversification quality assessment using the {(vol_max-vol_min)*100:.2f} percentage point spread
3. Forward-looking forecast analysis: is portfolio risk trending up, down, or stable?
4. Concentration concerns and practical loss scenarios on $100,000
5. Clear recommendation for investor type and any portfolio adjustments needed

Use all numbers provided and integrate historical patterns with forecast expectations."""

        elif style == "detailed":
            risky_stocks_str = ", ".join(
                [f"{t} ({v*100:.1f}%)" for t, v in top_3_risky]
            )

            return f"""Provide a comprehensive portfolio risk analysis for both retail and institutional investors, integrating historical performance with forward-looking forecasts.

PORTFOLIO: {n} Securities
Holdings: {ticker_str}

HISTORICAL METRICS:
• Average Volatility: {avg_vol:.4f} ({avg_vol*100:.2f}% annualized)
• Average VaR (95%): {avg_var:.4f} ({avg_var*100:.2f}%)
• Average CVaR (95%): {avg_cvar:.4f} ({avg_cvar*100:.2f}%)
• Volatility Range: {vol_min:.4f} ({vol_min*100:.2f}%) to {vol_max:.4f} ({vol_max*100:.2f}%)
• Standard Deviation: {vol_std:.4f}
• Top 3 Riskiest Holdings: {risky_stocks_str}
{forecast_summary}

Write 5-6 comprehensive paragraphs covering:

1. OVERALL RISK PROFILE & HISTORICAL CONTEXT: 
   Classify portfolio risk level using the {avg_vol*100:.2f}% average volatility. Compare this to market benchmarks (S&P 500 ~15-18%, high-growth portfolios ~25-30%). What has this portfolio's historical volatility meant in practice? Estimate typical daily portfolio swings. What type of investor has historically succeeded with this risk profile?

2. DIVERSIFICATION ANALYSIS: 
   Evaluate the volatility range from {vol_min*100:.2f}% to {vol_max*100:.2f}%. The {(vol_max-vol_min)*100:.2f} percentage point spread indicates what level of diversification? Is this well-diversified or concentrated? How does the standard deviation of {vol_std*100:.2f}% reflect portfolio construction quality? Discuss whether the portfolio achieves genuine diversification or merely holds multiple correlated assets.

3. FORWARD-LOOKING FORECAST INTEGRATION: 
   Analyze the forecast data in detail. How many securities have forecasts? What is the average forecasted volatility ({avg_forecast_vol*100:.2f if forecast_data else 'N/A'}%) compared to current {avg_vol*100:.2f}%? How many holdings show increasing vs decreasing risk? Identify specific securities where forecasts signal major changes. What does the overall forecast trend mean for portfolio risk in coming periods?

4. CONCENTRATION RISKS & KEY HOLDINGS: 
   Deep dive into the riskiest holdings: {risky_stocks_str}. What percentage of the portfolio do these represent? Are there concerning concentrations? How do their individual forecasts look? On a $100,000 portfolio, calculate realistic loss scenarios: use {avg_var*100:.2f}% VaR (95% confidence daily loss limit) and {avg_cvar*100:.2f}% CVaR (average loss in worst 5% of days). Provide dollar amounts.

5. INTEGRATED RISK-RETURN OUTLOOK: 
   Synthesize historical performance with forecast expectations. If forecasts show rising volatility across the portfolio, what does this mean for risk-adjusted returns? If volatility is moderating, is this a sign of maturing positions or reduced opportunities? How reliable are the forecasts given historical patterns? Should investors view forecasts as actionable signals or merely informational?

6. ACTIONABLE RECOMMENDATIONS: 
   Should any positions be reduced based on both high historical volatility AND concerning forecasts? Recommend specific rebalancing actions. How should investors monitor this portfolio (daily/weekly/monthly)? What triggers should prompt action (e.g., if volatility exceeds X% or forecasts deteriorate)? Suggest suitable allocation as % of total net worth. Recommend position size limits for riskiest holdings. Consider both current risk and forecasted trends in your recommendations.

Be thorough, precise, and actionable. Use ALL numbers provided. Explicitly connect historical metrics with forecast data to give investors a complete picture. Write in accessible language for both beginners and professionals."""

        else:  # technical
            forecast_metrics = ""
            if forecast_data:
                avg_forecast_vol = sum(f["forecast"] for f in forecast_data) / len(
                    forecast_data
                )
                forecast_metrics = f", σ̂ = {avg_forecast_vol:.4f}, Δσ̄ = {sum(f['change'] for f in forecast_data) / len(forecast_data):+.1f}%"

            return f"""Provide comprehensive technical portfolio analysis incorporating realized and forecasted volatility.

PORTFOLIO METRICS:
Historical: N={n}, σ̄={avg_vol:.4f}, VaR₉₅={avg_var:.4f}, CVaR₉₅={avg_cvar:.4f}
Dispersion: Range=[{vol_min:.4f}, {vol_max:.4f}], σ(σ)={vol_std:.4f}
Forecasts: n_forecasts={len(forecast_data) if forecast_data else 0}{forecast_metrics}

Analyze in 4-5 paragraphs:
1. Portfolio volatility regime and historical distribution characteristics (tail risk metrics, skewness implications)
2. Diversification quality: assess dispersion metrics and cross-sectional volatility distribution
3. Forward volatility analysis: model-based forecasts, consensus outlook, term structure of portfolio volatility
4. Risk decomposition: identify concentrated exposures, marginal VaR contributions, factor-based risk attribution
5. Optimization implications: mean-variance efficiency given forecasts, rebalancing triggers, volatility targeting strategies, and optimal hedge ratios

Use quantitative terminology and cite all metrics comprehensively."""


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

CRITICAL FORMATTING RULES:
- Write in normal paragraphs only - NO bullet points, NO numbered lists
- NEVER use markdown formatting like **bold**, *italic*, or any asterisks
- For emphasis, use ALL CAPS for important words/phrases (e.g., HIGH RISK, MODERATE VOLATILITY)
- NO special characters for formatting (no *, _, `, etc.)
- Keep it clean, professional text only

Keep analysis concise but comprehensive - quality over quantity.""",
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

⚠️ HIGHEST RISK POSITIONS:
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
