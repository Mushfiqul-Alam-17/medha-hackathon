// MEDHA shared helpers — insight lines & formatting + i18n
export const LETTERS = ["A", "B", "C", "D"];

// ── Translation strings ──
const S = {
  en: {
    // Nav
    navHome: "Home", navExam: "Exam", navDna: "DNA Report",
    navNotes: "Study Notes", navReadiness: "Readiness", navAnxiety: "Anxiety",
    navRetake: "Retake",
    // Landing
    heroEyebrow: "Behavioral Intelligence Exam",
    heroTitle1: "Know ", heroTitleAccent: "how", heroTitle2: " you think,",
    heroTitle3: "not just what you know.",
    heroSub: "MEDHA tracks your exam behavior — timing, hesitation, answer switches — and builds a cognitive DNA report. Built for Bangladeshi medical admission students.",
    startExam: "Start Exam →", seeHow: "See How It Works",
    stat1: "12", stat1l: "Biology Questions",
    stat2: "4", stat2l: "Behavior Groups",
    stat3: "30s", stat3l: "Per Question",
    featTitle: "More than scores",
    feat1h: "Behavior Tracking", feat1p: "Every click, hesitation, and answer switch is recorded in real-time.",
    feat2h: "DNA Report", feat2p: "4 cognitive groups: Mastered, Slow, Confused, Confidently Wrong.",
    feat3h: "AI Study Notes", feat3p: "Personalized notes generated from your weak areas — not generic content.",
    classTitle: "The 4 Behavior Groups",
    clsMasterTag: "MASTERED", clsMasterH: "Fast & Correct", clsMasterP: "You knew it instantly. No hesitation. This concept is fully internalized.",
    clsSlowTag: "SLOW", clsSlowH: "Correct but Slow", clsSlowP: "You got it right, but took too long. In a real exam, time runs out.",
    clsConfusedTag: "CONFUSED", clsConfusedH: "Switched Answers", clsConfusedP: "Multiple answer changes signal concept confusion — even if the final answer was right.",
    clsDangerTag: "DANGER", clsDangerH: "Confidently Wrong", clsDangerP: "Fast + wrong + no hesitation. The most dangerous pattern — you don't know you're wrong.",
    howTitle: "How MEDHA Works",
    how1: "Mood Check", how1p: "Pre-exam emotional state capture.",
    how2: "Live Exam", how2p: "12 Biology MCQs with 30s timer + behavior tracking.",
    how3: "DNA Report", how3p: "Behavioral classification of every answer.",
    how4: "Study Notes", how4p: "Personalized notes from your weak spots.",
    how5: "Readiness", how5p: "Admission readiness score with chapter heatmap.",
    footer: "MEDHA — Behavioral Intelligence for Medical Admission",
    // Mood
    moodTitle: "How are you feeling right now?",
    moodSub: "This helps us understand your exam behavior in context.",
    moodGreat: "Great", moodGood: "Good", moodOkay: "Okay",
    moodTired: "Tired", moodStressed: "Stressed",
    moodNote: "Your mood affects performance. Be honest — no judgment.",
    moodStart: "Start Exam →",
    // Exam
    confLabel: "How confident are you?",
    confSure: "Sure", confUnsure: "Unsure", confGuessing: "Guessing",
    skip: "Skip", next: "Next →", finishExam: "Finish Exam →",
    // Result
    scoreSub: "Biology · {total} Questions · Avg Time {avg}s",
    viewDna: "View DNA Report →",
    // DNA
    dnaEyebrow: "Behavior Replay",
    dnaTitle: "Your DNA Report",
    dnaSub: "Each answer classified by thinking pattern — speed, hesitation, and correctness.",
    dnaQuestions: " questions",
    genNotes: "Generate Study Notes →",
    clickPath: "Click path:",
    // Notes
    notesEyebrow: "AI Generated",
    notesTitle: "Personalized Study Notes",
    notesSub: "Generated from your DNA report weak areas — strengths excluded.",
    download: "Download .md",
    notesLoading1: "AI is analyzing your behavior…",
    notesLoading2: "Generating personalized study notes",
    notesEmpty: "Excellent! No weak areas found — all questions mastered. Try again for a new challenge.",
    slowBadge: "Slow — Speed Up",
    confusedBadge: "Confused — Understand Differences",
    dangerBadge: "Danger — Fix Misconception",
    explanation: "Explanation",
    memoryTrick: "Memory Trick",
    trapQ: "Trap Question:",
    whyCorrect: "Why Correct",
    whyTricked: "Why You Got Tricked",
    // Readiness
    readyEyebrow: "Readiness",
    readyTitle: "Readiness Score",
    readySub: "Calculated from your accuracy, mastery, and confidently-wrong answers.",
    readinessOf: "Readiness / 100",
    correctAns: "Correct Answers", mastered: "Mastered",
    confWrong: "Confidently Wrong", avgTime: "Avg Time / Question",
    chapTitle: "Chapter Frequency Heatmap",
    chapSub: "Which chapters appear most in admission exams — focus here.",
    prevAttempts: "Previous Attempts",
    retake: "Retake Exam ↻",
    // Anxiety
    anxEyebrow: "Emotional Intelligence",
    anxTitle: "Exam Anxiety Index",
    anxSub: "Calculated from your mood, hesitation patterns, answer switching, and time pressure.",
    anxLevel: "Anxiety Level",
    anxLow: "Low — Calm & Focused",
    anxMod: "Moderate — Some Pressure",
    anxHigh: "High — Significant Stress",
    anxCrit: "Critical — Overwhelmed",
    anxFactors: "Contributing Factors",
    anxTips: "Management Tips",
    anxTip1: "Practice timed tests regularly to build comfort with pressure.",
    anxTip2: "Use the 5-4-3-2-1 grounding technique before exams.",
    anxTip3: "Focus on breathing: 4 sec inhale, 7 sec hold, 8 sec exhale.",
    anxTip4: "Reframe anxiety as excitement — your body is preparing to perform.",
    // Share
    shareTitle: "Share Your Results",
    shareSub: "Download your DNA report card as an image.",
    shareDownload: "Download Report Card",
    shareCopied: "Image downloaded!",
    // Group defs
    gMasterTag: "Group 1 — Mastered", gMasterLabel: "Mastered",
    gMasterEmpty: "No mastered questions yet.",
    gSlowTag: "Group 2 — Slow", gSlowLabel: "Slow",
    gSlowEmpty: "No slow questions — great speed!",
    gConfusedTag: "Group 3 — Confused", gConfusedLabel: "Confused",
    gConfusedEmpty: "No confusion — decisions were firm!",
    gDangerTag: "Group 4 — Confidently Wrong", gDangerLabel: "Confidently Wrong",
    gDangerEmpty: "No confidently wrong answers — excellent!",
    // Insights
    insMasterFast: "Mastered — fast, correct, no hesitation. This concept is fully yours.",
    insSlowCorrect: "Correct — but took {t}s. At this speed, you may run out of time in the real exam.",
    insSlowWrong: "Wrong & slow — took {t}s and still got it wrong. This topic needs revision.",
    insConfusedCorrect: "Reached the right answer — but path {path} shows concept doubt.",
    insConfusedWrong: "Wrong & confused — multiple switches but still incorrect. Clarify this concept.",
    insDangerFast: "Wrong but fast — no hesitation before picking wrong. Confidently wrong is the most dangerous pattern.",
  },
  bn: {
    navHome: "হোম", navExam: "পরীক্ষা", navDna: "DNA রিপোর্ট",
    navNotes: "স্টাডি নোট", navReadiness: "প্রস্তুতি", navAnxiety: "উদ্বেগ",
    navRetake: "আবার দাও",
    heroEyebrow: "মেডিকেল ভর্তি প্রস্তুতি",
    heroTitle1: "বুঝো ", heroTitleAccent: "কেন", heroTitle2: " ভুল হচ্ছে,",
    heroTitle3: "শুধু পড়লেই হবে না।",
    heroSub: "MEDHA দেখে তুমি কত দ্রুত উত্তর দিচ্ছ, কতবার বদলাচ্ছ, কোথায় আটকে যাচ্ছ — তারপর বলে দেয় কোন টপিকে তুমি ভুল জানো কিন্তু মনে করো ঠিক জানো। মেডিকেল ভর্তি পরীক্ষার জন্য তৈরি।",
    startExam: "পরীক্ষা দাও →", seeHow: "কীভাবে কাজ করে",
    stat1: "১২", stat1l: "জীববিজ্ঞান প্রশ্ন", stat2: "৪", stat2l: "আচরণ গ্রুপ", stat3: "৩০ সে", stat3l: "প্রতি প্রশ্নে",
    featTitle: "নম্বরের বাইরেও কিছু আছে",
    feat1h: "আচরণ ট্র্যাকিং", feat1p: "প্রতিটা ক্লিক, দ্বিধা, উত্তর বদলানো — সব ধরা পড়ে।",
    feat2h: "DNA রিপোর্ট", feat2p: "৪ ভাগে ভাগ করে: পারো, ধীর, গোলমাল, ভুল জানো।",
    feat3h: "AI স্টাডি নোট", feat3p: "যেখানে দুর্বল সেখানকার নোট — সবার জন্য এক রকম না।",
    classTitle: "৪টা আচরণ গ্রুপ",
    clsMasterTag: "পারো", clsMasterH: "ঝটপট ঠিক উত্তর", clsMasterP: "এক সেকেন্ডেই পেরেছ। এটা তোমার পাকা।",
    clsSlowTag: "ধীর", clsSlowH: "ঠিক কিন্তু সময় বেশি", clsSlowP: "উত্তর ঠিক, কিন্তু আসল পরীক্ষায় এত সময় পাবে না।",
    clsConfusedTag: "গোলমাল", clsConfusedH: "উত্তর বারবার বদলেছ", clsConfusedP: "একটা দিয়ে আবার সরিয়েছ — মানে কনসেপ্ট ক্লিয়ার না।",
    clsDangerTag: "বিপদ", clsDangerH: "ভুল জানো, বুঝতেও পারো না", clsDangerP: "দ্রুত ভুল দিয়েছ আর ভেবেছ ঠিক আছে। এটাই সবচেয়ে ক্ষতিকর।",
    howTitle: "MEDHA কীভাবে কাজ করে",
    how1: "মুড চেক", how1p: "পরীক্ষার আগে জানতে চায় তুমি কেমন আছ।",
    how2: "লাইভ পরীক্ষা", how2p: "১২টা MCQ, প্রশ্নে ৩০ সেকেন্ড, আচরণ ট্র্যাক হয়।",
    how3: "DNA রিপোর্ট", how3p: "প্রতিটা উত্তরকে আচরণ দিয়ে বিচার করে।",
    how4: "স্টাডি নোট", how4p: "যেখানে দুর্বল সেখানে ফোকাসড নোট।",
    how5: "প্রস্তুতি স্কোর", how5p: "ভর্তি পরীক্ষায় কতটুকু রেডি সেটা বলে দেয়।",
    footer: "MEDHA — মেডিকেল ভর্তির জন্য আচরণভিত্তিক প্রস্তুতি",
    moodTitle: "এখন মনটা কেমন?",
    moodSub: "তোমার মেজাজ পরীক্ষার আচরণে প্রভাব ফেলে।",
    moodGreat: "দারুণ", moodGood: "ভালো", moodOkay: "চলবে",
    moodTired: "ক্লান্ত", moodStressed: "চাপে আছি",
    moodNote: "সৎ থাকো — কেউ বিচার করবে না।",
    moodStart: "পরীক্ষা দাও →",
    confLabel: "কতটা নিশ্চিত?",
    confSure: "নিশ্চিত", confUnsure: "কনফিউজড", confGuessing: "আন্দাজে",
    skip: "বাদ দাও", next: "পরের →", finishExam: "পরীক্ষা শেষ →",
    scoreSub: "জীববিজ্ঞান · {total}টা প্রশ্ন · গড় {avg} সেকেন্ড",
    viewDna: "DNA রিপোর্ট দেখো →",
    dnaEyebrow: "আচরণ রিপ্লে", dnaTitle: "তোমার DNA রিপোর্ট",
    dnaSub: "প্রতিটা উত্তর — কত দ্রুত, কতবার বদলেছ, ঠিক না ভুল — সব দিয়ে বিচার।",
    dnaQuestions: "টা প্রশ্ন", genNotes: "স্টাডি নোট বানাও →", clickPath: "ক্লিক পথ:",
    notesEyebrow: "AI তৈরি", notesTitle: "তোমার জন্য স্টাডি নোট",
    notesSub: "DNA রিপোর্টের দুর্বল জায়গা থেকে বানানো — যেটা পারো সেটা বাদ।",
    download: "ডাউনলোড .md",
    notesLoading1: "AI তোমার আচরণ দেখছে…",
    notesLoading2: "স্টাডি নোট বানাচ্ছে",
    notesEmpty: "সব ঠিক আছে! কোনো দুর্বল জায়গা নেই — আবার দাও কঠিন সেশনে।",
    slowBadge: "ধীর — স্পিড বাড়াও", confusedBadge: "গোলমাল — পার্থক্য বোঝো",
    dangerBadge: "বিপদ — ভুল ধারণা ঠিক করো",
    explanation: "ব্যাখ্যা", memoryTrick: "মনে রাখার শর্টকাট", trapQ: "ফাঁদ প্রশ্ন:",
    whyCorrect: "কেন ঠিক", whyTricked: "কোথায় ভুল হলো",
    readyEyebrow: "প্রস্তুতি", readyTitle: "তুমি কতটুকু রেডি?",
    readySub: "কত ঠিক, কত পারো, কত ভুল জানো — সব মিলিয়ে।",
    readinessOf: "রেডিনেস / ১০০",
    correctAns: "ঠিক উত্তর", mastered: "পাকা",
    confWrong: "ভুল জানো", avgTime: "গড় সময়",
    chapTitle: "অধ্যায় ভিত্তিক গুরুত্ব",
    chapSub: "১০ বছরের পরীক্ষায় কোন অধ্যায় থেকে বেশি এসেছে।",
    prevAttempts: "আগের পরীক্ষা", retake: "আবার দাও ↻",
    anxEyebrow: "মানসিক অবস্থা", anxTitle: "পরীক্ষার চাপ কতটুকু?",
    anxSub: "মেজাজ, দ্বিধা, উত্তর বদলানো আর সময়ের চাপ — সব মিলিয়ে।",
    anxLevel: "চাপের মাত্রা",
    anxLow: "কম — শান্ত, ফোকাসড", anxMod: "মাঝারি — একটু চাপ",
    anxHigh: "বেশি — অনেক চাপ", anxCrit: "ক্রিটিকাল — সামলাতে পারছ না",
    anxFactors: "কী কারণে চাপ",
    anxTips: "কী করতে পারো",
    anxTip1: "টাইমার দিয়ে প্র্যাকটিস করো — চাপে পরীক্ষা দেওয়ার অভ্যাস হবে।",
    anxTip2: "পরীক্ষার আগে 5-4-3-2-1 গ্রাউন্ডিং — ৫টা জিনিস দেখো, ৪টা ছোঁও।",
    anxTip3: "৪ সেকেন্ড শ্বাস নাও, ৭ সেকেন্ড ধরে রাখো, ৮ সেকেন্ডে ছাড়ো।",
    anxTip4: "টেনশন মানে তোমার ব্রেইন রেডি হচ্ছে — এটা ভালো সাইন।",
    shareTitle: "ফলাফল শেয়ার করো", shareSub: "DNA রিপোর্ট কার্ড ইমেজ হিসেবে ডাউনলোড করো।",
    shareDownload: "রিপোর্ট কার্ড ডাউনলোড", shareCopied: "ডাউনলোড হয়েছে!",
    gMasterTag: "গ্রুপ ১ — পারো", gMasterLabel: "পারো", gMasterEmpty: "এখনো কিছু মাস্টার হয়নি।",
    gSlowTag: "গ্রুপ ২ — ধীর", gSlowLabel: "ধীর গতি", gSlowEmpty: "কোনো ধীর প্রশ্ন নেই — দারুণ!",
    gConfusedTag: "গ্রুপ ৩ — গোলমাল", gConfusedLabel: "গোলমাল", gConfusedEmpty: "কোনো গোলমাল নেই!",
    gDangerTag: "গ্রুপ ৪ — ভুল জানো", gDangerLabel: "ভুল জানো", gDangerEmpty: "কোনো ভুল ধারণা নেই — অসাধারণ!",
    insMasterFast: "পাকা — ঝটপট ঠিক, কোনো দ্বিধা নেই। এই কনসেপ্ট তোমার আয়ত্তে।",
    insSlowCorrect: "ঠিক — কিন্তু {t} সেকেন্ড লেগেছে। আসল পরীক্ষায় এত সময় থাকবে না।",
    insSlowWrong: "ভুল আর ধীর — {t} সেকেন্ড নিয়েও পারোনি। এটা আবার পড়ো।",
    insConfusedCorrect: "শেষে ঠিক দিয়েছ — কিন্তু ক্লিক পথ {path} দেখায় কনসেপ্ট পাকা না।",
    insConfusedWrong: "ভুল আর গোলমাল — বারবার বদলেও ভুল। এই টপিক ক্লিয়ার করো।",
    insDangerFast: "ভুল কিন্তু ঝটপট — একটুও ভাবোনি। মনে করো ঠিক জানো কিন্তু আসলে ভুল। সবচেয়ে বিপজ্জনক।",
    share: "শেয়ার",
  }
};

