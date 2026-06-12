import requests
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

import time

import os
from dotenv import load_dotenv
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN", "")
MODEL_ID = "mushfiqul-17/medha-explainer-v1"
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_model(prompt):
    print(f"Sending request to Hugging Face Serverless API ({MODEL_ID})...")
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 600,
            "return_full_text": False,
            "temperature": 0.1,
            "do_sample": False
        }
    }
    
    for attempt in range(5):
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 503:
            # Hugging Face puts unused models to sleep. It needs time to load the weights.
            estimated_time = response.json().get("estimated_time", 20)
            print(f"Model is waking up on Hugging Face... waiting {estimated_time:.1f} seconds (Attempt {attempt+1}/5)")
            time.sleep(estimated_time)
        else:
            print(f"Error {response.status_code}: {response.text}")
            break
    return None

if __name__ == "__main__":
    system_msg = "তুমি MEDHA, বাংলাদেশের মেডিকেল ভর্তি পরীক্ষার একজন সহানুভূতিশীল টিউটর। শিক্ষার্থী সময় নিয়েছে কিন্তু ভুল উত্তর দিয়েছে — এটি প্রকৃত জ্ঞানের ঘাটতি। সহজ ভাষায় ধারণাটি বুঝিয়ে দাও এবং মনে রাখার কৌশল দাও।"
    question = "কোন রক্তের গ্রুপকে সার্বজনীন দাতা বলা হয়?"
    wrong_answer = "AB"
    correct_answer = "O"
    state = "GROWTH_AREA"
    chapter = "রোগ প্রতিরোধ ও রক্তের গ্রুপ"

    prompt = (
        f"<|im_start|>system\n{system_msg}<|im_end|>\n"
        f"<|im_start|>user\n"
        f"Question: {question}\n"
        f"Student answered: {wrong_answer} (Wrong)\n"
        f"Correct answer: {correct_answer}\n"
        f"Behavioral state: {state}\n"
        f"Chapter: {chapter}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    print("--- Prompt ---")
    print(prompt.strip())
    print("--------------\n")

    result = query_model(prompt)
    
    if result:
        print("\n✅ Success! Received output from model:")
        print("---------------------------------------")
        generated_text = result[0].get('generated_text', '')
        print(generated_text)
        
        print("\n--- JSON Validation ---")
        try:
            # Clean up token generation artifacts if any
            json_str = generated_text.strip()
            if json_str.endswith("<|im_end|>"):
                json_str = json_str[:-10].strip()
                
            parsed = json.loads(json_str)
            print("✅ Valid JSON output!")
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"❌ Failed to parse JSON: {e}")
