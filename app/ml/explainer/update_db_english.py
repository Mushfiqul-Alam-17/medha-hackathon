import sqlite3
import re
import sys
from pathlib import Path

# Add the directory to sys.path to import fix_english_options
sys.path.append(str(Path(__file__).parent))
from fix_english_options import ENGLISH_TO_BENGALI

db_path = Path(__file__).parent.parent.parent / "backend" / "medha.db"
if not db_path.exists():
    print(f"Error: Database not found at {db_path}")
    exit(1)

print(f"Connecting to database at {db_path}...")
conn = sqlite3.connect(str(db_path))
c = conn.cursor()

# Get all questions
c.execute("SELECT id, question_bn, option_a_bn, option_b_bn, option_c_bn, option_d_bn FROM questions")
rows = c.fetchall()

updated_count = 0

for row in rows:
    qid, q_text, opt_a, opt_b, opt_c, opt_d = row
    
    # Check if any field matches an English term and needs update
    new_q = q_text
    new_a = opt_a
    new_b = opt_b
    new_c = opt_c
    new_d = opt_d
    
    # Simple substitution helper
    def translate_text(text):
        if not text:
            return text
        text_stripped = text.strip()
        # Case insensitive exact match or word replacement
        if text_stripped in ENGLISH_TO_BENGALI:
            return ENGLISH_TO_BENGALI[text_stripped]
        # Check case insensitivity
        for eng, bn in ENGLISH_TO_BENGALI.items():
            if eng.lower() == text_stripped.lower():
                return bn
        return text

    updated = False
    
    # Check options first
    val_a = translate_text(opt_a)
    if val_a != opt_a:
        new_a = val_a
        updated = True
        
    val_b = translate_text(opt_b)
    if val_b != opt_b:
        new_b = val_b
        updated = True
        
    val_c = translate_text(opt_c)
    if val_c != opt_c:
        new_c = val_c
        updated = True
        
    val_d = translate_text(opt_d)
    if val_d != opt_d:
        new_d = val_d
        updated = True
        
    # Also check if any English term is embedded inside the question text
    for eng, bn in sorted(ENGLISH_TO_BENGALI.items(), key=lambda x: len(x[0]), reverse=True):
        # We replace the word if it appears in the question text
        # E.g. "Golgi complex" in "Golgi complex কোনটি সংশ্লেষ করে না?"
        if eng in new_q:
            new_q = new_q.replace(eng, bn)
            updated = True
            
    if updated:
        c.execute(
            "UPDATE questions SET question_bn = ?, option_a_bn = ?, option_b_bn = ?, option_c_bn = ?, option_d_bn = ? WHERE id = ?",
            (new_q, new_a, new_b, new_c, new_d, qid)
        )
        updated_count += 1

conn.commit()
print(f"Successfully updated {updated_count} questions in the database with Bengali translations!")
conn.close()
