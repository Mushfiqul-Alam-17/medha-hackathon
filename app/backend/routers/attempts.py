from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from services.scoring_service import calculate_scoring, build_dna_groups
from services.question_service import get_question_metadata
from typing import Optional, Any, Dict, List

router = APIRouter(prefix="/attempts", tags=["attempts"])

@router.get("/{session_id}")
def get_attempt(session_id: str, db: Session = Depends(get_db)):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    results = db.query(models.QuestionResult).filter(models.QuestionResult.session_id == session_id).all()
    
    LETTERS = ["A", "B", "C", "D"]
    
    def get_option_text(q: models.Question, option_letter: str) -> str:
        mapping = {
            "A": q.option_a_bn,
            "B": q.option_b_bn,
            "C": q.option_c_bn,
            "D": q.option_d_bn
        }
        return mapping.get(option_letter, "")
        
    classified_results = []
    for r in results:
        q = get_question_metadata(db, r.question_id)
        if not q:
            continue
        classified_results.append({
            "id": r.id,
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
            "question_bn": q.question_bn,
            "question_en": q.question_en,
            "options_bn": [q.option_a_bn, q.option_b_bn, q.option_c_bn, q.option_d_bn],
            "options_en": [q.option_a_en, q.option_b_en, q.option_c_en, q.option_d_en] if q.option_a_en else None,
            "correct_answer": q.correct,
            "correct_answer_text": get_option_text(q, q.correct),
            "final_answer_text": get_option_text(q, r.final_answer) if r.final_answer else None,
            "explanation_bn": q.explanation_bn,
            "explanation_en": q.explanation_en,
            "confusable_note_bn": q.confusable_note_bn,
            "confusable_note_en": q.confusable_note_en,
            "memory_trick": q.memory_trick,
            "trap_note": q.trap_note,
            "pdf_file": q.pdf_file,
            "pdf_page": q.pdf_page,
            "pdf_bbox": q.pdf_bbox,
            "classifier_label": r.classifier_label or "MASTERY",
            "classifier_confidence": r.classifier_confidence or {}
        })
        
    # Scoring
    scoring = calculate_scoring(classified_results)
    
    # DNA Groups
    dna_groups = build_dna_groups(classified_results)
    
    # Map item helper for frontend format
    def map_item(r):
        return {
            "questionId": r["question_id"],
            "finalAnswerIndex": LETTERS.index(r["final_answer"]) if r["final_answer"] in LETTERS else None,
            "isCorrect": r["is_correct"],
            "confidence": r["confidence_tap"],
            "questionText": r["question_bn"],
            "options": r["options_bn"],
            "correctAnswerIndex": LETTERS.index(r["correct_answer"]) if r["correct_answer"] in LETTERS else 0,
            "chapter": r["chapter_name"],
            "timeTaken": r["time_taken"],
            "clickSequence": r["click_path"],
            "pdf_file": r["pdf_file"],
            "pdf_page": r["pdf_page"]
        }
        
    mapped_items = [map_item(r) for r in classified_results]
    
    # Parse notes if cached
    parsed_notes = None
    if session.notes_cache:
        slow = []
        confused = []
        danger = []
        
        for sec in session.notes_cache:
            header = sec.get("header", "")
            items = sec.get("items", [])
            if "Priority Focus" in header:
                for item in items:
                    danger.append({
                        "topic": item.get("topic"),
                        "explanation": item.get("explanation"),
                        "dangerNote": item.get("frame"),
                        "whyCorrect": f"সঠিক উত্তর: {item.get('correct_answer')}" if item.get("correct_answer") else None,
                        "whyTricked": f"তোমার উত্তর: {item.get('wrong_answer')}" if item.get("wrong_answer") else None,
                        "memoryTrick": item.get("memory_trick"),
                        "trapQuestion": item.get("trap_note"),
                        "pdf_file": item.get("pdf_file"),
                        "pdf_page": item.get("pdf_page"),
                        "correct_answer": item.get("correct_answer")
                    })
            elif "Trust Gap" in header:
                for item in items:
                    slow.append({
                        "topic": item.get("topic"),
                        "explanation": item.get("explanation"),
                        "speedNote": item.get("frame"),
                        "memoryTrick": item.get("memory_trick"),
                        "pdf_file": item.get("pdf_file"),
                        "pdf_page": item.get("pdf_page"),
                        "correct_answer": item.get("correct_answer")
                    })
            elif "Growth Area" in header:
                for item in items:
                    confused.append({
                        "topic": item.get("topic"),
                        "explanation": item.get("explanation"),
                        "memoryTrick": item.get("memory_trick"),
                        "comparisonTable": [
                            {"concept": "মনে রেখো", "description": item.get("confusable_note"), "isCorrect": True}
                        ] if item.get("confusable_note") else [],
                        "pdf_file": item.get("pdf_file"),
                        "pdf_page": item.get("pdf_page"),
                        "correct_answer": item.get("correct_answer")
                    })
                    
        parsed_notes = {
            "sections": session.notes_cache,
            "slow": slow,
            "confused": confused,
            "danger": danger
        }
        
    return {
        "id": session.id,
        "score": scoring["final_score"],
        "total": scoring["total"],
        "accuracy": scoring["accuracy"],
        "readiness": {
            "correct": scoring["raw_score"],
            "total": scoring["total"],
            "avgTime": "12s"
        },
        "items": mapped_items,
        "groups": {
            "master": [map_item(r) for r in dna_groups.get("MASTERY", [])],
            "danger": [map_item(r) for r in dna_groups.get("PRIORITY_FOCUS", [])],
            "slow": [map_item(r) for r in dna_groups.get("TRUST_GAP", [])],
            "confused": [map_item(r) for r in dna_groups.get("GROWTH_AREA", [])]
        },
        "results": classified_results,
        "notes": parsed_notes,
        "notesSource": "assembly" if parsed_notes else None
    }
