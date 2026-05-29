import { useEffect, useState } from "react";
import { Check, X } from "lucide-react";
import { LETTERS, scoreTitle, t } from "../utils/lang";

const CIRC = 2 * Math.PI * 50;

export default function Result({ attempt, onViewDNA, lang }) {
  const items = attempt.items;
  const correct = attempt.readiness.correct;
  const total = attempt.readiness.total;
  const [offset, setOffset] = useState(CIRC);

  useEffect(() => {
    const tm = setTimeout(() => setOffset(CIRC * (1 - correct / total)), 250);
    return () => clearTimeout(tm);
  }, [correct, total]);

  const sub = t("scoreSub", lang).replace("{total}", total).replace("{avg}", attempt.readiness.avgTime);

  return (
    <div className="view" data-testid="result-view">
      <div className="wrap">
        <div className="result-hero">
          <div className="score-ring">
            <svg viewBox="0 0 120 120" width="132" height="132">
              <circle className="track" cx="60" cy="60" r="50" />
              <circle className="arc" cx="60" cy="60" r="50" strokeDasharray={CIRC} strokeDashoffset={offset} />
            </svg>
            <div className="inner">
              <span className="num" data-testid="score-num">{correct}</span>
              <span className="den">/ {total}</span>
            </div>
          </div>
          <div>
            <div className="score-title" data-testid="score-title">{scoreTitle(correct / total)}</div>
            <div className="score-sub">{sub}</div>
          </div>
        </div>

        <div className="result-list">
          {items.map((it, i) => (
            <div className="card result-card" key={it.questionId} data-testid={`result-card-${i}`}>
              <div className="result-q">{i + 1}. {it.questionText}</div>
              <div className="result-opts">
                {it.options.map((opt, j) => {
                  let cls = "r-opt", icon = null;
                  if (j === it.correctAnswerIndex) { cls += " correct"; icon = <Check size={15} className="r-icon" />; }
                  else if (j === it.finalAnswerIndex && !it.isCorrect) { cls += " wrong"; icon = <X size={15} className="r-icon" />; }
                  return (
                    <div className={cls} key={j}>
                      <span className="r-let">{LETTERS[j]}</span>{opt}{icon}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: 28, display: "flex", justifyContent: "center" }}>
          <button className="btn btn-primary" data-testid="view-dna-button" onClick={onViewDNA}>{t("viewDna", lang)}</button>
        </div>
      </div>
    </div>
  );
}
