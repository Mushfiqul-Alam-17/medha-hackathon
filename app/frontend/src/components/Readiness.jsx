import { useEffect, useState } from "react";
import { Timer, Award, CheckCircle, AlertTriangle, RefreshCw, BarChart2 } from "lucide-react";
import { t } from "../utils/lang";

const CIRC = 502.7; // 2 * Math.PI * 80

export default function Readiness({ attempt, chapters = [], history = [], onRetake, lang }) {
  const r = attempt.readiness || {};
  const score = attempt.score ?? 70; // score out of 100
  const items = attempt.items || [];
  
  const [animScore, setAnimScore] = useState(0);
  const [offset, setOffset] = useState(CIRC);

  useEffect(() => {
    let i = 0;
    const step = Math.max(1, Math.round(score / 30));
    const iv = setInterval(() => {
      i += step;
      if (i >= score) {
        i = score;
        clearInterval(iv);
      }
      setAnimScore(i);
    }, 24);
    
    const tm = setTimeout(() => setOffset(CIRC * (1 - score / 100)), 200);

    return () => {
      clearInterval(iv);
      clearTimeout(tm);
    };
  }, [score]);

  // Dynamic Metrics
  const correct = r.correct ?? items.filter(it => it.isCorrect).length;
  const total = r.total ?? items.length;
  const accuracyPct = total ? Math.round((correct / total) * 100) : 0;
  
  const masterCount = attempt.groups?.master?.length ?? items.filter(it => it.isCorrect && it.timeTaken <= 8).length;
  const dangerCount = attempt.groups?.danger?.length ?? items.filter(it => !it.isCorrect && it.timeTaken <= 8).length;
  
  const avgTime = items.length
    ? +(items.reduce((sum, it) => sum + (it.timeTaken || 0), 0) / items.length).toFixed(1)
    : 0;
  const speedRatio = avgTime ? +(25 / avgTime).toFixed(1) : 1.0;

  // Dynamic breakdown values
  const coveragePct = chapters.length
    ? Math.round((new Set(items.map(it => it.chapter)).size / chapters.length) * 100)
    : 75;

  const confidentItems = items.filter(it => it.confidence === "sure").length;
  const consistencyPct = items.length
    ? Math.round(((items.filter(it => it.confidence === "sure" && it.isCorrect).length + items.filter(it => it.confidence === "guessing" && !it.isCorrect).length) / items.length) * 100)
    : 80;

  const speedPct = Math.min(100, Math.round(speedRatio * 65));

  // Chapter frequency setup
  const maxFreq = chapters.length ? Math.max(...chapters.map((c) => c.frequency), 1) : 1;
  const chapterPerf = {};
  items.forEach((it) => {
    if (!chapterPerf[it.chapter]) chapterPerf[it.chapter] = { correct: 0, total: 0 };
    chapterPerf[it.chapter].total++;
    if (it.isCorrect) chapterPerf[it.chapter].correct++;
  });

  return (
    <div className="view fade-in" data-testid="readiness-view" style={{ background: "var(--paper)" }}>
      <div className="container-md screen-inner" style={{ paddingTop: 32 }}>
        
        {/* Header */}
        <div className="reveal show" style={{ marginBottom: 28 }}>
          <span className="pill" style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
            <BarChart2 size={13} />
            {t("readyEyebrow", lang)}
          </span>
          <h1 className="display" style={{ fontSize: "clamp(36px, 5vw, 56px)", marginTop: 14, marginBottom: 12 }}>
            {t("readyTitle", lang)}
          </h1>
          <p style={{ fontSize: 16, color: "var(--muted)", lineHeight: 1.7, maxWidth: 500 }}>
            {t("readySub", lang)}
          </p>
        </div>

        {/* 2-Column Grid */}
        <div className="readiness-grid" style={{ marginBottom: 32 }}>
          
          {/* Left Column: Gauge & Breakdown */}
          <div className="card readiness-ring-card" style={{ padding: 36, textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div className="readiness-ring" style={{ position: "relative", width: 200, height: 200 }}>
              <svg width="200" height="200" viewBox="0 0 200 200" style={{ transform: "rotate(-90deg)" }}>
                <circle cx="100" cy="100" r="80" fill="none" stroke="var(--paper2)" strokeWidth="16" />
                <circle
                  cx="100"
                  cy="100"
                  r="80"
                  fill="none"
                  stroke="var(--sage)"
                  strokeWidth="16"
                  strokeLinecap="round"
                  strokeDasharray={CIRC}
                  strokeDashoffset={offset}
                  id="readinessRing"
                  style={{ transition: "stroke-dashoffset 1.6s cubic-bezier(.4,0,.2,1)" }}
                />
              </svg>
              <div className="readiness-ring-center" style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                <span className="readiness-score" id="readinessScore" style={{ fontFamily: "'Hind Siliguri', serif", fontSize: 52, fontWeight: 600, letterSpacing: "-.03em", color: "var(--sage)", lineHeight: 1 }}>
                  {animScore}
                </span>
                <span style={{ fontSize: 12, color: "var(--muted)", marginTop: 3 }}>/ 100</span>
              </div>
            </div>

            <div style={{ marginTop: 20 }}>
              <span className="badge badge-master" style={{ fontSize: 13, padding: "7px 20px" }}>
                {animScore >= 80 ? (lang === "bn" ? "চমৎকার প্রস্তুতি" : "Excellent Readiness") : animScore >= 60 ? (lang === "bn" ? "ভালো প্রস্তুতি" : "Well Prepared") : (lang === "bn" ? "অনুশীলন প্রয়োজন" : "Needs Revision")}
              </span>
            </div>
            
            <p style={{ fontSize: 13, color: "var(--muted)", marginTop: 16, lineHeight: 1.65, maxWidth: 220 }}>
              {lang === "bn"
                ? "উদ্ভিদ শারীরস্থান অধ্যায়ে ফোকাস করলে প্রস্তুতি আরও ভালো হবে।"
                : "You're making steady progress. Clear concepts in Plant Anatomy to boost readiness."}
            </p>

            <hr className="divider" style={{ margin: "24px 0", width: "100%" }} />

            {/* Breakdown bars */}
            <div style={{ width: "100%" }}>
              <div className="eyebrow" style={{ marginBottom: 14, textAlign: "left" }}>
                {lang === "bn" ? "স্কোর বিশ্লেষণ" : "Score Breakdown"}
              </div>
              
              <div className="breakdown-bar-row" style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
                <span className="breakdown-bar-label" style={{ fontSize: 12.5, color: "var(--muted)", width: 90, textAlign: "left" }}>
                  {lang === "bn" ? "সঠিকতা" : "Accuracy"}
                </span>
                <div className="breakdown-bar-track" style={{ flex: 1, height: 8, background: "var(--paper2)", borderRadius: 999, overflow: "hidden" }}>
                  <div className="breakdown-bar-fill" style={{ height: "100%", borderRadius: 999, background: "var(--sage)", width: `${accuracyPct}%` }}></div>
                </div>
                <span className="breakdown-bar-val" style={{ fontSize: 12.5, fontWeight: 700, width: 36, textAlign: "right" }}>
                  {accuracyPct}%
                </span>
              </div>

              <div className="breakdown-bar-row" style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
                <span className="breakdown-bar-label" style={{ fontSize: 12.5, color: "var(--muted)", width: 90, textAlign: "left" }}>
                  {lang === "bn" ? "কভারেজ" : "Coverage"}
                </span>
                <div className="breakdown-bar-track" style={{ flex: 1, height: 8, background: "var(--paper2)", borderRadius: 999, overflow: "hidden" }}>
                  <div className="breakdown-bar-fill" style={{ height: "100%", borderRadius: 999, background: "var(--sage)", width: `${coveragePct}%` }}></div>
                </div>
                <span className="breakdown-bar-val" style={{ fontSize: 12.5, fontWeight: 700, width: 36, textAlign: "right" }}>
                  {coveragePct}%
                </span>
              </div>

              <div className="breakdown-bar-row" style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
                <span className="breakdown-bar-label" style={{ fontSize: 12.5, color: "var(--muted)", width: 90, textAlign: "left" }}>
                  {lang === "bn" ? "স্থায়িত্ব" : "Consistency"}
                </span>
                <div className="breakdown-bar-track" style={{ flex: 1, height: 8, background: "var(--paper2)", borderRadius: 999, overflow: "hidden" }}>
                  <div className="breakdown-bar-fill" style={{ height: "100%", borderRadius: 999, background: "var(--sage)", width: `${consistencyPct}%` }}></div>
                </div>
                <span className="breakdown-bar-val" style={{ fontSize: 12.5, fontWeight: 700, width: 36, textAlign: "right" }}>
                  {consistencyPct}%
                </span>
              </div>

              <div className="breakdown-bar-row" style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
                <span className="breakdown-bar-label" style={{ fontSize: 12.5, color: "var(--muted)", width: 90, textAlign: "left" }}>
                  {lang === "bn" ? "গতি" : "Speed"}
                </span>
                <div className="breakdown-bar-track" style={{ flex: 1, height: 8, background: "var(--paper2)", borderRadius: 999, overflow: "hidden" }}>
                  <div className="breakdown-bar-fill" style={{ height: "100%", borderRadius: 999, background: "var(--sage)", width: `${speedPct}%` }}></div>
                </div>
                <span className="breakdown-bar-val" style={{ fontSize: 12.5, fontWeight: 700, width: 36, textAlign: "right" }}>
                  {speedPct}%
                </span>
              </div>
            </div>
          </div>

          {/* Right Column: Metrics & Chapter heatmap */}
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            
            {/* 2x2 stats */}
            <div className="metric-2x2">
              <div className="card metric-card" style={{ padding: 20 }}>
                <div className="metric-val" style={{ fontFamily: "'Hind Siliguri', serif", fontSize: 26, color: "var(--master)", fontWeight: 600 }}>
                  {correct} <span style={{ fontSize: 14, color: "var(--muted)" }}>/ {total}</span>
                </div>
                <div className="metric-lbl" style={{ fontSize: 12, color: "var(--muted)", marginTop: 4 }}>
                  {t("correctAns", lang)}
                </div>
              </div>
              
              <div className="card metric-card" style={{ padding: 20 }}>
                <div className="metric-val" style={{ fontFamily: "'Hind Siliguri', serif", fontSize: 26, color: "var(--master)", fontWeight: 600 }}>
                  {masterCount}
                </div>
                <div className="metric-lbl" style={{ fontSize: 12, color: "var(--muted)", marginTop: 4 }}>
                  {t("mastered", lang)}
                </div>
              </div>

              <div className="card metric-card" style={{ padding: 20 }}>
                <div className="metric-val" style={{ fontFamily: "'Hind Siliguri', serif", fontSize: 26, color: "var(--danger)", fontWeight: 600 }}>
                  {dangerCount}
                </div>
                <div className="metric-lbl" style={{ fontSize: 12, color: "var(--muted)", marginTop: 4 }}>
                  {t("confWrong", lang)}
                </div>
              </div>

              <div className="card metric-card" style={{ padding: 20 }}>
                <div className="metric-val" style={{ fontFamily: "'Hind Siliguri', serif", fontSize: 26, color: "var(--brand)", fontWeight: 600 }}>
                  {avgTime}s
                </div>
                <div className="metric-lbl" style={{ fontSize: 12, color: "var(--muted)", marginTop: 4 }}>
                  {t("avgTime", lang)}
                </div>
              </div>
            </div>

            {/* Chapter Heatmap */}
            {chapters.length > 0 && (
              <div className="card" style={{ padding: 24 }}>
                <h3 className="display" style={{ fontSize: 18, marginBottom: 4 }}>{t("chapTitle", lang)}</h3>
                <p style={{ color: "var(--muted)", fontSize: 12.5, marginBottom: 18 }}>{t("chapSub", lang)}</p>
                
                <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                  {chapters.slice(0, 5).map((c, i) => {
                    const perf = chapterPerf[c.chapter];
                    const isWeak = perf && perf.correct < perf.total;
                    return (
                      <div className="chap-bar" key={c.chapter}>
                        <div className="chap-bar-top" style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 4 }}>
                          <span style={{ fontWeight: 600, display: "inline-flex", alignItems: "center", gap: 6 }}>
                            {c.chapter}{" "}
                            {isWeak && (
                              <span className="badge badge-danger" style={{ fontSize: 9, padding: "2px 6px" }}>
                                {lang === "bn" ? "দুর্বল" : "Weak"}
                              </span>
                            )}
                          </span>
                          <span style={{ color: "var(--muted)" }}>{c.frequency}%</span>
                        </div>
                        <div className="chap-track" style={{ height: 6, background: "var(--paper2)", borderRadius: 99 }}>
                          <div
                            className="chap-fill"
                            style={{
                              height: "100%",
                              borderRadius: 99,
                              background: isWeak ? "var(--danger)" : "var(--sage)",
                              width: `${(c.frequency / maxFreq) * 100}%`
                            }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

          </div>

        </div>

        {/* History Attempts List */}
        {history?.length > 1 && (
          <div className="card" style={{ padding: 28, marginBottom: 28 }}>
            <h3 className="display" style={{ fontSize: 18, marginBottom: 16 }}>{t("prevAttempts", lang)}</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {history.slice(0, 5).map((h, idx) => (
                <div className="hist-row" key={h.id || idx} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 16px", background: "var(--card)", border: "1px solid var(--line)", borderRadius: 10 }}>
                  <span style={{ fontSize: 13, color: "var(--muted)" }}>
                    {new Date(h.createdAt).toLocaleString("en-GB", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}
                  </span>
                  <span className="badge badge-master" style={{ fontWeight: 700 }}>
                    {lang === "bn" ? "প্রস্তুতি" : "Readiness"} {h.readiness?.score ?? h.score ?? "—"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions bar */}
        <div style={{ display: "flex", justifyContent: "center", marginTop: 24, paddingBottom: 40 }}>
          <button className="btn btn-primary" style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "12px 24px" }} data-testid="readiness-retake" onClick={onRetake}>
            <RefreshCw size={15} />
            {t("retake", lang)}
          </button>
        </div>

      </div>
    </div>
  );
}
