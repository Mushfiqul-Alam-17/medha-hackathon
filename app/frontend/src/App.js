import { useEffect, useState, useCallback } from "react";
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

const BACKEND = process.env.REACT_APP_BACKEND_URL || "https://medha-api.onrender.com";
const API = `${BACKEND}/api`;

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
  const [introDone, setIntroDone] = useState(false);
  const [view, setView] = useState("landing");
  const [questions, setQuestions] = useState([]);
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
        question_count: 15
      });
      setSessionId(data.session_id);
      
      // Map new backend schema to old Exam.jsx expected format
      const mappedQuestions = data.questions.map(q => ({
        id: q.id,
        chapter: q.chapter_name,
        text: q.question_bn,
        options: [q.option_a_bn, q.option_b_bn, q.option_c_bn, q.option_d_bn]
      }));
      
      setQuestions(mappedQuestions);
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
      
      // Map new backend payload to legacy frontend format
      const mapItem = (r) => ({
        questionId: r.question_id,
        finalAnswerIndex: r.final_answer ? LETTERS.indexOf(r.final_answer) : null,
        isCorrect: r.is_correct,
        confidence: r.confidence_tap,
        questionText: r.question_bn,
        options: r.options_bn,
        correctAnswerIndex: r.correct_answer ? LETTERS.indexOf(r.correct_answer) : 0,
        chapter: r.chapter_name,
        timeTaken: r.time_taken,
        clickSequence: r.click_path,
        pdf_file: r.pdf_file,
        pdf_page: r.pdf_page
      });
      
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

  return (
    <div className="App">
      <div className="app-bg" />
      <Toaster theme="dark" position="top-right" />
      {!introDone && <IntroAnimation onComplete={() => setIntroDone(true)} />}

      {introDone && (
        <>
          <NavBar view={view} examDone={examDone} onNav={handleNav} onRetake={handleRetake}
            lang={lang} onToggleLang={toggleLang} historyCount={history.length} />

          <div className="main-layout-container" style={{ display: "flex", width: "100%", minHeight: "calc(100vh - 70px)", position: "relative" }}>
            <div className="left-panel-content" style={{ flex: 1, width: activePdf ? "55%" : "100%", transition: "width 0.3s ease" }}>
              {view === "landing" && <Landing onStart={handleStart} lang={lang}
                onDemo={() => document.querySelector(".classifier-grid")?.scrollIntoView({ behavior: "smooth" })} />}
              {view === "mood" && <MoodCheck onContinue={handleMoodContinue} lang={lang} />}
              {view === "exam" && questions.length > 0 && (
                <Exam questions={questions} mood={window.__medhaMood} onFinish={handleFinish} lang={lang} showConfidence={showConfidence} />
              )}
              {view === "result" && attempt && <Result attempt={attempt} onViewDNA={() => setView("dna")} lang={lang} onOpenPdf={handleOpenPdf} />}
              {view === "dna" && attempt && <DnaReport groups={attempt.groups} onViewNotes={loadNotes} lang={lang} />}
              {view === "classifier" && attempt && <ClassifierPanel attempt={attempt} lang={lang} />}
              {view === "notes" && attempt && (
                <StudyNotes loading={notesLoading} notes={notes} source={notesSource} onDownload={downloadNotes} lang={lang} onOpenPdf={handleOpenPdf} />
              )}
              {view === "readiness" && attempt && (
                <Readiness attempt={attempt} chapters={chapters} history={history} onRetake={handleRetake} lang={lang} />
              )}
              {view === "anxiety" && attempt && <AnxietyScore attempt={attempt} lang={lang} />}
              {view === "share" && attempt && <ShareCard attempt={attempt} lang={lang} />}
              {view === "history" && (
                <History history={history} onViewAttempt={handleViewAttempt} onRetake={handleRetake} lang={lang} />
              )}
            </div>
            
            {activePdf && (
              <div className="right-panel-pdf" style={{ width: "45%", borderLeft: "2px solid var(--border)", background: "var(--bg)", display: "flex", flexDirection: "column", position: "sticky", top: 70, height: "calc(100vh - 70px)", zIndex: 100 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 16px", borderBottom: "1px solid var(--border)", background: "var(--bg-card)" }}>
                  <span style={{ fontSize: 14, fontWeight: "600", color: "var(--text)" }}>
                    📖 {activePdf.file.replace(/_/g, " ").replace(".pdf", "")} (Page {activePdf.page})
                  </span>
                  <button 
                    className="btn btn-ghost" 
                    style={{ padding: "4px 10px", fontSize: 13, minWidth: "auto" }}
                    onClick={() => setActivePdf(null)}
                  >
                    ✕ Close
                  </button>
                </div>
                <iframe 
                  src={`${BACKEND}/static/pdfs/${activePdf.file}#page=${activePdf.page}${activePdf.searchKeyword ? `&search=${encodeURIComponent(activePdf.searchKeyword)}` : ""}`}
                  title="Textbook Scroller"
                  style={{ width: "100%", height: "100%", border: "none" }}
                />
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
