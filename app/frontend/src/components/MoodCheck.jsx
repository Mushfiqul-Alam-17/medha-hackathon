import { useState } from "react";
import { t } from "../utils/lang";
import { Brain } from "lucide-react";

const MOODS = [
  { key: "great", emoji: "😊" },
  { key: "good", emoji: "🙂" },
  { key: "okay", emoji: "😐" },
  { key: "tired", emoji: "😴" },
  { key: "stressed", emoji: "😰" },
];

export default function MoodCheck({ onContinue, lang }) {
  const [mood, setMood] = useState(null);
  const [confidence, setConfidence] = useState(true); // default ON

  return (
    <div className="view" data-testid="mood-view">
      <div className="wrap mood-wrap">
        <h2>{t("moodTitle", lang)}</h2>
        <p style={{ color: "var(--text-dim)" }}>{t("moodSub", lang)}</p>

        <div className="mood-grid">
          {MOODS.map((m) => (
            <button key={m.key} className={`mood-btn ${mood === m.key ? "sel" : ""}`}
              data-testid={`mood-${m.key}`} onClick={() => setMood(m.key)}>
              <span className="mood-emoji">{m.emoji}</span>
              <span>{t("mood" + m.key.charAt(0).toUpperCase() + m.key.slice(1), lang)}</span>
            </button>
          ))}
        </div>

        {/* Confidence Tracking Toggle */}
        <div className="conf-toggle-card">
          <div className="conf-toggle-info">
            <div className="conf-toggle-icon"><Brain size={18} /></div>
            <div>
              <div className="conf-toggle-title">
                {lang === "bn" ? "আত্মবিশ্বাস ট্র্যাকিং" : "Confidence Tracking"}
              </div>
              <div className="conf-toggle-desc">
                {confidence
                  ? (lang === "bn"
                    ? "প্রতিটি প্রশ্নে Sure / Unsure / Guessing বেছে নিতে হবে।"
                    : "You'll rate Sure / Unsure / Guessing after each answer.")
                  : (lang === "bn"
                    ? "বন্ধ — শুধু উত্তর বেছে নাও, দ্রুত মোড।"
                    : "Off — just pick an answer, faster exam mode.")}
              </div>
            </div>
          </div>
          <button
            className={`toggle-btn ${confidence ? "on" : "off"}`}
            data-testid="confidence-toggle"
            onClick={() => setConfidence((v) => !v)}
            aria-label="Toggle confidence tracking"
          >
            <span className="toggle-knob" />
          </button>
        </div>

        <p className="mood-note">{t("moodNote", lang)}</p>

        <button className="btn btn-primary" data-testid="mood-continue"
          disabled={!mood}
          onClick={() => onContinue(mood, confidence)}>
          {t("moodStart", lang)}
        </button>
      </div>
    </div>
  );
}
