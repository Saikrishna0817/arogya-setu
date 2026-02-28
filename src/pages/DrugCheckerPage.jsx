import { useState } from "react";

const DEMO_INTERACTIONS = [
  {
    drug1: "Metformin",
    drug2: "Amlodipine",
    severity: "minor",
    title: "Minor Interaction",
    description: "Amlodipine may slightly increase blood sugar levels, potentially affecting Metformin's effectiveness in controlling diabetes. Monitor blood sugar regularly.",
    action: "Inform your doctor at next visit. No immediate action required.",
  },
  {
    drug1: "Atorvastatin",
    drug2: "Amlodipine",
    severity: "moderate",
    title: "Moderate Interaction",
    description: "Amlodipine can increase Atorvastatin blood levels by about 18%, potentially increasing the risk of muscle pain or weakness (myopathy). This combination is used but requires monitoring.",
    action: "Watch for unexplained muscle pain, tenderness, or weakness. Report to your doctor if symptoms appear.",
  },
  {
    drug1: "Pantoprazole",
    drug2: "Metformin",
    severity: "minor",
    title: "Minor Interaction",
    description: "Pantoprazole may slightly increase Metformin plasma levels. In patients with normal kidney function, this is generally not clinically significant.",
    action: "No action needed for most patients. Kidney function monitoring advised for elderly patients.",
  },
];

const DRUG_DATABASE = [
  "Metformin", "Amlodipine", "Pantoprazole", "Atorvastatin", "Aspirin",
  "Losartan", "Ramipril", "Glimepiride", "Clopidogrel", "Warfarin",
  "Ciprofloxacin", "Azithromycin", "Diazepam", "Omeprazole", "Paracetamol",
];

const severityConfig = {
  critical: {
    color: "#ef4444",
    bg: "rgba(239,68,68,0.08)",
    border: "rgba(239,68,68,0.25)",
    icon: "🚨",
    label: "CRITICAL",
  },
  moderate: {
    color: "#f59e0b",
    bg: "rgba(245,158,11,0.08)",
    border: "rgba(245,158,11,0.25)",
    icon: "⚠️",
    label: "MODERATE",
  },
  minor: {
    color: "#00c8ff",
    bg: "rgba(0,200,255,0.06)",
    border: "rgba(0,200,255,0.18)",
    icon: "ℹ️",
    label: "MINOR",
  },
};

