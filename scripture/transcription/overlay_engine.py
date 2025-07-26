# import threading
# import queue
# import time
# import sounddevice as sd
# import webrtcvad
# import numpy as np

# from faster_whisper import WhisperModel
# from scripture.pipeline.live_processor import process_transcript_chunk
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync

# class LiveVerseOverlayEngine:
#     """
#     🚀 FIXED VERSION: Real‑time capture → VAD → ASR → verse lookup → overlay.
#     """
#     def __init__(
#         self,
#         model_size: str = "tiny",
#         device: str = "cpu",
#         sample_rate: int = 16000,
#         vad_mode: int = 2,
#         max_chunk_time: float = 6.0,
#         silence_timeout: float = 1.0,
#         input_device: int = None
#     ):
#         # Load ASR model
#         print(f"🤖 Loading Whisper {model_size} model...")
#         self.model = WhisperModel(model_size, device=device, compute_type="int8")
#         print("✅ Whisper loaded!")

#         # Voice activity detection (VAD)
#         self.vad = webrtcvad.Vad(vad_mode)

#         # Queues
#         self.audio_q = queue.Queue(maxsize=50)
#         self.transcription_q = queue.Queue(maxsize=10)
#         self.trans_q = queue.Queue()
        
#         # Current audio buffer for VAD processing
#         self.current_buffer = bytearray()

#         # Audio parameters
#         self.sr = sample_rate
#         self.frame_ms = 30
#         self.frame_size = int(self.sr * self.frame_ms / 1000)
#         self.max_time = max_chunk_time
#         self.silence_timeout = silence_timeout

#         # Speech state tracking
#         self.last_speech_time = None
#         self.last_silence_time = None
#         self.buffer_start_time = None
#         self.min_buffer_duration = 0.1

#         # Control flags
#         self.running = False
#         self.input_device = input_device or sd.default.device[0]
#         print(f"🎙️ Using mic ID: {self.input_device}")

#         # Debug counters
#         self.debug_audio_callbacks = 0
#         self.debug_audio_processed = 0
#         self.debug_speech_detected = 0
#         self.debug_last_volume_check = time.time()
#         self.debug_volume_threshold = 0.005

#         # WebSocket support
#         self.channel_layer = get_channel_layer()
#         self.group_name = "live_verses"

#     def _audio_callback(self, indata, frames, time_info, status):
#         """Audio callback with debug info."""
#         self.debug_audio_callbacks += 1
        
#         if status:
#             print(f"[AudioErr] {status}")

#         volume = np.max(np.abs(indata))
#         now = time.time()
        
#         # Log volume every 5 seconds
#         if now - self.debug_last_volume_check > 5:
#             print(f"🔊 Audio callback #{self.debug_audio_callbacks}: volume={volume:.4f}")
#             self.debug_last_volume_check = now
        
#         if volume < self.debug_volume_threshold:
#             return

#         try:
#             audio_int16 = (indata[:, 0] * 32767).astype(np.int16)
#             self.audio_q.put_nowait(audio_int16.tobytes())
            
#             self.debug_audio_processed += 1
#             if self.debug_audio_processed % 50 == 0:
#                 print(f"📦 Audio chunks processed: {self.debug_audio_processed}")
                
#         except queue.Full:
#             try:
#                 self.audio_q.get_nowait()
#                 self.audio_q.put_nowait(audio_int16.tobytes())
#                 print("⚡ Queue full - removed old audio")
#             except:
#                 pass

#     def _capture(self):
#         """Stream audio from selected input device."""
#         try:
#             print(f"🎙️ Starting audio capture...")
            
#             with sd.InputStream(
#                 samplerate=self.sr,
#                 device=self.input_device,
#                 channels=1,
#                 dtype="float32",
#                 blocksize=self.frame_size,
#                 callback=self._audio_callback
#             ):
#                 print(f"✅ Audio stream active")
#                 while self.running:
#                     time.sleep(0.1)
                    
#         except Exception as e:
#             print(f"❌ Audio capture error: {e}")
#             raise

