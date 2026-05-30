import os
from dotenv import load_dotenv
import httpx
import asyncio

load_dotenv("c:/Users/mushf/Downloads/Medha/app/backend/.env")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")

async def test_openrouter():
    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {
        "model": "deepseek/deepseek-v4-flash:free",
        "messages": [{"role": "user", "content": "Say hello in Bengali"}]
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers, timeout=15)
        if resp.status_code == 200:
            print("SUCCESS")
            print(resp.json()['choices'][0]['message']['content'])
        else:
            print(f"FAILED: {resp.status_code}")
            print(resp.text)

asyncio.run(test_openrouter())
