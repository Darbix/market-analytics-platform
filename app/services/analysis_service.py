import numpy as np
import pandas as pd


def compute_analysis(data: list, monte_carlo_runs: int):
    df = pd.DataFrame(data)
    df.columns = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "_", "_", "_", "_", "_"
    ]

    df["close"] = df["close"].astype(float)

    if len(df) < 15:
        raise ValueError("Not enough candles for RSI")

    # ----- RSI -----
    RSI_PERIOD = 14
    RSI_SCALE = 100
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(RSI_PERIOD).mean()
    loss = -delta.clip(upper=0).rolling(RSI_PERIOD).mean()
    rs = gain / loss
    rsi = RSI_SCALE - (RSI_SCALE / (1 + rs))


    # ----- Volatility -----
    # Calculate periods per year dynamically
    periods_per_year = 365
    timestamps = pd.to_datetime(df["open_time"], unit="ms")
    if len(timestamps) >= 2:
        delta_seconds = (timestamps.iloc[-1] - timestamps.iloc[0]).total_seconds()
        periods = len(timestamps) - 1
        seconds_per_period = delta_seconds / periods
        seconds_per_year = 365 * 24 * 60 * 60
        periods_per_year = seconds_per_year / seconds_per_period
    
    # Compute annualized volatility
    returns = df["close"].pct_change().dropna()
    volatility = returns.std() * np.sqrt(periods_per_year)


    # ----- Monte Carlo -----
    last_price = df["close"].iloc[-1]
    returns = df["close"].pct_change().dropna()
    mu = returns.mean()
    sigma = returns.std()

    simulations = []

    for _ in range(monte_carlo_runs):
        price = last_price
        for _ in range(30):
            price *= (1 + np.random.normal(mu, sigma))
        simulations.append(price)

    mc_mean = float(np.mean(simulations))

    return {
        "volatility": float(volatility),
        "rsi_last": float(rsi.iloc[-1]),
        "monte_carlo_mean": mc_mean,
    }
