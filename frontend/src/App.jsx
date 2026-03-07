import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom";
import React, { useState } from "react";
import { BsPiggyBank, BsChatDots } from "react-icons/bs";
import { HiOutlineMenu } from "react-icons/hi";

import Dashboard from "./pages/Dashboard";
import Analytics from "./pages/Analytics";


function App() {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <Router>
      <div className="flex flex-col min-h-screen bg-background text-white">

        {/* Top Bar */}
        <header className="h-16 flex items-center gap-4 px-4 bg-bar1 shadow-lg sticky top-0 z-50">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="p-2 rounded-lg hover:bg-white/10 transition"
          >
            <HiOutlineMenu size={22} />
          </button>

          <div className="md:text-xl text-lg font-semibold text-primary flex items-center gap-2">
            <BsPiggyBank />
            <span>Market Analytics Platform</span>
          </div>
        </header>

        <div className="flex flex-1 flex-col md:flex-row">
          {/* Sidebar */}
          <aside
            className={`
              bg-bar2 overflow-hidden border-0 border-solid duration-300 ease-in-out
              transition-all
              ${isOpen 
                ? "max-h-64 opacity-100 border-b border-bar-border"
                : "max-h-0 opacity-0 border-b border-transparent"}
                
              md:sticky md:top-16 md:h-[calc(100vh-64px)] 
              md:max-h-none md:self-stretch md:border-b-0 
              md:transition-[width,opacity]
              ${isOpen 
                ? "md:w-60 md:opacity-100 md:border-r border-bar-border" 
                : "md:w-0 md:opacity-0 md:border-r md:border-transparent"}
            `}
          >
            <div className="min-w-60 md:w-60">
              <nav className="flex flex-col gap-2 pt-2 pb-1 text-lg">
                <NavItem to="/">Dashboard</NavItem>
                <NavItem to="/analytics">Analytics</NavItem>
              </nav>
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 sm:p-6 bg-background overflow-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </main>
        </div>

        {/* Floating Chat Bot Icon */}
        <button className="fixed bottom-6 right-6 z-50 group flex items-center justify-center w-14 h-14 
                         bg-primary text-black rounded-full shadow-lg animate-bounce [animation-duration:3s]
                           hover:scale-110 active:scale-95 transition-all">
          <BsChatDots size={24} />
          <span className="absolute right-16 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 
                           group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
            Need help?
          </span>
        </button>
      </div>
    </Router>
  );
}

function NavItem({ to, children }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `px-5 py-2 flex items-center relative transition-colors hover:bg-white/5 ${
          isActive? "text-primary": "text-gray-400 hover:text-white"
        }`
      }
    >
      {({ isActive }) => (
        <>
          {children}
          {/* Vertical Line Active Indicator */}
          {isActive && (
            <div className="absolute right-0 top-1/2 -translate-y-1/2 h-6/7 w-0.75 bg-primary rounded-l-full" />
          )}
        </>
      )}
    </NavLink>
  );
}

export default App;
