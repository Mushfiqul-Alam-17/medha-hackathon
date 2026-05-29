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
    stat1: "8", stat1l: "Biology Questions",
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
    how2: "Live Exam", how2p: "8 Biology MCQs with 30s timer + behavior tracking.",
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
    heroEyebrow: "আচরণভিত্তিক বুদ্ধিমত্তা পরীক্ষা",
    heroTitle1: "জানো ", heroTitleAccent: "কীভাবে", heroTitle2: " তুমি ভাবো,",
    heroTitle3: "শুধু কী জানো তা নয়।",
    heroSub: "MEDHA তোমার পরীক্ষার আচরণ ট্র্যাক করে — সময়, দ্বিধা, উত্তর পরিবর্তন — এবং একটি জ্ঞানীয় DNA রিপোর্ট তৈরি করে। বাংলাদেশি মেডিকেল ভর্তি শিক্ষার্থীদের জন্য তৈরি।",
    startExam: "পরীক্ষা শুরু →", seeHow: "কীভাবে কাজ করে",
    stat1: "৮", stat1l: "জীববিজ্ঞান প্রশ্ন", stat2: "৪", stat2l: "আচরণ গ্রুপ", stat3: "৩০ সে", stat3l: "প্রতি প্রশ্নে",
    featTitle: "শুধু নম্বর নয়",
    feat1h: "আচরণ ট্র্যাকিং", feat1p: "প্রতিটি ক্লিক, দ্বিধা, উত্তর পরিবর্তন রিয়েল-টাইমে রেকর্ড।",
    feat2h: "DNA রিপোর্ট", feat2p: "৪টি গ্রুপ: আয়ত্তে, ধীর, বিভ্রান্ত, আত্মবিশ্বাসী ভুল।",
    feat3h: "AI স্টাডি নোট", feat3p: "তোমার দুর্বল জায়গা থেকে তৈরি — জেনেরিক নয়।",
    classTitle: "৪টি আচরণ গ্রুপ",
    clsMasterTag: "আয়ত্তে", clsMasterH: "দ্রুত ও সঠিক", clsMasterP: "তুমি তৎক্ষণাৎ জানতে। কোনো দ্বিধা নেই।",
    clsSlowTag: "ধীর", clsSlowH: "সঠিক কিন্তু ধীর", clsSlowP: "সঠিক উত্তর দিয়েছ, তবে অনেক সময় লেগেছে।",
    clsConfusedTag: "বিভ্রান্ত", clsConfusedH: "উত্তর বদলেছ", clsConfusedP: "একাধিকবার উত্তর পরিবর্তন ধারণায় দ্বিধা দেখায়।",
    clsDangerTag: "বিপদ", clsDangerH: "আত্মবিশ্বাসী ভুল", clsDangerP: "দ্রুত + ভুল + কোনো দ্বিধা নেই। সবচেয়ে বিপজ্জনক।",
    howTitle: "MEDHA কীভাবে কাজ করে",
    how1: "মুড চেক", how1p: "পরীক্ষার আগে মানসিক অবস্থা।",
    how2: "লাইভ পরীক্ষা", how2p: "৮টি MCQ, ৩০ সে টাইমার + আচরণ ট্র্যাকিং।",
    how3: "DNA রিপোর্ট", how3p: "প্রতিটি উত্তরের আচরণভিত্তিক শ্রেণিবিন্যাস।",
    how4: "স্টাডি নোট", how4p: "দুর্বল জায়গা থেকে ব্যক্তিগত নোট।",
    how5: "প্রস্তুতি", how5p: "ভর্তি প্রস্তুতি স্কোর ও অধ্যায় হিটম্যাপ।",
    footer: "MEDHA — মেডিকেল ভর্তির জন্য আচরণভিত্তিক বুদ্ধিমত্তা",
    moodTitle: "এই মুহূর্তে তোমার মন কেমন?",
    moodSub: "এটি তোমার পরীক্ষার আচরণ বুঝতে সাহায্য করে।",
    moodGreat: "দারুণ", moodGood: "ভালো", moodOkay: "মোটামুটি",
    moodTired: "ক্লান্ত", moodStressed: "চাপে",
    moodNote: "তোমার মেজাজ পারফরম্যান্সে প্রভাব ফেলে। সৎ থাকো।",
    moodStart: "পরীক্ষা শুরু →",
    confLabel: "কতটা নিশ্চিত তুমি?",
    confSure: "নিশ্চিত", confUnsure: "অনিশ্চিত", confGuessing: "অনুমান",
    skip: "Skip", next: "Next →", finishExam: "Finish Exam →",
    scoreSub: "জীববিজ্ঞান · {total}টি প্রশ্ন · গড় সময় {avg}s",
    viewDna: "DNA রিপোর্ট দেখো →",
    dnaEyebrow: "আচরণ রিপ্লে", dnaTitle: "তোমার DNA রিপোর্ট",
    dnaSub: "প্রতিটি উত্তর চিন্তার ধরন অনুযায়ী শ্রেণিবদ্ধ।",
    dnaQuestions: "টি প্রশ্ন", genNotes: "স্টাডি নোট তৈরি করো →", clickPath: "ক্লিক পথ:",
    notesEyebrow: "AI তৈরি", notesTitle: "ব্যক্তিগত স্টাডি নোট",
    notesSub: "তোমার DNA রিপোর্টের দুর্বল জায়গা থেকে তৈরি।",
    download: "ডাউনলোড .md",
    notesLoading1: "AI তোমার আচরণ বিশ্লেষণ করছে…",
    notesLoading2: "ব্যক্তিগত স্টাডি নোট তৈরি হচ্ছে",
    notesEmpty: "চমৎকার! কোনো দুর্বল জায়গা নেই — আবার চেষ্টা করো।",
    slowBadge: "ধীর — গতি বাড়াও", confusedBadge: "বিভ্রান্ত — পার্থক্য বোঝো",
    dangerBadge: "বিপদ — ভুল ধারণা সংশোধন",
    explanation: "ব্যাখ্যা", memoryTrick: "মেমোরি ট্রিক", trapQ: "ফাঁদ প্রশ্ন:",
    whyCorrect: "কেন সঠিক", whyTricked: "কেন ভুল করো",
    readyEyebrow: "প্রস্তুতি", readyTitle: "প্রস্তুতির স্কোর",
    readySub: "সঠিকতা, আয়ত্ত ও আত্মবিশ্বাসী ভুলের ভিত্তিতে।",
    readinessOf: "Readiness / ১০০",
    correctAns: "সঠিক উত্তর", mastered: "আয়ত্তে",
    confWrong: "আত্মবিশ্বাসী ভুল", avgTime: "গড় সময় / প্রশ্ন",
    chapTitle: "অধ্যায় ফ্রিকোয়েন্সি হিটম্যাপ",
    chapSub: "ভর্তি পরীক্ষায় কোন অধ্যায় থেকে বেশি প্রশ্ন আসে।",
    prevAttempts: "আগের প্রচেষ্টা", retake: "আবার চেষ্টা করো ↻",
    anxEyebrow: "আবেগীয় বুদ্ধিমত্তা", anxTitle: "পরীক্ষার উদ্বেগ সূচক",
    anxSub: "মেজাজ, দ্বিধা, উত্তর পরিবর্তন ও সময় চাপের ভিত্তিতে।",
    anxLevel: "উদ্বেগ মাত্রা",
    anxLow: "কম — শান্ত ও মনোযোগী", anxMod: "মাঝারি — কিছু চাপ",
    anxHigh: "উচ্চ — উল্লেখযোগ্য চাপ", anxCrit: "সংকটজনক — অভিভূত",
    anxFactors: "অবদানকারী কারণ",
    anxTips: "ব্যবস্থাপনা পরামর্শ",
    anxTip1: "নিয়মিত সময়সীমাযুক্ত পরীক্ষা অনুশীলন করো।",
    anxTip2: "পরীক্ষার আগে 5-4-3-2-1 গ্রাউন্ডিং কৌশল ব্যবহার করো।",
    anxTip3: "শ্বাসের দিকে মনোযোগ দাও: ৪ সে শ্বাস নাও, ৭ সে ধরো, ৮ সে ছাড়ো।",
    anxTip4: "উদ্বেগকে উত্তেজনা হিসেবে দেখো — তোমার শরীর প্রস্তুত হচ্ছে।",
    shareTitle: "তোমার ফলাফল শেয়ার করো", shareSub: "DNA রিপোর্ট কার্ড ইমেজ হিসেবে ডাউনলোড করো।",
    shareDownload: "রিপোর্ট কার্ড ডাউনলোড", shareCopied: "ইমেজ ডাউনলোড হয়েছে!",
    gMasterTag: "গ্রুপ ১ — আয়ত্তে", gMasterLabel: "আয়ত্তে", gMasterEmpty: "এখনো কোনো আয়ত্ত প্রশ্ন নেই।",
    gSlowTag: "গ্রুপ ২ — ধীর", gSlowLabel: "ধীর গতি", gSlowEmpty: "কোনো ধীর প্রশ্ন নেই — দুর্দান্ত!",
    gConfusedTag: "গ্রুপ ৩ — বিভ্রান্ত", gConfusedLabel: "বিভ্রান্ত", gConfusedEmpty: "কোনো বিভ্রান্তি নেই!",
    gDangerTag: "গ্রুপ ৪ — আত্মবিশ্বাসী ভুল", gDangerLabel: "আত্মবিশ্বাসী ভুল", gDangerEmpty: "কোনো আত্মবিশ্বাসী ভুল নেই — চমৎকার!",
    insMasterFast: "আয়ত্তে — দ্রুত, সঠিক, কোনো দ্বিধা নেই। এই ধারণাটি তোমার পুরোপুরি আয়ত্তে।",
    insSlowCorrect: "সঠিক — তবে {t} সে. লেগেছে। এই গতিতে আসল পরীক্ষায় সময় ফুরিয়ে যেতে পারে।",
    insSlowWrong: "ভুল ও ধীর — {t} সে. লেগেছে তবুও ভুল। এই বিষয়টি আবার পড়া দরকার।",
    insConfusedCorrect: "সঠিক উত্তর দিয়েছ — কিন্তু ক্লিক পথ {path} ধারণায় দ্বিধা প্রকাশ করে।",
    insConfusedWrong: "ভুল ও বিভ্রান্ত — একাধিক পরিবর্তন তবুও ভুল। এই কনসেপ্টটি পরিষ্কার করো।",
    insDangerFast: "ভুল কিন্তু দ্রুত — ভুল করার আগে কোনো দ্বিধা নেই। আত্মবিশ্বাসী ভুল সবচেয়ে বিপজ্জনক প্যাটার্ন।",
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
