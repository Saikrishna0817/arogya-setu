import { useEffect, useRef, useState } from "react";

// ─── 3D DNA / Medical Helix Animation ───────────────────────────────────────
function MedicalAnimation() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let animId;
    let t = 0;

    const resize = () => {
      canvas.width = canvas.offsetWidth * window.devicePixelRatio;
      canvas.height = canvas.offsetHeight * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };
    resize();
    window.addEventListener("resize", resize);

    const W = () => canvas.offsetWidth;
    const H = () => canvas.offsetHeight;

    const drawFrame = () => {
      ctx.clearRect(0, 0, W(), H());
      t += 0.008;

      const cx = W() / 2;
      const cy = H() / 2;
      const helixH = H() * 0.75;
      const helixY = cy - helixH / 2;
      const amplitude = W() * 0.12;
      const nodes = 28;

      // Draw floating particles
      for (let p = 0; p < 40; p++) {
        const px = (Math.sin(p * 2.4 + t * 0.7) * 0.45 + 0.5) * W();
        const py = (Math.cos(p * 1.9 + t * 0.5) * 0.45 + 0.5) * H();
        const pr = Math.sin(p * 3.1 + t) * 1.5 + 2;
        const alpha = (Math.sin(p * 2 + t * 1.2) + 1) * 0.5 * 0.12;
        ctx.beginPath();
        ctx.arc(px, py, pr, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0,255,180,${alpha})`;
        ctx.fill();
      }

      // DNA helix strands
      for (let i = 0; i < nodes; i++) {
        const frac = i / (nodes - 1);
        const y = helixY + frac * helixH;
        const angle = frac * Math.PI * 5 + t;
        const x1 = cx + Math.sin(angle) * amplitude;
        const x2 = cx + Math.sin(angle + Math.PI) * amplitude;
        const depth1 = (Math.sin(angle) + 1) / 2;
        const depth2 = (Math.sin(angle + Math.PI) + 1) / 2;

        // Strand 1 node
        const r1 = 5 + depth1 * 5;
        const grd1 = ctx.createRadialGradient(x1, y, 0, x1, y, r1 * 2);
        grd1.addColorStop(0, `rgba(0,255,180,${0.6 + depth1 * 0.4})`);
        grd1.addColorStop(1, `rgba(0,200,255,0)`);
        ctx.beginPath();
        ctx.arc(x1, y, r1, 0, Math.PI * 2);
        ctx.fillStyle = grd1;
        ctx.fill();

        // Strand 2 node
        const r2 = 5 + depth2 * 5;
        const grd2 = ctx.createRadialGradient(x2, y, 0, x2, y, r2 * 2);
        grd2.addColorStop(0, `rgba(167,139,250,${0.6 + depth2 * 0.4})`);
        grd2.addColorStop(1, `rgba(0,200,255,0)`);
        ctx.beginPath();
        ctx.arc(x2, y, r2, 0, Math.PI * 2);
        ctx.fillStyle = grd2;
        ctx.fill();

        // Rungs (cross connectors)
        if (i % 3 === 0) {
          const rungAlpha = 0.1 + Math.abs(Math.sin(angle)) * 0.3;
          const grdR = ctx.createLinearGradient(x1, y, x2, y);
          grdR.addColorStop(0, `rgba(0,255,180,${rungAlpha})`);
          grdR.addColorStop(0.5, `rgba(0,200,255,${rungAlpha * 1.5})`);
          grdR.addColorStop(1, `rgba(167,139,250,${rungAlpha})`);
          ctx.beginPath();
          ctx.moveTo(x1, y);
          ctx.lineTo(x2, y);
          ctx.strokeStyle = grdR;
          ctx.lineWidth = 1.5;
          ctx.stroke();
        }

        // Strand curves
        if (i > 0) {
          const prevFrac = (i - 1) / (nodes - 1);
          const prevY = helixY + prevFrac * helixH;
          const prevAngle = prevFrac * Math.PI * 5 + t;
          const px1 = cx + Math.sin(prevAngle) * amplitude;
          const px2 = cx + Math.sin(prevAngle + Math.PI) * amplitude;

          ctx.beginPath();
          ctx.moveTo(px1, prevY);
          ctx.lineTo(x1, y);
          ctx.strokeStyle = `rgba(0,255,180,0.18)`;
          ctx.lineWidth = 1.2;
          ctx.stroke();

          ctx.beginPath();
          ctx.moveTo(px2, prevY);
          ctx.lineTo(x2, y);
          ctx.strokeStyle = `rgba(167,139,250,0.18)`;
          ctx.lineWidth = 1.2;
          ctx.stroke();
        }
      }

      // Central glow
      const cgrd = ctx.createRadialGradient(cx, cy, 0, cx, cy, amplitude * 1.5);
      cgrd.addColorStop(0, `rgba(0,255,180,0.04)`);
      cgrd.addColorStop(1, `rgba(0,200,255,0)`);
      ctx.beginPath();
      ctx.ellipse(cx, cy, amplitude * 1.5, helixH * 0.5, 0, 0, Math.PI * 2);
      ctx.fillStyle = cgrd;
      ctx.fill();

      animId = requestAnimationFrame(drawFrame);
    };

    drawFrame();
    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{ width: "100%", height: "100%", display: "block" }}
    />
  );
}

// ─── Stats Counter ────────────────────────────────────────────────────────────
function StatCard({ value, label, color }) {
  const [count, setCount] = useState(0);
  const numVal = parseInt(value.replace(/\D/g, ""), 10);
  const suffix = value.replace(/[0-9]/g, "");

  useEffect(() => {
    let start = 0;
    const duration = 1800;
    const step = numVal / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= numVal) {
        setCount(numVal);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, 16);
    return () => clearInterval(timer);
  }, [numVal]);

  return (
    <div className="stat-card">
      <span className="stat-value" style={{ background: color, WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>
        {count}{suffix}
      </span>
      <span className="stat-label">{label}</span>
    </div>
  );
}

// ─── Feature Card ─────────────────────────────────────────────────────────────
function FeatureCard({ icon, title, desc, href, gradient, delay }) {
  return (
    <a href={href} className="feat-card" style={{ animationDelay: delay }}>
      <div className="feat-icon" style={{ background: gradient }}>{icon}</div>
      <h3 className="feat-title">{title}</h3>
      <p className="feat-desc">{desc}</p>
      <div className="feat-arrow">→</div>
    </a>
  );
}

// ─── Homepage ─────────────────────────────────────────────────────────────────
export default function HomePage() {
  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Outfit:wght@300;400;500;600;700&display=swap');

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body, html {
          background: #03030a;
          color: #fff;
          font-family: 'Outfit', sans-serif;
          overflow-x: hidden;
        }

        /* ── Hero ── */
        .hero {
          min-height: 100vh;
          display: grid;
          grid-template-columns: 1fr 1fr;
          align-items: center;
          padding: 120px 4rem 4rem;
          position: relative;
          gap: 4rem;
          max-width: 1400px;
          margin: 0 auto;
        }

        .hero-bg {
          position: fixed;
          inset: 0;
          pointer-events: none;
          z-index: 0;
          overflow: hidden;
        }

        .hero-bg::before {
          content: '';
          position: absolute;
          top: -20%;
          right: -10%;
          width: 700px;
          height: 700px;
          background: radial-gradient(ellipse, rgba(0,255,180,0.045) 0%, transparent 65%);
          border-radius: 50%;
        }

        .hero-bg::after {
          content: '';
          position: absolute;
          bottom: -10%;
          left: -5%;
          width: 500px;
          height: 500px;
          background: radial-gradient(ellipse, rgba(167,139,250,0.04) 0%, transparent 65%);
          border-radius: 50%;
        }

        .hero-left {
          position: relative;
          z-index: 2;
          animation: fadeInUp 0.9s ease both;
        }

        .hero-eyebrow {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          font-size: 0.7rem;
          font-weight: 600;
          letter-spacing: 0.18em;
          text-transform: uppercase;
          color: #00ffb4;
          background: rgba(0,255,180,0.07);
          border: 1px solid rgba(0,255,180,0.15);
          padding: 5px 14px;
          border-radius: 20px;
          margin-bottom: 1.5rem;
        }

        .hero-eyebrow-dot {
          width: 5px;
          height: 5px;
          border-radius: 50%;
          background: #00ffb4;
          box-shadow: 0 0 6px #00ffb4;
          animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.4; transform: scale(0.8); }
        }

        .hero-title {
          font-family: 'Cinzel', serif;
          font-size: clamp(2.8rem, 5vw, 4.5rem);
          font-weight: 900;
          line-height: 1.05;
          margin-bottom: 1.25rem;
          letter-spacing: -0.01em;
        }

        .hero-title .line1 {
          display: block;
          background: linear-gradient(90deg, #00ffb4 0%, #00c8ff 50%, #a78bfa 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .hero-title .line2 {
          display: block;
          color: rgba(255,255,255,0.9);
          font-size: 0.7em;
          font-weight: 600;
          margin-top: 0.25rem;
        }

        .hero-subtitle {
          color: rgba(255,255,255,0.45);
          font-size: 1rem;
          line-height: 1.75;
          max-width: 480px;
          margin-bottom: 2.5rem;
        }

        .hero-subtitle strong {
          color: rgba(255,255,255,0.75);
          font-weight: 500;
        }

        .hero-cta-row {
          display: flex;
          align-items: center;
          gap: 1rem;
          flex-wrap: wrap;
        }

        .btn-primary {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          background: linear-gradient(135deg, #00ffb4 0%, #00c8ff 100%);
          color: #000;
          font-family: 'Outfit', sans-serif;
          font-size: 0.9rem;
          font-weight: 700;
          padding: 13px 28px;
          border-radius: 10px;
          text-decoration: none;
          transition: all 0.25s ease;
          box-shadow: 0 0 30px rgba(0,255,180,0.3);
          letter-spacing: 0.03em;
        }

        .btn-primary:hover {
          box-shadow: 0 0 50px rgba(0,255,180,0.5);
          transform: translateY(-2px);
        }

        .btn-secondary {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          color: rgba(255,255,255,0.6);
          font-family: 'Outfit', sans-serif;
          font-size: 0.88rem;
          font-weight: 500;
          padding: 12px 20px;
          border-radius: 10px;
          text-decoration: none;
          border: 1px solid rgba(255,255,255,0.1);
          transition: all 0.25s ease;
          letter-spacing: 0.03em;
        }

        .btn-secondary:hover {
          border-color: rgba(0,255,180,0.3);
          color: #00ffb4;
          background: rgba(0,255,180,0.04);
        }

        .hero-right {
          position: relative;
          z-index: 2;
          height: 520px;
          animation: fadeIn 1.2s ease both 0.3s;
        }

        .canvas-wrap {
          width: 100%;
          height: 100%;
          position: relative;
        }

        .canvas-glow {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%,-50%);
          width: 300px;
          height: 300px;
          background: radial-gradient(circle, rgba(0,255,180,0.08) 0%, transparent 70%);
          border-radius: 50%;
          pointer-events: none;
        }

        /* ── Stats ── */
        .stats-section {
          max-width: 1200px;
          margin: 0 auto;
          padding: 3rem 4rem;
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 1.5rem;
          position: relative;
          z-index: 2;
        }

        .stat-card {
          background: rgba(255,255,255,0.02);
          border: 1px solid rgba(255,255,255,0.05);
          border-radius: 14px;
          padding: 1.5rem;
          text-align: center;
          transition: all 0.3s ease;
        }

        .stat-card:hover {
          border-color: rgba(0,255,180,0.12);
          background: rgba(0,255,180,0.03);
        }

        .stat-value {
          display: block;
          font-family: 'Cinzel', serif;
          font-size: 2.2rem;
          font-weight: 700;
          letter-spacing: -0.02em;
          margin-bottom: 0.4rem;
        }

        .stat-label {
          color: rgba(255,255,255,0.35);
          font-size: 0.76rem;
          letter-spacing: 0.08em;
          text-transform: uppercase;
        }

        /* ── Features ── */
        .features-section {
          max-width: 1200px;
          margin: 0 auto;
          padding: 4rem 4rem 6rem;
          position: relative;
          z-index: 2;
        }

        .section-header {
          text-align: center;
          margin-bottom: 3rem;
        }

        .section-label {
          font-size: 0.7rem;
          font-weight: 600;
          letter-spacing: 0.2em;
          text-transform: uppercase;
          color: #00ffb4;
          margin-bottom: 0.75rem;
          display: block;
        }

        .section-title {
          font-family: 'Cinzel', serif;
          font-size: clamp(1.8rem, 3vw, 2.8rem);
          font-weight: 700;
          background: linear-gradient(135deg, #fff 30%, rgba(255,255,255,0.4) 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          margin-bottom: 0.75rem;
        }

        .section-sub {
          color: rgba(255,255,255,0.35);
          font-size: 0.9rem;
          max-width: 480px;
          margin: 0 auto;
          line-height: 1.7;
        }

        .features-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 1.5rem;
        }

        .feat-card {
          background: rgba(255,255,255,0.02);
          border: 1px solid rgba(255,255,255,0.05);
          border-radius: 16px;
          padding: 1.75rem;
          text-decoration: none;
          color: inherit;
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
          animation: fadeInUp 0.6s ease both;
          cursor: pointer;
          display: block;
        }

        .feat-card::before {
          content: '';
          position: absolute;
          inset: 0;
          background: linear-gradient(135deg, rgba(0,255,180,0.04) 0%, transparent 60%);
          opacity: 0;
          transition: opacity 0.3s ease;
        }

        .feat-card:hover {
          border-color: rgba(0,255,180,0.18);
          transform: translateY(-4px);
          box-shadow: 0 20px 60px rgba(0,0,0,0.4);
        }

        .feat-card:hover::before {
          opacity: 1;
        }

        .feat-icon {
          width: 46px;
          height: 46px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.3rem;
          margin-bottom: 1.25rem;
        }

        .feat-title {
          font-size: 1rem;
          font-weight: 600;
          color: rgba(255,255,255,0.9);
          margin-bottom: 0.6rem;
          letter-spacing: 0.01em;
        }

        .feat-desc {
          color: rgba(255,255,255,0.35);
          font-size: 0.82rem;
          line-height: 1.7;
          margin-bottom: 1.25rem;
        }

        .feat-arrow {
          color: rgba(0,255,180,0.5);
          font-size: 1rem;
          transition: transform 0.2s ease;
        }

        .feat-card:hover .feat-arrow {
          transform: translateX(4px);
          color: #00ffb4;
        }

        /* ── How It Works ── */
        .how-section {
          max-width: 1100px;
          margin: 0 auto 6rem;
          padding: 0 4rem;
          position: relative;
          z-index: 2;
        }

        .steps-row {
          display: flex;
          gap: 0;
          position: relative;
        }

        .steps-row::before {
          content: '';
          position: absolute;
          top: 24px;
          left: 24px;
          right: 24px;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(0,255,180,0.2), transparent);
        }

        .step {
          flex: 1;
          text-align: center;
          padding: 0 1.5rem;
        }

        .step-num {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: rgba(5,5,10,1);
          border: 1px solid rgba(0,255,180,0.25);
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: 'Cinzel', serif;
          font-size: 0.9rem;
          font-weight: 700;
          color: #00ffb4;
          margin: 0 auto 1rem;
          position: relative;
          z-index: 1;
        }

        .step-title {
          font-size: 0.88rem;
          font-weight: 600;
          color: rgba(255,255,255,0.8);
          margin-bottom: 0.5rem;
        }

        .step-desc {
          font-size: 0.76rem;
          color: rgba(255,255,255,0.3);
          line-height: 1.6;
        }

        /* ── Keyframes ── */
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(24px); }
          to   { opacity: 1; transform: translateY(0); }
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to   { opacity: 1; }
        }

        /* ── Responsive ── */
        @media (max-width: 1024px) {
          .hero { grid-template-columns: 1fr; padding: 100px 2rem 3rem; }
          .hero-right { height: 360px; }
          .stats-section { grid-template-columns: repeat(2, 1fr); padding: 2rem; }
          .features-section, .how-section { padding: 3rem 2rem; }
          .features-grid { grid-template-columns: repeat(2, 1fr); }
        }

        @media (max-width: 600px) {
          .features-grid { grid-template-columns: 1fr; }
          .steps-row { flex-direction: column; gap: 2rem; }
          .steps-row::before { display: none; }
        }
      `}</style>

      {/* Background glow */}
      <div className="hero-bg" />

      {/* Hero */}
      <section className="hero">
        <div className="hero-left">
          <div className="hero-eyebrow">
            <span className="hero-eyebrow-dot" />
            AI-Powered Prescription Intelligence
          </div>

          <h1 className="hero-title">
            <span className="line1">Aarogya Setu</span>
            <span className="line2">Bridging Prescriptions & Patients</span>
          </h1>

          <p className="hero-subtitle">
            Scan any prescription — handwritten or printed — and receive{" "}
            <strong>safe, structured, voice-guided</strong> medication instructions in{" "}
            <strong>Telugu or Hindi</strong>. Built for India's 800 million rural patients.
          </p>

          <div className="hero-cta-row">
            <a href="/scan" className="btn-primary">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <rect x="3" y="3" width="18" height="18" rx="3"/><path d="M3 9h18M9 21V9"/>
              </svg>
              Scan Prescription
            </a>
            <a href="/drug-checker" className="btn-secondary">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
              Drug Safety Check
            </a>
          </div>
        </div>

        <div className="hero-right">
          <div className="canvas-wrap">
            <div className="canvas-glow" />
            <MedicalAnimation />
          </div>
        </div>
      </section>

      {/* Stats */}
      <div className="stats-section">
        <StatCard value="800M+" label="Rural patients served" color="linear-gradient(90deg,#00ffb4,#00c8ff)" />
        <StatCard value="3B+" label="Annual prescriptions in India" color="linear-gradient(90deg,#00c8ff,#a78bfa)" />
        <StatCard value="80%" label="Prescriptions still handwritten" color="linear-gradient(90deg,#a78bfa,#f472b6)" />
        <StatCard value="30s" label="Prescription to guidance" color="linear-gradient(90deg,#f472b6,#00ffb4)" />
      </div>

      {/* Features */}
      <section className="features-section">
        <div className="section-header">
          <span className="section-label">Core Features</span>
          <h2 className="section-title">Five Layers of Patient Safety</h2>
          <p className="section-sub">From OCR extraction to voice-guided vernacular instructions — every step designed to protect patients.</p>
        </div>

        <div className="features-grid">
          <FeatureCard
            icon="📷"
            title="Scan Prescription"
            desc="Upload or capture any handwritten or printed prescription. Tesseract OCR extracts text; Claude AI structures it into safe, clear medicine cards."
            href="/scan"
            gradient="linear-gradient(135deg,rgba(0,255,180,0.15),rgba(0,200,255,0.1))"
            delay="0s"
          />
          <FeatureCard
            icon="🛡️"
            title="Drug Interaction Checker"
            desc="Cross-checks every medicine pair against local database + OpenFDA + Claude AI. Critical, moderate, and minor severity alerts with patient-friendly explanations."
            href="/drug-checker"
            gradient="linear-gradient(135deg,rgba(239,68,68,0.12),rgba(255,140,0,0.08))"
            delay="0.07s"
          />
          <FeatureCard
            icon="⚠️"
            title="Dosage Anomaly Detection"
            desc="Flags doses that exceed safe limits or look like OCR errors. Confidence-scored badges indicate whether it's a prescription issue or a reading error."
            href="/dosage"
            gradient="linear-gradient(135deg,rgba(255,200,0,0.12),rgba(255,140,0,0.08))"
            delay="0.14s"
          />
          <FeatureCard
            icon="📅"
            title="Medication Schedule"
            desc="Auto-generates Morning / Afternoon / Evening / Night schedules with food instructions. Export as PDF, iCal, or WhatsApp summary."
            href="/schedule"
            gradient="linear-gradient(135deg,rgba(167,139,250,0.12),rgba(0,200,255,0.08))"
            delay="0.21s"
          />
          <FeatureCard
            icon="🔐"
            title="Prescription Vault"
            desc="Encrypted local storage for chronic patients. Timeline view, medicine search, allergy registry, and side-by-side prescription comparison."
            href="/vault"
            gradient="linear-gradient(135deg,rgba(0,200,255,0.12),rgba(167,139,250,0.08))"
            delay="0.28s"
          />
          <FeatureCard
            icon="📋"
            title="Multi-Prescription Mode"
            desc="Upload prescriptions from multiple doctors simultaneously. Detects cross-prescription drug interactions that no individual doctor can see."
            href="/multi-prescription"
            gradient="linear-gradient(135deg,rgba(244,114,182,0.12),rgba(167,139,250,0.08))"
            delay="0.35s"
          />
        </div>
      </section>

      {/* How It Works */}
      <section className="how-section">
        <div className="section-header">
          <span className="section-label">Pipeline</span>
          <h2 className="section-title">How It Works</h2>
          <p className="section-sub">Six processing stages — prescription image to vernacular voice guidance in under 30 seconds.</p>
        </div>

        <div className="steps-row">
          {[
            { n: "01", t: "Capture", d: "Upload or camera capture prescription" },
            { n: "02", t: "Preprocess", d: "OpenCV deskew, denoise, contrast enhance" },
            { n: "03", t: "OCR", d: "Tesseract 5 extracts raw prescription text" },
            { n: "04", t: "AI Structure", d: "Claude API structures into medicine JSON" },
            { n: "05", t: "Safety Check", d: "Drug interactions + dosage validation" },
            { n: "06", t: "Voice Output", d: "Telugu / Hindi audio + schedule export" },
          ].map((s) => (
            <div className="step" key={s.n}>
              <div className="step-num">{s.n}</div>
              <div className="step-title">{s.t}</div>
              <div className="step-desc">{s.d}</div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
