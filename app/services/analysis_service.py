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
        raise ValueError("Not enough candles for RSI") # TODO

    # RSI
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # Volatility
    volatility = df["close"].pct_change().std() * np.sqrt(252)

    # Monte Carlo
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
