"""
MEDHA — Questions Router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import schemas
from services.question_service import get_exam_questions, get_chapter_frequencies

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/session", response_model=List[schemas.QuestionOut])
def start_exam_questions(
    count: int = 15,
    chapter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Fetch random questions for a new exam session."""
    return get_exam_questions(db, count=count, chapter=chapter)


@router.get("/chapters", response_model=List[schemas.ChapterInfo])
def list_chapters(db: Session = Depends(get_db)):
    """Get chapter list and historical frequency data."""
    return get_chapter_frequencies(db)


@router.get("/test-bank")
def get_test_bank(count: int = 10, db: Session = Depends(get_db)):
    """Fetch random questions WITH answers and PDF locations for the test site."""
    from models import Question
    from sqlalchemy.sql.expression import func
    questions = db.query(Question).order_by(func.random()).limit(count).all()
    return [{
        "id": q.id,
        "chapter_name": q.chapter_name,
        "topic": q.topic,
        "question_bn": q.question_bn,
        "option_a_bn": q.option_a_bn,
        "option_b_bn": q.option_b_bn,
        "option_c_bn": q.option_c_bn,
        "option_d_bn": q.option_d_bn,
        "correct": q.correct,
        "pdf_file": q.pdf_file,
        "pdf_page": q.pdf_page,
        "trap_note": q.trap_note,
        "difficulty": q.difficulty
    } for q in questions]
