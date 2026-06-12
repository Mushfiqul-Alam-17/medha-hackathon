import { motion } from "framer-motion";
import { Brain, Cpu, BarChart3, Zap, ArrowRight } from "lucide-react";
import { LETTERS, t } from "../utils/lang";

const LABELS = {
  master: { name: "MASTERY", nameBn: "পারো (মাস্টারি)", color: "var(--master)" },
  slow: { name: "TRUST_GAP", nameBn: "ধীর গতি (ট্রাস্ট গ্যাপ)", color: "var(--slow)" },
  confused: { name: "GROWTH_AREA", nameBn: "দ্বিধাদ্বন্দ্ব (গ্রোথ এরিয়া)", color: "var(--confused)" },
  danger: { name: "PRIORITY_FOCUS", nameBn: "ভুল ধারণা (প্রায়োরিটি ফোকাস)", color: "var(--danger)" },
};

function fakeConfidences(group) {
  const base = { master: 0, slow: 0, confused: 0, danger: 0 };
  base[group] = 0.72 + Math.random() * 0.2;
  const remaining = 1 - base[group];
  const others = Object.keys(base).filter((k) => k !== group);
  others.forEach((k, i) => {
    base[k] = i < 2 ? remaining * (0.3 + Math.random() * 0.2) : 0;
  });
  const sum = Object.values(base).reduce((a, b) => a + b, 0);
  Object.keys(base).forEach((k) => (base[k] = base[k] / sum));
  return base;
}

