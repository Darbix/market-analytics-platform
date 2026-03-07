import React, { useEffect, useState } from "react";

const COINS = [
  { symbol: "BTCUSDT", color: "text-orange-400" },
  { symbol: "ETHUSDT", color: "text-blue-400" },
  { symbol: "BNBUSDT", color: "text-yellow-400" },
  { symbol: "SOLUSDT", color: "text-purple-400" },
];

export default function Dashboard() {
  const [market, setMarket] = useState({});
  const [loading, setLoading] = useState(true);

  const fetchPrices = async () => {
    try {
      const symbols = COINS.map((c) => c.symbol);

      const res = await fetch(
        `https://api.binance.com/api/v3/ticker/24hr?symbols=${JSON.stringify(symbols)}`
      );

      const data = await res.json();

      const mapped = {};
      data.forEach((coin) => {
        mapped[coin.symbol] = {
          price: Number(coin.lastPrice),
          change: Number(coin.priceChangePercent),
        };
      });

      setMarket(mapped);
      setLoading(false);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchPrices();
    const interval = setInterval(fetchPrices, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen text-white p-4">
      <div className="max-w-6xl mx-auto space-y-6">

        <h1 className="text-3xl tracking-tight">Crypto Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {COINS.map((coin) => (
            <PriceCard
              key={coin.symbol}
              coin={coin}
              data={market[coin.symbol]}
              loading={loading}
            />
          ))}
        </div>

      </div>
    </div>
  );
}

function PriceCard({ coin, data, loading }) {
  const base = coin.symbol.replace("USDT", "");

  const change = data?.change ?? 0;
  const positive = change >= 0;

  return (
    <div className="bg-box border border-box-border p-5 rounded-2xl relative overflow-hidden shadow-lg flex flex-col justify-between min-h-40">

      <div className="absolute -top-10 -right-10 w-35 h-35 rounded-full blur-3xl opacity-30 bg-primary" />

      <div className="relative z-10">

        <div className="flex flex-col gap-1">
          <span className="text-gray-400 text-xs uppercase tracking-wider">
            Binance Price
          </span>

          <h3 className={`text-xl font-bold ${coin.color}`}>
            {base}
          </h3>
        </div>

        <div className="mt-4 flex flex-col gap-1">

          <span className={`text-3xl font-mono font-bold font-white`}>
            {loading ? "$---" : `$${data?.price.toLocaleString()}`}
          </span>

          {!loading && (
            <span
              className={`text-sm font-semibold ${
                positive ? "text-green-400" : "text-red-400"
              }`}
            >
              {positive ? "▲" : "▼"} {Math.abs(change).toFixed(2)}%
            </span>
          )}

          {!loading && (
            <span className="text-xs text-gray-400 mt-1 italic">
              24h Price Change
            </span>
          )}
        </div>

      </div>

      <div className="mt-4 pt-3 border-t border-box-border/50 text-xs text-gray-500 relative z-10">
        Symbol: {coin.symbol}
      </div>

    </div>
  );
}
