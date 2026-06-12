import { motion } from "framer-motion";
import { Clock, RefreshCw } from "lucide-react";
import { t } from "../utils/lang";

export default function History({ history = [], onViewAttempt, onRetake, lang }) {
  if (!history || history.length === 0) {
    return (
      <div className="view fade-in" data-testid="history-view" style={{ background: "var(--paper)" }}>
        <div className="container-md screen-inner" style={{ paddingTop: 32 }}>
          <div className="reveal show" style={{ marginBottom: 28 }}>
            <span className="pill">{lang === "bn" ? "ইতিহাস" : "History"}</span>
            <h1 className="display" style={{ fontSize: "clamp(34px, 5vw, 52px)", marginTop: 14, marginBottom: 12 }}>
              {lang === "bn" ? "পূর্ববর্তী পরীক্ষাসমূহ" : "Previous Sessions"}
            </h1>
            <p style={{ fontSize: 15, color: "var(--muted)" }}>
              {lang === "bn" ? "এখনো কোনো পরীক্ষা সম্পন্ন করা হয়নি।" : "No exams taken yet."}
            </p>
          </div>
          <div style={{ display: "flex", justifyContent: "center", marginTop: 24 }}>
            <button className="btn btn-primary" onClick={onRetake}>
              {lang === "bn" ? "প্রথম পরীক্ষা দিন →" : "Take Your First Exam →"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Calculate history stats
  const scores = history.map(h => h.readiness?.score ?? h.score ?? 0);
  const avg = scores.length ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
  const best = Math.max(...scores, 0);
  const latest = scores[0] || 0;
  const trend = scores.length >= 2 ? (scores[0] >= scores[1] ? "up" : "down") : "stable";

  return (
    <div className="view fade-in" data-testid="history-view" style={{ background: "var(--paper)" }}>
      <div className="container-md screen-inner" style={{ paddingTop: 32 }}>
        
        {/* Header */}
        <div className="reveal show" style={{ marginBottom: 28 }}>
          <span className="pill" style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
            <Clock size={13} />
            {lang === "bn" ? "ইতিহাস" : "History"}
          </span>
          <h1 className="display" style={{ fontSize: "clamp(34px, 5vw, 52px)", marginTop: 14, marginBottom: 12 }}>
            {lang === "bn" ? "পূর্ববর্তী পরীক্ষাসমূহ" : "Previous Sessions"}
          </h1>
          <p style={{ fontSize: 15, color: "var(--muted)", lineHeight: 1.6 }}>
            {lang === "bn"
              ? `মোট ${history.length}টি সেশন সম্পন্ন হয়েছে। প্রতিটি সেশন আপনার প্রস্তুতি বিশ্লেষণ করতে সাহায্য করে।`
              : `${history.length} session${history.length > 1 ? "s" : ""} completed. Track your cognitive evolution over time.`}
          </p>
        </div>

        {/* Summary Stats Cards */}
        <div className="summary-cards" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 16, marginBottom: 32 }}>
          <div className="card summary-card" style={{ padding: 22, background: "var(--card)" }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", marginBottom: 8 }}>
              {lang === "bn" ? "মোট সেশন" : "Total Sessions"}
            </div>
            <div className="display" style={{ fontSize: 32, fontWeight: 600, color: "var(--brand)" }}>
              {history.length}
            </div>
          </div>

          <div className="card summary-card" style={{ padding: 22, background: "var(--card)" }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", marginBottom: 8 }}>
              {lang === "bn" ? "গড় রেডিনেস" : "Avg Readiness"}
            </div>
            <div className="display" style={{ fontSize: 32, fontWeight: 600, color: "var(--ink)" }}>
              {avg}%
            </div>
          </div>

          <div className="card summary-card" style={{ padding: 22, background: "var(--card)" }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", marginBottom: 8 }}>
              {lang === "bn" ? "সেরা রেডিনেস" : "Best Score"}
            </div>
            <div className="display" style={{ fontSize: 32, fontWeight: 600, color: "var(--master)" }}>
              {best}%
            </div>
          </div>

          <div className="card summary-card" style={{ padding: 22, background: "var(--card)" }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", marginBottom: 8 }}>
              {lang === "bn" ? "সর্বশেষ স্কোর" : "Latest Score"}
            </div>
            <div className="display" style={{ fontSize: 32, fontWeight: 600, color: trend === "up" ? "var(--master)" : trend === "down" ? "var(--danger)" : "var(--ink)" }}>
              {latest}%
              <span style={{ fontSize: 14, marginLeft: 6, fontWeight: 600 }}>
                {trend === "up" ? "↑" : trend === "down" ? "↓" : "•"}
              </span>
            </div>
          </div>
        </div>

        {/* History List */}
        <div style={{ display: "flex", flexDirection: "column", gap: 14, marginBottom: 32 }}>
          {history.map((h, i) => {
            const r = h.readiness || {};
            const date = new Date(h.createdAt);
            const timeStr = date.toLocaleString(lang === "bn" ? "bn-BD" : "en-GB", {
              day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit"
            });
            const scoreVal = r.score ?? h.score ?? 0;
            const scoreColor = scoreVal >= 70 ? "var(--master)" : scoreVal >= 40 ? "var(--ochre)" : "var(--danger)";

            return (
              <motion.div
                className="history-session"
                key={h.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                onClick={() => onViewAttempt && onViewAttempt(h.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: 20,
                  borderRadius: "var(--r-md)",
                  border: "1px solid var(--line)",
                  background: "var(--card)",
                  cursor: "pointer",
                  transition: "all .15s"
                }}
              >
                {/* Left Side */}
                <div>
                  <div className="session-header" style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 6 }}>
                    <span className="badge" style={{ background: "var(--paper2)", color: "var(--ink)", fontWeight: 700, padding: "2px 8px", fontSize: 11 }}>
                      #{history.length - i}
                    </span>
                    <span className="session-date" style={{ fontSize: 13, color: "var(--muted)" }}>
                      {timeStr}
                    </span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    {h.mood && (
                      <span className="badge" style={{ background: "var(--paper2)", color: "var(--muted)", fontSize: 11, padding: "2px 8px" }}>
                        {h.mood}
                      </span>
                    )}
                    <span style={{ fontSize: 13, color: "var(--muted)" }}>
                      {r.correct ?? "?"} / {r.total ?? "?"} {lang === "bn" ? "সঠিক উত্তর" : "correct"}
                    </span>
                  </div>
                </div>

                {/* Right Side */}
                <div style={{ textAlign: "right" }}>
                  <div className="session-score" style={{ fontFamily: "'Hind Siliguri', serif", fontSize: 28, fontWeight: 600, color: scoreColor }}>
                    {scoreVal}%
                  </div>
                  <div style={{ fontSize: 11, color: "var(--muted)", textTransform: "uppercase", fontWeight: 700, letterSpacing: ".05em" }}>
                    {lang === "bn" ? "রেডিনেস" : "Readiness"}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Retake Button */}
        <div style={{ display: "flex", justifyContent: "center", marginTop: 24, paddingBottom: 40 }}>
          <button className="btn btn-primary" style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "12px 24px" }} onClick={onRetake}>
            <RefreshCw size={15} />
            {t("retake", lang)}
          </button>
        </div>

      </div>
    </div>
  );
}
