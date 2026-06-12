import { Languages, Clock, Menu } from "lucide-react";
import { t } from "../utils/lang";
import { useState } from "react";

export default function NavBar({ view, examDone, onNav, onRetake, lang, onToggleLang, historyCount }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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
    <nav className="fixed top-0 left-0 right-0 z-[100] bg-[#FCF7F0]/90 backdrop-blur-md border-b border-[#E4D8CA] h-[68px]" data-testid="navbar">
      <div className="max-w-[1100px] mx-auto px-4 md:px-6 h-full flex items-center justify-between gap-4">
        
        {/* Logo */}
        <button 
          className="flex items-center gap-2.5 shrink-0 hover:opacity-80 transition-opacity" 
          onClick={() => onNav("landing")}
        >
          <div className="w-9 h-9 flex items-center justify-center shrink-0">
            <svg width="38" height="38" viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="38" height="38" rx="10" fill="#1C1815"/>
              <line x1="8.5" y1="29.5" x2="19" y2="19" stroke="#D34A20" strokeWidth="1.6" strokeLinecap="round"/>
              <line x1="19" y1="19" x2="29.5" y2="9.5" stroke="#D34A20" strokeWidth="1.6" strokeLinecap="round" opacity="0.65"/>
              <line x1="19" y1="19" x2="29" y2="23.5" stroke="#D34A20" strokeWidth="1.1" strokeLinecap="round" opacity="0.38"/>
              <line x1="19" y1="19" x2="9" y2="14.5" stroke="#D34A20" strokeWidth="1.1" strokeLinecap="round" opacity="0.38"/>
              <circle cx="8.5" cy="29.5" r="2.8" fill="#D34A20"/>
              <circle cx="19" cy="19" r="2.4" fill="#D34A20" opacity="0.9"/>
              <circle cx="29.5" cy="9.5" r="2" fill="#D34A20" opacity="0.6"/>
              <circle cx="29" cy="23.5" r="1.6" fill="#D34A20" opacity="0.35"/>
              <circle cx="9" cy="14.5" r="1.6" fill="#D34A20" opacity="0.35"/>
            </svg>
          </div>
          <span className="text-[19px] font-extrabold tracking-[-0.03em] bg-gradient-to-br from-[#1C1815] to-[#3A2E28] bg-clip-text text-transparent hidden sm:block">
            MEDHA
          </span>
        </button>

        {/* Desktop Links */}
        <div className="hidden md:flex items-center gap-1 overflow-x-auto no-scrollbar mask-edges">
          {tabs.map((tb) => (
            <button
              key={tb.key}
              className={`px-3 py-2 rounded-lg text-[13.5px] font-medium transition-colors whitespace-nowrap flex items-center gap-1.5
                ${view === tb.key ? "bg-white shadow-sm text-[#D34A20]" : "text-slate-600 hover:bg-white/50 hover:text-slate-900"}`}
              onClick={() => onNav(tb.key)}
            >
              {tb.key === "history" && <Clock size={13} />}
              {tb.label}
              {tb.badge > 0 && (
                <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-[#F9E5DA] text-[#D34A20] font-bold">
                  {tb.badge}
                </span>
              )}
            </button>
          ))}
          
          <button
            className="px-3 py-2 rounded-lg text-[13.5px] font-medium text-slate-600 hover:bg-white/50 hover:text-slate-900 flex items-center gap-1.5"
            onClick={onToggleLang}
            title={lang === "en" ? "বাংলায় দেখুন" : "Switch to English"}
          >
            <Languages size={14} />
            {lang === "en" ? "বাংলা" : "EN"}
          </button>
        </div>

        {/* Actions & Mobile Menu */}
        <div className="flex items-center gap-2 shrink-0">
          {examDone ? (
            <button className="hidden sm:block px-4 py-2 rounded-full text-[13px] font-medium border border-[#E4D8CA] text-slate-700 hover:bg-white transition-colors" onClick={onRetake}>
              {lang === "bn" ? "আবার পরীক্ষা দিন" : "Retake Exam"}
            </button>
          ) : (
            <button className="px-5 py-2.5 rounded-xl text-[14px] font-medium bg-[#D34A20] text-white hover:bg-[#B93D18] shadow-sm transition-colors" onClick={() => onNav("mood")}>
              {lang === "bn" ? "পরীক্ষা শুরু করুন" : "Start Exam"}
            </button>
          )}

          {/* Mobile Menu Toggle */}
          <button 
            className="md:hidden p-2 rounded-lg text-slate-600 hover:bg-white/50"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <Menu size={20} />
          </button>
        </div>
      </div>

      {/* Mobile Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden absolute top-[68px] left-0 right-0 bg-[#FCF7F0] border-b border-[#E4D8CA] shadow-xl flex flex-col p-4 gap-2 animate-in slide-in-from-top-2">
          {tabs.map((tb) => (
            <button
              key={tb.key}
              className={`p-3 text-left rounded-xl text-[15px] font-medium flex items-center justify-between
                ${view === tb.key ? "bg-white text-[#D34A20]" : "text-slate-600 hover:bg-white/50"}`}
              onClick={() => { onNav(tb.key); setMobileMenuOpen(false); }}
            >
              <div className="flex items-center gap-2">
                {tb.key === "history" && <Clock size={16} />}
                {tb.label}
              </div>
              {tb.badge > 0 && (
                <span className="px-2 py-1 rounded-full text-[11px] bg-[#F9E5DA] text-[#D34A20] font-bold">
                  {tb.badge}
                </span>
              )}
            </button>
          ))}
          <div className="h-px bg-[#E4D8CA] my-2" />
          <button
            className="p-3 text-left rounded-xl text-[15px] font-medium text-slate-600 hover:bg-white/50 flex items-center gap-2"
            onClick={() => { onToggleLang(); setMobileMenuOpen(false); }}
          >
            <Languages size={16} />
            {lang === "en" ? "Switch to বাংলা" : "Switch to English"}
          </button>
        </div>
      )}
    </nav>
  );
}