#     def _process_audio_fast(self):
#         """Process audio with VAD."""
#         print("🎙️ Starting fast audio processing...")
        
#         while self.running:
#             try:
#                 chunk = self.audio_q.get(timeout=0.5)
#             except queue.Empty:
#                 self._check_timeout()
#                 continue

#             self.current_buffer.extend(chunk)
            
#             if self.buffer_start_time is None:
#                 self.buffer_start_time = time.time()

#             self._process_vad_frames_fast()

#     def _process_vad_frames_fast(self):
#         """Process VAD frames without consuming buffer."""
#         now = time.time()
        
#         # Process frames for VAD detection without consuming buffer
#         frames_processed = 0
#         speech_frames = 0
#         temp_buffer = self.current_buffer[:]  # Copy for VAD testing
        
#         while len(temp_buffer) >= 2 * self.frame_size and frames_processed < 3:
#             frame = bytes(temp_buffer[:2 * self.frame_size])
#             temp_buffer = temp_buffer[2 * self.frame_size:]
#             frames_processed += 1

#             try:
#                 is_speech = self.vad.is_speech(frame, sample_rate=self.sr)
                
#                 if is_speech:
#                     speech_frames += 1
#                     self.last_speech_time = now
#                     self.last_silence_time = None
#                     self.debug_speech_detected += 1
#                 else:
#                     if self.last_silence_time is None:
#                         self.last_silence_time = now

#             except Exception as e:
#                 print(f"❌ VAD error: {e}")
#                 break
        
#         # Check emission without clearing buffer in VAD
#         should_emit = self._should_emit_transcript(now)
#         if should_emit:
#             print(f"⚡ Emitting: {should_emit}")
#             self._queue_for_transcription()

#     def _should_emit_transcript(self, now):
#         """Decide when to emit transcript."""
#         if len(self.current_buffer) == 0:
#             return False
            
#         buffer_duration = now - (self.buffer_start_time or now)
        
#         if buffer_duration < self.min_buffer_duration:
#             return False
        
#         # Max time
#         if buffer_duration >= self.max_time:
#             return f"max time ({buffer_duration:.1f}s)"
        
#         # Silence after speech
#         if (self.last_speech_time and self.last_silence_time and 
#             self.last_silence_time - self.last_speech_time >= self.silence_timeout):
#             return f"silence boundary"
        
#         return False

#     def _check_timeout(self):
#         """Check for timeout during empty queue."""
#         if len(self.current_buffer) == 0 or self.buffer_start_time is None:
#             return
            
#         now = time.time()
#         buffer_duration = now - self.buffer_start_time
        
#         if buffer_duration >= self.max_time:
#             print(f"⏰ Timeout during silence ({buffer_duration:.1f}s)")
#             self._queue_for_transcription()

#     def _queue_for_transcription(self):
#         """Queue audio for background transcription."""
#         if len(self.current_buffer) == 0:
#             return

#         buffer_duration = time.time() - (self.buffer_start_time or time.time())
        
#         try:
#             audio_i16 = np.frombuffer(bytes(self.current_buffer), dtype=np.int16)
#             audio_f32 = audio_i16.astype(np.float32) / 32768.0
            
#             volume = np.sqrt(np.mean(audio_f32**2))
#             print(f"🔊 Buffer volume: {volume:.4f}, duration: {buffer_duration:.1f}s")
            
#             if volume < 0.005:
#                 print("🔇 Too quiet, skipping transcription")
#                 self._clear_buffer()
#                 return

#             try:
#                 self.transcription_q.put_nowait({
#                     'audio': audio_f32.copy(),
#                     'duration': buffer_duration,
#                     'volume': volume,
#                     'timestamp': time.time()
#                 })
#                 print(f"📦 Queued {buffer_duration:.1f}s audio for transcription")
#             except queue.Full:
#                 print("⚠️ Transcription queue full")

#         except Exception as e:
#             print(f"❌ Error queuing audio: {e}")

#         self._clear_buffer()

