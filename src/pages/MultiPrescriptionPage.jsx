import { useState } from "react";

const PRESCRIPTIONS = [
  {
    id: 1,
    doctor: "Dr. Ramesh Reddy",
    specialty: "Cardiologist",
    date: "Feb 25, 2026",
    color: "#00c8ff",
    medicines: [
      { name: "Amlodipine", dose: "5mg", freq: "OD", slot: "Night" },
      { name: "Atorvastatin", dose: "10mg", freq: "OD", slot: "Night" },
      { name: "Clopidogrel", dose: "75mg", freq: "OD", slot: "Morning" },
    ],
  },
  {
    id: 2,
    doctor: "Dr. Sunita Sharma",
    specialty: "Endocrinologist",
    date: "Feb 20, 2026",
    color: "#00ffb4",
    medicines: [
      { name: "Metformin", dose: "500mg", freq: "BD", slot: "Morning + Night" },
      { name: "Glimepiride", dose: "1mg", freq: "OD", slot: "Morning" },
      { name: "Pantoprazole", dose: "40mg", freq: "OD", slot: "Morning" },
    ],
  },
];

const CROSS_INTERACTIONS = [
  {
    drug1: "Clopidogrel",
    rx1: "Cardiologist",
    drug2: "Pantoprazole",
    rx2: "Endocrinologist",
    severity: "moderate",
    desc: "Pantoprazole reduces the antiplatelet effect of Clopidogrel by inhibiting CYP2C19. This combination may increase cardiac risk.",
    action: "Inform your cardiologist about the Pantoprazole prescription. An alternative PPI like Rabeprazole may be used.",
  },
];

const slotColors = {
  Morning: "#f59e0b",
  Night: "#a78bfa",
  "Morning + Night": "#00ffb4",
  Afternoon: "#00c8ff",
};

