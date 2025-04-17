from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import whisper, uuid, os, tempfile, subprocess, shutil, asyncio
from deep_translator import GoogleTranslator

app = FastAPI(title="Transcription / Traduction + Streaming")

model = whisper.load_model("base")
translator = GoogleTranslator(source="auto")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/transcription")
async def transcribe(
    audio: UploadFile = File(...),
    lang: str = Query("orig", regex="^(orig|en|fr)$")
):
    if not audio.content_type.startswith("audio/"):
        raise HTTPException(400, "Fichier audio requis")
    suffix = os.path.splitext(audio.filename)[1] or ".wav"
    tmp_path = f"/tmp/{uuid.uuid4()}{suffix}"
    with open(tmp_path, "wb") as f:
        f.write(await audio.read())

    try:
        res = model.transcribe(tmp_path)
        text = res.get("text", "").strip()
        detected = res.get("language", "unknown")
    except Exception as e:
        raise HTTPException(500, f"Erreur transcription : {e}")
    finally:
        os.remove(tmp_path)

    if lang != "orig":
        try:
            text = translator.translate(text, target=lang)
        except Exception as e:
            raise HTTPException(500, f"Erreur traduction : {e}")

    return {"text": text, "detected_language": detected, "output_language": lang}

#Webs streaming
@app.websocket("/ws/stream")
async def stream_ws(
    websocket: WebSocket,
    lang: str = Query("orig", regex="^(orig|en|fr)$")
):
    await websocket.accept()
    tmpdir = tempfile.mkdtemp()
    ogg_path = os.path.join(tmpdir, "stream.ogg")
    wav_path = os.path.join(tmpdir, "stream.wav")
    last_len = 0
    ogg_file = open(ogg_path, "wb")
    try:
        while True:
            try:
                chunk = await websocket.receive_bytes()
            except WebSocketDisconnect:
                break  #session terminé?
            ogg_file.write(chunk)
            await ogg_file.flush()
            # conversion rapide en tache asynchrone
            await asyncio.to_thread(
                subprocess.run,
                ["ffmpeg", "-y", "-i", ogg_path, "-ac", "1", "-ar", "16000",
                 "-loglevel", "quiet", wav_path],
            )
            # transduction
            result = await asyncio.to_thread(model.transcribe, wav_path)
            text = result.get("text", "").strip()
            if lang != "orig":
                text = await asyncio.to_thread(translator.translate, text, lang)
            if len(text) >= last_len:
                await websocket.send_text(text[last_len:])
                last_len = len(text)
    finally:
        ogg_file.close()
        shutil.rmtree(tmpdir, ignore_errors=True)
