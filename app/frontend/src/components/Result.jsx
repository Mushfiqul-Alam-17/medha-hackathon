import { useEffect, useState } from "react";
import { Check, X, AlertTriangle, SkipForward, ArrowRight, BookOpen } from "lucide-react";
import { LETTERS, scoreTitle, t } from "../utils/lang";

const BACKEND = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
const CIRC = 414.7; // 2 * Math.PI * 66
const NEG_PENALTY = 0.25;

export default function Result({ attempt, onViewDNA, lang, onOpenPdf }) {
  const items = attempt.items || [];
  const correct = attempt.readiness?.correct ?? 0;
  const total = attempt.readiness?.total ?? 12;
  const [offset, setOffset] = useState(CIRC);

  useEffect(() => {
    const tm = setTimeout(() => setOffset(CIRC * (1 - correct / total)), 250);
    return () => clearTimeout(tm);
  }, [correct, total]);

  // Calculations
  const wrong = items.filter((it) => it.finalAnswerIndex !== null && !it.isCorrect).length;
  const skipped = items.filter((it) => it.finalAnswerIndex === null).length;
  const rawScore = correct;
  const negDeduction = +(wrong * NEG_PENALTY).toFixed(2);
  const finalScore = +(rawScore - negDeduction).toFixed(2);

  const avgTime = items.length
    ? +(items.reduce((sum, it) => sum + (it.timeTaken || 0), 0) / items.length).toFixed(1)
    : 0;

  const speedRatio = avgTime ? +(25 / avgTime).toFixed(1) : 1.0;

  // Guessed & Wrong items for skip coach
  const guessedWrong = items.filter(
    (it) => it.confidence === "guessing" && !it.isCorrect && it.finalAnswerIndex !== null
  );
  const savedMarks = +(guessedWrong.length * NEG_PENALTY).toFixed(2);

  const getPhenotype = (item) => {
    if (attempt.groups?.master?.some(x => x.questionId === item.questionId)) return "master";
    if (attempt.groups?.slow?.some(x => x.questionId === item.questionId)) return "slow";
    if (attempt.groups?.confused?.some(x => x.questionId === item.questionId)) return "confused";
    if (attempt.groups?.danger?.some(x => x.questionId === item.questionId)) return "danger";
    return "master"; // Fallback
  };

  const getPhenotypeName = (p) => {
    const names = {
      master: { en: "Mastered", bn: "পাকা" },
      slow: { en: "Slow", bn: "ধীর গতি" },
      confused: { en: "Confused", bn: "গোলমাল" },
      danger: { en: "Danger", bn: "ভুল জানো" }
    };
    return names[p]?.[lang] || names[p]?.en || p;
  };

  const getPhenotypeColor = (p) => {
    const colors = {
      master: "var(--master)",
      slow: "var(--slow)",
      confused: "var(--confused)",
      danger: "var(--danger)"
    };
    return colors[p] || "var(--master)";
  };

  return (
    <div className="view fade-in" data-testid="result-view" style={{ background: "var(--paper)" }}>
      <div className="container-md screen-inner" style={{ paddingTop: 32 }}>
        
        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
          <div className="eyebrow">{lang === "bn" ? "পরীক্ষা সম্পন্ন" : "Exam Complete"}</div>
          <span className="badge badge-master" style={{ fontSize: 13, padding: "6px 16px" }}>
            {lang === "bn" ? "সেশন শেষ" : "Session Complete"}
          </span>
        </div>

        {/* Hero Card */}
        <div className="card result-hero-card" style={{ padding: 40, marginBottom: 24 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 40, flexWrap: "wrap" }}>
            
            {/* Score progress ring */}
            <div className="score-ring-wrap">
              <svg width="160" height="160" viewBox="0 0 160 160">
                <circle cx="80" cy="80" r="66" fill="none" stroke="var(--line)" strokeWidth="12" />
                <circle
                  cx="80"
                  cy="80"
                  r="66"
                  fill="none"
                  stroke="var(--master)"
                  strokeWidth="12"
                  strokeLinecap="round"
                  strokeDasharray={CIRC}
                  strokeDashoffset={offset}
                  id="resultRing"
                  style={{ transition: "stroke-dashoffset 1.4s cubic-bezier(.4,0,.2,1)" }}
                />
              </svg>
              <div className="ring-center">
                <span className="ring-score" id="resultScore" style={{ color: "var(--master)" }}>
                  {correct}
                </span>
                <span className="ring-label">/ {total}</span>
              </div>
            </div>

            {/* Performance Stats */}
            <div style={{ flex: 1, minWidth: 280 }}>
              <p style={{ fontSize: 13, color: "var(--muted)", marginBottom: 6 }}>
                {lang === "bn" ? "কার্যকারিতা বিবরণ" : "Performance Summary"}
              </p>
              <h1 className="display" style={{ fontSize: 36, marginBottom: 20 }}>
                {scoreTitle(correct / total, lang)}
              </h1>
              <div className="result-stats">
                <div className="result-stat">
                  <div className="result-stat-val" style={{ color: "var(--master)" }}>
                    {correct} <span style={{ fontSize: 14, color: "var(--muted)" }}>/ {total}</span>
                  </div>
                  <div className="result-stat-lbl">{lang === "bn" ? "সঠিক উত্তর" : "Correct Answers"}</div>
                </div>
                <div className="result-stat">
                  <div className="result-stat-val">{avgTime}s</div>
                  <div className="result-stat-lbl">{lang === "bn" ? "গড় প্রতিক্রিয়া সময়" : "Avg Response Time"}</div>
                </div>
                <div className="result-stat">
                  <div className="result-stat-val" style={{ color: "var(--brand)" }}>
                    −{negDeduction} <span style={{ fontSize: 14, color: "var(--muted)" }}>pts</span>
                  </div>
                  <div className="result-stat-lbl">{lang === "bn" ? "নেগেটিভ জরিমানা" : "Negative Penalty"}</div>
                </div>
                <div className="result-stat">
                  <div className="result-stat-val">{speedRatio}x</div>
                  <div className="result-stat-lbl">{lang === "bn" ? "গড় গতির তুলনা" : "Speed vs Average"}</div>
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* Negative Marking Card */}
        <div className="card" style={{ padding: 28, marginBottom: 24 }}>
          <h2 className="display" style={{ fontSize: 20, marginBottom: 20 }}>
            {lang === "bn" ? "নেগেটিভ মার্কিং বিশ্লেষণ" : "Negative Marking Analysis"}
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 12 }}>
            <div style={{ padding: 14, borderRadius: "var(--r-sm)", background: "var(--masterSoft)" }}>
              <p style={{ fontSize: 11, color: "var(--muted)", marginBottom: 4 }}>{lang === "bn" ? "সঠিক" : "Correct"}</p>
              <p style={{ fontFamily: "'Hind Siliguri', serif", fontSize: 20, fontWeight: 600, color: "var(--master)" }}>
                {correct} × +1
              </p>
              <p style={{ fontSize: "11.5px", color: "var(--master)", marginTop: 2 }}>+{rawScore} pts</p>
            </div>
            <div style={{ padding: 14, borderRadius: "var(--r-sm)", background: "var(--dangerSoft)" }}>
              <p style={{ fontSize: 11, color: "var(--muted)", marginBottom: 4 }}>{lang === "bn" ? "জরিমানা" : "Penalty"}</p>
              <p style={{ fontFamily: "'Hind Siliguri', serif", fontSize: 20, fontWeight: 600, color: "var(--danger)" }}>
                {wrong} × −0.25
              </p>
              <p style={{ fontSize: "11.5px", color: "var(--danger)", marginTop: 2 }}>−{negDeduction} pts</p>
            </div>
            <div style={{ padding: 14, borderRadius: "var(--r-sm)", background: "var(--paper2)" }}>
              <p style={{ fontSize: 11, color: "var(--muted)", marginBottom: 4 }}>{lang === "bn" ? "স্কিপ" : "Skipped"}</p>
              <p style={{ fontFamily: "'Hind Siliguri', serif", fontSize: 20, fontWeight: 600, color: "var(--muted)" }}>
                {skipped} × 0
              </p>
              <p style={{ fontSize: "11.5px", color: "var(--muted)", marginTop: 2 }}>0 pts</p>
            </div>
            <div style={{ padding: 14, borderRadius: "var(--r-sm)", background: "var(--brandSoft)" }}>
              <p style={{ fontSize: 11, color: "var(--muted)", marginBottom: 4 }}>{lang === "bn" ? "চূড়ান্ত স্কোর" : "Final Score"}</p>
              <p style={{ fontFamily: "'Hind Siliguri', serif", fontSize: 20, fontWeight: 600, color: "var(--brand)" }}>
                {finalScore}
              </p>
              <p style={{ fontSize: "11.5px", color: "var(--brand)", marginTop: 2 }}>{lang === "bn" ? "সর্বমোট" : "Out of"} {total}</p>
            </div>
          </div>
        </div>

        {/* Skip Coach */}
        {guessedWrong.length > 0 && (
          <div className="card" style={{ padding: 28, borderLeft: "4px solid var(--brand)", marginBottom: 24 }}>
            <h3 className="display" style={{ fontSize: 18, color: "var(--brand)", marginBottom: 12, display: "flex", alignItems: "center", gap: 8 }}>
              <SkipForward size={20} />
              {lang === "bn" ? "স্কিপ স্ট্র্যাটেজি কোচ" : "Skip Strategy Coach"}
            </h3>
            <p style={{ fontSize: "14.5px", lineHeight: 1.6, color: "var(--muted)", marginBottom: 16 }}>
              {lang === "bn"
                ? `তুমি ${guessedWrong.length}টি প্রশ্নে অনুমান করে ভুল করেছ। এগুলো স্কিপ করলে তোমার +${savedMarks} মার্কস বাঁচত!`
                : `You guessed on ${guessedWrong.length} question${guessedWrong.length > 1 ? "s" : ""} and got them wrong. Skipping would have saved you +${savedMarks} marks!`}
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 16 }}>
              {guessedWrong.map((it) => (
                <div key={it.questionId} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 12px", background: "var(--paper2)", borderRadius: "var(--r-sm)" }}>
                  <span style={{ color: "var(--danger)", fontWeight: 700, fontSize: 13 }}>−0.25</span>
                  <span style={{ fontSize: 13, color: "var(--ink)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {it.questionText}
                  </span>
                </div>
              ))}
            </div>
            <div style={{ fontSize: "12.5px", color: "var(--muted)", fontStyle: "italic" }}>
              {lang === "bn"
                ? "💡 পরীক্ষায় অনুমান ≠ উত্তর দেওয়া। সন্দেহ থাকলে স্কিপ করো — নেগেティブ মার্কিং বেশি ক্ষতিকর।"
                : "💡 In real exams, guessing ≠ answering. When in doubt, skip — negative marks hurt more than a blank."}
            </div>
          </div>
        )}

        {/* Question Review List */}
        <div className="card" style={{ padding: 28, marginBottom: 24 }}>
          <h2 className="display" style={{ fontSize: 20, marginBottom: 20 }}>
            {lang === "bn" ? "প্রশ্নাবলি ও আচরণ বিশ্লেষণ" : "Questions & Behavioral Review"}
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            {items.map((it, i) => {
              const p = getPhenotype(it);
              return (
                <div key={it.questionId} style={{ borderBottom: "1px solid var(--line)", paddingBottom: 20 }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12, flexWrap: "wrap", gap: 8 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <span className="badge" style={{ background: "var(--paper2)", color: "var(--ink)", fontWeight: 700 }}>
                        Q{i + 1}
                      </span>
                      <span style={{ fontSize: 13, color: "var(--muted)", fontWeight: 500 }}>
                        {it.chapter}
                      </span>
                      <span style={{ fontSize: 12, color: "var(--muted)" }}>
                        • {it.timeTaken}s {lang === "bn" ? "ব্যয়িত" : "taken"}
                      </span>
                    </div>
                    <span className="badge" style={{ background: `${getPhenotypeColor(p)}Soft`, color: getPhenotypeColor(p), fontWeight: 700 }}>
                      {getPhenotypeName(p)}
                    </span>
                  </div>

                  <p className="q-text" style={{ fontSize: 17, fontWeight: 600, marginBottom: 16 }}>
                    {it.questionText}
                  </p>

                  <div className="options" style={{ pointerEvents: "none" }}>
                    {it.options.map((opt, j) => {
                      let cls = "option-btn";
                      if (j === it.correctAnswerIndex) cls += " correct";
                      else if (j === it.finalAnswerIndex && !it.isCorrect) cls += " wrong";
                      return (
                        <div className={cls} key={j} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                          <span className="option-letter">{LETTERS[j]}</span>
                          <span style={{ flex: 1 }}>{opt}</span>
                          {j === it.correctAnswerIndex && <Check size={16} style={{ color: "var(--master)" }} />}
                          {j === it.finalAnswerIndex && !it.isCorrect && <X size={16} style={{ color: "var(--danger)" }} />}
                        </div>
                      );
                    })}
                  </div>

                  {it.pdf_file && it.pdf_page && (
                    <div style={{ marginTop: 14, display: "flex", justifyContent: "flex-end" }}>
                      <button
                        onClick={() => onOpenPdf(it.pdf_file, it.pdf_page, it.options[it.correctAnswerIndex])}
                        className="btn btn-ghost"
                        style={{ padding: "6px 12px", fontSize: 12.5, display: "inline-flex", alignItems: "center", gap: 6, borderRadius: 8 }}
                      >
                        <BookOpen size={14} />
                        {lang === "bn" ? `মূল বইয়ের রেফারেন্স (পৃষ্ঠা ${it.pdf_page})` : `Textbook Ref (Page ${it.pdf_page})`}
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* CTA Banner */}
        <div className="cta-strip reveal show" style={{ marginBottom: 32 }}>
          <div>
            <h3 className="display" style={{ fontSize: 22 }}>
              {lang === "bn" ? "সম্পূর্ণ আচরণগত বিশ্লেষণ দেখুন" : "View your cognitive DNA"}
            </h3>
            <p>
              {lang === "bn"
                ? "আপনার সম্পূর্ণ ExamDNA রিপোর্ট দেখুন এবং জানুন ঠিক কোথায় উন্নতি প্রয়োজন।"
                : "Explore how your speed, switches, and confidence create your cognitive DNA."}
            </p>
          </div>
          <div className="cta-strip-actions">
            <button className="btn btn-primary" style={{ borderRadius: 10, padding: "12px 22px", display: "inline-flex", alignItems: "center", gap: 8 }} onClick={onViewDNA}>
              {lang === "bn" ? "DNA রিপোর্ট দেখুন" : "View DNA Report"}
              <ArrowRight size={16} />
            </button>
          </div>
        </div>

        <div className="page-footer" style={{ paddingBottom: 40 }}>
          {lang === "bn" ? "মেধা — মেডিকেল ভর্তি প্রস্তুতি" : "MEDHA — Medical Admission Prep"}
        </div>
      </div>
    </div>
  );
}
