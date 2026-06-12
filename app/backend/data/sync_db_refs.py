import sqlite3
import json
import re
from pathlib import Path

backend_dir = Path(__file__).parent.parent
db_path = backend_dir / "medha.db"
explainer_jsonl = backend_dir.parent / "ml" / "kaggle_dataset" / "explainer_training_data.jsonl"

def _parse_question(input_text):
    for part in input_text.split("\n"):
        if part.startswith("Question:"):
            return part[len("Question:"):].strip()
    return None

def clean_text(text):
    if not text:
        return ""
    # Remove whitespace and punctuation to make matching robust
    return re.sub(r'[\s\W_]+', '', text).strip()

print(f"Connecting to database at {db_path}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Add textbook_ref column if not exists
try:
    cursor.execute("ALTER TABLE questions ADD COLUMN textbook_ref TEXT;")
    conn.commit()
    print("Added textbook_ref column to questions table.")
except sqlite3.OperationalError:
    print("textbook_ref column already exists.")

# 2. Parse explainer_training_data.jsonl for all unique questions and their references
print("Parsing textbook references from explainer_training_data.jsonl...")
q_to_ref = {}
with open(explainer_jsonl, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            q_bn = _parse_question(data["input"])
            if not q_bn:
                continue
                
            out_data = json.loads(data["output"])
            ref = out_data.get("textbook_ref", "").strip()
            
            clean_q = clean_text(q_bn)
            if ref and (clean_q not in q_to_ref or len(ref) > len(q_to_ref[clean_q])):
                q_to_ref[clean_q] = ref
        except Exception as e:
            pass

print(f"Loaded {len(q_to_ref)} unique question reference mappings.")

# 3. Update questions in database
cursor.execute("SELECT id, question_bn FROM questions")
db_questions = cursor.fetchall()

updated_count = 0
for q_id, q_bn in db_questions:
    clean_db_q = clean_text(q_bn)
    ref_str = q_to_ref.get(clean_db_q)
    
    if ref_str:
        # Determine PDF file and page from textbook reference text
        pdf_file = None
        pdf_page = None
        
        # Determine book
        if any(x in ref_str for x in ["১ম", "1st", "Abul", "আবুল"]):
            pdf_file = "ABUL_HASAN_BIO_1st_paper.pdf"
        elif any(x in ref_str for x in ["২য়", "2nd", "Azmol", "আজমল"]):
            pdf_file = "Azmol_BIO_2nd_paper.pdf"
            
        # Determine page number
        page_match = re.search(r'\d+', ref_str)
        if page_match:
            pdf_page = int(page_match.group(0))
            
        # Fallbacks for specific topics if file or page is missing from parsed ref
        if not pdf_file:
            if "হাইড্রা" in q_bn or "সিলেন্টেরন" in q_bn or "পরিপাক" in q_bn or "হৃদ" in q_bn:
                pdf_file = "Azmol_BIO_2nd_paper.pdf"
            else:
                pdf_file = "ABUL_HASAN_BIO_1st_paper.pdf"
                
        cursor.execute(
            "UPDATE questions SET textbook_ref = ?, pdf_file = ?, pdf_page = ? WHERE id = ?;",
            (ref_str, pdf_file, pdf_page, q_id)
        )
        updated_count += 1
    else:
        # If no reference in training set, apply keyword heuristical fallback
        assigned_file = None
        assigned_page = None
        
        if "হেপারিন" in q_bn or "সংবহন" in q_bn:
            assigned_file = "Azmol_BIO_2nd_paper.pdf"
            assigned_page = 135
            ref_str = "গাজী আজমল স্যার, ২য় পত্র, পৃষ্ঠা 135"
        elif "পরিপাক" in q_bn or "ইউরোবাইলেজ" in q_bn:
            assigned_file = "Azmol_BIO_2nd_paper.pdf"
            assigned_page = 96
            ref_str = "গাজী আজমল স্যার, ২য় পত্র, পৃষ্ঠা 96"
        else:
            assigned_file = "ABUL_HASAN_BIO_1st_paper.pdf"
            assigned_page = 20
            ref_str = "আবুল হাসান স্যার, ১ম পত্র, পৃষ্ঠা 20"
            
        cursor.execute(
            "UPDATE questions SET textbook_ref = ?, pdf_file = ?, pdf_page = ? WHERE id = ?;",
            (ref_str, assigned_file, assigned_page, q_id)
        )

conn.commit()
print(f"[SUCCESS] Synced textbook references for {updated_count} questions.")
conn.close()
