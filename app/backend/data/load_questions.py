"""
MEDHA — Production Question Loader
Loads the explainer proofread pool (first 228 training rows → 38 unique questions)
from questions_clean.jsonl into SQLite.
"""

import argparse
import json
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from database import SessionLocal, init_db
from models import Question

EXPLAINER_JSONL = backend_dir.parent / "ml" / "kaggle_dataset" / "explainer_training_data.jsonl"
EXPLAINER_LINE_CUTOFF = 222  # 37 questions × 6 behavioral variants each


def _parse_explainer_question(line: str) -> str | None:
    data = json.loads(line)
    for part in data["input"].split("\n"):
        if part.startswith("Question:"):
            return part[len("Question:") :].strip()
    return None


def get_explainer_pool_question_bns() -> list[str]:
    """Unique question texts from the first 228 explainer training rows."""
    ordered: list[str] = []
    seen: set[str] = set()
    with open(EXPLAINER_JSONL, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if i > EXPLAINER_LINE_CUTOFF:
                break
            if not line.strip():
                continue
            q_bn = _parse_explainer_question(line)
            if q_bn and q_bn not in seen:
                seen.add(q_bn)
                ordered.append(q_bn)
    return ordered


def _build_question_row(q_data: dict, pdf_mappings: dict) -> Question:
    opts = q_data.get("options", {})
    q_id = q_data.get("id")
    mapping = pdf_mappings.get(q_id)

    return Question(
        year=str(q_data.get("year", "Unknown")),
        subject=q_data.get("subject", "Biology"),
        chapter_code=q_data.get("chapter_code", "EXPLAINER"),
        chapter_name=q_data.get("chapter_name_bn", ""),
        topic=q_data.get("chapter_name_en") or q_data.get("topic", ""),
        difficulty=q_data.get("difficulty", "medium"),
        question_bn=q_data.get("question_bn", ""),
        question_en=q_data.get("question_en") or None,
        option_a_bn=opts.get("A", {}).get("bn", ""),
        option_a_en=opts.get("A", {}).get("en") or None,
        option_b_bn=opts.get("B", {}).get("bn", ""),
        option_b_en=opts.get("B", {}).get("en") or None,
        option_c_bn=opts.get("C", {}).get("bn", ""),
        option_c_en=opts.get("C", {}).get("en") or None,
        option_d_bn=opts.get("D", {}).get("bn", ""),
        option_d_en=opts.get("D", {}).get("en") or None,
        correct=q_data.get("correct", "A"),
        explanation_bn=q_data.get("explanation_bn", ""),
        explanation_en=q_data.get("explanation_en") or None,
        memory_trick="",
        trap_note=q_data.get("confusable_note", ""),
        frequency=q_data.get("frequency", 1),
        verified=q_data.get("verified", True),
        pdf_file=mapping["file"] if mapping else None,
        pdf_page=mapping["page"] if mapping else None,
        pdf_bbox=mapping["bbox"] if mapping else None,
    )


def run(force: bool = False):
    print("Initializing Database...")
    init_db()

    data_file = backend_dir / "data" / "questions_clean.jsonl"
    if not data_file.exists():
        print(f"ERROR: {data_file} not found.")
        return
    if not EXPLAINER_JSONL.exists():
        print(f"ERROR: {EXPLAINER_JSONL} not found.")
        return

    pool_bns = get_explainer_pool_question_bns()
    print(f"Explainer pool: {len(pool_bns)} unique questions from first {EXPLAINER_LINE_CUTOFF} training rows.")

    clean_by_bn: dict[str, dict] = {}
    with open(data_file, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                clean_by_bn[row["question_bn"]] = row

    spelling_map = {
        "ফুসফসের আবরণকে কী বলে?": "ফুসফুসের আবরণকে কী বলে?"
    }

    missing = [q for q in pool_bns if spelling_map.get(q, q) not in clean_by_bn]
    if missing:
        print(f"WARNING: {len(missing)} explainer questions missing from questions_clean.jsonl: {missing}")

    mapping_file = backend_dir / "data" / "question_pdf_mapping.json"
    pdf_mappings = {}
    if mapping_file.exists():
        with open(mapping_file, encoding="utf-8") as f:
            pdf_mappings = json.load(f)

    db = SessionLocal()
    existing = db.query(Question).count()
    if existing > 0 and not force:
        print(f"Database already contains {existing} questions.")
        print("Run with --force to reload the explainer pool.")
        db.close()
        return

    if force and existing > 0:
        deleted = db.query(Question).delete()
        db.commit()
        print(f"Cleared {deleted} existing questions.")

    loaded_count = 0
    for q_bn in pool_bns:
        lookup_bn = spelling_map.get(q_bn, q_bn)
        if lookup_bn in clean_by_bn:
            db.add(_build_question_row(clean_by_bn[lookup_bn], pdf_mappings))
            loaded_count += 1
        else:
            print(f"Skipping seeding of missing question: {q_bn}")

    db.commit()
    count = db.query(Question).count()
    print(f"[SUCCESS] Seeded {loaded_count} explainer-pool questions (total in DB: {count}).")
    db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load explainer proofread questions into medha.db")
    parser.add_argument("--force", action="store_true", help="Replace existing questions with the explainer pool")
    args = parser.parse_args()
    run(force=args.force)
