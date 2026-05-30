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
  (notes.slow || []).forEach((n) => {
    md += `## [Slow] ${n.topic}\n- **Explanation:** ${n.explanation || ""}\n- **Memory Trick:** ${n.memoryTrick || ""}\n- **Trap:** ${n.trapQuestion || ""}\n\n`;
  });
  (notes.confused || []).forEach((n) => {
    md += `## [Confused] ${n.topic}\n\n| Concept | Description |\n| --- | --- |\n`;
    (n.comparisonTable || []).forEach((r) => { md += `| ${r.concept} | ${r.description} |\n`; });
    md += `\n- **Memory Trick:** ${n.memoryTrick || ""}\n- **Trap:** ${n.trapQuestion || ""}\n\n`;
  });
  (notes.danger || []).forEach((n) => {
    md += `## [Danger] ${n.topic}\n- **Explanation:** ${n.explanation || ""}\n- **Why Correct:** ${n.whyCorrect || ""}\n- **Why Tricked:** ${n.whyTricked || ""}\n- **Trap:** ${n.trapQuestion || ""}\n\n`;
  });
  return md;
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
  const [lang, setLang] = useState("en");
  const [showConfidence, setShowConfidence] = useState(true);

  useEffect(() => {
    axios.get(`${API}/questions`).then((r) => setQuestions(r.data.questions)).catch(() => {});
    axios.get(`${API}/chapters`).then((r) => setChapters(r.data.chapters)).catch(() => {});
  }, []);

  // Load history on mount and after each attempt
  const refreshHistory = useCallback(() => {
    axios.get(`${API}/attempts`).then((r) => setHistory(r.data.attempts)).catch(() => {});
  }, []);

  useEffect(() => { refreshHistory(); }, [refreshHistory]);

  const examDone = !!attempt;

  const handleStart = () => setView("mood");

  const handleMoodContinue = (mood, confidenceEnabled) => {
    setShowConfidence(confidenceEnabled);
    setView("exam");
    window.__medhaMood = mood;
  };

  const handleFinish = async (items, mood) => {
    try {
      const { data } = await axios.post(`${API}/attempts`, { mood, items });
      setAttempt(data);
      setNotes(null);
      setNotesSource(null);
      setView("result");
      refreshHistory();
    } catch (e) {
      toast.error("Failed to save results. Please try again.");
    }
  };

  const loadNotes = useCallback(async () => {
    setView("notes");
    if (notes || !attempt) return;
    setNotesLoading(true);
    const dnaReport = {
      slow: attempt.groups.slow,
      confused: attempt.groups.confused,
      danger: attempt.groups.danger,
    };
    try {
      const { data } = await axios.post(`${API}/notes`, { dnaReport, attemptId: attempt.id });
      setNotes(data.notes);
      setNotesSource(data.source);
      if (data.source === "ai") toast.success("✨ AI-powered study notes generated!");
      else toast("Notes generated (offline mode).");
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
    if (key === "landing") { setView("landing"); return; }
    if (key === "mood") { setView("mood"); return; }
    if (key === "notes") { loadNotes(); return; }
    setView(key);
  };

  const handleRetake = () => {
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

          {view === "landing" && <Landing onStart={handleStart} lang={lang}
            onDemo={() => document.querySelector(".classifier-grid")?.scrollIntoView({ behavior: "smooth" })} />}
          {view === "mood" && <MoodCheck onContinue={handleMoodContinue} lang={lang} />}
          {view === "exam" && questions.length > 0 && (
            <Exam questions={questions} mood={window.__medhaMood} onFinish={handleFinish} lang={lang} showConfidence={showConfidence} />
          )}
          {view === "result" && attempt && <Result attempt={attempt} onViewDNA={() => setView("dna")} lang={lang} />}
          {view === "dna" && attempt && <DnaReport groups={attempt.groups} onViewNotes={loadNotes} lang={lang} />}
          {view === "classifier" && attempt && <ClassifierPanel attempt={attempt} lang={lang} />}
          {view === "notes" && attempt && (
            <StudyNotes loading={notesLoading} notes={notes} source={notesSource} onDownload={downloadNotes} lang={lang} />
          )}
          {view === "readiness" && attempt && (
            <Readiness attempt={attempt} chapters={chapters} history={history} onRetake={handleRetake} lang={lang} />
          )}
          {view === "anxiety" && attempt && <AnxietyScore attempt={attempt} lang={lang} />}
          {view === "share" && attempt && <ShareCard attempt={attempt} lang={lang} />}
          {view === "history" && (
            <History history={history} onViewAttempt={handleViewAttempt} onRetake={handleRetake} lang={lang} />
          )}
        </>
      )}
    </div>
  );
}
