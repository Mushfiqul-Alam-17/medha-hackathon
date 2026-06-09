import sqlite3
import json

conn = sqlite3.connect(r'c:\Users\mushf\Downloads\Medha\app\backend\medha.db')
c = conn.cursor()
c.execute('SELECT id, question_bn, correct, option_a_bn, option_b_bn, option_c_bn, option_d_bn, pdf_file, pdf_page FROM questions')
rows = c.fetchall()

matches = []
for r in rows:
    q_bn = r[1]
    if "গাঠনিক" in q_bn or "কোলাজেন" in q_bn or "প্রোটিন" in q_bn:
        matches.append({
            "id": r[0],
            "question": r[1],
            "correct": r[2],
            "options": [r[3], r[4], r[5], r[6]],
            "pdf_file": r[7],
            "pdf_page": r[8]
        })

with open("matches.json", "w", encoding="utf-8") as f:
    json.dump(matches, f, ensure_ascii=False, indent=2)

print(f"Done! Found {len(matches)} matches. Saved to matches.json.")
conn.close()
