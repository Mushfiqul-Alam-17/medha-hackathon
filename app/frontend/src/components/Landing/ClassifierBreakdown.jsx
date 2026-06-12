import { t } from "../../utils/lang";

export default function ClassifierBreakdown({ lang }) {
  const categories = [
    { id: "cls-master", tag: "clsMasterTag", hk: "clsMasterH", pk: "clsMasterP", color: "#2D7A4F", softColor: "#EBF5EF" },
    { id: "cls-slow", tag: "clsSlowTag", hk: "clsSlowH", pk: "clsSlowP", color: "#C07A10", softColor: "#FDF3E3" },
    { id: "cls-confused", tag: "clsConfusedTag", hk: "clsConfusedH", pk: "clsConfusedP", color: "#5057A6", softColor: "#EEEFFE" },
    { id: "cls-danger", tag: "clsDangerTag", hk: "clsDangerH", pk: "clsDangerP", color: "#C03A2A", softColor: "#F7E0DC" },
  ];

  return (
    <div className="py-24 border-t border-[#E4D8CA]">
      <div className="mb-12">
        <span className="text-[13px] font-bold tracking-wider uppercase text-[#D34A20] block mb-3">
          {lang === "bn" ? "আচরণ বিশ্লেষণ" : "Phenotype Breakdown"}
        </span>
        <h2 className="text-[26px] font-semibold font-['Hind Siliguri'] text-slate-800">
          {t("classTitle", lang)}
        </h2>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {categories.map(({ id, tag, hk, pk, color, softColor }) => (
          <div 
            key={id} 
            className="rounded-2xl p-6 transition-all duration-300 hover:shadow-lg hover:-translate-y-1"
            style={{ 
              border: `1px solid ${color}33`, 
              background: `linear-gradient(180deg, ${softColor}88, transparent)` 
            }}
          >
            <span 
              className="font-mono text-[11px] font-bold tracking-[0.1em] uppercase"
              style={{ color }}
            >
              {t(tag, lang)}
            </span>
            <h4 className="font-['Hind Siliguri'] text-[17px] font-semibold mt-2 mb-1.5 text-slate-800">
              {t(hk, lang)}
            </h4>
            <p className="text-slate-500 text-[13px] leading-relaxed">
              {t(pk, lang)}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
