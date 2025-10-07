import yfinance as yf
import pandas as pd


def fetch_stock_data(ticker, period="1yr", interval="1d"):
    """
    Fetch historical stock data for a given ticker symbol.

    Parameters:
    - ticker (str): The stock ticker symbol.
    - period (str): The period over which to fetch data (e.g., '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max').
    - interval (str): The data interval (e.g., '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo').

    Returns:
    - pd.DataFrame: A DataFrame containing the historical stock data.
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)

    hist.reset_index(inplace=True)
    hist["Date"] = hist["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")

    hist.dropna(inplace=True)

    return hist


def compute_returns(hist):
    """
    Compute daily returns from historical stock data.

    Parameters:
    - hist (pd.DataFrame): DataFrame containing historical stock data with a 'Close' column.

    Returns:
    - pd.Series: A Series containing the daily returns.
    """

    hist["Return"] = hist["Close"].pct_change()
    hist.dropna(inplace=True)

    return hist["Return"]


def prepare_data(ticker, period="1yr", interval="1d"):
    """
    Fetch historical stock data and compute daily returns.

    Parameters:
    - ticker (str): The stock ticker symbol.
    - period (str): The period over which to fetch data.
    - interval (str): The data interval.

    Returns:
    - pd.DataFrame: A DataFrame containing the historical stock data with returns.
    """
    hist = fetch_stock_data(ticker, period, interval)
    hist["Return"] = compute_returns(hist)

    return hist
