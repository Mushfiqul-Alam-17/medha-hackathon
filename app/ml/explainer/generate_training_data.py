"""
MEDHA — Explainer Training Data Generator (V2) - GROQ VERSION
Generates targeted training data for Qwen2.5-3B fine-tuning using Groq API.
This creates (Input, Output) pairs for the explanation generator model.
"""

import json
import os
import sys
import time
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

# Load API key from .env
backend_dir = Path(__file__).parent.parent.parent / "backend"
load_dotenv(backend_dir / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("ERROR: GROQ_API_KEY not found in .env", flush=True)
    exit(1)

client = Groq(api_key=GROQ_API_KEY)

# Load questions
questions_file = backend_dir / "data" / "questions_clean.jsonl"
questions = []
with open(questions_file, 'r', encoding='utf-8') as f:
    for line in f:
        questions.append(json.loads(line.strip()))

def format_input(q, wrong_letter, behavior_state):
    return f"""Question: {q['question_bn']}
Student answered: {q['options'][wrong_letter]['bn']} (Wrong)
Correct answer: {q['options'][q['correct']]['bn']}
Behavioral state: {behavior_state}
Chapter: {q['chapter_name_bn']}
"""

def generate_example(q, wrong_letter, behavior_state):
    correct_ans = q['options'][q['correct']]['bn']
    wrong_ans = q['options'][wrong_letter]['bn']
    
    prompt = f"""
You are creating training data for MEDHA, a medical exam tutoring AI for Bangladesh students.
Generate a JSON response for a student who answered this question WRONG.

Question (Bengali): {q['question_bn']}
Student's wrong answer: {wrong_ans}  
Correct answer: {correct_ans}
Chapter: {q['chapter_name_bn']}
Behavioral State: {behavior_state}

Generate ONLY valid JSON in this exact format:
{{
  "explanation": "2 sentences in Bengali: why correct answer is right + why wrong answer is wrong",
  "why_wrong": "1 sentence in Bengali: the specific misconception that causes this mistake",
  "memory_trick": "1 memorable trick in Bengali or simple English: mnemonic, rhyme, or visual",
  "textbook_ref": "Chapter name and approximate location in NCTB textbook"
}}

Rules:
- Write Bengali in Unicode Bengali script
- Be specific to THIS question, not generic
- Memory trick must be truly memorable, not just a repetition
- If Behavioral State is PRIORITY_FOCUS (confidently wrong), be direct.
- If Behavioral State is GROWTH_AREA (unsure), be encouraging.
- ONLY OUTPUT THE JSON BLOCK. NO OTHER TEXT.
"""
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.5,
        )
        raw = response.choices[0].message.content.strip()
        # Clean markdown if present
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        return json.loads(raw.strip())
    except Exception as e:
        print(f"Failed to generate for question {q['id']}: {e}", flush=True)
        return None

def run():
    out_dir = Path(__file__).parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "explainer_training_data.jsonl"
    
    # Check existing progress
    existing_combinations = set()
    if out_file.exists():
        with open(out_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    existing_combinations.add(data['input'])
                    
    print(f"Found {len(existing_combinations)} existing valid examples.", flush=True)
    print(f"Generating missing training data using Groq API...", flush=True)
    
    count = 0
    missing = 0
    
    with open(out_file, 'a', encoding='utf-8') as f:
        for i, q in enumerate(questions):
            # Identify the two most likely wrong answers
            # In a real system, we'd use analytics. Here we just pick the first two wrong options.
            wrong_options = [k for k, v in q['options'].items() if k != q['correct']]
            
            for idx, wrong_letter in enumerate(wrong_options[:2]):
                state = "PRIORITY_FOCUS" if idx == 0 else "GROWTH_AREA"
                
                input_str = format_input(q, wrong_letter, state)
                
                # Skip if already generated successfully
                if input_str in existing_combinations:
                    continue
                    
                missing += 1
                print(f"Generating missing variant for Q{i+1}/{len(questions)} - Variant {idx+1}", flush=True)
                
                # Try up to 3 times to get valid JSON
                example = None
                for attempt in range(3):
                    example = generate_example(q, wrong_letter, state)
                    if example:
                        break
                    print(f"Attempt {attempt+1} failed, retrying...", flush=True)
                    time.sleep(1)
                
                if example:
                    data = {
                        "input": input_str,
                        "output": json.dumps(example, ensure_ascii=False)
                    }
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")
                    f.flush()  # Force write to disk immediately
                    existing_combinations.add(input_str)
                else:
                    print(f"Failed to generate valid JSON for Q{i+1} after 3 attempts.", flush=True)
                    
                # Small delay to respect rate limits
                time.sleep(0.5)

    print(f"Done! Finished generating {missing} missing examples. Total is now {len(existing_combinations)}.", flush=True)

if __name__ == "__main__":
    run()
