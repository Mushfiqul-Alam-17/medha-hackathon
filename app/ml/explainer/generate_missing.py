"""
Generate missing training records using round-robin Groq API clients.
Reads missing_inputs.json, generates outputs, appends to explainer_training_data.jsonl.
"""
import json, os, sys, time, re, requests
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

backend_dir = Path(r"c:\Users\mushf\Downloads\Medha\app\backend")
load_dotenv(backend_dir / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Multiple Groq keys for round-robin
GROQ_KEYS = []
if GROQ_API_KEY:
    GROQ_KEYS.append(("Groq-env", GROQ_API_KEY))

GROQ_MODELS = ["llama-3.3-70b-versatile", "meta-llama/llama-4-scout-17b-16e-instruct"]

# Build client list
CLIENTS = []
for key_name, key_val in GROQ_KEYS:
    for model in GROQ_MODELS:
        CLIENTS.append({"name": f"{key_name}/{model.split('/')[-1]}", "key": key_val, "model": model})

current_idx = 0
print(f"Configured {len(CLIENTS)} Groq clients for round-robin", flush=True)

# Load missing records  
missing_path = r"c:\Users\mushf\Downloads\Medha\app\ml\explainer\data\missing_inputs.json"
with open(missing_path, 'r', encoding='utf-8') as f:
    missing = json.loads(f.read())

# Check what's already in the file (in case of restart)
output_path = r"c:\Users\mushf\Downloads\Medha\app\ml\explainer\data\explainer_training_data.jsonl"
existing_inputs = set()
with open(output_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            r = json.loads(line.strip())
            existing_inputs.add(r['input'])

already_done = sum(1 for m in missing if m['input'] in existing_inputs)
remaining = [m for m in missing if m['input'] not in existing_inputs]
print(f"Missing records: {len(missing)}, Already done: {already_done}, Remaining: {len(remaining)}", flush=True)

# Page refs from DB
import sqlite3
conn = sqlite3.connect(str(backend_dir / "medha.db"))
cur = conn.cursor()
cur.execute("SELECT question_bn, pdf_page FROM questions")
q_pages = {row[0]: row[1] for row in cur.fetchall() if row[1]}
conn.close()

botany_chapters = ["কোষ ও কোষ অঙ্গাণু", "উদ্ভিদবিজ্ঞান ও শ্রেণীবিন্যাস", "জীবপ্রযুক্তি", 
                   "উদ্ভিদ শরীরতত্ত্ব", "কোষ রসায়ন", "কোষ বিভাজন", "অণুজীব ও ভাইরাস"]

def get_ref(q_bn, chapter):
    tb = "আবুল হাসান স্যার, ১ম পত্র" if any(b in chapter for b in botany_chapters) else "গাজী আজমল স্যার, ২য় পত্র"
    page = q_pages.get(q_bn)
    return f"{tb}, পৃষ্ঠা {page}" if page else tb

def call_groq(prompt, key, model):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.4, "max_tokens": 500}
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    if r.status_code == 200:
        text = r.json()['choices'][0]['message']['content'].strip()
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        return text.strip()
    elif r.status_code == 429:
        raise Exception(f"429 Rate limited")
    else:
        raise Exception(f"HTTP {r.status_code}: {r.text[:200]}")

def generate_one(record):
    global current_idx
    ref = get_ref(record['q_bn'], record['chapter'])
    
    if record['is_correct']:
        prompt = f"""Generate tutoring JSON for a Bangladeshi student's CORRECT answer.
Q: {record['q_bn']}
Student: {record['student_ans']} (Correct)
Chapter: {record['chapter']}
State: {record['state']}

Output ONLY raw JSON:
{{"explanation": "2 sentences Bengali, why correct + reinforce concept", "why_wrong": "1 sentence common trap or 'None'", "memory_trick": "max 8 Bengali words mnemonic", "textbook_ref": "{ref}"}}
Rules: 100% biologically accurate Bengali. No markdown."""
    else:
        prompt = f"""Generate tutoring JSON for a Bangladeshi student's WRONG answer.
Q: {record['q_bn']}
Student: {record['student_ans']}
Correct: {record['correct_ans']}
Chapter: {record['chapter']}
State: {record['state']}

Output ONLY raw JSON:
{{"explanation": "2 sentences Bengali, why correct is right + why wrong is wrong", "why_wrong": "1 sentence the biological misconception", "memory_trick": "max 8 Bengali words mnemonic", "textbook_ref": "{ref}"}}
Rules: 100% biologically accurate Bengali. No markdown."""

    for attempt in range(len(CLIENTS)):
        client = CLIENTS[current_idx % len(CLIENTS)]
        current_idx += 1
        try:
            raw = call_groq(prompt, client['key'], client['model'])
            result = json.loads(raw)
            result['textbook_ref'] = ref
            return json.dumps(result, ensure_ascii=False), client['name']
        except Exception as e:
            err = str(e)
            if "429" in err:
                time.sleep(2)
                continue
            else:
                time.sleep(1)
                continue
    return None, None

# Generate
generated = 0
failed = 0

with open(output_path, 'a', encoding='utf-8') as f:
    for i, record in enumerate(remaining):
        q_short = record['q_bn'][:40]
        output, client_name = generate_one(record)
        if output:
            data = {"input": record['input'], "output": output}
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
            f.flush()
            generated += 1
            if (i+1) % 20 == 0:
                print(f"[{i+1}/{len(remaining)}] ✅ via {client_name} | Q: {q_short}...", flush=True)
        else:
            failed += 1
            print(f"[{i+1}/{len(remaining)}] ❌ FAILED | Q: {q_short}...", flush=True)
        
        time.sleep(0.5)  # Rate limiting

print(f"\n{'='*50}", flush=True)
print(f"COMPLETE!", flush=True)
print(f"  Generated: {generated}", flush=True)
print(f"  Failed: {failed}", flush=True)

# Final verify
with open(output_path, 'r', encoding='utf-8') as f:
    total = sum(1 for l in f if l.strip())
print(f"  Total records in file: {total}", flush=True)