export function t(key, lang = "en") { return S[lang]?.[key] || S.en[key] || key; }

export function buildInsight(item, lang = "en") {
  const tm = item.timeTaken;
  const switched = item.switchCount >= 1;
  const correct = item.isCorrect;
  const fast = tm <= 6;
  if (switched) {
    return correct
      ? { cls: "ins-confused", text: t("insConfusedCorrect", lang).replace("{path}", item.clickSequence.join("→")) }
      : { cls: "ins-confused", text: t("insConfusedWrong", lang) };
  }
  if (fast && !correct) return { cls: "ins-danger", text: t("insDangerFast", lang) };
  if (fast && correct) return { cls: "ins-master", text: t("insMasterFast", lang) };
  return correct
    ? { cls: "ins-slow", text: t("insSlowCorrect", lang).replace("{t}", tm) }
    : { cls: "ins-slow", text: t("insSlowWrong", lang).replace("{t}", tm) };
}

export function groupDefs(lang = "en") {
  return {
    master: { cls: "g-master", tagText: t("gMasterTag", lang), label: t("gMasterLabel", lang), empty: t("gMasterEmpty", lang) },
    slow: { cls: "g-slow", tagText: t("gSlowTag", lang), label: t("gSlowLabel", lang), empty: t("gSlowEmpty", lang) },
    confused: { cls: "g-confused", tagText: t("gConfusedTag", lang), label: t("gConfusedLabel", lang), empty: t("gConfusedEmpty", lang) },
    danger: { cls: "g-danger", tagText: t("gDangerTag", lang), label: t("gDangerLabel", lang), empty: t("gDangerEmpty", lang) },
  };
}

