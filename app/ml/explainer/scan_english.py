"""Scan questions_clean.jsonl for questions with English-only bn options."""
import sys, json, re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

backend_dir = Path(__file__).parent.parent.parent / "backend"
f = open(backend_dir / "data" / "questions_clean.jsonl", 'r', encoding='utf-8')
lines = f.readlines()
f.close()

eng_questions = []
for l in lines:
    if not l.strip(): continue
    q = json.loads(l.strip())
    has_eng = False
    for k, v in q['options'].items():
        bn = v['bn'].strip()
        # Check if bn text is purely ASCII/English (no Bengali Unicode)
        if re.match(r'^[A-Za-z\s\-\(\)\d\.\,\^\+\/\:\;\*\[\]\'\"]+$', bn):
            has_eng = True
            break
    if has_eng:
        eng_questions.append(q)

print(f"Total questions: {len(lines)}")
print(f"Questions with at least one English-only bn option: {len(eng_questions)}")
print()

# Print samples
for q in eng_questions[:20]:
    opts = {k: v['bn'] for k, v in q['options'].items()}
    print(f"  {q['id']}: {q['question_bn'][:60]}")
    print(f"    Options: {opts}")
    print(f"    Correct: {q['correct']} = {q['options'][q['correct']]['bn']}")
    print()
