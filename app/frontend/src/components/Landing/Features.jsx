import { Activity, BarChart3, Sparkles } from "lucide-react";
import { t } from "../../utils/lang";

export default function Features({ lang }) {
  const features = [
    { icon: Activity, hk: "feat1h", pk: "feat1p" },
    { icon: BarChart3, hk: "feat2h", pk: "feat2p" },
    { icon: Sparkles, hk: "feat3h", pk: "feat3p" }
  ];

  return (
    <div className="py-24">
      <div className="mb-12">
        <span className="text-[13px] font-bold tracking-wider uppercase text-[#D34A20] block mb-3">
          {lang === "bn" ? "ফিচার সমূহ" : "Everything you need"}
        </span>
        <h2 className="text-[clamp(28px,4vw,42px)] font-semibold font-['Hind Siliguri'] leading-tight text-slate-800">
          {lang === "bn" ? (
            <>মেডিকেল ভর্তি প্রস্তুতিকে<br />সহজ করার জন্য ডিজাইনকৃত</>
          ) : (
            <>Designed around how<br />doctors-in-training think.</>
          )}
        </h2>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {features.map(({ icon: Ic, hk, pk }) => (
          <div key={hk} className="bg-white rounded-2xl p-7 border border-[#E4D8CA] hover:shadow-[0_8px_32px_rgba(44,28,17,0.06)] hover:-translate-y-1 transition-all duration-300 group">
            <div className="w-11 h-11 rounded-xl bg-[#F9E5DA] text-[#D34A20] flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <Ic size={20} />
            </div>
            <h3 className="text-[17px] font-semibold text-slate-800 mb-2">{t(hk, lang)}</h3>
            <p className="text-[14px] text-slate-500 leading-relaxed">{t(pk, lang)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
