import requests
import os
from typing import Dict, Optional


def generate_ai_summary(
    metrics_data: Dict, style: str = "concise", hf_token: Optional[str] = None
) -> str:
    """
    Generate AI summary from risk metrics.

    Args:
        metrics_data: Your metrics dict with 'portfolio_summary' and 'details'
        style: 'concise' (default), 'detailed', or 'technical'
        hf_token: Hugging Face token (or set HUGGINGFACE_TOKEN env var)

    Returns:
        Summary string with risk analysis
    """

    # Get HF token
    token = hf_token or os.getenv("HUGGINGFACE_TOKEN")

    # If no token, return rule-based summary (fallback)
    if not token:
        return _fallback_summary(metrics_data)

    try:
        # Create prompt
        prompt = _create_prompt(metrics_data, style)

        # Call HF API
        summary = _call_llm(prompt, token)

        return summary

    except Exception as e:
        print(f"LLM failed, using fallback: {e}")
        return _fallback_summary(metrics_data)


def _create_prompt(metrics_data: Dict, style: str) -> str:
    """Create prompt based on single ticker or portfolio."""

    details = metrics_data.get("details", [])
    portfolio = metrics_data.get("portfolio_summary", {})

    # Single ticker
    if len(details) == 1:
        d = details[0]
        ticker = d["ticker"]
        vol = d["historical_volatility"]
        var = d["VaR_95"]
        cvar = d["CVaR_95"]

        if style == "concise":
            return f"""Analyze this stock in 2-3 sentences:
{ticker}: Volatility={vol:.4f}, VaR(95%)={var:.4f}, CVaR={cvar:.4f}
Explain risk level for investors."""

        elif style == "detailed":
            garch = d.get("forecasted_volatility_garch", "N/A")
            xgb = d.get("forecasted_volatility_xgboost", "N/A")
            lstm = d.get("forecasted_volatility_lstm", "N/A")

            return f"""Detailed risk analysis:
{ticker}
Current: Vol={vol:.4f}, VaR={var:.4f}, CVaR={cvar:.4f}
Forecast: GARCH={garch}, XGBoost={xgb}, LSTM={lstm}

Write paragraph on: risk level, future outlook, investment advice."""

        else:  # technical
            return f"""Technical analysis for {ticker}:
σ={vol:.4f}, VaR₉₅={var:.4f}, CVaR₉₅={cvar:.4f}
Interpret these risk metrics."""

    # Portfolio
    else:
        tickers = ", ".join(portfolio["tickers"])
        avg_vol = portfolio["average_volatility"]
        avg_var = portfolio["average_VaR_95"]
        avg_cvar = portfolio["average_CVaR_95"]
        n = len(portfolio["tickers"])

        if style == "concise":
            return f"""Summarize portfolio risk in 2-3 sentences:
{n} stocks: {tickers}
Avg Vol={avg_vol:.4f}, VaR={avg_var:.4f}, CVaR={avg_cvar:.4f}"""

        elif style == "detailed":
            return f"""Portfolio analysis:
{n} stocks: {tickers}
Average Vol={avg_vol:.4f}, VaR={avg_var:.4f}, CVaR={avg_cvar:.4f}

Assess: overall risk, diversification benefit, recommendation."""

        else:
            return f"""Technical portfolio metrics:
N={n}, σ̄={avg_vol:.4f}, VaR₉₅={avg_var:.4f}, CVaR₉₅={avg_cvar:.4f}"""


def _call_llm(prompt: str, token: str, max_retries: int = 3) -> str:
    """Call Hugging Face API."""

    # Using Flan-T5-base (best free option)
    url = "https://api-inference.huggingface.co/models/google/flan-t5-base"

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
        },
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").strip()
                elif isinstance(result, dict):
                    return result.get("generated_text", "").strip()

            elif response.status_code == 503:
                # Model loading, wait and retry
                print(f"Model loading... retry {attempt + 1}/{max_retries}")
                import time

                time.sleep(10)
                continue

            else:
                print(f"API error: {response.status_code}")

        except Exception as e:
            print(f"Request failed: {e}")
            if attempt < max_retries - 1:
                import time

                time.sleep(5)

    raise Exception("LLM API failed after retries")


