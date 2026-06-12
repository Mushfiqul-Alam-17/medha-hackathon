import { useState, useEffect } from "react";
import { Download, Sparkles, BookOpen, Layers, CheckCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { t } from "../utils/lang";
import { useReveal, useToast } from "../hooks/useAnimations";

const BACKEND = import.meta.env.VITE_BACKEND_URL || (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" ? "http://localhost:8000" : "https://medha-api.onrender.com");

function PremiumNotesLoader({ lang }) {
  const [step, setStep] = useState(0);

  const steps = lang === "bn" ? [
    { text: "আপনার আচরণগত ডেটা বিশ্লেষণ করা হচ্ছে (সময়, দ্বিধা, অপশন বদল)...", icon: Layers, color: "var(--brand)" },
    { text: "ভুল ও ধীর উত্তরের কনসেপ্টগুলো চিহ্নিত করা হচ্ছে...", icon: Sparkles, color: "var(--ochre)" },
    { text: "NCTB পাঠ্যবইয়ের পৃষ্ঠা এবং প্রাসঙ্গিক টপিক ম্যাচ করা হচ্ছে...", icon: BookOpen, color: "var(--sage)" },
    { text: "আপনার জন্য কাস্টম মেমোরি ট্রিকস ও ব্যাখ্যা সাজানো হচ্ছে...", icon: CheckCircle, color: "var(--brand)" }
  ] : [
    { text: "Analyzing behavioral response patterns (timing, switches, hesitation)...", icon: Layers, color: "var(--brand)" },
    { text: "Isolating weak concepts and blind spots...", icon: Sparkles, color: "var(--ochre)" },
    { text: "Mapping concepts to NCTB Textbook pages and chapters...", icon: BookOpen, color: "var(--sage)" },
    { text: "Compiling personalized memory tricks and trap explanations...", icon: CheckCircle, color: "var(--brand)" }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setStep((s) => (s + 1) % steps.length);
    }, 2000);
    return () => clearInterval(interval);
  }, [steps.length]);

  const CurrentIcon = steps[step].icon;

  return (
    <div className="notes-loading-premium" style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: "50vh", textAlign: "center", padding: "40px 20px" }}>
      <div style={{ position: "relative", marginBottom: 32 }}>
        <motion.div
          animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.6, 0.3] }}
          transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
          style={{
            position: "absolute",
            top: -20,
            left: -20,
            right: -20,
            bottom: -20,
            borderRadius: "50%",
            background: `radial-gradient(circle, ${steps[step].color}33 0%, transparent 70%)`,
            filter: "blur(10px)"
          }}
        />
        
        <motion.div
          key={step}
          initial={{ scale: 0.8, opacity: 0, rotate: -10 }}
          animate={{ scale: 1, opacity: 1, rotate: 0 }}
          exit={{ scale: 0.8, opacity: 0, rotate: 10 }}
          transition={{ type: "spring", stiffness: 100, damping: 10 }}
          style={{
            width: 80,
            height: 80,
            borderRadius: "20px",
            background: "rgba(255, 255, 255, 0.02)",
            border: `1px solid ${steps[step].color}44`,
            display: "grid",
            placeItems: "center",
            color: steps[step].color,
            boxShadow: `0 8px 32px -8px ${steps[step].color}22`
          }}
        >
          <CurrentIcon size={40} />
        </motion.div>

        <motion.div
          animate={{ y: [0, -10, 0], opacity: [0.5, 1, 0.5] }}
          transition={{ repeat: Infinity, duration: 1.5, delay: 0.2 }}
          style={{ position: "absolute", top: -8, right: -8, color: "var(--ochre)" }}
        >
          <Sparkles size={18} />
        </motion.div>
      </div>

      <div style={{ minHeight: 80, display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
        <AnimatePresence mode="wait">
          <motion.p
            key={step}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            style={{
              fontSize: 18,
              fontWeight: 600,
              color: "var(--ink)",
              maxWidth: 450,
              margin: 0,
              lineHeight: 1.5,
              fontFamily: "'Hind Siliguri', serif"
            }}
          >
            {steps[step].text}
          </motion.p>
        </AnimatePresence>
        
        <motion.span
          animate={{ opacity: [0.4, 0.8, 0.4] }}
          transition={{ repeat: Infinity, duration: 1.8 }}
          style={{
            fontSize: 12,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            fontWeight: 700,
            color: "var(--muted)"
          }}
        >
          {lang === "bn" ? "অ্যালগরিদম প্রসেসিং..." : "Algorithm processing..."}
        </motion.span>
      </div>

      <div style={{ display: "flex", gap: 8, marginTop: 24 }}>
        {steps.map((_, idx) => (
          <div
            key={idx}
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              backgroundColor: idx === step ? steps[step].color : "var(--line)",
              transition: "background-color 0.3s ease"
            }}
          />
        ))}
      </div>
    </div>
  );
}

