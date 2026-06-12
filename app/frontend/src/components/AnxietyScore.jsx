import { useEffect, useState } from "react";
import { Brain, Heart, AlertTriangle, Shield } from "lucide-react";
import { t, computeAnxiety } from "../utils/lang";

const LEVEL_ICONS = { low: Shield, mod: Heart, high: AlertTriangle, crit: Brain };
const CIRC = 345.4; // Arc length for semi-circle: Math.PI * 110

export default function AnxietyScore({ attempt, lang }) {
  const anx = computeAnxiety(attempt);
  const [offset, setOffset] = useState(CIRC);
  const [animScore, setAnimScore] = useState(0);

  useEffect(() => {
    const to = setTimeout(() => setOffset(CIRC * (1 - anx.score / 100)), 300);
    let i = 0;
    const step = Math.max(1, Math.round(anx.score / 30));
    const iv = setInterval(() => {
      i += step;
      if (i >= anx.score) {
        i = anx.score;
        clearInterval(iv);
      }
      setAnimScore(i);
    }, 24);
    return () => {
      clearTimeout(to);
      clearInterval(iv);
    };
  }, [anx.score]);

  const Ic = LEVEL_ICONS[anx.level] || Brain;
  const levelText = t("anx" + anx.level.charAt(0).toUpperCase() + anx.level.slice(1), lang);
  const tips = [t("anxTip1", lang), t("anxTip2", lang), t("anxTip3", lang), t("anxTip4", lang)];

  // Calculate needle rotation angle (-90 deg to 90 deg for 180 degrees arc)
  const angle = (anx.score / 100) * 180 - 90;

  return (
    <div className="view fade-in" data-testid="anxiety-view" style={{ background: "var(--paper)" }}>
      <div className="container-md screen-inner" style={{ paddingTop: 32 }}>
        
        {/* Mindful Headings */}
        <div className="reveal show" style={{ textAlign: "center", maxWidth: 560, margin: "0 auto 40px" }}>
          <div style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            padding: "5px 14px",
            borderRadius: 999,
            background: "var(--card)",
            border: "1px solid var(--line)",
            fontSize: "11.5px",
            fontWeight: 600,
            color: "var(--muted)",
            letterSpacing: ".12em",
            textTransform: "uppercase",
            marginBottom: 16
          }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--sage)" }}></span>
            {lang === "bn" ? "মাইন্ডফুলনেস ইনসাইটস" : "Mindful Insights"}
          </div>
          <h1 className="display" style={{ fontSize: "clamp(34px, 5vw, 52px)", marginBottom: 12 }}>
            {lang === "bn" ? "উদ্বেগ সূচক বিশ্লেষণ" : "Your Exam Anxiety Score"}
          </h1>
          <p style={{ fontSize: "15.5px", color: "var(--muted)", lineHeight: 1.7 }}>
            {lang === "bn"
              ? "পরীক্ষায় আপনার মুড, দ্বিধা ও অপশন বদলানোর ধরণ থেকে উদ্বেগের মাত্রা পরিমাপ করা হয়েছে। সচেতনতাই সুস্থতার প্রথম ধাপ।"
              : "A gentle reflection of how exam pressure is showing up in your pacing and decisions. Awareness is the first step toward calm."}
          </p>
        </div>

        {/* 2-Column Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 24, alignItems: "start" }}>
          
          {/* Column 1: Dial Gauge */}
          <div className="card reveal show" style={{ padding: "28px 24px", display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div style={{ display: "flex", alignItems: "center", justifyBetween: "space-between", width: "100%", marginBottom: 16 }}>
              <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".15em", textTransform: "uppercase", color: "var(--muted)" }}>
                {t("anxLevel", lang)}
              </span>
              <span style={{ fontSize: "11.5px", color: "var(--muted)", display: "flex", alignItems: "center", gap: 5 }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--ochre)" }}></span>
                {lang === "bn" ? "রিয়েল-টাইম ট্র্যাক" : "Live track"}
              </span>
            </div>

            {/* Gauge Graphic */}
            <div className="gauge-wrap" style={{ width: "100%", maxWidth: 300 }}>
              <svg viewBox="0 0 300 180" style={{ width: "100%" }} fill="none">
                <defs>
                  <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#395F54" />
                    <stop offset="40%" stopColor="#C37A28" />
                    <stop offset="75%" stopColor="#D34A20" />
                    <stop offset="100%" stopColor="#C03A2A" />
                  </linearGradient>
                </defs>
                
                {/* Background arc */}
                <path d="M40 160 A110 110 0 1 1 260 160" stroke="var(--line)" strokeWidth="18" strokeLinecap="round" />
                
                {/* Filled progress arc */}
                <path
                  d="M40 160 A110 110 0 1 1 260 160"
                  stroke="url(#gaugeGrad)"
                  strokeWidth="18"
                  strokeLinecap="round"
                  strokeDasharray={CIRC}
                  strokeDashoffset={offset}
                  id="gaugeArc"
                  style={{ transition: "stroke-dashoffset 1.4s ease" }}
                />
                
                {/* Dial needle */}
                <line
                  id="gaugeNeedle"
                  x1="150"
                  y1="160"
                  x2="150"
                  y2="70"
                  stroke="var(--ink)"
                  strokeWidth="3"
                  strokeLinecap="round"
                  style={{ transform: `rotate(${angle}deg)`, transformOrigin: "150px 160px", transition: "transform 1.4s ease" }}
                />
                
                <circle cx="150" cy="160" r="7" fill="var(--ink)" />
                <text x="36" y="176" fontSize="11" fill="#395F54" fontFamily="'Plus Jakarta Sans', sans-serif" fontWeight="600">
                  {lang === "bn" ? "শান্ত" : "Calm"}
                </text>
                <text x="230" y="176" fontSize="11" fill="#C03A2A" fontFamily="'Plus Jakarta Sans', sans-serif" fontWeight="600">
                  {lang === "bn" ? "চাপ" : "High"}
                </text>
              </svg>

              <div className="gauge-readout" style={{ textAlign: "center", marginTop: 8 }}>
                <div className="gauge-score" id="anxietyScore" style={{ fontFamily: "'Hind Siliguri', serif", fontSize: 54, fontWeight: 600 }}>
                  {animScore}
                </div>
                <div style={{ fontSize: 13, color: "var(--muted)", marginTop: 4 }}>
                  {levelText}
                </div>
              </div>
            </div>

            {/* Level Pills indicator */}
            <div className="anxiety-level-pills" style={{ display: "flex", justifyContent: "center", gap: 6, marginTop: 16, flexWrap: "wrap" }}>
              <span className={`anxiety-pill ${anx.level === "low" ? "active" : ""}`}>
                {lang === "bn" ? "শান্ত (০-২৫)" : "Calm (0-25)"}
              </span>
              <span className={`anxiety-pill ${anx.level === "mod" ? "active" : ""}`}>
                {lang === "bn" ? "মাঝারি (২৬-৫০)" : "Moderate (26-50)"}
              </span>
              <span className={`anxiety-pill ${anx.level === "high" ? "active" : ""}`}>
                {lang === "bn" ? "উচ্চ (৫১-৭৫)" : "High (51-75)"}
              </span>
              <span className={`anxiety-pill ${anx.level === "crit" ? "active" : ""}`}>
                {lang === "bn" ? "ক্রিটিকাল (৭৬-১০০)" : "Critical (76-100)"}
              </span>
            </div>

            {/* Mindfulness banner */}
            <div style={{
              width: "100%",
              marginTop: 24,
              padding: "14px 16px",
              background: "var(--ochreSoft)",
              color: "var(--ochre)",
              borderRadius: 12,
              fontSize: "13.5px",
              fontWeight: 600,
              textAlign: "center"
            }}>
              {lang === "bn" ? "✦ পরবর্তী পরীক্ষার আগে ৩ বার গভীর শ্বাস নিন ✦" : "✦ Take 3 deep diaphragmatic breaths now ✦"}
            </div>
          </div>

          {/* Column 2: Factors & Mindfulness Tips */}
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            
            {/* Contributing Factors */}
            {anx.factors.length > 0 && (
              <div className="card reveal show" style={{ padding: 28 }}>
                <h2 className="display" style={{ fontSize: 20, marginBottom: 6 }}>
                  {t("anxFactors", lang)}
                </h2>
                <p style={{ fontSize: "13.5px", color: "var(--muted)", marginBottom: 20 }}>
                  {lang === "bn" ? "আচরণগত সংকেত যা চাপ বৃদ্ধি করছে:" : "Behavioral signals affecting your anxiety score."}
                </p>

                <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                  {anx.factors.map((f, i) => (
                    <div className="anx-factor" key={i}>
                      <div className="anx-factor-meta" style={{ display: "flex", justifyContent: "space-between", fontSize: 13, color: "var(--ink)", fontWeight: 600, marginBottom: 6 }}>
                        <span>{f.label}</span>
                        <span style={{ color: f.color }}>+{f.impact} pts</span>
                      </div>
                      <div className="anx-factor-bar" style={{ height: 6, background: "var(--paper2)", borderRadius: 99 }}>
                        <div className="anx-factor-fill" style={{
                          height: "100%",
                          borderRadius: 99,
                          background: f.color,
                          width: `${Math.min(100, f.impact * 2.5)}%`
                        }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Mindfulness Tips */}
            <div className="card reveal show" style={{ padding: 28 }}>
              <h2 className="display" style={{ fontSize: 20, marginBottom: 16 }}>
                {t("anxTips", lang)}
              </h2>
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {tips.map((tip, i) => (
                  <div key={i} style={{ display: "flex", gap: 14, alignItems: "flex-start" }}>
                    <span style={{
                      width: 24,
                      height: 24,
                      borderRadius: "50%",
                      background: "var(--sageSoft)",
                      color: "var(--sage)",
                      fontWeight: 700,
                      fontSize: 12.5,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexShrink: 0
                    }}>
                      {i + 1}
                    </span>
                    <span style={{ fontSize: 13.5, color: "var(--muted)", lineHeight: 1.55 }}>
                      {tip}
                    </span>
                  </div>
                ))}
              </div>
            </div>

          </div>

        </div>

        <div className="page-footer" style={{ paddingBottom: 40, marginTop: 40 }}>
          {lang === "bn" ? "মেধা — কগনিটিভ ওয়েলবিয়িং" : "MEDHA — Cognitive Wellbeing Analytics"}
        </div>

      </div>
    </div>
  );
}
