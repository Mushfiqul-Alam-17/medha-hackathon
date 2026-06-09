import json
import os

questions = []
with open(r'c:\Users\mushf\Downloads\Medha\app\backend\data\questions_clean.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        questions.append(json.loads(line))

total_questions = len(questions)
unique_questions = len(set([q['question_bn'] for q in questions]))

inputs = set()
for q in questions:
    wrong_options = [k for k in q['options'].keys() if k != q['correct']]
    for k in wrong_options[:2]:
        inputs.add(f"{q['question_bn']} - {k}")

print(f"Total questions in file: {total_questions}")
print(f"Unique questions (by question_bn): {unique_questions}")
print(f"Total unique input combinations (Question + Wrong Option): {len(inputs)}")
