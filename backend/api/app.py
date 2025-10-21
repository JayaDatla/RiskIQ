from fastapi import FastAPI
from typing import List
from backend.api.risk_models import get_risk_metrics

app = FastAPI()


@app.get("/risk/{ticker}")
def get_single_ticker_risk(ticker: str):
    data = get_risk_metrics(ticker)
    return {
        "portfolio_summary": {
            "tickers": [data["ticker"]],
            "average_volatility": data["historical_volatility"],
            "average_VaR_95": data["VaR_95"],
            "average_CVaR_95": data["CVaR_95"],
        },
        "details": [data],
    }


@app.post("/portfolio_risk")
def get_portfolio_risk(tickers: List[str]):
    results = []
    for ticker in tickers:
        try:
            data = get_risk_metrics(ticker)
            results.append(data)
        except Exception as e:
            results.append({"ticker": ticker, "error": str(e)})

    valid = [r for r in results if "error" not in r]
    if valid:
        avg_vol = sum(r["historical_volatility"] for r in valid) / len(valid)
        avg_var = sum(r["VaR_95"] for r in valid) / len(valid)
        avg_cvar = sum(r["CVaR_95"] for r in valid) / len(valid)
    else:
        avg_vol = avg_var = avg_cvar = None

    return {
        "portfolio_summary": {
            "tickers": [r["ticker"] for r in valid],
            "average_volatility": avg_vol,
            "average_VaR_95": avg_var,
            "average_CVaR_95": avg_cvar,
        },
        "details": results,
    }
