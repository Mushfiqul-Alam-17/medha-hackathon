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
#  Persistent storage (JSON fallback for demo)
# ──────────────────────────────────────────────────────────────
DB_FILE = "attempts.json"

def load_db() -> List[Dict[str, Any]]:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load DB: {e}")
    return []

def save_db(db: List[Dict[str, Any]]):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save DB: {e}")

ATTEMPTS_DB: List[Dict[str, Any]] = load_db()

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
    },
    {
        "id": 9,
        "chapter": "স্নায়ুতন্ত্র",
        "text": "মানবদেহে স্নায়ুকোষের (neuron) দীর্ঘ প্রবর্ধনকে কী বলে?",
        "options": ["ডেনড্রাইট", "অ্যাক্সন", "সোমা", "সিন্যাপস"],
        "correctIndex": 1,
        "concept": "নিউরনের গঠন",
        "explanation": "অ্যাক্সন স্নায়ুকোষের দীর্ঘ প্রবর্ধন যা বৈদ্যুতিক সংকেত কোষদেহ (soma) থেকে দূরে পরবর্তী নিউরন বা পেশিকোষে বহন করে।",
        "memoryTrick": "অ্যাক্সন = Arrow (তীর) — সংকেতকে দূরে নিয়ে যায়।",
        "trap": "ডেনড্রাইট সংকেত গ্রহণ করে, প্রেরণ করে না — উল্টো কাজ।"
    },
    {
        "id": 10,
        "chapter": "কোষ বিভাজন",
        "text": "মিয়োসিস কোষ বিভাজনের ফলে কতটি অপত্য কোষ তৈরি হয়?",
        "options": ["২টি", "৩টি", "৪টি", "৮টি"],
        "correctIndex": 2,
        "concept": "মিয়োসিস ও হ্যাপ্লয়েড কোষ",
        "explanation": "মিয়োসিসে একটি ডিপ্লয়েড কোষ দুইবার বিভাজিত হয়ে ৪টি হ্যাপ্লয়েড কোষ তৈরি করে — গ্যামেট (শুক্রাণু/ডিম্বাণু) তৈরির জন্য।",
        "memoryTrick": "মিয়োসিস = 'মি' = 4 (চারটি কোষ)। মাইটোসিস = 2।",
        "trap": "মাইটোসিসে ২টি কোষ হয়; মিয়োসিসে ৪টি — দুটো গুলিয়ে ফেলার ফাঁদ।"
    },
    {
        "id": 11,
        "chapter": "বাস্তুবিদ্যা",
        "text": "বাস্তুসংস্থানে (ecosystem) শক্তি প্রবাহের প্রথম স্তর কোনটি?",
        "options": ["গৌণ খাদক", "প্রাথমিক খাদক", "উৎপাদক", "বিয়োজক"],
        "correctIndex": 2,
        "concept": "শক্তি প্রবাহ ও ট্রফিক স্তর",
        "explanation": "উৎপাদক (Producer) সালোকসংশ্লেষণের মাধ্যমে সৌরশক্তিকে রাসায়নিক শক্তিতে রূপান্তর করে — তারাই শক্তি প্রবাহের প্রথম স্তর।",
        "memoryTrick": "উৎপাদক = Producer = প্রথম (P = P)। প্রথমে তৈরি হয়, তারপর খাওয়া হয়।",
        "trap": "প্রাথমিক খাদক দ্বিতীয় স্তর — 'প্রাথমিক' শব্দ দেখে প্রথম মনে হতে পারে।"
    },
    {
        "id": 12,
        "chapter": "রেচন",
        "text": "মানবদেহে রক্ত পরিস্রাবণ (filtration) কোন অঙ্গে হয়?",
        "options": ["যকৃৎ", "বৃক্ক (কিডনি)", "ফুসফুস", "অগ্ন্যাশয়"],
        "correctIndex": 1,
        "concept": "বৃক্কের কার্যপ্রণালী",
        "explanation": "বৃক্কের নেফ্রনে গ্লোমেরুলাসের মাধ্যমে রক্ত পরিস্রাবিত হয় — বর্জ্য ও অতিরিক্ত পানি আলাদা হয়ে মূত্র তৈরি করে।",
        "memoryTrick": "কিডনি = ক্লিনার (K = Kidney = Kleen)। রক্ত ফিল্টার করে।",
        "trap": "যকৃৎ বিষাক্ত পদার্থ ভাঙে (detoxify), কিন্তু রক্ত ফিল্টার করে বৃক্ক — দুটো আলাদা কাজ।"
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
    {"chapter": "স্নায়ুতন্ত্র", "frequency": 13},
    {"chapter": "বাস্তুবিদ্যা", "frequency": 7},
    {"chapter": "রেচন", "frequency": 10},
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
    attemptId: Optional[str] = None


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


import random

_SLOW_PREFIXES = [
    "sathi ujtor diyecho kintu onek somoy niyecho. Medical admission e proti proshne gorh 36 second - ei speed e porikkhay tumi shesh korte parbena.",
    "Thik kintu dhir. Amol porikkhay 100 ta proshno 60 minute e - orthath dwidha korar sujog nei. Speed barao.",
    "Tumi jano, kintu somoy niyontron durbhol. Shesher diker proshno skip korte hobe ja marks komabe.",
]

_DANGER_PREFIXES = [
    "Tumi druto uttor diyecho ebong atmobishwashi chile - kintu bhul korecho. Eta sobar cheye bipojjonok pattern karon tumi jano-o na je tumi bhul jano.",
    "Druto uttor + bhul = negative marking. Medical porikkhay proti bhul uttore 0.25 kata jay. Atmobishwashi bhul theke sobcheye beshi marks jay.",
    "Over-confidence sobcheye boro shotru. Tumi bhebecho jano, kintu aslei bhul tottho mukhostho korecho.",
]


def fallback_notes(dna_report: Dict[str, Any]) -> Dict[str, Any]:
    notes = {"slow": [], "confused": [], "danger": []}

    for it in dna_report.get("slow", []):
        prefix = random.choice(_SLOW_PREFIXES)
        notes["slow"].append({
            "topic": it.get("concept") or it.get("chapter") or "Topic",
            "explanation": f"{it.get('explanation', '')} {prefix}",
            "memoryTrick": it.get("memoryTrick", "Practice with a timer - do 10 questions in 200 seconds daily."),
            "trapQuestion": it.get("trap", "Similar options thakle sobcheye specific uttorta bechhe nao."),
        })

    _confused_descs = [
        "Bhul bikolpo - eta concept er sathe related holeo, porikkhay confused korar jonno deya hoyeche.",
        "Bhul bikolpo - namer mil thakleo function alada. Ei fandey poro na.",
        "Bhul bikolpo - eki category-r kintu kaj sompurno alada. Parthokko ta mone rakho.",
    ]

    for it in dna_report.get("confused", []):
        correct_text = it.get("correctAnswerText", "")
        table = [{"concept": correct_text, "description": f"Sothik uttor: {it.get('explanation', '')}"}]
        descs = list(_confused_descs)
        random.shuffle(descs)
        for idx, opt in enumerate(it.get("options", [])):
            if idx != it.get("correctAnswerIndex"):
                table.append({"concept": opt, "description": descs[idx % len(descs)]})
        notes["confused"].append({
            "topic": it.get("concept") or it.get("chapter") or "Topic",
            "comparisonTable": table,
            "memoryTrick": it.get("memoryTrick", "Concept gulo-r parthokko nije haate likhe barbar practice koro."),
            "trapQuestion": it.get("trap", "Porikkhok pray-i kachakachi shobdo diye confused korar cheshta kore. Shotorko thako."),
        })

    for it in dna_report.get("danger", []):
        prefix = random.choice(_DANGER_PREFIXES)
        notes["danger"].append({
            "topic": it.get("concept") or it.get("chapter") or "Topic",
            "explanation": prefix,
            "whyCorrect": f"Sothik uttor holo '{it.get('correctAnswerText','')}' - {it.get('explanation', '')}",
            "whyTricked": f"{it.get('trap', 'Sadhranoto ekta concept er sathe arekta guliye felar karone emon hoy.')} NCTB textbook theke abar poro - shudhu mukhostho noy, keno sothik seta bojho.",
            "trapQuestion": it.get("trap", "Similar option thakle protita option er mul parthokko chinta koro - druto uttor dio na."),
        })

    return notes



# ──────────────────────────────────────────────────────────────
#  Routes
# ──────────────────────────────────────────────────────────────
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_KEY = os.getenv("GROQ_API_KEY", "")

import httpx

NOTES_SYSTEM_PROMPT = """You are MEDHA, a Bangladeshi medical admission exam tutor AI.
You receive a student's behavioral DNA report — questions classified as "slow", "confused", or "danger" based on their real-time exam behavior (timing, answer switching, confidence).

Generate personalized study notes in this EXACT JSON format:
{
  "slow": [{"topic":"...","explanation":"...","memoryTrick":"...","trapQuestion":"..."}],
  "confused": [{"topic":"...","comparisonTable":[{"concept":"...","description":"..."}],"memoryTrick":"...","trapQuestion":"..."}],
  "danger": [{"topic":"...","explanation":"...","whyCorrect":"...","whyTricked":"...","trapQuestion":"..."}]
}

Rules:
- Write in Bangla (Bengali script) for explanations, memory tricks, and trap questions
- For "slow" items: explain the concept clearly and give a speed-boosting memory trick
- For "confused" items: create a comparison table showing the correct answer vs what they confused it with
- For "danger" items: explain WHY the student's wrong answer felt correct and WHY the actual answer is right
- Memory tricks should be catchy, exam-focused, and memorable
- Trap questions should be realistic MCQ traps an admission student might face
- Return ONLY valid JSON, no markdown, no backticks"""


def build_llm_prompt(dna_report: Dict[str, Any]) -> str:
    parts = []
    for group in ["slow", "confused", "danger"]:
        items = dna_report.get(group, [])
        if not items:
            continue
        parts.append(f"\n## {group.upper()} questions ({len(items)}):")
        for it in items:
            parts.append(f"- Question: {it.get('questionText', '')}")
            parts.append(f"  Correct: {it.get('correctAnswerText', '')}")
            chosen = it.get('finalAnswerText', 'skipped')
            parts.append(f"  Student chose: {chosen}")
            parts.append(f"  Time: {it.get('timeTaken', 0)}s, Switches: {it.get('switchCount', 0)}")
            parts.append(f"  Chapter: {it.get('chapter', '')}")
            parts.append(f"  Concept: {it.get('concept', '')}")
    return "\n".join(parts) if parts else "No weak areas found."


async def call_gemini(prompt: str) -> Optional[Dict]:
    if not GEMINI_KEY:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{"parts": [{"text": NOTES_SYSTEM_PROMPT + "\n\nStudent DNA Report:\n" + prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096, "responseMimeType": "application/json"}
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                logger.warning(f"Gemini returned {resp.status_code}: {resp.text[:200]}")
                return None
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
    except Exception as e:
        logger.warning(f"Gemini failed: {e}")
        return None


async def call_groq(prompt: str) -> Optional[Dict]:
    if not GROQ_KEY:
        return None
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": NOTES_SYSTEM_PROMPT},
            {"role": "user", "content": f"Student DNA Report:\n{prompt}"}
        ],
        "temperature": 0.7,
        "max_tokens": 4096,
        "response_format": {"type": "json_object"}
    }
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                logger.warning(f"Groq returned {resp.status_code}: {resp.text[:200]}")
                return None
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            return json.loads(text)
    except Exception as e:
        logger.warning(f"Groq failed: {e}")
        return None


@app.get("/")
async def health_check():
    return {"message": "MEDHA API is alive and running!"}

@api_router.get("/")
async def root():
    return {"message": "MEDHA API live"}


@api_router.get("/questions")
async def get_questions():
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
    save_db(ATTEMPTS_DB)
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


OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")

async def call_openrouter(prompt: str) -> Optional[Dict]:
    if not OPENROUTER_KEY:
        return None
    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {
        "model": "google/gemma-4-31b-it:free", # Stable free endpoint for Google Gemma
        "messages": [
            {"role": "system", "content": NOTES_SYSTEM_PROMPT},
            {"role": "user", "content": f"Student DNA Report:\n{prompt}"}
        ],
        "response_format": {"type": "json_object"}
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}", 
        "Content-Type": "application/json",
        "HTTP-Referer": "https://medha.vercel.app", 
        "X-Title": "MEDHA"
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                logger.warning(f"OpenRouter returned {resp.status_code}: {resp.text[:200]}")
                return None
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            return json.loads(text)
    except Exception as e:
        logger.warning(f"OpenRouter failed: {e}")
        return None

@api_router.post("/notes")
async def generate_notes(req: NotesRequest):
    target_attempt = None
    if req.attemptId:
        for r in ATTEMPTS_DB:
            if r["id"] == req.attemptId:
                target_attempt = r
                if "notes" in r and "notesSource" in r:
                    return {"notes": r["notes"], "source": r["notesSource"]}
                break

    prompt = build_llm_prompt(req.dnaReport)

    result_notes = None
    source = None

    # Try OpenRouter first (reliable free tier)
    notes = await call_openrouter(prompt)
    if notes:
        logger.info("✅ Notes generated via OpenRouter")
        result_notes = notes
        source = "ai"

    # Try Gemini 
    if not result_notes:
        notes = await call_gemini(prompt)
        if notes:
            logger.info("✅ Notes generated via Gemini")
            result_notes = notes
            source = "ai"

    # Try Groq
    if not result_notes:
        notes = await call_groq(prompt)
        if notes:
            logger.info("✅ Notes generated via Groq")
            result_notes = notes
            source = "ai"

    # Final fallback: deterministic
    if not result_notes:
        logger.info("⚠️ Using deterministic fallback notes")
        result_notes = fallback_notes(req.dnaReport)
        source = "fallback"

    if target_attempt is not None:
        target_attempt["notes"] = result_notes
        target_attempt["notesSource"] = source
        save_db(ATTEMPTS_DB)

    return {"notes": result_notes, "source": source}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

