import { useState, useEffect } from "react";
import { Check, X, Timer, Award, Repeat2, AlertTriangle, Sparkles, ArrowRight } from "lucide-react";
import { LETTERS, buildInsight, groupDefs, t } from "../utils/lang";

const ORDER = ["master", "slow", "confused", "danger"];
const ICONS = { master: Award, slow: Timer, confused: Repeat2, danger: AlertTriangle };
const CIRC = 414.7; // 2 * Math.PI * 66

function DnaCard({ item, lang, idx }) {
  const insight = buildInsight(item, lang);
  
  // Chip logic
  const isFast = item.timeTaken <= 8;
  const isSlow = item.timeTaken >= 25;
  const switchCount = item.clickSequence?.length > 1 ? item.clickSequence.length - 1 : 0;

  return (
    <div className="card" style={{ padding: 22, marginBottom: 12, background: "var(--card)" }}>
      {/* Meta Row */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10, fontSize: 12, color: "var(--muted)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span className="badge" style={{ background: "var(--paper2)", color: "var(--ink)", fontWeight: 700 }}>
            Q{idx + 1}
          </span>
          <span>{item.chapter}</span>
        </div>
        <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <Timer size={13} /> {item.timeTaken}s {lang === "bn" ? "প্রতিক্রিয়া" : "response"}
        </span>
      </div>

      {/* Question Text */}
      <p style={{ fontSize: "14.5px", fontWeight: 600, color: "var(--ink)", marginBottom: 12 }}>
        {item.questionText}
      </p>

      {/* Selected Option Info */}
      <p style={{ fontSize: "13.5px", color: "var(--muted)", marginBottom: 12 }}>
        {lang === "bn" ? "উত্তর প্রদান:" : "Selected:"}{" "}
        <strong style={{ color: item.isCorrect ? "var(--master)" : "var(--danger)" }}>
          {item.finalAnswerIndex !== null && item.finalAnswerIndex !== undefined
            ? `${LETTERS[item.finalAnswerIndex]}. ${item.options[item.finalAnswerIndex]}`
            : (lang === "bn" ? "স্কিপড (কোনো উত্তর দেওয়া হয়নি)" : "Skipped")}
        </strong>
      </p>

      {/* Click Path (if any) */}
      {item.clickSequence?.length > 0 && (
        <div className="click-path" style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", margin: "10px 0", padding: "8px 12px", background: "var(--paper2)", borderRadius: 8 }}>
          <span className="cp-label" style={{ fontSize: 12, color: "var(--muted)", fontWeight: 600 }}>
            {t("clickPath", lang)}
          </span>
          {item.clickSequence.map((l, sIdx) => {
            const isLast = sIdx === item.clickSequence.length - 1;
            const nodeBg = isLast
              ? (item.isCorrect ? "var(--masterSoft)" : "var(--dangerSoft)")
              : "var(--line)";
            const nodeColor = isLast
              ? (item.isCorrect ? "var(--master)" : "var(--danger)")
              : "var(--muted)";
            return (
              <span key={sIdx} style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                <span style={{
                  padding: "2px 6px",
                  borderRadius: 4,
                  fontSize: 11.5,
                  fontWeight: 700,
                  background: nodeBg,
                  color: nodeColor
                }}>
                  {l}
                </span>
                {sIdx < item.clickSequence.length - 1 && <span style={{ fontSize: 11, color: "var(--muted)" }}>→</span>}
              </span>
            );
          })}
        </div>
      )}

      {/* Behavior Chips */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 12 }}>
        {isFast && (
          <span className="badge badge-master" style={{ fontSize: 11, padding: "3px 10px" }}>
            {lang === "bn" ? "⚡ খুব দ্রুত" : "⚡ Very Fast"}
          </span>
        )}
        {isSlow && (
          <span className="badge badge-slow" style={{ fontSize: 11, padding: "3px 10px" }}>
            {lang === "bn" ? "🐢 ধীর গতি" : "🐢 Hesitant"}
          </span>
        )}
        {switchCount > 0 && (
          <span className="badge badge-confused" style={{ fontSize: 11, padding: "3px 10px" }}>
            {lang === "bn" ? `🔀 ${switchCount} বার পরিবর্তন` : `🔀 ${switchCount} switches`}
          </span>
        )}
        {item.confidence && (
          <span className="badge" style={{
            fontSize: 11,
            padding: "3px 10px",
            background: item.confidence === "sure" ? "var(--masterSoft)" : "var(--paper2)",
            color: item.confidence === "sure" ? "var(--master)" : "var(--muted)",
          }}>
            {item.confidence === "sure"
              ? (lang === "bn" ? "✓ নিশ্চিত" : "✓ Confident")
              : item.confidence === "unsure"
              ? (lang === "bn" ? "⚠ অনিশ্চিত" : "⚠ Unsure")
              : (lang === "bn" ? "🎲 অনুমান" : "🎲 Guessing")}
          </span>
        )}
      </div>

      {/* Textual Insight */}
      <div className={`dna-insight ${insight.cls}`} style={{ marginTop: 12, padding: "10px 14px", borderRadius: 8, fontSize: 13, borderLeft: "3px solid currentColor" }}>
        {insight.text}
      </div>
    </div>
  );
}

