import { Dna, Languages, Clock } from "lucide-react";
import { t } from "../utils/lang";

export default function NavBar({ view, examDone, onNav, onRetake, lang, onToggleLang, historyCount }) {
  const tabs = [
    { key: "landing", label: t("navHome", lang) },
    ...(examDone ? [
      { key: "result", label: t("navExam", lang) },
      { key: "dna", label: t("navDna", lang) },
      { key: "classifier", label: lang === "bn" ? "ক্লাসিফায়ার" : "Classifier" },
      { key: "notes", label: t("navNotes", lang) },
      { key: "readiness", label: t("navReadiness", lang) },
      { key: "anxiety", label: t("navAnxiety", lang) },
      { key: "share", label: t("share", lang) },
    ] : []),
    { key: "history", label: lang === "bn" ? "ইতিহাস" : "History", badge: historyCount || 0 },
  ];

  return (
    <nav className="nav" data-testid="navbar">
      <div className="nav-logo" onClick={() => onNav("landing")}>
        <Dna size={20} style={{ marginRight: 6, verticalAlign: "middle", color: "var(--accent)" }} />
        Medha<span>.</span>
      </div>
      <div className="nav-tabs">
        {tabs.map((tb) => (
          <button key={tb.key} className={`nav-tab ${view === tb.key ? "active" : ""}`}
            data-testid={`nav-${tb.key}`} onClick={() => onNav(tb.key)}>
            {tb.key === "history" && <Clock size={13} style={{ marginRight: 3, verticalAlign: "middle" }} />}
            {tb.label}
            {tb.badge > 0 && <span className="nav-badge">{tb.badge}</span>}
          </button>
        ))}
        {examDone && (
          <button className="nav-tab" data-testid="nav-retake" onClick={onRetake}
            style={{ color: "var(--accent)" }}>{t("navRetake", lang)}</button>
        )}
        <button className="nav-tab lang-toggle" data-testid="lang-toggle" onClick={onToggleLang}
          title={lang === "en" ? "বাংলায় দেখুন" : "Switch to English"}>
          <Languages size={15} style={{ marginRight: 4, verticalAlign: "middle" }} />
          {lang === "en" ? "বাং" : "EN"}
        </button>
      </div>
    </nav>
  );
}
