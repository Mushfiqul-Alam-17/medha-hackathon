import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { t } from "../utils/lang";

export default function Readiness({ attempt, chapters, history, onRetake, lang }) {
  const r = attempt.readiness;
  const [animScore, setAnimScore] = useState(0);
  const [bars, setBars] = useState(false);

  useEffect(() => {
    let i = 0;
    const step = Math.max(1, Math.round(r.score / 30));
    const iv = setInterval(() => {
      i += step;
      if (i >= r.score) { i = r.score; clearInterval(iv); }
      setAnimScore(i);
    }, 24);
    const tm = setTimeout(() => setBars(true), 200);
    return () => { clearInterval(iv); clearTimeout(tm); };
  }, [r.score]);

  const maxFreq = Math.max(...chapters.map((c) => c.frequency), 1);

  // Weakness detection: find chapters where user got questions wrong
  const chapterPerf = {};
  (attempt.items || []).forEach((it) => {
    if (!chapterPerf[it.chapter]) chapterPerf[it.chapter] = { correct: 0, total: 0 };
    chapterPerf[it.chapter].total++;
    if (it.isCorrect) chapterPerf[it.chapter].correct++;
  });

  return (
    <div className="view" data-testid="readiness-view">
      <div className="wrap">
        <div className="section-head">
          <span className="pill">{t("readyEyebrow", lang)}</span>
          <h2 style={{ marginTop: 16 }}>{t("readyTitle", lang)}</h2>
          <p>{t("readySub", lang)}</p>
        </div>

        <div className="ready-top">
          <div className="card ready-score">
            <div className="ready-num" data-testid="readiness-score">{animScore}</div>
            <div className="ready-lbl">{t("readinessOf", lang)}</div>
          </div>
          <div className="metric-grid">
            {[
              { v: `${r.correct}/${r.total}`, l: t("correctAns", lang), c: "var(--green)" },
              { v: r.master, l: t("mastered", lang), c: "var(--green)" },
              { v: r.danger, l: t("confWrong", lang), c: "var(--red)" },
              { v: `${r.avgTime}s`, l: t("avgTime", lang), c: "var(--accent)" },
            ].map((m) => (
              <div className="card metric" key={m.l}>
                <div className="m-val" style={{ color: m.c }}>{m.v}</div>
                <div className="m-lbl">{m.l}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="card" style={{ marginBottom: 24 }}>
          <h3 style={{ fontSize: 18, marginBottom: 6 }}>{t("chapTitle", lang)}</h3>
          <p style={{ color: "var(--text-dim)", fontSize: 14, marginBottom: 20 }}>{t("chapSub", lang)}</p>
          {chapters.map((c, i) => {
            const perf = chapterPerf[c.chapter];
            const isWeak = perf && perf.correct < perf.total;
            return (
              <div className="chap-bar" key={c.chapter}>
                <div className="chap-bar-top">
                  <span>{c.chapter} {isWeak && <span className="chap-weak-badge">⚠ Weak</span>}</span>
                  <span className="pct">{c.frequency}%</span>
                </div>
                <div className="chap-track">
                  <motion.div className={`chap-fill ${isWeak ? "chap-fill-weak" : ""}`} initial={{ width: 0 }}
                    animate={{ width: bars ? `${(c.frequency / maxFreq) * 100}%` : 0 }}
                    transition={{ duration: 0.9, delay: i * 0.06 }} />
                </div>
              </div>
            );
          })}
        </div>

        {history?.length > 1 && (
          <div className="card" style={{ marginBottom: 24 }}>
            <h3 style={{ fontSize: 18, marginBottom: 16 }}>{t("prevAttempts", lang)}</h3>
            {history.slice(0, 6).map((h) => (
              <div className="hist-row" key={h.id} style={{ background: "var(--surface-2)", borderRadius: 10 }}>
                <span className="h-date">{new Date(h.createdAt).toLocaleString("en-GB", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}</span>
                <span className="hist-badge">Readiness {h.readiness?.score ?? "—"}</span>
              </div>
            ))}
          </div>
        )}

        <div style={{ display: "flex", justifyContent: "center" }}>
          <button className="btn btn-primary" data-testid="readiness-retake" onClick={onRetake}>{t("retake", lang)}</button>
        </div>
      </div>
    </div>
  );
}
