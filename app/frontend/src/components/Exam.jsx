import { useState, useEffect, useRef, useCallback } from "react";
import { LETTERS, t } from "../utils/lang";

const PER_Q_SECONDS = 30;
const CIRC = 2 * Math.PI * 24;

export default function Exam({ questions, mood, onFinish, lang, showConfidence = true }) {
  const [qi, setQi] = useState(0);
  const [selected, setSelected] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [secLeft, setSecLeft] = useState(PER_Q_SECONDS);

  const startRef = useRef(Date.now());
  const clicksRef = useRef([]);
  const itemsRef = useRef([]);
  const tickRef = useRef(null);

  const q = questions[qi];

  const selectedRef = useRef(null);
  const confidenceRef = useRef(null);
  selectedRef.current = selected;
  confidenceRef.current = confidence;

  const commitQuestion = useCallback((finalIndex, conf) => {
    if (!q) return;
    if (itemsRef.current.length > qi) return; // Prevent duplicate commits for the same question
    
    const timeTaken = (Date.now() - startRef.current) / 1000;
    itemsRef.current.push({
      questionId: q.id,
      finalAnswerIndex: finalIndex,
      clickSequence: [...clicksRef.current],
      timeTaken: Math.max(0.5, timeTaken),
      confidence: conf,
    });
  }, [q, qi]);

  const [submitting, setSubmitting] = useState(false);

  const goNext = useCallback((finalIndex, conf) => {
    if (submitting) return;
    if (itemsRef.current.length > qi) return; // Prevent duplicate transitions
    
    clearInterval(tickRef.current);
    commitQuestion(finalIndex, conf);
    if (qi < questions.length - 1) {
      setQi((p) => p + 1);
    } else {
      setSubmitting(true);
      // Give App.js a chance to catch failure and re-enable if needed
      Promise.resolve(onFinish(itemsRef.current, mood)).catch(() => setSubmitting(false));
    }
  }, [qi, questions.length, commitQuestion, onFinish, mood, submitting]);

  useEffect(() => {
    setSelected(null);
    setConfidence(null);
    setSecLeft(PER_Q_SECONDS);
    startRef.current = Date.now();
    clicksRef.current = [];
    clearInterval(tickRef.current);
    tickRef.current = setInterval(() => {
      setSecLeft((s) => {
        if (s <= 1) {
          clearInterval(tickRef.current);
          goNext(selectedRef.current, confidenceRef.current);
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => clearInterval(tickRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [qi]);

  const pickOption = (i) => {
    if (selected === i) return;
    setSelected(i);
    clicksRef.current.push(LETTERS[i]);
  };

  if (!q) return null;

  const progress = ((qi + 1) / questions.length) * 100;
  const offset = CIRC * (1 - secLeft / PER_Q_SECONDS);
  const urgent = secLeft <= 8;
  const isLast = qi === questions.length - 1;

  return (
    <div className="view" data-testid="exam-view">
      <div className="wrap exam-wrap">
        <div className="exam-top">
          <div className="progress">
            <div className="progress-bar"><div className="progress-fill" style={{ width: progress + "%" }} /></div>
            <span className="progress-lbl" data-testid="exam-progress">{qi + 1} / {questions.length}</span>
          </div>
          <div className="timer">
            <svg viewBox="0 0 52 52" width="52" height="52">
              <circle className="track" cx="26" cy="26" r="24" />
              <circle className={`ring ${urgent ? "urgent" : ""}`} cx="26" cy="26" r="24"
                strokeDasharray={CIRC} strokeDashoffset={offset} />
            </svg>
            <span className="num" data-testid="exam-timer">{secLeft}</span>
          </div>
        </div>

        <div className="q-box">
          <span className="q-tag">{q.chapter}</span>
          <p className="q-text" data-testid="question-text">{q.text}</p>
        </div>

        <div className="opts">
          {q.options.map((opt, i) => (
            <button key={i} className={`opt ${selected === i ? "sel" : ""}`}
              data-testid={`option-${i}`} onClick={() => pickOption(i)}>
              <span className="opt-letter">{LETTERS[i]}</span>{opt}
            </button>
          ))}
        </div>

        {showConfidence && selected !== null && (
          <div className="confidence" data-testid="confidence-block">
            <div className="c-label">{t("confLabel", lang)}</div>
            <div className="conf-opts">
              {[["sure", t("confSure", lang)], ["unsure", t("confUnsure", lang)], ["guessing", t("confGuessing", lang)]].map(([k, l]) => (
                <button key={k} className={`conf-opt ${confidence === k ? "sel" : ""}`}
                  data-testid={`confidence-${k}`} onClick={() => setConfidence(k)}>{l}</button>
              ))}
            </div>
          </div>
        )}

        <div className="exam-nav">
          <button className="btn btn-ghost" data-testid="skip-button" onClick={() => goNext(selected, confidence)}>{t("skip", lang)}</button>
          <button className="btn btn-primary" data-testid="next-button"
            disabled={submitting || selected === null || (showConfidence && confidence === null)}
            onClick={() => goNext(selected, showConfidence ? confidence : "none")}>
            {isLast ? t("finishExam", lang) : t("next", lang)}
          </button>
        </div>
      </div>
    </div>
  );
}
