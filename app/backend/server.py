from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import json
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

app = FastAPI(title="MEDHA API")
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("medha")

# ──────────────────────────────────────────────────────────────
#  In-memory storage (no MongoDB required for demo)
# ──────────────────────────────────────────────────────────────
ATTEMPTS_DB: List[Dict[str, Any]] = []

# ──────────────────────────────────────────────────────────────
#  Biology question bank (HSC level — Bangladesh medical admission)
# ──────────────────────────────────────────────────────────────
QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "chapter": "কোষ ও এর গঠন",
        "text": "ইউক্যারিওটিক কোষে কোন অঙ্গাণু কোষীয় শ্বসনের মাধ্যমে ATP উৎপন্ন করে?",
        "options": ["নিউক্লিয়াস", "রাইবোজোম", "মাইটোকন্ড্রিয়া", "লাইসোজোম"],
        "correctIndex": 2,
        "concept": "মাইটোকন্ড্রিয়া ও ATP উৎপাদন",
        "explanation": "মাইটোকন্ড্রিয়া কোষের শক্তি-কারখানা; এটি গ্লুকোজ ও অক্সিজেন ব্যবহার করে কোষীয় শ্বসনের মাধ্যমে ATP তৈরি করে।",
        "memoryTrick": "মাইটো = শক্তির কারখানা (powerhouse)। ATP মানেই মাইটোকন্ড্রিয়া।",
        "trap": "ক্লোরোপ্লাস্ট আলোক-শক্তি ধরে, কিন্তু ATP-এর প্রধান উৎস মাইটোকন্ড্রিয়া — দুটো গুলিয়ে ফেলো না।"
    },
    {
        "id": 2,
        "chapter": "সালোকসংশ্লেষণ",
        "text": "উদ্ভিদ সূর্যালোককে রাসায়নিক শক্তিতে রূপান্তরিত করার প্রক্রিয়াকে কী বলে?",
        "options": ["কোষীয় শ্বসন", "প্রস্বেদন", "সালোকসংশ্লেষণ", "গাঁজন"],
        "correctIndex": 2,
        "concept": "সালোকসংশ্লেষণ বনাম অনুরূপ প্রক্রিয়া",
        "explanation": "সালোকসংশ্লেষণে উদ্ভিদ CO₂ ও জল থেকে সূর্যালোকের সাহায্যে গ্লুকোজ ও অক্সিজেন তৈরি করে।",
        "memoryTrick": "ফটো = আলো, সিন্থেসিস = তৈরি — আলো দিয়ে খাদ্য তৈরি।",
        "trap": "কোষীয় শ্বসন উল্টো প্রক্রিয়া — এটি খাদ্য ভেঙে শক্তি মুক্ত করে।"
    },
    {
        "id": 3,
        "chapter": "কোষ বিভাজন",
        "text": "কোষ চক্রের কোন দশায় DNA-এর প্রতিলিপি (replication) সম্পন্ন হয়?",
        "options": ["G₁ দশা", "G₂ দশা", "S দশা", "M দশা"],
        "correctIndex": 2,
        "concept": "S দশা ও DNA প্রতিলিপি",
        "explanation": "কোষ চক্র G₁ → S → G₂ → M ক্রমে চলে। DNA কেবল S (Synthesis) দশায় কপি হয়।",
        "memoryTrick": "S = Synthesis = DNA সংশ্লেষণ। শুধু S দশাতেই DNA দ্বিগুণ হয়।",
        "trap": "G₂ দেখে মনে হয় 'বিভাজনের প্রস্তুতি', কিন্তু তখন DNA কপি আগেই শেষ।"
    },
    {
        "id": 4,
        "chapter": "নিউক্লিক অ্যাসিড",
        "text": "নিউক্লিয়াস থেকে রাইবোজোমে জিনগত তথ্য বহন করে কোন অণু?",
        "options": ["tRNA", "mRNA", "rRNA", "snRNA"],
        "correctIndex": 1,
        "concept": "RNA-এর প্রকারভেদ ও কাজ",
        "explanation": "mRNA (messenger RNA) DNA থেকে কোডন কপি করে রাইবোজোমে বহন করে, যেখানে প্রোটিন তৈরি হয়।",
        "memoryTrick": "m = messenger = বার্তাবাহক। তথ্য বহন করলেই mRNA।",
        "trap": "tRNA অ্যামিনো অ্যাসিড আনে, rRNA রাইবোজোম গঠন করে — তথ্য বহন করে না।"
    },
    {
        "id": 5,
        "chapter": "এনজাইম",
        "text": "এনজাইম কীভাবে রাসায়নিক বিক্রিয়ার হার বৃদ্ধি করে?",
        "options": ["সক্রিয়ন শক্তি কমিয়ে", "তাপমাত্রা বাড়িয়ে", "বিক্রিয়ক ধ্বংস করে", "pH বাড়িয়ে"],
        "correctIndex": 0,
        "concept": "এনজাইম ও সক্রিয়ন শক্তি",
        "explanation": "এনজাইম জৈব অনুঘটক; এটি বিক্রিয়ার সক্রিয়ন শক্তি (activation energy) কমিয়ে বিক্রিয়ার হার বাড়ায়, নিজে অপরিবর্তিত থাকে।",
        "memoryTrick": "এনজাইম = শর্টকাট পথ — কম শক্তিতেই বিক্রিয়া হয়।",
        "trap": "এনজাইম তাপমাত্রা বা pH পরিবর্তন করে না; বরং নির্দিষ্ট তাপ-pH-এ সর্বোচ্চ কাজ করে।"
    },
    {
        "id": 6,
        "chapter": "রক্ত ও সংবহন",
        "text": "রক্তে অক্সিজেন পরিবহনের জন্য দায়ী প্রোটিন কোনটি?",
        "options": ["অ্যালবুমিন", "হিমোগ্লোবিন", "ফাইব্রিনোজেন", "গ্লোবিউলিন"],
        "correctIndex": 1,
        "concept": "হিমোগ্লোবিন ও অক্সিজেন পরিবহন",
        "explanation": "হিমোগ্লোবিন লোহিত রক্তকণিকার লৌহযুক্ত প্রোটিন; এটি ফুসফুস থেকে অক্সিজেন গ্রহণ করে কোষে পৌঁছে দেয়।",
        "memoryTrick": "হিমো = লোহা (heme) → লোহা অক্সিজেন ধরে।",
        "trap": "ফাইব্রিনোজেন রক্ত জমাট বাঁধায়, অক্সিজেন বহন করে না।"
    },
    {
        "id": 7,
        "chapter": "শ্বসন",
        "text": "অক্সিজেনের অনুপস্থিতিতে মানব পেশিকোষে গ্লুকোজ ভেঙে কী উৎপন্ন হয়?",
        "options": ["ইথানল", "ল্যাকটিক অ্যাসিড", "কার্বন ডাই-অক্সাইড", "অ্যাসিটিক অ্যাসিড"],
        "correctIndex": 1,
        "concept": "অবাত শ্বসন (Anaerobic respiration)",
        "explanation": "অক্সিজেন ছাড়া মানব পেশিকোষে গ্লুকোজ অবাত শ্বসনে ল্যাকটিক অ্যাসিডে পরিণত হয়, যা পেশিতে ক্লান্তি সৃষ্টি করে।",
        "memoryTrick": "মানুষ → ল্যাকটিক অ্যাসিড; ইস্ট → ইথানল।",
        "trap": "ইথানল উৎপন্ন হয় ইস্ট/উদ্ভিদে, মানব পেশিতে নয়।"
    },
    {
        "id": 8,
        "chapter": "বংশগতি",
        "text": "মেন্ডেলের একসংকর জননে F₂ জনুতে ফেনোটাইপিক অনুপাত কত?",
        "options": ["1 : 1", "9 : 3 : 3 : 1", "3 : 1", "1 : 2 : 1"],
        "correctIndex": 2,
        "concept": "মেন্ডেলের একসংকর জনন",
        "explanation": "একসংকর জননে (একটি বৈশিষ্ট্য) F₂ জনুতে প্রকট ও প্রচ্ছন্নের ফেনোটাইপিক অনুপাত হয় 3 : 1।",
        "memoryTrick": "একসংকর = 3:1 (ফেনোটাইপ), 1:2:1 (জিনোটাইপ)।",
        "trap": "9:3:3:1 হলো দ্বিসংকর জননের অনুপাত — একসংকরের সাথে মিলিয়ে ফেলো না।"
    }
]

