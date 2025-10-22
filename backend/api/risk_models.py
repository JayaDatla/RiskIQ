from unittest import result
import pandas as pd
import numpy as np
from scipy.stats import norm
from arch import arch_model
from sympy import per
import xgboost as xgb
import joblib
import torch
import torch.nn as nn
import warnings
import os
from backend.api.fetch_data import prepare_data
import yfinance as yf

warnings.filterwarnings("ignore")

# ============================================================
#  VOLATILITY & RISK MEASURES
# ============================================================


def compute_volatility(returns):
    """
    Compute annualized volatility from daily returns.

    Volatility is a statistical measure of the dispersion of returns for a given security or market index.
    It quantifies the degree of variation of a trading price series over time. High volatility indicates
    large price swings, while low volatility suggests more stable prices.

    Volatility is calculated as the standard deviation of daily returns
    multiplied by the square root of 252 (approx. trading days in a year).

    Parameters:
    returns : pd.Series
        Series of daily percentage returns.

    Returns:
    float
        Annualized volatility estimate.
    """
    returns = returns.dropna()
    vol = returns.std()
    ann_vol = vol * np.sqrt(252)
    return ann_vol


def compute_var(returns, confidence_level=0.95):
    """
    Compute Value at Risk (VaR) using the parametric (normal distribution) method.

    Value at Risk (VaR) estimates the maximum expected loss for a given confidence level
    over a specified time horizon.

    Parameters:
    returns : pd.Series
        Series of returns.
    confidence_level : float, optional
        Confidence level for VaR calculation (default = 0.95).

    Returns:
    float
        Value at Risk (negative value indicates potential loss).
    """
    mu = returns.mean()
    sigma = returns.std()
    var = norm.ppf(1 - confidence_level, mu, sigma)
    return var


def compute_cvar(returns, confidence=0.95):
    """
    Compute Conditional Value at Risk (CVaR), also known as Expected Shortfall.

    CVaR measures the expected loss beyond the Value at Risk (VaR) threshold —
    essentially, the average of the worst-case losses.

    Parameters:
    returns : pd.Series
        Series of returns.
    confidence : float, optional
        Confidence level (default = 0.95).

    Returns:
    float
        Conditional Value at Risk.
    """
    var = compute_var(returns, confidence)
    cvar = returns[returns < var].mean()
    return cvar


# ============================================================
#  GARCH MODEL
# ============================================================


def run_garch(returns):
    """
    Fit a GARCH(1,1) model to returns and forecast next-period volatility.

    GARCH (Generalized Autoregressive Conditional Heteroskedasticity) models
    estimate time-varying volatility in financial time series.

    Parameters:
    returns : pd.Series
        Series of returns.

    Returns:
    float
        Forecasted volatility for the next period.
    """
    model = arch_model(returns, vol="Garch", p=1, q=1)
    fitted_model = model.fit(disp="off")
    forecast = fitted_model.forecast(horizon=1)
    next_vol = np.sqrt(forecast.variance.values[-1][0])
    return next_vol


# ============================================================
#  XGBOOST MODEL
# ============================================================


def build_features(returns):
    """
    Build features for XGBoost model from returns.

    This version matches the features used during training:
    - RollingVolatility: 20-day rolling std deviation of returns
    - RollingMean: 20-day rolling mean of returns
    - Lag1, Lag2, Lag3: Previous return lags

    Parameters:
    returns : pd.Series
        Series of returns.

    Returns:
    pd.DataFrame
        DataFrame of features for the XGBoost model.
    """
    df = pd.DataFrame()
    df["RollingVolatility"] = returns.rolling(window=20).std()
    df["RollingMean"] = returns.rolling(window=20).mean()
    df["Lag1"] = returns.shift(1)
    df["Lag2"] = returns.shift(2)
    df["Lag3"] = returns.shift(3)
    df = df.dropna()
    return df


