# scripture/transcription/controller.py
from threading import Thread
from scripture.transcription.overlay_engine import LiveVerseOverlayEngine

class TranscriptionController:
    _engine: LiveVerseOverlayEngine = None
    _thread: Thread = None

    @classmethod
    def start(cls):
        if cls._engine is None:
            cls._engine = LiveVerseOverlayEngine(model_size="small", device="cpu")
            cls._engine.running = True
            cls._thread = Thread(target=cls._engine.start, daemon=True)
            cls._thread.start()
            print("[Controller] Transcription started")
        else:
            print("[Controller] Already running")

    @classmethod
    def stop(cls):
        if cls._engine:
            cls._engine.stop()   # you’ll add this method
            cls._engine = None
            print("[Controller] Transcription stopped")
        else:
            print("[Controller] Not running")
