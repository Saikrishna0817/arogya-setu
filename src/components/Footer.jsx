export default function Footer() {
  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Outfit:wght@300;400;500&display=swap');

        .footer {
          background: rgba(3,3,8,0.99);
          border-top: 1px solid rgba(0,255,180,0.07);
          padding: 3rem 4rem 2rem;
          font-family: 'Outfit', sans-serif;
          position: relative;
          overflow: hidden;
        }

        .footer::before {
          content: '';
          position: absolute;
          bottom: -60px;
          left: 50%;
          transform: translateX(-50%);
          width: 600px;
          height: 120px;
          background: radial-gradient(ellipse, rgba(0,255,180,0.04) 0%, transparent 70%);
          pointer-events: none;
        }

        .footer-grid {
          display: grid;
          grid-template-columns: 2fr 1fr 1fr 1fr;
          gap: 3rem;
          max-width: 1200px;
          margin: 0 auto;
        }

        .footer-brand .logo-text {
          font-family: 'Cinzel', serif;
          font-size: 1.3rem;
          font-weight: 700;
          background: linear-gradient(90deg, #00ffb4, #00c8ff, #a78bfa);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          display: block;
          margin-bottom: 0.75rem;
        }

        .footer-brand p {
          color: rgba(255,255,255,0.35);
          font-size: 0.82rem;
          line-height: 1.7;
          max-width: 260px;
          margin: 0 0 1.25rem 0;
        }

        .footer-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          background: rgba(0,255,180,0.06);
          border: 1px solid rgba(0,255,180,0.12);
          border-radius: 20px;
          padding: 4px 12px;
          font-size: 0.7rem;
          color: rgba(0,255,180,0.7);
          letter-spacing: 0.06em;
        }

        .footer-col h4 {
          font-size: 0.72rem;
          font-weight: 600;
          letter-spacing: 0.15em;
          text-transform: uppercase;
          color: rgba(255,255,255,0.25);
          margin: 0 0 1rem 0;
        }

        .footer-col ul {
          list-style: none;
          margin: 0;
          padding: 0;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .footer-col a {
          color: rgba(255,255,255,0.45);
          text-decoration: none;
          font-size: 0.83rem;
          transition: color 0.2s ease;
          display: inline-block;
        }

        .footer-col a:hover {
          color: #00ffb4;
        }

        .footer-bottom {
          max-width: 1200px;
          margin: 2.5rem auto 0;
          padding-top: 1.5rem;
          border-top: 1px solid rgba(255,255,255,0.05);
          display: flex;
          align-items: center;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: 1rem;
        }

        .footer-bottom p {
          color: rgba(255,255,255,0.2);
          font-size: 0.75rem;
          margin: 0;
        }

        .footer-bottom .disclaimer {
          font-size: 0.7rem;
          color: rgba(255,100,100,0.4);
          max-width: 500px;
          text-align: right;
        }

        .footer-pulse {
          display: inline-block;
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #00ffb4;
          box-shadow: 0 0 6px #00ffb4;
          animation: footerpulse 2s ease-in-out infinite;
        }

        @keyframes footerpulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }

        @media (max-width: 900px) {
          .footer { padding: 2rem 1.5rem; }
          .footer-grid { grid-template-columns: 1fr 1fr; gap: 2rem; }
          .footer-bottom .disclaimer { text-align: left; }
        }

        @media (max-width: 500px) {
          .footer-grid { grid-template-columns: 1fr; }
        }
      `}</style>

      <footer className="footer">
        <div className="footer-grid">
          <div className="footer-brand">
            <span className="logo-text">Arogya Setu</span>
            <p>AI-powered prescription intelligence for rural and semi-urban India. Bridging the gap between prescriptions and patients.</p>
            <span className="footer-badge">
              <span className="footer-pulse" />
              DPDP Act 2023 Compliant
            </span>
          </div>

          <div className="footer-col">
            <h4>Features</h4>
            <ul>
              <li><a href="/scan">Scan Prescription</a></li>
              <li><a href="/drug-checker">Drug Interaction</a></li>
              <li><a href="/schedule">Med Schedule</a></li>
              <li><a href="/vault">Rx Vault</a></li>
              <li><a href="/multi-prescription">Multi-Rx</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h4>Technology</h4>
            <ul>
              <li><a href="#">Tesseract OCR</a></li>
              <li><a href="#">Claude AI API</a></li>
              <li><a href="#">OpenFDA Data</a></li>
              <li><a href="#">IndicTrans2</a></li>
              <li><a href="#">Offline First</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h4>Languages</h4>
            <ul>
              <li><a href="#">English</a></li>
              <li><a href="#">తెలుగు</a></li>
              <li><a href="#">हिन्दी</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <p>© 2025 Arogya Setu · MedCircular · Built with ❤️ for rural India</p>
          <p className="disclaimer">⚠️ For informational use only. Always consult your doctor or pharmacist before taking or stopping any medication.</p>
        </div>
      </footer>
    </>
  );
}