#     def _clear_buffer(self):
#         """Clear buffer and reset timing."""
#         self.current_buffer.clear()
#         self.buffer_start_time = None
#         self.last_speech_time = None
#         self.last_silence_time = None

#     def _transcription_worker(self):
#         """🔥 FIXED: Background transcription with correct API."""
#         print("🤖 Starting transcription worker...")
        
#         while self.running:
#             try:
#                 audio_data = self.transcription_q.get(timeout=1)
#                 print(f"🤖 Got audio for transcription: {audio_data['duration']:.1f}s")
#             except queue.Empty:
#                 continue

#             try:
#                 print(f"🤖 Transcribing {audio_data['duration']:.1f}s audio...")
#                 start_time = time.time()
                
#                 # 🔥 FIXED: Minimal transcription call - no unsupported parameters
#                 segments, info = self.model.transcribe(
#                     audio_data['audio'],
#                     language="en"
#                 )
                
#                 # Collect text
#                 text_parts = []
#                 for seg in segments:
#                     text_parts.append(seg.text.strip())
                
#                 text = " ".join(text_parts).strip()
#                 transcription_time = time.time() - start_time
                
#                 print(f"⏱️ Transcription took {transcription_time:.1f}s")
                
#                 if text:
#                     print(f"🗣️ TRANSCRIBED: '{text}'")
#                     self.trans_q.put(text)
#                 else:
#                     print("🔇 No speech detected in transcription")

#             except Exception as e:
#                 print(f"❌ Transcription error: {e}")

#     def _overlay_loop(self):
#         """Process final transcriptions for verse overlay."""
#         print("📡 Starting overlay loop...")
        
#         while self.running:
#             try:
#                 text = self.trans_q.get(timeout=1)
#                 print(f"📖 Processing for verses: '{text}'")
#             except queue.Empty:
#                 continue

#             try:
#                 result = process_transcript_chunk(text)

#                 async_to_sync(self.channel_layer.group_send)(
#                     self.group_name,
#                     {
#                         "type": "send_overlay",
#                         "chunk": result["chunk"],
#                         "verses": result["verses"],
#                     }
#                 )
#                 print(f"📡 Sent {len(result['verses'])} verses")
                
#             except Exception as e:
#                 print(f"❌ Overlay error: {e}")

#     def start(self):
#         """Launch all threads."""
#         self.running = True
#         print("🚀 Starting FIXED LiveVerseOverlayEngine...")
        
#         capture_thread = threading.Thread(target=self._capture, daemon=True)
#         audio_thread = threading.Thread(target=self._process_audio_fast, daemon=True)
#         transcription_thread = threading.Thread(target=self._transcription_worker, daemon=True)
#         overlay_thread = threading.Thread(target=self._overlay_loop, daemon=True)
        
#         capture_thread.start()
#         audio_thread.start()
#         transcription_thread.start()
#         overlay_thread.start()
        
#         print("✅ All threads started!")

#     def stop(self):
#         """Stop all threads."""
#         print("🛑 Stopping LiveVerseOverlayEngine...")
#         self.running = False

import threading
import queue
import time
import re
import sounddevice as sd
import webrtcvad
import numpy as np
from collections import deque
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum


from faster_whisper import WhisperModel
from scripture.pipeline.live_processor import process_transcript_chunk
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class ContextMode(Enum):
    NORMAL = "normal"
    SCRIPTURE = "scripture"
    STORY = "story"

@dataclass
class TranscriptContext:
    text: str
    timestamp: float
    scripture_probability: float
    mode: ContextMode

