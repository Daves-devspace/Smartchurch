# Real-Time Sermon Translator & Dynamic Scripture Finder (2-Week Sprint)

## Project Overview
Two-week accelerated delivery of two modules within the church management system:

1. **Real-Time Sermon Translator** – Instant transcription and translation of live sermons.
2. **Dynamic Scripture Finder** – Auto-detection and display of quoted Bible verses.

---

## 1. Real-Time Sermon Translator

### Objective
- Break language barriers and support hearing-impaired attendees through live captions.

### Process Steps

1. **Audio Capture & Preprocessing**
   - **Tool:** WebRTC-based lightweight client (mobile/tablet).
   - **Free Resource:** WebRTC SDK, SoX for noise reduction scripts.
   - **AI Structure:** Edge pre-processing with PyAnNote or RNNoise.
   - **Mitigation:** Test in actual sanctuary acoustics; toggle noise-profile presets.

2. **Real-Time Transcription**
   - **Model:** Hugging Face `openai/whisper-small` fine-tuned on 1–2 hours of sermon audio.
   - **Free Resource:** Whisper weights on HF; free-tier GPU on Google Colab or Hugging Face Inference API (community plan).
   - **Pipeline:** 500 ms audio frames → Whisper chunk inference → assemble partial transcripts.
   - **Mitigation:** Use float16 inference to halve latency; cache warm models in memory.

3. **On-the-Fly Translation**
   - **Model:** HF `Helsinki-NLP/opus-mt-en-{target}` for streaming translation.
   - **Free Resource:** Hugging Face inference endpoints (100 k tokens free/month) or self-host on CPU with `transformers` + `torchserve`.
   - **Pipeline:** Buffer last 3 sentences for context → translate → merge back.
   - **Mitigation:** Post-edit segment-level consistency at natural pauses.

4. **User Delivery**
   - **Framework:** WebSockets (Socket.io) to web/mobile clients.
   - **Fallback:** Local IndexedDB cache; download `vtt` file post-service.
   - **Mitigation:** Graceful degrade to transcript-only if translation API quota exceeded.

---

## 2. Dynamic Scripture Finder

### Objective
- Enhance engagement by showing full Bible passages when quoted live.

### Process Steps

1. **Transcript Monitoring & NER**
   - **Approach:** Hybrid regex + custom HF `token-classification` model (fine-tuned on 200 annotated transcripts).
   - **Free Resource:** `datasets` library, existing `regex` patterns from open-source sermon bots.
   - **Mitigation:** Fallback to regex if confidence < 0.7.

2. **Scripture Retrieval**
   - **Database:** Public domain Bible texts (e.g., [Bible API](https://api.bible/)).
   - **Indexing:** SQLite full-text search (FTS5) for sub-20 ms lookups.
   - **Free Resource:** SQLite (built-in), free-tier hosting (Railway.app).
   - **Mitigation:** Pre-warm FTS index in memory; monitor query times.

3. **Presentation Layer**
   - **UI:** React component overlay; collapsible “Verse History” drawer.
   - **Free Resource:** MUI (free tier) or TailwindCSS + Headless UI.
   - **Mitigation:** Limit on-screen verses to 3; queue remainder in history panel.

4. **Audit & Analytics**
   - **Logging:** JSON logs stored in AWS S3 (free tier 5 GB) or local file system.
   - **Free Resource:** AWS Free Tier, or Firebase Realtime Database free plan.
   - **Mitigation:** Encrypt logs at rest; auto-purge after 60 days.

---

## Free Resources & AI Architecture

- **Hugging Face Models:** `openai/whisper-small`, `Helsinki-NLP/opus-mt`, custom `token-classification` checkpoints.
- **Frameworks/Libraries:** `transformers`, `datasets`, `torchserve`, WebRTC, SoX, SQLite FTS5.
- **Hosting:** Google Colab (for fine-tuning), HF Inference API (community tier), Railway.app or Vercel free tiers.
- **Data:** 1–2 hours of recorded sermons for ASR finetuning, 200 transcripts for NER training, public domain Bible texts.
- **Architecture:** Shared audio→transcript pipeline feeding both NMT and NER. Separate microservices behind an API Gateway. Stateless workers for ASR/NMT; a lightweight FTS retrieval service.

---

## 2‑Week Implementation Plan

| Week | Tasks                                                                                 |
|------|---------------------------------------------------------------------------------------|
| **Week 1** | • Set up audio client & streaming infra
            • Fine-tune Whisper on sermons (1 day)
            • Deploy ASR service and test end-to-end (2 days)
            • Integrate NMT pipeline; deploy translation service (2 days)
            • Client-side UI to display captions; caching logic (1 day)
            • Pilot test translator in one service (1 day)                             |
| **Week 2** | • Annotate transcripts; fine-tune NER model (1 day)
            • Build FTS5 Bible index; retrieval API (1 day)
            • Develop React overlay with history panel (2 days)
            • Connect NER → retrieval → UI flow (1 day)
            • Security review & log retention setup (1 day)
            • Final integration test, feedback loop, and deploy to production (1 day)|

---

## Challenges & Mitigations

- **API Quotas:** Monitor usage; implement quota-fallback to self-hosted models.
- **Latency Spikes:** Use model quantization (int8), GPU inference; autoscale workers.
- **Acoustic Variation:** Collect diverse sermon samples; continuous model updates.
- **UI Overload:** Throttle verse displays; batch updates at natural breaks.

---

**Sprint Goal:** Delivered, tested, and live in production within 2 weeks using open-source and free-tier tools.
