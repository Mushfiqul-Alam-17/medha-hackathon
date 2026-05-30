import { useEffect, useState } from "react";
import { Check, X, AlertTriangle, SkipForward } from "lucide-react";
import { LETTERS, scoreTitle, t } from "../utils/lang";

const CIRC = 2 * Math.PI * 50;
const NEG_PENALTY = 0.25;

export default function Result({ attempt, onViewDNA, lang }) {
  const items = attempt.items;
  const correct = attempt.readiness.correct;
  const total = attempt.readiness.total;
  const [offset, setOffset] = useState(CIRC);

  useEffect(() => {
    const tm = setTimeout(() => setOffset(CIRC * (1 - correct / total)), 250);
    return () => clearTimeout(tm);
  }, [correct, total]);

  // Negative marking calculation
  const wrong = items.filter((it) => it.finalAnswerIndex !== null && !it.isCorrect).length;
  const skipped = items.filter((it) => it.finalAnswerIndex === null).length;
  const rawScore = correct;
  const negDeduction = +(wrong * NEG_PENALTY).toFixed(2);
  const finalScore = +(rawScore - negDeduction).toFixed(2);

  // Skip coach: guessed + wrong
  const guessedWrong = items.filter(
    (it) => it.confidence === "guessing" && !it.isCorrect && it.finalAnswerIndex !== null
  );
  const savedMarks = +(guessedWrong.length * NEG_PENALTY).toFixed(2);

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

        {/* Negative Marking Card */}
        <div className="card neg-card">
          <h3 className="neg-title">
            <AlertTriangle size={18} style={{ marginRight: 6, color: "var(--amber)" }} />
            {lang === "bn" ? "নেগেটিভ মার্কিং বিশ্লেষণ" : "Negative Marking Analysis"}
          </h3>
          <div className="neg-grid">
            <div className="neg-item">
              <div className="neg-val" style={{ color: "var(--green)" }}>+{rawScore}</div>
              <div className="neg-lbl">{lang === "bn" ? "সঠিক উত্তর" : "Correct"}</div>
            </div>
            <div className="neg-item">
              <div className="neg-val" style={{ color: "var(--red)" }}>−{negDeduction}</div>
              <div className="neg-lbl">{lang === "bn" ? "ভুল জরিমানা" : "Wrong Penalty"}</div>
            </div>
            <div className="neg-item">
              <div className="neg-val" style={{ color: "var(--text-dim)" }}>{skipped}</div>
              <div className="neg-lbl">{lang === "bn" ? "স্কিপ (০ প্রভাব)" : "Skipped (0 impact)"}</div>
            </div>
            <div className="neg-item neg-final">
              <div className="neg-val" style={{ color: "var(--accent)", fontSize: 28 }}>{finalScore}</div>
              <div className="neg-lbl">{lang === "bn" ? "চূড়ান্ত স্কোর" : "Final Score"}</div>
            </div>
          </div>
          <div className="neg-formula">
            {lang === "bn"
              ? `সূত্র: ${rawScore} − (${wrong} × ০.২৫) = ${finalScore}`
              : `Formula: ${rawScore} − (${wrong} × 0.25) = ${finalScore}`}
          </div>
        </div>

        {/* Skip Coach */}
        {guessedWrong.length > 0 && (
          <div className="card skip-card">
            <h3 className="skip-title">
              <SkipForward size={18} style={{ marginRight: 6, color: "var(--accent)" }} />
              {lang === "bn" ? "স্কিপ কোচ" : "Skip Strategy Coach"}
            </h3>
            <p className="skip-text">
              {lang === "bn"
                ? `তুমি ${guessedWrong.length}টি প্রশ্নে অনুমান করে ভুল করেছ। এগুলো স্কিপ করলে তোমার +${savedMarks} মার্কস বাঁচত!`
                : `You guessed on ${guessedWrong.length} question${guessedWrong.length > 1 ? "s" : ""} and got them wrong. Skipping would have saved you +${savedMarks} marks!`}
            </p>
            <div className="skip-questions">
              {guessedWrong.map((it, i) => (
                <div className="skip-q" key={it.questionId}>
                  <span className="skip-q-mark">−{NEG_PENALTY}</span>
                  <span className="skip-q-text">{it.questionText.slice(0, 60)}…</span>
                </div>
              ))}
            </div>
            <div className="skip-tip">
              {lang === "bn"
                ? "💡 পরীক্ষায় অনুমান ≠ উত্তর দেওয়া। সন্দেহ থাকলে স্কিপ করো — নেগেটিভ মার্কিং বেশি ক্ষতিকর।"
                : "💡 In real exams, guessing ≠ answering. When in doubt, skip — negative marks hurt more than a blank."}
            </div>
          </div>
        )}

        {/* Question List */}
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
