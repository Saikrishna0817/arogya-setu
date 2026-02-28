import { useState } from "react";

const VAULT_DATA = [
  {
    id: 1,
    date: "Feb 25, 2026",
    doctor: "Dr. Ramesh Reddy",
    hospital: "Apollo Clinic, Hyderabad",
    type: "Cardiology",
    medicines: ["Amlodipine 5mg", "Atorvastatin 10mg", "Aspirin 75mg"],
    tags: ["BP", "Cholesterol"],
    days: 3,
    color: "#00c8ff",
  },
  {
    id: 2,
    date: "Jan 12, 2026",
    doctor: "Dr. Sunita Sharma",
    hospital: "KIMS Hospital, Secunderabad",
    type: "Endocrinology",
    medicines: ["Metformin 500mg", "Glimepiride 1mg"],
    tags: ["Diabetes"],
    days: 49,
    color: "#00ffb4",
  },
  {
    id: 3,
    date: "Dec 5, 2025",
    doctor: "Dr. Anjali Nair",
    hospital: "City Health Center",
    type: "General",
    medicines: ["Pantoprazole 40mg", "Domperidone 10mg", "ORS Sachets"],
    tags: ["Acidity", "GI"],
    days: 88,
    color: "#a78bfa",
  },
  {
    id: 4,
    date: "Nov 18, 2025",
    doctor: "Dr. Venkat Rao",
    hospital: "Govt. Primary Health Center",
    type: "General",
    medicines: ["Paracetamol 500mg", "Cetirizine 10mg", "Amoxicillin 500mg"],
    tags: ["Fever", "Allergy"],
    days: 102,
    color: "#f59e0b",
  },
];

const ALLERGEN_REGISTRY = [
  { drug: "Penicillin", severity: "critical", reaction: "Anaphylaxis" },
  { drug: "Sulfa drugs", severity: "moderate", reaction: "Skin rash, urticaria" },
];

