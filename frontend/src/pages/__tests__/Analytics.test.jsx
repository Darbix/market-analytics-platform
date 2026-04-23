
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Analytics from "../Analytics";
import { JobStatus } from "../../constants/jobStatus";


beforeEach(() => {
  jest.useFakeTimers();
  global.fetch = jest.fn();
});

afterEach(() => {
  jest.useRealTimers();
  jest.resetAllMocks();
});


describe('Analytics component', () => {
  test("runs full analysis and displays results", async () => {
    fetch
      // 1. Request price download
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ job_id: "price123" }),
      })
      // 2. Poll price job - immediately completed
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: JobStatus.COMPLETED }),
      })
      // 3. Fetch prices
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: {
            prices: [
              { timestamp: 1680000000000, close: 50000 },
              { timestamp: 1680086400000, close: 51000 },
            ],
          },
        }),
      })
      // 4. Run analysis
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ job_id: "analysis123" }),
      })
      // 5. Poll analysis job - immediately completed
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: JobStatus.COMPLETED,
          data: {
            volatility: 0.25,
            rsi_last: 65,
            monte_carlo_mean: 52000,
          },
        }),
      });

    render(<Analytics />);

    // Trigger a full analysis
    const button = screen.getByRole("button", { name: /run complete analysis/i });
    fireEvent.click(button);

    // Final UI assertions
    expect(await screen.findByText(/volatility/i)).toBeInTheDocument();
    expect(await screen.findByText(/relative strength/i)).toBeInTheDocument();
    expect(await screen.findByText(/expected mean/i)).toBeInTheDocument();

    // Monte Carlo mean
    expect(await screen.findByText("$52,000")).toBeInTheDocument();

    // Last price (from fetched prices)
    expect(await screen.findByText("$51,000")).toBeInTheDocument();

    // Loading state disappears
    expect(button).not.toBeDisabled();
  });

  test("shows processing state and disables button", async () => {
    // Mock fetches to simulate processing state
    fetch
      // Request price download
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ job_id: "price123" }),
      })
      // Poll price job - still processing
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: JobStatus.PROCESSING }),
      });

    render(<Analytics />);

    const button = screen.getByRole("button", { name: /run complete analysis/i });
    fireEvent.click(button);

    // The button is disabled during processing
    expect(button).toBeDisabled();

    // The "Step 1: Downloading Price Data..." message should appear
    expect(await screen.findByText("Step 1: Downloading Price Data...")).toBeInTheDocument();

    // Step 2 should not appear yet
    expect(
      screen.queryByText("Step 2: Computing analytics...")
    ).not.toBeInTheDocument();
  });

  test("shows step 2 when analysis is processing", async () => {
    fetch
      // 1. Request price download
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ job_id: "price123" }),
      })
      // 2. Poll price job - immediately completed
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: JobStatus.COMPLETED }),
      })
      // 3. Fetch prices
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: {
            prices: [{ timestamp: 1, close: 50000 }],
          },
        }),
      })
      // 4. Run analysis
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ job_id: "analysis123" }),
      })
      // 5. Poll analysis job - still processing
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: JobStatus.PROCESSING }),
      });

    render(<Analytics />);

    const button = screen.getByRole("button", { name: /run complete analysis/i });
    fireEvent.click(button);

    expect(
      await screen.findByText("Step 2: Computing analytics...")
    ).toBeInTheDocument();
  });

  test("handles analysis failure", async () => {
    fetch
      // 1. Request price download
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ job_id: "price123" }),
      })
      // 2. Poll price job - immediately completed
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: JobStatus.COMPLETED }),
      })
      // 3. Fetch prices
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: {
            prices: [{ timestamp: 1, close: 50000 }],
          },
        }),
      })
      // 4. Run analysis
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ job_id: "analysis123" }),
      })
      // 5. Poll analysis job - failed
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: JobStatus.FAILED }),
      });

    render(<Analytics />);

    fireEvent.click(
      screen.getByRole("button", { name: /run complete analysis/i })
    );

    expect(
      await screen.findByText(/analysis task failed/i)
    ).toBeInTheDocument();
  });
});
