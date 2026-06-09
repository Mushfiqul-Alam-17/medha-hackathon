"""
MEDHA Backend — Pydantic Schemas
Request/response validation models for all API routes.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ──────────────────────────────────────────────────────────────
#  Student Schemas
# ──────────────────────────────────────────────────────────────

class StudentRegister(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)


class StudentResponse(BaseModel):
    student_id: str
    username: str
    created_at: datetime
    total_sessions: int = 0

    class Config:
        from_attributes = True


class StudentLogin(BaseModel):
    username: str


class StudentLoginResponse(BaseModel):
    student_id: str
    username: str
    exists: bool
    total_sessions: int = 0


# ──────────────────────────────────────────────────────────────
#  Question Schemas
# ──────────────────────────────────────────────────────────────

class QuestionOut(BaseModel):
    """Question as served to the student — NO correct answer, NO explanation."""
    id: int
    chapter_name: str
    topic: Optional[str] = None
    difficulty: str = "medium"
    question_bn: str
    question_en: Optional[str] = None
    option_a_bn: str
    option_a_en: Optional[str] = None
    option_b_bn: str
    option_b_en: Optional[str] = None
    option_c_bn: str
    option_c_en: Optional[str] = None
    option_d_bn: str
    option_d_en: Optional[str] = None

    class Config:
        from_attributes = True


class ChapterInfo(BaseModel):
    chapter_code: str
    chapter_name: str
    frequency: int
    question_count: int


# ──────────────────────────────────────────────────────────────
#  Session Schemas
# ──────────────────────────────────────────────────────────────

class SessionStart(BaseModel):
    student_id: str
    mood: Optional[str] = None  # tired | low | okay | good | focused
    question_count: int = Field(default=15, ge=5, le=100)
    chapter: Optional[str] = None  # Filter by chapter, None = all


class SessionStartResponse(BaseModel):
    session_id: str
    questions: List[QuestionOut]
    total_questions: int


class QuestionEvent(BaseModel):
    """Single question behavioral event sent during or after exam."""
    session_id: str
    question_id: int
    click_path: List[str] = Field(default_factory=list)  # ["C", "A", "B"]
    final_answer: Optional[str] = None  # "A", "B", "C", "D"
    confidence_tap: Optional[str] = None  # sure | unsure | guessing
    time_taken: float = 0.0  # Seconds
    time_expired: bool = False
    skipped: bool = False


class QuestionEventResponse(BaseModel):
    ok: bool = True
    result_id: str


# ──────────────────────────────────────────────────────────────
#  Session Completion Schemas
# ──────────────────────────────────────────────────────────────

class SessionComplete(BaseModel):
    session_id: str
    tab_switches: int = 0
    items: List[QuestionEvent] = Field(default_factory=list)


class ClassifiedResult(BaseModel):
    """Single question result with classifier output + question details."""
    question_id: int
    chapter_name: str
    topic: Optional[str] = None
    question_bn: str
    question_en: Optional[str] = None
    options_bn: List[str]
    options_en: Optional[List[str]] = None
    correct_answer: str  # "A", "B", "C", "D"
    correct_answer_text: str
    final_answer: Optional[str] = None
    final_answer_text: Optional[str] = None
    click_path: List[str]
    confidence_tap: Optional[str] = None
    time_taken: float
    switch_count: int
    is_correct: bool
    skipped: bool
    time_expired: bool
    classifier_label: str
    classifier_confidence: Dict[str, float]
    # Question metadata for notes assembly
    explanation_bn: Optional[str] = None
    explanation_en: Optional[str] = None
    confusable_note_bn: Optional[str] = None
    confusable_note_en: Optional[str] = None
    memory_trick: Optional[str] = None
    trap_note: Optional[str] = None
    difficulty: str = "medium"
    
    # NCTB Textbook Highlights
    pdf_file: Optional[str] = None
    pdf_page: Optional[int] = None
    pdf_bbox: Optional[List[float]] = None


class ScoringResult(BaseModel):
    total: int
    correct: int
    wrong: int
    skipped: int
    raw_score: float
    negative_deduction: float
    final_score: float
    risky_attempts: int
    potential_saving: float
    skip_coach_score: float
    accuracy: float


class DnaGroups(BaseModel):
    MASTERY: List[ClassifiedResult] = []
    PRIORITY_FOCUS: List[ClassifiedResult] = []
    TRUST_GAP: List[ClassifiedResult] = []
    GROWTH_AREA: List[ClassifiedResult] = []


class SessionCompleteResponse(BaseModel):
    session_id: str
    classified_results: List[ClassifiedResult]
    scoring: ScoringResult
    dna_groups: DnaGroups
    readiness_score: int
    wellbeing: Optional[Dict[str, Any]] = None


# ──────────────────────────────────────────────────────────────
#  Notes Schemas
# ──────────────────────────────────────────────────────────────

class NotesGenerate(BaseModel):
    session_id: str


class NoteItem(BaseModel):
    topic: str
    question_text: str
    explanation: str
    frame: str  # Behavioral framing
    memory_trick: Optional[str] = None
    trap_note: Optional[str] = None
    correct_answer: Optional[str] = None
    wrong_answer: Optional[str] = None
    confusable_note: Optional[str] = None
    comparison_table: Optional[List[Dict[str, Any]]] = None
    pdf_file: Optional[str] = None
    pdf_page: Optional[int] = None



class NotesSection(BaseModel):
    header: str
    description: str
    items: List[NoteItem]


class NotesResponse(BaseModel):
    session_id: str
    sections: List[NotesSection]
    source: str = "assembly"  # "assembly" | "cached"


# ──────────────────────────────────────────────────────────────
#  Profile Schemas
# ──────────────────────────────────────────────────────────────

class ChapterProfile(BaseModel):
    chapter_code: str
    chapter_name: str
    mastery_count: int
    priority_count: int
    trust_count: int
    growth_count: int
    readiness_score: int
    trend: Optional[str] = None


class ProfileResponse(BaseModel):
    student_id: str
    username: str
    total_sessions: int
    chapters: List[ChapterProfile]
    overall_readiness: int
    mood_history: List[str]


class ReadinessResponse(BaseModel):
    student_id: str
    readiness_score: int
    trend: Optional[str] = None
    session_scores: List[int] = []  # Last 7 session readiness scores


class HistoryReadiness(BaseModel):
    score: int
    correct: int
    total: int

class SessionSummary(BaseModel):
    id: str
    createdAt: datetime
    mood: Optional[str] = None
    readiness: HistoryReadiness


class HistoryResponse(BaseModel):
    student_id: str
    sessions: List[SessionSummary]


# ──────────────────────────────────────────────────────────────
#  Health Check
# ──────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    classifier_available: bool = False
    question_count: int = 0
    student_count: int = 0