class SmartScriptureAnalyzer:
    """Intelligent scripture detection and context analysis."""
    
    # Bible books for quick lookup
    BIBLE_BOOKS = {
        'genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy', 'joshua', 'judges', 'ruth',
        '1 samuel', '2 samuel', '1 kings', '2 kings', '1 chronicles', '2 chronicles', 'ezra',
        'nehemiah', 'esther', 'job', 'psalms', 'proverbs', 'ecclesiastes', 'song of solomon',
        'isaiah', 'jeremiah', 'lamentations', 'ezekiel', 'daniel', 'hosea', 'joel', 'amos',
        'obadiah', 'jonah', 'micah', 'nahum', 'habakkuk', 'zephaniah', 'haggai', 'zechariah',
        'malachi', 'matthew', 'mark', 'luke', 'john', 'acts', 'romans', '1 corinthians',
        '2 corinthians', 'galatians', 'ephesians', 'philippians', 'colossians', '1 thessalonians',
        '2 thessalonians', '1 timothy', '2 timothy', 'titus', 'philemon', 'hebrews', 'james',
        '1 peter', '2 peter', '1 john', '2 john', '3 john', 'jude', 'revelation'
    }
    
    # Common abbreviations
    BOOK_ABBREVS = {
        'gen', 'ex', 'lev', 'num', 'deut', 'josh', 'judg', 'sam', 'kgs', 'chr', 'neh',
        'ps', 'prov', 'eccl', 'isa', 'jer', 'lam', 'ezek', 'dan', 'hos', 'joel', 'obad',
        'mic', 'nah', 'hab', 'zeph', 'hag', 'zech', 'mal', 'matt', 'mk', 'lk', 'jn',
        'rom', 'cor', 'gal', 'eph', 'phil', 'col', 'thess', 'tim', 'tit', 'heb', 'jas',
        'pet', 'jude', 'rev'
    }
    
    # Non-scripture penalty words
    PENALTY_WORDS = {
        'coffee', 'morning', 'nap', 'breakfast', 'lunch', 'dinner', 'weather', 'sports',
        'politics', 'news', 'shopping', 'driving', 'parking', 'traffic', 'movie', 'tv',
        'facebook', 'instagram', 'twitter', 'phone', 'computer', 'internet', 'email'
    }
    
    # Scripture indicator phrases
    SCRIPTURE_INDICATORS = {
        'scripture says', 'bible says', 'word of god', 'according to', 'as written',
        'it is written', 'the lord says', 'thus says', 'verse', 'chapter', 'book of',
        'gospel of', 'epistle', 'psalms', 'proverbs', 'testament'
    }
    
    def __init__(self):
        self.verse_pattern = re.compile(r'\b(\d{1,3}):(\d{1,3})\b')
        self.chapter_pattern = re.compile(r'\bchapter\s+(\d{1,3})\b', re.IGNORECASE)
        self.book_pattern = re.compile(r'\b([1-3]?\s?[a-z]+)\s+(\d{1,3})\b', re.IGNORECASE)
    
    def calculate_scripture_probability(self, text: str, context_history: List[TranscriptContext]) -> float:
        """Calculate probability that text contains scripture references."""
        text_lower = text.lower()
        score = 0.0
        
        # Check for Bible books (high weight)
        for book in self.BIBLE_BOOKS:
            if book in text_lower:
                score += 0.4
        
        # Check for abbreviations (medium weight)
        words = text_lower.split()
        for word in words:
            if word in self.BOOK_ABBREVS:
                score += 0.3
        
        # Check for verse patterns (high weight)
        if self.verse_pattern.search(text):
            score += 0.4
        
        # Check for chapter references (medium weight)
        if self.chapter_pattern.search(text):
            score += 0.3
        
        # Check for scripture indicators (medium weight)
        for indicator in self.SCRIPTURE_INDICATORS:
            if indicator in text_lower:
                score += 0.25
        
        # Apply penalties for non-scripture words
        penalty = sum(0.2 for word in self.PENALTY_WORDS if word in text_lower)
        score = max(0, score - penalty)
        
        # Context boost - if recent transcripts had scripture
        if context_history:
            recent_scripture = sum(1 for ctx in context_history[-3:] 
                                 if ctx.scripture_probability > 0.3)
            if recent_scripture >= 2:
                score += 0.2  # Context boost
        
        return min(1.0, score)
    
    def determine_context_mode(self, probability: float, current_mode: ContextMode, 
                             mode_start_time: float) -> Tuple[ContextMode, float]:
        """Determine the appropriate context mode based on content."""
        now = time.time()
        mode_duration = now - mode_start_time
        
        # High probability scripture content
        if probability > 0.5:
            return ContextMode.SCRIPTURE, now if current_mode != ContextMode.SCRIPTURE else mode_start_time
        
        # Stay in scripture mode for a while after detection
        if current_mode == ContextMode.SCRIPTURE and mode_duration < 20:
            return ContextMode.SCRIPTURE, mode_start_time
        
        # Low probability content that looks like stories/narratives
        if probability < 0.1 and len(text.split()) > 10:
            return ContextMode.STORY, now if current_mode != ContextMode.STORY else mode_start_time
        
        return ContextMode.NORMAL, now if current_mode != ContextMode.NORMAL else mode_start_time

