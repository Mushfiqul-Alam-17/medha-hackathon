import { Check, X, Timer, Award, Repeat2, AlertTriangle, Sparkles } from "lucide-react";
import { LETTERS, buildInsight, groupDefs, t } from "../utils/lang";

const ORDER = ["master", "slow", "confused", "danger"];
const ICONS = { master: Award, slow: Timer, confused: Repeat2, danger: AlertTriangle };

function DnaCard({ item, lang }) {
  const insight = buildInsight(item, lang);
  return (
    <div className="dna-card">
      <div className="dna-card-time"><Timer size={13} /> {item.timeTaken}s · {item.chapter}</div>
      <div className="dna-q">{item.questionText}</div>
      <div className="dna-opts">
        {item.options.map((opt, i) => {
          let cls = "dna-opt", icon = null;
          if (i === item.correctAnswerIndex) { cls += " correct"; icon = <Check size={14} className="d-icon" />; }
          else if (i === item.finalAnswerIndex && !item.isCorrect) { cls += " wrong"; icon = <X size={14} className="d-icon" />; }
          return <div className={cls} key={i}><span className="d-let">{LETTERS[i]}</span>{opt}{icon}</div>;
        })}
      </div>
      {item.clickSequence?.length > 0 && (
        <div className="click-path">
          <span className="cp-label">{t("clickPath", lang)}</span>
          {item.clickSequence.map((l, idx) => {
            const isLast = idx === item.clickSequence.length - 1;
            const cls = "cp-node" + (isLast ? (item.isCorrect ? " final-right" : " final-wrong") : "");
            return (
              <span key={idx} style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
                <span className={cls}>{l}</span>
                {idx < item.clickSequence.length - 1 && <span className="cp-arrow">→</span>}
              </span>
            );
          })}
        </div>
      )}
      <div className={`dna-insight ${insight.cls}`}>{insight.text}</div>
    </div>
  );
}

export default function DnaReport({ groups, onViewNotes, lang }) {
  const defs = groupDefs(lang);
  return (
    <div className="view" data-testid="dna-view">
      <div className="wrap">
        <div className="section-head">
          <span className="pill"><Sparkles size={13} /> {t("dnaEyebrow", lang)}</span>
          <h2 style={{ marginTop: 16 }}>{t("dnaTitle", lang)}</h2>
          <p>{t("dnaSub", lang)}</p>
        </div>

        {ORDER.map((key) => {
          const def = defs[key];
          const items = groups[key] || [];
          const Ic = ICONS[key];
          return (
            <div className={`dna-group ${def.cls}`} key={key} data-testid={`dna-group-${key}`}>
              <div className="dna-group-head">
                <div className="dna-group-ic"><Ic size={20} /></div>
                <div className="dna-group-meta">
                  <span className="dna-group-tag">{def.tagText}</span>
                  <span className="dna-group-label">{def.label}</span>
                </div>
                <span className="dna-group-count">{items.length}{t("dnaQuestions", lang)}</span>
              </div>
              {items.length === 0 ? (
                <div className="no-group">{def.empty}</div>
              ) : (
                <div className="dna-cards">{items.map((it) => <DnaCard key={it.questionId} item={it} lang={lang} />)}</div>
              )}
            </div>
          );
        })}

        <div style={{ marginTop: 12, display: "flex", justifyContent: "center" }}>
          <button className="btn btn-primary" data-testid="generate-notes-button" onClick={onViewNotes}>{t("genNotes", lang)}</button>
        </div>
      </div>
    </div>
  );
}
