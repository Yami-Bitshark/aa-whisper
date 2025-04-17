from pathlib import Path
import sys, pathlib

from app import app 
from fastapi.testclient import TestClient

root = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(root))
client = app.test_client() if hasattr(app, "test_client") else None
client = TestClient(app)
AUDIO_PATH = Path("demo/input.wav")

def test_transcription_vrai_modele():
    assert AUDIO_PATH.exists(), "Le fichier demo/input.wav est manquant"
    with AUDIO_PATH.open("rb") as f:
        r = client.post("/transcription",files={"audio": ("input.wav", f, "audio/wav")})
    data = r.json()
    assert r.status_code == 200
    assert data["text"].strip()
