import { Activity, BarChart3, Sparkles } from "lucide-react";
import { t } from "../utils/lang";

export default function Landing({ onStart, onDemo, lang }) {
  return (
    <div className="view" data-testid="landing-view">
      <div className="wrap">
        {/* Hero */}
        <div className="hero">
          <div>
            <span className="pill"><span className="dot" />{t("heroEyebrow", lang)}</span>
            <h1>
              {t("heroTitle1", lang)}<span className="accent">{t("heroTitleAccent", lang)}</span>{t("heroTitle2", lang)}<br />
              {t("heroTitle3", lang)}
            </h1>
            <p>{t("heroSub", lang)}</p>
            <div className="hero-btns">
              <button className="btn btn-primary" data-testid="start-exam-button" onClick={onStart}>{t("startExam", lang)}</button>
              <button className="btn btn-ghost" onClick={onDemo}>{t("seeHow", lang)}</button>
            </div>
          </div>
          <div className="hero-visual">
            <img src="https://static.prod-images.emergentagent.com/jobs/60022136-80a9-4a74-b8e8-b42dc49e9be7/images/018a280c091d4daf0516f9d7580cf662b6020925e99a798ecd17efe9f32bbaa0.png" alt="DNA visualization" />
            <div className="glass-tag gt-1"><div><span className="gt-val" style={{ color: "var(--green)" }}>92%</span><div className="gt-lbl">Accuracy</div></div></div>
            <div className="glass-tag gt-2"><div><span className="gt-val" style={{ color: "var(--amber)" }}>4.2s</span><div className="gt-lbl">Avg Response</div></div></div>
            <div className="glass-tag gt-3"><div><span className="gt-val" style={{ color: "var(--red)" }}>2</span><div className="gt-lbl">Blind Spots</div></div></div>
          </div>
        </div>

        {/* Stats */}
        <div className="stats-row">
          <div className="stat"><div className="num">{t("stat1", lang)}</div><div className="lbl">{t("stat1l", lang)}</div></div>
          <div className="stat"><div className="num">{t("stat2", lang)}</div><div className="lbl">{t("stat2l", lang)}</div></div>
          <div className="stat"><div className="num">{t("stat3", lang)}</div><div className="lbl">{t("stat3l", lang)}</div></div>
        </div>

        {/* Features */}
        <div className="section-gap">
          <div className="section-head"><h2>{t("featTitle", lang)}</h2></div>
          <div className="feature-grid">
            {[[Activity, "feat1h", "feat1p"], [BarChart3, "feat2h", "feat2p"], [Sparkles, "feat3h", "feat3p"]].map(([Ic, hk, pk]) => (
              <div className="card feature-card" key={hk}>
                <div className="feature-ic"><Ic size={20} /></div>
                <h3>{t(hk, lang)}</h3><p>{t(pk, lang)}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Classifier */}
        <div className="section-gap">
          <div className="section-head"><h2>{t("classTitle", lang)}</h2></div>
          <div className="classifier-grid">
            {[
              ["cls-master", "clsMasterTag", "clsMasterH", "clsMasterP"],
              ["cls-slow", "clsSlowTag", "clsSlowH", "clsSlowP"],
              ["cls-confused", "clsConfusedTag", "clsConfusedH", "clsConfusedP"],
              ["cls-danger", "clsDangerTag", "clsDangerH", "clsDangerP"],
            ].map(([cls, tag, h, p]) => (
              <div className={`cls-card ${cls}`} key={cls}>
                <span className="cls-tag">{t(tag, lang)}</span>
                <h4>{t(h, lang)}</h4><p>{t(p, lang)}</p>
              </div>
            ))}
          </div>
        </div>

        {/* How it works */}
        <div className="section-gap">
          <div className="section-head"><h2>{t("howTitle", lang)}</h2></div>
          <div className="how-grid">
            {["how1", "how2", "how3", "how4", "how5"].map((k, i) => (
              <div className="how-step" key={k}>
                <span className="how-n">0{i + 1}</span>
                <h4>{t(k, lang)}</h4><p>{t(k + "p", lang)}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="footer">{t("footer", lang)}</div>
      </div>
    </div>
  );
}
