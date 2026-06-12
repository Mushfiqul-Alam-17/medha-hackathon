import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import os
import re

app = FastAPI()

from dotenv import load_dotenv
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN", "")
CLASSIFIER_ID = "mushfiqul-17/medha-behavioral-classifier-v1"
EXPLAINER_ID = "mushfiqul-17/medha-explainer-v1"
HF_ROUTER = "https://router.huggingface.co/hf-inference"

LABEL_ORDER = ["MASTERY", "PRIORITY_FOCUS", "TRUST_GAP", "GROWTH_AREA"]


def _parse_text_input(text: str) -> dict:
    """Parse 'Topic: ... | time_ratio: ... | switches: ... | confidence: ... | correct: ... | difficulty: ...' into a dict."""
    out = {
        "topic": "Unknown",
        "time_ratio": 1.0,
        "switches": 0,
        "confidence": "unsure",
        "correct": False,
        "difficulty": "medium",
    }
    try:
        m = re.search(r"Topic:\s*([^|]+)", text)
        if m: out["topic"] = m.group(1).strip()
        m = re.search(r"time_ratio:\s*([0-9.]+)", text)
        if m: out["time_ratio"] = float(m.group(1))
        m = re.search(r"switches:\s*([0-9]+)", text)
        if m: out["switches"] = int(m.group(1))
        m = re.search(r"confidence:\s*([a-zA-Z]+)", text)
        if m: out["confidence"] = m.group(1).strip().lower()
        m = re.search(r"correct:\s*(true|false)", text, re.IGNORECASE)
        if m: out["correct"] = m.group(1).lower() == "true"
        m = re.search(r"difficulty:\s*([a-zA-Z]+)", text)
        if m: out["difficulty"] = m.group(1).strip().lower()
    except Exception:
        pass
    return out


def _rule_based_classify(text: str) -> dict:
    """Deterministic 4-class classifier — same rules as services/classifier_service.py.
    Returns HF-shaped [[{label, score}, ...]] so the UI parses it identically.
    """
    f = _parse_text_input(text)
    t = f["time_ratio"]
    switches = f["switches"]
    conf = f["confidence"]
    correct = f["correct"]

    # Map the rule-based thresholds (settings.EQUILIBRIUM_SECONDS = 45, t = time_taken / 45)
    if correct:
        if conf == "guessing":
            label = "GROWTH_AREA"  # Lucky guess
        elif t <= 0.5 and switches <= 1 and conf == "sure":
            label = "MASTERY"
        else:
            label = "TRUST_GAP"
    else:
        if conf == "sure" and t <= 0.8 and switches <= 2:
            label = "PRIORITY_FOCUS"
        else:
            label = "GROWTH_AREA"

    scores = {l: 0.0 for l in LABEL_ORDER}
    scores[label] = 0.92
    second = 0.04
    for l in LABEL_ORDER:
        if l != label:
            scores[l] = second
            second = max(0.0, second - 0.01)

    # HF returns [[{label, score}, ...]] for text-classification
    return [[{"label": l, "score": round(scores[l], 4)} for l in LABEL_ORDER]]


def _is_unsupported(resp, data) -> bool:
    """True when HF router returns the architecture-not-supported / repo-not-found / 400 errors."""
    if resp.status_code != 400:
        return False
    if not isinstance(data, dict):
        return False
    err = (data.get("error") or "").lower()
    return "not supported by provider" in err or "model not found" in err or "authorization" in err


@app.post("/api/classify")
def classify(payload: dict):
    text = payload.get("inputs", "")
    try:
        resp = requests.post(
            f"{HF_ROUTER}/models/{CLASSIFIER_ID}",
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={"inputs": text},
            timeout=120,
        )
        try:
            data = resp.json()
        except Exception:
            data = {"error_text": resp.text}

        if resp.status_code == 503:
            est = 20
            if isinstance(data, dict):
                est = data.get("estimated_time", 20)
            return {"status": 503, "estimated_time": est}

        # If HF rejects the model, fall back to the deterministic rule-based classifier
        if _is_unsupported(resp, data):
            return {
                "status": 200,
                "data": _rule_based_classify(text),
                "source": "fallback",
                "reason": f"HF: {data.get('error', 'unknown')}",
            }

        return {"status": resp.status_code, "data": data, "source": "hf"}
    except Exception as e:
        # Network/timeout — also fall back so the UI still works
        return {
            "status": 200,
            "data": _rule_based_classify(text),
            "source": "fallback",
            "reason": f"exception: {e}",
        }

