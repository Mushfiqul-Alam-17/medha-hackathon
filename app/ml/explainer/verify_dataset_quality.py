import json
import re
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"c:\Users\mushf\Downloads\Medha\app\ml\explainer\data\explainer_training_data.jsonl"
if not os.path.exists(file_path):
    print("Dataset file not found.")
    exit(1)

records = []
with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            records.append(json.loads(line))

print(f"Loaded {len(records)} records.")

errors = 0
english_tricks = 0
invalid_json = 0

for idx, r in enumerate(records):
    # Check JSON output parsing
    try:
        out = json.loads(r["output"])
    except Exception as e:
        invalid_json += 1
        errors += 1
        print(f"Record {idx+1}: Invalid JSON output: {e}")
        continue
        
    # Check memory trick english words
    trick = out.get("memory_trick", "")
    # Check if there are 2 or more consecutive english words (separated by spaces or hyphens)
    if re.search(r'[a-zA-Z]{2,}[\s\-\'\"]+[a-zA-Z]{2,}', trick):
        english_tricks += 1
        errors += 1
        print(f"Record {idx+1}: English memory trick leak: '{trick}'")
        
    # Check explanation english sentences
    explanation = out.get("explanation", "")
    if re.search(r'[a-zA-Z]{3,}\s+[a-zA-Z]{3,}\s+[a-zA-Z]{3,}', explanation):
         print(f"Record {idx+1}: Possible English explanation leak: '{explanation}'")
         errors += 1

print("\n--- REPORT ---")
print(f"Total Records: {len(records)}")
print(f"Invalid JSON: {invalid_json}")
print(f"English Memory Tricks Leaked: {english_tricks}")
print(f"Total Errors Found: {errors}")

if errors == 0:
    print("[SUCCESS] Dataset quality check passed perfectly! No English leaks or formatting issues.")
else:
    print("[WARNING] Dataset quality issues found. Please review the reports above.")
