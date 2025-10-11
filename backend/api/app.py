from fastapi import FastAPI
from backend.api.risk_models import get_risk_metrics
from typing import List

app = FastAPI()


@app.get("/risk/{ticker}")
def get_single_ticker_risk(ticker: str):
    data = get_risk_metrics(ticker)
    return {
        "metricsByTicker": {
            data["ticker"]: {
                "volatilitySeries": data.get("volatilitySeries", []),
                "VaR_95": data["VaR_95"],
                "CVaR_95": data["CVaR_95"],
                "forecasted_volatility_garch": data["forecasted_volatility_garch"],
                "forecasted_volatility_xgboost": data["forecasted_volatility_xgboost"],
                "forecasted_volatility_lstm": data["forecasted_volatility_lstm"],
            }
        },
        "portfolioVaR": data["VaR_95"],
        "portfolioCVaR": data["CVaR_95"],
    }


@app.post("/portfolio_risk")
def get_portfolio_risk(tickers: List[str]):
    results = {}
    valid = []

    for ticker in tickers:
        try:
            data = get_risk_metrics(ticker)
            results[ticker] = {
                "volatilitySeries": data.get("volatilitySeries", []),
                "VaR_95": data["VaR_95"],
                "CVaR_95": data["CVaR_95"],
                "forecasted_volatility_garch": data["forecasted_volatility_garch"],
                "forecasted_volatility_xgboost": data["forecasted_volatility_xgboost"],
                "forecasted_volatility_lstm": data["forecasted_volatility_lstm"],
            }
            valid.append(data)
        except Exception as e:
            # If any ticker fails, skip it but record minimal info
            results[ticker] = {"error": str(e)}

    if valid:
        avg_var = sum(r["VaR_95"] for r in valid) / len(valid)
        avg_cvar = sum(r["CVaR_95"] for r in valid) / len(valid)
    else:
        avg_var = avg_cvar = None

    return {
        "metricsByTicker": results,
        "portfolioVaR": avg_var,
        "portfolioCVaR": avg_cvar,
    }