# Chapter frequency in admission exams (static reference data)
CHAPTER_FREQUENCY: List[Dict[str, Any]] = [
    {"chapter": "কোষ ও এর গঠন", "frequency": 18},
    {"chapter": "কোষ বিভাজন", "frequency": 15},
    {"chapter": "নিউক্লিক অ্যাসিড", "frequency": 14},
    {"chapter": "সালোকসংশ্লেষণ", "frequency": 12},
    {"chapter": "বংশগতি", "frequency": 11},
    {"chapter": "রক্ত ও সংবহন", "frequency": 10},
    {"chapter": "এনজাইম", "frequency": 9},
    {"chapter": "শ্বসন", "frequency": 8},
]

QUESTION_BY_ID = {q["id"]: q for q in QUESTIONS}


# ──────────────────────────────────────────────────────────────
#  Models
# ──────────────────────────────────────────────────────────────
class AttemptItem(BaseModel):
    questionId: int
    finalAnswerIndex: Optional[int] = None
    clickSequence: List[str] = []
    timeTaken: float = 0
    confidence: Optional[str] = None  # sure | unsure | guessing


class AttemptCreate(BaseModel):
    mood: Optional[str] = None
    items: List[AttemptItem]


class NotesRequest(BaseModel):
    dnaReport: Dict[str, Any]


