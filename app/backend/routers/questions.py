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
