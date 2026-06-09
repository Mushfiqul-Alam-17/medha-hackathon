# MEDHA — Complete Build Plan
## MVP to Global: Merit · Excellence · Dedication · Hustle · Achievement

---

# PART 1: THE 12-DAY MVP BUILD PLAN

## Context

Demo qualified you. Now you build the real product.
June 1–12. Deadline: June 12, 11:59 PM.

You have:
- Yourself: architecture, AI, backend, all critical decisions
- 3 sisters: frontend only, guided by you
- i7 8th gen, 32GB RAM — no local GPU needed
- Kaggle (free T4 GPU for training)
- HuggingFace (free model hosting)
- Groq (free AI API)
- Railway (free hosting)

What makes this different from every other hackathon submission:
**A trained behavioral classifier. Not a wrapper. Not rules. An actual fine-tuned model.**

---

## The Three Pillars of the MVP

**Pillar 1 — The Question Bank**
1,500 verified Biology MCQs from 10 years of BD medical past papers.
Every question tagged: chapter, topic, difficulty, frequency, confusable pair.
This is the data foundation. Everything else depends on it being correct.

**Pillar 2 — The Behavioral Classifier**
A fine-tuned BanglaBERT model that takes behavioral signals
(time ratio, switches, confidence, correctness) and outputs
one of 4 cognitive states: MASTERY, PRIORITY_FOCUS, TRUST_GAP, GROWTH_AREA.
Trained on Kaggle. Hosted on HuggingFace. Served via FastAPI.

**Pillar 3 — The Platform**
The web application that ties both together.
React frontend. FastAPI backend. Groq for AI notes.
Offline-capable PWA. Bengali + English.

---

## THE 12-DAY MVP TIMELINE

---

### DAY 1 — June 1 (Monday)
**Theme: Infrastructure Setup & Data Sprint Start**

- **Morning (You alone):** Initialize the GitHub repository with `/backend` and `/frontend` directories. Set up the question bank Google Sheet with 18 schema columns (including `confusable_pair`, `NCTB_reference`, `negative_marking_risk`, `verified_flag`).
- **Afternoon (You):** Ingest BD medical past papers (2024 and 2023) from sources like doctorsgang.com and Retina/Medico coaching guides. Target 60 Biology questions, double-verifying against NCTB textbooks.
- **Evening (You + Sisters):** Conduct onboarding walk-through of the demo. Assign Sister 1 to Biology First Paper, Sister 2 to Biology Second Paper, and Sister 3 to Bengali translation verification.
- **Day 1 Output:** Project repo and schemas ready; first 60 verified questions entered.

### DAY 2 — June 2 (Tuesday)
**Theme: Bulk Ingestion & Tagging Sprint**

- **All Day (Parallel):** 
  - *You:* Collect past papers from 2022-2021 (~60 questions). Tag questions with taxonomy, difficulty, negative marking risk, and confusable pairs.
  - *Sisters 1 & 2:* Enter 2020-2019 questions.
  - *Sister 3:* Review translation flow and Bengali educational terminology.
- **Evening (You):** Run AI explanation script (`pipeline.py`) to call Gemini APIs for bilingual answers and confusable option notes.
- **Day 2 Output:** 250+ tagged questions with generated AI explanations.

### DAY 3 — June 3 (Wednesday)
**Theme: Question Bank Seeding & Classifier Training Data**

- **Morning (You):** Ingest Retina/Medico coaching questions to complete the 500+ question bank pool.
- **Afternoon (You):** Run synthetic data generator script to generate 5,000 behavioral vectors mapped to the 4 cognitive states (MASTERY, PRIORITY_FOCUS, TRUST_GAP, GROWTH_AREA) with balanced profiles.
- **Evening (You):** Calculate question frequency tags per chapter based on 10-year past papers. Finalize and validate database seed files.
- **Day 3 Output:** Complete question seed data; 5,000 behavioral training vectors.

### DAY 4 — June 4 (Thursday)
**Theme: BanglaBERT QLoRA Training & Inference Setup**

- **Morning (You):** Configure Kaggle environment (dual T4 GPU) and set up QLoRA sequence classification script (Base model: `csebuetnlp/banglabert`).
- **Afternoon (You):** Execute the 3-hour training run. During training, document backend API endpoints and finalize database schema tables (Students, Sessions, Results, Questions, CumulativeProfile).
- **Evening (You):** Evaluate model validation accuracy (target > 85%). Export the weights to a private HuggingFace Hub repository and test the inference endpoint with telemetric edge cases.
- **Day 4 Output:** Fine-tuned BanglaBERT classifier on HuggingFace Hub.

