import json

questions = []
with open(r'c:\Users\mushf\Downloads\Medha\app\backend\data\questions_clean.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        questions.append(json.loads(line))

existing_inputs = set()
with open('data/explainer_training_data.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            existing_inputs.add(json.loads(line)['input'])

# Find the missing one
missing_prompts = []
missing_q = None
missing_wrong_letter = None
missing_state = None

for i, q in enumerate(questions):
    wrong_options = [k for k, v in q['options'].items() if k != q['correct']]
    for idx, wrong_letter in enumerate(wrong_options[:2]):
        state = "PRIORITY_FOCUS" if idx == 0 else "GROWTH_AREA"
        
        # This formatting must exactly match format_input() from generate_training_data.py
        input_str = f"Question: {q['question_bn']}\nStudent answered: {q['options'][wrong_letter]['bn']} (Wrong)\nCorrect answer: {q['options'][q['correct']]['bn']}\nBehavioral state: {state}\nChapter: {q['chapter_name_bn']}\n"
        
        if input_str not in existing_inputs:
            missing_prompts.append((q, wrong_letter, state, input_str))

for mp in missing_prompts:
    print(f"MISSING: {mp[3].splitlines()[0]}")
    print(f"Wrong Answer: {mp[0]['options'][mp[1]]['bn']}")
    
print(f"Total missing: {len(missing_prompts)}")
