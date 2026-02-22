import React, { useState } from "react";
import { JobStatus } from "../constants/jobStatus";


export default function Analysis() {
  const [symbol, setSymbol] = useState("");
  const [interval, setInterval] = useState("1m");
  const [limit, setLimit] = useState(10);
  const [monteCarlo, setMonteCarlo] = useState(1000);
  const [result, setResult] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);

  const runAnalysis = async () => {
    const res = await fetch("/api/analysis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol, interval, limit, monte_carlo_runs: monteCarlo }),
    });
    const data = await res.json();
    setJobId(data.job_id);
    pollResult(data.job_id);
  };

  const pollResult = async (id) => {
    const res = await fetch(`/api/analysis/${id}`);
    const data = await res.json();

    console.log(data)

    if (data.status === JobStatus.PENDING ||
        data.status === JobStatus.PROCESSING) {
      setStatus(JobStatus.PROCESSING);
      setTimeout(() => pollResult(id), 2000);
    }
    else if (data.status === JobStatus.FAILED) {
      setStatus(JobStatus.FAILED);
    }
    else {
      setStatus(JobStatus.COMPLETED);
      setResult(data.data);
    }
  };    


  return (
    <div>
      <h1 className="text-xl font-bold mb-4">Analysis</h1>
      <div className="flex flex-col gap-2 mb-4">
        Symbol: <input value={symbol} onChange={(e) => setSymbol(e.target.value)} placeholder="BTCUSDT" className="border p-2 rounded" />
        Interval: <select value={interval} onChange={(e) => setInterval(e.target.value)} className="border p-2 rounded">
          <option value="1m">1m</option>
          <option value="3m">3m</option>
          <option value="5m">5m</option>
          <option value="15m">15m</option>
          <option value="30m">30m</option>
          <option value="1h">1h</option>
          <option value="2h">2h</option>
          <option value="4h">4h</option>
          <option value="6h">6h</option>
          <option value="8h">8h</option>
          <option value="12h">12h</option>
          <option value="1d">1d</option>
          <option value="3d">3d</option>
          <option value="1w">1w</option>
          <option value="1M">1M</option>
        </select>
        {/* Limit: <input type="number" value={limit} onChange={(e) => setLimit(Number(e.target.value))} placeholder="Limit" className="border p-2 rounded"/> */}
        Limit: <input 
          type="number" 
          min="10"
          value={limit} 
          onChange={(e) => {
            const val = Number(e.target.value);
            if (val >= 10) setLimit(val);
          }} 
          placeholder="Limit" 
          className="border p-2 rounded" 
        />
        
        Monte Carlo Iterations: <input 
          type="number" 
          min="1"
          value={monteCarlo} 
          onChange={(e) => {
            const val = Number(e.target.value);
            if (val >= 1) setMonteCarlo(Number(e.target.value));
          }} 
          placeholder="Monte Carlo runs" 
          className="border p-2 rounded" 
        />
        
        <button onClick={runAnalysis} className="bg-blue-600 text-white px-4 py-2 rounded">Run Analysis</button>
      </div>

      {status === JobStatus.FAILED && (
        <div className="mt-4 p-4 border rounded bg-red-100 text-red-700">
            <h2 className="font-bold">Job {jobId} failed!</h2>
        </div>
      )}

      {status === JobStatus.PROCESSING && (
        <div className="mt-4">
            Processing job {jobId}...
        </div>
      )}

      {result && (
        <div className="mt-4 p-4 border rounded bg-white">
          <h2 className="font-bold mb-2">Results</h2>
          <p>Volatility: {result.volatility}</p>
          <p>RSI Last: {result.rsi_last}</p>
          <p>Monte Carlo Mean: {result.monte_carlo_mean}</p>
        </div>
      )}
    </div>
  );
}
