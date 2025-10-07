from fastapi import FastAPI
from backend.api.risk_models import get_risk_metrics


app = FastAPI(
    title="RiskIQ Backend API",
    description="Backend service that provides risk analytics and volatility forecasts using GARCH, XGBoost, and LSTM models.",
    version="1.0.0",
)


@app.get("/")
def home():
    return {"message": "Welcome to RiskIQ API 👋"}


@app.get("/risk-metrics/{ticker}")
def get_metrics(ticker: str, period: str = "1y", interval: str = "1d"):
    """
    Fetch and compute all risk metrics for a given stock ticker.
    Example: /risk-metrics/AAPL?period=6mo&interval=1d

    """
    try:
        result = get_risk_metrics(ticker, period, interval)
        return result
    except Exception as e:
        return {"error": str(e)}
