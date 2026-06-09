"""
MEDHA — Sessions Router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import schemas
from services.session_service import start_session, record_question_event, complete_session
from services.question_service import get_exam_questions
from services.wellbeing_service import record_mood

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/start", response_model=schemas.SessionStartResponse)
def api_start_session(req: schemas.SessionStart, db: Session = Depends(get_db)):
    """Initialize a new exam session and return the questions."""
    # 1. Record mood
    if req.mood:
        record_mood(req.student_id, req.mood, db)
        
    # 2. Create session record
    session = start_session(db, req.student_id, req.mood or "unknown", req.question_count)
    
    # 3. Get questions
    questions = get_exam_questions(db, count=req.question_count, chapter=req.chapter)
    
    return {
        "session_id": session.id,
        "questions": questions,
        "total_questions": len(questions)
    }


@router.post("/event", response_model=schemas.QuestionEventResponse)
def api_question_event(req: schemas.QuestionEvent, db: Session = Depends(get_db)):
    """Record a single question attempt (fire-and-forget during exam)."""
    try:
        result = record_question_event(db, req)
        return {"ok": True, "result_id": result.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/complete", response_model=schemas.SessionCompleteResponse)
def api_complete_session(req: schemas.SessionComplete, db: Session = Depends(get_db)):
    """Finalize session, run classifier, and return full DNA report."""
    try:
        # Process bulk items if passed
        for item in req.items:
            item.session_id = req.session_id
            record_question_event(db, item)
            
        return complete_session(db, req.session_id, req.tab_switches)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
