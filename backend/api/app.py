from fastapi import FastAPI
from typing import List
from backend.api.risk_models import get_risk_metrics
from llama_cpp import Llama
import os
import json
import urllib.request

app = FastAPI(title="RiskIQ Backend with Financial LLM Summaries")

MODEL_DIR = "models"
MODEL_NAME = "phi-3-mini-4k-instruct-q4.gguf"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)
HF_MODEL_URL = (
    "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/"
    + MODEL_NAME
)

os.makedirs(MODEL_DIR, exist_ok=True)

if not os.path.exists(MODEL_PATH):
    print(f"🔽 Downloading model from {HF_MODEL_URL} ...")
    urllib.request.urlretrieve(HF_MODEL_URL, MODEL_PATH)
    print("✅ Model downloaded successfully.")

llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=4, verbose=False)


def generate_summary(data: dict) -> str:
    prompt = f"""
You are a professional financial analyst writing executive summaries.

Summarize the following risk report for either a single asset or a portfolio.
Include historical volatility, VaR, CVaR, and forecasted volatilities from GARCH, XGBoost, and LSTM models.

Be concise (max 150 words), factual, and professional.

Data:
{json.dumps(data, indent=2)}

Summary:
"""
    try:
        result = llm(prompt, max_tokens=220, stop=["Summary:"], temperature=0.6)
        summary_text = result["choices"][0]["text"].strip()
        if not summary_text:
            summary_text = "Unable to generate forecast summary at this time."
        return summary_text
    except Exception as e:
        return f"Error generating summary: {str(e)}"


@app.get("/risk/{ticker}")
def get_single_ticker_risk(ticker: str):
    data = get_risk_metrics(ticker)
    response = {
        "portfolio_summary": {
            "tickers": [data["ticker"]],
            "average_volatility": data["historical_volatility"],
            "average_VaR_95": data["VaR_95"],
            "average_CVaR_95": data["CVaR_95"],
        },
        "details": [data],
    }
    response["summary"] = generate_summary(response)
    return response


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

    response = {
        "portfolio_summary": {
            "tickers": [r["ticker"] for r in valid],
            "average_volatility": avg_vol,
            "average_VaR_95": avg_var,
            "average_CVaR_95": avg_cvar,
        },
        "details": results,
    }

    response["summary"] = generate_summary(response)
    return response