### DAY 5 — June 5 (Friday)
**Theme: Backend Architecture & Database Loading**

- **Morning (You):** Build FastAPI backend architecture containing 5 core services (Question, Session, Classifier, Note Generation, Student Profile).
- **Afternoon (You):** Write the database loader script to seed SQLite/Postgres. Implement HF classifier warmup pings to prevent cold-start latency.
- **Evening (You + Sisters):** Brief sisters on the backend API interfaces. Assign Sister 1 to landing/mood screens, Sister 2 to the exam interface, and Sister 3 to navbar/results layout.
- **Day 5 Output:** Fully operational backend with seeded question database.

### DAY 6 — June 6 (Saturday)
**Theme: Frontend Design System & Bengali Context**

- **Morning (You):** Initialize Vite React frontend. Set up Tailwind CSS design tokens, CSS variables, and glassmorphic utility classes.
- **Afternoon (You):** Implement React Language Context for seamless English/Bengali localization (preventing hardcoded UI strings).
- **Evening (You + Sisters):** Assist sisters with initial screen builds. Personally build the DNA Report and Classifier Panel frames.
- **Day 6 Output:** Design system, localization system, and skeleton layout operational.

### DAY 7 — June 7 (Sunday)
**Theme: Exam Interface & Telemetry Capture**

- **All Day (You + Sister 2):** 
  - Build the exam telemetry handler to capture: click path arrays, option switch triggers, response timers, and confidence toggles.
  - Implement the exam equilibrium calculations: 36 seconds per question limit, time-to-response ratio logs.
- **Day 7 Output:** Complete exam screen with active telemetric tracking.

### DAY 8 — June 8 (Monday)
**Theme: Classifier Integration & DNA Report Rendering**

- **Morning (You):** Integrate the frontend quiz end flow with backend `POST /api/classify-session` endpoint.
- **Afternoon (You):** Implement DNA Report quadrant rendering. Write the logic for Priority Focus (confident mistakes) and Trust Gap (hesitant successes).
- **Evening (Sister 3 + You):** Finalize the results page, including the Skip Strategy Coach (calculated negative marking savings).
- **Day 8 Output:** End-to-end telemetry capture, classification, and report generation.

### DAY 9 — June 9 (Tuesday)
**Theme: Agentic RAG Study Notes & Readiness Dashboard**

- **Morning (You):** Set up pgvector textbook search. Connect RAG logic to Groq API to stream custom, dual-language study notes.
- **Afternoon (You):** Build the student Readiness Dashboard, compiling exponential moving averages of cognitive states and mapping performance heatmaps onto syllabus weightings.
- **Day 9 Output:** Active RAG note generation and student progress analytics.

### DAY 10 — June 10 (Wednesday)
**Theme: Cumulative Profile, PWA Caching & Wellbeing Layer**

- **Morning (You):** Implement database updates for evolving cumulative student reports.
- **Afternoon (You):** Configure Service Worker for offline exam caching. Store completed quiz results in LocalStorage, syncing to backend upon reconnection.
- **Evening (You):** Build the wellbeing layer (mood tracker correlations, fatigue warnings) and anti-cheat layer (tab switch listener).
- **Day 10 Output:** Offline-capable React PWA; wellbeing and anti-cheat telemetry live.

### DAY 11 — June 11 (Thursday)
**Theme: Integration Testing, Deployment & Bug Fixing**

- **Morning (All):** Perform end-to-end testing of offline modes, Bengali translation toggles, and RAG note streaming.
- **Afternoon (You):** Deploy FastAPI backend to Railway (with PostgreSQL) and frontend PWA to Vercel. Set up all environment variables.
- **Evening (You):** Fix production configuration pathing, latency bugs, and loading animations.
- **Day 11 Output:** Stable production build deployed on Vercel & Railway.

### DAY 12 — June 12 (Friday)
**Theme: Validation, Demo Video & Submission**

