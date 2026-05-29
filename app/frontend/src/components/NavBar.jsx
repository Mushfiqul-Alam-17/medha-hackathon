import { Dna, Languages } from "lucide-react";
import { t } from "../utils/lang";

export default function NavBar({ view, examDone, onNav, onRetake, lang, onToggleLang }) {
  const tabs = [
    { key: "landing", label: t("navHome", lang) },
    ...(examDone ? [
      { key: "result", label: t("navExam", lang) },
      { key: "dna", label: t("navDna", lang) },
      { key: "notes", label: t("navNotes", lang) },
      { key: "readiness", label: t("navReadiness", lang) },
      { key: "anxiety", label: t("navAnxiety", lang) },
      { key: "share", label: "Share" },
    ] : []),
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
            data-testid={`nav-${tb.key}`} onClick={() => onNav(tb.key)}>{tb.label}</button>
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
