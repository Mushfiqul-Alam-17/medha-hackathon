import { useState } from "react";
import { t } from "../utils/lang";
import { Check } from "lucide-react";

const MOODS = [
  { key: "great", emoji: "😄", labelEn: "Great", labelBn: "দারুণ", subEn: "Locked in", subBn: "পুরো ফোকাস" },
  { key: "good", emoji: "🙂", labelEn: "Good", labelBn: "ভালো", subEn: "Ready to go", subBn: "প্রস্তুত" },
  { key: "okay", emoji: "😐", labelEn: "Okay", labelBn: "চলবে", subEn: "Getting there", subBn: "মোটামুটি" },
  { key: "tired", emoji: "😴", labelEn: "Tired", labelBn: "ক্লান্ত", subEn: "A bit slow", subBn: "একটু ক্লান্ত" },
  { key: "stressed", emoji: "😰", labelEn: "Stressed", labelBn: "চাপে আছি", subEn: "Feeling pressure", subBn: "মানসিক চাপে" },
];

export default function MoodCheck({ onContinue, lang }) {
  const [mood, setMood] = useState("okay");
  const [confidence, setConfidence] = useState(true);

  return (
    <div className="min-h-screen bg-[#FCF7F0] flex flex-col items-center justify-center py-10 px-4" data-testid="mood-view">
      
      {/* Stepper */}
      <div className="flex items-center justify-center gap-3 mb-10 text-xs font-semibold animate-in fade-in slide-in-from-top-4">
        <div className="w-6 h-6 rounded-full flex items-center justify-center bg-[#395F54] text-white">
          <Check size={12} strokeWidth={3} />
        </div>
        <span className="text-[#395F54]">{lang === "bn" ? "কনফিগার" : "Configure"}</span>
        <div className="w-8 h-px bg-[#E4D8CA]"></div>
        <div className="w-6 h-6 rounded-full flex items-center justify-center bg-[#D34A20] text-white shadow-md">2</div>
        <span className="text-slate-800 font-bold">{lang === "bn" ? "মুড চেক" : "Mood Check"}</span>
        <div className="w-8 h-px bg-[#E4D8CA]"></div>
        <div className="w-6 h-6 rounded-full flex items-center justify-center bg-white border border-[#E4D8CA] text-slate-400">3</div>
        <span className="text-slate-400">{lang === "bn" ? "শুরু করুন" : "Begin"}</span>
      </div>

      {/* Main Card */}
      <div className="bg-white rounded-3xl p-8 md:p-10 w-full max-w-[580px] shadow-[0_8px_32px_rgba(44,28,17,0.06)] border border-[#E4D8CA] animate-in zoom-in-95 duration-500">
        <p className="text-[11px] font-bold text-[#D34A20] tracking-[0.18em] uppercase text-center mb-3">
          {lang === "bn" ? "চেক-ইন · ১৫ সেকেন্ড" : "Check-In · 15 seconds"}
        </p>
        
        <h1 className="text-3xl md:text-[40px] font-bold font-['Hind Siliguri'] text-center text-slate-800 mb-3">
          {t("moodTitle", lang)}
        </h1>
        <p className="text-center text-slate-500 text-[15px] mb-8">
          {t("moodSub", lang)}
        </p>

        {/* Mood Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-8">
          {MOODS.map((m) => {
            const isSelected = mood === m.key;
            return (
              <button 
                key={m.key} 
                className={`flex flex-col items-center p-4 rounded-2xl border-2 transition-all duration-200 
                  ${isSelected 
                    ? "border-[#D34A20] bg-[#F9E5DA] shadow-md scale-105" 
                    : "border-[#E4D8CA] bg-white hover:border-[#D34A20]/40 hover:bg-slate-50"
                  }`}
                data-testid={`mood-${m.key}`} 
                onClick={() => setMood(m.key)}
              >
                <div className="text-3xl mb-2">{m.emoji}</div>
                <div className="text-[14px] font-bold text-slate-800">
                  {lang === "bn" ? m.labelBn : m.labelEn}
                </div>
                <div className="text-[11px] text-slate-500 mt-1">
                  {lang === "bn" ? m.subBn : m.subEn}
                </div>
              </button>
            );
          })}
        </div>

        <hr className="border-t border-[#E4D8CA] mb-6" />

        {/* Confidence Toggle */}
        <div className="flex items-center gap-4 mb-8">
          <div className="flex-1">
            <div className="text-[15px] font-semibold text-slate-800">
              {lang === "bn" ? "আত্মবিশ্বাস ট্র্যাকিং" : "Confidence Tracking"}
            </div>
            <div className="text-[13px] text-slate-500 mt-1 leading-relaxed">
              {confidence
                ? (lang === "bn"
                  ? "প্রতিটি প্রশ্নে Sure / Unsure বেছে নিতে হবে।"
                  : "Track how confident you feel before selecting each answer.")
                : (lang === "bn"
                  ? "বন্ধ — দ্রুত পরীক্ষা মোড।"
                  : "Off — just pick an answer, faster exam mode.")}
            </div>
          </div>
          
          <button 
            className={`relative w-12 h-6 rounded-full transition-colors duration-300 ease-in-out shrink-0 focus:outline-none focus:ring-2 focus:ring-[#D34A20] focus:ring-offset-2
              ${confidence ? "bg-[#D34A20]" : "bg-slate-300"}`}
            onClick={() => setConfidence((v) => !v)}
            role="switch"
            aria-checked={confidence}
          >
            <span 
              className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-sm transition-transform duration-300 ease-in-out
                ${confidence ? "translate-x-6" : "translate-x-0"}`}
            />
          </button>
        </div>

        <button 
          className={`w-full py-4 rounded-xl text-[16px] font-semibold text-white transition-all duration-300
            ${mood 
              ? "bg-[#D34A20] hover:bg-[#B93D18] hover:shadow-lg hover:-translate-y-0.5" 
              : "bg-slate-300 cursor-not-allowed"}`}
          data-testid="mood-continue"
          disabled={!mood}
          onClick={() => onContinue(mood, confidence)}
        >
          {lang === "bn" ? "পরীক্ষা শুরু করুন →" : "Begin Exam →"}
        </button>
        
        <p className="text-center text-[12px] text-slate-400 mt-4 font-medium">
          {lang === "bn" ? "১৫টি প্রশ্ন · জীববিজ্ঞান · মেডিকেল ভর্তি প্রস্তুতি" : "15 questions · Biology · MBBS Admission"}
        </p>
      </div>
    </div>
  );
}
