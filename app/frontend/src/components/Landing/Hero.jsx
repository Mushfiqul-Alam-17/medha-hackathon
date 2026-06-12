import { AlertCircle } from "lucide-react";
import { t } from "../../utils/lang";

export default function Hero({ onStart, onDemo, lang }) {
  return (
    <div className="hero grid grid-cols-1 md:grid-cols-[1.1fr_0.9fr] gap-12 items-center pt-10 relative z-10">
      <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 ease-out">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-[#E4D8CA] shadow-sm text-xs font-semibold mb-6">
          <span className="w-2 h-2 rounded-full bg-[#D34A20] animate-pulse"></span>
          {t("heroEyebrow", lang)}
        </div>
        
        <h1 className="text-[clamp(42px,5.5vw,68px)] leading-[0.95] font-bold my-6 font-['Hind Siliguri']">
          {lang === "bn" ? (
            <>
              বুঝো <em className="text-[#D34A20] not-italic relative inline-block">কেন<svg className="absolute w-full h-2 bottom-0 left-0 text-[#D34A20]/30" viewBox="0 0 100 10" preserveAspectRatio="none"><path d="M0,5 Q50,10 100,5" stroke="currentColor" strokeWidth="4" fill="none"/></svg></em><br />
              ভুল হচ্ছে,<br />
              শুধু পড়লেই হবে না।
            </>
          ) : (
            <>
              Know <em className="text-[#D34A20] not-italic relative inline-block">how<svg className="absolute w-full h-2 bottom-0 left-0 text-[#D34A20]/30" viewBox="0 0 100 10" preserveAspectRatio="none"><path d="M0,5 Q50,10 100,5" stroke="currentColor" strokeWidth="4" fill="none"/></svg></em><br />
              you think,<br />
              not just what<br />
              you know.
            </>
          )}
        </h1>
        
        <p className="text-base leading-relaxed text-slate-500 max-w-[460px] mb-8">
          {t("heroSub", lang)}
        </p>
        
        <div className="flex flex-wrap gap-3">
          <button 
            className="px-7 py-3 text-[15px] font-medium rounded-xl bg-[#D34A20] text-white hover:bg-[#B93D18] hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300" 
            data-testid="start-exam-button" 
            onClick={onStart}
          >
            {t("startExam", lang)}
          </button>
          <button 
            className="px-6 py-3 text-[15px] font-medium rounded-xl bg-white border border-[#E4D8CA] text-slate-700 hover:bg-slate-50 hover:shadow-md transition-all duration-300" 
            onClick={onDemo}
          >
            {t("seeHow", lang)}
          </button>
        </div>
        
        <div className="flex gap-7 mt-10 pt-8 border-t border-[#E4D8CA]">
          {[
            { val: "12K+", lbl: lang === "bn" ? "বিশ্লেষিত শিক্ষার্থী" : "Students analyzed" },
            { val: "94.7%", lbl: lang === "bn" ? "সঠিকতা হার" : "Classifier accuracy" },
            { val: "4", lbl: lang === "bn" ? "আচরণ গ্রুপ" : "Behavioral phenotypes" }
          ].map((stat, i) => (
            <div key={i} className="hover:scale-105 transition-transform">
              <div className="font-['Hind Siliguri'] text-3xl font-semibold text-slate-800">{stat.val}</div>
              <div className="text-xs text-slate-500 mt-1">{stat.lbl}</div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="relative flex justify-center animate-in fade-in zoom-in-95 duration-1000 delay-200">
        {/* Floating elements styling */}
        <div className="bg-white border border-[#E4D8CA] rounded-2xl p-6 w-[340px] rotate-2 shadow-[0_18px_60px_rgba(56,32,16,0.11)] hover:rotate-0 transition-all duration-500 relative group cursor-default">
          <div className="text-[11px] font-bold tracking-[0.15em] uppercase text-slate-400 mb-3">
            {lang === "bn" ? "ডিএনএ রিপোর্ট — রিয়া এস." : "ExamDNA Report — Riya S."}
          </div>
          
          <div className="flex items-center justify-between mb-1 w-full">
            <span className="text-[13px] font-semibold flex-1 text-slate-800">{lang === "bn" ? "আচরণগত প্যাটার্ন" : "Response Patterns"}</span>
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-[#EBF5EF] text-[#2D7A4F] font-medium border border-[#2D7A4F]/20">{lang === "bn" ? "৭৪% স্কোর" : "74% Score"}</span>
          </div>
          
          <div className="h-20 relative my-3 group-hover:scale-[1.02] transition-transform">
            <svg viewBox="0 0 300 80" preserveAspectRatio="none" fill="none" className="w-full h-full">
              <defs>
                <linearGradient id="cg" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#D34A20" stopOpacity=".22" />
                  <stop offset="100%" stopColor="#D34A20" stopOpacity="0" />
                </linearGradient>
              </defs>
              <path d="M0,60 L30,45 L60,50 L90,28 L120,35 L150,20 L180,30 L210,18 L240,25 L270,12 L300,20 L300,80 L0,80Z" fill="url(#cg)" className="transition-all duration-700" />
              <path d="M0,60 L30,45 L60,50 L90,28 L120,35 L150,20 L180,30 L210,18 L240,25 L270,12 L300,20" stroke="#D34A20" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="drop-shadow-sm" />
              <circle cx="150" cy="20" r="4" fill="#D34A20" className="animate-pulse" />
              <circle cx="270" cy="12" r="4" fill="#D34A20" className="animate-pulse delay-300" />
            </svg>
          </div>
          
          <div className="flex flex-wrap gap-1.5 mt-2">
            <span className="text-[10px] px-2 py-1 rounded bg-[#EBF5EF] text-[#2D7A4F]">Master 52%</span>
            <span className="text-[10px] px-2 py-1 rounded bg-[#FDF3E3] text-[#C07A10]">Slow 24%</span>
            <span className="text-[10px] px-2 py-1 rounded bg-[#EEEFFE] text-[#5057A6]">Confused 16%</span>
            <span className="text-[10px] px-2 py-1 rounded bg-[#F7E0DC] text-[#C03A2A]">Danger 8%</span>
          </div>
        </div>
        
        {/* Floating note card */}
        <div className="absolute -bottom-5 -left-5 bg-white border border-[#E4D8CA] rounded-xl px-4 py-3 shadow-[0_8px_32px_rgba(44,28,17,0.08)] w-[200px] -rotate-3 animate-[float_4s_ease-in-out_infinite] hover:-rotate-1 hover:scale-105 transition-all">
          <div className="font-mono text-[10px] font-bold text-[#D34A20] mb-1.5 flex items-center gap-1">
            <AlertCircle size={12} /> {lang === "bn" ? "দুর্বলতা সনাক্ত" : "Weakness Detected"}
          </div>
          <div className="text-[13px] font-semibold text-slate-800">{lang === "bn" ? "উদ্ভিদ শারীরস্থান" : "Plant Anatomy"}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">{lang === "bn" ? "২৯% আয়ত্ত — গুরুত্ব দিন" : "29% mastery — needs focus"}</div>
        </div>
      </div>
    </div>
  );
}
