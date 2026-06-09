"""
MEDHA — Session Service
Manages exam lifecycles: starting, tracking events, and completing.
Wires together classification, scoring, and profiling on completion.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import models
import schemas
from services.classifier_service import classify_session
from services.scoring_service import calculate_scoring, build_dna_groups, calculate_readiness
from services.wellbeing_service import check_wellbeing_triggers
from services.profile_service import update_cumulative_profile
from services.question_service import get_question_metadata


def start_session(db: Session, student_id: str, mood: str, total_questions: int) -> models.Session:
    """Create a new exam session record."""
    session = models.Session(
        student_id=student_id,
        mood_at_start=mood,
        total_questions=total_questions
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def record_question_event(db: Session, event: schemas.QuestionEvent) -> models.QuestionResult:
    """
    Save a single question result.
    This is called repeatedly during the exam (fire-and-forget).
    """
    # Look up the question to verify correctness
    q = get_question_metadata(db, event.question_id)
    if not q:
        raise ValueError(f"Question {event.question_id} not found")

    is_correct = (event.final_answer == q.correct) if event.final_answer else False

    result = models.QuestionResult(
        session_id=event.session_id,
        question_id=event.question_id,
        click_path=event.click_path,
        final_answer=event.final_answer,
        confidence_tap=event.confidence_tap,
        is_correct=is_correct,
        time_taken=event.time_taken,
        time_expired=event.time_expired,
        skipped=event.skipped
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def complete_session(db: Session, session_id: str, tab_switches: int = 0) -> schemas.SessionCompleteResponse:
    """
    Finalize the exam. This is the main orchestration function.
    1. Fetch all raw results
    2. Build data payloads
    3. Call classifier
    4. Calculate scores
    5. Update cumulative profile
    6. Return everything the frontend needs
    """
    db_session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise ValueError("Session not found")

    results = db.query(models.QuestionResult).filter(models.QuestionResult.session_id == session_id).all()
    
    # 1. Prepare raw payload for classifier & frontend
    raw_results_for_classification = []
    for r in results:
        q = get_question_metadata(db, r.question_id)
        raw_results_for_classification.append({
            "id": r.id,  # internal ID
            "question_id": r.question_id,
            "topic": q.topic or q.chapter_name,
            "chapter_name": q.chapter_name,
            "difficulty": q.difficulty,
            "time_taken": r.time_taken,
            "click_path": r.click_path,
            "confidence_tap": r.confidence_tap,
            "is_correct": r.is_correct,
            "skipped": r.skipped,
            "time_expired": r.time_expired,
            "final_answer": r.final_answer,
            "switch_count": max(0, len(r.click_path) - 1) if r.click_path else 0,
            # Metadata needed for frontend cards and notes assembly
            "question_bn": q.question_bn,
            "question_en": q.question_en,
            "options_bn": [q.option_a_bn, q.option_b_bn, q.option_c_bn, q.option_d_bn],
            "options_en": [q.option_a_en, q.option_b_en, q.option_c_en, q.option_d_en] if q.option_a_en else None,
            "correct_answer": q.correct,
            # Determine correct text
            "correct_answer_text": _get_option_text(q, q.correct),
            "final_answer_text": _get_option_text(q, r.final_answer) if r.final_answer else None,
            "explanation_bn": q.explanation_bn,
            "explanation_en": q.explanation_en,
            "confusable_note_bn": q.confusable_note_bn,
            "confusable_note_en": q.confusable_note_en,
            "memory_trick": q.memory_trick,
            "trap_note": q.trap_note,
            "pdf_file": q.pdf_file,
            "pdf_page": q.pdf_page,
            "pdf_bbox": q.pdf_bbox
        })

    # 2. Classify all results
    classified_results = classify_session(raw_results_for_classification)

    # 3. Update database with classification labels
    # We do this so we can query historically later
    for cr in classified_results:
        db_result = next((r for r in results if r.id == cr["id"]), None)
        if db_result:
            db_result.classifier_label = cr["classifier_label"]
            db_result.classifier_confidence = cr["classifier_confidence"]

    # 4. Calculate Scoring
    scoring = calculate_scoring(classified_results)
    
    # 5. Build DNA Groups
    dna_groups = build_dna_groups(classified_results)
    session_readiness = calculate_readiness(dna_groups)

    # 6. Finalize session record
    db_session.completed_at = datetime.now(timezone.utc)
    db_session.tab_switches = tab_switches
    db_session.raw_score = scoring["raw_score"]
    db_session.final_score = scoring["final_score"]
    db_session.negative_deduction = scoring["negative_deduction"]
    
    # Update student totals
    student = db.query(models.Student).filter(models.Student.id == db_session.student_id).first()
    if student:
        student.total_sessions += 1

    db.commit()

    # 7. Update Cumulative Profile
    update_cumulative_profile(db_session.student_id, classified_results, db)

    # 8. Check Wellbeing triggers
    wellbeing = check_wellbeing_triggers(db_session.student_id, db_session.mood_at_start, db)

    # Format response
    response_results = [schemas.ClassifiedResult(**cr) for cr in classified_results]
    
    return schemas.SessionCompleteResponse(
        session_id=session_id,
        classified_results=response_results,
        scoring=schemas.ScoringResult(**scoring),
        dna_groups=schemas.DnaGroups(**dna_groups),
        readiness_score=session_readiness,
        wellbeing=wellbeing if wellbeing["show_card"] else None
    )


def _get_option_text(q: models.Question, option_letter: str) -> str:
    """Helper to extract the text for A, B, C, D."""
    mapping = {
        "A": q.option_a_bn,
        "B": q.option_b_bn,
        "C": q.option_c_bn,
        "D": q.option_d_bn
    }
    return mapping.get(option_letter, "")
