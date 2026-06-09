"""
MEDHA — Profile Router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from services.profile_service import get_overall_readiness

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/{student_id}", response_model=schemas.ProfileResponse)
def get_student_profile(student_id: str, db: Session = Depends(get_db)):
    """Fetch cumulative student profile including chapter breakdowns."""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    profiles = db.query(models.CumulativeProfile).filter(models.CumulativeProfile.student_id == student_id).all()
    
    chapter_profiles = []
    for p in profiles:
        # We'd fetch the actual chapter name if needed, assuming the DB has a map or using code directly
        chapter_profiles.append(schemas.ChapterProfile(
            chapter_code=p.chapter_code,
            chapter_name=p.chapter_code, # Fallback
            mastery_count=p.mastery_count,
            priority_count=p.priority_count,
            trust_count=p.trust_count,
            growth_count=p.growth_count,
            readiness_score=p.readiness_score,
            trend=p.trend
        ))

    readiness = get_overall_readiness(student_id, db)

    return {
        "student_id": student.id,
        "username": student.username,
        "total_sessions": student.total_sessions,
        "chapters": chapter_profiles,
        "overall_readiness": readiness["score"],
        "mood_history": student.mood_history or []
    }


@router.get("/{student_id}/readiness", response_model=schemas.ReadinessResponse)
def get_student_readiness(student_id: str, db: Session = Depends(get_db)):
    """Fetch just the overall readiness score and trend line."""
    readiness = get_overall_readiness(student_id, db)
    return {
        "student_id": student_id,
        "readiness_score": readiness["score"],
        "trend": readiness["trend"],
        "session_scores": readiness["session_scores"]
    }


@router.get("/{student_id}/history", response_model=schemas.HistoryResponse)
def get_student_history(student_id: str, db: Session = Depends(get_db)):
    """Fetch history of past sessions."""
    from services.scoring_service import calculate_readiness

    sessions = db.query(models.Session).filter(
        models.Session.student_id == student_id,
        models.Session.completed_at != None
    ).order_by(models.Session.completed_at.desc()).limit(20).all()

    history = []
    for s in sessions:
        # Fetch question results to compute readiness score dynamically
        results = db.query(models.QuestionResult).filter(models.QuestionResult.session_id == s.id).all()
        groups = {
            "MASTERY": [1] * len([r for r in results if r.classifier_label == "MASTERY"]),
            "PRIORITY_FOCUS": [1] * len([r for r in results if r.classifier_label == "PRIORITY_FOCUS"]),
            "TRUST_GAP": [1] * len([r for r in results if r.classifier_label == "TRUST_GAP"]),
            "GROWTH_AREA": [1] * len([r for r in results if r.classifier_label == "GROWTH_AREA"])
        }
        score = calculate_readiness(groups)
        correct_count = sum(1 for r in results if r.is_correct)

        history.append({
            "id": s.id,
            "createdAt": s.started_at,
            "mood": s.mood_at_start,
            "readiness": {
                "score": score,
                "correct": correct_count,
                "total": s.total_questions
            }
        })

    return {"student_id": student_id, "sessions": history}
