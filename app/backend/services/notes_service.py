"""
MEDHA — Notes Service (AI-Powered)
Assembles personalized study notes by querying the custom Qwen2.5-3B model
deployed on Hugging Face.
"""

from typing import Dict, List, Any
import requests
import json
import time
import os
import concurrent.futures
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from app/backend/.env
load_dotenv(Path(__file__).parent.parent / ".env")

FALLBACK_MAP = {}
try:
    explainer_path = Path(__file__).parent.parent.parent / "ml" / "kaggle_dataset" / "explainer_training_data.jsonl"
    if explainer_path.exists():
        with open(explainer_path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= 222:
                    break
                if not line.strip():
                    continue
                data = json.loads(line)
                
                # Parse input field to extract Question and Behavioral state
                q_bn = ""
                state = ""
                for part in data["input"].split("\n"):
                    if part.startswith("Question:"):
                        q_bn = part[len("Question:"):].strip()
                    elif part.startswith("Behavioral state:"):
                        state = part[len("Behavioral state:"):].strip()
                
                if q_bn and state:
                    try:
                        out_data = json.loads(data["output"])
                        FALLBACK_MAP[(q_bn, state)] = {
                            "explanation": out_data.get("explanation", ""),
                            "why_wrong": out_data.get("why_wrong", ""),
                            "memory_trick": out_data.get("memory_trick", ""),
                            "textbook_ref": out_data.get("textbook_ref", "")
                        }
                    except Exception:
                        pass
except Exception as e:
    print(f"Error loading explainer fallback map: {e}")

HF_TOKEN = os.getenv("HF_TOKEN", "")
MODEL_ID = os.getenv("HF_EXPLAINER_ID", "mushfiqul-17/medha-explainer-v1")
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_groq_fallback(q: Dict, state: str, sys_msg: str) -> Dict:
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("Groq API key not found in environment.")
        return {}

    question = q.get('question_bn', '')
    wrong_answer = q.get('final_answer_text', '') or q.get('correct_answer_text', '')
    correct_answer = q.get('correct_answer_text', '')
    chapter = q.get('topic', '') or q.get('chapter_name', 'Biology')

    wrong_str = f"{wrong_answer} (Wrong)" if state != "TRUST_GAP" else f"{correct_answer} (Correct)"

    messages = [
        {
            "role": "system",
            "content": (
                f"{sys_msg}\n"
                "You must respond with a JSON object containing exactly three keys:\n"
                "1. 'explanation' (detailed concept explanation in Bengali, tailored to the student's cognitive state)\n"
                "2. 'why_wrong' (explanation of the student's mistake or the trap they fell into in Bengali)\n"
                "3. 'memory_trick' (mnemonic or memory aid in Bengali to remember the concept easily)\n\n"
                "Do not include any other text, markdown formatting (like ```json), or wrapping. Respond with pure JSON."
            )
        },
        {
            "role": "user",
            "content": (
                f"Question: {question}\n"
                f"Student answered: {wrong_str}\n"
                f"Correct answer: {correct_answer}\n"
                f"Behavioral state: {state}\n"
                f"Chapter: {chapter}"
            )
        }
    ]

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": messages,
                "temperature": 0.2,
                "response_format": {"type": "json_object"}
            },
            timeout=15
        )
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"]
            data = json.loads(content)
            # Normalize keys if model returned them slightly differently
            normalized = {}
            for k, v in data.items():
                k_lower = k.lower()
                if "explain" in k_lower:
                    normalized["explanation"] = v
                elif "wrong" in k_lower or "trap" in k_lower:
                    normalized["why_wrong"] = v
                elif "memory" in k_lower or "trick" in k_lower:
                    normalized["memory_trick"] = v
                else:
                    normalized[k] = v
            return normalized
    except Exception as e:
        print(f"Groq Fallback Error: {e}")
    return {}

