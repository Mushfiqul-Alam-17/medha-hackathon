import { t } from "../../utils/lang";

export default function HowItWorks({ lang }) {
  const steps = ["how1", "how2", "how3", "how4", "how5"];

  return (
    <div className="py-24 border-t border-[#E4D8CA] scroll-mt-24">
      <div className="mb-12">
        <h2 className="text-[26px] font-semibold font-['Hind Siliguri'] text-slate-800">
          {t("howTitle", lang)}
        </h2>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
        {steps.map((k, i) => (
          <div key={k} className="relative group">
            <span className="font-mono text-[#D34A20] text-[13px] font-bold tracking-wider">
              0{i + 1}
            </span>
            <h4 className="text-[15px] my-2 font-['Hind Siliguri'] font-semibold text-slate-800 group-hover:text-[#D34A20] transition-colors">
              {t(k, lang)}
            </h4>
            <p className="text-slate-500 text-[13px] leading-relaxed">
              {t(k + "p", lang)}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