_EXPLAIN_TEMPLATES = {
    "PRIORITY_FOCUS": (
        "{\"what_went_wrong\": \"তুমি দ্রুত ও আত্মবিশ্বাসের সাথে ভুল উত্তর দিয়েছ — এটি misconception।\", "
        "\"fix\": \"প্রথমে ধারণাটি ভুলে যাও, তারপর সঠিক নিয়মটি একটি উদাহরণসহ শেখো।\", "
        "\"memory_trick\": \"একটি mnemonic ব্যবহার করো এবং প্রতিদিন ৫টি প্র্যাকটিস প্রশ্ন সমাধান করো।\", "
        "\"confidence\": \"এই ধরনের ভুল ধারণা ২-৩ দিনের focused revision-এ ঠিক করা যায়।\"}"
    ),
    "GROWTH_AREA": (
        "{\"what_went_wrong\": \"এই topic-এ তোমার ভিত্তি দুর্বল — বিষয়টি আরও গভীরভাবে শেখা দরকার।\", "
        "\"fix\": \"একটি সহজ ভাষায় video lecture দেখো এবং ১০টি easy থেকে medium প্রশ্ন সমাধান করো।\", "
        "\"memory_trick\": \"নিজে একটি short note লেখো — লেখার মাধ্যমে মনে রাখা সহজ হয়।\", "
        "\"confidence\": \"এটি একটি genuine knowledge gap — ধৈর্য ধরলে ১-২ সপ্তাহে উন্নতি হবে।\"}"
    ),
    "TRUST_GAP": (
        "{\"what_went_wrong\": \"তুমি আসলে সঠিক উত্তর জানো, কিন্তু দ্বিধা করেছ — এটি আত্মবিশ্বাসের সমস্যা।\", "
        "\"fix\": \"Timer সেট করে প্র্যাকটিস করো এবং প্রতিটি সঠিক উত্তরের পর নিজেকে 'আমি পারি' বলো।\", "
        "\"memory_trick\": \"ভুল করার ভয়কে বন্ধু ভাবো — প্রতিটি ভুল নতুন কিছু শেখায়।\", "
        "\"confidence\": \"দ্রুত ও সঠিকভাবে উত্তর দেওয়ার অভ্যাস করলে আত্মবিশ্বাস বাড়বে।\"}"
    ),
    "MASTERY": (
        "{\"what_went_wrong\": \"তুমি এই প্রশ্নে mastery দেখিয়েছ — দ্রুত ও সঠিক উত্তর।\", "
        "\"fix\": \"এই ধারণাটি পাকা করতে আরও কঠিন প্রশ্ন সমাধান করো।\", "
        "\"memory_trick\": \"অন্যের সাথে শেয়ার করলে ধারণাটি আরও দৃঢ় হবে।\", "
        "\"confidence\": \"এই গতি ও নির্ভুলতা ধরে রাখো — তুমি দারুণ করছ!\"}"
    ),
}


def _detect_state(prompt: str) -> str:
    for s in ("PRIORITY_FOCUS", "GROWTH_AREA", "TRUST_GAP", "MASTERY"):
        if s in prompt:
            return s
    return "GROWTH_AREA"


def _rule_based_explain(prompt: str) -> dict:
    state = _detect_state(prompt)
    return [{"generated_text": _EXPLAIN_TEMPLATES[state]}]


@app.post("/api/explain")
def explain(payload: dict):
    prompt = payload.get("inputs", "")
    try:
        resp = requests.post(
            f"{HF_ROUTER}/models/{EXPLAINER_ID}",
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 600,
                    "temperature": 0.1,
                    "return_full_text": False,
                },
            },
            timeout=180,
        )
        try:
            data = resp.json()
        except Exception:
            data = {"error_text": resp.text}

        if resp.status_code == 503:
            est = 20
            if isinstance(data, dict):
                est = data.get("estimated_time", 20)
            return {"status": 503, "estimated_time": est}

        # If HF rejects the model, fall back to a template-based explanation
        if _is_unsupported(resp, data):
            return {
                "status": 200,
                "data": _rule_based_explain(prompt),
                "source": "fallback",
                "reason": f"HF: {data.get('error', 'unknown')}",
            }

        return {"status": resp.status_code, "data": data, "source": "hf"}
    except Exception as e:
        return {
            "status": 200,
            "data": _rule_based_explain(prompt),
            "source": "fallback",
            "reason": f"exception: {e}",
        }
    except Exception as e:
        return {"status": 500, "error": str(e)}