def query_explainer(q: Dict, state: str) -> Dict:
    """Query the custom QLoRA model on Hugging Face."""
    system_messages = {
        "PRIORITY_FOCUS": "তুমি MEDHA, বাংলাদেশের মেডিকেল ভর্তি পরীক্ষার একজন বিশেষজ্ঞ টিউটর। শিক্ষার্থী দ্রুত ও আত্মবিশ্বাসের সাথে ভুল উত্তর দিয়েছে — এটি সবচেয়ে বিপজ্জনক অবস্থা। ভুল ধারণাটি সরাসরি ও স্পষ্টভাবে সংশোধন করো।",
        "GROWTH_AREA": "তুমি MEDHA, বাংলাদেশের মেডিকেল ভর্তি পরীক্ষার একজন সহানুভূতিশীল টিউটর। শিক্ষার্থী সময় নিয়েছে কিন্তু ভুল উত্তর দিয়েছে — এটি প্রকৃত জ্ঞানের ঘাটতি। সহজ ভাষায় ধারণাটি বুঝিয়ে দাও এবং মনে রাখার কৌশল দাও।",
        "TRUST_GAP": "তুমি MEDHA, বাংলাদেশের মেডিকেল ভর্তি পরীক্ষার একজন টিউটর। শিক্ষার্থী সঠিক উত্তর দিয়েছে কিন্তু দ্বিধায় ছিল — তারা আসলে জানে কিন্তু বিশ্বাস করে না। তাদের আত্মবিশ্বাস বাড়াও এবং ধারণাটি পাকা করো।"
    }
    
    sys_msg = system_messages.get(state, "তুমি MEDHA, বাংলাদেশের মেডিকেল ভর্তি পরীক্ষার একজন টিউটর। শিক্ষার্থীকে সঠিক ও সহজবোধ্য ব্যাখ্যা দাও।")
    
    question = q.get('question_bn', '')
    wrong_answer = q.get('final_answer_text', '') or q.get('correct_answer_text', '')
    correct_answer = q.get('correct_answer_text', '')
    chapter = q.get('topic', '') or q.get('chapter_name', 'Biology')

    wrong_str = f"{wrong_answer} (Wrong)" if state != "TRUST_GAP" else f"{correct_answer} (Correct)"

    prompt = (
        f"<|im_start|>system\n{sys_msg}<|im_end|>\n"
        f"<|im_start|>user\n"
        f"Question: {question}\n"
        f"Student answered: {wrong_str}\n"
        f"Correct answer: {correct_answer}\n"
        f"Behavioral state: {state}\n"
        f"Chapter: {chapter}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 600,
            "return_full_text": False,
            "temperature": 0.1,
            "do_sample": False
        }
    }

    try:
        for attempt in range(2):
            resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=15)
            if resp.status_code == 200:
                gen_text = resp.json()[0].get("generated_text", "")
                json_str = gen_text.strip()
                if json_str.endswith("<|im_end|>"):
                    json_str = json_str[:-10].strip()
                return json.loads(json_str)
            elif resp.status_code == 503:
                time.sleep(3)
            else:
                break
    except Exception as e:
        print(f"HF API Error: {e}")
    
    # HF Inference failed or not supported. Fall back to Groq.
    print(f"HF Inference unavailable. Trying Groq fallback for {state}...")
    groq_data = query_groq_fallback(q, state, sys_msg)
    if groq_data:
        return groq_data

    # Pre-generated dataset fallback
    q_bn = q.get('question_bn', '')
    if (q_bn, state) in FALLBACK_MAP:
        print(f"Found pre-generated explanation in dataset for state: {state}")
        return FALLBACK_MAP[(q_bn, state)]

    # Ultimate static fallback
    print("Groq and dataset fallbacks also failed. Using static DB fallback.")
    return {
        "explanation": q.get("explanation_bn", "এই প্রশ্নের ব্যাখ্যা বর্তমানে উপলব্ধ নেই।"),
        "why_wrong": q.get("trap_note", "খুব কাছাকাছি অপশন দেখে বিভ্রান্ত হওয়া যাবে না।"),
        "memory_trick": q.get("memory_trick", ""),
        "textbook_ref": f"{q.get('pdf_file', '')} page {q.get('pdf_page', '')}"
    }

