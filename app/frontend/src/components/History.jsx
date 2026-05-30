import { motion } from "framer-motion";
import { Clock, TrendingUp, ChevronRight, Brain } from "lucide-react";
import { t } from "../utils/lang";

export default function History({ history, onViewAttempt, onRetake, lang }) {
  if (!history || history.length === 0) {
    return (
      <div className="view" data-testid="history-view">
        <div className="wrap">
          <div className="section-head">
            <span className="pill">{lang === "bn" ? "ইতিহাস" : "History"}</span>
            <h2 style={{ marginTop: 16 }}>{lang === "bn" ? "আগের পরীক্ষাসমূহ" : "Previous Exams"}</h2>
            <p>{lang === "bn" ? "এখনো কোনো পরীক্ষা দেওয়া হয়নি।" : "No exams taken yet."}</p>
          </div>
          <div style={{ display: "flex", justifyContent: "center", marginTop: 24 }}>
            <button className="btn btn-primary" onClick={onRetake}>
              {lang === "bn" ? "প্রথম পরীক্ষা দাও →" : "Take Your First Exam →"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="view" data-testid="history-view">
      <div className="wrap">
        <div className="section-head">
          <span className="pill">
            <Clock size={13} style={{ marginRight: 4, verticalAlign: "middle" }} />
            {lang === "bn" ? "ইতিহাস" : "History"}
          </span>
          <h2 style={{ marginTop: 16 }}>{lang === "bn" ? "আগের পরীক্ষাসমূহ" : "Previous Exams"}</h2>
          <p>{lang === "bn"
            ? `মোট ${history.length}টি সেশন সম্পন্ন। প্রতিটি সেশন তোমার প্রোফাইলকে আরও স্মার্ট করে।`
            : `${history.length} session${history.length > 1 ? "s" : ""} completed. Each session makes your profile smarter.`
          }</p>
        </div>

        {/* Summary Stats */}
        <div className="hist-summary">
          {(() => {
            const scores = history.map(h => h.readiness?.score ?? 0);
            const avg = scores.length ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
            const best = Math.max(...scores);
            const latest = scores[0] || 0;
            const trend = scores.length >= 2 ? (scores[0] >= scores[1] ? "up" : "down") : "stable";
            return [
              { v: history.length, l: lang === "bn" ? "মোট সেশন" : "Total Sessions", c: "var(--accent)" },
              { v: avg, l: lang === "bn" ? "গড় স্কোর" : "Avg Readiness", c: "var(--text)" },
              { v: best, l: lang === "bn" ? "সেরা স্কোর" : "Best Score", c: "var(--green)" },
              { v: `${latest}${trend === "up" ? " ↑" : trend === "down" ? " ↓" : ""}`, l: lang === "bn" ? "সর্বশেষ" : "Latest", c: trend === "up" ? "var(--green)" : trend === "down" ? "var(--red)" : "var(--text)" },
            ].map((m) => (
              <div className="card metric" key={m.l}>
                <div className="m-val" style={{ color: m.c }}>{m.v}</div>
                <div className="m-lbl">{m.l}</div>
              </div>
            ));
          })()}
        </div>

        {/* Session List */}
        <div className="hist-list">
          {history.map((h, i) => {
            const r = h.readiness || {};
            const date = new Date(h.createdAt);
            const timeStr = date.toLocaleString(lang === "bn" ? "bn-BD" : "en-GB", {
              day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit"
            });
            const scoreColor = (r.score || 0) >= 70 ? "var(--green)" : (r.score || 0) >= 40 ? "var(--amber)" : "var(--red)";

            return (
              <motion.div
                className="card hist-card"
                key={h.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                onClick={() => onViewAttempt && onViewAttempt(h.id)}
                style={{ cursor: onViewAttempt ? "pointer" : "default" }}
              >
                <div className="hist-card-left">
                  <div className="hist-card-num">#{history.length - i}</div>
                  <div>
                    <div className="hist-card-date">{timeStr}</div>
                    <div className="hist-card-mood">
                      {h.mood && <span className="hist-mood-chip">{h.mood}</span>}
                      <span className="hist-card-meta">
                        {r.correct ?? "?"}/{r.total ?? "?"} {lang === "bn" ? "সঠিক" : "correct"}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="hist-card-right">
                  <div className="hist-card-score" style={{ color: scoreColor }}>{r.score ?? "—"}</div>
                  <div className="hist-card-score-label">{lang === "bn" ? "রেডিনেস" : "Readiness"}</div>
                </div>
              </motion.div>
            );
          })}
        </div>

        <div style={{ display: "flex", justifyContent: "center", marginTop: 24 }}>
          <button className="btn btn-primary" onClick={onRetake}>
            {t("retake", lang)}
          </button>
        </div>
      </div>
    </div>
  );
}