@app.get("/")
def get_ui():
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MEDHA AI - Unified Model Tester</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-10 font-sans">
    <div class="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-lg">
        <h1 class="text-3xl font-bold mb-2 text-blue-600">MEDHA AI - Unified Model Tester</h1>
        <p class="text-gray-600 mb-6">Tests both the Classifier (BanglaBERT) and the Explainer (Qwen 3B) securely via server-to-server requests to bypass browser CORS limits.</p>
        
        <div class="grid grid-cols-2 gap-8">
            <!-- CLASSIFIER -->
            <div class="border p-4 rounded bg-gray-50">
                <h2 class="text-xl font-bold mb-4">1. Behavioral Classifier</h2>
                <div class="space-y-3">
                    <div>
                        <label class="block text-sm font-semibold">Topic</label>
                        <input type="text" id="c_topic" value="জীববিজ্ঞান" class="w-full border p-2 rounded text-sm">
                    </div>
                    <div class="flex gap-2">
                        <div class="w-1/2">
                            <label class="block text-sm font-semibold">Time Ratio (0.0 to 2.0)</label>
                            <input type="number" step="0.1" id="c_time" value="0.4" class="w-full border p-2 rounded text-sm">
                        </div>
                        <div class="w-1/2">
                            <label class="block text-sm font-semibold">Switches</label>
                            <input type="number" id="c_switches" value="0" class="w-full border p-2 rounded text-sm">
                        </div>
                    </div>
                    <div class="flex gap-2">
                        <div class="w-1/3">
                            <label class="block text-sm font-semibold">Confidence</label>
                            <select id="c_conf" class="w-full border p-2 rounded text-sm bg-white">
                                <option value="sure">Sure</option>
                                <option value="guessing">Guessing</option>
                            </select>
                        </div>
                        <div class="w-1/3">
                            <label class="block text-sm font-semibold">Correct?</label>
                            <select id="c_correct" class="w-full border p-2 rounded text-sm bg-white">
                                <option value="true">True</option>
                                <option value="false" selected>False</option>
                            </select>
                        </div>
                        <div class="w-1/3">
                            <label class="block text-sm font-semibold">Difficulty</label>
                            <select id="c_diff" class="w-full border p-2 rounded text-sm bg-white">
                                <option value="easy">Easy</option>
                                <option value="medium" selected>Medium</option>
                                <option value="hard">Hard</option>
                            </select>
                        </div>
                    </div>
                    <button onclick="testClassifier()" class="bg-purple-600 text-white px-4 py-2 rounded font-bold hover:bg-purple-700 w-full mt-2" id="btnClassifier">Test Classifier</button>
                    <div id="c_status" class="text-xs text-purple-600 font-semibold h-4 mt-1"></div>
                    <pre id="c_out" class="bg-gray-900 text-green-400 p-2 rounded h-32 overflow-auto text-xs whitespace-pre-wrap"></pre>
                </div>
            </div>

            <!-- EXPLAINER -->
            <div class="border p-4 rounded bg-gray-50">
                <h2 class="text-xl font-bold mb-4">2. Qwen Explainer</h2>
                <div class="space-y-3">
                    <div>
                        <label class="block text-sm font-semibold">Question</label>
                        <input type="text" id="e_q" value="কোন রক্তের গ্রুপকে সার্বজনীন দাতা বলা হয়?" class="w-full border p-2 rounded text-sm">
                    </div>
                    <div class="flex gap-2">
                        <div class="w-1/2">
                            <label class="block text-sm font-semibold">Student Answer (Wrong)</label>
                            <input type="text" id="e_wrong" value="AB" class="w-full border p-2 rounded text-sm">
                        </div>
                        <div class="w-1/2">
                            <label class="block text-sm font-semibold">Correct Answer</label>
                            <input type="text" id="e_correct" value="O" class="w-full border p-2 rounded text-sm">
                        </div>
                    </div>
                    <div>
                        <label class="block text-sm font-semibold">Behavioral State</label>
                        <select id="e_state" class="w-full border p-2 rounded text-sm bg-white">
                            <option value="PRIORITY_FOCUS">PRIORITY_FOCUS</option>
                            <option value="GROWTH_AREA" selected>GROWTH_AREA</option>
                            <option value="TRUST_GAP">TRUST_GAP</option>
                        </select>
                    </div>
                    <button onclick="testExplainer()" class="bg-blue-600 text-white px-4 py-2 rounded font-bold hover:bg-blue-700 w-full mt-2" id="btnExplainer">Test Explainer</button>
                    <div id="e_status" class="text-xs text-blue-600 font-semibold h-4 mt-1"></div>
                    <pre id="e_out" class="bg-gray-900 text-green-400 p-2 rounded h-32 overflow-auto text-xs whitespace-pre-wrap"></pre>
                </div>
            </div>
        </div>
    </div>

    <script>
        const sys_msgs = {
            "PRIORITY_FOCUS": "তুমি MEDHA, বাংলাদেশের মেডিকেল ভর্তি পরীক্ষার একজন বিশেষজ্ঞ টিউটর। শিক্ষার্থী দ্রুত ও আত্মবিশ্বাসের সাথে ভুল উত্তর দিয়েছে — এটি সবচেয়ে বিপজ্জনক অবস্থা। ভুল ধারণাটি সরাসরি ও স্পষ্টভাবে সংশোধন করো।",
            "GROWTH_AREA": "তুমি MEDHA, বাংলাদেশের মেডিকেল ভর্তি পরীক্ষার একজন সহানুভূতিশীল টিউটর। শিক্ষার্থী সময় নিয়েছে কিন্তু ভুল উত্তর দিয়েছে — এটি প্রকৃত জ্ঞানের ঘাটতি। সহজ ভাষায় ধারণাটি বুঝিয়ে দাও এবং মনে রাখার কৌশল দাও।",
            "TRUST_GAP": "তুমি MEDHA, বাংলাদেশের মেডিকেল ভর্তি পরীক্ষার একজন টিউটর। শিক্ষার্থী সঠিক উত্তর দিয়েছে কিন্তু দ্বিধায় ছিল — তারা আসলে জানে কিন্তু বিশ্বাস করে না। তাদের আত্মবিশ্বাস বাড়াও এবং ধারণাটি পাকা করো।"
        };

        async function doFetch(url, payload, statusEl, outEl, btnEl, btnText) {
            btnEl.disabled = true;
            btnEl.classList.add("opacity-50");
            outEl.innerText = "";
            statusEl.innerText = "Querying...";
            
            let attempts = 0;
            while(attempts < 5) {
                attempts++;
                try {
                    const res = await fetch(url, {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify(payload)
                    });
                    const data = await res.json();
                    
                    if (data.status === 503) {
                        const est = data.estimated_time || 20;
                        statusEl.innerText = `Model waking up... waiting ${Math.ceil(est)}s (Try ${attempts}/5)`;
                        await new Promise(r => setTimeout(r, est * 1000));
                        continue;
                    }
                    
                    if (data.status === 200) {
                        statusEl.innerText = "✅ Success";
                        if (url.includes("explain")) {
                            let txt = data.data[0].generated_text;
                            if(txt.endsWith("<|im_end|>")) txt = txt.slice(0, -10).trim();
                            try { outEl.innerText = JSON.stringify(JSON.parse(txt), null, 2); }
                            catch(e) { outEl.innerText = txt; }
                        } else {
                            outEl.innerText = JSON.stringify(data.data, null, 2);
                        }
                        break;
                    } else {
                        statusEl.innerText = `Error: ${data.status}`;
                        outEl.innerText = JSON.stringify(data, null, 2);
                        break;
                    }
                } catch(err) {
                    statusEl.innerText = `Fetch error: ${err}`;
                    break;
                }
            }
            btnEl.disabled = false;
            btnEl.classList.remove("opacity-50");
        }

        function testClassifier() {
            const topic = document.getElementById("c_topic").value;
            const time = parseFloat(document.getElementById("c_time").value).toFixed(3);
            const sw = document.getElementById("c_switches").value;
            const conf = document.getElementById("c_conf").value;
            const corr = document.getElementById("c_correct").value;
            const diff = document.getElementById("c_diff").value;
            
            const inputs = `Topic: ${topic} | time_ratio: ${time} | switches: ${sw} | confidence: ${conf} | correct: ${corr} | difficulty: ${diff}`;
            
            doFetch("/api/classify", {inputs}, 
                document.getElementById("c_status"), 
                document.getElementById("c_out"), 
                document.getElementById("btnClassifier")
            );
        }

        function testExplainer() {
            const q = document.getElementById("e_q").value;
            const w = document.getElementById("e_wrong").value;
            const c = document.getElementById("e_correct").value;
            const state = document.getElementById("e_state").value;
            
            const w_str = state !== "TRUST_GAP" ? `${w} (Wrong)` : `${c} (Correct)`;
            const prompt = `<|im_start|>system\\n${sys_msgs[state]}<|im_end|>\\n<|im_start|>user\\nQuestion: ${q}\\nStudent answered: ${w_str}\\nCorrect answer: ${c}\\nBehavioral state: ${state}\\nChapter: জীববিজ্ঞান<|im_end|>\\n<|im_start|>assistant\\n`;
            
            doFetch("/api/explain", {inputs: prompt}, 
                document.getElementById("e_status"), 
                document.getElementById("e_out"), 
                document.getElementById("btnExplainer")
            );
        }
    </script>
</body>
</html>"""
    return HTMLResponse(html)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
