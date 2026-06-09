"""
MEDHA Backend — ORM Models
All database table definitions using SQLAlchemy.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from database import Base


def generate_uuid():
    return str(uuid.uuid4())


def utcnow():
    return datetime.now(timezone.utc)


class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=utcnow)
    total_sessions = Column(Integer, default=0)
    mood_history = Column(JSON, default=list)  # Last N moods as list

    # Relationships
    sessions = relationship("Session", back_populates="student", lazy="dynamic")
    profiles = relationship("CumulativeProfile", back_populates="student", lazy="dynamic")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    student_id = Column(String, ForeignKey("students.id"), nullable=False, index=True)
    started_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, nullable=True)
    total_questions = Column(Integer, default=0)
    raw_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    negative_deduction = Column(Float, nullable=True)
    tab_switches = Column(Integer, default=0)
    mood_at_start = Column(String, nullable=True)
    notes_cache = Column(JSON, nullable=True)  # Cached assembled study notes

    # Relationships
    student = relationship("Student", back_populates="sessions")
    results = relationship("QuestionResult", back_populates="session", lazy="select",
                           order_by="QuestionResult.created_at")


class QuestionResult(Base):
    __tablename__ = "question_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False, index=True)
    question_id = Column(Integer, nullable=False)
    click_path = Column(JSON, default=list)       # Array of clicked option labels e.g. ["C", "A", "B"]
    final_answer = Column(String, nullable=True)   # "A", "B", "C", "D" or None
    confidence_tap = Column(String, nullable=True)  # sure | unsure | guessing
    is_correct = Column(Boolean, default=False)
    time_taken = Column(Float, default=0.0)         # Seconds spent on this question
    time_expired = Column(Boolean, default=False)    # True if timer ran out
    skipped = Column(Boolean, default=False)         # True if student clicked skip
    classifier_label = Column(String, nullable=True)  # MASTERY | PRIORITY_FOCUS | TRUST_GAP | GROWTH_AREA
    classifier_confidence = Column(JSON, nullable=True)  # {label: score} dict
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    session = relationship("Session", back_populates="results")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(String, nullable=True)            # Exam year e.g. "2024"
    subject = Column(String, default="Biology")
    chapter_code = Column(String, nullable=True)     # Short code for grouping
    chapter_name = Column(String, nullable=False)    # Full chapter name
    topic = Column(String, nullable=True)            # Specific topic within chapter
    difficulty = Column(String, default="medium")    # easy | medium | hard

    # Bilingual question text
    question_en = Column(Text, nullable=True)
    question_bn = Column(Text, nullable=False)

    # Bilingual options
    option_a_en = Column(String, nullable=True)
    option_a_bn = Column(String, nullable=False)
    option_b_en = Column(String, nullable=True)
    option_b_bn = Column(String, nullable=False)
    option_c_en = Column(String, nullable=True)
    option_c_bn = Column(String, nullable=False)
    option_d_en = Column(String, nullable=True)
    option_d_bn = Column(String, nullable=False)

    # Answer
    correct = Column(String, nullable=False)  # "A", "B", "C", "D"

    # Explanations (pre-generated, used by notes_service)
    explanation_en = Column(Text, nullable=True)
    explanation_bn = Column(Text, nullable=True)

    # Confusable pair analysis
    confusable_pair = Column(String, nullable=True)      # e.g. "A-C" which options get confused
    confusable_note_en = Column(Text, nullable=True)
    confusable_note_bn = Column(Text, nullable=True)

    # Metadata
    frequency = Column(Integer, default=0)          # How often this topic appears in past exams
    neg_marking_risk = Column(String, nullable=True)  # high | medium | low
    verified = Column(Boolean, default=False)

    # Memory aids (from existing question bank)
    memory_trick = Column(Text, nullable=True)
    trap_note = Column(Text, nullable=True)

    # NCTB Textbook Highlights
    pdf_file = Column(String, nullable=True)         # filename e.g. "biology_part1.pdf"
    pdf_page = Column(Integer, nullable=True)        # 1-indexed page number
    pdf_bbox = Column(JSON, nullable=True)           # [x0, y0, x1, y1]


class CumulativeProfile(Base):
    __tablename__ = "cumulative_profiles"

    id = Column(String, primary_key=True, default=generate_uuid)
    student_id = Column(String, ForeignKey("students.id"), nullable=False, index=True)
    chapter_code = Column(String, nullable=False)
    mastery_count = Column(Integer, default=0)
    priority_count = Column(Integer, default=0)
    trust_count = Column(Integer, default=0)
    growth_count = Column(Integer, default=0)
    readiness_score = Column(Integer, default=0)
    trend = Column(String, nullable=True)          # "improving" | "declining" | "stable"
    last_updated = Column(DateTime, default=utcnow)

    # Relationships
    student = relationship("Student", back_populates="profiles")
