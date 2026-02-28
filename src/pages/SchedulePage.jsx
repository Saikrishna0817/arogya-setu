import { useState } from "react";

const SCHEDULE_DATA = {
  Morning: [
    { name: "Metformin", dose: "500mg", food: "After food", days: "30", daysLeft: 23, color: "#00ffb4", tag: "Diabetes" },
    { name: "Atorvastatin", dose: "10mg", food: "Any time", days: "30", daysLeft: 23, color: "#a78bfa", tag: "Cholesterol", note: "Alternatively can be taken at night" },
    { name: "Pantoprazole", dose: "40mg", food: "Before food", days: "14", daysLeft: 7, color: "#f59e0b", tag: "Acidity" },
  ],
  Afternoon: [
    { name: "Metformin", dose: "500mg", food: "After food", days: "30", daysLeft: 23, color: "#00ffb4", tag: "Diabetes" },
  ],
  Evening: [],
  Night: [
    { name: "Amlodipine", dose: "5mg", food: "Any time", days: "30", daysLeft: 23, color: "#00c8ff", tag: "BP", note: "Take at the same time every night" },
  ],
};

const slotIcons = {
  Morning: "🌅",
  Afternoon: "☀️",
  Evening: "🌇",
  Night: "🌙",
};

function MedPill({ med }) {
  return (
    <div style={{
      background: `${med.color}10`,
      border: `1px solid ${med.color}28`,
      borderRadius: 10,
      padding: "10px 12px",
      marginBottom: 8,
      transition: "all 0.2s",
      cursor: "default",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8, marginBottom: 6 }}>
        <div>
          <span style={{ fontWeight: 600, fontSize: "0.88rem", color: "rgba(255,255,255,0.9)", display: "block" }}>{med.name}</span>
          <span style={{ fontSize: "0.7rem", color: med.color, fontWeight: 600 }}>{med.dose}</span>
        </div>
        <span style={{
          fontSize: "0.6rem", fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase",
          background: `${med.color}18`, color: med.color, borderRadius: 4, padding: "2px 7px", flexShrink: 0
        }}>{med.tag}</span>
      </div>

      <div style={{ display: "flex", gap: 5, flexWrap: "wrap", marginBottom: med.note ? 6 : 0 }}>
        <span style={{ fontSize: "0.68rem", background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 5, padding: "2px 7px", color: "rgba(255,255,255,0.45)" }}>
          🍽️ {med.food}
        </span>
        <span style={{ fontSize: "0.68rem", background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 5, padding: "2px 7px", color: "rgba(255,255,255,0.45)" }}>
          📅 Day {parseInt(med.days) - med.daysLeft + 1}/{med.days}
        </span>
      </div>

      {/* Progress bar */}
      <div style={{ height: 3, background: "rgba(255,255,255,0.06)", borderRadius: 2, marginTop: 8, overflow: "hidden" }}>
        <div style={{
          height: "100%",
          width: `${((parseInt(med.days) - med.daysLeft) / parseInt(med.days)) * 100}%`,
          background: `linear-gradient(90deg, ${med.color}, ${med.color}88)`,
          borderRadius: 2,
        }} />
      </div>

      {med.note && (
        <p style={{ fontSize: "0.68rem", color: "rgba(255,255,255,0.3)", marginTop: 6, fontStyle: "italic" }}>📌 {med.note}</p>
      )}
    </div>
  );
}

