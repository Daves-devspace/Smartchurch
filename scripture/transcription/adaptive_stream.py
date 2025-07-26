# import sounddevice as sd
# import numpy as np
# import queue
# import time
# import webrtcvad
# import collections
# import torchaudio
# from faster_whisper import WhisperModel
# from sentence_transformers import SentenceTransformer, util

# vad = webrtcvad.Vad(2)  # 0-3: sensitivity

# model = WhisperModel("base")
# embedder = SentenceTransformer("all-MiniLM-L6-v2")

# # Simulated Bible verse database
# bible_db = {
#     "Jeremiah 24:7": "And I will give them a heart to know me, that I am the Lord...",
#     "John 3:16": "For God so loved the world...",
# }

# verse_embeddings = {
#     k: embedder.encode(v, convert_to_tensor=True)
#     for k, v in bible_db.items()
# }

# class AdaptiveTranscriber:
#     def __init__(self):
#         self.sample_rate = 16000
#         self.frame_duration = 30  # ms
#         self.chunk_duration = 1.0  # sec
#         self.buffer_duration = 5.0
#         self.min_transcript_words = 5
#         self.silence_threshold = 0.5

#         self.q = queue.Queue()
#         self.buffer = []
#         self.last_speech_time = time.time()

#     def audio_callback(self, indata, frames, time_info, status):
#         self.q.put(indata.copy())

#     def is_speech(self, audio):
#         return vad.is_speech(audio.tobytes(), self.sample_rate)

#     def record_loop(self):
#         with sd.InputStream(callback=self.audio_callback, channels=1, samplerate=self.sample_rate, dtype='int16', blocksize=int(self.sample_rate * self.chunk_duration)):
#             while True:
#                 audio_chunk = self.q.get()
#                 self.buffer.append(audio_chunk)

#                 is_speaking = self.is_speech(audio_chunk.flatten())
#                 if is_speaking:
#                     self.last_speech_time = time.time()

#                 # If silence detected or buffer is full
#                 if time.time() - self.last_speech_time > self.silence_threshold or self.get_buffer_duration() > self.buffer_duration:
#                     self.flush_buffer()

#     def get_buffer_duration(self):
#         return len(self.buffer) * self.chunk_duration

#     def flush_buffer(self):
#         if not self.buffer:
#             return

#         audio = np.concatenate(self.buffer, axis=0).flatten().astype(np.float32) / 32768.0
#         segments, _ = model.transcribe(audio, language="en", beam_size=5)

#         full_text = " ".join([seg.text for seg in segments]).strip()
#         print(f"\nTranscript: {full_text}")

#         if len(full_text.split()) >= self.min_transcript_words:
#             self.match_bible_verse(full_text)

#         self.buffer = []

#     def match_bible_verse(self, text):
#         emb = embedder.encode(text, convert_to_tensor=True)

#         best_match, best_score = None, 0
#         for ref, ref_emb in verse_embeddings.items():
#             sim = util.pytorch_cos_sim(emb, ref_emb).item()
#             if sim > best_score:
#                 best_match, best_score = ref, sim

#         if best_score > 0.6:
#             print(f"🔍 Matched Verse: {best_match} — {bible_db[best_match]} (Score: {best_score:.2f})")
#         else:
#             print("⚠️ No strong verse match found.")

# # Start
# transcriber = AdaptiveTranscriber()
# transcriber.record_loop()
