import React from "react";
import { Line } from "react-chartjs-2";

export default function PriceChart({ prices, symbol }) {
  const css = getComputedStyle(document.documentElement);
  const color_up = css.getPropertyValue("--color-success").trim();
  const color_down = css.getPropertyValue("--color-failure").trim();
  const color_primary = css.getPropertyValue("--color-primary").trim();

  const chartData = {
    labels: prices.map((p) =>
      // Parsed timestamps as values for x axis
      new Date(p.timestamp).toLocaleString("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      })
    ),
    datasets: [
      {
        // Close prices as values for y axis
        label: `${symbol} Close Price`,
        data: prices.map((p) => p.close),
        tension: 0.0,
        pointRadius: 1.8,
        pointHoverRadius: 5,
        backgroundColor: "rgba(255,255,255,0.1)",
        fill: false,
        segment: {
          borderColor: (ctx) => {
            const { p0, p1 } = ctx;
            return p1.parsed.y > p0.parsed.y
              ? color_up
              : color_down;
          },
        },

        pointBackgroundColor: (ctx) => {
          const i = ctx.dataIndex;
          if (i === 0)
            return color_up;
          const prev = ctx.dataset.data[i - 1];
          const curr = ctx.dataset.data[i];
          return curr > prev ? color_up : color_down;
        },
      },
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        labels: { color: "#e5e7eb" },
      },
      tooltip: {
        mode: "nearest",
        intersect: true,
        backgroundColor: "#151515",
        titleColor: color_primary,
        bodyColor: "#808080",
        padding: 10,
      },
    },
    interaction: {
      mode: "nearest",
      intersect: true,
    },
    scales: {
      x: {
        ticks: { color: "#999", maxTicksLimit: 40},
        grid: { color: "rgba(255,255,255,0.05)" },
      },
      y: {
        min: 0,
        ticks: { color: "#999" },
        grid: { color: "rgba(255,255,255,0.05)" },
      },
    },
  };

  return <Line data={chartData} options={chartOptions} />;
}
