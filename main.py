from fastapi import FastAPI, Request
import requests
import uuid
import os

app = FastAPI()

# 🔑 ADD YOUR ELEVENLABS KEY HERE:
ELEVENLABS_API_KEY = "sk_5d58ceb8f5dc7e87c71563957010b1c28616336496210636"

# 🔑 ADD YOUR VOICE ID HERE:
VOICE_ID = "bIHbv24MWmeRgasZH58o"


@app.post("/tts")
async def tts(request: Request):
    data = await request.json()
    text = data.get("text", "")

    if not text:
        return {"error": "No text provided"}

    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream",
        headers={"xi-api-key": ELEVENLABS_API_KEY},
        json={"text": text})

    if response.status_code != 200:
        return {"error": "TTS failed"}

    # Save audio file
    filename = f"{uuid.uuid4()}.mp3"
    with open(f"static/{filename}", "wb") as f:
        f.write(response.content)

    # Give back link
    return {"url": f"https://bateman-tts-server.onrender.com/static/{filename}"}


import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
