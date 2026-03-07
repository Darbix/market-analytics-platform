import React, { useState } from "react";
import { Line } from "react-chartjs-2";
import { JobStatus } from "../constants/jobStatus";
import PriceChart from "../components/PriceChart.jsx";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler
);


export default function MarketAnalytics() {
  // Shared inputs
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [interval, setInterval] = useState("1d");
  const [limit, setLimit] = useState(365);

  // Price history state
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [prices, setPrices] = useState([]);
  const [priceJobId, setPriceJobId] = useState(null);
  const [priceStatus, setPriceStatus] = useState(null);

  // Analysis state
  const [monteCarlo, setMonteCarlo] = useState(1000);
  const [analysisJobId, setAnalysisJobId] = useState(null);
  const [analysisStatus, setAnalysisStatus] = useState(null);
  const [result, setResult] = useState(null);

  const handleFullAnalysis = async () => {
    // Clear old results
    setResult(null);
    setPrices([]);
    
    // Download price data
    await requestPriceDownload();
  };

  const requestPriceDownload = async () => {
    try {
      setPriceStatus(JobStatus.PENDING);
      setAnalysisStatus(JobStatus.PENDING);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      const res = await fetch("/api/price-history", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol,
          interval,
          limit,
          startTime: startTime || null,
          endTime: endTime || null,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!res.ok)
        throw new Error("Failed to request price download");

      const data = await res.json();
      setPriceJobId(data.job_id);
      pollPriceJob(data.job_id);
    }
    catch (err) {
      console.error(err);
      setPriceStatus(JobStatus.FAILED);
      setAnalysisStatus(JobStatus.FAILED);
    }
  };

  const pollPriceJob = async (id) => {
    const res = await fetch(`/api/jobs/${id}`);
    const data = await res.json();

    if ([JobStatus.PENDING, JobStatus.PROCESSING].includes(data.status)) {
      setPriceStatus(JobStatus.PROCESSING);
      setTimeout(() => pollPriceJob(id), 2000);
    }
    else if (data.status === JobStatus.FAILED) {
      setPriceStatus(JobStatus.FAILED);
    }
    else {
      setPriceStatus(JobStatus.COMPLETED);
      // Fetch prices and wait for them
      const latestPrices = await fetchPrices(); 
      runAnalysis(); 
    }
  };

  const fetchPrices = async () => {
    const params = new URLSearchParams({ interval, limit });
    if (startTime) params.append("startTime", startTime);
    if (endTime) params.append("endTime", endTime);

    const res = await fetch(`/api/price-history/${symbol}?${params.toString()}`);
    const data = await res.json();
    setPrices(data.data.prices);
    return data.data.prices;
  };

  const runAnalysis = async () => {
    const res = await fetch("/api/analysis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        symbol,
        interval,
        limit,
        monte_carlo_runs: monteCarlo,
      }),
    });
    const data = await res.json();
    setAnalysisJobId(data.job_id);
    pollAnalysisJob(data.job_id);
  };

  const pollAnalysisJob = async (id) => {
    const res = await fetch(`/api/analysis/${id}`);
    const data = await res.json();

    if ([JobStatus.PENDING, JobStatus.PROCESSING].includes(data.status)) {
      setAnalysisStatus(JobStatus.PROCESSING);
      setTimeout(() => pollAnalysisJob(id), 2000);
    }
    else if (data.status === JobStatus.FAILED) {
      setAnalysisStatus(JobStatus.FAILED);
    }
    else {
      setAnalysisStatus(JobStatus.COMPLETED);
      setResult(data.data);
    }
  };


  return (
    <div className="min-h-screen text-white p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        <h1 className="text-3xl tracking-tight text-white bg-clip-text">
          Trading Analytics
        </h1>

        {/* Inputs */}
        <div className="flex flex-col gap-6 bg-box border border-box-border rounded-3xl p-6">

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input label="Symbol">
              <input
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                placeholder="BTCUSDT"
                className="w-full"
              />
            </Input>

            <Input label="Interval">
              <select value={interval} onChange={(e) => setInterval(e.target.value)} className="w-full">
                {["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"]
                  .map((int) => <option key={int} value={int}>{int}</option>)}
              </select>
            </Input>

            <Input label="Limit">
              <input
                type="number"
                min="1"
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                className="w-full"
              />
            </Input>

            <Input label="Start Time">
              <input
                type="datetime-local"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="w-full"
              />
            </Input>

            <Input label="End Time">
              <input
                type="datetime-local"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                className="w-full"
              />
            </Input>

            <Input label="Monte Carlo Iterations">
              <input
                type="number"
                min="1"
                value={monteCarlo}
                onChange={(e) => setMonteCarlo(Number(e.target.value))}
                className="w-full"
              />
            </Input>
          </div>

          <div className="flex gap-4 border-t border-box-border/50 pt-4">
            <button
              onClick={handleFullAnalysis}
              disabled={[JobStatus.PROCESSING, JobStatus.PENDING].some(status => [priceStatus, analysisStatus].includes(status))}
              className="
                bg-primary hover:brightness-120 disabled:opacity-50 transition-all
                rounded-xl font-bold text-black flex items-center gap-2 py-2.5 px-8
              "
            >
              {/* Animated Loading Circle */}
              {[JobStatus.PROCESSING, JobStatus.PENDING].some(status => [priceStatus, analysisStatus].includes(status)) && (
                <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin" />
              )}
              Run Complete Analysis
            </button>
          </div>

        </div>

        {/* Dynamic Status Display */}
        {[JobStatus.PROCESSING, JobStatus.PROCESSING].some(status => [priceStatus, analysisStatus].includes(status)) && (
          <Box>
            <div className="flex flex-col gap-2">
              {priceStatus === JobStatus.PROCESSING && <StatusMsg msg="Step 1: Downloading Price Data..." />}
              {analysisStatus === JobStatus.PROCESSING && <StatusMsg msg="Step 2: Computing analytics..." />}
            </div>
          </Box>
        )}
        {priceStatus === JobStatus.FAILED && (
          <Box>
            <div className="text-error font-medium">
              ⨉ Price data download job failed.
            </div>
          </Box>
        )}
        {analysisStatus === JobStatus.FAILED && (
          <Box>
            <div className="text-error font-medium">
              ⨉ Analysis task failed.
            </div>
          </Box>
        )}

        {/* Analysis Result Cards */}
        {result && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-8">
            {/* Volatility */}
            <AnalysisCard
              title="Volatility"
              subtitle="Market Risk"
              glowColor={result.volatility < 0.3 ? "bg-green-500" : result.volatility < 0.6 ? "bg-yellow-500" : "bg-red-500"}
              value={`${(result.volatility * 100).toFixed(1)}\u2009%`}
              trend={
                <span className={result.volatility > 0.6 ? "text-red-400" : "text-green-400"}>
                  {result.volatility > 0.6 ? "🞮 High" : "✓ Stable"}
                </span>
              }
              footer={
                <div className="flex flex-col text-sm text-gray-400">
                  <span>
                    Status: <span className="text-white font-semibold">
                      {result.volatility < 0.3 ? "Low Risk" : "Moderate"}
                    </span>
                  </span>
                  <span className="text-xs text-gray-500 mt-1 italic">
                    The price could fluctuate by {(result.volatility * 100).toFixed(1)}&thinsp;% in a&nbsp;year if the trend continues that way.
                  </span>
              </div>
              }
            />

            {/* RSI */}
            <AnalysisCard
              title="Relative Strength"
              subtitle="Momentum"
              glowColor={result.rsi_last > 70 ? "bg-red-500" : result.rsi_last < 30 ? "bg-green-500" : "bg-blue-500"}
              value={result.rsi_last.toFixed(1)}
              footer={
                <div className="space-y-3">
                  <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500" style={{ width: `${result.rsi_last}%` }} />
                  </div>
                  <span className="text-sm text-gray-400">
                    Condition: <span className="text-white font-semibold">{result.rsi_last > 70 ? "Overbought" : "Neutral"}</span>
                  </span>
                </div>
              }
            />

            {/* Last Price */}
            <AnalysisCard
              title="Last Price"
              subtitle="Info"
              glowColor="bg-primary"
              value={`$${prices[prices.length - 1]?.close?.toLocaleString() || "---"}`}
              footer={
                <p className="text-xs text-gray-500 italic">
                  { Date(prices[prices.length - 1].timestamp).toLocaleString("en-GB") }
                </p>
              }
            />

            {/* Monte Carlo */}
            <AnalysisCard
              title="Expected Mean"
              subtitle="Projection"
              glowColor="bg-primary"
              value={`$${result.monte_carlo_mean.toLocaleString(undefined, {maximumFractionDigits: 2})}`}
              trend={
                prices.length > 0 && (
                  <span className={`text-sm font-bold rounded-md bg-opacity-10 
                    ${result.monte_carlo_mean > prices[prices.length - 1].close 
                      ? "text-green-400" 
                      : "text-red-400"}`}>
                    {result.monte_carlo_mean > prices[prices.length - 1].close ? "▲ Bullish Bias" : "▼ Bearish Bias"}
                  </span>
                )
              }
              footer={
                <p className="text-xs text-gray-500 italic leading-tight">
                  The average simulated price after {monteCarlo} periods if future behaves like the past.
                </p>
              }
            />
          </div>
        )}

        {/* Price History Chart */}
        {prices.length > 0 && (
          <div className="overflow-x-auto bg-box border border-box-border rounded-3xl p-6">
            <PriceChart prices={prices} symbol={symbol} />
          </div>
        )}
      </div>
    </div>
  );
}