def _fallback_summary(metrics_data: Dict) -> str:
    """Rule-based summary if LLM fails."""

    details = metrics_data.get("details", [])
    portfolio = metrics_data.get("portfolio_summary", {})

    # Single ticker
    if len(details) == 1:
        d = details[0]
        ticker = d["ticker"]
        vol = d["historical_volatility"]
        var = abs(d["VaR_95"])
        cvar = abs(d["CVaR_95"])

        # Assess risk
        if vol > 0.5:
            risk = "HIGH RISK"
            desc = "very high volatility"
        elif vol > 0.35:
            risk = "MODERATE-HIGH RISK"
            desc = "elevated volatility"
        elif vol > 0.25:
            risk = "MODERATE RISK"
            desc = "moderate volatility"
        else:
            risk = "LOW-MODERATE RISK"
            desc = "relatively stable"

        summary = f"📊 {ticker} Risk Analysis\n\n"
        summary += f"Risk Level: {risk}\n"
        summary += f"Historical Volatility: {vol:.2%}\n"
        summary += f"Value at Risk (95%): {var:.2%}\n"
        summary += f"Conditional VaR: {cvar:.2%}\n\n"
        summary += f"{ticker} exhibits {desc} with annualized volatility of {vol:.2%}. "
        summary += f"At 95% confidence, potential maximum loss (VaR) is {var:.2%}. "

        if vol > 0.4:
            summary += "This is a high-risk investment suitable only for aggressive portfolios with high risk tolerance."
        elif vol > 0.25:
            summary += "Suitable for balanced portfolios with moderate risk tolerance."
        else:
            summary += "Suitable for conservative portfolios seeking stability."

        return summary

    # Portfolio
    else:
        n = len(details)
        tickers = ", ".join(portfolio["tickers"][:5])  # First 5
        if n > 5:
            tickers += f"... (+{n-5} more)"

        avg_vol = portfolio["average_volatility"]
        avg_var = abs(portfolio["average_VaR_95"])
        avg_cvar = abs(portfolio["average_CVaR_95"])

        # Portfolio risk level
        if avg_vol > 0.4:
            risk = "HIGH RISK"
        elif avg_vol > 0.3:
            risk = "MODERATE-HIGH RISK"
        elif avg_vol > 0.2:
            risk = "MODERATE RISK"
        else:
            risk = "LOW RISK"

        # Find outliers
        high_risk = [d for d in details if d["historical_volatility"] > avg_vol * 1.3]
        low_risk = [d for d in details if d["historical_volatility"] < avg_vol * 0.7]

        summary = f"📊 Portfolio Risk Analysis ({n} stocks)\n\n"
        summary += f"Overall Risk: {risk}\n"
        summary += f"Average Volatility: {avg_vol:.2%}\n"
        summary += f"Average VaR (95%): {avg_var:.2%}\n"
        summary += f"Average CVaR: {avg_cvar:.2%}\n\n"
        summary += f"Portfolio includes: {tickers}\n\n"
        summary += f"The portfolio shows average volatility of {avg_vol:.2%} across {n} stocks. "

        if len(high_risk) > 0:
            summary += f"{len(high_risk)} high-volatility stocks detected. "

        summary += (
            f"Diversification across {n} assets helps reduce overall portfolio risk. "
        )

        if avg_vol > 0.35:
            summary += "This is an aggressive portfolio requiring close monitoring."
        elif avg_vol > 0.25:
            summary += "Suitable for moderate risk tolerance with regular rebalancing."
        else:
            summary += "Well-balanced portfolio for conservative to moderate investors."

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


# Quick test
if __name__ == "__main__":
    # Test with example data
    test_data = {
        "portfolio_summary": {
            "tickers": ["ADANIGREEN.NS"],
            "average_volatility": 0.54359,
            "average_VaR_95": -0.05777,
            "average_CVaR_95": -0.09612,
        },
        "details": [
            {
                "ticker": "ADANIGREEN.NS",
                "historical_volatility": 0.54359,
                "VaR_95": -0.05777,
                "CVaR_95": -0.09612,
                "forecasted_volatility_garch": 0.0217,
                "forecasted_volatility_xgboost": 0.0109,
                "forecasted_volatility_lstm": 0.00182,
            }
        ],
    }

    print("Testing Summary Generator...")
    print("=" * 60)

    # Test fallback (no token)
    summary = generate_ai_summary(test_data, style="concise")
    print(summary)
    print("\n" + "=" * 60)

    # Test risk level
    risk = get_risk_level(test_data)
    print(f"Risk Level: {risk}")