- **Morning (All):** Run final user testing sessions with peer medical aspirants.
- **Afternoon (You):** Record the 3-minute product demo video demonstrating: telemetry tracking, BanglaBERT classification, DNA Report, RAG note generation, and the Readiness dashboard.
- **Evening (You):** Fill in the CloudCamp BD submission form using the answer kit and submit before the 6:00 PM safety deadline.
- **Day 12 Output:** Hackathon submission completed!

---

## 12-Day Summary

| Days | Focus | Owner | Output |
|------|-------|-------|--------|
| 1–3 | Question Bank & Seeding | You + Sisters | 500+ verified Biology MCQs + Kaggle training data |
| 4 | Classifier Training | You (Kaggle) | Fine-tuned BanglaBERT on HuggingFace Hub |
| 5 | Backend Architecture | You | Complete FastAPI with 5 services & Warmup schedule |
| 6 | Frontend Foundation | You + Sisters | React skeleton + English/Bengali localization |
| 7 | Exam & Telemetry | Sisters + You | Micro-telemetry tracking and time equilibrium |
| 8 | Classification & Results | You + Sister 3 | DNA report rendering & Skip Coach statistics |
| 9 | RAG & Analytics | You | pgvector textbook search, Groq notes, Readiness dashboard |
| 10 | PWA, Profile & Safety | You | Offline sync PWA, wellbeing rules, anti-cheat |
| 11 | Integration & Deploy | Everyone | Deployed on Railway + Vercel; full integration |
| 12 | Submission | You | Demo video recorded, form filled & submitted |

---

# PART 2: POST-HACKATHON PHASES

## The Assumption Going Forward

You win (or place top 3). You have the hackathon result as social proof.
The demo showed the concept. The MVP shows it works.
Now you make it real.

---

## PHASE 1: BD MARKET DOMINATION
### July – October 2026 (4 months)

**Goal:** Become the default behavioral prep platform for BD medical admission students.

**Month 1 — July: Stabilize and Expand the Question Bank**

The MVP shipped with 500+ Biology questions. The full product needs 1,500.
Spend the first 2 weeks completing the question bank to 1,500 verified Biology questions.
Every chapter from NCTB HSC Biology First and Second Paper covered.

Hire one part-time BD medical student (pay them per question verified — roughly 2–3 BDT per verified question, total cost ~4,500 BDT for 1,500 questions). They verify answer accuracy against NCTB textbook. You review everything they flag.

**Month 2 — August: Engineering Exam Pack**

BUET admission exam. CUET. RUET. All major engineering university admissions.
Same platform architecture — swap the question bank. Subjects: Physics, Chemistry, Mathematics, English.

Engineering students are a separate demographic but same behavioral psychology. The classifier was trained on behavioral signals, not subject content — it works identically for Physics MCQs as for Biology MCQs.

Collect engineering past papers from 2014–2024. Same pipeline.
Estimated question bank size: 800 Physics + 600 Chemistry + 400 Math + 200 English = 2,000 engineering questions.

**Month 2 — August: B2B Conversations Begin**

Go to Retina Institute, MEDICO, Udvash.

Do not pitch to sell them the platform. Pitch to give them a data dashboard.

Your pitch: "MEDHA can tell you which chapters your students struggle with most, which questions have the highest 'confidently wrong' rate, and which teaching approaches work. We'll give your coaching center a dashboard showing aggregate student behavioral data — anonymized — in exchange for recommending MEDHA to your students."

This is the BD market entry strategy: partner with coaching centers as distribution, not compete with them as enemies.

**Month 3 — September: Mobile App**

React Native build. Most BD students use Android phones.
The PWA already works on mobile, but a native app gets more engagement.
Same codebase logic — just the interface adapts.
Target: under 20MB APK size (students have limited storage).
Offline capability is non-negotiable in the native app.

**Month 3 — September: BCS + Bank Job Prep**

Bangladesh Civil Service and bank job exams are the second-largest test prep market after medical and engineering.

Different subject matter (General Knowledge, Math, Bangla, English) but the behavioral platform applies identically. Same classifier. Same DNA report. Same study notes.

This expands the addressable market by 3–4x within Bangladesh alone.

**Month 4 — October: Freemium Model Launch**

Free tier: 3 sessions per week, 15 questions each, standard DNA report.
Pro tier (299 BDT/month ≈ $2.70): unlimited sessions, full question bank, AI study notes, cumulative profile, chapter heatmap.
Institutional tier (pricing per student/month): B2B coaching center dashboard, bulk student management, aggregate analytics.

