"""
MEDHA — Wellbeing Service
Checks student mood history, session frequency, and performance drops
to trigger supportive, non-judgmental wellbeing interventions.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from models import Student, Session as ExamSession


def check_wellbeing_triggers(student_id: str, current_mood: Optional[str], db: Session) -> Dict[str, Any]:
    """
    Evaluate behavioral and self-reported metrics to determine if a wellbeing
    card should be shown to the student before or after an exam.
    """
    triggers = []
    
    # Fetch student and recent history
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return {"show_card": False, "triggers": [], "message": ""}

    # 1. Consecutive Low Moods
    mood_history = student.mood_history or []
    # If the current mood is provided, consider it the latest
    recent_moods = mood_history[-2:] if not current_mood else (mood_history[-1:] + [current_mood])
    
    if len(recent_moods) >= 2 and all(m in ["tired", "low"] for m in recent_moods):
        triggers.append("consecutive_low_mood")

    # 2. Overuse (Fatigue Risk)
    # Check sessions in the last 24 hours
    one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
    sessions_today = db.query(ExamSession).filter(
        ExamSession.student_id == student_id,
        ExamSession.started_at >= one_day_ago
    ).count()

    if sessions_today >= 3:
        triggers.append("overuse")

    # 3. Significant Score Drop
    # Get the last two completed sessions
    recent_sessions = db.query(ExamSession).filter(
        ExamSession.student_id == student_id,
        ExamSession.completed_at != None
    ).order_by(ExamSession.completed_at.desc()).limit(2).all()

    if len(recent_sessions) == 2:
        last_score = recent_sessions[0].final_score
        prev_score = recent_sessions[1].final_score
        # E.g. score dropped by more than 20% of a 15-question set (~3 points out of 15)
        # Note: scores can be None if session was empty, handle carefully
        if last_score is not None and prev_score is not None:
             if last_score < (prev_score - 3.0): 
                 triggers.append("significant_score_drop")

    # Construct the intervention response
    show_card = len(triggers) > 0
    message = _get_wellbeing_message(triggers)

    return {
        "show_card": show_card,
        "triggers": triggers,
        "message": message
    }


def _get_wellbeing_message(triggers: List[str]) -> str:
    if not triggers:
        return ""
    
    if "consecutive_low_mood" in triggers and "overuse" in triggers:
        return "You've been studying hard and feeling drained. MEDHA strongly suggests taking a full break today. Medical admission is a marathon, not a sprint. Rest is productive."
    elif "overuse" in triggers:
        return "You've done a lot of sessions today! Cognitive fatigue reduces retention. Consider stepping away from the screen for a bit."
    elif "consecutive_low_mood" in triggers:
        return "It looks like you've been feeling low or tired lately. Be kind to yourself. Make sure you are eating well and sleeping enough."
    elif "significant_score_drop" in triggers:
        return "Your score dropped recently—don't panic! This happens when you are tired or tackling a harder topic. Take a breather, review your Growth Areas calmly, and trust your progress."
    
    return "Remember to take care of yourself. Your wellbeing is your best study tool."

def record_mood(student_id: str, mood: str, db: Session):
    """Updates the student's mood history (keeps last 10)."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if student and mood:
        history = list(student.mood_history) if student.mood_history else []
        history.append(mood)
        # Keep only the last 10 moods to prevent infinite growth
        student.mood_history = history[-10:]
        db.commit()
