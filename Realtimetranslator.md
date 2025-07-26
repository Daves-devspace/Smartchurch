# Real-Time Sermon Translator

## Overview
Capture live sermon audio, transcribe speech, and translate into multiple languages in real time.

---

## Tech Stack
- **Backend:** Django, Django Channels (WebSockets)
- **ASR Model:** Hugging Face `openai/whisper-small` (fine-tuned)
- **Translation Model:** Hugging Face `Helsinki-NLP/opus-mt-en-sw` (optional fine-tuning)
- **Audio Streaming:** WebRTC client, WebSocket (Socket.IO)
- **Preprocessing:** SoX, RNNoise or PyAnNote
- **Containerization:** Docker, Docker Compose
- **Deployment:** Railway.app free tier / AWS Free Tier

---

## Architecture
1. **Audio Capture & Preprocessing**
   - Client: WebRTC-based mic capture.
   - Noise suppression: RNNoise library.
   - Chunking: 500 ms audio frames.

2. **ASR Pipeline**
   - Model: `openai/whisper-small` loaded via `transformers`.
   - Fine-Tuning Data: 1–2 hrs of sermon recordings.
   - Inference: GPU/CPU with float16 quantization.

3. **Translation Pipeline**
   - Model: `opus-mt-en-sw` for English↔Kiswahili.
   - Context Buffer: Rolling window of 3 sentences.
   - Fallback: Whisper translate mode for quick demo.

4. **Delivery**
   - WebSocket: Streams transcripts & translations.
   - Client UI: React CaptionOverlay component.
   - Caching: IndexedDB for offline subtitle storage.

---

## Implementation Steps (2 Weeks)
| Day | Task                                             |
|-----|--------------------------------------------------|
| 1   | Setup Django + Channels, deploy WebSocket server.|
| 2   | Integrate WebRTC client for audio capture.       |
| 3-4 | Fine-tune Whisper on sermon dataset (1.5 hrs).   |
| 5   | Deploy ASR service; test transcript latency.     |
| 6-7 | Integrate MarianMT translation pipeline.         |
| 8   | Implement context buffering & merging logic.     |
| 9   | Build React CaptionOverlay & WebSocket client.   |
| 10  | Add local caching & offline VTT download.        |
| 11  | Pilot test in sanctuary; gather feedback.        |
| 12-13 | Optimize models (quantization, batching).     |
| 14  | Final deployment & monitoring setup.             |

---

## Challenges & Mitigations
- **Latency:** Quantize models; use GPU where available.
- **Noise:** Collect varied audio samples; adjust RNNoise profiles.
- **Quota:** Monitor HF API usage; self-host models as backup.
- **Code-Switching:** Fine-tune on bilingual sermon data.
