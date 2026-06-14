# Orange Corners Cohort 8 Application Draft

---

### 1. Describe the problem you are solving
**Limit**: Max 1500 characters
**Draft (1,018 characters)**:
Medical admission preparation in Bangladesh is highly competitive, with over 140,000 candidates competing for only ~5,000 public seats (a <4% acceptance rate). In this high-stakes race, students spend massive amounts of money and time solving practice questions. However, traditional test-prep platforms only provide binary feedback (correct/incorrect). They completely miss the cognitive and behavioral patterns behind a student's answer. Students fail to identify *why* they make mistakes: whether it is a core knowledge gap, a confidence deficit (hesitating on correct answers, leading to lost time), or a deeply ingrained misconception (answering wrong choices quickly with high confidence, leading to severe negative marking). Additionally, typical AI study assistants hallucinate facts or page numbers, which is fatal for medical prep where absolute textbook accuracy is mandatory.

---

### 2. How are you solving the problem?
**Limit**: Max 1500 characters
**Draft (1,093 characters)**:
MEDHA solves this by capturing and analyzing student behavioral telemetry (hesitation time, confidence taps, and option switches) to diagnose *why* mistakes happen. 
Our platform automatically profiles each question response into one of four cognitive categories:
1. **Mastery**: Quick, correct, and confident.
2. **Trust Gap**: Correct but slow/hesitant—we build speed and conviction.
3. **Priority Focus**: Fast and incorrect—indicates a dangerous false belief that leads to negative marking.
4. **Growth Area**: Slow and incorrect—indicates a genuine knowledge gap.

Based on this diagnosis, MEDHA generates personalized study notes containing tailored explanations, memory shortcuts (mnemonics), and a direct page-jumping NCTB PDF viewer. Instead of wasting hours searching through 300-page textbooks, students are instantly transported to the exact page and paragraph they need to review. To ensure 100% accuracy, the system uses a tiered Retrieval-Augmented Generation (RAG) architecture that anchors AI-generated explanations to verified textbook database records, completely eliminating hallucination.

---

### 3. Describe your product or service
**Limit**: Max 1000 characters
**Draft (910 characters)**:
**What it does**: MEDHA is an AI-powered, behavior-adaptive test-prep web application for competitive college admission exams (starting with Bangladesh medical admissions). 
**How it works**:
1. **Telemetry Capture**: While taking mock exams, the app tracks student response telemetry (time elapsed, option changes, confidence inputs).
2. **Cognitive Profiling**: Our classifier maps responses into four performance zones (Mastery, Trust Gap, Priority Focus, Growth Area).
3. **Personalized Study Notes**: The RAG orchestrator generates customized study guides with explainers, mnemonics, and specific textbook page references.
4. **Instant Review**: Integrated with a byte-range loaded PDF viewer that opens the exact textbook page reference instantly inside the browser.
5. **Readiness Dashboard**: Tracks a student's progress and subject-level readiness over time to guide target study.

---

### 4. Explain how your business is addressing the selected SDGs?
*(Note: Selected SDGs are SDG 4 - Quality Education and SDG 10 - Reduced Inequalities)*
**Limit**: Max 1000 characters
**Draft (988 characters)**:
MEDHA directly addresses SDG 4 (Quality Education) and SDG 10 (Reduced Inequalities):
* **SDG 4 (Quality Education)**: By moving beyond static test prep, MEDHA provides hyper-personalized, active learning matching the pedagogy of a premium private tutor. It reinforces conceptual clarity, provides memory aids, and links directly to textbook sources. This raises educational quality, helping students master complex science topics.
* **SDG 10 (Reduced Inequalities)**: Quality coaching centers and private tutors in Bangladesh are concentrated in major cities and are prohibitively expensive for middle- and low-income families, creating massive regional and economic educational inequality. MEDHA democratizes access to elite, personalized cognitive coaching by offering it at a fraction of the cost, downloadable on any web browser, giving students from rural and underprivileged backgrounds an equal opportunity to compete in national exams.