# ──────────────────────────────────────────────────────────────
#  Classification (mirrors the frontend classifier)
# ──────────────────────────────────────────────────────────────
def classify_item(it: AttemptItem) -> Dict[str, Any]:
    q = QUESTION_BY_ID[it.questionId]
    correct_index = q["correctIndex"]
    is_correct = it.finalAnswerIndex == correct_index
    fast = it.timeTaken <= 6
    switched = len(it.clickSequence) >= 2

    if switched:
        group = "confused"
    elif fast and not is_correct:
        group = "danger"
    elif fast and is_correct:
        group = "master"
    else:
        group = "slow"

    return {
        "questionId": q["id"],
        "chapter": q["chapter"],
        "questionText": q["text"],
        "options": q["options"],
        "correctAnswerIndex": correct_index,
        "correctAnswerText": q["options"][correct_index],
        "finalAnswerIndex": it.finalAnswerIndex,
        "finalAnswerText": q["options"][it.finalAnswerIndex] if it.finalAnswerIndex is not None else None,
        "timeTaken": round(it.timeTaken, 1),
        "clickSequence": it.clickSequence,
        "switchCount": max(0, len(it.clickSequence) - 1),
        "confidence": it.confidence,
        "isCorrect": is_correct,
        "group": group,
        "concept": q["concept"],
        "explanation": q["explanation"],
        "memoryTrick": q["memoryTrick"],
        "trap": q["trap"],
    }