export const GROUP_DEFS = groupDefs("en");

export function scoreTitle(pct) {
  if (pct === 1) return "Perfect Score";
  if (pct >= 0.8) return "Excellent Work";
  if (pct >= 0.6) return "Good Effort";
  if (pct >= 0.4) return "Keep Pushing";
  return "Needs Practice";
}

export function computeAnxiety(attempt) {
  const items = attempt.items || [];
  const mood = attempt.mood;
  let score = 0;
  const factors = [];
  // Mood factor
  const moodScores = { stressed: 30, tired: 20, okay: 10, good: 5, great: 0 };
  score += moodScores[mood] || 10;
  if (mood === "stressed" || mood === "tired") factors.push({ label: "Pre-exam mood: " + mood, impact: moodScores[mood], color: "var(--red)" });
  // Switching factor
  const switches = items.filter(i => i.switchCount >= 1).length;
  const switchPct = items.length ? (switches / items.length) * 100 : 0;
  if (switchPct > 0) { score += switchPct * 0.4; factors.push({ label: `Answer switching: ${switches}/${items.length} questions`, impact: Math.round(switchPct * 0.4), color: "var(--amber)" }); }
  // Time pressure
  const timeouts = items.filter(i => i.timeTaken >= 25).length;
  if (timeouts > 0) { score += timeouts * 8; factors.push({ label: `Time pressure: ${timeouts} questions near timeout`, impact: timeouts * 8, color: "var(--red)" }); }
  // Low confidence
  const guessing = items.filter(i => i.confidence === "guessing").length;
  if (guessing > 0) { score += guessing * 6; factors.push({ label: `Guessing: ${guessing} questions`, impact: guessing * 6, color: "var(--amber)" }); }
  // Danger questions (confidently wrong)
  const danger = items.filter(i => i.group === "danger").length;
  if (danger > 0) { score += danger * 5; factors.push({ label: `Blind spots: ${danger} confidently wrong`, impact: danger * 5, color: "var(--red)" }); }
  score = Math.min(100, Math.max(0, Math.round(score)));
  let level, levelCls;
  if (score <= 25) { level = "low"; levelCls = "anx-low"; }
  else if (score <= 50) { level = "mod"; levelCls = "anx-mod"; }
  else if (score <= 75) { level = "high"; levelCls = "anx-high"; }
  else { level = "crit"; levelCls = "anx-crit"; }
  return { score, level, levelCls, factors };
}
