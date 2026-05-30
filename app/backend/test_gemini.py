import os
from dotenv import load_dotenv
import httpx
import asyncio

load_dotenv("c:/Users/mushf/Downloads/Medha/app/backend/.env")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

async def test_gemini():
    print(f"Key loaded: {'Yes' if GEMINI_KEY else 'No'}")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{"parts": [{"text": "Hello, are you working?"}]}],
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(resp.json()["candidates"][0]["content"]["parts"][0]["text"])
        else:
            print(resp.text)

asyncio.run(test_gemini())
