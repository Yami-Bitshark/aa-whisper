# aa‑whisper

> Repo : <https://github.com/Yami-Bitshark/aa-whisper>

## Fonctionnalités

- **API REST** : `POST /transcription` pour convertir un fichier audio en texte.  
- **Interface Web** :  
  - upload d’un fichier `.wav` puis transcription ;  
  - enregistrement micro, envoi et transcription ;  
  - transcription *temps‑réel* du micro via WebSocket.

---

## Installation rapide

```bash
git clone https://github.com/Yami-Bitshark/aa-whisper.git
cd aa-whisper
docker compose up -d --build
```

- L’application est disponible sur **http://localhost**.  
- Les modèles Whisper sont mis en cache dans `./whisper_cache`.

---

## Appel REST — Transcription de fichier

### curl

```bash
curl -X POST \
     -F "audio=@./demo/input.wav" \
     "http://localhost/transcription"
```

### Python (`requests`)

```python
import requests

with open("./demo/input.wav", "rb") as f:
    files = {"audio": f}
    r = requests.post("http://localhost/transcription", files=files)
    print(r.json())
```
### Format de la réponse JSON

```json
{
  "text": "<string : texte transcrit ou traduit>",
  "detected_language": "<string : code langue détectée, ex \"fr\">",
  "output_language": "<string : \"orig\", \"en\" ou \"fr\">"
}
```