def run_xgboost(returns):
    """
    Predict next-period volatility using a pretrained XGBoost model.

    XGBoost (Extreme Gradient Boosting) is a high-performance machine learning algorithm
    particularly suited for structured tabular data.

    The model is pretrained and stored in 'backend/model_store/xgb_vol_model.joblib'.

    Parameters:
    returns : pd.Series
        Series of returns.

    Returns:
    float
        Predicted next-period volatility.
    """
    model_path = os.path.join("backend", "model_store", "xgb_vol_model.joblib")

    if not os.path.exists(model_path):
        raise FileNotFoundError("Pretrained XGBoost model not found.")

    model = joblib.load(model_path)
    X = build_features(returns)
    latest_features = X.tail(1)

    predicted_vol = model.predict(latest_features)
    return predicted_vol[0]


# ============================================================
#  LSTM MODEL
# ============================================================


class LSTMVolatilityModel(nn.Module):
    """
    LSTM model for volatility prediction.

    Long Short-Term Memory (LSTM) networks capture sequential dependencies
    and are particularly effective for time series forecasting.
    """

    def __init__(self, input_size=1, hidden_size=64, num_layers=2, output_size=1):
        super(LSTMVolatilityModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h0 = torch.zeros(2, x.size(0), 64)
        c0 = torch.zeros(2, x.size(0), 64)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out


def run_lstm(returns):
    """
    Predict next-period volatility using a pretrained LSTM model.

    The LSTM model is pretrained and stored in 'backend/model_store/lstm_vol_model.pth'.

    Parameters:
    returns : pd.Series
        Series of returns.

    Returns:
    float
        Predicted next-period volatility.
    """
    model_path = os.path.join("backend", "model_store", "lstm_vol_model.pt")

    if not os.path.exists(model_path):
        raise FileNotFoundError("Pretrained LSTM model not found.")

    model = LSTMVolatilityModel()
    model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
    model.eval()

    seq_len = 10
    series = returns[-seq_len:].values.reshape(1, seq_len, 1)
    series = torch.tensor(series, dtype=torch.float32)

    with torch.no_grad():
        pred = model(series).item()

    return pred


# ============================================================
#  MASTER FUNCTION — COMBINE ALL METRICS
# ============================================================


def convert_numpy_types(obj, round_to=5):
    """Recursively convert NumPy types to native Python types and round floats."""
    import numpy as np

    if isinstance(obj, dict):
        return {k: convert_numpy_types(v, round_to) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(i, round_to) for i in obj]
    elif isinstance(obj, (np.float32, np.float64, float)):
        return round(float(obj), round_to)
    elif isinstance(obj, (np.int32, np.int64, int)):
        return int(obj)
    else:
        return obj


def get_risk_metrics(ticker, period="1y", interval="1d"):
    """
    Fetch historical data, compute statistical risk metrics, and generate volatility forecasts.
    """
    hist = prepare_data(ticker, period, interval)
    # Detect currency (best-effort)
    try:
        yf_t = yf.Ticker(ticker)
        currency = getattr(getattr(yf_t, "fast_info", {}), "currency", None)
        if not currency:
            info = getattr(yf_t, "info", {}) or {}
            currency = info.get("currency")
        currency = currency or "USD"
    except Exception:
        currency = "USD"
    returns = hist["Return"].dropna()

    # --- Compute historical metrics ---
    hist_vol = compute_volatility(returns)
    var_95 = compute_var(returns)
    cvar_95 = compute_cvar(returns)

    # --- Forecast future volatility ---
    garch_vol = run_garch(returns)
    xgb_vol = run_xgboost(returns)
    lstm_vol = run_lstm(returns)

    # --- Prepare historical data for frontend charts ---
    hist_chart = (
        hist[["Date", "Close", "Return"]].dropna().tail(252)
    )  # 1 year ~ 252 trading days
    hist_chart["Date"] = hist_chart["Date"].astype(str)

    result = {
        "ticker": ticker,
        "historical_volatility": float(hist_vol),
        "VaR_95": float(var_95),
        "CVaR_95": float(cvar_95),
        "forecasted_volatility_garch": float(garch_vol),
        "forecasted_volatility_xgboost": float(xgb_vol),
        "forecasted_volatility_lstm": float(lstm_vol),
        "historical_data": hist_chart.to_dict(orient="records"),
        "currency": currency,
    }

    return convert_numpy_types(result)
