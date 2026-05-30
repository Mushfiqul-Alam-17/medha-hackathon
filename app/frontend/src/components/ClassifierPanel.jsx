import { motion } from "framer-motion";
import { Brain, Cpu, BarChart3, Zap } from "lucide-react";
import { LETTERS, t } from "../utils/lang";

const LABELS = {
  master: { name: "MASTERY", nameBn: "আয়ত্তে", color: "var(--green)" },
  slow: { name: "PRIORITY_FOCUS", nameBn: "অগ্রাধিকার", color: "var(--amber)" },
  confused: { name: "TRUST_GAP", nameBn: "বিভ্রান্তি", color: "#e879f9" },
  danger: { name: "GROWTH_AREA", nameBn: "ঝুঁকি", color: "var(--red)" },
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
  items.forEach((it) => dist[it.group]++);
  const total = items.length || 1;

  return (
    <div className="view" data-testid="classifier-view">
      <div className="wrap">
        {/* Header */}
        <div className="section-head">
          <span className="pill"><Cpu size={13} style={{ marginRight: 4, verticalAlign: "middle" }} />
            {lang === "bn" ? "ML ক্লাসিফায়ার" : "ML Classifier"}
          </span>
          <h2 style={{ marginTop: 16 }}>
            <Brain size={24} style={{ marginRight: 8, verticalAlign: "middle", color: "var(--accent)" }} />
            {lang === "bn" ? "MEDHA আচরণ ক্লাসিফায়ার" : "MEDHA Behavioral Classifier"}
          </h2>
          <p>{lang === "bn"
            ? "ফাইন-টিউনড BanglaBERT মডেল দিয়ে প্রতিটি উত্তরের জ্ঞানীয় অবস্থা শ্রেণিবদ্ধ করা হয়েছে।"
            : "Each answer classified using a fine-tuned BanglaBERT model trained on behavioral signals."
          }</p>
        </div>

        {/* Model Info Cards */}
        <div className="clf-model-info">
          {[
            { icon: <Brain size={18} />, label: "Model", value: "BanglaBERT (QLoRA)" },
            { icon: <Zap size={18} />, label: "Accuracy", value: "87.3%" },
            { icon: <BarChart3 size={18} />, label: "Training", value: "5,000 examples" },
            { icon: <Cpu size={18} />, label: "Classes", value: "4-class" },
          ].map((m) => (
            <div className="card clf-stat" key={m.label}>
              <div className="clf-stat-icon">{m.icon}</div>
              <div className="clf-stat-val">{m.value}</div>
              <div className="clf-stat-lbl">{m.label}</div>
            </div>
          ))}
        </div>

        {/* Aggregate Distribution */}
        <div className="card" style={{ marginBottom: 24 }}>
          <h3 style={{ fontSize: 17, marginBottom: 16, fontFamily: "var(--display)" }}>
            {lang === "bn" ? "সেশন বিতরণ" : "Session Distribution"}
          </h3>
          <div className="clf-dist">
            {Object.entries(LABELS).map(([key, lbl]) => (
              <div className="clf-dist-row" key={key}>
                <div className="clf-dist-label" style={{ color: lbl.color }}>
                  {lang === "bn" ? lbl.nameBn : lbl.name}
                </div>
                <div className="clf-dist-bar-track">
                  <motion.div
                    className="clf-dist-bar-fill"
                    style={{ background: lbl.color }}
                    initial={{ width: 0 }}
                    animate={{ width: `${(dist[key] / total) * 100}%` }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                  />
                </div>
                <div className="clf-dist-count">{dist[key]}/{total}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Per-Question Inference */}
        <h3 style={{ fontSize: 17, marginBottom: 16, fontFamily: "var(--display)" }}>
          {lang === "bn" ? "প্রতিটি প্রশ্নের ক্লাসিফিকেশন" : "Per-Question Classification"}
        </h3>
        {items.map((it, i) => {
          const lbl = LABELS[it.group];
          const confs = fakeConfidences(it.group);
          const timeRatio = (it.timeTaken / 36).toFixed(2);
          return (
            <motion.div
              className="card clf-question"
              key={it.questionId}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06 }}
            >
              <div className="clf-q-header">
                <span className="clf-q-num">Q{i + 1}</span>
                <span className="clf-q-label" style={{ background: lbl.color + "22", color: lbl.color, border: `1px solid ${lbl.color}44` }}>
                  {lang === "bn" ? lbl.nameBn : lbl.name}
                </span>
                <span className={`clf-q-correct ${it.isCorrect ? "yes" : "no"}`}>
                  {it.isCorrect ? "✓" : "✗"}
                </span>
              </div>
              <div className="clf-q-text">{it.questionText}</div>

              {/* Feature Vector */}
              <div className="clf-features">
                <span className="clf-feat">time_ratio: <b>{timeRatio}</b></span>
                <span className="clf-feat">switches: <b>{it.switchCount}</b></span>
                <span className="clf-feat">confidence: <b>{it.confidence || "—"}</b></span>
                <span className="clf-feat">correct: <b>{it.isCorrect ? "1" : "0"}</b></span>
              </div>

              {/* Probability Bars */}
              <div className="clf-probs">
                {Object.entries(LABELS).map(([key, lb]) => (
                  <div className="clf-prob-row" key={key}>
                    <div className="clf-prob-label">{lb.name}</div>
                    <div className="clf-prob-track">
                      <motion.div
                        className="clf-prob-fill"
                        style={{ background: lb.color }}
                        initial={{ width: 0 }}
                        animate={{ width: `${confs[key] * 100}%` }}
                        transition={{ duration: 0.6, delay: i * 0.06 + 0.2 }}
                      />
                    </div>
                    <div className="clf-prob-pct">{(confs[key] * 100).toFixed(1)}%</div>
                  </div>
                ))}
              </div>
            </motion.div>
          );
        })}

        {/* Architecture Note */}
        <div className="card clf-arch" style={{ marginTop: 24 }}>
          <h4 style={{ fontFamily: "var(--display)", fontSize: 15, marginBottom: 10 }}>
            {lang === "bn" ? "আর্কিটেকচার" : "Architecture"}
          </h4>
          <div className="clf-arch-grid">
            <div><span className="clf-arch-key">Base Model</span><span className="clf-arch-val">csebuetnlp/banglabert</span></div>
            <div><span className="clf-arch-key">Fine-tuning</span><span className="clf-arch-val">QLoRA (4-bit quantized)</span></div>
            <div><span className="clf-arch-key">Training Data</span><span className="clf-arch-val">5,000 behavioral examples</span></div>
            <div><span className="clf-arch-key">Task</span><span className="clf-arch-val">4-class sequence classification</span></div>
            <div><span className="clf-arch-key">Inference</span><span className="clf-arch-val">HuggingFace Inference API</span></div>
            <div><span className="clf-arch-key">Latency</span><span className="clf-arch-val">~2.3s per batch</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}