export default function MultiPrescriptionPage() {
  const [state, setState] = useState("upload"); // upload | results
  const [selected, setSelected] = useState([0, 1]);

  const activePrescriptions = PRESCRIPTIONS.filter((_, i) => selected.includes(i));

  const MERGED_SCHEDULE = {
    Morning: [
      { name: "Clopidogrel", dose: "75mg", color: "#00c8ff", source: "Dr. Ramesh Reddy", flag: null },
      { name: "Metformin", dose: "500mg", color: "#00ffb4", source: "Dr. Sunita Sharma", flag: null },
      { name: "Glimepiride", dose: "1mg", color: "#00ffb4", source: "Dr. Sunita Sharma", flag: null },
      { name: "Pantoprazole", dose: "40mg", color: "#00ffb4", source: "Dr. Sunita Sharma", flag: "⚠️" },
    ],
    Night: [
      { name: "Amlodipine", dose: "5mg", color: "#00c8ff", source: "Dr. Ramesh Reddy", flag: null },
      { name: "Atorvastatin", dose: "10mg", color: "#00c8ff", source: "Dr. Ramesh Reddy", flag: null },
      { name: "Metformin", dose: "500mg", color: "#00ffb4", source: "Dr. Sunita Sharma", flag: null },
    ],
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Outfit:wght@300;400;500;600;700&display=swap');
        * { box-sizing: border-box; }
        body { background: #03030a; color: #fff; font-family: 'Outfit', sans-serif; }

        .multi-page { min-height: 100vh; padding: 90px 2rem 4rem; background: #03030a; }
        .multi-container { max-width: 1000px; margin: 0 auto; }

        .page-title {
          font-family: 'Cinzel', serif; font-size: 2rem; font-weight: 700;
          background: linear-gradient(90deg, #f472b6, #a78bfa, #00c8ff);
          -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
          margin-bottom: 0.4rem;
        }
        .page-sub { color: rgba(255,255,255,0.35); font-size: 0.9rem; margin-bottom: 2rem; }

        /* Upload area */
        .upload-area {
          display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 2rem;
        }

        .upload-slot {
          border: 2px dashed rgba(255,255,255,0.08); border-radius: 16px;
          padding: 2.5rem 1.5rem; text-align: center; cursor: pointer; transition: all 0.3s;
        }

        .upload-slot:hover { border-color: rgba(167,139,250,0.3); background: rgba(167,139,250,0.03); }

        .slot-icon { font-size: 2rem; margin-bottom: 0.75rem; display: block; }
        .slot-title { font-size: 0.9rem; font-weight: 600; color: rgba(255,255,255,0.6); margin-bottom: 6px; }
        .slot-hint { font-size: 0.75rem; color: rgba(255,255,255,0.25); }

        .analyze-btn {
          width: 100%; background: linear-gradient(135deg, #f472b6, #a78bfa);
          color: #fff; font-family: 'Outfit', sans-serif; font-size: 0.9rem; font-weight: 700;
          padding: 13px; border: none; border-radius: 10px; cursor: pointer;
          transition: all 0.25s; letter-spacing: 0.04em; box-shadow: 0 0 25px rgba(244,114,182,0.25);
          margin-bottom: 2rem;
        }
        .analyze-btn:hover { box-shadow: 0 0 40px rgba(244,114,182,0.4); transform: translateY(-2px); }

        /* Prescriptions grid */
        .rx-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 2rem; }

        .rx-card {
          background: rgba(255,255,255,0.02);
          border-radius: 14px; overflow: hidden; animation: fadeInUp 0.5s ease both;
        }

        .rx-header {
          padding: 1rem 1.25rem; display: flex; align-items: center; gap: 10px;
          border-bottom: 1px solid rgba(255,255,255,0.05);
        }

        .rx-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

        .rx-doctor { font-size: 0.9rem; font-weight: 700; color: rgba(255,255,255,0.85); }
        .rx-specialty { font-size: 0.7rem; color: rgba(255,255,255,0.3); }
        .rx-date { margin-left: auto; font-size: 0.65rem; color: rgba(255,255,255,0.2); }

        .rx-body { padding: 0.9rem; }

        .rx-med {
          display: flex; align-items: center; gap: 8px; padding: 6px 0;
          border-bottom: 1px solid rgba(255,255,255,0.03); font-size: 0.82rem;
        }
        .rx-med:last-child { border-bottom: none; }

        .med-dot-sm { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }

        /* Cross-interaction */
        .cross-warn {
          border: 1px solid rgba(245,158,11,0.25); background: rgba(245,158,11,0.06);
          border-radius: 14px; padding: 1.25rem; margin-bottom: 2rem; animation: fadeInUp 0.5s ease both;
        }

        .cross-title { font-size: 0.88rem; font-weight: 700; color: "#f59e0b"; margin-bottom: 0.5rem; }
        .cross-drugs { display: flex; align-items: center; gap: 8px; margin-bottom: 0.75rem; font-size: 0.84rem; }
        .cross-separator { color: rgba(255,255,255,0.2); }

        .source-tag {
          font-size: 0.62rem; fontWeight: 700; padding: "2px 7px"; borderRadius: 4;
          letterSpacing: "0.06em";
        }

        /* Merged schedule */
        .merged-title {
          font-size: 0.78rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
          color: rgba(255,255,255,0.25); margin-bottom: 1rem;
        }

        .merged-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 2rem; }

        .merged-slot {
          background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
          border-radius: 14px; overflow: hidden; animation: fadeInUp 0.5s ease both;
        }

        .slot-head {
          padding: 0.75rem 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.05);
          font-size: 0.78rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
          color: rgba(255,255,255,0.4); display: flex; align-items: center; gap: 6px;
        }

        .merged-med-row {
          display: flex; align-items: center; gap: 8px; padding: 8px 1.1rem;
          border-bottom: 1px solid rgba(255,255,255,0.03); font-size: 0.82rem;
          transition: all 0.2s;
        }
        .merged-med-row:hover { background: rgba(255,255,255,0.02); }
        .merged-med-row:last-child { border-bottom: none; }

        .merged-med-name { color: rgba(255,255,255,0.8); font-weight: 500; flex: 1; }
        .merged-med-dose { color: rgba(255,255,255,0.35); font-size: 0.75rem; }
        .merged-source-chip {
          font-size: 0.58rem; fontWeight: 700; border-radius: 4; padding: "2px 6px";
        }

        .export-row { display: flex; gap: 10px; flex-wrap: wrap; }

        .btn-ex {
          display: inline-flex; align-items: center; gap: 6px;
          font-family: 'Outfit', sans-serif; font-size: 0.82rem; font-weight: 600;
          padding: 9px 18px; border-radius: 9px; cursor: pointer; border: 1px solid; transition: all 0.2s; text-decoration: none;
        }

        @keyframes fadeInUp { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }
      `}</style>

      <div className="multi-page">
        <div className="multi-container">
          <h1 className="page-title">Multi-Prescription Mode</h1>
          <p className="page-sub">Upload prescriptions from multiple doctors. We detect cross-prescription drug interactions no individual doctor can see.</p>

          {state === "upload" && (
            <>
              <div className="upload-area">
                {[1, 2, 3, 4].map((n) => (
                  <div key={n} className="upload-slot">
                    <span className="slot-icon">📋</span>
                    <div className="slot-title">Prescription #{n}</div>
                    <div className="slot-hint">Click to upload or drag & drop</div>
                  </div>
                ))}
              </div>
              <button className="analyze-btn" onClick={() => setState("results")}>
                🔍 Analyze All Prescriptions Together (Demo — 2 loaded)
              </button>
            </>
          )}

          {state === "results" && (
            <>
              {/* Prescription cards */}
              <div className="rx-grid">
                {PRESCRIPTIONS.map((rx, idx) => (
                  <div className="rx-card" key={rx.id} style={{ border: `1px solid ${rx.color}22`, animationDelay: `${idx * 0.1}s` }}>
                    <div className="rx-header">
                      <div className="rx-dot" style={{ background: rx.color, boxShadow: `0 0 8px ${rx.color}60` }} />
                      <div>
                        <div className="rx-doctor">{rx.doctor}</div>
                        <div className="rx-specialty">{rx.specialty}</div>
                      </div>
                      <div className="rx-date">{rx.date}</div>
                    </div>
                    <div className="rx-body">
                      {rx.medicines.map((med) => (
                        <div className="rx-med" key={med.name}>
                          <div className="med-dot-sm" style={{ background: rx.color }} />
                          <span style={{ color: "rgba(255,255,255,0.75)", fontWeight: 500 }}>{med.name}</span>
                          <span style={{ color: "rgba(255,255,255,0.35)", fontSize: "0.75rem", marginLeft: "auto" }}>{med.dose} · {med.freq}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* Cross-prescription interaction warning */}
              <div style={{ marginBottom: "0.5rem", fontSize: "0.72rem", fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: "rgba(255,255,255,0.25)" }}>
                Cross-Prescription Interactions
              </div>
              {CROSS_INTERACTIONS.map((interaction, i) => (
                <div key={i} className="cross-warn" style={{ animationDelay: `${i * 0.08}s` }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                    <span style={{ fontSize: "1.1rem" }}>⚠️</span>
                    <span style={{ fontSize: "0.65rem", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", color: "#f59e0b", background: "rgba(245,158,11,0.12)", border: "1px solid rgba(245,158,11,0.25)", borderRadius: 4, padding: "2px 8px" }}>
                      MODERATE · CROSS-PRESCRIPTION
                    </span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10, flexWrap: "wrap" }}>
                    <span style={{ fontWeight: 700, color: "#00c8ff" }}>{interaction.drug1}</span>
                    <span style={{ fontSize: "0.65rem", color: "#00c8ff", background: "rgba(0,200,255,0.08)", border: "1px solid rgba(0,200,255,0.2)", borderRadius: 4, padding: "1px 7px" }}>{interaction.rx1}</span>
                    <span style={{ color: "rgba(255,255,255,0.25)", fontSize: "1.1rem" }}>↔</span>
                    <span style={{ fontWeight: 700, color: "#00ffb4" }}>{interaction.drug2}</span>
                    <span style={{ fontSize: "0.65rem", color: "#00ffb4", background: "rgba(0,255,180,0.08)", border: "1px solid rgba(0,255,180,0.2)", borderRadius: 4, padding: "1px 7px" }}>{interaction.rx2}</span>
                  </div>
                  <p style={{ color: "rgba(255,255,255,0.55)", fontSize: "0.82rem", lineHeight: 1.7, marginBottom: 10 }}>{interaction.desc}</p>
                  <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 8, padding: "9px 14px" }}>
                    <span style={{ fontSize: "0.65rem", fontWeight: 700, color: "#f59e0b", letterSpacing: "0.1em", textTransform: "uppercase" }}>Recommended Action</span>
                    <p style={{ color: "rgba(255,255,255,0.6)", fontSize: "0.8rem", marginTop: 4, lineHeight: 1.6 }}>{interaction.action}</p>
                  </div>
                </div>
              ))}

              {/* Merged Schedule */}
              <div className="merged-title">Unified Medication Schedule (All Prescriptions)</div>
              <div className="merged-grid">
                {Object.entries(MERGED_SCHEDULE).map(([slot, meds], idx) => (
                  <div className="merged-slot" key={slot} style={{ animationDelay: `${idx * 0.08}s` }}>
                    <div className="slot-head">
                      <span>{slot === "Morning" ? "🌅" : "🌙"}</span>
                      {slot}
                      <span style={{ marginLeft: "auto", fontSize: "0.65rem", background: "rgba(255,255,255,0.06)", borderRadius: 8, padding: "2px 8px", color: "rgba(255,255,255,0.25)" }}>
                        {meds.length} medicines
                      </span>
                    </div>
                    {meds.map((med, i) => (
                      <div key={i} className="merged-med-row">
                        <div style={{ width: 8, height: 8, borderRadius: "50%", background: med.color, flexShrink: 0 }} />
                        <span className="merged-med-name">
                          {med.flag && <span style={{ marginRight: 4 }}>{med.flag}</span>}
                          {med.name}
                        </span>
                        <span className="merged-med-dose">{med.dose}</span>
                        <span style={{ fontSize: "0.58rem", fontWeight: 700, color: med.color, background: `${med.color}12`, border: `1px solid ${med.color}25`, borderRadius: 4, padding: "1px 5px", flexShrink: 0 }}>
                          {med.source.split(" ")[1]}
                        </span>
                      </div>
                    ))}
                  </div>
                ))}
              </div>

              {/* Export row */}
              <div className="export-row">
                <a href="#" className="btn-ex" style={{ borderColor: "rgba(0,255,180,0.2)", color: "#00ffb4", background: "rgba(0,255,180,0.04)" }}>
                  📄 Export Merged PDF
                </a>
                <a href="#" className="btn-ex" style={{ borderColor: "rgba(167,139,250,0.2)", color: "#a78bfa", background: "rgba(167,139,250,0.04)" }}>
                  📆 Export to Calendar
                </a>
                <button className="btn-ex" style={{ borderColor: "rgba(255,255,255,0.1)", color: "rgba(255,255,255,0.4)", background: "transparent", cursor: "pointer" }} onClick={() => setState("upload")}>
                  ↩ Upload New
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}
