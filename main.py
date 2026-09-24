from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
import edge_tts
import tempfile
import os

app = FastAPI()


class TTSRequest(BaseModel):
    text: str
    language: str = "English"


VOICE_MAP = {
    "English": "en-US-EmmaMultilingualNeural",
    "Telugu": "te-IN-ShrutiNeural",
    "Hindi": "hi-IN-SwaraNeural",
    "Tanglish (Tamil)": "ta-IN-PallaviNeural",
    "Tamil": "ta-IN-PallaviNeural"
}


@app.get("/")
def home():
    return {"status": "Food Lens TTS is running"}


@app.post("/tts")
async def text_to_speech(request: TTSRequest):

    voice = VOICE_MAP.get(
        request.language,
        "en-US-EmmaMultilingualNeural"
    )

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )

    temp_file.close()

    try:
        communicate = edge_tts.Communicate(
            request.text,
            voice
        )

        await communicate.save(temp_file.name)

        with open(temp_file.name, "rb") as audio:
            audio_data = audio.read()

        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=food-lens.mp3"
            }
        )

    finally:
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