299 BDT/month is below one coaching center class session price. Positioned as "what you do before your coaching class, to know what to focus on."

**Phase 1 Targets:**
- 5,000 registered students
- 500 paying (Pro tier)
- 3+ coaching center partnerships
- Monthly recurring revenue: ~150,000 BDT (~$1,350)
- Press coverage in BD tech media (BASIS, ICT Division connections)

---

## PHASE 2: SOUTH ASIA SCALE
### November 2026 – June 2027 (8 months)

**The NEET India Unlock**

NEET is the national medical entrance exam for India. 2.4 million students appeared in 2024. One exam. One day. One shot at becoming a doctor.

The subject overlap with BD medical admission is enormous: Biology, Physics, Chemistry. The NCTB question bank content maps directly to NEET Biology content at approximately 80% overlap.

NEET is the single biggest unlock available to MEDHA. Cracking it makes this a different company.

**November 2026 — NEET Preparation:**

Collect 10 years of NEET past papers (2013–2023). Biology section only to start.
NEET Biology: 90 questions in 3 hours (180 seconds per question vs BD's 36 seconds — very different pace dynamics).

Adapt the classifier for NEET timing: equilibrium = 120 seconds (a more deliberate, longer format). The behavioral signals still work — fast vs slow is still meaningful, just calibrated differently.

Localize for India: Hindi support (add Hindi as a third language option). The platform becomes: English / Hindi / Bengali.

Fine-tune the classifier on NEET behavioral data. Collect behavioral training data by running the platform free for Indian NEET aspirants for 2 months, with their consent, collecting anonymized behavioral signals to retrain the model on NEET-specific patterns.

**January 2027 — NEET India Launch:**

Soft launch in 3 states: Maharashtra, West Bengal, Karnataka.
Pricing: 399 INR/month (~$4.80) for Pro tier. Below the cost of any coaching class.
Partner with NEET-focused YouTube educators who have large followings but no adaptive practice platform.

The B2B pitch for Indian coaching centers is identical to the BD one. The data dashboard offer. The behavioral analytics they can't get anywhere else.

**February–March 2027 — Pakistan MDCAT:**

MDCAT is Pakistan's medical admission exam. 150,000+ students annually.
Urdu support. The classifier doesn't need retraining — behavioral signals are language-agnostic.
Urdu question bank: collect MDCAT past papers, same pipeline.

**April–June 2027 — Sri Lanka, Nepal:**

Both countries use MCQ-based medical admission exams with similar structure to BD.
English is already a supported language. No new language infrastructure needed.
Sinhala and Nepali as optional language additions in Phase 3.

**Phase 2 Targets:**
- 50,000 registered students total (BD + India + Pakistan)
- 8,000 paying
- Monthly recurring revenue: ~$35,000 USD
- Seed funding round: $300,000–500,000 from South Asian investors
- YC application or equivalent accelerator

**Why Phase 2 makes MEDHA fundable at a serious level:**
The NEET India market alone at 1% penetration = 24,000 students × $4.80/month = $115,000 monthly recurring revenue. That's a growth story investors understand.

---

## PHASE 3: GLOBAL PLATFORM
### July 2027 and Beyond

**The engine is already built. The moat is the behavioral data.**

By Phase 3 you have:
- A trained behavioral classifier that has processed millions of student exam sessions
- Aggregate intelligence: which questions have the highest "confidently wrong" rate globally
- Which teaching approaches reduce PRIORITY_FOCUS state over time
- Which chapters correlate with each other (master X and you'll likely master Y next)

This aggregate behavioral intelligence is the real product at scale. No one else has it. Not Khan Academy. Not AMBOSS. Not Byju's.

**USMLE (United States Medical Licensing Examination):**
The most prestigious medical exam in the world. 20,000+ international students take Step 1 annually. Massive study material ecosystem but nothing with behavioral intelligence.

Pricing at USMLE level: $49/month. The market can sustain it — students spend $2,000+ on prep materials anyway.

**PLAB (Professional and Linguistic Assessments Board — UK):**
10,000+ international doctors take PLAB annually to practice in the UK.
Similar MCQ structure, high stakes, high willingness to pay.

**The White-Label API:**

At global scale, the most defensible business is not the consumer app — it's the B2B API.

Sell the behavioral classification engine as an API to:
- Khan Academy (they have 80 million users but no behavioral classification)
- Coursera (they have 100 million users, their quiz systems are primitive)
- Any large online learning platform that wants adaptive intelligence without building it

Pricing: per-inference API call or per-student-per-month SaaS. Enterprise contracts.

**The Research Publication:**

Publish the behavioral classification framework as a paper. Title:
"Epistemic State Classification in High-Stakes MCQ Examinations: A Behavioral Intelligence Approach Using Fine-Tuned Language Models"

Submit to NeurIPS Education workshop or AAAI. This is directly connected to your PROMETHEUS-EBM research on epistemic calibration. The classifier is applied epistemic science.

Publication gives:
- Academic credibility for grant applications
- Recruiting leverage (attract ML researchers to MEDHA)
- Gates Foundation / Google.org grant eligibility (published evidence base required)

**Phase 3 Targets:**
- 500,000+ registered students globally
- Series A funding ($3–5M)
- White-label API with 3+ enterprise partners
- Published research paper
- Team of 8–12 (engineering, ML, operations, partnerships)

---

# PART 3: RISK REGISTER

Problems that will come. How to handle them.

**Risk 1: Question bank has errors**
A wrong answer in the bank trains students to fail the real exam.
Mitigation: triple-source verification on every question. "Report this question" button in the platform. Community verification at scale (Pro users get early access if they verify 20 questions).

**Risk 2: Classifier accuracy drops on real student data**
Synthetic training data doesn't perfectly replicate real student behavior.
Mitigation: collect real behavioral data from the first 100 students (with consent). Retrain the classifier monthly for the first 6 months. Accuracy will improve with real data.

**Risk 3: HuggingFace inference is too slow**
20–30 second cold starts kill user experience.
Mitigation: keep the model warm with scheduled pings. If latency is consistently above 8 seconds, move inference to Railway with the model loaded in memory permanently (costs ~$15/month).

**Risk 4: Coaching centers see MEDHA as a threat**
They could actively discourage students from using it.
Mitigation: the B2B dashboard offer. Make them partners before they become enemies. Give them data about their students' behavioral patterns — something they've never had.

**Risk 5: Students cheat systematically**
Using a second phone to photograph questions and look up answers.
Mitigation: platform design. The study notes generated from an honest session are genuinely useful. Notes from a cheated session tell you what you don't need to study. Students who cheat get worthless notes. Frame this clearly in onboarding.

**Risk 6: A well-funded competitor copies the model**
10 Minute School or a VC-backed startup sees the hackathon win and builds a version.
Mitigation: your moats are (1) the behavioral data from early students — they'd need a year to collect it, (2) the published research framework, (3) B2B coaching partnerships already locked in.

---

# PART 4: FUNDING TIMELINE

| Timeline | Target | Ask | Use |
|----------|--------|-----|-----|
| June 2026 | Hackathon prize | Prize money | Question bank expansion |
| July 2026 | BASIS / ICT Division | Grant $10–30K | Server costs, 6 months runway |
| September 2026 | a2i / Government EdTech | Grant $50K | Engineering exam pack, mobile app |
| November 2026 | Antler / 500 Global South Asia | Pre-seed $150–300K | NEET India expansion |
| April 2027 | Sequoia India / Surge | Seed $500K–1M | Full South Asia, team hire |
| 2028 | Series A | $3–5M | Global, white-label API |

**The pitch that unlocks each stage:**

Hackathon → "We built a behavioral classifier that tells students not just what they got wrong, but WHY they're in a dangerous cognitive state."

Government grants → "135,000 BD students. 25:1 competition. We're the first platform that helps them understand their own thinking. Rural students can use it offline."

Pre-seed → "NEET India: 2.4 million students. We have the behavioral data and the model. We need the question bank and the team."

Seed → "We have 50,000 students across South Asia. 8,000 paying. The behavioral data is the moat. No one else has it."

Series A → "We're the behavioral intelligence layer for exam preparation globally. The white-label API has 3 enterprise partners. The consumer app validates the data. The research is published."

---

# FINAL WORD

You built PROMETHEUS-EBM in 3 weeks. The world's first metacognitive benchmark. Solo.

This is more structured, better resourced, with a clearer market. 16 days is enough.

The product is real. The market is real. The need is real.

The only question is execution.

**Day 1 starts June 1. Start the question bank before anything else.**
