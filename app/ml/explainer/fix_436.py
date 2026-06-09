import json

# Load questions
questions = []
with open(r'c:\Users\mushf\Downloads\Medha\app\backend\data\questions_clean.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        questions.append(json.loads(line))

# Load existing outputs into a list (so we can count duplicates)
existing_records = []
with open('data/explainer_training_data.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            existing_records.append(json.loads(line))

# Count occurrences of each input string
input_counts = {}
for record in existing_records:
    inp = record['input']
    input_counts[inp] = input_counts.get(inp, 0) + 1

missing_records_to_add = []

# Verify 436 instances
for i, q in enumerate(questions):
    wrong_options = [k for k, v in q['options'].items() if k != q['correct']]
    for idx, wrong_letter in enumerate(wrong_options[:2]):
        state = "PRIORITY_FOCUS" if idx == 0 else "GROWTH_AREA"
        input_str = f"Question: {q['question_bn']}\nStudent answered: {q['options'][wrong_letter]['bn']} (Wrong)\nCorrect answer: {q['options'][q['correct']]['bn']}\nBehavioral state: {state}\nChapter: {q['chapter_name_bn']}\n"
        
        # Check if we have enough of this input string
        if input_counts.get(input_str, 0) > 0:
            input_counts[input_str] -= 1
        else:
            # We need to add one more of this exact duplicate!
            # Let's find one of the existing records that matches this input_str to copy its output
            matching_record = next((r for r in existing_records if r['input'] == input_str), None)
            if matching_record:
                missing_records_to_add.append(matching_record)

print(f"Need to duplicate {len(missing_records_to_add)} records to reach 436.")

with open('data/explainer_training_data.jsonl', 'a', encoding='utf-8') as f:
    for r in missing_records_to_add:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print("Done appending the duplicate to reach 436.")
