import { useState, useRef, useEffect } from "react";
import { JobStatus } from "../constants/jobStatus";

export function useAnalytics() {
    // Shared inputs
    const [symbol, setSymbol] = useState("BTCUSDT");
    const [intervalframe, setIntervalframe] = useState("1d");
    const [limit, setLimit] = useState(365);
    const [error, setError] = useState(null);
  
    // Price history state
    const [startTime, setStartTime] = useState("");
    const [endTime, setEndTime] = useState("");
    const [prices, setPrices] = useState([]);
    const [priceStatus, setPriceStatus] = useState(null);
  
    // Analysis state
    const [monteCarlo, setMonteCarlo] = useState(1000);
    const [analysisStatus, setAnalysisStatus] = useState(null);
    const [result, setResult] = useState(null);
  
    
    // Variables to stop potention polling loops  
    const cancelPricePollRef = useRef(null);
    const cancelAnalysisPollRef = useRef(null);
    
    useEffect(() => {
      return () => {
        cancelPricePollRef.current?.();
        cancelAnalysisPollRef.current?.();
      };
    }, []);
  
    const handleFullAnalysis = async () => {
      // Clear old results
      setResult(null);
      setPrices([]);
      setError(null);
      setPriceStatus(null);
      setAnalysisStatus(null);
  
      cancelPricePollRef.current?.();
      cancelAnalysisPollRef.current?.();
      
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
            interval: intervalframe,
            limit,
            startTime: startTime || null,
            endTime: endTime || null
          }),
          signal: controller.signal,
        });
        clearTimeout(timeoutId);
        if (!res.ok)
          throw new Error("Failed to request price download.");
        const data = await res.json();

        cancelPricePollRef.current?.();
        cancelPricePollRef.current = pollPriceJob(data.job_id);
      }
      catch (error) {
        setError(`Failed to fetch price data from the server: ${error}`)
        setPriceStatus(JobStatus.FAILED);
        setAnalysisStatus(JobStatus.FAILED);
      }
    };
  
    const createPoller = ({
      urlBuilder,
      onPending,
      onSuccess,
      onFailure,
      interval = 2000,
    }) => {
      return (id) => {
        let cancelled = false;
  
        const run = async () => {
          try {
            const res = await fetch(urlBuilder(id));
            if (!res.ok)
              throw new Error(`The server returned an error: ${res.status}`);
            const data = await res.json();
  
            if (cancelled)
              return;
  
            if ([JobStatus.PENDING, JobStatus.PROCESSING].includes(data.status)) {
              onPending?.(data);
              setTimeout(() => !cancelled && run(), interval);
            }
            else if (data.status === JobStatus.FAILED) {
              onFailure?.(data);
            }
            else {
              onSuccess?.(data);
            }
          }
          catch (error) {
            onFailure?.(error);
          }
        };
  
        run();
  
        return () => {
          cancelled = true;
        };
      };
    };
  
    const pollPriceJob = createPoller({
      urlBuilder: (id) => `/api/jobs/${id}`,
  
      onPending: () => {
        setPriceStatus(JobStatus.PROCESSING);
      },
  
      onFailure: (error) => {
        setError(`Failed to fetch price data ${error}`);
        setPriceStatus(JobStatus.FAILED);
      },
  
      onSuccess: async () => {
        setPriceStatus(JobStatus.COMPLETED);
        // The job exists so we can fetch the prices
        await fetchPrices();
        runAnalysis();
      },
    });
  
    const fetchPrices = async () => {
      const params = new URLSearchParams({
        interval: intervalframe,
        limit
      });
      if (startTime)
        params.append("startTime", startTime);
      if (endTime)
        params.append("endTime", endTime);
  
      let prices = null;
  
      try {
        const res = await fetch(`/api/price-history/${symbol}?${params.toString()}`);
        if (!res.ok)
            throw new Error(`The server returned an error: ${res.status}`);
        const data = await res.json();
        prices = data.data.prices;
        setPrices(data.data.prices);
      }
      catch (error) {
        setError(`Failed to fetch prices: ${error}`)
        setPriceStatus(JobStatus.FAILED);
      }
      return prices;
    };
  
    const runAnalysis = async () => {
      try {
        const res = await fetch("/api/analysis", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            symbol,
            interval: intervalframe,
            limit,
            monte_carlo_runs: monteCarlo,
            startTime: startTime || null,
            endTime: endTime || null
          }),
        });
        if (!res.ok)
          throw new Error(`The server returned an error: ${res.status}`);
        const data = await res.json();

        cancelAnalysisPollRef.current?.();
        cancelAnalysisPollRef.current = pollAnalysisJob(data.job_id);
      }
      catch (error) {
        setError(`Failed to start analysis: ${error}`);
        setAnalysisStatus(JobStatus.FAILED);
      }
    };
  
    const pollAnalysisJob = createPoller({
      urlBuilder: (id) => `/api/analysis/${id}`,
  
      onPending: () => {
        setAnalysisStatus(JobStatus.PROCESSING);
      },
  
      onFailure: (error) => {
        setError(`Failed to fetch analysis data: ${error}`)
        setAnalysisStatus(JobStatus.FAILED);
      },
  
      onSuccess: (data) => {
        setAnalysisStatus(JobStatus.COMPLETED);
        setResult(data.data);
      },
    });

  return {
    symbol, intervalframe, limit, error, startTime, endTime,
    prices, priceStatus, monteCarlo, analysisStatus, result,

    setSymbol, setIntervalframe, setLimit, setStartTime,
    setEndTime, setMonteCarlo, handleFullAnalysis
  };
}
