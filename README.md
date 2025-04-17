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
  "detected_language": "<string : code langue détectée, ex "fr">",
  "output_language": "<string : \"orig\", \"en\" ou \"fr\">"
}
```

---

## Choix CPU / GPU

| Cible | Dockerfile / docker‑compose |
|-------|----------------------------|
| **CPU** | Dans le *Dockerfile* : remplacer l’image de base par<br>`#FROM python:3.9-slim for cpu`.<br>Dans *docker‑compose.yml* : **supprimer** le bloc :<br>
    runtime: nvidia
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
 |
| **GPU** | Ne rien changer. |

---

## Exécution

### Avec *docker compose*

```bash
docker compose up -d --build
```

### Ou directement avec `docker run`

```bash
docker build -t aa-whisper .
# CPU :
docker run -d -p 80:80 --name whisper aa-whisper
# GPU (NVIDIA) :
docker run -d -p 80:80 --gpus all --name whisper aa-whisper
```

---

## Tests unitaires

```bash
# depuis le host
pytest

# ou dans le conteneur
docker exec -it whisper bash -c "pytest"
```