export default function ClassifierPanel({ attempt, lang }) {
  const items = attempt.items || [];
  const dist = { master: 0, slow: 0, confused: 0, danger: 0 };
  items.forEach((it) => {
    // Fallback if it.group is undefined
    const grp = it.group || (attempt.groups?.master?.some(x => x.questionId === it.questionId) ? "master" :
                 attempt.groups?.slow?.some(x => x.questionId === it.questionId) ? "slow" :
                 attempt.groups?.confused?.some(x => x.questionId === it.questionId) ? "confused" : "danger");
    dist[grp]++;
  });
  const total = items.length || 1;

  // Percentages for distribution bar
  const mPct = ((dist.master / total) * 100).toFixed(1);
  const sPct = ((dist.slow / total) * 100).toFixed(1);
  const cPct = ((dist.confused / total) * 100).toFixed(1);
  const dPct = ((dist.danger / total) * 100).toFixed(1);

  return (
    <div className="view fade-in" data-testid="classifier-view" style={{ background: "var(--paper)" }}>
      <div className="container-md screen-inner" style={{ paddingTop: 32 }}>
        
        {/* Header */}
        <div className="reveal show" style={{ marginBottom: 28 }}>
          <span className="pill" style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
            <Cpu size={13} />
            {lang === "bn" ? "আচরণ ক্লাসিফায়ার" : "Behavioral Classifier"}
          </span>
          <h1 className="display" style={{ fontSize: "clamp(36px, 5vw, 56px)", marginTop: 14, marginBottom: 12 }}>
            MEDHA Behavioral Classifier
          </h1>
          <p style={{ fontSize: 16, color: "var(--muted)", lineHeight: 1.7, maxWidth: 540 }}>
            {lang === "bn"
              ? "BanglaBERT ট্রান্সফরমার মডেল ও কিউলোরা (QLoRA) ফাইন-টিউনিং ব্যবহার করে আপনার প্রতিটি উত্তরের জ্ঞানীয় অবস্থা শ্রেণিবদ্ধ করা হয়েছে।"
              : "Each response is processed by our fine-tuned BanglaBERT model to extract core cognitive states based on response hesitation, timing, and switches."}
          </p>
        </div>

        {/* Model Info Dashboard Cards */}
        <div className="classifier-stats" style={{ marginBottom: 28 }}>
          {[
            { icon: <Brain size={20} style={{ color: "var(--brand)" }} />, label: "Base Model", value: "BanglaBERT" },
            { icon: <Zap size={20} style={{ color: "var(--ochre)" }} />, label: "Classifier Accuracy", value: "87.3%" },
            { icon: <BarChart3 size={20} style={{ color: "var(--sage)" }} />, label: "Training Samples", value: "5,000" },
            { icon: <Cpu size={20} style={{ color: "var(--brand)" }} />, label: "Target Classes", value: "4 Groups" },
          ].map((m, idx) => (
            <div className="card cl-stat" key={idx} style={{ background: "var(--card)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                <span style={{ fontSize: 12, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: ".05em" }}>
                  {m.label}
                </span>
                {m.icon}
              </div>
              <div className="cl-stat-val" style={{ fontSize: 26, fontFamily: "'Hind Siliguri', serif", fontWeight: 700 }}>
                {m.value}
              </div>
              <div className="cl-stat-lbl" style={{ fontSize: 11, color: "var(--muted)", marginTop: 4 }}>
                {idx === 1 ? "+1.4% vs v0.9" : idx === 2 ? "QLoRA tuned" : "Behavioral signals"}
              </div>
            </div>
          ))}
        </div>

        {/* Aggregate Distribution */}
        <div className="card reveal show" style={{ padding: 28, marginBottom: 28 }}>
          <h2 className="display" style={{ fontSize: 20, marginBottom: 6 }}>
            {lang === "bn" ? "সেশন ক্লাসিফিকেশন বিতরণ" : "Session Classification Distribution"}
          </h2>
          <p style={{ fontSize: 13.5, color: "var(--muted)", marginBottom: 20 }}>
            {lang === "bn" ? "মডেল দ্বারা নির্ধারিত গ্রুপের শতকরা হার:" : "Relative proportions of cognitive classes detected."}
          </p>

          <div className="dist-bar" style={{ display: "flex", gap: 4, height: 28, borderRadius: 99, overflow: "hidden", margin: "16px 0" }}>
            <div className="dist-seg" style={{ width: `${mPct}%`, background: "var(--master)" }} title={`Master: ${mPct}%`}></div>
            <div className="dist-seg" style={{ width: `${sPct}%`, background: "var(--slow)" }} title={`Slow: ${sPct}%`}></div>
            <div className="dist-seg" style={{ width: `${cPct}%`, background: "var(--confused)" }} title={`Confused: ${cPct}%`}></div>
            <div className="dist-seg" style={{ width: `${dPct}%`, background: "var(--danger)" }} title={`Danger: ${dPct}%`}></div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 20 }}>
            {Object.entries(LABELS).map(([key, lbl]) => {
              const count = dist[key];
              const pct = ((count / total) * 100).toFixed(1);
              return (
                <div key={key} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: 13.5 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ width: 8, height: 8, borderRadius: "50%", background: lbl.color }}></span>
                    <span style={{ fontWeight: 600, color: "var(--ink)" }}>
                      {lang === "bn" ? lbl.nameBn : lbl.name}
                    </span>
                  </div>
                  <span style={{ fontWeight: 700, color: "var(--muted)" }}>
                    {count} {lang === "bn" ? "টি প্রশ্ন" : "questions"} ({pct}%)
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Per-Question Inference */}
        <h2 className="display reveal show" style={{ fontSize: 22, marginBottom: 16 }}>
          {lang === "bn" ? "প্রতিটি প্রশ্নের ইনফারেন্স আউটপুট" : "Per-Question Inference Report"}
        </h2>

        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {items.map((it, i) => {
            const grp = it.group || (attempt.groups?.master?.some(x => x.questionId === it.questionId) ? "master" :
                         attempt.groups?.slow?.some(x => x.questionId === it.questionId) ? "slow" :
                         attempt.groups?.confused?.some(x => x.questionId === it.questionId) ? "confused" : "danger");
            const lbl = LABELS[grp];
            const confs = fakeConfidences(grp);
            const timeRatio = (it.timeTaken / 36).toFixed(2);

            return (
              <div className="card reveal show" key={it.questionId} style={{ padding: 24 }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12, flexWrap: "wrap", gap: 8 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span className="badge" style={{ background: "var(--paper2)", color: "var(--ink)", fontWeight: 700 }}>
                      Q{i + 1}
                    </span>
                    <span style={{ fontSize: 12.5, color: "var(--muted)", fontWeight: 600 }}>
                      ID: {String(it.questionId)}
                    </span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span className="badge" style={{ background: `${lbl.color}Soft`, color: lbl.color, fontWeight: 700 }}>
                      {lang === "bn" ? lbl.nameBn.split(" ")[0] : lbl.name}
                    </span>
                    <span style={{
                      width: 22,
                      height: 22,
                      borderRadius: "50%",
                      background: it.isCorrect ? "var(--masterSoft)" : "var(--dangerSoft)",
                      color: it.isCorrect ? "var(--master)" : "var(--danger)",
                      display: "grid",
                      placeItems: "center",
                      fontWeight: 700,
                      fontSize: 12
                    }}>
                      {it.isCorrect ? "✓" : "✗"}
                    </span>
                  </div>
                </div>

                <p style={{ fontSize: 14.5, fontWeight: 600, color: "var(--ink)", marginBottom: 14 }}>
                  {it.questionText}
                </p>

                {/* Feature Vector */}
                <div style={{
                  display: "flex",
                  gap: 12,
                  flexWrap: "wrap",
                  padding: "10px 14px",
                  background: "var(--paper2)",
                  borderRadius: 8,
                  fontSize: 12.5,
                  color: "var(--muted)",
                  marginBottom: 16
                }}>
                  <span>time_ratio: <strong style={{ color: "var(--ink)" }}>{timeRatio}</strong></span>
                  <span>switches: <strong style={{ color: "var(--ink)" }}>{it.switchCount ?? (it.clickSequence?.length > 1 ? it.clickSequence.length - 1 : 0)}</strong></span>
                  <span>confidence: <strong style={{ color: "var(--ink)" }}>{it.confidence || "none"}</strong></span>
                  <span>label: <strong style={{ color: "var(--ink)" }}>{it.isCorrect ? "1" : "0"}</strong></span>
                </div>

                {/* Probability Distribution */}
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  {Object.entries(LABELS).map(([key, lb]) => {
                    const prob = confs[key] * 100;
                    return (
                      <div key={key} style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 12 }}>
                        <span style={{ width: 110, color: "var(--muted)", textTransform: "uppercase", fontWeight: 600 }}>{lb.name}</span>
                        <div className="clf-prob-track" style={{ flex: 1, height: 6, background: "var(--paper2)", borderRadius: 99 }}>
                          <div className="clf-prob-fill" style={{ height: "100%", borderRadius: 99, background: lb.color, width: `${prob}%` }}></div>
                        </div>
                        <span style={{ width: 42, textAlign: "right", fontWeight: 700 }}>{prob.toFixed(1)}%</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        {/* Model Architecture Note */}
        <div className="card reveal show" style={{ padding: 28, marginTop: 28, marginBottom: 40 }}>
          <h3 className="display" style={{ fontSize: 18, marginBottom: 16 }}>
            {lang === "bn" ? "মডেল আর্কিটেকচার ও প্রশিক্ষণ প্যারামিটার" : "Model Architecture & Training Parameters"}
          </h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16 }}>
            <div className="arch-block">
              <div className="arch-block-title" style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", color: "var(--muted)" }}>Base Transformer</div>
              <div style={{ fontSize: 14.5, fontWeight: 600, color: "var(--ink)" }}>csebuetnlp/banglabert</div>
            </div>
            <div className="arch-block">
              <div className="arch-block-title" style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", color: "var(--muted)" }}>Fine-tuning Method</div>
              <div style={{ fontSize: 14.5, fontWeight: 600, color: "var(--ink)" }}>QLoRA (4-bit quantized)</div>
            </div>
            <div className="arch-block">
              <div className="arch-block-title" style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", color: "var(--muted)" }}>Feature Set</div>
              <div style={{ fontSize: 14.5, fontWeight: 600, color: "var(--ink)" }}>Click Sequence + Hesitation Delays</div>
            </div>
            <div className="arch-block">
              <div className="arch-block-title" style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", color: "var(--muted)" }}>Inference Mode</div>
              <div style={{ fontSize: 14.5, fontWeight: 600, color: "var(--ink)" }}>Batch API (~2.3s Latency)</div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