def process_item(q: Dict, state: str, frame: str) -> Dict:
    ai_data = query_explainer(q, state)
    
    return {
        "topic": q.get("chapter_name") or q.get("topic") or "Unknown Topic",
        "question_text": q.get("question_bn", ""),
        "frame": frame,
        "correct_answer": q.get("correct_answer_text", ""),
        "wrong_answer": q.get("final_answer_text", ""),
        "explanation": ai_data.get("explanation", q.get("explanation_bn", "")),
        "confusable_note": ai_data.get("why_wrong", q.get("confusable_note_bn")),
        "memory_trick": ai_data.get("memory_trick", q.get("memory_trick")),
        "trap_note": q.get("trap_note", ""),
        "pdf_file": q.get("pdf_file"),
        "pdf_page": q.get("pdf_page"),
        "textbook_ref": q.get("textbook_ref") or ai_data.get("textbook_ref")
    }

def assemble_notes(dna_report: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    sections = []
    
    # We only process up to 3 items in parallel per section to avoid hitting HF rate limits heavily
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # 1. PRIORITY_FOCUS
        priority_items = dna_report.get("PRIORITY_FOCUS", [])[:3]
        if priority_items:
            frame = "তুমি দ্রুত এবং আত্মবিশ্বাসের সাথে উত্তর দিয়েছ, কিন্তু উত্তরটি ভুল ছিল। এর মানে এই টপিকে তোমার একটি ভুল ধারণা (false belief) আছে যা দ্রুত সংশোধন করা প্রয়োজন।"
            future_to_item = {executor.submit(process_item, q, "PRIORITY_FOCUS", frame): q for q in priority_items}
            items = []
            for future in concurrent.futures.as_completed(future_to_item):
                items.append(future.result())
            sections.append({
                "header": "অবিলম্বে সংশোধন প্রয়োজন (Priority Focus)",
                "description": "এই প্রশ্নগুলোতে তুমি আত্মবিশ্বাসী ছিলে কিন্তু ভুল করেছ। এগুলো সবচেয়ে বিপজ্জনক কারণ এখানে নেগেটিভ মার্কিং হওয়ার সম্ভাবনা সবচেয়ে বেশি।",
                "items": items
            })

        # 2. TRUST_GAP
        trust_items = dna_report.get("TRUST_GAP", [])[:2]
        if trust_items:
            frame = "তুমি সঠিক উত্তর দিয়েছ, কিন্তু দ্বিধা করেছ বা বেশি সময় নিয়েছ। কনসেপ্ট তোমার জানা আছে, শুধু নিজের উপর বিশ্বাস বাড়াতে হবে।"
            future_to_item = {executor.submit(process_item, q, "TRUST_GAP", frame): q for q in trust_items}
            items = []
            for future in concurrent.futures.as_completed(future_to_item):
                items.append(future.result())
            sections.append({
                "header": "নিজের উপর বিশ্বাস রাখো (Trust Gap)",
                "description": "তুমি এগুলো পারো, কিন্তু পরীক্ষার হলে দ্বিধা করো। এই কনসেপ্টগুলোতে স্পিড বাড়াতে হবে।",
                "items": items
            })

        # 3. GROWTH_AREA
        growth_items = dna_report.get("GROWTH_AREA", [])[:2]
        if growth_items:
            frame = "এই টপিকটি তোমার এখনও ভালোভাবে পড়া হয়নি। এটি নতুন করে পড়ার জন্য সময় বের করো।"
            future_to_item = {executor.submit(process_item, q, "GROWTH_AREA", frame): q for q in growth_items}
            items = []
            for future in concurrent.futures.as_completed(future_to_item):
                items.append(future.result())
            sections.append({
                "header": "নতুন করে পড়তে হবে (Growth Area)",
                "description": "এই টপিকগুলোতে তোমার প্রস্তুতি এখনো অসম্পূর্ণ। সময় নিয়ে এগুলো ক্লিয়ার করতে হবে।",
                "items": items
            })

    return sections
