import { useState, useEffect, useRef, useCallback } from "react";
import { LETTERS, t } from "../utils/lang";
import { Brain, Cpu, Sparkles, Clock } from "lucide-react";
import { motion } from "framer-motion";

export default function Exam({ questions, mood, onFinish, lang, showConfidence = true }) {
  const [qi, setQi] = useState(0);
  const [answers, setAnswers] = useState(() => 
    Array(questions.length).fill(null).map(() => ({
      selected: null,
      confidence: null,
      clickSequence: [],
      timeTaken: 0
    }))
  );
  const [visited, setVisited] = useState(new Set([0]));
  const [qStartTime, setQStartTime] = useState(Date.now());
  const [totalSecondsLeft, setTotalSecondsLeft] = useState(questions.length * 30);
  const [submitting, setSubmitting] = useState(false);

  const q = questions[qi];
  const answersRef = useRef(answers);
  answersRef.current = answers;

  // Handle question navigation and accumulate time spent
  const navigateTo = (index) => {
    if (index < 0 || index >= questions.length) return;
    
    // Accumulate time spent on current question
    const elapsed = (Date.now() - qStartTime) / 1000;
    setAnswers(prev => {
      const copy = [...prev];
      copy[qi] = {
        ...copy[qi],
        timeTaken: copy[qi].timeTaken + elapsed
      };
      return copy;
    });

    setQi(index);
    setVisited(prev => {
      const next = new Set(prev);
      next.add(index);
      return next;
    });
    setQStartTime(Date.now());
  };

  // Option selection
  const selectOption = (optIndex) => {
    setAnswers(prev => {
      const copy = [...prev];
      const currentAns = copy[qi];
      const alreadySelected = currentAns.selected === optIndex;
      
      const newClickSequence = [...currentAns.clickSequence];
      if (!alreadySelected) {
        newClickSequence.push(LETTERS[optIndex]);
      }

      copy[qi] = {
        ...currentAns,
        selected: optIndex,
        clickSequence: newClickSequence
      };
      return copy;
    });
  };

  // Confidence selection
  const selectConfidence = (confValue) => {
    setAnswers(prev => {
      const copy = [...prev];
      copy[qi] = {
        ...copy[qi],
        confidence: confValue
      };
      return copy;
    });
  };

  // Submit Exam
  const submitExam = useCallback(() => {
    if (submitting) return;
    
    // Accumulate final question time
    const elapsed = (Date.now() - qStartTime) / 1000;
    const finalAnswers = [...answers];
    finalAnswers[qi] = {
      ...(finalAnswers[qi] || {}),
      timeTaken: (finalAnswers[qi]?.timeTaken || 0) + elapsed
    };

    setSubmitting(true);

    const finalItems = finalAnswers.map((ans, idx) => ({
      questionId: questions[idx].id,
      finalAnswerIndex: ans.selected,
      clickSequence: ans.clickSequence,
      timeTaken: Math.max(0.5, ans.timeTaken),
      confidence: ans.confidence || "none"
    }));

    Promise.resolve(onFinish(finalItems, mood)).catch(() => setSubmitting(false));
  }, [submitting, qStartTime, answers, qi, questions, onFinish, mood]);

  // Global Countdown Timer
  useEffect(() => {
    if (submitting) return;
    const timer = setInterval(() => {
      setTotalSecondsLeft(s => {
        if (s <= 1) {
          clearInterval(timer);
          submitExam();
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [qi, submitting, submitExam]);

  if (!q) return null;

  // HuggingFace ML Showcase Loading Screen
  if (submitting) {
    return (
      <div className="view" data-testid="exam-view">
        <div className="wrap" style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: "60vh", textAlign: "center" }}>
          <motion.div
            animate={{ scale: [1, 1.1, 1], rotate: [0, 5, -5, 0] }}
            transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
            style={{ marginBottom: 24, position: "relative" }}
          >
            <Brain size={64} style={{ color: "var(--accent)" }} />
            <motion.div
              animate={{ opacity: [0, 1, 0], scale: [0.8, 1.2, 0.8] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
              style={{ position: "absolute", top: -10, right: -10 }}
            >
              <Sparkles size={24} style={{ color: "var(--amber)" }} />
            </motion.div>
          </motion.div>
          
          <h2 style={{ fontSize: 24, marginBottom: 12, fontFamily: "var(--display)" }}>
            {lang === "bn" ? "HuggingFace ইনফারেন্স চলছে..." : "Running HuggingFace Inference..."}
          </h2>
          <p style={{ color: "var(--text-dim)", maxWidth: 350, margin: "0 auto 24px", lineHeight: 1.5 }}>
            {lang === "bn" 
              ? "BanglaBERT আপনার আচরণগত ডেটা (সময়, দ্বিধা, স্কিপ) বিশ্লেষণ করে আপনার জ্ঞানীয় প্রোফাইল তৈরি করছে।" 
              : "BanglaBERT is analyzing your behavioral data (timing, hesitations, skips) to map your cognitive profile."}
          </p>
          
          <div style={{ display: "flex", gap: 12, color: "var(--text-dim)", fontSize: 13, background: "var(--paper2)", padding: "8px 16px", borderRadius: 20, border: "1px solid var(--border)" }}>
            <span style={{ display: "flex", alignItems: "center", gap: 6 }}><Cpu size={14} /> T4 GPU x2</span>
            <span>|</span>
            <span style={{ display: "flex", alignItems: "center", gap: 6 }}>180M Parameters</span>
          </div>
        </div>
      </div>
    );
  }

  // Format time
  const formatTime = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  };

  const answeredCount = answers.filter(a => a.selected !== null).length;
  const progressPercent = (answeredCount / questions.length) * 100;

  return (
    <div className="min-h-screen bg-[#FCF7F0] pt-[68px]" data-testid="exam-view">
      <div className="flex flex-col md:flex-row min-h-[calc(100vh-68px)] max-w-[1400px] mx-auto">
        {/* Sidebar */}
        <aside className="w-full md:w-[280px] shrink-0 border-b md:border-b-0 md:border-r border-[#E4D8CA] bg-white flex flex-col md:sticky top-[68px] md:h-[calc(100vh-68px)] z-10 order-2 md:order-1">
          <div className="p-4 md:p-5 border-b border-[#E4D8CA]">
            <div className="text-[11px] font-bold uppercase tracking-[0.14em] text-slate-400 mb-2">
              {lang === "bn" ? "পরীক্ষার অগ্রগতি" : "Question Progress"}
            </div>
            <div style={{ fontSize: 28, fontFamily: "var(--display)", fontWeight: 600, lineHeight: 1 }}>
              {answeredCount}<span style={{ fontSize: 16, color: "var(--muted)" }}> / {questions.length}</span>
            </div>
            <div style={{ marginTop: 10, height: 8, background: "var(--paper2)", borderRadius: 999, overflow: "hidden" }}>
              <div style={{ height: "100%", width: `${progressPercent}%`, background: "var(--sage)", borderRadius: 999, transition: "width .5s" }}></div>
            </div>
            <div style={{ display: "flex", gap: 16, marginTop: 10, fontSize: "11.5px", color: "var(--muted)" }}>
              <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                <span style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--sage)" }}></span>
                {lang === "bn" ? "উত্তর দেওয়া" : "Answered"}
              </span>
              <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                <span style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--ochre)" }}></span>
                {lang === "bn" ? "বাকি আছে" : "Skipped/Todo"}
              </span>
            </div>
          </div>

          <div style={{ padding: 16, flex: 1, overflowY: "auto" }}>
            <div style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: ".14em", color: "var(--muted)", marginBottom: 12 }}>
              {lang === "bn" ? "প্রশ্ন গ্রিড" : "Question Grid"}
            </div>
            <div className="q-grid" style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8, padding: 0 }}>
              {questions.map((_, idx) => {
                const ans = answers[idx];
                const isCurrent = idx === qi;
                const isAnswered = ans.selected !== null;
                const isVisited = visited.has(idx);

                let dotClass = "todo";
                if (isCurrent) dotClass = "current";
                else if (isAnswered) dotClass = "answered";
                else if (isVisited) dotClass = "skipped";

                return (
                  <button 
                    key={idx}
                    className={`q-dot ${dotClass}`} 
                    onClick={() => navigateTo(idx)}
                    style={{
                      width: 36,
                      height: 36,
                      borderRadius: 8,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 12,
                      fontWeight: 600,
                      cursor: "pointer",
                      transition: "all .12s",
                      fontFamily: "inherit",
                      border: isCurrent ? "1.5px solid var(--brand)" : "1px solid var(--line)",
                      backgroundColor: isCurrent ? "var(--brand)" : isAnswered ? "var(--sage)" : isVisited ? "var(--ochreSoft)" : "white",
                      color: isCurrent ? "white" : isAnswered ? "white" : isVisited ? "var(--ochre)" : "var(--muted)"
                    }}
                  >
                    {idx + 1}
                  </button>
                );
              })}
            </div>
          </div>

          <div style={{ padding: "14px 16px", borderTop: "1px solid var(--line)" }}>
            <button className="btn btn-ghost w-full" style={{ padding: 11, borderRadius: 10 }} onClick={submitExam}>
              {lang === "bn" ? "পরীক্ষা শেষ করুন" : "End Exam"}
            </button>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 8, fontSize: "11.5px", color: "var(--muted)" }}>
              <span>{lang === "bn" ? "অটো-সেভড" : "Auto-saved"}</span>
              <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#22c55e" }}></span>
                {lang === "bn" ? "লাইভ" : "Live"}
              </span>
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col order-1 md:order-2">
          {/* Top Bar */}
          <div className="px-5 md:px-10 py-3 md:py-4 border-b border-[#E4D8CA] flex items-center justify-between bg-white/90 backdrop-blur-md sticky top-[68px] md:top-0 z-[9]">
            <div>
              <div className="text-[10px] md:text-[11px] font-bold tracking-[0.15em] uppercase text-slate-400 text-left">
                {lang === "bn" ? `${q.chapter} · প্রশ্ন ${qi + 1}` : `Biology · ${q.chapter} · Q${qi + 1}`}
              </div>
            </div>
            <div className={`flex items-center gap-1.5 font-['Hind Siliguri'] text-xl md:text-2xl font-semibold ${totalSecondsLeft < 60 ? "text-[#C03A2A]" : "text-[#D34A20]"}`}>
              <Clock size={18} /> {formatTime(totalSecondsLeft)}
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button className="btn btn-ghost" style={{ padding: "7px 14px", fontSize: "12.5px", borderRadius: 8 }} onClick={() => navigateTo(qi + 1)}>
                {t("skip", lang)}
              </button>
            </div>
          </div>

          {/* Question and Options */}
          <div className="exam-main" style={{ flex: 1, padding: "32px 40px", maxWidth: 720, margin: "0 auto", width: "100%" }}>
            <div className="q-number" style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".15em", textTransform: "uppercase", color: "var(--muted)", marginBottom: 8, textAlign: "left" }}>
              {lang === "bn" ? `প্রশ্ন ${qi + 1} (মোট ${questions.length} এর)` : `Question ${qi + 1} of ${questions.length}`}
            </div>
            <h1 className={`q-text ${lang === "bn" ? "bengali" : ""}`} style={{ fontSize: 24, lineHeight: 1.55, fontWeight: 600, marginBottom: 28, textAlign: "left" }}>
              {q.text}
            </h1>

            <div className="options" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {q.options.map((opt, optIdx) => {
                const isSelected = answers[qi].selected === optIdx;
                return (
                  <button 
                    key={optIdx} 
                    className={`option-btn ${isSelected ? "selected" : ""}`}
                    onClick={() => selectOption(optIdx)}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 14,
                      padding: "16px 20px",
                      borderRadius: 14,
                      border: isSelected ? "1.5px solid var(--brand)" : "1.5px solid var(--line)",
                      background: isSelected ? "var(--brandSoft)" : "white",
                      cursor: "pointer",
                      fontFamily: "inherit",
                      fontSize: 15,
                      textAlign: "left",
                      transition: "all .15s"
                    }}
                  >
                    <span className="option-letter" style={{ width: 28, height: 28, borderRadius: 8, background: isSelected ? "var(--brand)" : "var(--paper2)", color: isSelected ? "white" : "var(--muted)", fontWeight: 700, fontSize: 13, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                      {LETTERS[optIdx]}
                    </span>
                    <span style={{ color: "var(--ink)" }}>{opt}</span>
                  </button>
                );
              })}
            </div>

            {/* Confidence Tracking Block */}
            {showConfidence && answers[qi].selected !== null && (
              <div className="confidence" style={{ marginTop: 24, padding: "16px 20px", background: "white", border: "1px solid var(--line)", borderRadius: 14, display: "flex", alignItems: "center", justifyContent: "space-between", animation: "fadeUp .35s ease both" }}>
                <span style={{ fontSize: "13.5px", fontWeight: 600 }}>{t("confLabel", lang)}</span>
                <div style={{ display: "flex", gap: 8 }}>
                  {[["sure", t("confSure", lang)], ["unsure", t("confUnsure", lang)], ["guessing", t("confGuessing", lang)]].map(([key, label]) => {
                    const isSelected = answers[qi].confidence === key;
                    return (
                      <button 
                        key={key} 
                        className="btn" 
                        onClick={() => selectConfidence(key)}
                        style={{
                          padding: "6px 14px",
                          fontSize: "12.5px",
                          borderRadius: 8,
                          border: isSelected ? "none" : "1.5px solid var(--line)",
                          background: isSelected ? "var(--sageSoft)" : "white",
                          color: isSelected ? "var(--sage)" : "var(--muted)",
                          fontWeight: 600
                        }}
                      >
                        {label}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Action Bar footer */}
          <div className="sticky bottom-0 bg-white/95 backdrop-blur-md border-t border-[#E4D8CA] px-5 md:px-10 py-3 md:py-4 flex items-center justify-between z-[8]">
            <button 
              className="px-4 py-2.5 rounded-xl text-[14px] font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-50 transition-colors"
              disabled={qi === 0}
              onClick={() => navigateTo(qi - 1)}
            >
              {lang === "bn" ? "← পূর্ববর্তী" : "← Prev"}
            </button>
            <div className="text-[13px] font-medium text-slate-500">
              {qi + 1} / {questions.length}
            </div>
            {qi < questions.length - 1 ? (
              <button 
                className="px-5 py-2.5 rounded-xl text-[14px] font-medium bg-[#D34A20] text-white hover:bg-[#B93D18] shadow-sm transition-colors"
                onClick={() => navigateTo(qi + 1)}
              >
                {lang === "bn" ? "পরবর্তী →" : "Next →"}
              </button>
            ) : (
              <button 
                className="px-5 py-2.5 rounded-xl text-[14px] font-medium bg-[#395F54] text-white hover:bg-[#2B4A41] shadow-sm transition-colors"
                onClick={submitExam}
              >
                {lang === "bn" ? "পরীক্ষা শেষ →" : "Finish →"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