function VaultCard({ item, onCompare, isSelected }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div style={{
      background: isSelected ? `${item.color}08` : "rgba(255,255,255,0.02)",
      border: `1px solid ${isSelected ? item.color + "35" : "rgba(255,255,255,0.06)"}`,
      borderRadius: 14,
      padding: "1.25rem",
      marginBottom: "1rem",
      transition: "all 0.25s",
      animation: "fadeInUp 0.5s ease both",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "1rem", marginBottom: 10 }}>
        <div>
          <div style={{ fontSize: "0.9rem", fontWeight: 700, color: "rgba(255,255,255,0.9)", marginBottom: 4 }}>
            {item.doctor}
          </div>
          <div style={{ fontSize: "0.75rem", color: "rgba(255,255,255,0.35)" }}>{item.hospital}</div>
        </div>
        <div style={{ textAlign: "right", flexShrink: 0 }}>
          <div style={{ fontSize: "0.72rem", fontWeight: 700, color: item.color, background: `${item.color}15`, border: `1px solid ${item.color}25`, borderRadius: 6, padding: "2px 9px", marginBottom: 5 }}>
            {item.type}
          </div>
          <div style={{ fontSize: "0.68rem", color: "rgba(255,255,255,0.25)" }}>📅 {item.date}</div>
        </div>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginBottom: 10 }}>
        {item.medicines.map((m) => (
          <span key={m} style={{ fontSize: "0.72rem", background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 6, padding: "3px 9px", color: "rgba(255,255,255,0.5)" }}>
            💊 {m}
          </span>
        ))}
      </div>

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
        <div style={{ display: "flex", gap: 5 }}>
          {item.tags.map((t) => (
            <span key={t} style={{ fontSize: "0.62rem", fontWeight: 700, letterSpacing: "0.08em", color: item.color, textTransform: "uppercase" }}>{t}</span>
          ))}
          <span style={{ fontSize: "0.65rem", color: "rgba(255,255,255,0.2)", marginLeft: 4 }}>• {item.days} days ago</span>
        </div>

        <div style={{ display: "flex", gap: 6 }}>
          <button
            onClick={() => onCompare(item.id)}
            style={{
              fontSize: "0.7rem", fontWeight: 600, padding: "4px 10px", borderRadius: 6,
              border: `1px solid ${isSelected ? item.color + "60" : "rgba(255,255,255,0.1)"}`,
              background: isSelected ? `${item.color}15` : "transparent",
              color: isSelected ? item.color : "rgba(255,255,255,0.35)",
              cursor: "pointer", fontFamily: "Outfit, sans-serif", transition: "all 0.2s",
            }}
          >
            {isSelected ? "✓ Selected" : "Compare"}
          </button>
          <button
            onClick={() => setExpanded(!expanded)}
            style={{
              fontSize: "0.7rem", fontWeight: 600, padding: "4px 10px", borderRadius: 6,
              border: "1px solid rgba(255,255,255,0.1)",
              background: "transparent", color: "rgba(255,255,255,0.35)",
              cursor: "pointer", fontFamily: "Outfit, sans-serif",
            }}
          >
            {expanded ? "▲" : "▼"}
          </button>
        </div>
      </div>

      {expanded && (
        <div style={{ borderTop: "1px solid rgba(255,255,255,0.05)", marginTop: 12, paddingTop: 12, animation: "fadeIn 0.3s ease" }}>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button style={{ fontSize: "0.75rem", padding: "6px 14px", borderRadius: 8, border: "1px solid rgba(255,255,255,0.1)", background: "transparent", color: "rgba(255,255,255,0.5)", cursor: "pointer", fontFamily: "Outfit, sans-serif" }}>
              📄 Download PDF
            </button>
            <button style={{ fontSize: "0.75rem", padding: "6px 14px", borderRadius: 8, border: "1px solid rgba(167,139,250,0.2)", background: "rgba(167,139,250,0.05)", color: "#a78bfa", cursor: "pointer", fontFamily: "Outfit, sans-serif" }}>
              🔄 Re-process
            </button>
            <button style={{ fontSize: "0.75rem", padding: "6px 14px", borderRadius: 8, border: "1px solid rgba(239,68,68,0.15)", background: "transparent", color: "rgba(239,68,68,0.5)", cursor: "pointer", fontFamily: "Outfit, sans-serif" }}>
              🗑 Delete
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function VaultPage() {
  const [search, setSearch] = useState("");
  const [compareIds, setCompareIds] = useState([]);
  const [tab, setTab] = useState("history"); // history | allergies | export

  const filtered = VAULT_DATA.filter((v) =>
    v.doctor.toLowerCase().includes(search.toLowerCase()) ||
    v.medicines.some((m) => m.toLowerCase().includes(search.toLowerCase())) ||
    v.tags.some((t) => t.toLowerCase().includes(search.toLowerCase()))
  );

  const toggleCompare = (id) => {
    if (compareIds.includes(id)) {
      setCompareIds(compareIds.filter((c) => c !== id));
    } else if (compareIds.length < 2) {
      setCompareIds([...compareIds, id]);
    }
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Outfit:wght@300;400;500;600;700&display=swap');
        * { box-sizing: border-box; }
        body { background: #03030a; color: #fff; font-family: 'Outfit', sans-serif; }

        .vault-page { min-height: 100vh; padding: 90px 2rem 4rem; background: #03030a; }
        .vault-container { max-width: 900px; margin: 0 auto; }

        .page-title {
          font-family: 'Cinzel', serif; font-size: 2rem; font-weight: 700;
          background: linear-gradient(90deg, #00c8ff, #a78bfa, #f472b6);
          -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
          margin-bottom: 0.4rem;
        }
        .page-sub { color: rgba(255,255,255,0.35); font-size: 0.9rem; margin-bottom: 2rem; }

        .tab-bar { display: flex; gap: 4px; margin-bottom: 2rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0; }

        .tab-btn {
          font-family: 'Outfit', sans-serif; font-size: 0.82rem; font-weight: 600;
          padding: 8px 18px; border: none; background: transparent; color: rgba(255,255,255,0.35);
          cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px; transition: all 0.2s;
        }
        .tab-btn.active { color: #00c8ff; border-bottom-color: #00c8ff; }
        .tab-btn:hover { color: rgba(255,255,255,0.7); }

        .search-bar {
          width: 100%; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
          border-radius: 10px; padding: 11px 16px; color: #fff;
          font-family: 'Outfit', sans-serif; font-size: 0.88rem; outline: none;
          transition: all 0.2s; margin-bottom: 1.5rem;
        }
        .search-bar:focus { border-color: rgba(0,200,255,0.3); background: rgba(0,200,255,0.02); }
        .search-bar::placeholder { color: rgba(255,255,255,0.2); }

        .vault-stats { display: grid; grid-template-columns: repeat(3,1fr); gap: 1rem; margin-bottom: 2rem; }

        .vs-card {
          background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05);
          border-radius: 10px; padding: 1rem; text-align: center;
        }
        .vs-num { font-family: 'Cinzel', serif; font-size: 1.8rem; font-weight: 700; display: block; margin-bottom: 3px; }
        .vs-lbl { font-size: 0.68rem; letter-spacing: 0.1em; text-transform: uppercase; color: rgba(255,255,255,0.3); }

        .compare-banner {
          background: rgba(167,139,250,0.08); border: 1px solid rgba(167,139,250,0.2);
          border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 1.5rem;
          display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
          color: #a78bfa; font-size: 0.84rem; font-weight: 500;
          animation: fadeIn 0.3s ease;
        }

        .compare-cta {
          background: #a78bfa; color: #000; font-family: 'Outfit', sans-serif;
          font-size: 0.8rem; font-weight: 700; padding: 7px 16px; border: none;
          border-radius: 8px; cursor: pointer; transition: all 0.2s;
        }
        .compare-cta:hover { box-shadow: 0 0 20px rgba(167,139,250,0.4); }

        .allergy-card {
          background: rgba(239,68,68,0.06); border: 1px solid rgba(239,68,68,0.18);
          border-radius: 12px; padding: 1.1rem 1.25rem; display: flex;
          align-items: center; gap: 14px; margin-bottom: 0.75rem; animation: fadeInUp 0.5s ease both;
        }
        .allergy-sev {
          font-size: 0.62rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
          border-radius: 4px; padding: 3px 8px;
        }
        .allergy-drug { font-weight: 700; font-size: 0.9rem; color: rgba(255,255,255,0.85); }
        .allergy-reaction { font-size: 0.77rem; color: rgba(255,255,255,0.4); margin-top: 2px; }

        .pin-lock {
          display: flex; align-items: center; gap: 8px;
          background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05);
          border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 2rem;
          color: rgba(255,255,255,0.25); font-size: 0.8rem;
        }

        @keyframes fadeInUp { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }
        @keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
      `}</style>

      <div className="vault-page">
        <div className="vault-container">
          <h1 className="page-title">Prescription Vault</h1>
          <p className="page-sub">Encrypted prescription history for chronic patients. AES-256 encrypted, stored locally.</p>

          <div className="pin-lock">
            <span>🔐</span> Vault is PIN-protected. All data is encrypted on your device. No data leaves without your consent.
          </div>

          {/* Stats */}
          <div className="vault-stats">
            <div className="vs-card">
              <span className="vs-num" style={{ background: "linear-gradient(90deg,#00c8ff,#a78bfa)", WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent", backgroundClip:"text" }}>
                {VAULT_DATA.length}
              </span>
              <span className="vs-lbl">Prescriptions saved</span>
            </div>
            <div className="vs-card">
              <span className="vs-num" style={{ background: "linear-gradient(90deg,#a78bfa,#f472b6)", WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent", backgroundClip:"text" }}>
                12
              </span>
              <span className="vs-lbl">Unique medicines</span>
            </div>
            <div className="vs-card">
              <span className="vs-num" style={{ background: "linear-gradient(90deg,#ef4444,#f59e0b)", WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent", backgroundClip:"text" }}>
                {ALLERGEN_REGISTRY.length}
              </span>
              <span className="vs-lbl">Known allergies</span>
            </div>
          </div>

          {/* Tabs */}
          <div className="tab-bar">
            {["history", "allergies", "export"].map((t) => (
              <button key={t} className={`tab-btn ${tab === t ? "active" : ""}`} onClick={() => setTab(t)}>
                {t === "history" ? "📋 History" : t === "allergies" ? "⚠️ Allergy Registry" : "📤 Export"}
              </button>
            ))}
          </div>

          {tab === "history" && (
            <>
              <input
                className="search-bar"
                placeholder="🔍  Search by doctor, medicine, or condition..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />

              {compareIds.length === 2 && (
                <div className="compare-banner">
                  <span>2 prescriptions selected — compare side by side</span>
                  <button className="compare-cta" onClick={() => setCompareIds([])}>
                    🔍 Compare Now
                  </button>
                </div>
              )}

              {compareIds.length === 1 && (
                <div className="compare-banner">
                  <span>Select one more prescription to compare</span>
                  <button style={{ fontSize: "0.75rem", background: "none", border: "none", color: "rgba(167,139,250,0.5)", cursor: "pointer" }} onClick={() => setCompareIds([])}>
                    Cancel
                  </button>
                </div>
              )}

              {filtered.map((item) => (
                <VaultCard
                  key={item.id}
                  item={item}
                  onCompare={toggleCompare}
                  isSelected={compareIds.includes(item.id)}
                />
              ))}

              {filtered.length === 0 && (
                <div style={{ textAlign: "center", padding: "3rem", color: "rgba(255,255,255,0.2)", fontSize: "0.88rem" }}>
                  No prescriptions found for "{search}"
                </div>
              )}
            </>
          )}

          {tab === "allergies" && (
            <div>
              <p style={{ color: "rgba(255,255,255,0.3)", fontSize: "0.82rem", marginBottom: "1.5rem" }}>
                Every new prescription is cross-checked against this allergy registry automatically.
              </p>

              {ALLERGEN_REGISTRY.map((a, i) => (
                <div key={i} className="allergy-card" style={{ animationDelay: `${i * 0.08}s` }}>
                  <span style={{ fontSize: "1.5rem" }}>🚫</span>
                  <div style={{ flex: 1 }}>
                    <div className="allergy-drug">{a.drug}</div>
                    <div className="allergy-reaction">{a.reaction}</div>
                  </div>
                  <span className="allergy-sev" style={{
                    color: a.severity === "critical" ? "#ef4444" : "#f59e0b",
                    background: a.severity === "critical" ? "rgba(239,68,68,0.1)" : "rgba(245,158,11,0.1)",
                    border: `1px solid ${a.severity === "critical" ? "rgba(239,68,68,0.25)" : "rgba(245,158,11,0.25)"}`,
                  }}>
                    {a.severity}
                  </span>
                </div>
              ))}

              <button style={{
                marginTop: "1rem", width: "100%", padding: "11px", border: "1px dashed rgba(0,255,180,0.2)",
                background: "transparent", borderRadius: 10, color: "rgba(0,255,180,0.5)",
                fontFamily: "Outfit, sans-serif", fontSize: "0.85rem", cursor: "pointer", transition: "all 0.2s",
              }}>
                + Add Allergy
              </button>
            </div>
          )}

          {tab === "export" && (
            <div>
              <p style={{ color: "rgba(255,255,255,0.3)", fontSize: "0.82rem", marginBottom: "1.5rem" }}>
                Generate a complete medication history PDF for specialist consultations.
              </p>
              {[
                { icon: "📄", label: "Complete Medicine History PDF", sub: "All prescriptions, medicines, dates", color: "#00ffb4" },
                { icon: "📊", label: "Chronic Condition Summary", sub: "Condition-wise medicine timeline", color: "#00c8ff" },
                { icon: "🗑", label: "Delete All My Data", sub: "Immediate, irreversible removal", color: "#ef4444" },
              ].map((item, i) => (
                <div key={i} style={{
                  display: "flex", alignItems: "center", gap: 16, padding: "1.1rem 1.25rem",
                  background: "rgba(255,255,255,0.02)", border: `1px solid ${item.color}18`,
                  borderRadius: 12, marginBottom: 10, cursor: "pointer", transition: "all 0.2s",
                  animation: "fadeInUp 0.5s ease both", animationDelay: `${i * 0.07}s`,
                }}>
                  <span style={{ fontSize: "1.4rem" }}>{item.icon}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: "0.88rem", color: item.color, marginBottom: 3 }}>{item.label}</div>
                    <div style={{ fontSize: "0.73rem", color: "rgba(255,255,255,0.3)" }}>{item.sub}</div>
                  </div>
                  <span style={{ color: "rgba(255,255,255,0.2)" }}>→</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