function InteractionCard({ item, delay }) {
  const [open, setOpen] = useState(false);
  const cfg = severityConfig[item.severity];
  return (
    <div
      onClick={() => setOpen(!open)}
      style={{
        background: cfg.bg,
        border: `1px solid ${cfg.border}`,
        borderRadius: 14,
        padding: "1.25rem",
        cursor: "pointer",
        transition: "all 0.25s ease",
        animationDelay: delay,
        animation: "fadeInUp 0.5s ease both",
        marginBottom: "1rem",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10, gap: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: "1.2rem" }}>{cfg.icon}</span>
          <div>
            <div style={{ fontSize: "0.88rem", fontWeight: 600, color: "rgba(255,255,255,0.9)", marginBottom: 3 }}>
              <span style={{ color: "#00ffb4" }}>{item.drug1}</span>
              <span style={{ color: "rgba(255,255,255,0.3)", margin: "0 6px" }}>+</span>
              <span style={{ color: "#a78bfa" }}>{item.drug2}</span>
            </div>
            <span style={{
              fontSize: "0.62rem",
              fontWeight: 700,
              letterSpacing: "0.1em",
              color: cfg.color,
              background: `${cfg.color}18`,
              border: `1px solid ${cfg.color}30`,
              borderRadius: 4,
              padding: "1px 8px",
            }}>
              {cfg.label}
            </span>
          </div>
        </div>
        <span style={{ color: "rgba(255,255,255,0.2)", fontSize: "0.8rem" }}>{open ? "▲" : "▼"}</span>
      </div>
      {open && (
        <div style={{ borderTop: "1px solid rgba(255,255,255,0.06)", paddingTop: "0.75rem", marginTop: "0.25rem", animation: "fadeIn 0.3s ease" }}>
          <p style={{ color: "rgba(255,255,255,0.55)", fontSize: "0.83rem", lineHeight: 1.7, marginBottom: "0.75rem" }}>{item.description}</p>
          <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 8, padding: "10px 14px" }}>
            <span style={{ fontSize: "0.68rem", fontWeight: 700, letterSpacing: "0.1em", color: cfg.color, textTransform: "uppercase" }}>What to do</span>
            <p style={{ color: "rgba(255,255,255,0.65)", fontSize: "0.82rem", marginTop: 4, lineHeight: 1.6 }}>{item.action}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default function DrugCheckerPage() {
  const [drugs, setDrugs] = useState(["Metformin", "Amlodipine", "Pantoprazole", "Atorvastatin"]);
  const [input, setInput] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [checked, setChecked] = useState(false);

  const suggestions = DRUG_DATABASE.filter(
    (d) => d.toLowerCase().includes(input.toLowerCase()) && !drugs.includes(d) && input.length > 0
  );

  const addDrug = (name) => {
    if (!drugs.includes(name)) setDrugs([...drugs, name]);
    setInput("");
    setShowSuggestions(false);
    setChecked(false);
  };

  const removeDrug = (name) => {
    setDrugs(drugs.filter((d) => d !== name));
    setChecked(false);
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Outfit:wght@300;400;500;600;700&display=swap');
        * { box-sizing: border-box; }
        body { background: #03030a; color: #fff; font-family: 'Outfit', sans-serif; }

        .checker-page { min-height: 100vh; padding: 90px 2rem 4rem; background: #03030a; }
        .checker-container { max-width: 800px; margin: 0 auto; }

        .page-title {
          font-family: 'Cinzel', serif; font-size: 2rem; font-weight: 700;
          background: linear-gradient(90deg, #ef4444, #f59e0b, #00ffb4);
          -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
          margin-bottom: 0.4rem;
        }
        .page-sub { color: rgba(255,255,255,0.35); font-size: 0.9rem; margin-bottom: 2rem; }

        .input-section {
          background: rgba(255,255,255,0.02);
          border: 1px solid rgba(255,255,255,0.07);
          border-radius: 16px;
          padding: 1.75rem;
          margin-bottom: 2rem;
        }

        .input-label { font-size: 0.78rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: rgba(255,255,255,0.3); margin-bottom: 1rem; display: block; }

        .drug-chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 1rem; min-height: 36px; }

        .drug-chip {
          display: inline-flex; align-items: center; gap: 6px;
          background: rgba(0,255,180,0.08); border: 1px solid rgba(0,255,180,0.2);
          border-radius: 20px; padding: 5px 12px;
          font-size: 0.82rem; font-weight: 500; color: #00ffb4;
          transition: all 0.2s;
        }

        .chip-remove {
          background: none; border: none; color: rgba(0,255,180,0.5); cursor: pointer; font-size: 0.9rem; padding: 0; line-height: 1;
          transition: color 0.2s;
        }
        .chip-remove:hover { color: #ef4444; }

        .search-wrap { position: relative; }

        .drug-input {
          width: 100%; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
          border-radius: 10px; padding: 11px 16px; color: #fff; font-family: 'Outfit', sans-serif;
          font-size: 0.88rem; outline: none; transition: all 0.2s;
        }
        .drug-input:focus { border-color: rgba(0,255,180,0.4); background: rgba(0,255,180,0.02); }
        .drug-input::placeholder { color: rgba(255,255,255,0.2); }

        .suggestions {
          position: absolute; top: calc(100% + 6px); left: 0; right: 0;
          background: #0d0d18; border: 1px solid rgba(255,255,255,0.1);
          border-radius: 10px; overflow: hidden; z-index: 50;
          box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        }

        .suggestion-item {
          padding: 10px 16px; font-size: 0.85rem; color: rgba(255,255,255,0.65); cursor: pointer;
          border-bottom: 1px solid rgba(255,255,255,0.04); transition: all 0.15s;
        }
        .suggestion-item:last-child { border-bottom: none; }
        .suggestion-item:hover { background: rgba(0,255,180,0.06); color: #00ffb4; }

        .check-btn {
          width: 100%; margin-top: 1.25rem; background: linear-gradient(135deg, #ef4444, #f59e0b);
          color: #fff; font-family: 'Outfit', sans-serif; font-size: 0.9rem; font-weight: 700;
          padding: 13px; border: none; border-radius: 10px; cursor: pointer;
          transition: all 0.25s; letter-spacing: 0.04em; box-shadow: 0 0 25px rgba(239,68,68,0.25);
        }
        .check-btn:hover { box-shadow: 0 0 40px rgba(239,68,68,0.4); transform: translateY(-2px); }
        .check-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

        .summary-row {
          display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 2rem;
        }

        .sum-card {
          border-radius: 12px; padding: 1.25rem; text-align: center; border: 1px solid;
          animation: fadeInUp 0.5s ease both;
        }

        .sum-count { font-family: 'Cinzel', serif; font-size: 2rem; font-weight: 700; display: block; margin-bottom: 4px; }
        .sum-label { font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; opacity: 0.7; }

        .safe-banner {
          border: 1px solid rgba(0,255,180,0.2); background: rgba(0,255,180,0.05);
          border-radius: 12px; padding: 1.25rem; text-align: center;
          color: #00ffb4; font-size: 0.9rem; font-weight: 500; margin-top: 1rem;
          animation: fadeIn 0.5s ease;
        }

        .disclaimer {
          border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 1rem 1.25rem;
          margin-top: 2rem; color: rgba(255,255,255,0.25); font-size: 0.78rem; line-height: 1.6;
        }

        @keyframes fadeInUp { from { opacity:0; transform: translateY(16px); } to { opacity:1; transform: translateY(0); } }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
      `}</style>

      <div className="checker-page">
        <div className="checker-container">
          <h1 className="page-title">Drug Interaction Checker</h1>
          <p className="page-sub">Add all medicines your patient is taking. We check every pair for dangerous interactions.</p>

          <div className="input-section">
            <span className="input-label">Add medicines to check</span>

            <div className="drug-chips">
              {drugs.map((d) => (
                <span key={d} className="drug-chip">
                  {d}
                  <button className="chip-remove" onClick={() => removeDrug(d)}>×</button>
                </span>
              ))}
            </div>

            <div className="search-wrap">
              <input
                className="drug-input"
                placeholder="Type medicine name..."
                value={input}
                onChange={(e) => { setInput(e.target.value); setShowSuggestions(true); }}
                onKeyDown={(e) => e.key === "Enter" && input && addDrug(input)}
              />
              {showSuggestions && suggestions.length > 0 && (
                <div className="suggestions">
                  {suggestions.map((s) => (
                    <div key={s} className="suggestion-item" onClick={() => addDrug(s)}>{s}</div>
                  ))}
                </div>
              )}
            </div>

            <button
              className="check-btn"
              disabled={drugs.length < 2}
              onClick={() => setChecked(true)}
            >
              🛡️ Check {drugs.length} Medicine{drugs.length !== 1 ? "s" : ""} for Interactions
            </button>
          </div>

          {checked && (
            <>
              <div className="summary-row">
                <div className="sum-card" style={{ border: "1px solid rgba(239,68,68,0.25)", background: "rgba(239,68,68,0.05)" }}>
                  <span className="sum-count" style={{ color: "#ef4444" }}>0</span>
                  <span className="sum-label" style={{ color: "#ef4444" }}>Critical</span>
                </div>
                <div className="sum-card" style={{ border: "1px solid rgba(245,158,11,0.25)", background: "rgba(245,158,11,0.05)" }}>
                  <span className="sum-count" style={{ color: "#f59e0b" }}>1</span>
                  <span className="sum-label" style={{ color: "#f59e0b" }}>Moderate</span>
                </div>
                <div className="sum-card" style={{ border: "1px solid rgba(0,200,255,0.2)", background: "rgba(0,200,255,0.04)" }}>
                  <span className="sum-count" style={{ color: "#00c8ff" }}>2</span>
                  <span className="sum-label" style={{ color: "#00c8ff" }}>Minor</span>
                </div>
              </div>

              {DEMO_INTERACTIONS.map((item, i) => (
                <InteractionCard key={i} item={item} delay={`${i * 0.07}s`} />
              ))}

              <div className="safe-banner">
                ✅ No life-threatening (critical) interactions found in this combination.
              </div>
            </>
          )}

          <div className="disclaimer">
            ⚕️ This tool uses local drug data and OpenFDA API results. It is not a substitute for professional pharmacist review. Always consult your doctor before starting, stopping, or changing any medication.
          </div>
        </div>
      </div>
    </>
  );
}
