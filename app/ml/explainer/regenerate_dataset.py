import json
import os
import sys
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# Force stdout to UTF-8 to prevent console encoding crashes on Windows
sys.stdout.reconfigure(encoding='utf-8')

# Paths
ml_explainer_dir = Path(__file__).parent
backend_dir = ml_explainer_dir.parent.parent / "backend"
load_dotenv(backend_dir / ".env")

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Round-robin list of LLM clients
CLIENTS = []

# 1. Direct Gemini API (Primary high-quality model, 20 RPM, 20 RPD)
if GEMINI_API_KEY:
    CLIENTS.append({
        "name": "Gemini-Free",
        "type": "gemini",
        "key": GEMINI_API_KEY,
        "model": "gemini-2.5-flash-lite"
    })

# 2. Direct Groq High-Quality APIs (Secondary high-quality models)
# We configure multiple high-quality models to rotate limits and stay within TPD limits
groq_keys = []
if GROQ_API_KEY:
    groq_keys.append(("Groq-Old", GROQ_API_KEY))

groq_models = [
    "llama-3.3-70b-versatile",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b"
]

for key_name, key_val in groq_keys:
    for model in groq_models:
        model_alias = model.split("/")[-1]
        CLIENTS.append({
            "name": f"{key_name}-{model_alias}",
            "type": "groq",
            "key": key_val,
            "model": model
        })

if not CLIENTS:
    print("ERROR: No API keys configured.", flush=True)
    sys.exit(1)

print(f"Configured {len(CLIENTS)} active high-quality clients for rotation.", flush=True)

input_file = ml_explainer_dir / "data" / "explainer_training_data.jsonl"
temp_file = ml_explainer_dir / "data" / "explainer_training_data_temp.jsonl"
backup_file = ml_explainer_dir / "data" / "explainer_training_data_backup.jsonl"

def get_textbook_hint(chapter):
    # Botany chapters in Bangladesh curriculum
    botany_chapters = ["কোষ ও কোষ অঙ্গাণু", "উদ্ভিদবিজ্ঞান ও শ্রেণীবিন্যাস", "জীবপ্রযুক্তি", "উদ্ভিদ শরীরতত্ত্ব", "কোষ রসায়ন", "কোষ বিভাজন", "অণুজীব ও ভাইরাস"]
    if any(bot in chapter for bot in botany_chapters):
        return "অধ্যাপক আবুল হাসান স্যারের জীববিজ্ঞান ১ম পত্র (উদ্ভিদবিজ্ঞান)"
    else:
        return "গাজী আজমল স্যারের জীববিজ্ঞান ২য় পত্র (প্রাণীবিজ্ঞান)"

def parse_input(input_str):
    lines = input_str.strip().split('\n')
    q_bn = ""
    wrong_ans = ""
    correct_ans = ""
    state = ""
    chapter = ""
    is_correct = False
    for line in lines:
        if line.startswith("Question:"):
            q_bn = line[len("Question:"):].strip()
        elif line.startswith("Student answered:"):
            ans_part = line[len("Student answered:"):].strip()
            if ans_part.endswith("(Wrong)"):
                wrong_ans = ans_part[:-7].strip()
                is_correct = False
            elif ans_part.endswith("(Correct)"):
                wrong_ans = ans_part[:-9].strip()
                is_correct = True
            else:
                wrong_ans = ans_part
                is_correct = False
        elif line.startswith("Correct answer:"):
            correct_ans = line[len("Correct answer:"):].strip()
        elif line.startswith("Behavioral state:"):
            state = line[len("Behavioral state:"):].strip()
        elif line.startswith("Chapter:"):
            chapter = line[len("Chapter:"):].strip()
    return q_bn, wrong_ans, correct_ans, state, chapter, is_correct

def clean_json_content(content):
    content = content.strip()
    # Strip reasoning/thinking blocks if present (e.g. from reasoning models)
    if "<think>" in content:
        parts = content.split("</think>")
        if len(parts) > 1:
            content = parts[1].strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()

# Current index for round-robin rotation
current_client_idx = 0

