import { useEffect, useState, useCallback, useMemo } from "react";
import axios from "axios";
import { Toaster, toast } from "sonner";
import "@/App.css";

import IntroAnimation from "@/components/IntroAnimation";
import NavBar from "@/components/NavBar";
import Landing from "@/components/Landing";
import MoodCheck from "@/components/MoodCheck";
import Exam from "@/components/Exam";
import Result from "@/components/Result";
import DnaReport from "@/components/DnaReport";
import ClassifierPanel from "@/components/ClassifierPanel";
import StudyNotes from "@/components/StudyNotes";
import Readiness from "@/components/Readiness";
import AnxietyScore from "@/components/AnxietyScore";
import ShareCard from "@/components/ShareCard";
import History from "@/components/History";
import { localizeQuestion, localizeResultItem } from "@/utils/medha";

const BACKEND = import.meta.env.VITE_BACKEND_URL || (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" ? "http://localhost:8000" : "https://medha-api.onrender.com");
const API = `${BACKEND}/api`;

const MOCK_ATTEMPT = {
  id: "mock-session",
  score: 74,
  total: 12,
  accuracy: 75,
  mood: "great",
  readiness: {
    correct: 9,
    total: 12,
    avgTime: "18.4s",
    score: 73
  },
  groups: {
    master: [
      { questionId: 1, chapter: "Cell Biology", questionText: "Which organelle is known as the powerhouse of the cell?", finalAnswerIndex: 1, options: ["Nucleus", "Mitochondria", "Ribosome", "Golgi"], isCorrect: true, timeTaken: 4, clickSequence: ["B"], switchCount: 0, group: "master", confidence: "sure" }
    ],
    slow: [
      { questionId: 2, chapter: "Genetics", questionText: "Which chamber of the heart pumps oxygenated blood to the body?", finalAnswerIndex: 2, options: ["Left Atrium", "Right Ventricle", "Left Ventricle", "Right Atrium"], isCorrect: true, timeTaken: 52, clickSequence: ["B", "C"], switchCount: 1, group: "slow", confidence: "unsure" }
    ],
    confused: [
      { questionId: 3, chapter: "Plant Anatomy", questionText: "The tissue responsible for transport of water in plants is:", finalAnswerIndex: 2, options: ["Phloem", "Parenchyma", "Xylem", "Sclerenchyma"], isCorrect: true, timeTaken: 48, clickSequence: ["A", "C"], switchCount: 2, group: "confused", confidence: "unsure" }
    ],
    danger: [
      { questionId: 4, chapter: "Plant Anatomy", questionText: "Osmosis is the movement of water from...", finalAnswerIndex: 0, options: ["High solute to low solute concentration", "Low solute to high solute concentration", "High pressure to low pressure", "None of the above"], isCorrect: false, timeTaken: 6, clickSequence: ["A"], switchCount: 0, group: "danger", confidence: "sure" }
    ]
  },
  items: [
    { questionId: 1, chapter: "Cell Biology", questionText: "Which organelle is known as the powerhouse of the cell?", finalAnswerIndex: 1, options: ["Nucleus", "Mitochondria", "Ribosome", "Golgi"], isCorrect: true, timeTaken: 4, clickSequence: ["B"], switchCount: 0, group: "master", confidence: "sure" },
    { questionId: 2, chapter: "Genetics", questionText: "Which chamber of the heart pumps oxygenated blood to the body?", finalAnswerIndex: 2, options: ["Left Atrium", "Right Ventricle", "Left Ventricle", "Right Atrium"], isCorrect: true, timeTaken: 52, clickSequence: ["B", "C"], switchCount: 1, group: "slow", confidence: "unsure" },
    { questionId: 3, chapter: "Plant Anatomy", questionText: "The tissue responsible for transport of water in plants is:", finalAnswerIndex: 2, options: ["Phloem", "Parenchyma", "Xylem", "Sclerenchyma"], isCorrect: true, timeTaken: 48, clickSequence: ["A", "C"], switchCount: 2, group: "confused", confidence: "unsure" },
    { questionId: 4, chapter: "Plant Anatomy", questionText: "Osmosis is the movement of water from...", finalAnswerIndex: 0, options: ["High solute to low solute concentration", "Low solute to high solute concentration", "High pressure to low pressure", "None of the above"], isCorrect: false, timeTaken: 6, clickSequence: ["A"], switchCount: 0, group: "danger", confidence: "sure" }
  ]
};

const MOCK_NOTES = {
  danger: [
    {
      topic: "Osmosis: Direction of Water Movement",
      explanation: "You answered that osmosis moves water from high solute to low solute concentration. This is a critical misconception reversal.",
      dangerNote: "Osmosis is the movement of water molecules from a region of lower solute concentration (higher water potential) to a region of higher solute concentration (lower water potential) through a semi-permeable membrane.",
      memoryTrick: "Solvent moves, not solute — remember this distinction",
      trapQuestion: "Hypotonic solution → water moves INTO the cell; Hypertonic solution → water moves OUT of the cell",
      pdf_file: "ABUL_HASAN_BIO_1st_paper.pdf",
      pdf_page: 42,
      textbook_ref: "আবুল হাসান স্যার, ১ম পত্র, পৃষ্ঠা 42",
      correct_answer: "B"
    }
  ],
  confused: [
    {
      topic: "Xylem vs Phloem: Transport Functions",
      explanation: "You switched between answers 3 times on this question. The confusion is between two transport tissue types.",
      comparisonTable: [
        { concept: "XYLEM ✓", description: "Transports water & minerals from roots → leaves. Unidirectional.", isCorrect: true },
        { concept: "PHLOEM", description: "Transports sugars & food from leaves → all parts. Bidirectional.", isCorrect: false }
      ],
      pdf_file: "ABUL_HASAN_BIO_1st_paper.pdf",
      pdf_page: 88,
      textbook_ref: "আবুল হাসান স্যার, ১ম পত্র, পৃষ্ঠা 88",
      correct_answer: "A"
    }
  ],
  slow: [
    {
      topic: "Heart Chambers: Oxygenated Blood Flow",
      explanation: "You got this right but took 52 seconds with significant hesitation. This needs fluency, not knowledge.",
      speedNote: "Quick recall chain: Lungs → Left Atrium → Left Ventricle → Body. The left ventricle is the strongest — it pumps against full systemic resistance.",
      memoryTrick: "Left side = oxygenated blood (just came from lungs); Right side = deoxygenated blood",
      pdf_file: "Azmol_BIO_2nd_paper.pdf",
      pdf_page: 154,
      textbook_ref: "গাজী আজমল স্যার, ২য় পত্র, পৃষ্ঠা 154",
      correct_answer: "C"
    }
  ]
};

function notesToMarkdown(notes) {
  let md = "# MEDHA — Personalized Study Notes\n\n";
  (notes.sections || []).forEach((section) => {
    md += `## ${section.header}\n${section.description}\n\n`;
    (section.items || []).forEach((item) => {
      md += `### ${item.topic}\n- **Explanation:** ${item.explanation || ""}\n- **Insight:** ${item.frame || ""}\n- **Memory Trick:** ${item.memory_trick || ""}\n- **Trap:** ${item.trap_note || ""}\n\n`;
    });
  });
  return md;
}

function parseNotes(sections) {
  const slow = [];
  const confused = [];
  const danger = [];
  
  (sections || []).forEach(sec => {
    const header = sec.header || "";
    const items = sec.items || [];
    if (header.includes("Priority Focus")) {
      items.forEach(item => {
        danger.push({
          topic: item.topic,
          explanation: item.explanation,
          dangerNote: item.frame,
          whyCorrect: item.correct_answer ? `সঠিক উত্তর: ${item.correct_answer}` : null,
          whyTricked: item.wrong_answer ? `তোমার উত্তর: ${item.wrong_answer}` : null,
          memoryTrick: item.memory_trick,
          trapQuestion: item.trap_note,
          pdf_file: item.pdf_file,
          pdf_page: item.pdf_page,
          textbook_ref: item.textbook_ref,
          correct_answer: item.correct_answer
        });
      });
    } else if (header.includes("Trust Gap")) {
      items.forEach(item => {
        slow.push({
          topic: item.topic,
          explanation: item.explanation,
          speedNote: item.frame,
          memoryTrick: item.memory_trick,
          pdf_file: item.pdf_file,
          pdf_page: item.pdf_page,
          textbook_ref: item.textbook_ref,
          correct_answer: item.correct_answer
        });
      });
    } else if (header.includes("Growth Area")) {
      items.forEach(item => {
        confused.push({
          topic: item.topic,
          explanation: item.explanation,
          memoryTrick: item.memory_trick,
          comparisonTable: item.confusable_note ? [
            { concept: "মনে রেখো", description: item.confusable_note, isCorrect: true }
          ] : [],
          pdf_file: item.pdf_file,
          pdf_page: item.pdf_page,
          textbook_ref: item.textbook_ref,
          correct_answer: item.correct_answer
        });
      });
    }
  });

  return {
    sections: sections,
    slow,
    confused,
    danger
  };
}

export default function App() {
  const [introDone, setIntroDone] = useState(true);
  const [view, setView] = useState("landing");
  const [questions, setQuestions] = useState([]);
  const [sessionQuestions, setSessionQuestions] = useState([]);
  const [chapters, setChapters] = useState([]);
  const [attempt, setAttempt] = useState(null);
  const [notes, setNotes] = useState(null);
  const [notesLoading, setNotesLoading] = useState(false);
  const [notesSource, setNotesSource] = useState(null);
  const [history, setHistory] = useState([]);
  const [studentId, setStudentId] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [lang, setLang] = useState("en");
  const [showConfidence, setShowConfidence] = useState(true);
  const [activePdf, setActivePdf] = useState(null);
  
  const handleOpenPdf = (file, page, searchKeyword = "") => {
    setActivePdf({ file, page, searchKeyword });
  };

  useEffect(() => {
    // 1. Authenticate Demo Student
    axios.post(`${API}/students/login`, { username: "demo_student" })
      .then((r) => setStudentId(r.data.student_id))
      .catch(() => {});
      
    // 2. Load general metadata
    axios.get(`${API}/questions/chapters`).then((r) => setChapters(r.data)).catch(() => {});
  }, []);

  // Load history
  const refreshHistory = useCallback(() => {
    if (!studentId) return;
    axios.get(`${API}/profile/${studentId}/history`).then((r) => setHistory(r.data.sessions)).catch(() => {});
  }, [studentId]);

  useEffect(() => { refreshHistory(); }, [refreshHistory]);

  const examDone = !!attempt;

  const handleStart = () => setView("mood");

  const handleMoodContinue = async (mood, confidenceEnabled) => {
    setShowConfidence(confidenceEnabled);
    window.__medhaMood = mood;
    
    try {
      const { data } = await axios.post(`${API}/sessions/start`, {
        student_id: studentId,
        mood: mood,
        question_count: 15,
        chapter: "TEST15"
      });
      setSessionId(data.session_id);
      setSessionQuestions(data.questions);
      setQuestions(data.questions.map((q) => localizeQuestion(q, lang)));
      setView("exam");
    } catch(e) {
      toast.error("Failed to start session.");
    }
  };

  const handleFinish = async (items, mood) => {
    try {
      const LETTERS = ["A", "B", "C", "D"];
      const { data } = await axios.post(`${API}/sessions/complete`, {
        session_id: sessionId,
        items: items.map(i => ({
          session_id: sessionId,
          question_id: i.questionId,
          click_path: i.clickSequence || [],
          final_answer: i.finalAnswerIndex !== null && i.finalAnswerIndex !== undefined ? LETTERS[i.finalAnswerIndex] : null,
          confidence_tap: i.confidence === "none" ? null : i.confidence,
          time_taken: i.timeTaken,
          time_expired: false, // Legacy exam didn't flag this separately
          skipped: i.finalAnswerIndex === null || i.finalAnswerIndex === undefined
        }))
      });
      
      const masterIds = new Set((data.dna_groups.MASTERY || []).map(x => x.question_id));
      const dangerIds = new Set((data.dna_groups.PRIORITY_FOCUS || []).map(x => x.question_id));
      const slowIds = new Set((data.dna_groups.TRUST_GAP || []).map(x => x.question_id));
      const confusedIds = new Set((data.dna_groups.GROWTH_AREA || []).map(x => x.question_id));

      // Map new backend payload to legacy frontend format
      const mapItem = (r) => {
        let group = "slow";
        if (masterIds.has(r.question_id)) group = "master";
        else if (dangerIds.has(r.question_id)) group = "danger";
        else if (slowIds.has(r.question_id)) group = "slow";
        else if (confusedIds.has(r.question_id)) group = "confused";

        return {
          questionId: r.question_id,
          finalAnswerIndex: r.final_answer ? LETTERS.indexOf(r.final_answer) : null,
          isCorrect: r.is_correct,
          confidence: r.confidence_tap,
          questionText: r.question_bn,
          question_bn: r.question_bn,
          question_en: r.question_en,
          options: r.options_bn,
          options_bn: r.options_bn,
          options_en: r.options_en,
          correctAnswerIndex: r.correct_answer ? LETTERS.indexOf(r.correct_answer) : 0,
          chapter: r.chapter_name,
          chapter_name: r.chapter_name,
          topic: r.topic,
          timeTaken: r.time_taken,
          clickSequence: r.click_path || [],
          switchCount: r.click_path ? Math.max(0, r.click_path.length - 1) : 0,
          group: group,
          pdf_file: r.pdf_file,
          pdf_page: r.pdf_page
        };
      };
      
      const mappedAttempt = {
        id: data.session_id,
        score: data.scoring.final_score,
        total: data.scoring.total,
        accuracy: data.scoring.accuracy,
        readiness: {
          correct: data.scoring.raw_score,
          total: data.scoring.total,
          avgTime: "12s" // Hardcoded for MVP display
        },
        items: data.classified_results.map(mapItem),
        groups: {
          master: (data.dna_groups.MASTERY || []).map(mapItem),
          danger: (data.dna_groups.PRIORITY_FOCUS || []).map(mapItem),
          slow: (data.dna_groups.TRUST_GAP || []).map(mapItem),
          confused: (data.dna_groups.GROWTH_AREA || []).map(mapItem)
        },
        results: data.classified_results
      };
      
      setAttempt(mappedAttempt);
      window.__medhaAttempt = mappedAttempt;
      setNotes(null);
      setNotesSource(null);
      
      if (data.wellbeing) {
        toast(data.wellbeing.message, { duration: 8000, icon: "💙" });
      }
      
      setView("result");
      refreshHistory();
    } catch (e) {
      toast.error("Failed to save results. Please try again.");
      throw e;
    }
  };

  const loadNotes = useCallback(async () => {
    setView("notes");
    if (notes || !attempt) return;
    setNotesLoading(true);

    try {
      const { data } = await axios.post(`${API}/notes/generate`, { session_id: attempt.id });
      setNotes(parseNotes(data.sections));
      setNotesSource(data.source);
      toast.success("✨ Study notes assembled from verified data!");
    } catch (e) {
      toast.error("Failed to generate notes.");
    } finally {
      setNotesLoading(false);
    }
  }, [notes, attempt]);

  // Load a past attempt from history  
  const handleViewAttempt = async (attemptId) => {
    try {
      const { data } = await axios.get(`${API}/attempts/${attemptId}`);
      setAttempt(data);
      if (data.notes) {
        setNotes(data.notes);
        setNotesSource(data.notesSource || null);
      } else {
        setNotes(null);
        setNotesSource(null);
      }
      setView("result");
    } catch (e) {
      toast.error("Failed to load attempt.");
    }
  };

  const handleNav = (key) => {
    setActivePdf(null);
    if (key === "landing") { setView("landing"); return; }
    if (key === "mood") { setView("mood"); return; }
    if (key === "notes") { loadNotes(); return; }
    setView(key);
  };

  const handleRetake = () => {
    setActivePdf(null);
    setAttempt(null);
    setNotes(null);
    setNotesSource(null);
    setSessionQuestions([]);
    setQuestions([]);
    setView("landing");
  };

  const downloadNotes = () => {
    const blob = new Blob([notesToMarkdown(notes)], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "medha-study-notes.md"; a.click();
    URL.revokeObjectURL(url);
    toast.success("Notes downloaded.");
  };

  const toggleLang = () => setLang((l) => l === "en" ? "bn" : "en");

  useEffect(() => {
    if (sessionQuestions.length) {
      setQuestions(sessionQuestions.map((q) => localizeQuestion(q, lang)));
    }
  }, [lang, sessionQuestions]);

  const localizeAttempt = useCallback((attemptData) => {
    if (!attemptData?.items) return attemptData;
    const mapGroup = (items) => (items || []).map((item) => localizeResultItem(item, lang));
    return {
      ...attemptData,
      items: mapGroup(attemptData.items),
      groups: attemptData.groups
        ? {
            master: mapGroup(attemptData.groups.master),
            danger: mapGroup(attemptData.groups.danger),
            slow: mapGroup(attemptData.groups.slow),
            confused: mapGroup(attemptData.groups.confused),
          }
        : attemptData.groups,
    };
  }, [lang]);

  const displayAttempt = useMemo(
    () => localizeAttempt(attempt || MOCK_ATTEMPT),
    [attempt, localizeAttempt]
  );
  const displayNotes = notes || MOCK_NOTES;

  return (
    <div className="App">
      <div className="app-bg" />
      <Toaster theme="dark" position="top-right" />
      {!introDone && <IntroAnimation onComplete={() => setIntroDone(true)} />}

      {introDone && (
        <>
          <NavBar 
            view={view} 
            examDone={!!attempt} 
            onNav={handleNav} 
            onRetake={handleRetake} 
            lang={lang} 
            onToggleLang={toggleLang} 
            historyCount={history.length} 
          />
          
          <main style={{ minHeight: "100vh", paddingTop: "68px" }}>
            {view === "landing" && (
              <Landing 
                onStart={handleStart} 
                onDemo={() => handleNav("dna")} 
                lang={lang} 
              />
            )}
            {view === "mood" && (
              <MoodCheck 
                onContinue={handleMoodContinue} 
                lang={lang} 
              />
            )}
            {view === "exam" && (
              <Exam 
                questions={questions} 
                onFinish={handleFinish} 
                showConfidence={showConfidence} 
                lang={lang} 
              />
            )}
            {view === "result" && (
              <Result 
                attempt={displayAttempt} 
                onViewNotes={() => handleNav("notes")} 
                onViewDNA={() => handleNav("dna")} 
                lang={lang} 
              />
            )}
            {view === "dna" && (
              <DnaReport 
                attempt={displayAttempt} 
                onViewNotes={() => handleNav("notes")} 
                lang={lang} 
              />
            )}
            {view === "dna-detail" && (
              <DnaReport 
                attempt={displayAttempt} 
                onViewNotes={() => handleNav("notes")} 
                lang={lang} 
              />
            )}
            {view === "notes" && (
              <StudyNotes 
                notes={displayNotes} 
                loading={notesLoading} 
                source={notesSource || "fallback"}
                onDownload={downloadNotes}
                onOpenPdf={handleOpenPdf}
                onViewReadiness={() => handleNav("readiness")}
                lang={lang} 
              />
            )}
            {view === "readiness" && (
              <Readiness 
                attempt={displayAttempt} 
                chapters={chapters}
                history={history}
                onRetake={handleRetake}
                lang={lang} 
              />
            )}
            {view === "anxiety" && (
              <AnxietyScore 
                attempt={displayAttempt} 
                lang={lang} 
              />
            )}
            {view === "classifier" && (
              <ClassifierPanel 
                attempt={displayAttempt} 
                lang={lang} 
              />
            )}
            {view === "history" && (
              <History 
                history={history} 
                onViewAttempt={handleViewAttempt} 
                lang={lang} 
              />
            )}
            {view === "share" && (
              <ShareCard 
                attempt={displayAttempt} 
                lang={lang} 
              />
            )}
          {activePdf && (
            <div className="pdf-modal-overlay" onClick={() => setActivePdf(null)} style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0,0,0,0.5)", zIndex: 9999, display: "flex", alignItems: "center", justifyContent: "center", animation: "fadeIn .2s" }}>
              <div className="pdf-modal-content" onClick={e => e.stopPropagation()} style={{ background: "white", width: "95%", maxWidth: 1000, height: "90%", borderRadius: 12, overflow: "hidden", display: "flex", flexDirection: "column", boxShadow: "0 20px 40px rgba(0,0,0,0.2)", animation: "fadeUp .3s ease" }}>
                <div className="pdf-modal-header" style={{ padding: "16px 24px", display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--line)", background: "var(--paper)" }}>
                  <div>
                    <h3 style={{ margin: 0, fontFamily: "var(--display)", fontSize: 20 }}>{lang === "bn" ? "পাঠ্যবই রেফারেন্স" : "Reference Textbook"}</h3>
                    <p style={{ margin: "4px 0 0", fontSize: 13, color: "var(--muted)" }}>{lang === "bn" ? `পৃষ্ঠা ${activePdf.page}` : `Page ${activePdf.page}`}</p>
                  </div>
                  <button onClick={() => setActivePdf(null)} className="btn btn-ghost" style={{ padding: "8px 16px", borderRadius: 8 }}>{lang === "bn" ? "বন্ধ করুন" : "Close"}</button>
                </div>
                <iframe src={`${BACKEND}/static/pdfs/${activePdf.file}#page=${activePdf.page}`} style={{ flex: 1, width: "100%", border: "none", background: "#f5f5f5" }} />
              </div>
            </div>
          )}
          </main>
        </>
      )}
      {/* Toast notification div — used by useToast() hook */}
      <div id="toast" />
    </div>
  );
}
