import { useState } from "react";

const DEMO_MEDICINES = [
  {
    id: 1,
    name: "Metformin",
    generic: "Metformin Hydrochloride",
    dose: "500mg",
    frequency: "Twice daily",
    duration: "30 days",
    food: "After food",
    instructions: "Do not crush. Swallow whole.",
    confidence: 92,
    tag: "Diabetes",
  },
  {
    id: 2,
    name: "Amlodipine",
    generic: "Amlodipine Besylate",
    dose: "5mg",
    frequency: "Once daily",
    duration: "30 days",
    food: "Any time",
    instructions: "Preferably at the same time each day.",
    confidence: 88,
    tag: "Blood Pressure",
  },
  {
    id: 3,
    name: "Pantoprazole",
    generic: "Pantoprazole Sodium",
    dose: "40mg",
    frequency: "Once daily",
    duration: "14 days",
    food: "Before food",
    instructions: "Take 30 minutes before breakfast.",
    confidence: 76,
    tag: "Acidity",
  },
  {
    id: 4,
    name: "Atorvastatin",
    generic: "Atorvastatin Calcium",
    dose: "10mg",
    frequency: "Once at bedtime",
    duration: "30 days",
    food: "Any time",
    instructions: "Best taken at night for maximum effectiveness.",
    confidence: 95,
    tag: "Cholesterol",
  },
];

function ConfidenceBadge({ score }) {
  const color = score >= 90 ? "#00ffb4" : score >= 75 ? "#f59e0b" : "#ef4444";
  const label = score >= 90 ? "High" : score >= 75 ? "Medium" : "Low";
  return (
    <span style={{
      fontSize: "0.65rem",
      fontWeight: 700,
      color,
      background: `${color}18`,
      border: `1px solid ${color}30`,
      borderRadius: 4,
      padding: "2px 7px",
      letterSpacing: "0.06em",
    }}>
      {score}% {label}
    </span>
  );
}

function MedicineCard({ med, index }) {
  const [expanded, setExpanded] = useState(false);
  const tagColors = {
    Diabetes: "rgba(0,255,180,0.1)",
    "Blood Pressure": "rgba(167,139,250,0.1)",
    Acidity: "rgba(255,160,60,0.1)",
    Cholesterol: "rgba(0,200,255,0.1)",
  };

  return (
    <div
      className="med-card"
      style={{ animationDelay: `${index * 0.08}s`, background: tagColors[med.tag] || "rgba(255,255,255,0.02)" }}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="med-header">
        <div>
          <span className="med-name">{med.name}</span>
          <span className="med-generic">{med.generic}</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
          <ConfidenceBadge score={med.confidence} />
          <span className="med-tag">{med.tag}</span>
        </div>
      </div>

      <div className="med-pills-row">
        <span className="med-pill dose">💊 {med.dose}</span>
        <span className="med-pill freq">🔁 {med.frequency}</span>
        <span className="med-pill dur">📅 {med.duration}</span>
        <span className="med-pill food">🍽️ {med.food}</span>
      </div>

      {expanded && (
        <div className="med-expanded">
          <p className="med-instruction">📝 {med.instructions}</p>
          <div className="med-telugu">
            <span className="lang-label">తెలుగు</span>
            <p>రోజుకు రెండు సార్లు తినిన తర్వాత వేసుకోండి</p>
          </div>
          <div className="med-hindi">
            <span className="lang-label">हिन्दी</span>
            <p>खाने के बाद दिन में दो बार लें</p>
          </div>
        </div>
      )}

      <div className="med-expand-hint">{expanded ? "▲ Less" : "▼ Details & Translation"}</div>
    </div>
  );
}