def call_client(client, prompt):
    ctype = client["type"]
    ckey = client["key"]
    cmodel = client["model"]
    cname = client["name"]
    
    if ctype == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{cmodel}:generateContent?key={ckey}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 600,
                "temperature": 0.2
            }
        }
        r = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=20)
        if r.status_code == 200:
            res_data = r.json()
            return clean_json_content(res_data["candidates"][0]["content"]["parts"][0]["text"])
        else:
            raise Exception(f"Google Gemini HTTP {r.status_code}: {r.text}")
            
    elif ctype == "groq":
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {ckey}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": cmodel,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        if r.status_code == 200:
            return clean_json_content(r.json()["choices"][0]["message"]["content"])
        else:
            raise Exception(f"Groq HTTP {r.status_code}: {r.text}")
            
    elif ctype == "openrouter":
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {ckey}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Mushfiqul-Alam-17/medha-hackathon",
            "X-Title": "Medha"
        }
        req_max_tokens = 220
        for attempt in range(3):
            payload = {
                "model": cmodel,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": req_max_tokens,
                "temperature": 0.2
            }
            r = requests.post(url, headers=headers, json=payload, timeout=20)
            if r.status_code == 200:
                return clean_json_content(r.json()["choices"][0]["message"]["content"])
            elif r.status_code == 402:
                err_msg = r.text
                import re
                match = re.search(r"can only afford (\d+)", err_msg)
                if match:
                    affordable = int(match.group(1))
                    if affordable >= 100:
                        new_max = affordable - 5
                        print(f"  [OpenRouter] Wallet low balance. Requested {req_max_tokens}, can afford {affordable}. Retrying with max_tokens={new_max}...", flush=True)
                        req_max_tokens = new_max
                        continue
                raise Exception(f"OpenRouter HTTP 402: {err_msg}")
            else:
                raise Exception(f"OpenRouter HTTP {r.status_code}: {r.text}")

def generate_correct_output(q_bn, student_ans, correct_ans, state, chapter, is_correct):
    global current_client_idx
    textbook_hint = get_textbook_hint(chapter)
    
    if is_correct:
        prompt = f"""
Generate tutoring JSON for a Bangladeshi student's CORRECT answer.
Q: {q_bn}
Student's: {student_ans} (Correct)
Chapter: {chapter}
State: {state} (MASTERY = fast/confident, TRUST_GAP = slow/unsure, needs reassurance)

Output JSON format:
{{
  "explanation": "2 sentences in Bengali (max 15 words/sent): 1st confirms why the answer is correct, 2nd reinforces the core concept.",
  "why_wrong": "1 concise sentence in Bengali (max 15 words) on a common trap/distractor, or 'None'.",
  "memory_trick": "1 short trick strictly in Bengali script (max 8 words): mnemonic, rhyme, or association (no English sentences/words).",
  "textbook_ref": "Realistic reference to standard Bangladeshi HSC Biology textbook (max 8 words). Example: {textbook_hint}."
}}

Rules:
- 100% biologically accurate, natural academic Bengali script.
- Transliterate scientific terms in memory_trick to Bengali (e.g., 'গলগি বডি' not 'Golgi Body').
- ONLY output raw JSON. No markdown, no extra text.
"""
    else:
        prompt = f"""
Generate tutoring JSON for a Bangladeshi student's WRONG answer.
Q: {q_bn}
Student's: {student_ans}
Correct: {correct_ans}
Chapter: {chapter}
State: {state}

Output JSON format:
{{
  "explanation": "2 sentences in Bengali (max 15 words/sent): 1st explains why correct is right, 2nd explains why wrong is wrong.",
  "why_wrong": "1 concise sentence in Bengali (max 15 words) explaining the biological misconception or why they are confused (do NOT use robotic templates like 'ছাত্র বুঝতে ভুল করেছে' or 'বিভ্রান্ত হয়েছে').",
  "memory_trick": "1 short trick strictly in Bengali script (max 8 words): mnemonic, rhyme, or association (no English sentences/words).",
  "textbook_ref": "Realistic reference to standard Bangladeshi HSC Biology textbook (max 8 words). Example: {textbook_hint}."
}}

Rules:
- 100% biologically accurate, natural academic Bengali script.
- Transliterate scientific terms in memory_trick to Bengali (e.g., 'গলগি বডি' not 'Golgi Body').
- ONLY output raw JSON. No markdown, no extra text.
"""
    
    # Try clients round-robin, cycling upon failures
    num_clients = len(CLIENTS)
    for retry_attempt in range(num_clients * 2):  # Try up to twice for each client in the rotation list
        if not CLIENTS:
            break
        client = CLIENTS[current_client_idx]
        cname = client["name"]
        
        try:
            output_content = call_client(client, prompt)
            json.loads(output_content)  # Verify valid JSON
            
            # Rotate index to the next client for the next request
            current_client_idx = (current_client_idx + 1) % num_clients
            return output_content, cname
            
        except Exception as e:
            err_str = str(e)
            is_429 = "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "Rate limit" in err_str or "quota" in err_str.lower()
            is_402 = "402" in err_str or "credits" in err_str.lower() or "afford" in err_str.lower()
            
            # Determine if this error is persistent (daily quota / credit exhaust) or temporary (per-minute limits)
            is_persistent = False
            if is_402:
                is_persistent = True
            elif is_429:
                if client["type"] == "gemini":
                    err_lower = err_str.lower()
                    if "day" in err_lower or "daily" in err_lower or "requestsperday" in err_lower:
                        is_persistent = True
                    else:
                        is_persistent = False
                else:
                    err_lower = err_str.lower()
                    # Check for minute limits vs daily/tpd/rpd limits
                    if "tpm" in err_lower or "rpm" in err_lower or "tokens per minute" in err_lower or "requests per minute" in err_lower:
                        is_persistent = False
                    else:
                        is_persistent = True
            
            if is_persistent:
                print(f"  Client {cname} failed with persistent error (Quota/RateLimit/Credits): {e}. Removing from active rotation permanently.", flush=True)
                CLIENTS.remove(client)
                if not CLIENTS:
                    print("ERROR: No working LLM clients remaining!", flush=True)
                    sys.exit(1)
                num_clients = len(CLIENTS)
                current_client_idx = current_client_idx % num_clients
                continue
            
            sleep_time = 15.0 if is_429 else 2.0
            print(f"  Client {cname} failed: {e}. Sleeping {sleep_time}s and switching client...", flush=True)
            
            # Rotate index to the next client for the next request
            current_client_idx = (current_client_idx + 1) % num_clients
            time.sleep(sleep_time)  # Pause before retry
            
    return None, None