function PDFLink({ pdfFile, pdfPage, lang, onOpenPdf, correctAnswer }) {
  if (!pdfFile || !pdfPage) return null;
  const handleClick = (e) => {
    if (onOpenPdf) {
      e.preventDefault();
      onOpenPdf(pdfFile, pdfPage, correctAnswer);
    }
  };
  return (
    <div className="note-pdf-link" style={{ marginTop: 16, display: "flex", justifyContent: "flex-end" }}>
      <button
        onClick={handleClick}
        className="btn btn-ghost" 
        style={{ padding: "6px 12px", fontSize: 12.5, display: "inline-flex", alignItems: "center", gap: 6, borderRadius: 8 }}
      >
        <BookOpen size={14} />
        {lang === "bn" ? `বইয়ে রি-রিড করুন (পৃষ্ঠা ${pdfPage})` : `Reread Textbook (Page ${pdfPage})`}
      </button>
    </div>
  );
}

function NoteRow({ label, children }) {
  return (
    <div className="note-row" style={{ marginTop: 12 }}>
      <span className="note-lbl" style={{ display: "block", fontSize: 11, fontWeight: 700, letterSpacing: ".1em", textTransform: "uppercase", color: "var(--muted)", marginBottom: 4 }}>
        {label}
      </span>
      <div className="note-val" style={{ fontSize: 14.5, color: "var(--ink)", lineHeight: 1.6 }}>{children}</div>
    </div>
  );
}

