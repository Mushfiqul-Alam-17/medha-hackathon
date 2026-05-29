import { useState } from "react";
import { t } from "../utils/lang";

const MOODS = [
  { key: "great", emoji: "😊" },
  { key: "good", emoji: "🙂" },
  { key: "okay", emoji: "😐" },
  { key: "tired", emoji: "😴" },
  { key: "stressed", emoji: "😰" },
];

export default function MoodCheck({ onContinue, lang }) {
  const [mood, setMood] = useState(null);

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

        <p className="mood-note">{t("moodNote", lang)}</p>

        <button className="btn btn-primary" data-testid="mood-continue"
          disabled={!mood} onClick={() => onContinue(mood)}>{t("moodStart", lang)}</button>
      </div>
    </div>
  );
}
