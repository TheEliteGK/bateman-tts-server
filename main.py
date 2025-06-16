from fastapi import FastAPI, Request
import requests
import uuid
import os
import uvicorn

app = FastAPI()

# ✅ Use env vars or hardcode for test
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
VOICE_ID = os.environ.get("VOICE_ID")
GROUP_ID = "16610227"  # Your group ID

# ✅ Upload to Roblox — WAV version
def upload_to_roblox(filename):
    api_key = os.environ.get("ROBLOX_API_KEY")

    with open(filename, "rb") as f:
        audio_data = f.read()

    url = "https://apis.roblox.com/assets/v1/assets"

    headers = {
        "x-api-key": api_key
    }

    files = {
        "fileContent": ("voice.wav", audio_data, "audio/wav")
    }

    data = {
        "assetType": "Audio",
        "name": f"TTS_{uuid.uuid4()}",
        "description": "Auto-generated TTS audio",
        "groupId": GROUP_ID
    }

    response = requests.post(url, headers=headers, files=files, data=data)

    print("Roblox Upload Status:", response.status_code)
    print("Roblox Upload Response:", response.text)

    if response.status_code == 201:
        return response.json().get("id")
    else:
        return None

# ✅ TTS route — request WAV from ElevenLabs
@app.post("/tts")
async def tts(request: Request):
    data = await request.json()
    text = data.get("text", "")

    if not text:
        return {"error": "No text provided"}

    # ✅ Request WAV format explicitly
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream",
        headers={"xi-api-key": ELEVENLABS_API_KEY},
        json={
            "text": text,
            "voice_settings": {
                "audio_format": "wav"
            }
        }
    )

    print("ElevenLabs Status:", response.status_code)
    if response.status_code != 200:
        return {"error": "TTS failed"}

    # ✅ Save as WAV
    os.makedirs("static", exist_ok=True)
    filename = f"static/{uuid.uuid4()}.wav"
    with open(filename, "wb") as f:
        f.write(response.content)

    # ✅ Upload to Roblox
    asset_id = upload_to_roblox(filename)

    if asset_id:
        return {"assetId": asset_id}
    else:
        return {"error": "Roblox upload failed"}

# ✅ Local run
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)