function AnalysisCard({ title, subtitle, value, trend, footer, glowColor = "bg-primary" }) {
  return (
    <div className="bg-box border border-box-border p-5 rounded-2xl relative overflow-hidden shadow-lg flex flex-col justify-between min-h-50">
    {/* Blur Glow */}
    <div className={`absolute -top-10 -right-10 w-35 h-35 rounded-full blur-3xl opacity-30 ${glowColor}`} />
    
    <div className="relative z-10">
      <div className="flex flex-col gap-1">
        <span className="text-gray-400 text-xs font-medium uppercase tracking-wider">{subtitle}</span>
        <h3 className="text-xl font-bold text-white">{title}</h3>
      </div>

      {/* Main Value Area */}
      <div className="mt-4 flex flex-col gap-1">
        <span className="text-3xl font-mono font-bold text-white leading-none">
          {value}
        </span>
        {/* Appendix Indicator */}
        {trend && (
          <div className="mt-1">
            {trend}
          </div>
        )}
      </div>
    </div>
    
    {/* Bottom Information */}
    <div className="mt-4 pt-4 border-t border-box-border/50 relative z-10">
      {footer}
    </div>
  </div>
  )
}

function Input({ label, children }) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm text-gray-400">{label}</label>
      {React.cloneElement(children, {
        className: `
          w-full px-4 py-2.5 rounded-lg
          bg-bar2 border border-bar-border
          text-white transition-all outline-none input-placeholder
          focus:border-primary
        `
      })}
    </div>
  );
}

function StatusMsg({ msg }) {
  return (
    <div className="flex items-center gap-3 text-secondary animate-pulse text-sm font-medium">
      {msg}
    </div>
  );
}

function Box({ children, className = "" }) {
  return (
    <div className={`flex flex-col gap-6 bg-box border border-box-border rounded-3xl p-6 ${className}`}>
      {children}
    </div>
  );
}