export default function SchedulePage() {
  const [activeDay, setActiveDay] = useState("Today");
  const [view, setView] = useState("grid"); // grid | list

  const days = ["Today", "Tomorrow", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"];

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Outfit:wght@300;400;500;600;700&display=swap');
        * { box-sizing: border-box; }
        body { background: #03030a; color: #fff; font-family: 'Outfit', sans-serif; }

        .sched-page { min-height: 100vh; padding: 90px 2rem 4rem; background: #03030a; }
        .sched-container { max-width: 1100px; margin: 0 auto; }

        .page-title {
          font-family: 'Cinzel', serif; font-size: 2rem; font-weight: 700;
          background: linear-gradient(90deg, #a78bfa, #00c8ff, #00ffb4);
          -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
          margin-bottom: 0.4rem;
        }
        .page-sub { color: rgba(255,255,255,0.35); font-size: 0.9rem; margin-bottom: 2rem; }

        .top-bar {
          display: flex; align-items: center; justify-content: space-between;
          gap: 1rem; flex-wrap: wrap; margin-bottom: 2rem;
        }

        .day-tabs { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 4px; }

        .day-tab {
          font-family: 'Outfit', sans-serif; font-size: 0.78rem; font-weight: 600;
          padding: 7px 16px; border-radius: 20px; cursor: pointer; white-space: nowrap;
          border: 1px solid rgba(255,255,255,0.08); background: transparent; color: rgba(255,255,255,0.4);
          transition: all 0.2s;
        }
        .day-tab:hover { border-color: rgba(167,139,250,0.3); color: #a78bfa; }
        .day-tab.active { background: rgba(167,139,250,0.12); border-color: rgba(167,139,250,0.3); color: #a78bfa; }

        .export-row { display: flex; gap: 8px; }

        .btn-export {
          display: inline-flex; align-items: center; gap: 6px;
          font-family: 'Outfit', sans-serif; font-size: 0.78rem; font-weight: 600;
          padding: 7px 14px; border-radius: 8px; cursor: pointer; border: 1px solid rgba(255,255,255,0.1);
          background: transparent; color: rgba(255,255,255,0.5); transition: all 0.2s; text-decoration: none;
        }
        .btn-export:hover { border-color: rgba(167,139,250,0.3); color: #a78bfa; background: rgba(167,139,250,0.04); }

        .btn-export.green { border-color: rgba(0,255,180,0.2); color: #00ffb4; background: rgba(0,255,180,0.04); }
        .btn-export.green:hover { box-shadow: 0 0 20px rgba(0,255,180,0.2); }

        .sched-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 1.25rem;
        }

        .sched-col {
          background: rgba(255,255,255,0.02);
          border: 1px solid rgba(255,255,255,0.06);
          border-radius: 16px;
          overflow: hidden;
          animation: fadeInUp 0.5s ease both;
        }

        .col-header {
          display: flex; align-items: center; gap: 8px;
          padding: 1rem 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.05);
        }

        .col-title {
          font-size: 0.82rem; font-weight: 700; letter-spacing: 0.08em;
          text-transform: uppercase; color: rgba(255,255,255,0.5);
        }

        .col-count {
          margin-left: auto; font-size: 0.65rem; font-weight: 700;
          background: rgba(255,255,255,0.06); border-radius: 10px;
          padding: 2px 8px; color: rgba(255,255,255,0.3);
        }

        .col-body { padding: 0.9rem; }

        .empty-slot {
          text-align: center; padding: 2rem 1rem;
          color: rgba(255,255,255,0.15); font-size: 0.8rem;
        }

        .empty-slot .empty-icon { font-size: 1.5rem; display: block; margin-bottom: 6px; opacity: 0.4; }

        /* Summary strip */
        .summary-strip {
          display: grid; grid-template-columns: repeat(4, 1fr);
          gap: 1rem; margin-bottom: 2rem;
        }

        .sum-item {
          background: rgba(255,255,255,0.02);
          border: 1px solid rgba(255,255,255,0.05);
          border-radius: 10px; padding: 0.9rem; text-align: center;
        }

        .sum-big { font-family: 'Cinzel', serif; font-size: 1.6rem; font-weight: 700; display: block; margin-bottom: 3px; }
        .sum-tiny { font-size: 0.68rem; letter-spacing: 0.1em; text-transform: uppercase; color: rgba(255,255,255,0.3); }

        .whatsapp-btn {
          display: flex; align-items: center; justify-content: center; gap: 8px;
          background: rgba(37,211,102,0.08); border: 1px solid rgba(37,211,102,0.2);
          border-radius: 10px; padding: 12px; color: #25d366;
          font-family: 'Outfit', sans-serif; font-size: 0.85rem; font-weight: 600;
          cursor: pointer; transition: all 0.25s; margin-top: 1.5rem; text-decoration: none; width: 100%;
        }
        .whatsapp-btn:hover { background: rgba(37,211,102,0.12); box-shadow: 0 0 20px rgba(37,211,102,0.15); }

        @keyframes fadeInUp { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }

        @media (max-width: 900px) {
          .sched-grid { grid-template-columns: repeat(2, 1fr); }
          .summary-strip { grid-template-columns: repeat(2, 1fr); }
        }
        @media (max-width: 500px) {
          .sched-grid { grid-template-columns: 1fr; }
        }
      `}</style>

      <div className="sched-page">
        <div className="sched-container">
          <h1 className="page-title">Medication Schedule</h1>
          <p className="page-sub">Your personalized daily medicine schedule — Morning, Afternoon, Evening, Night.</p>

          {/* Summary strip */}
          <div className="summary-strip">
            <div className="sum-item">
              <span className="sum-big" style={{ background: "linear-gradient(90deg,#00ffb4,#00c8ff)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>4</span>
              <span className="sum-tiny">Total medicines</span>
            </div>
            <div className="sum-item">
              <span className="sum-big" style={{ background: "linear-gradient(90deg,#a78bfa,#f472b6)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>5</span>
              <span className="sum-tiny">Doses today</span>
            </div>
            <div className="sum-item">
              <span className="sum-big" style={{ background: "linear-gradient(90deg,#f59e0b,#ef4444)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>7</span>
              <span className="sum-tiny">Days remaining (min)</span>
            </div>
            <div className="sum-item">
              <span className="sum-big" style={{ background: "linear-gradient(90deg,#00c8ff,#a78bfa)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>3</span>
              <span className="sum-tiny">Refills needed soon</span>
            </div>
          </div>

          {/* Top bar */}
          <div className="top-bar">
            <div className="day-tabs">
              {days.map((d) => (
                <button key={d} className={`day-tab ${activeDay === d ? "active" : ""}`} onClick={() => setActiveDay(d)}>{d}</button>
              ))}
            </div>

            <div className="export-row">
              <button className="btn-export">📄 PDF</button>
              <button className="btn-export">📆 iCal</button>
              <button className="btn-export green">▶ Voice</button>
            </div>
          </div>

          {/* Schedule grid */}
          <div className="sched-grid">
            {Object.entries(SCHEDULE_DATA).map(([slot, meds], idx) => (
              <div className="sched-col" key={slot} style={{ animationDelay: `${idx * 0.07}s` }}>
                <div className="col-header">
                  <span style={{ fontSize: "1.1rem" }}>{slotIcons[slot]}</span>
                  <span className="col-title">{slot}</span>
                  <span className="col-count">{meds.length}</span>
                </div>
                <div className="col-body">
                  {meds.length === 0 ? (
                    <div className="empty-slot">
                      <span className="empty-icon">💤</span>
                      No medicines
                    </div>
                  ) : (
                    meds.map((med, i) => <MedPill key={i} med={med} />)
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* WhatsApp share */}
          <a href="#" className="whatsapp-btn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="#25d366"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
            Share schedule on WhatsApp
          </a>
        </div>
      </div>
    </>
  );
}
