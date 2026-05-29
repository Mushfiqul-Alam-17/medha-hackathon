import os
from dotenv import load_dotenv
import httpx
import asyncio

load_dotenv("c:/Users/mushf/Downloads/Medha/app/backend/.env")
GROQ_KEY = os.getenv("GROQ_API_KEY", "")

async def test_groq():
    print(f"Key loaded: {'Yes' if GROQ_KEY else 'No'}")
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": "Hello, are you working?"}
        ]
    }
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(resp.json()["choices"][0]["message"]["content"])
        else:
            print(resp.text)

asyncio.run(test_groq())