class EnhancedLiveVerseOverlayEngine:
    """
    🚀 ENHANCED VERSION: Smart scripture detection with adaptive processing.
    """
    def __init__(
        self,
        model_size: str = "tiny",
        device: str = "cpu",
        sample_rate: int = 16000,
        vad_mode: int = 2,
        max_chunk_time: float = 4.0,  # Reduced for faster response
        silence_timeout: float = 1.0,
        input_device: int = None
    ):
        # Load ASR model
        print(f"🤖 Loading Whisper {model_size} model...")
        self.model = WhisperModel(model_size, device=device, compute_type="int8")
        print("✅ Whisper loaded!")

        # Voice activity detection (VAD)
        self.vad = webrtcvad.Vad(vad_mode)

        # Queues (smaller for better performance)
        self.audio_q = queue.Queue(maxsize=30)
        self.transcription_q = queue.PriorityQueue(maxsize=5)  # Priority queue
        self.trans_q = queue.Queue()
        
        # Smart scripture analyzer
        self.scripture_analyzer = SmartScriptureAnalyzer()
        
        # Context tracking
        self.context_history = deque(maxlen=10)
        self.current_mode = ContextMode.NORMAL
        self.mode_start_time = time.time()
        
        # Current audio buffer for VAD processing
        self.current_buffer = bytearray()

        # Audio parameters
        self.sr = sample_rate
        self.frame_ms = 30
        self.frame_size = int(self.sr * self.frame_ms / 1000)
        self.max_time = max_chunk_time
        self.silence_timeout = silence_timeout

        # Speech state tracking
        self.last_speech_time = None
        self.last_silence_time = None
        self.buffer_start_time = None
        self.min_buffer_duration = 0.1

        # Control flags
        self.running = False
        self.input_device = input_device or sd.default.device[0]
        print(f"🎙️ Using mic ID: {self.input_device}")

        # Enhanced debug counters
        self.debug_audio_callbacks = 0
        self.debug_audio_processed = 0
        self.debug_speech_detected = 0
        self.debug_last_volume_check = time.time()
        self.debug_volume_threshold = 0.008  # Slightly higher threshold
        self.debug_transcriptions_skipped = 0
        self.debug_false_positives = 0
        self.debug_verses_found = 0

        # WebSocket support
        self.channel_layer = get_channel_layer()
        self.group_name = "live_verses"

    def _should_transcribe(self, audio_data: np.ndarray, duration: float) -> Tuple[bool, int]:
        """Intelligent decision on whether to transcribe based on context and content likelihood."""
        volume = np.sqrt(np.mean(audio_data**2))
        
        # Always transcribe in scripture mode (high alert)
        if self.current_mode == ContextMode.SCRIPTURE:
            return True, 1  # High priority
        
        # Skip very quiet audio
        if volume < self.debug_volume_threshold:
            return False, 0
        
        # Skip very short audio in story mode
        if self.current_mode == ContextMode.STORY and duration < 2.0:
            return False, 0
        
        # Normal processing
        if duration > 2.0 or volume > 0.015:
            return True, 2 if self.current_mode == ContextMode.NORMAL else 3
        
        return False, 0

    def _audio_callback(self, indata, frames, time_info, status):
        """Audio callback with debug info."""
        self.debug_audio_callbacks += 1
        
        if status:
            print(f"[AudioErr] {status}")

        volume = np.max(np.abs(indata))
        now = time.time()
        
        # Log volume every 5 seconds
        if now - self.debug_last_volume_check > 5:
            print(f"🔊 Audio callback #{self.debug_audio_callbacks}: volume={volume:.4f} | Mode: {self.current_mode.value}")
            self.debug_last_volume_check = now
        
        if volume < self.debug_volume_threshold:
            return

        try:
            audio_int16 = (indata[:, 0] * 32767).astype(np.int16)
            self.audio_q.put_nowait(audio_int16.tobytes())
            
            self.debug_audio_processed += 1
            if self.debug_audio_processed % 50 == 0:
                print(f"📦 Processed: {self.debug_audio_processed} | Skipped: {self.debug_transcriptions_skipped} | Verses: {self.debug_verses_found}")
                
        except queue.Full:
            try:
                self.audio_q.get_nowait()
                self.audio_q.put_nowait(audio_int16.tobytes())
                print("⚡ Queue full - removed old audio")
            except:
                pass

    def _capture(self):
        """Stream audio from selected input device."""
        try:
            print(f"🎙️ Starting audio capture...")
            
            with sd.InputStream(
                samplerate=self.sr,
                device=self.input_device,
                channels=1,
                dtype="float32",
                blocksize=self.frame_size,
                callback=self._audio_callback
            ):
                print(f"✅ Audio stream active")
                while self.running:
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"❌ Audio capture error: {e}")
            raise

    def _process_audio_smart(self):
        """Smart audio processing with VAD and context awareness."""
        print("🧠 Starting smart audio processing...")
        
        while self.running:
            try:
                chunk = self.audio_q.get(timeout=0.5)
            except queue.Empty:
                self._check_timeout()
                continue

            self.current_buffer.extend(chunk)
            
            if self.buffer_start_time is None:
                self.buffer_start_time = time.time()

            self._process_vad_frames_smart()

    def _process_vad_frames_smart(self):
        """Process VAD frames with smart context awareness."""
        now = time.time()
        
        # Process frames for VAD detection
        frames_processed = 0
        speech_frames = 0
        temp_buffer = self.current_buffer[:]
        
        while len(temp_buffer) >= 2 * self.frame_size and frames_processed < 3:
            frame = bytes(temp_buffer[:2 * self.frame_size])
            temp_buffer = temp_buffer[2 * self.frame_size:]
            frames_processed += 1

            try:
                is_speech = self.vad.is_speech(frame, sample_rate=self.sr)
                
                if is_speech:
                    speech_frames += 1
                    self.last_speech_time = now
                    self.last_silence_time = None
                    self.debug_speech_detected += 1
                else:
                    if self.last_silence_time is None:
                        self.last_silence_time = now

            except Exception as e:
                print(f"❌ VAD error: {e}")
                break
        
        # Smart emission decision
        should_emit = self._should_emit_transcript_smart(now)
        if should_emit:
            print(f"⚡ Smart emit: {should_emit}")
            self._queue_for_smart_transcription()

    def _should_emit_transcript_smart(self, now):
        """Smart decision on when to emit based on context mode."""
        if len(self.current_buffer) == 0:
            return False
            
        buffer_duration = now - (self.buffer_start_time or now)
        
        if buffer_duration < self.min_buffer_duration:
            return False
        
        # Adaptive timing based on mode
        max_time = self.max_time
        if self.current_mode == ContextMode.SCRIPTURE:
            max_time = 3.0  # Faster response in scripture mode
        elif self.current_mode == ContextMode.STORY:
            max_time = 6.0  # Longer buffering in story mode
        
        # Max time
        if buffer_duration >= max_time:
            return f"max time ({buffer_duration:.1f}s, mode: {self.current_mode.value})"
        
        # Adaptive silence timeout
        silence_timeout = self.silence_timeout
        if self.current_mode == ContextMode.SCRIPTURE:
            silence_timeout = 0.8  # More sensitive in scripture mode
        
        # Silence after speech
        if (self.last_speech_time and self.last_silence_time and 
            self.last_silence_time - self.last_speech_time >= silence_timeout):
            return f"silence boundary (mode: {self.current_mode.value})"
        
        return False

    def _check_timeout(self):
        """Check for timeout during empty queue."""
        if len(self.current_buffer) == 0 or self.buffer_start_time is None:
            return
            
        now = time.time()
        buffer_duration = now - self.buffer_start_time
        
        max_time = self.max_time
        if self.current_mode == ContextMode.SCRIPTURE:
            max_time = 3.0
        elif self.current_mode == ContextMode.STORY:
            max_time = 6.0
        
        if buffer_duration >= max_time:
            print(f"⏰ Smart timeout ({buffer_duration:.1f}s, mode: {self.current_mode.value})")
            self._queue_for_smart_transcription()

    def _queue_for_smart_transcription(self):
        """Queue audio for smart transcription with priority."""
        if len(self.current_buffer) == 0:
            return

        buffer_duration = time.time() - (self.buffer_start_time or time.time())
        
        try:
            audio_i16 = np.frombuffer(bytes(self.current_buffer), dtype=np.int16)
            audio_f32 = audio_i16.astype(np.float32) / 32768.0
            
            volume = np.sqrt(np.mean(audio_f32**2))
            
            # Smart transcription decision
            should_transcribe, priority = self._should_transcribe(audio_f32, buffer_duration)
            
            if not should_transcribe:
                print(f"🔇 Skipping transcription: volume={volume:.4f}, duration={buffer_duration:.1f}s, mode={self.current_mode.value}")
                self.debug_transcriptions_skipped += 1
                self._clear_buffer()
                return

            try:
                # Priority queue item: (priority, timestamp, data)
                queue_item = (priority, time.time(), {
                    'audio': audio_f32.copy(),
                    'duration': buffer_duration,
                    'volume': volume,
                    'timestamp': time.time(),
                    'mode': self.current_mode
                })
                self.transcription_q.put_nowait(queue_item)
                print(f"📦 Smart queued: {buffer_duration:.1f}s, priority={priority}, mode={self.current_mode.value}")
            except queue.Full:
                print("⚠️ Transcription queue full - processing backlog")

        except Exception as e:
            print(f"❌ Error in smart queuing: {e}")

        self._clear_buffer()

    def _clear_buffer(self):
        """Clear buffer and reset timing."""
        self.current_buffer.clear()
        self.buffer_start_time = None
        self.last_speech_time = None
        self.last_silence_time = None

    def _smart_transcription_worker(self):
        """🔥 Smart transcription worker with context awareness."""
        print("🧠 Starting smart transcription worker...")
        
        while self.running:
            try:
                priority, queue_time, audio_data = self.transcription_q.get(timeout=1)
                print(f"🤖 Processing priority {priority} audio: {audio_data['duration']:.1f}s")
            except queue.Empty:
                continue

            try:
                print(f"🤖 Smart transcribing {audio_data['duration']:.1f}s audio (mode: {audio_data['mode'].value})...")
                start_time = time.time()
                
                # Transcription with language hint
                segments, info = self.model.transcribe(
                    audio_data['audio'],
                    language="en"
                )
                
                # Collect text
                text_parts = []
                for seg in segments:
                    text_parts.append(seg.text.strip())
                
                text = " ".join(text_parts).strip()
                transcription_time = time.time() - start_time
                
                print(f"⏱️ Transcription took {transcription_time:.1f}s")
                
                if text:
                    # Smart scripture analysis
                    scripture_prob = self.scripture_analyzer.calculate_scripture_probability(
                        text, list(self.context_history)
                    )
                    
                    # Update context
                    context = TranscriptContext(
                        text=text,
                        timestamp=time.time(),
                        scripture_probability=scripture_prob,
                        mode=audio_data['mode']
                    )
                    self.context_history.append(context)
                    
                    # Update context mode
                    self.current_mode, self.mode_start_time = self.scripture_analyzer.determine_context_mode(
                        scripture_prob, self.current_mode, self.mode_start_time
                    )
                    
                    print(f"🗣️ TRANSCRIBED: '{text}' (prob: {scripture_prob:.2f}, mode: {self.current_mode.value})")
                    
                    # Queue for processing if likely scripture content
                    if scripture_prob > 0.2 or self.current_mode == ContextMode.SCRIPTURE:
                        self.trans_q.put({
                            'text': text,
                            'probability': scripture_prob,
                            'mode': self.current_mode,
                            'timestamp': time.time()
                        })
                    else:
                        print(f"🚫 Skipping non-scripture content (prob: {scripture_prob:.2f})")
                        self.debug_false_positives += 1
                else:
                    print("🔇 No speech detected in transcription")

            except Exception as e:
                print(f"❌ Smart transcription error: {e}")

    def _smart_overlay_loop(self):
        """Process transcriptions with smart scripture detection."""
        print("📡 Starting smart overlay loop...")
        
        while self.running:
            try:
                data = self.trans_q.get(timeout=1)
                text = data['text']
                probability = data['probability']
                mode = data['mode']
                print(f"📖 Smart processing: '{text}' (prob: {probability:.2f})")
            except queue.Empty:
                continue

            try:
                result = process_transcript_chunk(text)
                
                if result['verses']:
                    self.debug_verses_found += len(result['verses'])
                    print(f"✅ Found {len(result['verses'])} verses!")

                # Send enhanced data to frontend
                async_to_sync(self.channel_layer.group_send)(
                    self.group_name,
                    {
                        "type": "send_overlay",
                        "chunk": result["chunk"],
                        "verses": result["verses"],
                        "probability": probability,
                        "mode": mode.value,
                        "confidence": min(1.0, probability * 1.2),  # Boost for UI
                        "timestamp": time.time()
                    }
                )
                print(f"📡 Smart sent: {len(result['verses'])} verses, prob: {probability:.2f}")
                
            except Exception as e:
                print(f"❌ Smart overlay error: {e}")

    def start(self):
        """Launch all smart threads."""
        self.running = True
        print("🚀 Starting ENHANCED Smart LiveVerseOverlayEngine...")
        
        capture_thread = threading.Thread(target=self._capture, daemon=True)
        audio_thread = threading.Thread(target=self._process_audio_smart, daemon=True)
        transcription_thread = threading.Thread(target=self._smart_transcription_worker, daemon=True)
        overlay_thread = threading.Thread(target=self._smart_overlay_loop, daemon=True)
        
        capture_thread.start()
        audio_thread.start()
        transcription_thread.start()
        overlay_thread.start()
        
        print("✅ All smart threads started!")
        print(f"📊 Performance tracking enabled:")
        print(f"   - Transcriptions skipped: {self.debug_transcriptions_skipped}")
        print(f"   - False positives: {self.debug_false_positives}")
        print(f"   - Verses found: {self.debug_verses_found}")

    def stop(self):
        """Stop all threads."""
        print("🛑 Stopping Enhanced LiveVerseOverlayEngine...")
        print(f"📊 Final stats:")
        print(f"   - Audio processed: {self.debug_audio_processed}")
        print(f"   - Transcriptions skipped: {self.debug_transcriptions_skipped}")
        print(f"   - False positives: {self.debug_false_positives}")
        print(f"   - Verses found: {self.debug_verses_found}")
        print(f"   - Efficiency: {((self.debug_transcriptions_skipped / max(1, self.debug_audio_processed)) * 100):.1f}% skipped")
        self.running = False

    def get_performance_stats(self) -> Dict:
        """Get current performance statistics."""
        total_processed = max(1, self.debug_audio_processed)
        return {
            'audio_processed': self.debug_audio_processed,
            'transcriptions_skipped': self.debug_transcriptions_skipped,
            'false_positives': self.debug_false_positives,
            'verses_found': self.debug_verses_found,
            'skip_efficiency': (self.debug_transcriptions_skipped / total_processed) * 100,
            'current_mode': self.current_mode.value,
            'context_history_size': len(self.context_history)
        }