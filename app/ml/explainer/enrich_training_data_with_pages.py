import json
import sqlite3
import re
from pathlib import Path

# Paths
ml_explainer_dir = Path(__file__).parent
input_file = ml_explainer_dir / "data" / "explainer_training_data.jsonl"
db_path = ml_explainer_dir.parent.parent / "backend" / "medha.db"

if not input_file.exists():
    print(f"ERROR: {input_file} not found.")
    exit(1)

print("Connecting to DB...")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Load all database questions to build a fast lookup dict by question_bn
cur.execute("SELECT question_bn, pdf_file, pdf_page FROM questions")
db_qs = cur.fetchall()

q_map = {}
for q_bn, pdf_file, pdf_page in db_qs:
    # Clean text to prevent minor whitespace/formatting issues from blocking match
    clean_q = re.sub(r'\s+', '', q_bn)
    q_map[clean_q] = (pdf_file, pdf_page)

print(f"Loaded {len(q_map)} lookup questions from DB.")

# Read training data records
records = []
with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            records.append(json.loads(line))

print(f"Loaded {len(records)} records from training data.")

updated_count = 0
not_found = 0

for r in records:
    # Parse question from input
    inp = r["input"]
    q_match = re.search(r"Question:\s*(.*?)\n", inp)
    if q_match:
        q_text = q_match.group(1).strip()
        clean_q = re.sub(r'\s+', '', q_text)
        
        if clean_q in q_map:
            pdf_file, pdf_page = q_map[clean_q]
            if pdf_file and pdf_page:
                try:
                    out = json.loads(r["output"])
                    
                    # Construct specific reference based on mapped file and page
                    if "ABUL_HASAN" in pdf_file:
                        ref_str = f"আবুল হাসান স্যার, ১ম পত্র, পৃষ্ঠা {pdf_page}"
                    elif "Azmol" in pdf_file:
                        ref_str = f"গাজী আজমল স্যার, ২য় পত্র, পৃষ্ঠা {pdf_page}"
                    else:
                        ref_str = f"জীববিজ্ঞান, পৃষ্ঠা {pdf_page}"
                        
                    out["textbook_ref"] = ref_str
                    
                    r["output"] = json.dumps(out, ensure_ascii=False)
                    updated_count += 1
                except Exception as e:
                    pass
        else:
            not_found += 1

print(f"Enriched {updated_count} records with exact page numbers. ({not_found} questions not found in DB lookup)")

# Save back to the file
with open(input_file, 'w', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print("Successfully saved enriched training data!")
conn.close()
