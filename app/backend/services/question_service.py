"""
MEDHA — Question Service
Handles fetching, filtering, and preparing questions for the exam interface.
Strips out correct answers and explanations before sending to the frontend.
"""

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from typing import List, Dict, Any, Optional
from models import Question
import schemas


def get_exam_questions(db: Session, count: int = 15, chapter: Optional[str] = None) -> List[schemas.QuestionOut]:
    """
    Fetch random questions for an exam session.
    Strips sensitive fields (correct answer, explanations) by returning QuestionOut schemas.
    """
    query = db.query(Question)
    
    if chapter:
        query = query.filter(Question.chapter_code == chapter)
        
    # Get random questions using SQLite random function
    questions = query.order_by(func.random()).limit(count).all()
    
    # Convert ORM models to Pydantic schemas (which automatically drops sensitive fields)
    return [schemas.QuestionOut.model_validate(q) for q in questions]


def get_chapter_frequencies(db: Session) -> List[schemas.ChapterInfo]:
    """
    Get all unique chapters, their total question counts, and historical frequencies.
    Used for the readiness heatmap.
    """
    # Group by chapter_name and chapter_code, sum frequencies and count questions
    results = db.query(
        Question.chapter_code,
        Question.chapter_name,
        func.sum(Question.frequency).label("total_frequency"),
        func.count(Question.id).label("question_count")
    ).group_by(Question.chapter_code, Question.chapter_name).all()
    
    chapters = []
    for r in results:
        # Fallback if frequency is missing
        freq = r.total_frequency if r.total_frequency is not None else 10
        chapters.append(schemas.ChapterInfo(
            chapter_code=r.chapter_code or "GEN",
            chapter_name=r.chapter_name,
            frequency=freq,
            question_count=r.question_count
        ))
        
    # Sort by frequency descending
    chapters.sort(key=lambda x: x.frequency, reverse=True)
    return chapters


def get_question_metadata(db: Session, question_id: int) -> Optional[Question]:
    """
    Fetch the full question object (including answers and explanations).
    Used backend-side during session completion to classify and score.
    """
    return db.query(Question).filter(Question.id == question_id).first()
