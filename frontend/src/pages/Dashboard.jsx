import React, { useEffect, useState } from "react";

export default function Dashboard() {
  const [symbol, setSymbol] = useState("");
  const [interval, setInterval] = useState("1m");
  const [jobs, setJobs] = useState([]);

  const addSymbol = async () => {
    const res = await fetch("/track", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol, interval }),
    });
    const data = await res.json();
    alert(`Job created with ID: ${data.job_id}`);
    setSymbol("");
  };

  useEffect(() => {
    // Optionally: fetch tracked symbols from backend if you have an endpoint
  }, []);

  return (
    <div>
      <h1 className="text-xl font-bold mb-4">Dashboard</h1>
      <div className="flex gap-2 mb-4">
        <input
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          placeholder="Symbol (e.g., BTCUSDT)"
          className="border p-2 rounded"
        />
        <select
          value={interval}
          onChange={(e) => setInterval(e.target.value)}
          className="border p-2 rounded"
        >
          <option value="1m">1m</option>
          <option value="5m">5m</option>
          <option value="15m">15m</option>
        </select>
        <button
          onClick={addSymbol}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Track
        </button>
      </div>
    </div>
  );
}
