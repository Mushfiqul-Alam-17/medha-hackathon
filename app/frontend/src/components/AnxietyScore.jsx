import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Brain, Heart, AlertTriangle, Shield } from "lucide-react";
import { t, computeAnxiety } from "../utils/lang";

const LEVEL_ICONS = { low: Shield, mod: Heart, high: AlertTriangle, crit: Brain };
const CIRC = 2 * Math.PI * 54;

export default function AnxietyScore({ attempt, lang }) {
  const anx = computeAnxiety(attempt);
  const [offset, setOffset] = useState(CIRC);
  const [animScore, setAnimScore] = useState(0);

  useEffect(() => {
    const to = setTimeout(() => setOffset(CIRC * (1 - anx.score / 100)), 300);
    let i = 0;
    const step = Math.max(1, Math.round(anx.score / 30));
    const iv = setInterval(() => { i += step; if (i >= anx.score) { i = anx.score; clearInterval(iv); } setAnimScore(i); }, 24);
    return () => { clearTimeout(to); clearInterval(iv); };
  }, [anx.score]);

  const Ic = LEVEL_ICONS[anx.level];
  const levelText = t("anx" + anx.level.charAt(0).toUpperCase() + anx.level.slice(1), lang);
  const tips = [t("anxTip1", lang), t("anxTip2", lang), t("anxTip3", lang), t("anxTip4", lang)];

  return (
    <div className="view" data-testid="anxiety-view">
      <div className="wrap">
        <div className="section-head">
          <span className="pill"><Brain size={13} /> {t("anxEyebrow", lang)}</span>
          <h2 style={{ marginTop: 16 }}>{t("anxTitle", lang)}</h2>
          <p>{t("anxSub", lang)}</p>
        </div>

        <div className="anx-hero">
          <div className="anx-ring-wrap">
            <svg viewBox="0 0 120 120" width="148" height="148">
              <circle className="track" cx="60" cy="60" r="54" />
              <circle className={`anx-arc ${anx.levelCls}`} cx="60" cy="60" r="54"
                strokeDasharray={CIRC} strokeDashoffset={offset}
                style={{ transition: "stroke-dashoffset 1.2s ease" }} />
            </svg>
            <div className="anx-inner">
              <span className="anx-num">{animScore}</span>
              <span className="anx-of">/ 100</span>
            </div>
          </div>
          <div className={`anx-level-card ${anx.levelCls}`}>
            <Ic size={22} />
            <div>
              <div className="anx-level-label">{t("anxLevel", lang)}</div>
              <div className="anx-level-text">{levelText}</div>
            </div>
          </div>
        </div>

        {anx.factors.length > 0 && (
          <div className="card" style={{ marginTop: 24 }}>
            <h3 style={{ fontSize: 18, marginBottom: 16 }}>{t("anxFactors", lang)}</h3>
            <div className="anx-factors">
              {anx.factors.map((f, i) => (
                <motion.div className="anx-factor" key={i}
                  initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.12 }}>
                  <div className="anx-factor-bar">
                    <motion.div className="anx-factor-fill"
                      style={{ background: f.color }}
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(100, f.impact * 2.5)}%` }}
                      transition={{ duration: 0.8, delay: i * 0.12 }} />
                  </div>
                  <div className="anx-factor-meta">
                    <span>{f.label}</span>
                    <span className="anx-factor-impact" style={{ color: f.color }}>+{f.impact}</span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        <div className="card" style={{ marginTop: 24 }}>
          <h3 style={{ fontSize: 18, marginBottom: 16 }}>{t("anxTips", lang)}</h3>
          <div className="anx-tips">
            {tips.map((tip, i) => (
              <motion.div className="anx-tip" key={i}
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + i * 0.1 }}>
                <span className="anx-tip-num">{i + 1}</span>
                <span>{tip}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
