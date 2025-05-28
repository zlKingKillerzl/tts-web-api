
# 🔊 Voice Synthesis Project with Coqui TTS and FastAPI

This project offers a **modern REST API** and a **web interface** to synthesize speech from text using the **XTTS-v2 model from Coqui TTS**. The API is built with **FastAPI** for high performance and includes a **smart caching system** to optimize repeated requests.

The web interface is developed with **HTML + Tailwind CSS + JavaScript**, providing an elegant, responsive user experience with **Dark/Light Mode** support and toast notifications.

---

## 📂 Project Structure

```
your_project/
├── fastapi_app.py           # FastAPI backend
├── index.html               # Web interface
├── manage_tts_api.py        # Script to manage environment and API
├── start.bat                # Start script for Windows
├── speaker.wav              # Reference voice file (cloning)
├── Dockerfile               # Dockerfile with GPU (CUDA) support
├── Dockerfile.cpu           # Dockerfile for CPU (alternative)
├── docker-compose.yml       # Optional orchestration with Docker Compose
└── cached_audio/            # Cached audio files (generated automatically)
```

---

## 💻 Requirements

- **Operating System:** Windows, Linux, or macOS
- **Conda:** Anaconda or Miniconda (for local execution)
- **NVIDIA GPU (Recommended):** For CUDA acceleration via Docker or locally
- **NVIDIA Container Toolkit:** Required for Docker with GPU ([installation guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html))
- **CUDA Toolkit:** CUDA 12.x support for local GPU execution
- **Internet Connection:** Needed to download models on first run

---

## 🚀 Manual Installation (Without Docker)

1. Run:

```
start.bat
```

or manually:

```
python manage_tts_api.py
```

2. In the menu, select:

```
1. Install environment and dependencies
```

Wait for the installation to finish.

---

## 🐳 Running with Docker (Recommended)

### 🔥 GPU (Preferred)

**Manual build:**
```bash
docker build -t tts-api .
docker run --gpus all -p 5001:5001 -v ${PWD}/cached_audio:/app/cached_audio tts-api
```

### 🖥️ CPU (Alternative)

**Manual build:**
```bash
docker build -t tts-api-cpu -f Dockerfile.cpu .
docker run -p 5001:5001 -v ${PWD}/cached_audio:/app/cached_audio tts-api-cpu
```

### ⚙️ Using Docker Compose (Recommended)

```bash
docker-compose up --build
```

✔️ `docker-compose.yml` is configured for GPU by default. To run on CPU, edit it and remove:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - capabilities: [gpu]
```

---

## 🌐 Using the Web Interface

Once the API is running, open:

```
http://localhost:5001
```

Features:
- Text input for speech synthesis
- Language selector
- Custom audio player
- Download generated audio
- Dark/Light Mode
- Toast notifications for feedback

---

## 📚 API Documentation (Swagger)

Open:

```
http://localhost:5001/docs
```

### 🔗 Endpoints:

| Method | Endpoint          | Description                                  |
|--------|--------------------|----------------------------------------------|
| POST   | `/synthesize`      | Generate audio and return JSON with path.    |
| POST   | `/api/audio`       | Generate audio and return .wav directly.     |
| GET    | `/`                | Return the web interface (index.html).       |
| GET    | `/{path:path}`     | Serve files (cached_audio, speaker.wav).     |
| GET    | `/health`          | Check API and TTS model health.              |

### 🔊 Request Body (POST):

```json
{
  "text": "Hello world",
  "language": "en"
}
```

### 🔥 Example Response:

```json
{
  "message": "Audio generated successfully!",
  "output_file": "cached_audio/89f7f526811668c14c0047a600799b26.wav"
}
```

---

## 📦 Audio Cache

Generated audio files are stored in `cached_audio/`.

- Filenames are unique hashes of **text + language**.
- Example:

```
cached_audio/89f7f526811668c14c0047a600799b26.wav
```

If you submit the same text and language again, the audio is instantly served from the cache.

---

## 🌍 Supported Languages

- 🇺🇸 English (en)
- 🇪🇸 Spanish (es)
- 🇫🇷 French (fr)
- 🇩🇪 German (de)
- 🇮🇹 Italian (it)
- 🇵🇹 Portuguese (pt)
- 🇵🇱 Polish (pl)
- 🇹🇷 Turkish (tr)
- 🇷🇺 Russian (ru)
- 🇳🇱 Dutch (nl)
- 🇨🇿 Czech (cs)
- 🇸🇦 Arabic (ar)
- 🇨🇳 Chinese Simplified (zh-cn)
- 🇯🇵 Japanese (ja)
- 🇭🇺 Hungarian (hu)
- 🇰🇷 Korean (ko)
- 🇮🇳 Hindi (hi)

---

## 🛠️ Troubleshooting

| Error                                                | Solution                                              |
|------------------------------------------------------|-------------------------------------------------------|
| Conda not found                                      | Install Miniconda or Anaconda.                        |
| `speaker.wav not found`                              | Place `speaker.wav` in the same folder.               |
| Port already in use                                  | Use option 4 in the menu to change the port.          |
| TypeError: TTS() got an unexpected keyword 'device'  | Fixed in this version (correct use of .to(device)).   |

---

## 🚀 Future Improvements

- [ ] Implement proper **Rate Limiting**.
- [ ] Convert to **PWA** (Progressive Web App).
- [ ] Add token-based authentication (JWT or API Key).
- [ ] Dockerize with distributed cache (Redis).
- [ ] Deploy to cloud (Render, Railway, AWS).

---

## 💙 Credits

- Based on **XTTS-v2 model by Coqui TTS**.
- Web interface made with **HTML + Tailwind CSS + JavaScript**.
- Backend developed with **FastAPI + Python**.

---

## 📜 License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

---

## 🏆 Status

**Ready for local production, container deployment (Docker with GPU/CPU), and scalable cloud deployment.**