export default function ScanPage() {
  const [state, setState] = useState("upload"); // upload | scanning | results
  const [dragOver, setDragOver] = useState(false);

  const handleScan = () => {
    setState("scanning");
    setTimeout(() => setState("results"), 2800);
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Outfit:wght@300;400;500;600;700&display=swap');

        .scan-page {
          min-height: 100vh;
          background: #03030a;
          color: #fff;
          font-family: 'Outfit', sans-serif;
          padding: 90px 2rem 4rem;
        }

        .scan-container {
          max-width: 960px;
          margin: 0 auto;
        }

        .page-title {
          font-family: 'Cinzel', serif;
          font-size: 2rem;
          font-weight: 700;
          background: linear-gradient(90deg, #00ffb4, #00c8ff);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          margin-bottom: 0.4rem;
        }

        .page-sub {
          color: rgba(255,255,255,0.35);
          font-size: 0.9rem;
          margin-bottom: 2.5rem;
        }

        /* Upload Zone */
        .upload-zone {
          border: 2px dashed rgba(0,255,180,0.2);
          border-radius: 20px;
          padding: 4rem 2rem;
          text-align: center;
          transition: all 0.3s ease;
          cursor: pointer;
          position: relative;
          overflow: hidden;
          background: rgba(0,255,180,0.02);
        }

        .upload-zone:hover, .upload-zone.drag {
          border-color: rgba(0,255,180,0.5);
          background: rgba(0,255,180,0.05);
        }

        .upload-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
          display: block;
          filter: grayscale(0.2);
        }

        .upload-title {
          font-size: 1.2rem;
          font-weight: 600;
          color: rgba(255,255,255,0.85);
          margin-bottom: 0.5rem;
        }

        .upload-hint {
          color: rgba(255,255,255,0.3);
          font-size: 0.82rem;
          margin-bottom: 1.75rem;
        }

        .btn-scan {
          background: linear-gradient(135deg, #00ffb4, #00c8ff);
          color: #000;
          font-family: 'Outfit', sans-serif;
          font-size: 0.9rem;
          font-weight: 700;
          padding: 12px 32px;
          border: none;
          border-radius: 10px;
          cursor: pointer;
          transition: all 0.25s ease;
          box-shadow: 0 0 25px rgba(0,255,180,0.3);
          letter-spacing: 0.04em;
        }

        .btn-scan:hover {
          box-shadow: 0 0 40px rgba(0,255,180,0.5);
          transform: translateY(-2px);
        }

        .demo-note {
          color: rgba(255,255,255,0.2);
          font-size: 0.72rem;
          margin-top: 1rem;
        }

        /* Scanning animation */
        .scan-anim {
          text-align: center;
          padding: 5rem 2rem;
        }

        .scan-progress-wrap {
          position: relative;
          width: 120px;
          height: 120px;
          margin: 0 auto 2rem;
        }

        .scan-ring {
          width: 120px;
          height: 120px;
          border-radius: 50%;
          border: 2px solid rgba(0,255,180,0.1);
          border-top-color: #00ffb4;
          animation: spin 1s linear infinite;
          position: absolute;
          inset: 0;
        }

        .scan-ring-2 {
          width: 90px;
          height: 90px;
          border-radius: 50%;
          border: 2px solid rgba(0,200,255,0.1);
          border-bottom-color: #00c8ff;
          animation: spin 1.5s linear infinite reverse;
          position: absolute;
          top: 15px;
          left: 15px;
        }

        .scan-icon-center {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%,-50%);
          font-size: 1.8rem;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .scan-stages {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
          max-width: 360px;
          margin: 0 auto;
        }

        .scan-stage {
          display: flex;
          align-items: center;
          gap: 10px;
          color: rgba(255,255,255,0.4);
          font-size: 0.84rem;
        }

        .scan-stage.done {
          color: #00ffb4;
        }

        .scan-stage.active {
          color: #fff;
          font-weight: 500;
        }

        .stage-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: currentColor;
          flex-shrink: 0;
        }

        .stage-dot.active {
          animation: pulse 0.8s ease-in-out infinite;
        }

        /* Results */
        .results-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 1.5rem;
          flex-wrap: wrap;
          gap: 1rem;
        }

        .results-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          background: rgba(0,255,180,0.08);
          border: 1px solid rgba(0,255,180,0.2);
          color: #00ffb4;
          font-size: 0.78rem;
          font-weight: 600;
          padding: 5px 12px;
          border-radius: 20px;
          letter-spacing: 0.06em;
        }

        .results-actions {
          display: flex;
          gap: 0.75rem;
          flex-wrap: wrap;
        }

        .btn-action {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          font-family: 'Outfit', sans-serif;
          font-size: 0.8rem;
          font-weight: 600;
          padding: 8px 16px;
          border-radius: 8px;
          cursor: pointer;
          border: 1px solid rgba(255,255,255,0.1);
          background: transparent;
          color: rgba(255,255,255,0.6);
          transition: all 0.2s;
          text-decoration: none;
        }

        .btn-action:hover {
          border-color: rgba(0,255,180,0.3);
          color: #00ffb4;
          background: rgba(0,255,180,0.04);
        }

        .btn-action.primary {
          background: linear-gradient(135deg, #00ffb4, #00c8ff);
          color: #000;
          border-color: transparent;
          box-shadow: 0 0 20px rgba(0,255,180,0.2);
        }

        .btn-action.primary:hover {
          box-shadow: 0 0 30px rgba(0,255,180,0.4);
          transform: translateY(-1px);
          color: #000;
        }

        /* Medicine cards */
        .med-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 1.25rem;
          margin-bottom: 2rem;
        }

        .med-card {
          border: 1px solid rgba(255,255,255,0.06);
          border-radius: 14px;
          padding: 1.25rem;
          cursor: pointer;
          transition: all 0.25s ease;
          animation: fadeInUp 0.5s ease both;
        }

        .med-card:hover {
          border-color: rgba(0,255,180,0.18);
          transform: translateY(-2px);
        }

        .med-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1rem;
          gap: 1rem;
        }

        .med-name {
          display: block;
          font-size: 1rem;
          font-weight: 600;
          color: rgba(255,255,255,0.9);
          margin-bottom: 3px;
        }

        .med-generic {
          display: block;
          font-size: 0.72rem;
          color: rgba(255,255,255,0.3);
          font-style: italic;
        }

        .med-tag {
          font-size: 0.62rem;
          font-weight: 600;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          color: rgba(255,255,255,0.3);
        }

        .med-pills-row {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          margin-bottom: 0.75rem;
        }

        .med-pill {
          font-size: 0.73rem;
          background: rgba(255,255,255,0.04);
          border: 1px solid rgba(255,255,255,0.07);
          border-radius: 6px;
          padding: 3px 9px;
          color: rgba(255,255,255,0.6);
          white-space: nowrap;
        }

        .med-pill.dose { color: #00ffb4; border-color: rgba(0,255,180,0.15); background: rgba(0,255,180,0.06); }
        .med-pill.freq { color: #00c8ff; border-color: rgba(0,200,255,0.15); background: rgba(0,200,255,0.06); }

        .med-expand-hint {
          font-size: 0.7rem;
          color: rgba(255,255,255,0.2);
          text-align: right;
          margin-top: 0.5rem;
          letter-spacing: 0.04em;
        }

        .med-expanded {
          border-top: 1px solid rgba(255,255,255,0.05);
          padding-top: 0.75rem;
          margin-top: 0.5rem;
          animation: fadeIn 0.3s ease;
        }

        .med-instruction {
          color: rgba(255,255,255,0.5);
          font-size: 0.8rem;
          margin-bottom: 0.75rem;
        }

        .lang-label {
          font-size: 0.65rem;
          font-weight: 700;
          letter-spacing: 0.1em;
          color: #00ffb4;
          background: rgba(0,255,180,0.08);
          border-radius: 4px;
          padding: 2px 7px;
          margin-right: 8px;
        }

        .med-telugu, .med-hindi {
          display: flex;
          align-items: center;
          gap: 4px;
          margin-bottom: 5px;
        }

        .med-telugu p, .med-hindi p {
          color: rgba(255,255,255,0.45);
          font-size: 0.8rem;
        }

        .warn-banner {
          border: 1px solid rgba(239,68,68,0.25);
          background: rgba(239,68,68,0.06);
          border-radius: 12px;
          padding: 1rem 1.25rem;
          display: flex;
          align-items: flex-start;
          gap: 10px;
          margin-bottom: 1.5rem;
        }

        .warn-banner .warn-icon { font-size: 1.1rem; flex-shrink: 0; }
        .warn-banner p { color: rgba(239,100,100,0.9); font-size: 0.82rem; margin: 0; line-height: 1.6; }

        .btn-reset {
          background: none;
          border: 1px solid rgba(255,255,255,0.08);
          color: rgba(255,255,255,0.3);
          font-family: 'Outfit', sans-serif;
          font-size: 0.8rem;
          padding: 8px 16px;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-reset:hover {
          color: rgba(255,255,255,0.6);
          border-color: rgba(255,255,255,0.15);
        }

        @keyframes fadeInUp {
          from { opacity:0; transform: translateY(16px); }
          to   { opacity:1; transform: translateY(0); }
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to   { opacity: 1; }
        }

        @media (max-width: 680px) {
          .med-grid { grid-template-columns: 1fr; }
        }
      `}</style>

      <div className="scan-page">
        <div className="scan-container">
          <h1 className="page-title">Scan Prescription</h1>
          <p className="page-sub">Upload a prescription image — OCR extracts text, AI structures it, and we translate it for you.</p>

          {state === "upload" && (
            <div
              className={`upload-zone ${dragOver ? "drag" : ""}`}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => { e.preventDefault(); setDragOver(false); }}
            >
              <span className="upload-icon">📋</span>
              <div className="upload-title">Drop prescription image here</div>
              <div className="upload-hint">Supports JPG, PNG, PDF · Handwritten &amp; printed prescriptions</div>
              <button className="btn-scan" onClick={handleScan}>
                ⚡ Scan with AI (Demo)
              </button>
              <p className="demo-note">* This demo uses a pre-loaded sample prescription</p>
            </div>
          )}

          {state === "scanning" && (
            <div className="scan-anim">
              <div className="scan-progress-wrap">
                <div className="scan-ring" />
                <div className="scan-ring-2" />
                <div className="scan-icon-center">🔬</div>
              </div>
              <div className="scan-stages">
                {[
                  { label: "Image preprocessing (OpenCV)", status: "done" },
                  { label: "OCR extraction (Tesseract 5)", status: "done" },
                  { label: "AI structuring (Claude API)", status: "active" },
                  { label: "Safety validation", status: "pending" },
                  { label: "Translation to Telugu/Hindi", status: "pending" },
                ].map((s, i) => (
                  <div key={i} className={`scan-stage ${s.status}`}>
                    <div className={`stage-dot ${s.status === "active" ? "active" : ""}`} />
                    {s.label}
                    {s.status === "done" && " ✓"}
                  </div>
                ))}
              </div>
            </div>
          )}

          {state === "results" && (
            <>
              <div className="warn-banner">
                <span className="warn-icon">⚠️</span>
                <p>Always verify with your pharmacist or doctor before taking these medicines. This AI analysis is for informational support only.</p>
              </div>

              <div className="results-header">
                <div>
                  <span className="results-badge">✅ {DEMO_MEDICINES.length} medicines extracted</span>
                </div>
                <div className="results-actions">
                  <a href="/drug-checker" className="btn-action">🛡️ Check Interactions</a>
                  <a href="/schedule" className="btn-action">📅 Generate Schedule</a>
                  <a href="/vault" className="btn-action primary">💾 Save to Vault</a>
                  <button className="btn-reset" onClick={() => setState("upload")}>↩ Scan Again</button>
                </div>
              </div>

              <div className="med-grid">
                {DEMO_MEDICINES.map((med, i) => (
                  <MedicineCard key={med.id} med={med} index={i} />
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}
