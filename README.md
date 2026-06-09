# MEDHA — Behavioral Intelligence for Medical Admission

**Merit · Excellence · Dedication · Hustle · Achievement**

Bangladesh's first behavioral exam analytics platform for MBBS/BDS admission students. MEDHA tracks *how* students think during exams — timing, hesitation, answer switches, confidence — and classifies every answer into one of 4 behavioral states using a fine-tuned BanglaBERT model.

## The 4 Behavioral States

| State | Speed | Result | What it means |
|---|---|---|---|
| **MASTERY** | Fast | Correct | Concept fully internalized. No action needed. |
| **PRIORITY FOCUS** | Fast | Wrong | Most dangerous — confidently wrong. Fix immediately. |
| **TRUST GAP** | Slow | Correct | Knows it but doubts themselves. Build speed. |
| **GROWTH AREA** | Slow | Wrong | Genuine knowledge gap. Study this topic. |

## Architecture

```
Frontend (React SPA)
    ↓ axios
Backend (FastAPI + SQLAlchemy)
    ↓
Behavioral Classifier (Fine-tuned BanglaBERT via HuggingFace Inference API)
    ↓
DNA Report → AI Study Notes → Readiness Score
```

## Project Structure

```
app/
├── backend/           # FastAPI backend
│   ├── main.py        # App entry point
│   ├── config.py      # Environment config
│   ├── database.py    # SQLAlchemy setup
│   ├── models.py      # ORM models
│   ├── schemas.py     # Pydantic schemas
│   ├── routers/       # API routes (sessions, students, questions, notes, profile)
│   ├── services/      # Business logic (classifier, scoring, notes, profile, wellbeing)
│   └── data/          # Question bank + seed scripts
├── frontend/          # React SPA (behavioral exam UI)
│   └── src/
└── ml/                # Machine learning pipelines
    ├── classifier/    # BanglaBERT behavioral classifier
    └── explainer/     # Qwen2.5-3B explanation generator (V2)
```

## Setup

### Backend
```bash
cd app/backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # Fill in your HuggingFace token
python data/load_questions.py
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd app/frontend
npm install
npm start
```

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic
- **Frontend:** React, Axios, Lucide Icons
- **AI/ML:** BanglaBERT (csebuetnlp/banglabert), QLoRA fine-tuning, HuggingFace Inference API
- **Database:** SQLite (dev), PostgreSQL (prod)
- **Deployment:** Railway (backend), Vercel (frontend), HuggingFace (models)

## Training the Classifier

See [`app/ml/classifier/README.md`](app/ml/classifier/README.md) for complete training guide.

## License

Proprietary — MEDHA Team