import re

def is_valid_trick(trick):
    # Reject English phrases (two or more English words separated by space/hyphen/quotes)
    if re.search(r'[a-zA-Z]{2,}[\s\-\'\"]+[a-zA-Z]{2,}', trick):
        return False
    return True

def run():
    questions_file = backend_dir / "data" / "questions_clean.jsonl"
    if not questions_file.exists():
        print(f"ERROR: Questions file {questions_file} does not exist.")
        sys.exit(1)
        
    # Read questions
    questions = []
    with open(questions_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line))
                
    # Generate the target inputs:
    # 4 wrong variants + 2 correct variants per question
    raw_target_records = []
    for q in questions:
        wrong_options = [k for k, v in q['options'].items() if k != q['correct']]
        if len(wrong_options) < 3:
            # Fallback if a question doesn't have 4 options
            w0 = wrong_options[0] if len(wrong_options) > 0 else q['correct']
            w1 = wrong_options[1] if len(wrong_options) > 1 else w0
            w2 = wrong_options[2] if len(wrong_options) > 2 else w1
        else:
            w0, w1, w2 = wrong_options[0], wrong_options[1], wrong_options[2]
            
        # 4 wrong variants
        wrong_variants = [
            (w0, "PRIORITY_FOCUS"),
            (w1, "GROWTH_AREA"),
            (w2, "PRIORITY_FOCUS"),
            (w0, "GROWTH_AREA")
        ]
        # 2 correct variants
        correct_variants = [
            (q['correct'], "MASTERY"),
            (q['correct'], "TRUST_GAP")
        ]
        
        # Combine them into a single list of 6 variants per question
        for wrong_letter, state in wrong_variants:
            inp = f"Question: {q['question_bn']}\nStudent answered: {q['options'][wrong_letter]['bn']} (Wrong)\nCorrect answer: {q['options'][q['correct']]['bn']}\nBehavioral state: {state}\nChapter: {q['chapter_name_bn']}\n"
            raw_target_records.append({
                "input": inp,
                "q_bn": q['question_bn'],
                "wrong_ans": q['options'][wrong_letter]['bn'],
                "correct_ans": q['options'][q['correct']]['bn'],
                "state": state,
                "chapter": q['chapter_name_bn'],
                "is_correct": False
            })
            
        for correct_letter, state in correct_variants:
            inp = f"Question: {q['question_bn']}\nStudent answered: {q['options'][correct_letter]['bn']} (Correct)\nCorrect answer: {q['options'][q['correct']]['bn']}\nBehavioral state: {state}\nChapter: {q['chapter_name_bn']}\n"
            raw_target_records.append({
                "input": inp,
                "q_bn": q['question_bn'],
                "wrong_ans": q['options'][correct_letter]['bn'],
                "correct_ans": q['options'][q['correct']]['bn'],
                "state": state,
                "chapter": q['chapter_name_bn'],
                "is_correct": True
            })
            
    # Deduplicate target records based on their normalized input
    target_records = []
    seen_inputs = set()
    for record in raw_target_records:
        norm_inp = record['input'].strip().replace('\r\n', '\n')
        if norm_inp not in seen_inputs:
            seen_inputs.add(norm_inp)
            target_records.append(record)
            
    total_records = len(target_records)
    print(f"Generated {total_records} unique target inputs (from {len(raw_target_records)} raw variants) from questions_clean.jsonl.", flush=True)
    
    # Load already completed valid records from temp file only to ensure we only load cleaned high-quality records
    existing_cache = {}
    for p in [temp_file]:
        if p.exists():
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                record = json.loads(line)
                                inp_norm = record['input'].strip().replace('\r\n', '\n')
                                # Validate inner output JSON has all required keys
                                out_parsed = json.loads(record['output'])
                                required_keys = ["explanation", "why_wrong", "memory_trick", "textbook_ref"]
                                if all(k in out_parsed for k in required_keys):
                                    existing_cache[inp_norm] = record['output']
                            except Exception:
                                pass
            except Exception as e:
                print(f"Error reading cache file {p.name}: {e}", flush=True)
                
    print(f"Loaded {len(existing_cache)} unique valid cached records.", flush=True)
        
    # Overwrite the temp file and write all records in serial order
    with open(temp_file, 'w', encoding='utf-8') as f_out:
        for idx, record in enumerate(target_records):
            inp = record['input']
            normalized_inp = inp.strip().replace('\r\n', '\n')
            
            if normalized_inp in existing_cache:
                # Reuse!
                new_record = {
                    "input": inp,
                    "output": existing_cache[normalized_inp]
                }
                f_out.write(json.dumps(new_record, ensure_ascii=False) + "\n")
                f_out.flush()
                # Print progress occasionally
                if (idx + 1) % 50 == 0 or idx + 1 == total_records:
                    print(f"[{idx+1}/{total_records}] Restored from cache...", flush=True)
                continue
                
            # Otherwise, query!
            q_bn = record['q_bn']
            wrong_ans = record['wrong_ans']
            correct_ans = record['correct_ans']
            state = record['state']
            chapter = record['chapter']
            is_correct = record['is_correct']
            
            type_str = "Correct" if is_correct else "Wrong"
            print(f"[{idx+1}/{total_records}] Generating ({type_str}): Q: {q_bn[:40]}... (Answered: {wrong_ans}, Correct: {correct_ans})", flush=True)
            
            success = False
            client_sleep = 0.5
            for attempt in range(100):
                output_json, client_name = generate_correct_output(q_bn, wrong_ans, correct_ans, state, chapter, is_correct)
                if output_json:
                    try:
                        parsed = json.loads(output_json)
                        trick = parsed.get("memory_trick", "")
                        if is_valid_trick(trick):
                            new_record = {
                                "input": inp,
                                "output": output_json
                            }
                            f_out.write(json.dumps(new_record, ensure_ascii=False) + "\n")
                            f_out.flush()
                            existing_cache[normalized_inp] = output_json  # Add to in-memory cache immediately!
                            print(f" -> Success! (Client: {client_name})", flush=True)
                            success = True
                            client_sleep = 3.5 if client_name == "Gemini-Free" else 0.5
                            break
                        else:
                            print(f" -> WARNING: Invalid English memory trick detected ('{trick}'). Retrying with next client...", flush=True)
                            time.sleep(1.0)
                    except Exception as e:
                        print(f" -> WARNING: Failed to parse JSON ('{e}'). Retrying...", flush=True)
                        time.sleep(1.0)
                else:
                    print(f" -> WARNING: All clients failed. Sleeping for 45 seconds (Attempt {attempt+1}/100)...", flush=True)
                    time.sleep(45.0)
                    
            if not success:
                print(f" -> FAILED to generate valid response for record {idx+1} after 100 attempts. Stopping to prevent corruption.", flush=True)
                sys.exit(1)
                
            # Dynamic sleep to respect rate limits
            time.sleep(client_sleep)
            
    # Verify final count is exactly correct
    final_records = []
    with open(temp_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                final_records.append(json.loads(line))
                
    if len(final_records) == total_records:
        print(f"Regeneration complete! All {total_records} records processed successfully.", flush=True)
        # Create backup of the original file
        if input_file.exists():
            if backup_file.exists():
                os.remove(backup_file)
            os.rename(input_file, backup_file)
            print(f"Original file backed up to {backup_file}", flush=True)
            
        # Rename temp to original
        os.rename(temp_file, input_file)
        print(f"Regenerated file moved to {input_file}", flush=True)
    else:
        print(f"Warning: Count mismatch. Got {len(final_records)} records instead of {total_records}. Temp file is preserved at {temp_file}", flush=True)

if __name__ == "__main__":
    run()


