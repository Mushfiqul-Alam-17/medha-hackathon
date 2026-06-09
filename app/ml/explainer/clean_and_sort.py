import json
import os
from collections import defaultdict

input_file = "data/explainer_training_data.jsonl"
output_file = "data/explainer_training_data_sorted.jsonl"

valid_records = []
invalid_count = 0

# 1. Read and validate all lines
with open(input_file, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        line = line.strip()
        if not line:
            continue
            
        try:
            # Check if outer line is valid JSON
            data = json.loads(line)
            
            # Check if the inner 'output' string is valid JSON
            inner_json = json.loads(data['output'])
            
            # Ensure it has all required fields
            required_keys = ["explanation", "why_wrong", "memory_trick", "textbook_ref"]
            if all(k in inner_json for k in required_keys):
                valid_records.append(data)
            else:
                print(f"Line {i+1} missing required keys.")
                invalid_count += 1
                
        except json.JSONDecodeError as e:
            print(f"Line {i+1} is invalid JSON: {e}")
            invalid_count += 1

print(f"Found {len(valid_records)} completely valid records. Dropped {invalid_count} invalid ones.")

# 2. Group by Question so they are pairwise serially adjacent
# The 'input' string starts with "Question: <question_text>\n"
grouped_records = defaultdict(list)
for record in valid_records:
    # Extract just the question text to group by
    first_line = record['input'].split('\n')[0]
    grouped_records[first_line].append(record)

# 3. Write sorted records back to file
with open(output_file, 'w', encoding='utf-8') as f:
    for question, records in grouped_records.items():
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"Cleaned and sorted dataset saved to {output_file}")

# Replace original file with sorted
os.replace(output_file, input_file)
print("Original file replaced.")
