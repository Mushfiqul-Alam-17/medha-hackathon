import sqlite3
import re
import json

conn = sqlite3.connect(r'c:\Users\mushf\Downloads\Medha\app\backend\medha.db')
c = conn.cursor()
c.execute("SELECT id, question_bn, option_a_bn, option_b_bn, option_c_bn, option_d_bn, chapter_name FROM questions")
rows = c.fetchall()

def is_english_only(text):
    if not text:
        return False
    # Check if there is any Bengali character
    return not bool(re.search(r'[\u0980-\u09FF]', text))

matches = []
for r in rows:
    qid, q_text, opt_a, opt_b, opt_c, opt_d, ch = r
    
    eng_fields = []
    if is_english_only(q_text):
        eng_fields.append("question")
    if is_english_only(opt_a):
        eng_fields.append("option_a")
    if is_english_only(opt_b):
        eng_fields.append("option_b")
    if is_english_only(opt_c):
        eng_fields.append("option_c")
    if is_english_only(opt_d):
        eng_fields.append("option_d")
        
    if eng_fields:
        matches.append({
            "id": qid,
            "chapter": ch,
            "eng_fields": eng_fields,
            "question": q_text,
            "options": [opt_a, opt_b, opt_c, opt_d]
        })

with open("eng_db_matches.json", "w", encoding="utf-8") as f:
    json.dump(matches, f, ensure_ascii=False, indent=2)

print(f"Scan complete. Found {len(matches)} questions with English-only fields. Saved to eng_db_matches.json.")
conn.close()