def build_groups(items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    groups = {"slow": [], "confused": [], "master": [], "danger": []}
    for c in items:
        groups[c["group"]].append(c)
    return groups


def compute_readiness(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(items) or 1
    correct = sum(1 for c in items if c["isCorrect"])
    master = sum(1 for c in items if c["group"] == "master")
    danger = sum(1 for c in items if c["group"] == "danger")
    confused = sum(1 for c in items if c["group"] == "confused")
    slow = sum(1 for c in items if c["group"] == "slow")
    avg_time = round(sum(c["timeTaken"] for c in items) / total, 1)

    # Readiness: accuracy weighted, penalise danger & confusion, reward mastery
    score = (correct / total) * 70 + (master / total) * 30
    score -= (danger / total) * 20 + (confused / total) * 8
    score = max(0, min(100, round(score)))

    return {
        "score": score,
        "correct": correct,
        "total": total,
        "master": master,
        "danger": danger,
        "confused": confused,
        "slow": slow,
        "avgTime": avg_time,
    }


# ──────────────────────────────────────────────────────────────
#  Deterministic fallback notes (always works, zero tokens)
# ──────────────────────────────────────────────────────────────
def fallback_notes(dna_report: Dict[str, Any]) -> Dict[str, Any]:
    notes = {"slow": [], "confused": [], "danger": []}

    for it in dna_report.get("slow", []):
        notes["slow"].append({
            "topic": it.get("concept") or it.get("chapter") or "বিষয়",
            "explanation": it.get("explanation", ""),
            "memoryTrick": it.get("memoryTrick", ""),
            "trapQuestion": it.get("trap", ""),
        })

    for it in dna_report.get("confused", []):
        table = [{"concept": it.get("correctAnswerText", ""), "description": it.get("explanation", "")}]
        for idx, opt in enumerate(it.get("options", [])):
            if idx != it.get("correctAnswerIndex"):
                table.append({"concept": opt, "description": "এই অপশনটি ভিন্ন একটি ধারণা — সঠিকটির সাথে গুলিয়ে ফেলো না।"})
        notes["confused"].append({
            "topic": it.get("concept") or it.get("chapter") or "বিষয়",
            "comparisonTable": table,
            "memoryTrick": it.get("memoryTrick", ""),
            "trapQuestion": it.get("trap", ""),
        })

    for it in dna_report.get("danger", []):
        notes["danger"].append({
            "topic": it.get("concept") or it.get("chapter") or "বিষয়",
            "explanation": it.get("explanation", ""),
            "whyCorrect": f"সঠিক উত্তর '{it.get('correctAnswerText','')}' — {it.get('explanation','')}",
            "whyTricked": it.get("trap", ""),
            "trapQuestion": it.get("trap", ""),
        })

    return notes


# ──────────────────────────────────────────────────────────────
#  Routes
# ──────────────────────────────────────────────────────────────
@app.get("/")
async def health_check():
    return {"message": "MEDHA API is alive and running!"}

@api_router.get("/")
async def root():
    return {"message": "MEDHA API live"}


@api_router.get("/questions")
async def get_questions():
    # Return questions without revealing the correct answer index
    public = [{
        "id": q["id"],
        "chapter": q["chapter"],
        "text": q["text"],
        "options": q["options"],
    } for q in QUESTIONS]
    return {"questions": public, "total": len(public)}


@api_router.get("/chapters")
async def get_chapters():
    return {"chapters": CHAPTER_FREQUENCY}


@api_router.post("/attempts")
async def create_attempt(payload: AttemptCreate):
    classified = [classify_item(it) for it in payload.items]
    groups = build_groups(classified)
    readiness = compute_readiness(classified)

    doc = {
        "id": str(uuid.uuid4()),
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "mood": payload.mood,
        "items": classified,
        "groups": groups,
        "readiness": readiness,
    }
    ATTEMPTS_DB.append(doc)
    return doc


@api_router.get("/attempts")
async def list_attempts():
    rows = sorted(ATTEMPTS_DB, key=lambda r: r["createdAt"], reverse=True)[:50]
    summary = [{
        "id": r["id"],
        "createdAt": r["createdAt"],
        "mood": r.get("mood"),
        "readiness": r.get("readiness", {}),
    } for r in rows]
    return {"attempts": summary}


@api_router.get("/attempts/{attempt_id}")
async def get_attempt(attempt_id: str):
    for r in ATTEMPTS_DB:
        if r["id"] == attempt_id:
            return r
    raise HTTPException(status_code=404, detail="Attempt not found")


@api_router.post("/notes")
async def generate_notes(req: NotesRequest):
    return {"notes": fallback_notes(req.dnaReport), "source": "fallback"}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
