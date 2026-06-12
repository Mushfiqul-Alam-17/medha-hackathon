import { t } from "../../utils/lang";

export default function Footer({ lang }) {
  return (
    <div className="border-t border-[#E4D8CA] mt-24 py-10 text-center text-[13px] text-slate-500">
      {t("footer", lang)}
    </div>
  );
}