function ComparisonTable({ rows }) {
  if (!rows || rows.length === 0) return null;
  return (
    <div className="cmp-table-v2" style={{ marginTop: 14, display: "flex", flexDirection: "column", gap: 8 }}>
      {rows.map((row, j) => (
        <div className={`cmp-row-v2 ${row.isCorrect ? "correct" : "wrong"}`} key={j} style={{
          padding: "12px 16px",
          borderRadius: "var(--r-sm)",
          background: row.isCorrect ? "var(--masterSoft)" : "var(--dangerSoft)",
          borderLeft: `3px solid ${row.isCorrect ? "var(--master)" : "var(--danger)"}`
        }}>
          <div className="cmp-concept" style={{ fontSize: 13, fontWeight: 700, color: row.isCorrect ? "var(--master)" : "var(--danger)", marginBottom: 4 }}>
            {row.isCorrect ? "✓" : "✗"} {row.concept}
          </div>
          <div className="cmp-desc" style={{ fontSize: 13.5, color: "var(--ink)", lineHeight: 1.5 }}>
            {row.description}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function StudyNotes({ loading, notes, source, onDownload, lang, onOpenPdf }) {
  const [filter, setFilter] = useState("all"); // "all" | "danger" | "confused" | "slow"
  const empty = notes && !notes.slow?.length && !notes.confused?.length && !notes.danger?.length;
  const showToast = useToast();
  const headerRef = useReveal();

  const totalNotesCount = notes
    ? (notes.slow?.length || 0) + (notes.confused?.length || 0) + (notes.danger?.length || 0)
    : 0;

  // Render notes with local numbering index
  const renderNoteCard = (n, type, idx) => {
    let tagBg = "var(--brandSoft)";
    let tagColor = "var(--brand)";
    let tagText = "";
    
    if (type === "danger") {
      tagBg = "var(--dangerSoft)";
      tagColor = "var(--danger)";
      tagText = lang === "bn" ? `⚠️ বিপদ জোন · Section ${idx}` : `⚠️ Danger Zone · Section ${idx}`;
    } else if (type === "confused") {
      tagBg = "var(--confSoft)";
      tagColor = "var(--confused)";
      tagText = lang === "bn" ? `🔀 গোলমাল জোন · Section ${idx}` : `🔀 Confused Zone · Section ${idx}`;
    } else if (type === "slow") {
      tagBg = "var(--slowSoft)";
      tagColor = "var(--slow)";
      tagText = lang === "bn" ? `🐢 ধীর গতি জোন · Section ${idx}` : `🐢 Slow Zone · Section ${idx}`;
    }

    return (
      <div className="card note-card" key={type + idx} style={{ padding: 28, marginBottom: 16, background: "var(--card)" }}>
        <span className="note-tag" style={{ background: tagBg, color: tagColor, display: "inline-flex", alignItems: "center", gap: 6, padding: "4px 10px", borderRadius: 99, fontSize: 11, fontWeight: 700, textTransform: "uppercase", marginBottom: 14 }}>
          {tagText}
        </span>
        <div className="note-concept" style={{ fontSize: 20, fontWeight: 700, fontFamily: "'Hind Siliguri', serif", color: "var(--ink)", marginBottom: 10 }}>
          {n.topic}
        </div>
        
        {n.explanation && <NoteRow label={t("explanation", lang)}>{n.explanation}</NoteRow>}
        
        {/* Phenotype-specific components */}
        {type === "slow" && n.speedNote && (
          <div className="note-speed-callout" style={{ marginTop: 12, padding: "12px 16px", background: "var(--paper2)", borderRadius: 12, fontSize: 13.5, color: "var(--muted)" }}>
            ⏱ {n.speedNote}
          </div>
        )}

        {n.comparisonTable && n.comparisonTable.length > 0 && (
          <ComparisonTable rows={n.comparisonTable} />
        )}

        {type === "danger" && n.dangerNote && (
          <div className="note-danger-callout" style={{ marginTop: 12, padding: "14px 18px", background: "var(--dangerSoft)", borderRadius: 12, borderLeft: "3px solid var(--danger)", fontSize: 13.5, color: "var(--ink)" }}>
            ⚠️ {n.dangerNote}
          </div>
        )}

        {n.whyCorrect && <NoteRow label={t("whyCorrect", lang)}>{n.whyCorrect}</NoteRow>}
        {n.whyTricked && <NoteRow label={t("whyTricked", lang)}>{n.whyTricked}</NoteRow>}
        
        {n.memoryTrick && (
          <div className="note-memory-callout" style={{ marginTop: 14, padding: "12px 16px", background: "var(--ochreSoft)", color: "var(--ochre)", borderRadius: 12, fontSize: 13.5 }}>
            💡 {lang === "bn" ? "মনে রাখার শর্টকাট:" : "Memory Shortcut:"} <strong>{n.memoryTrick}</strong>
          </div>
        )}

        {n.trapQuestion && (
          <div className="note-trap" style={{ marginTop: 12, fontSize: 13, color: "var(--muted)", fontStyle: "italic" }}>
            🪤 {t("trapQ", lang)} "{n.trapQuestion}"
          </div>
        )}

        {n.textbook_ref && (
          <div className="note-textbook-ref" style={{ marginTop: 14, fontSize: 13.5, color: "var(--muted)", fontFamily: "'Hind Siliguri', serif" }}>
            📖 <strong>{lang === "bn" ? "মূল বই রেফারেন্স:" : "Textbook Ref:"}</strong> {n.textbook_ref}
          </div>
        )}

        <PDFLink pdfFile={n.pdfFile || n.pdf_file} pdfPage={n.pdfPage || n.pdf_page} lang={lang} onOpenPdf={onOpenPdf} correctAnswer={n.correct_answer} />
      </div>
    );
  };

  // Compile list based on active filter
  const renderList = () => {
    let results = [];
    let counter = 0;

    if (filter === "all" || filter === "danger") {
      notes.danger?.forEach((n) => {
        counter++;
        results.push({ n, type: "danger", index: counter });
      });
    }
    if (filter === "all" || filter === "confused") {
      notes.confused?.forEach((n) => {
        counter++;
        results.push({ n, type: "confused", index: counter });
      });
    }
    if (filter === "all" || filter === "slow") {
      notes.slow?.forEach((n) => {
        counter++;
        results.push({ n, type: "slow", index: counter });
      });
    }

    return results.map(({ n, type, index }) => renderNoteCard(n, type, index));
  };

  return (
    <div className="view fade-in" data-testid="notes-view" style={{ background: "var(--paper)" }}>
      <div className="container-md screen-inner" style={{ paddingTop: 32 }}>
        
        {/* Header */}
        <div ref={headerRef} className="reveal" style={{ marginBottom: 28 }}>
          <div className="eyebrow" style={{ marginBottom: 8 }}>{t("notesEyebrow", lang)}</div>
          <h1 className="display" style={{ fontSize: "clamp(34px, 5vw, 50px)", marginBottom: 10 }}>
            {t("notesTitle", lang)}
          </h1>
          <p style={{ fontSize: 15, color: "var(--muted)", maxWidth: 500, lineHeight: 1.7 }}>
            {t("notesSub", lang)}
          </p>
        </div>

        {loading && (
          <PremiumNotesLoader lang={lang} />
        )}

        {!loading && empty && (
          <div className="card" data-testid="notes-empty" style={{ padding: 40, textAlign: "center" }}>
            <p style={{ color: "var(--muted)", fontSize: 16 }}>{t("notesEmpty", lang)}</p>
          </div>
        )}

        {!loading && notes && !empty && (
          <>
            {/* Filter Tabs + Download */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
              <div className="filter-bar" style={{ marginBottom: 0, display: "flex", gap: 6, flexWrap: "wrap" }}>
                <button className={`filter-pill ${filter === "all" ? "active" : ""}`} onClick={() => setFilter("all")}>
                  {lang === "bn" ? `সব (${totalNotesCount})` : `All (${totalNotesCount})`}
                </button>
                <button className={`filter-pill ${filter === "danger" ? "active" : ""}`} onClick={() => setFilter("danger")}>
                  {lang === "bn" ? `বিপদ (${notes.danger?.length || 0})` : `Danger (${notes.danger?.length || 0})`}
                </button>
                <button className={`filter-pill ${filter === "confused" ? "active" : ""}`} onClick={() => setFilter("confused")}>
                  {lang === "bn" ? `গোলমাল (${notes.confused?.length || 0})` : `Confused (${notes.confused?.length || 0})`}
                </button>
                <button className={`filter-pill ${filter === "slow" ? "active" : ""}`} onClick={() => setFilter("slow")}>
                  {lang === "bn" ? `ধীর গতি (${notes.slow?.length || 0})` : `Slow (${notes.slow?.length || 0})`}
                </button>
              </div>
              <button className="btn btn-primary" style={{ borderRadius: 10, padding: "10px 18px", fontSize: 13, display: "inline-flex", alignItems: "center", gap: 6 }} onClick={() => {
                if (onDownload) onDownload();
                showToast(lang === "bn" ? "✅ নোটস ডাউনলোড হচ্ছে..." : "✅ Downloading notes...");
              }}>
                <Download size={14} />
                {t("download", lang)}
              </button>
            </div>

            {/* Note Cards List */}
            <div className="notes-list-container">
              {renderList()}
            </div>

            {source && (
              <div className="note-src" style={{ textAlign: "center", padding: "20px 0", fontSize: 12.5, color: "var(--muted)", borderTop: "1px solid var(--line)", marginTop: 32 }}>
                — {
                  source === "groq" ? "✨ AI-generated · Powered by Groq (Llama 3.3 70B)" :
                  source === "openrouter" ? "✨ AI-generated · Powered by OpenRouter (Gemma 4)" :
                  source === "gemini" ? "✨ AI-generated · Powered by Google Gemini" :
                  source === "fallback" ? "📚 MEDHA Behavioral Notes (Offline Mode)" :
                  "✨ AI-generated Study Notes"
                } —
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
