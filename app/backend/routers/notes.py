"""
MEDHA — Notes Router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from services.notes_service import assemble_notes
from services.scoring_service import build_dna_groups
from services.session_service import complete_session

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/generate", response_model=schemas.NotesResponse)
def api_generate_notes(req: schemas.NotesGenerate, db: Session = Depends(get_db)):
    """
    Generate study notes for a completed session.
    First checks cache. If not found, assembles from question metadata.
    """
    session = db.query(models.Session).filter(models.Session.id == req.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 1. Check cache
    if session.notes_cache:
        return {
            "session_id": req.session_id,
            "sections": session.notes_cache,
            "source": "cached"
        }

    # 2. Re-fetch classified results if needed
    results = db.query(models.QuestionResult).filter(models.QuestionResult.session_id == req.session_id).all()
    
    if not results:
        return {"session_id": req.session_id, "sections": [], "source": "assembly"}

    # We need the full question metadata for notes. 
    # Let's recreate the classified_results payload structure that complete_session builds
    from services.question_service import get_question_metadata
    
    enriched_results = []
    for r in results:
        q = get_question_metadata(db, r.question_id)
        enriched_results.append({
            "classifier_label": r.classifier_label,
            "topic": q.topic or q.chapter_name,
            "chapter_name": q.chapter_name,
            "question_bn": q.question_bn,
            "correct_answer_text": _get_option_text(q, q.correct),
            "final_answer_text": _get_option_text(q, r.final_answer) if r.final_answer else None,
            "explanation_bn": q.explanation_bn,
            "confusable_note_bn": q.confusable_note_bn,
            "memory_trick": q.memory_trick,
            "trap_note": q.trap_note,
            "pdf_file": q.pdf_file,
            "pdf_page": q.pdf_page
        })

    # 3. Build DNA Groups
    dna_report = build_dna_groups(enriched_results)

    # 4. Assemble Notes
    sections = assemble_notes(dna_report)

    # 5. Cache for future requests
    session.notes_cache = sections
    db.commit()

    return {
        "session_id": req.session_id,
        "sections": sections,
        "source": "assembly"
    }


def _get_option_text(q: models.Question, option_letter: str) -> str:
    mapping = {
        "A": q.option_a_bn,
        "B": q.option_b_bn,
        "C": q.option_c_bn,
        "D": q.option_d_bn
    }
    return mapping.get(option_letter, "")
