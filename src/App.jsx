import { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import HomePage from "./pages/HomePage";
import ScanPage from "./pages/ScanPage";
import DrugCheckerPage from "./pages/DrugCheckerPage";
import SchedulePage from "./pages/SchedulePage";
import VaultPage from "./pages/VaultPage";
import MultiPrescriptionPage from "./pages/MultiPrescriptionPage";

// Simple client-side router based on window.location.pathname
function getPage(path) {
  if (path === "/scan") return "scan";
  if (path === "/drug-checker") return "drug-checker";
  if (path === "/schedule") return "schedule";
  if (path === "/vault") return "vault";
  if (path === "/multi-prescription") return "multi-prescription";
  return "home";
}

export default function App() {
  const [page, setPage] = useState(() => getPage(window.location.pathname));
  // sidebar removed; content spans full width

  // Intercept link clicks for SPA navigation
  useEffect(() => {
    const handleClick = (e) => {
      const anchor = e.target.closest("a[href]");
      if (!anchor) return;
      const href = anchor.getAttribute("href");
      if (!href || href.startsWith("http") || href.startsWith("#")) return;
      e.preventDefault();
      window.history.pushState({}, "", href);
      setPage(getPage(href));
      window.scrollTo(0, 0);
    };

    document.addEventListener("click", handleClick);
    return () => document.removeEventListener("click", handleClick);
  }, []);

  // Browser back/forward
  useEffect(() => {
    const handlePop = () => setPage(getPage(window.location.pathname));
    window.addEventListener("popstate", handlePop);
    return () => window.removeEventListener("popstate", handlePop);
  }, []);

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        html, body {
          background: #03030a;
          color: #fff;
          font-family: 'Outfit', sans-serif;
          -webkit-font-smoothing: antialiased;
          scroll-behavior: smooth;
        }

        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: #03030a; }
        ::-webkit-scrollbar-thumb { background: rgba(0,255,180,0.2); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(0,255,180,0.4); }

        .app-layout {
          display: flex;
          flex-direction: column;
          min-height: 100vh;
        }

        .app-main {
          flex: 1;
          display: flex;
        }

        .app-content {
          flex: 1;
          transition: margin-left 0.3s ease;
          margin-left: 0;
        }
      `}</style>

      <div className="app-layout">
        <Navbar />

        <div className="app-main">
  
          <div className="app-content">
            {page === "home" && <HomePage />}
            {page === "scan" && <ScanPage />}
            {page === "drug-checker" && <DrugCheckerPage />}
            {page === "schedule" && <SchedulePage />}
            {page === "vault" && <VaultPage />}
            {page === "multi-prescription" && <MultiPrescriptionPage />}
          </div>
        </div>

        <div style={{ marginLeft: 0, transition: "margin-left 0.3s ease" }}>
          <Footer />
        </div>
      </div>
    </>
  );
}
