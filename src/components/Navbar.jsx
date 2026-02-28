import { useState, useEffect } from "react";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 30);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const navLinks = [
    { label: "Home", href: "/" },
    { label: "Scan Prescription", href: "/scan" },
    { label: "Drug Checker", href: "/drug-checker" },
    { label: "Schedule", href: "/schedule" },
    { label: "Vault", href: "/vault" },
    { label: "Multi-Rx", href: "/multi-prescription" },
  ];

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;900&family=Outfit:wght@300;400;500;600&display=swap');

        .navbar {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          z-index: 1000;
          padding: 0 2rem;
          height: 70px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          transition: all 0.4s ease;
          font-family: 'Outfit', sans-serif;
        }

        .navbar.scrolled {
          background: rgba(5, 5, 10, 0.92);
          backdrop-filter: blur(20px);
          border-bottom: 1px solid rgba(0,255,180,0.08);
          box-shadow: 0 4px 40px rgba(0,0,0,0.6);
        }

        .navbar.top {
          background: transparent;
        }

        .logo-wrap {
          display: flex;
          align-items: center;
          gap: 10px;
          text-decoration: none;
          cursor: pointer;
        }

        .logo-icon {
          width: 36px;
          height: 36px;
          position: relative;
        }

        .logo-icon svg {
          width: 100%;
          height: 100%;
          filter: drop-shadow(0 0 8px rgba(0,255,180,0.7));
        }

        .logo-text {
          font-family: 'Cinzel', serif;
          font-size: 1.25rem;
          font-weight: 900;
          background: linear-gradient(90deg, #00ffb4, #00c8ff, #a78bfa);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          letter-spacing: 0.05em;
        }

        .nav-links {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          list-style: none;
          margin: 0;
          padding: 0;
        }

        .nav-links a {
          font-size: 0.82rem;
          font-weight: 500;
          letter-spacing: 0.06em;
          text-transform: uppercase;
          color: rgba(255,255,255,0.55);
          text-decoration: none;
          padding: 6px 12px;
          border-radius: 6px;
          transition: all 0.25s ease;
          position: relative;
        }

        .nav-links a:hover {
          color: #00ffb4;
          background: rgba(0,255,180,0.06);
        }

        .nav-links a::after {
          content: '';
          position: absolute;
          bottom: 2px;
          left: 50%;
          transform: translateX(-50%);
          width: 0;
          height: 1px;
          background: linear-gradient(90deg, #00ffb4, #00c8ff);
          transition: width 0.25s ease;
        }

        .nav-links a:hover::after {
          width: 60%;
        }

        .nav-cta {
          background: linear-gradient(135deg, #00ffb4 0%, #00c8ff 100%);
          color: #000 !important;
          font-weight: 700 !important;
          border-radius: 8px !important;
          padding: 7px 18px !important;
          -webkit-text-fill-color: #000 !important;
          transition: all 0.25s ease !important;
          box-shadow: 0 0 20px rgba(0,255,180,0.25);
        }

        .nav-cta:hover {
          box-shadow: 0 0 30px rgba(0,255,180,0.5) !important;
          transform: translateY(-1px);
        }

        .nav-cta::after {
          display: none !important;
        }

        .hamburger {
          display: none;
          flex-direction: column;
          gap: 5px;
          cursor: pointer;
          padding: 6px;
        }

        .hamburger span {
          width: 22px;
          height: 2px;
          background: #00ffb4;
          border-radius: 2px;
          transition: all 0.3s;
        }

        .mobile-menu {
          display: none;
          position: fixed;
          top: 70px;
          left: 0;
          right: 0;
          background: rgba(5,5,10,0.97);
          backdrop-filter: blur(20px);
          border-bottom: 1px solid rgba(0,255,180,0.1);
          padding: 1rem 2rem 2rem;
          z-index: 999;
          flex-direction: column;
          gap: 0.5rem;
        }

        .mobile-menu.open {
          display: flex;
        }

        .mobile-menu a {
          color: rgba(255,255,255,0.7);
          text-decoration: none;
          font-size: 0.95rem;
          font-weight: 500;
          padding: 10px 0;
          border-bottom: 1px solid rgba(255,255,255,0.05);
          font-family: 'Outfit', sans-serif;
          letter-spacing: 0.04em;
        }

        @media (max-width: 900px) {
          .nav-links { display: none; }
          .hamburger { display: flex; }
        }
      `}</style>

      <nav className={`navbar ${scrolled ? "scrolled" : "top"}`}>
        <a className="logo-wrap" href="/">
          <div className="logo-icon">
            <svg
              viewBox="0 0 36 36"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle
                cx="18"
                cy="18"
                r="17"
                stroke="url(#ng)"
                strokeWidth="1.5"
                fill="none"
              />
              <path
                d="M18 8v20M8 18h20"
                stroke="url(#ng2)"
                strokeWidth="2.5"
                strokeLinecap="round"
              />
              <circle cx="18" cy="18" r="4" fill="url(#ng3)" />
              <defs>
                <linearGradient id="ng" x1="0" y1="0" x2="36" y2="36">
                  <stop stopColor="#00ffb4" />
                  <stop offset="1" stopColor="#00c8ff" />
                </linearGradient>
                <linearGradient id="ng2" x1="0" y1="0" x2="36" y2="36">
                  <stop stopColor="#00ffb4" />
                  <stop offset="1" stopColor="#a78bfa" />
                </linearGradient>
                <radialGradient id="ng3" cx="50%" cy="50%" r="50%">
                  <stop stopColor="#00ffb4" />
                  <stop offset="1" stopColor="#00c8ff" />
                </radialGradient>
              </defs>
            </svg>
          </div>
          <span className="logo-text">Aarogya Setu</span>
        </a>

        <ul className="nav-links">
          {navLinks.map((l) => (
            <li key={l.href}>
              <a
                href={l.href}
                className={l.label === "Scan Prescription" ? "nav-cta" : ""}
              >
                {l.label}
              </a>
            </li>
          ))}
        </ul>

        <div className="hamburger" onClick={() => setMenuOpen(!menuOpen)}>
          <span />
          <span />
          <span />
        </div>
      </nav>

      <div className={`mobile-menu ${menuOpen ? "open" : ""}`}>
        {navLinks.map((l) => (
          <a key={l.href} href={l.href} onClick={() => setMenuOpen(false)}>
            {l.label}
          </a>
        ))}
      </div>
    </>
  );
}