export default function DnaReport({ attempt, onViewNotes, lang }) {
  const groups = attempt.groups || {};
  const items = attempt.items || [];
  const defs = groupDefs(lang);

  const correct = attempt.readiness?.correct ?? items.filter(it => it.isCorrect).length;
  const total = attempt.readiness?.total ?? items.length;
  const scorePct = total ? Math.round((correct / total) * 100) : 0;
  
  const [offset, setOffset] = useState(CIRC);

  useEffect(() => {
    const tm = setTimeout(() => setOffset(CIRC * (1 - correct / total)), 250);
    return () => clearTimeout(tm);
  }, [correct, total]);

  // Phenotype distribution counts
  const masterCount = groups.master?.length || 0;
  const slowCount = groups.slow?.length || 0;
  const confusedCount = groups.confused?.length || 0;
  const dangerCount = groups.danger?.length || 0;
  const totalCount = masterCount + slowCount + confusedCount + dangerCount || 1;

  const masterPct = ((masterCount / totalCount) * 100).toFixed(1);
  const slowPct = ((slowCount / totalCount) * 100).toFixed(1);
  const confusedPct = ((confusedCount / totalCount) * 100).toFixed(1);
  const dangerPct = ((dangerCount / totalCount) * 100).toFixed(1);

  // Dynamic Topic Breakdown
  const topicMap = {};
  items.forEach(it => {
    if (!it.chapter) return;
    if (!topicMap[it.chapter]) {
      topicMap[it.chapter] = { correct: 0, total: 0, items: [] };
    }
    topicMap[it.chapter].total++;
    if (it.isCorrect) {
      topicMap[it.chapter].correct++;
    }
    topicMap[it.chapter].items.push(it);
  });

  const topicsList = Object.entries(topicMap).map(([name, data]) => {
    const mastery = Math.round((data.correct / data.total) * 100);
    let status = "danger";
    if (mastery >= 80) status = "master";
    else if (mastery >= 60) status = "slow";
    else if (mastery >= 40) status = "confused";
    return { name, mastery, status, total: data.total };
  });

  const switchesCount = items.reduce(
    (sum, it) => sum + (it.clickSequence?.length > 1 ? it.clickSequence.length - 1 : 0),
    0
  );
  const skippedCount = items.filter(it => it.finalAnswerIndex === null).length;
  
  const totalTime = items.reduce((sum, it) => sum + (it.timeTaken || 0), 0);
  const avgTime = items.length > 0 ? (totalTime / items.length).toFixed(1) : 0;
  const speedRatio = items.length > 0 ? (avgTime / 45).toFixed(1) : 0;

  return (
    <div className="view fade-in" data-testid="dna-view" style={{ background: "var(--paper)" }}>
      <div className="container-md screen-inner" style={{ paddingTop: 32 }}>
        
        {/* Title */}
        <div className="reveal show">
          <div className="eyebrow" style={{ marginBottom: 8 }}>{t("dnaEyebrow", lang)}</div>
          <h1 className="display" style={{ fontSize: "clamp(40px, 5vw, 60px)", marginBottom: 10 }}>
            {t("dnaTitle", lang)}
          </h1>
          <p style={{ fontSize: "16.5px", color: "var(--muted)", maxWidth: 580, lineHeight: 1.7, marginBottom: 28 }}>
            {lang === "bn"
              ? `আমরা আপনার ${items.length}টি উত্তরের আচরণগত বিশ্লেষণ সম্পন্ন করেছি। এখানে আপনার ৪টি চিন্তাধারার ধরণ বিশ্লেষণ করা হলো:`
              : `We analyzed ${items.length} responses to map how you make choices, handle doubt, and allocate time. Four behavioral phenotypes identified.`}
          </p>
        </div>

        {/* DNA distribution bar */}
        <div className="card reveal show" style={{ padding: "24px 28px", marginBottom: 28 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12, flexWrap: "wrap", gap: 8 }}>
            <span style={{ fontSize: "11.5px", fontWeight: 700, letterSpacing: ".14em", textTransform: "uppercase", color: "var(--muted)" }}>
              {lang === "bn" ? `ফেনোটাইপ বিভাজন · ${items.length}টি প্রশ্ন` : `Phenotype Distribution · ${items.length} Questions`}
            </span>
            <div style={{ display: "flex", gap: 16, fontSize: 12, flexWrap: "wrap" }}>
              <span style={{ display: "flex", alignItems: "center", gap: 5 }}><span style={{ width: 9, height: 9, borderRadius: "50%", background: "var(--master)" }}></span>{defs.master.label}</span>
              <span style={{ display: "flex", alignItems: "center", gap: 5 }}><span style={{ width: 9, height: 9, borderRadius: "50%", background: "var(--slow)" }}></span>{defs.slow.label}</span>
              <span style={{ display: "flex", alignItems: "center", gap: 5 }}><span style={{ width: 9, height: 9, borderRadius: "50%", background: "var(--confused)" }}></span>{defs.confused.label}</span>
              <span style={{ display: "flex", alignItems: "center", gap: 5 }}><span style={{ width: 9, height: 9, borderRadius: "50%", background: "var(--danger)" }}></span>{defs.danger.label}</span>
            </div>
          </div>

          <div className="dna-bar" style={{ display: "flex", gap: 4, height: 16, borderRadius: 999, overflow: "hidden", margin: "16px 0" }}>
            <div className="dna-seg" style={{ width: `${masterPct}%`, background: "var(--master)" }} title={`Master: ${masterPct}%`}></div>
            <div className="dna-seg" style={{ width: `${slowPct}%`, background: "var(--slow)" }} title={`Slow: ${slowPct}%`}></div>
            <div className="dna-seg" style={{ width: `${confusedPct}%`, background: "var(--confused)" }} title={`Confused: ${confusedPct}%`}></div>
            <div className="dna-seg" style={{ width: `${dangerPct}%`, background: "var(--danger)" }} title={`Danger: ${dangerPct}%`}></div>
          </div>

          <div style={{ display: "flex", flexWrap: "wrap", gap: 20, marginTop: 12, fontSize: 13, color: "var(--muted)" }}>
            <span>{lang === "bn" ? "সঠিকতা:" : "Accuracy:"} <strong style={{ color: "var(--ink)" }}>{scorePct}%</strong></span>
            <span>{lang === "bn" ? "গড় সময়:" : "Avg Response:"} <strong style={{ color: "var(--ink)" }}>{avgTime}s</strong></span>
            <span>{lang === "bn" ? "পরিবর্তন সংখ্যা:" : "Switches:"} <strong style={{ color: "var(--ink)" }}>{switchesCount}</strong></span>
            <span>{lang === "bn" ? "বাদ দেওয়া:" : "Skipped:"} <strong style={{ color: "var(--ink)" }}>{skippedCount}</strong></span>
          </div>
        </div>

        {/* Dashboard layout (Score + Quick Stats) */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 20, marginBottom: 28 }} className="reveal show">
          
          {/* Ring Card */}
          <div className="card" style={{ padding: 28, display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center" }}>
            <div className="score-ring-wrap" style={{ width: 160, height: 160 }}>
              <svg width="160" height="160" viewBox="0 0 160 160">
                <circle cx="80" cy="80" r="66" fill="none" stroke="var(--paper2)" strokeWidth="12" />
                <circle
                  cx="80"
                  cy="80"
                  r="66"
                  fill="none"
                  stroke="var(--sage)"
                  strokeWidth="12"
                  strokeLinecap="round"
                  strokeDasharray={CIRC}
                  strokeDashoffset={offset}
                  id="dnaRing"
                  style={{ transition: "stroke-dashoffset 1.4s cubic-bezier(.4,0,.2,1)" }}
                />
              </svg>
              <div className="ring-center">
                <span className="ring-score" id="dnaScore" style={{ color: "var(--sage)" }}>
                  {correct}
                </span>
                <span className="ring-label">{lang === "bn" ? "সঠিক উত্তর" : "Correct"}</span>
              </div>
            </div>
            <span className="badge badge-master" style={{ marginTop: 14, fontSize: 13, padding: "6px 18px" }}>
              {lang === "bn" ? "মাস্টারি লেভেল" : "Mastery Level"}
            </span>
          </div>

          {/* Quick stats grid */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
            <div className="card" style={{ padding: 18 }}>
              <span className="display" style={{ fontSize: 28, fontWeight: 600, display: "block" }}>{items.length}</span>
              <span style={{ fontSize: 13, color: "var(--muted)", marginTop: 4, display: "block" }}>
                {lang === "bn" ? "উত্তর দেওয়া হয়েছে" : "Questions Answered"}
              </span>
            </div>
            <div className="card" style={{ padding: 18 }}>
              <span className="display" style={{ fontSize: 28, fontWeight: 600, display: "block" }}>{scorePct}%</span>
              <span style={{ fontSize: 13, color: "var(--muted)", marginTop: 4, display: "block" }}>
                {lang === "bn" ? "সঠিকতার হার" : "Accuracy Rate"}
              </span>
            </div>
            <div className="card" style={{ padding: 18 }}>
              <span className="display" style={{ fontSize: 28, fontWeight: 600, display: "block" }}>{speedRatio}x</span>
              <span style={{ fontSize: 13, color: "var(--muted)", marginTop: 4, display: "block" }}>
                {lang === "bn" ? "গড় গতির তুলনা" : "Speed Ratio"}
              </span>
            </div>
            <div className="card" style={{ padding: 18 }}>
              <span className="display" style={{ fontSize: 28, fontWeight: 600, display: "block" }}>
                {topicsList.length}
              </span>
              <span style={{ fontSize: 13, color: "var(--muted)", marginTop: 4, display: "block" }}>
                {lang === "bn" ? "বিশ্লেষিত অধ্যায়" : "Chapters Analyzed"}
              </span>
            </div>
          </div>

        </div>

        {/* Cognitive Phenotype Progress Rows */}
        <div className="card reveal show" style={{ padding: 28, marginBottom: 28 }}>
          <h2 className="display" style={{ fontSize: 22, marginBottom: 6 }}>
            {lang === "bn" ? "আচরণগত ক্লাসিফিকেশন" : "Cognitive Phenotypes"}
          </h2>
          <p style={{ fontSize: 14, color: "var(--muted)", marginBottom: 24 }}>
            {lang === "bn" ? "আপনার উত্তরগুলো যে ৪টি গ্রুপে ভাগ হয়েছে তার অনুপাত:" : "Breakdown of your problem-solving approaches."}
          </p>

          <div className="class-row">
            <div className="class-meta">
              <div className="class-name"><span className="dot-sm" style={{ background: "var(--master)" }}></span>{defs.master.label}</div>
              <div className="class-desc">{lang === "bn" ? "সঠিক ও আত্মবিশ্বাসী" : "Confident & correct"}</div>
            </div>
            <div className="bar-track"><div className="bar-fill" style={{ background: "var(--master)", width: `${masterPct}%` }}></div></div>
            <div className="class-val">{masterPct}%</div>
          </div>

          <div className="class-row">
            <div className="class-meta">
              <div className="class-name"><span class="dot-sm" style={{ background: "var(--slow)" }}></span>{defs.slow.label}</div>
              <div className="class-desc">{lang === "bn" ? "সঠিক কিন্তু ধীর" : "Correct but slow/hesitant"}</div>
            </div>
            <div className="bar-track"><div className="bar-fill" style={{ background: "var(--slow)", width: `${slowPct}%` }}></div></div>
            <div className="class-val">{slowPct}%</div>
          </div>

          <div className="class-row">
            <div className="class-meta">
              <div className="class-name"><span class="dot-sm" style={{ background: "var(--confused)" }}></span>{defs.confused.label}</div>
              <div className="class-desc">{lang === "bn" ? "দ্বিধাদ্বন্দ্ব ও উত্তর বদল" : "Switched answers"}</div>
            </div>
            <div className="bar-track"><div className="bar-fill" style={{ background: "var(--confused)", width: `${confusedPct}%` }}></div></div>
            <div className="class-val">{confusedPct}%</div>
          </div>

          <div className="class-row">
            <div className="class-meta">
              <div className="class-name"><span class="dot-sm" style={{ background: "var(--danger)" }}></span>{defs.danger.label}</div>
              <div className="class-desc">{lang === "bn" ? "দ্রুত ও ভুল (বিপদ)" : "Confidently incorrect"}</div>
            </div>
            <div className="bar-track"><div className="bar-fill" style={{ background: "var(--danger)", width: `${dangerPct}%` }}></div></div>
            <div className="class-val">{dangerPct}%</div>
          </div>
        </div>

        {/* Dynamic Topic Breakdown Cards */}
        {topicsList.length > 0 && (
          <>
            <h2 className="display reveal show" style={{ fontSize: 22, marginBottom: 18 }}>
              {lang === "bn" ? "অধ্যায় ভিত্তিক পারফরম্যান্স" : "Topic Breakdown"}
            </h2>
            <div className="topic-grid2 reveal show" style={{ marginBottom: 32 }}>
              {topicsList.map((topic, tIdx) => (
                <div className="card topic-card" key={tIdx} style={{ background: "var(--card)" }}>
                  <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12, marginBottom: 12 }}>
                    <div>
                      <h3 className="display" style={{ fontSize: 18 }}>{topic.name}</h3>
                      <p style={{ fontSize: "12.5px", color: "var(--muted)", marginTop: 3 }}>
                        {topic.total} {lang === "bn" ? "টি প্রশ্ন" : "questions"}
                      </p>
                    </div>
                    <span className={`badge badge-${topic.status}`} style={{ textTransform: "uppercase" }}>
                      {defs[topic.status]?.label || topic.status}
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, color: "var(--muted)", marginBottom: 8 }}>
                    <span>{lang === "bn" ? "দক্ষতা" : "Mastery"}</span>
                    <span>{topic.mastery}%</span>
                  </div>
                  <div className="topic-mini-track" style={{ height: 6, background: "var(--paper2)", borderRadius: 99, overflow: "hidden" }}>
                    <div className="topic-mini-fill" style={{ height: "100%", width: `${topic.mastery}%`, background: `var(--${topic.status})`, borderRadius: 99 }}></div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {/* Detailed Question Replay Section (Screen 6) */}
        <div className="reveal show" style={{ marginTop: 48, marginBottom: 20 }}>
          <div className="eyebrow" style={{ marginBottom: 8 }}>{lang === "bn" ? "বিস্তারিত আচরণ রিপ্লে" : "Detailed Behavior Replay"}</div>
          <h2 className="display" style={{ fontSize: 30 }}>
            {lang === "bn" ? "প্রশ্ন-বাই-প্রশ্ন আচরণগত মানচিত্র" : "Question-by-Question Behavioral Map"}
          </h2>
          <p style={{ fontSize: 14.5, color: "var(--muted)", marginTop: 6 }}>
            {lang === "bn"
              ? "আপনার প্রতিটি উত্তরকে তাদের গতি ও দ্বিধার ধরণ অনুযায়ী সাজানো হয়েছে।"
              : "Every interaction mapped chronologically and classified into its respective phenotype cluster."}
          </p>
        </div>

        {ORDER.map((key) => {
          const def = defs[key];
          const groupItems = groups[key] || [];
          const Ic = ICONS[key];
          return (
            <div className={`dna-group ${def.cls}`} key={key} data-testid={`dna-group-${key}`} style={{ marginTop: 24 }}>
              <div className="dna-group-head" style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 16 }}>
                <div className="dna-group-ic" style={{
                  width: 42,
                  height: 42,
                  borderRadius: 10,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  background: `var(--${key}Soft)`,
                  color: `var(--${key})`
                }}>
                  <Ic size={20} />
                </div>
                <div className="dna-group-meta" style={{ flex: 1 }}>
                  <span className="dna-group-tag" style={{ display: "block", fontSize: 11, fontWeight: 700, letterSpacing: ".1em", textTransform: "uppercase", color: "var(--muted)" }}>
                    {def.tagText}
                  </span>
                  <span className="dna-group-label" style={{ fontSize: 18, fontWeight: 700, fontFamily: "'Hind Siliguri', serif" }}>
                    {def.label}
                  </span>
                </div>
                <span className="dna-group-count" style={{ fontSize: 13, color: "var(--muted)", fontWeight: 600 }}>
                  {groupItems.length} {lang === "bn" ? "টি প্রশ্ন" : "questions"}
                </span>
              </div>
              
              {groupItems.length === 0 ? (
                <div className="card no-group" style={{ padding: 20, textAlign: "center", color: "var(--muted)", fontStyle: "italic" }}>
                  {def.empty}
                </div>
              ) : (
                <div className="dna-cards">
                  {groupItems.map((it) => {
                    const originalIdx = items.findIndex(x => x.questionId === it.questionId);
                    return (
                      <DnaCard
                        key={it.questionId}
                        item={it}
                        lang={lang}
                        idx={originalIdx !== -1 ? originalIdx : 0}
                      />
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}

        {/* Notes Generation CTA */}
        <div className="cta-strip reveal show" style={{ marginTop: 40, marginBottom: 40 }}>
          <div>
            <h3 className="display" style={{ fontSize: 22 }}>
              {lang === "bn" ? "দুর্বল জায়গাগুলো দূর করতে প্রস্তুত?" : "Ready to master these concepts?"}
            </h3>
            <p>
              {lang === "bn"
                ? "আপনার গোলমাল ও বিপজ্জনক ভুল থাকা টপিকগুলোর জন্য একটি ব্যক্তিগতকৃত অধ্যয়ন পরিকল্পনা তৈরি করুন।"
                : "Generate customized explanation sheets and memory shortcuts targeting your exact gaps."}
            </p>
          </div>
          <div className="cta-strip-actions">
            <button className="btn btn-primary" style={{ borderRadius: 10, padding: "12px 22px", display: "inline-flex", alignItems: "center", gap: 8 }} onClick={onViewNotes}>
              {t("genNotes", lang)}
              <ArrowRight size={16} />
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
