import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Analysis from "./pages/Analysis";
// import PriceHistory from "./pages/PriceHistory";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <nav className="bg-blue-600 text-white p-4 flex space-x-4">
          <Link to="/">Dashboard</Link>
          <Link to="/analysis">Analysis</Link>
          <Link to="/price-history">Price History</Link>
        </nav>
        <div className="p-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analysis" element={<Analysis />} />
            {/* <Route path="/price-history" element={<PriceHistory />} /> */}
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;