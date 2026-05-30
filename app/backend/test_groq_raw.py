import os
from dotenv import load_dotenv
import httpx
import asyncio
import json

load_dotenv("c:/Users/mushf/Downloads/Medha/app/backend/.env")
GROQ_KEY = os.getenv("GROQ_API_KEY", "")

NOTES_SYSTEM_PROMPT = """You are MEDHA, a Bangladeshi medical admission exam tutor AI.
You receive a student's behavioral DNA report — questions classified as "slow", "confused", or "danger" based on their real-time exam behavior.
Generate personalized study notes in this EXACT JSON format:
{
  "slow": [{"topic":"topic","explanation":"explain","speedNote":"speed","memoryTrick":"trick","trapQuestion":"trap"}],
  "confused": [{"topic":"topic","explanation":"explain","comparisonTable":[],"memoryTrick":"trick","trapQuestion":"trap"}],
  "danger": [{"topic":"topic","explanation":"explain","dangerNote":"danger","whyCorrect":"correct","whyTricked":"tricked","memoryTrick":"trick","trapQuestion":"trap"}]
}
Rules:
- Write everything in Bangla
- Return ONLY valid JSON, no markdown, no backticks"""

async def test_groq():
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": NOTES_SYSTEM_PROMPT},
            {"role": "user", "content": "Student DNA Report:\n## SLOW questions (1):\n- Question: What is the main site of cellular respiration?\n  Correct Answer: Mitochondria\n  Student chose: Mitochondria\n  Time: 45s\n  Concept: Mitochondria"}
        ],
        "temperature": 0.7,
        "max_tokens": 4096,
        "response_format": {"type": "json_object"}
    }
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code == 200:
            text = resp.json()["choices"][0]["message"]["content"]
            print("RAW TEXT RECEIVED:")
            print(repr(text))
            try:
                parsed = json.loads(text)
                print("PARSED SUCCESSFUL")
            except Exception as e:
                print(f"PARSING FAILED: {e}")
        else:
            print(f"STATUS {resp.status_code}: {resp.text}")

asyncio.run(test_groq())
