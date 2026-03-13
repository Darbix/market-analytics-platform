import typer
import time
from datetime import datetime
from typing import Optional

from cli_tool.api import (
    request_price_history,
    run_analysis,
    get_job,
    get_analysis,
    get_prices
)

app = typer.Typer(help="Market Analytics CLI")

# ---- Shared options ----
start_time_option = typer.Option(
    None,
    "--start-time",
    formats=["%Y-%m-%d", "%Y-%m-%dT%H:%M"],
    help="UTC start time (YYYY-MM-DD or YYYY-MM-DDTHH:MM). Example: 2026-01-20T00:00",
)
end_time_option = typer.Option(
    None,
    "--end-time",
    formats=["%Y-%m-%d", "%Y-%m-%dT%H:%M"],
    help="UTC end time (YYYY-MM-DD or YYYY-MM-DDTHH:MM). Example: 2026-03-01T00:00",
)


def wait_for_job(job_id: int, delay=2):
    while True:
        job = get_job(job_id)
        status = job["status"]

        typer.echo(f"Job {job_id} status: {status}")

        if status in ["completed", "failed"]:
            return status

        time.sleep(delay)


@app.command()
def download(
    symbol: str = typer.Argument(..., help="Ticker symbol (e.g., BTCUSDT)."),
    interval: str = typer.Option("1d", help="Timeframe interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)."),
    limit: int = typer.Option(365, help="Number of data points to fetch."),
    start_time: Optional[datetime] = start_time_option,
    end_time: Optional[datetime] = end_time_option

):
    """Download price history."""

    typer.echo("Requesting price history download...")

    res = request_price_history(symbol, interval, limit, start_time, end_time)
    job_id = res["job_id"]
    typer.echo(f"Job created: {job_id}")

    status = wait_for_job(job_id)

    if status == "completed":
        typer.echo("Download completed!\nFetching data...")
        prices = get_prices(symbol, interval, limit, start_time, end_time)
        for p in prices["prices"]:
            typer.echo(p)
    else:
        typer.echo("Download failed")


@app.command()
def analyze(
    symbol: str = typer.Argument(..., help="Ticker symbol (e.g., BTCUSDT)."),
    interval: str = typer.Option("1d", help="Timeframe interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)."),
    limit: int = typer.Option(365, help="Number of data points to fetch."),
    start_time: Optional[datetime] = start_time_option,
    end_time: Optional[datetime] = end_time_option,
    monte_carlo_runs: int = typer.Option(1000, help="Number of simulation runs.")

):
    """Run analytics on market data."""

    typer.echo("Starting analysis...")
    res = run_analysis(symbol, interval, limit, start_time, end_time, monte_carlo_runs)
    job_id = res["job_id"]
    typer.echo(f"Job created: {job_id}")

    status = wait_for_job(job_id)

    if status != "completed":
        typer.echo("Analysis failed")
        raise typer.Exit()

    result = get_analysis(job_id)

    data = result["data"]

    typer.echo("\n=== Analysis Result ===")
    typer.echo(f"Volatility: {data['volatility']:.4f}")
    typer.echo(f"RSI: {data['rsi_last']:.2f}")
    typer.echo(f"Monte Carlo Mean: {data['monte_carlo_mean']:.2f}")
