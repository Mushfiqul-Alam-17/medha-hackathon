import json
import os
import sys

def validate_classifier_data(filepath):
    print(f"\n--- Validating {os.path.basename(filepath)} ---")
    if not os.path.exists(filepath):
        print("❌ File not found!")
        return False
        
    valid_labels = {"MASTERY", "PRIORITY_FOCUS", "TRUST_GAP", "GROWTH_AREA"}
    valid_lines = 0
    errors = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            try:
                data = json.loads(line)
                if 'text' not in data or 'label' not in data:
                    print(f"Line {i+1}: Missing 'text' or 'label'")
                    errors += 1
                    continue
                if not isinstance(data['text'], str) or not data['text'].strip():
                    print(f"Line {i+1}: Invalid 'text' field")
                    errors += 1
                    continue
                if data['label'] not in valid_labels:
                    print(f"Line {i+1}: Invalid label '{data['label']}'")
                    errors += 1
                    continue
                valid_lines += 1
            except json.JSONDecodeError:
                print(f"Line {i+1}: Invalid JSON")
                errors += 1

    print(f"✅ Valid lines: {valid_lines}")
    if errors > 0:
        print(f"❌ Errors found: {errors}")
        return False
    else:
        print(f"✅ No errors found!")
        return True

def validate_explainer_data(filepath):
    print(f"\n--- Validating {os.path.basename(filepath)} ---")
    if not os.path.exists(filepath):
        print("❌ File not found!")
        return False
        
    valid_lines = 0
    errors = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            try:
                data = json.loads(line)
                if 'input' not in data or 'output' not in data:
                    if errors < 5: print(f"Line {i+1}: Missing 'input' or 'output'")
                    errors += 1
                    continue
                
                # Check input format roughly
                inp = data['input']
                if "Question:" not in inp or "Behavioral state:" not in inp:
                    if errors < 5: print(f"Line {i+1}: Invalid 'input' format")
                    errors += 1
                    continue
                
                # Check output format (should be valid JSON string)
                out = data['output']
                try:
                    out_json = json.loads(out)
                    required_keys = {"explanation", "why_wrong", "memory_trick", "textbook_ref"}
                    if not required_keys.issubset(out_json.keys()):
                        if errors < 5: print(f"Line {i+1}: 'output' JSON missing required keys. Found: {list(out_json.keys())}")
                        errors += 1
                        continue
                except json.JSONDecodeError:
                    if errors < 5: print(f"Line {i+1}: 'output' is not a valid JSON string")
                    errors += 1
                    continue
                    
                valid_lines += 1
            except json.JSONDecodeError:
                if errors < 5: print(f"Line {i+1}: Invalid JSON on line")
                errors += 1

    print(f"✅ Valid lines: {valid_lines}")
    if errors > 0:
        print(f"❌ Errors found: {errors}")
        if errors > 5: print(f"... and {errors - 5} more errors.")
        return False
    else:
        print(f"✅ No errors found!")
        return True

if __name__ == "__main__":
    base_dir = r"c:\Users\mushf\Downloads\Medha\app\ml\kaggle_dataset"
    c_train = os.path.join(base_dir, "classifier_train.jsonl")
    c_val = os.path.join(base_dir, "classifier_val.jsonl")
    e_train = os.path.join(base_dir, "explainer_training_data.jsonl")
    
    sys.stdout.reconfigure(encoding='utf-8')
    
    res1 = validate_classifier_data(c_train)
    res2 = validate_classifier_data(c_val)
    res3 = validate_explainer_data(e_train)
    
    if res1 and res2 and res3:
        print("\n🏆 ALL FILES ARE 100% VALID AND READY FOR TRAINING!")
    else:
        print("\n🚨 SOME FILES HAVE ERRORS! Fix them before training.")
