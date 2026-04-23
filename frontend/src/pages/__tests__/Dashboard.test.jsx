import React from "react";
import { render, screen } from "@testing-library/react";
import Dashboard, { COINS } from "../Dashboard";
import {
  mockFetchSuccess,
  mockFetchLoading,
  mockFetchError,
} from "../../test_utils/mockFetch";


afterAll(() => {
  jest.restoreAllMocks();
});

beforeEach(() => {
  global.fetch = jest.fn();
});

afterEach(() => {
  jest.clearAllMocks();
});

const mockData = [
  { symbol: "BTCUSDT", lastPrice: "5000", priceChangePercent: "2" },
  { symbol: "ETHUSDT", lastPrice: "4000", priceChangePercent: "-1" },
  { symbol: "BNBUSDT", lastPrice: "6000", priceChangePercent: "3" },
  { symbol: "SOLUSDT", lastPrice: "1000", priceChangePercent: "1" },
];


describe("Dashboard Page", () => {
  test("shows price placeholders on initial render", () => {
    mockFetchLoading();

    render(<Dashboard />);

    const placeholders = screen.getAllByText("$---");
    expect(placeholders).toHaveLength(COINS.length);

    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  test("does not show a price change symbol while loading", () => {
    mockFetchLoading();

    render(<Dashboard />);

    expect(screen.queryByText(/▲/)).not.toBeInTheDocument();
    expect(screen.queryByText(/▼/)).not.toBeInTheDocument();
  });

  test("renders positive and negative price change indicators", async () => {
    mockFetchSuccess(mockData);

    render(<Dashboard />);

    expect(await screen.findByText(/▲ 2.00%/)).toBeInTheDocument();
    expect(await screen.findByText(/▼ 1.00%/)).toBeInTheDocument();
  });

  test("renders coin base symbols", async () => {
    mockFetchSuccess(mockData);

    render(<Dashboard />);

    expect(await screen.findByText("BTC")).toBeInTheDocument();
    expect(await screen.findByText("ETH")).toBeInTheDocument();
    expect(await screen.findByText("BNB")).toBeInTheDocument();
    expect(await screen.findByText("SOL")).toBeInTheDocument();
  });

  test("renders fetched prices after loading with no error", async () => {
    mockFetchSuccess(mockData);

    render(<Dashboard />);

    expect(await screen.findByText("$5,000")).toBeInTheDocument();
    expect(await screen.findByText("$4,000")).toBeInTheDocument();
    expect(await screen.findByText("$6,000")).toBeInTheDocument();
    expect(await screen.findByText("$1,000")).toBeInTheDocument();

    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  test("calls fetch with a correct endpoint", async () => {
    mockFetchLoading();
    
    render(<Dashboard />);

    const expectedSymbols = JSON.stringify(COINS.map(c => c.symbol));

    expect(fetch).toHaveBeenCalledWith(
      `https://api.binance.com/api/v3/ticker/24hr?symbols=${expectedSymbols}`
    );
  });

  test("calls fetch repeatedly on interval", () => {
    jest.useFakeTimers();

    mockFetchLoading();
    render(<Dashboard />);

    expect(fetch).toHaveBeenCalledTimes(1);

    // Fast-forward 10 seconds
    jest.advanceTimersByTime(10000);

    expect(fetch).toHaveBeenCalledTimes(2);
  });

  test("shows error alert when fetch fails", async () => {
    mockFetchError();

    render(<Dashboard />);

    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });

  test("cleans up interval on unmount", () => {
    jest.useFakeTimers();
    const clearSpy = jest.spyOn(global, "clearInterval");

    const { unmount } = render(<Dashboard />);
    unmount();

    expect(clearSpy).toHaveBeenCalled();
  });

  test("handles empty API response gracefully", async () => {
    mockFetchSuccess([]);

    render(<Dashboard />);

    expect(await screen.findAllByText("$---")).toHaveLength(COINS.length);
  });
});
